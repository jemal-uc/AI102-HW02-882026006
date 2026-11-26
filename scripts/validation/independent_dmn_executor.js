const fs = require("fs");
const path = require("path");
const { DmnModdle } = require("dmn-moddle");
const { evaluate, unaryTest } = require("feelin");

const ROOT = path.resolve(__dirname, "..", "..");
const DMN_PATH = path.join(ROOT, "src", "decision-model", "AsuransiNusantara.dmn");
const SPEC_PATH = path.join(ROOT, "src", "specification", "CANONICAL_DECISION_SPECIFICATION.json");
const OUT_PATH = path.join(ROOT, "tests", "test-results", "INDEPENDENT_EXECUTION_RESULTS.json");

function parseRefId(refObj) {
  if (!refObj || !refObj.href) return null;
  return refObj.href.replace(/^#/, "");
}

function buildDynamicTopoOrder(decisionsMap) {
  const inDegree = {};
  const adj = {};
  for (const id of Object.keys(decisionsMap)) {
    inDegree[id] = 0;
    adj[id] = [];
  }
  for (const [id, dec] of Object.entries(decisionsMap)) {
    for (const req of dec.informationRequirement || []) {
      const depId = parseRefId(req.requiredDecision);
      if (depId && decisionsMap[depId]) {
        adj[depId].push(id);
        inDegree[id]++;
      }
    }
  }
  const queue = Object.keys(inDegree).filter((id) => inDegree[id] === 0).sort();
  const order = [];
  while (queue.length > 0) {
    const cur = queue.shift();
    order.push(cur);
    for (const nxt of adj[cur]) {
      inDegree[nxt]--;
      if (inDegree[nxt] === 0) queue.push(nxt);
    }
  }
  if (order.length !== Object.keys(decisionsMap).length) {
    throw new Error("Cycle detected during topological sort!");
  }
  return order;
}

function bindBkmFunctions(defs) {
  const bkmFns = {};
  for (const el of defs.drgElement || []) {
    if (el.$type !== "dmn:BusinessKnowledgeModel") continue;
    const paramNames = (el.encapsulatedLogic.formalParameter || []).map((p) => p.name);
    const bodyExpr = el.encapsulatedLogic.body.text;
    bkmFns[el.name] = (...args) => {
      const localCtx = { ...bkmFns };
      paramNames.forEach((pName, idx) => {
        localCtx[pName] = args[idx] === undefined ? null : args[idx];
      });
      const res = evaluate(bodyExpr, localCtx);
      if (res.warnings && res.warnings.length > 0) {
        throw new Error(`FEEL warning inside BKM ${el.name}: ${JSON.stringify(res.warnings)}`);
      }
      return res.value;
    };
  }
  return bkmFns;
}

function parseAllowedValuesList(text) {
  if (!text) return null;
  const res = evaluate(`[${text}]`, {});
  return Array.isArray(res.value) ? res.value : null;
}

function executeDecisionTable(decEl, ctx, itemDefsMap) {
  const dt = decEl.decisionLogic;
  const hitPolicy = dt.hitPolicy || "UNIQUE";
  const aggregation = dt.aggregation || null;

  const inputVals = (dt.input || []).map((inp) => {
    const r = evaluate(inp.inputExpression.text, ctx);
    if (r.warnings && r.warnings.length > 0) {
      throw new Error(`FEEL warning in ${decEl.id} inputExpression (${inp.inputExpression.text}): ${JSON.stringify(r.warnings)}`);
    }
    return r.value;
  });

  const matched = [];
  for (const rule of dt.rule || []) {
    let ok = true;
    for (let i = 0; i < (dt.input || []).length; i++) {
      const cell = rule.inputEntry[i].text.trim();
      if (cell === "-") continue;
      const ut = unaryTest(cell, { "?": inputVals[i] });
      if (ut.warnings && ut.warnings.length > 0) {
        throw new Error(`FEEL warning in ${decEl.id}/${rule.id} cell ${cell}: ${JSON.stringify(ut.warnings)}`);
      }
      if (!ut.value) {
        ok = false;
        break;
      }
    }
    if (ok) {
      const outRes = evaluate(rule.outputEntry[0].text, ctx);
      if (outRes.warnings && outRes.warnings.length > 0) {
        throw new Error(`FEEL warning in ${decEl.id}/${rule.id} output: ${JSON.stringify(outRes.warnings)}`);
      }
      matched.push({ ruleId: rule.id, value: outRes.value });
      if (hitPolicy === "FIRST") break;
    }
  }

  if (matched.length === 0) {
    throw new Error(`Completeness failure in ${decEl.id}: no rule matched inputs ${JSON.stringify(inputVals)}`);
  }
  if (hitPolicy === "UNIQUE" && matched.length > 1) {
    throw new Error(`UNIQUE violation in ${decEl.id}: ${matched.map((m) => m.ruleId).join(", ")}`);
  }
  if (hitPolicy === "ANY") {
    const distinct = new Set(matched.map((m) => JSON.stringify(m.value)));
    if (distinct.size > 1) throw new Error(`ANY violation in ${decEl.id}`);
  }

  let output;
  if (hitPolicy === "COLLECT") {
    const vals = matched.map((m) => m.value);
    if (aggregation === "SUM") {
      output = Math.round(vals.reduce((a, b) => a + Number(b), 0) * 1e6) / 1e6;
    } else if (aggregation === "MIN") {
      output = Math.min(...vals);
    } else if (aggregation === "MAX") {
      output = Math.max(...vals);
    } else if (aggregation === "COUNT") {
      output = vals.length;
    } else {
      output = vals;
    }
  } else if (hitPolicy === "PRIORITY") {
    const outVals = parseAllowedValuesList(dt.output[0].outputValues?.text);
    matched.sort((a, b) => outVals.indexOf(a.value) - outVals.indexOf(b.value));
    output = matched[0].value;
  } else {
    output = matched[0].value;
  }

  // Validate against outputValues / itemDefinition allowedValues
  const typeRef = decEl.variable.typeRef;
  const itemDef = itemDefsMap[typeRef];
  if (itemDef && itemDef.allowedValues) {
    const allowed = parseAllowedValuesList(itemDef.allowedValues.text);
    if (allowed && !allowed.includes(output)) {
      throw new Error(`Output ${output} violates itemDefinition ${typeRef} allowedValues ${JSON.stringify(allowed)}`);
    }
  }

  return {
    decisionId: decEl.id,
    hitPolicy: aggregation ? `${hitPolicy} (${aggregation})` : hitPolicy,
    inputValues: inputVals,
    matchedRuleIds: matched.map((m) => m.ruleId),
    outputName: decEl.variable.name,
    outputValue: output,
  };
}

// Pure independent JS reference arithmetic check (zero shared code with DMN/FEEL)
function independentPremiumRef(inputs, dmnDecisions) {
  const { vehicleType, engineCC, coverType, insuredValue } = inputs;
  const isTpo = coverType === "TPO" || coverType === "THIRD_PARTY_ONLY";
  const isComp = coverType === "COMPREHENSIVE";
  let base = null;
  if (typeof insuredValue === "number" && insuredValue > 0 && typeof engineCC === "number" && engineCC > 0 && (isTpo || isComp)) {
    if (vehicleType === "MOTORCYCLE") {
      if (engineCC <= 150) base = isTpo ? Math.max(150000, insuredValue * 0.005) : Math.max(300000, insuredValue * 0.020);
      else if (engineCC <= 250) base = isTpo ? Math.max(200000, insuredValue * 0.007) : Math.max(450000, insuredValue * 0.025);
      else base = isTpo ? Math.max(350000, insuredValue * 0.010) : Math.max(750000, insuredValue * 0.032);
    } else if (vehicleType === "CAR") {
      if (engineCC <= 1500) base = isTpo ? Math.max(500000, insuredValue * 0.004) : Math.max(1500000, insuredValue * 0.018);
      else if (engineCC <= 2500) base = isTpo ? Math.max(650000, insuredValue * 0.005) : Math.max(2000000, insuredValue * 0.022);
      else base = isTpo ? Math.max(850000, insuredValue * 0.006) : Math.max(2500000, insuredValue * 0.028);
    }
  }
  if (base !== null) base = Math.round(base);

  const lDrv = dmnDecisions.driverRisk === "HIGH" ? 0.25 : dmnDecisions.driverRisk === "MEDIUM" ? 0.10 : 0;
  const lClm = dmnDecisions.claimsRisk === "MEDIUM" ? 0.20 : dmnDecisions.claimsRisk === "HIGH" ? 0.40 : dmnDecisions.claimsRisk === "UNKNOWN" ? 0.25 : 0;
  const lVeh = dmnDecisions.vehicleRisk === "MEDIUM" ? 0.10 : dmnDecisions.vehicleRisk === "HIGH" ? 0.20 : 0;
  const lPerf = inputs.performanceClass === "SPORT" ? 0.15 : inputs.performanceClass === "STANDARD" ? 0 : 0.30;
  const loading = Math.round((lDrv + lClm + lVeh + lPerf) * 1e6) / 1e6;
  const canIssue = dmnDecisions.underwritingDecision === "ACCEPT" && dmnDecisions.quoteReadiness === "READY" && base !== null && base > 0;
  const finalPrem = canIssue ? Math.round(base * (1 + loading)) : null;
  return { base, loading, finalPrem };
}

async function main() {
  const xml = fs.readFileSync(DMN_PATH, "utf8");
  const spec = JSON.parse(fs.readFileSync(SPEC_PATH, "utf8"));
  const moddle = new DmnModdle();
  const { rootElement: defs, warnings } = await moddle.fromXML(xml);

  const itemDefsMap = {};
  for (const idf of defs.itemDefinition || []) itemDefsMap[idf.name] = idf;

  const decsMap = {};
  for (const el of defs.drgElement || []) {
    if (el.$type === "dmn:Decision") decsMap[el.id] = el;
  }

  const topoOrder = buildDynamicTopoOrder(decsMap);
  const bkmFns = bindBkmFunctions(defs);

  // Preserved Stage 2 adversarial FEEL/date/null edge cases (renumbered TC-20..TC-27)
  const adversarialCases = [
    {
      id: "TC-20",
      name: "Stage 2 Adversarial — Future dateOfBirth (2027-01-01 -> -1 Sentinel -> Explicit Decline, Null Premium)",
      category: "Stage 2 Adversarial Preserved",
      inputs: { dateOfBirth: "2027-01-01", evaluationDate: "2026-11-25", claimsHistoryAvailable: true, claimDates: [], vehicleManufactureDate: "2024-01-01", vehicleType: "CAR", engineCC: 1500, performanceClass: "STANDARD", coverType: "COMPREHENSIVE", insuredValue: 200000000 },
      expected: { driverRisk: "INELIGIBLE", claimsRisk: "LOW", vehicleEligibility: "ELIGIBLE", vehicleRisk: "LOW", underwritingDecision: "DECLINE", inspectionDecision: "NOT_APPLICABLE", quoteReadiness: "NOT_APPLICABLE", basePremium: 3600000, totalRiskLoading: 0.0, finalPremium: null }
    },
    {
      id: "TC-21",
      name: "Stage 2 Adversarial — Future vehicleManufactureDate (2027-06-01 -> -1 -> Decline, Null Premium)",
      category: "Stage 2 Adversarial Preserved",
      inputs: { dateOfBirth: "1990-01-01", evaluationDate: "2026-11-25", claimsHistoryAvailable: true, claimDates: [], vehicleManufactureDate: "2027-06-01", vehicleType: "CAR", engineCC: 1500, performanceClass: "STANDARD", coverType: "TPO", insuredValue: 150000000 },
      expected: { driverRisk: "LOW", claimsRisk: "LOW", vehicleEligibility: "INELIGIBLE", vehicleRisk: "HIGH", underwritingDecision: "DECLINE", inspectionDecision: "NOT_APPLICABLE", quoteReadiness: "NOT_APPLICABLE", basePremium: 600000, totalRiskLoading: 0.2, finalPremium: null }
    },
    {
      id: "TC-22",
      name: "Stage 2/5 Adversarial — Non-Positive insuredValue (<=0 -> Ineligible/Decline, Base=null, Final=null)",
      category: "Stage 2 Adversarial Preserved",
      inputs: { dateOfBirth: "1990-01-01", evaluationDate: "2026-11-25", claimsHistoryAvailable: true, claimDates: [], vehicleManufactureDate: "2024-01-01", vehicleType: "CAR", engineCC: 1500, performanceClass: "STANDARD", coverType: "TPO", insuredValue: -100000 },
      expected: { driverRisk: "LOW", claimsRisk: "LOW", vehicleEligibility: "INELIGIBLE", vehicleRisk: "LOW", underwritingDecision: "DECLINE", inspectionDecision: "NOT_APPLICABLE", quoteReadiness: "NOT_APPLICABLE", basePremium: null, totalRiskLoading: 0.0, finalPremium: null }
    },
    {
      id: "TC-23",
      name: "Stage 2 Adversarial — Missing performanceClass (null -> Conservative HIGH +50% Loading)",
      category: "Stage 2 Adversarial Preserved",
      inputs: { dateOfBirth: "1990-01-01", evaluationDate: "2026-11-25", claimsHistoryAvailable: true, claimDates: [], vehicleManufactureDate: "2024-01-01", vehicleType: "CAR", engineCC: 2000, performanceClass: null, coverType: "COMPREHENSIVE", insuredValue: 400000000 },
      expected: { driverRisk: "LOW", claimsRisk: "LOW", vehicleEligibility: "ELIGIBLE", vehicleRisk: "HIGH", underwritingDecision: "ACCEPT", inspectionDecision: "NOT_REQUIRED", quoteReadiness: "READY", basePremium: 8800000, totalRiskLoading: 0.5, finalPremium: 13200000 }
    },
    {
      id: "TC-24",
      name: "Stage 2 Adversarial — Claim 1 Day Outside 24M Window (2024-11-24 only -> LOW)",
      category: "Stage 2 Adversarial Preserved",
      inputs: { dateOfBirth: "1990-01-01", evaluationDate: "2026-11-25", claimsHistoryAvailable: true, claimDates: ["2024-11-24"], vehicleManufactureDate: "2024-01-01", vehicleType: "MOTORCYCLE", engineCC: 150, performanceClass: "STANDARD", coverType: "TPO", insuredValue: 20000000 },
      expected: { driverRisk: "LOW", claimsRisk: "LOW", vehicleEligibility: "ELIGIBLE", vehicleRisk: "LOW", underwritingDecision: "ACCEPT", inspectionDecision: "NOT_REQUIRED", quoteReadiness: "READY", basePremium: 150000, totalRiskLoading: 0.0, finalPremium: 150000 }
    },
    {
      id: "TC-25",
      name: "Stage 2 Adversarial — Null Item Inside claimDates + 1 Valid Claim (0 FEEL Warnings)",
      category: "Stage 2 Adversarial Preserved",
      inputs: { dateOfBirth: "1990-01-01", evaluationDate: "2026-11-25", claimsHistoryAvailable: true, claimDates: ["2024-11-26", null], vehicleManufactureDate: "2024-01-01", vehicleType: "MOTORCYCLE", engineCC: 150, performanceClass: "STANDARD", coverType: "COMPREHENSIVE", insuredValue: 20000000 },
      expected: { driverRisk: "LOW", claimsRisk: "MEDIUM", vehicleEligibility: "ELIGIBLE", vehicleRisk: "LOW", underwritingDecision: "ACCEPT", inspectionDecision: "NOT_REQUIRED", quoteReadiness: "READY", basePremium: 400000, totalRiskLoading: 0.2, finalPremium: 480000 }
    },
    {
      id: "TC-26",
      name: "Stage 2 Adversarial — Driver Age Exact Lower Bound (Age 17 -> HIGH)",
      category: "Stage 2 Adversarial Preserved",
      inputs: { dateOfBirth: "2009-11-25", evaluationDate: "2026-11-25", claimsHistoryAvailable: true, claimDates: [], vehicleManufactureDate: "2024-01-01", vehicleType: "CAR", engineCC: 1500, performanceClass: "STANDARD", coverType: "COMPREHENSIVE", insuredValue: 200000000 },
      expected: { driverRisk: "HIGH", claimsRisk: "LOW", vehicleEligibility: "ELIGIBLE", vehicleRisk: "LOW", underwritingDecision: "ACCEPT", inspectionDecision: "NOT_REQUIRED", quoteReadiness: "READY", basePremium: 3600000, totalRiskLoading: 0.25, finalPremium: 4500000 }
    },
    {
      id: "TC-27",
      name: "Stage 2 Adversarial — 151cc SPORT Motorcycle (R-D04-04 HIGH)",
      category: "Stage 2 Adversarial Preserved",
      inputs: { dateOfBirth: "1985-01-01", evaluationDate: "2026-11-25", claimsHistoryAvailable: true, claimDates: [], vehicleManufactureDate: "2024-01-01", vehicleType: "MOTORCYCLE", engineCC: 151, performanceClass: "SPORT", coverType: "COMPREHENSIVE", insuredValue: 60000000 },
      expected: { driverRisk: "LOW", claimsRisk: "LOW", vehicleEligibility: "ELIGIBLE", vehicleRisk: "HIGH", underwritingDecision: "ACCEPT", inspectionDecision: "NOT_REQUIRED", quoteReadiness: "READY", basePremium: 1500000, totalRiskLoading: 0.35, finalPremium: 2025000 }
    }
  ];

  const allCases = [...spec.testCases, ...adversarialCases];
  const results = [];
  let passed = 0;

  for (const tc of allCases) {
    const ctx = { ...bkmFns, ...tc.inputs };
    const trace = {};
    for (const did of topoOrder) {
      const r = executeDecisionTable(decsMap[did], ctx, itemDefsMap);
      ctx[r.outputName] = r.outputValue;
      trace[did] = r;
    }

    const actual = {
      driverRisk: ctx.driverRisk,
      claimsRisk: ctx.claimsRisk,
      vehicleEligibility: ctx.vehicleEligibility,
      vehicleRisk: ctx.vehicleRisk,
      underwritingDecision: ctx.underwritingDecision,
      inspectionDecision: ctx.inspectionDecision,
      quoteReadiness: ctx.quoteReadiness,
      basePremium: ctx.basePremium,
      totalRiskLoading: ctx.totalRiskLoading,
      finalPremium: ctx.finalPremium,
    };

    const refArith = independentPremiumRef(tc.inputs, actual);
    const arithMatch = refArith.base === actual.basePremium && refArith.loading === actual.totalRiskLoading && refArith.finalPrem === actual.finalPremium;

    const mismatches = [];
    for (const [k, exp] of Object.entries(tc.expected)) {
      if (["driverAge", "recentClaimsCount", "vehicleAge"].includes(k)) continue;
      if (actual[k] !== exp) mismatches.push({ field: k, expected: exp, actual: actual[k] });
    }
    if (!arithMatch) mismatches.push({ field: "independentArithmetic", expected: refArith, actual: { base: actual.basePremium, loading: actual.totalRiskLoading, finalPrem: actual.finalPremium } });

    const ok = mismatches.length === 0;
    if (ok) passed++;
    results.push({ id: tc.id, name: tc.name, category: tc.category, actual, refArith, trace, mismatches, pass: ok });
  }

  const out = {
    executedAt: new Date().toISOString(),
    dynamicTopologicalOrder: topoOrder,
    boundBkmFunctions: Object.keys(bkmFns),
    dmnModdleWarnings: warnings.length,
    totalCases: allCases.length,
    passedCases: passed,
    failedCases: allCases.length - passed,
    cases: results,
  };
  fs.writeFileSync(OUT_PATH, JSON.stringify(out, null, 2), "utf8");
  console.log(JSON.stringify({ topoOrder, boundBkmFunctions: Object.keys(bkmFns), totalCases: allCases.length, passedCases: passed, failedCases: allCases.length - passed }, null, 2));
  if (passed !== allCases.length) process.exit(1);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
