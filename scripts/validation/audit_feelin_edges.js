const { evaluate, unaryTest } = require("feelin");
const path = require("path");
const fs = require("fs");

const spec = JSON.parse(fs.readFileSync(path.resolve(__dirname, "..", "..", "src", "specification", "CANONICAL_DECISION_SPECIFICATION.json"), "utf8"));
const bkm01 = spec.bkms[0].feelBody;
const bkm02 = spec.bkms[1].feelBody;

console.log("=== BKM01 EDGE PROBES ===");
const bkm01Cases = [
  ["future DOB 2027-01-01", { targetDate: "2027-01-01", referenceDate: "2026-11-25" }],
  ["same day 2026-11-25", { targetDate: "2026-11-25", referenceDate: "2026-11-25" }],
  ["null targetDate", { targetDate: null, referenceDate: "2026-11-25" }],
  ["invalid date string", { targetDate: "not-a-date", referenceDate: "2026-11-25" }],
  ["leap year feb 29 2008 to 2025-02-28", { targetDate: "2008-02-29", referenceDate: "2025-02-28" }],
  ["leap year feb 29 2008 to 2025-03-01", { targetDate: "2008-02-29", referenceDate: "2025-03-01" }],
];
for (const [lbl, ctx] of bkm01Cases) {
  try {
    console.log(lbl, "=>", JSON.stringify(evaluate(bkm01, ctx)));
  } catch (e) {
    console.log(lbl, "ERR:", e.message);
  }
}

console.log("=== BKM02 EDGE PROBES ===");
const bkm02Cases = [
  ["exact 24M boundary 2024-11-25", { claimDates: ["2024-11-25"], referenceDate: "2026-11-25", windowMonths: 24 }],
  ["1 day before 24M 2024-11-24", { claimDates: ["2024-11-24"], referenceDate: "2026-11-25", windowMonths: 24 }],
  ["1 day after 24M 2024-11-26", { claimDates: ["2024-11-26"], referenceDate: "2026-11-25", windowMonths: 24 }],
  ["same day as eval 2026-11-25", { claimDates: ["2026-11-25"], referenceDate: "2026-11-25", windowMonths: 24 }],
  ["future claim 2026-11-26", { claimDates: ["2026-11-26"], referenceDate: "2026-11-25", windowMonths: 24 }],
  ["list with null item", { claimDates: ["2025-06-01", null], referenceDate: "2026-11-25", windowMonths: 24 }],
  ["null list", { claimDates: null, referenceDate: "2026-11-25", windowMonths: 24 }],
];
for (const [lbl, ctx] of bkm02Cases) {
  try {
    console.log(lbl, "=>", JSON.stringify(evaluate(bkm02, ctx)));
  } catch (e) {
    console.log(lbl, "ERR:", e.message);
  }
}

console.log("=== D07 NULL/ZERO INSURED VALUE PROBE ===");
for (const iv of [null, 0, -100000]) {
  try {
    console.log("insuredValue =", iv, "=>", JSON.stringify(evaluate("decimal(max(500000, insuredValue * 0.004), 0)", { insuredValue: iv })));
  } catch (e) {
    console.log("insuredValue =", iv, "ERR:", e.message);
  }
}
