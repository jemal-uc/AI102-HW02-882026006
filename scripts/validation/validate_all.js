const fs = require("fs");
const path = require("path");
const { DmnModdle } = require("dmn-moddle");
const { evaluate, unaryTest } = require("feelin");

const ROOT = path.resolve(__dirname, "..", "..");
const DMN_PATH = path.join(ROOT, "src", "decision-model", "AsuransiNusantara.dmn");
const SPEC_PATH = path.join(ROOT, "src", "specification", "CANONICAL_DECISION_SPECIFICATION.json");
const OUT_RESULTS = path.join(ROOT, "tests", "test-results", "TEST_RESULTS.json");

function buildBkmCall(bkmName, params, body, argsMap) {
  // Bind formal parameters in context and evaluate the exact BKM FEEL body from the DMN XML
  return evaluate(body, argsMap).value;
}

function evalInputExpr(exprText, ctx, bkmMap) {
  // Detect BKM invocations inside DMN inputExpression (e.g. calculateAgeInYears(a, b) or countRecentClaims(a, b, 24))
  const mAge = exprText.match(/^calculateAgeInYears\(([^,]+),\s*([^)]+)\)$/);
  if (mAge) {
    const targetDate = ctx[mAge[1].trim()];
    const referenceDate = ctx[mAge[2].trim()];
    return evaluate(bkmMap["calculateAgeInYears"].body, { targetDate, referenceDate }).value;
  }
  const mClaims = exprText.match(/^countRecentClaims\(([^,]+),\s*([^,]+),\s*([^)]+)\)$/);
  if (mClaims) {
    const claimDates = ctx[mClaims[1].trim()];
    const referenceDate = ctx[mClaims[2].trim()];
    const windowMonths = Number(mClaims[3].trim());
    return evaluate(bkmMap["countRecentClaims"].body, { claimDates, referenceDate, windowMonths }).value;
  }
  return evaluate(exprText, ctx).value;
}

function evalDecisionTable(decEl, ctx, bkmMap) {
  const dt = decEl.decisionLogic;
  const hitPolicy = dt.hitPolicy || "UNIQUE";
  const aggregation = dt.aggregation || null;

  const inputVals = dt.input.map((inp) => evalInputExpr(inp.inputExpression.text, ctx, bkmMap));
  const matchedRules = [];

  for (const rule of dt.rule) {
    let allMatch = true;
    for (let i = 0; i < dt.input.length; i++) {
      const cellText = rule.inputEntry[i].text.trim();
      if (cellText === "-") continue;
      const val = inputVals[i];
      const ut = unaryTest(cellText, { "?": val });
      if (!ut.value) {
        allMatch = false;
        break;
      }
    }
    if (allMatch) {
      const outExpr = rule.outputEntry[0].text;
      const outVal = evaluate(outExpr, ctx).value;
      matchedRules.push({ ruleId: rule.id, output: outVal, description: rule.description });
      if (hitPolicy === "FIRST") break;
    }
  }

  if (matchedRules.length === 0) {
    throw new Error(`No rule matched in ${decEl.id} (${decEl.name}) for inputs ${JSON.stringify(inputVals)}`);
  }
  if (hitPolicy === "UNIQUE" && matchedRules.length > 1) {
    throw new Error(`UNIQUE violation in ${decEl.id}: matched ${matchedRules.map((r) => r.ruleId).join(", ")}`);
  }

  let finalValue;
  if (hitPolicy === "COLLECT" && aggregation === "SUM") {
    finalValue = matchedRules.reduce((acc, r) => acc + Number(r.output), 0);
    // Avoid IEEE-754 floating noise like 0.35000000000000003
    finalValue = Math.round(finalValue * 1e6) / 1e6;
  } else if (hitPolicy === "COLLECT") {
    finalValue = matchedRules.map((r) => r.output);
  } else {
    finalValue = matchedRules[0].output;
  }

  return {
    decisionId: decEl.id,
    hitPolicy: aggregation ? `${hitPolicy} (${aggregation})` : hitPolicy,
    inputValues: inputVals,
    matchedRuleIds: matchedRules.map((r) => r.ruleId),
    outputName: decEl.variable.name,
    outputValue: finalValue,
  };
}

async function main() {
  const xml = fs.readFileSync(DMN_PATH, "utf8");
  const spec = JSON.parse(fs.readFileSync(SPEC_PATH, "utf8"));
  const moddle = new DmnModdle();
  const { rootElement: defs, warnings } = await moddle.fromXML(xml);

  const bkmMap = {};
  const decMap = {};
  for (const el of defs.drgElement) {
    if (el.$type === "dmn:BusinessKnowledgeModel") {
      bkmMap[el.name] = {
        id: el.id,
        body: el.encapsulatedLogic.body.text,
      };
    } else if (el.$type === "dmn:Decision") {
      decMap[el.id] = el;
    }
  }

  // 1. Validate FEEL catalog expressions
  const feelResults = [];
  let feelPassed = 0;
  let feelTotal = 0;
  for (const item of spec.feelExpressionsCatalog) {
    const testRuns = [];
    for (const t of item.tests) {
      feelTotal++;
      const res = evaluate(item.expression, t.context);
      const pass = res.value === t.expected;
      if (pass) feelPassed++;
      testRuns.push({
        name: t.name,
        isEdgeCase: t.isEdgeCase,
        context: t.context,
        expected: t.expected,
        actual: res.value,
        warnings: res.warnings,
        pass,
      });
    }
    feelResults.push({
      id: item.id,
      category: item.category,
      expression: item.expression,
      tests: testRuns,
    });
  }

  // Also test leap-year pitfall contrast (days-and-time vs years-and-months)
  const dtVsYm = {
    daysAndTimeAge: evaluate('floor((date("2026-11-25") - date("2001-11-25")).days / 365.25)', {}).value,
    yearsAndMonthsAge: evaluate('years and months duration(date("2001-11-25"), date("2026-11-25")).years', {}).value,
  };

  // 2. Execute end-to-end test cases in topological order directly from the parsed DMN XML
  const evalOrder = ["D01", "D02", "D03", "D04", "D07", "D05", "D08", "D06", "D10", "D09"];
  const tcResults = [];
  let tcPassed = 0;

  for (const tc of spec.testCases) {
    const ctx = { ...tc.inputs };
    const trace = {};
    for (const did of evalOrder) {
      const res = evalDecisionTable(decMap[did], ctx, bkmMap);
      ctx[res.outputName] = res.outputValue;
      trace[did] = res;
    }

    const derivedDriverAge = evalInputExpr("calculateAgeInYears(dateOfBirth, evaluationDate)", ctx, bkmMap);
    const derivedRecentClaims = evalInputExpr("countRecentClaims(claimDates, evaluationDate, 24)", ctx, bkmMap);
    const derivedVehicleAge = evalInputExpr("calculateAgeInYears(vehicleManufactureDate, evaluationDate)", ctx, bkmMap);

    const actualSummary = {
      driverAge: derivedDriverAge,
      recentClaimsCount: derivedRecentClaims,
      vehicleAge: derivedVehicleAge,
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

    const mismatches = [];
    for (const [k, expVal] of Object.entries(tc.expected)) {
      if (actualSummary[k] !== expVal) {
        mismatches.push({ field: k, expected: expVal, actual: actualSummary[k] });
      }
    }
    const pass = mismatches.length === 0;
    if (pass) tcPassed++;

    tcResults.push({
      id: tc.id,
      name: tc.name,
      category: tc.category,
      inputs: tc.inputs,
      expected: tc.expected,
      actual: actualSummary,
      trace,
      mismatches,
      pass,
    });
  }

  const output = {
    executedAt: new Date().toISOString(),
    engines: {
      dmnModdleVersion: require("dmn-moddle/package.json").version,
      feelinVersion: require("feelin/package.json").version,
      dmnJsVersion: require("dmn-js/package.json").version,
      nodeVersion: process.version,
    },
    dmnModdleLoad: {
      file: path.basename(DMN_PATH),
      definitionsId: defs.id,
      drgElementsCount: defs.drgElement.length,
      warningsCount: warnings.length,
      warnings: warnings.map((w) => w.message),
    },
    durationPitfallVerification: dtVsYm,
    feelValidation: {
      total: feelTotal,
      passed: feelPassed,
      failed: feelTotal - feelPassed,
      expressions: feelResults,
    },
    endToEndValidation: {
      total: tcResults.length,
      passed: tcPassed,
      failed: tcResults.length - tcPassed,
      cases: tcResults,
    },
  };

  fs.writeFileSync(OUT_RESULTS, JSON.stringify(output, null, 2), "utf8");
  console.log(JSON.stringify({
    dmnModdleWarnings: warnings.length,
    feelPassed: `${feelPassed}/${feelTotal}`,
    endToEndPassed: `${tcPassed}/${tcResults.length}`,
    durationPitfallVerification: dtVsYm,
  }, null, 2));

  if (feelPassed !== feelTotal || tcPassed !== tcResults.length || warnings.length > 0) {
    process.exitCode = 1;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
