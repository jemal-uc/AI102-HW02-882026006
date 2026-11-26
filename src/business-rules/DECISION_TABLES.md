# Decision Tables Specification — Scenario B (`AsuransiNusantara`)

All **10 decision tables (`D01`–`D10`, 94 rules total)** below match `src/specification/CANONICAL_DECISION_SPECIFICATION.json` and `src/decision-model/AsuransiNusantara.dmn` 1-to-1. Every table declares explicit input types and output types, guarantees **100% completeness**, and eliminates unsafe `Rp0` premium fallbacks.

---

## Summary of Hit Policies & Justifications

| Decision | Hit Policy | Rationale | Completeness & Overlap Handling |
|---|---|---|---|
| `D01` Driver Risk Assessment | `UNIQUE (U)` | Age intervals `null`, `<0`, `[0..17)`, `[17..24]`, `[25..65]`, `>65` are strictly disjoint. | Zero overlaps; `null` and `-1` (future DOB) explicitly separated. |
| `D02` Claims Risk Assessment | `FIRST (F)` | Missing-history guard (`not(true)`) must precede claim-count rules so `false`/`null` never becomes `0` claims. | `R-D02-01` catches `false`/`null`; `R-D02-02` catches `null` list; `0`, `1`, `>=2` cover non-negative counts. |
| `D03` Vehicle Eligibility Assessment | `FIRST (F)` | Hard rejection gates (`type`, `null`/`<0`/`>15` age, `<=0` cc/value) short-circuit before `ELIGIBLE`; missing `insuredValue` (`null`) defers to `D10`. | Overlapping `INELIGIBLE` gates resolve deterministically via `FIRST`. |
| `D04` Vehicle Risk Assessment | `FIRST (F)` | Escalation hierarchy (`HIGH > MEDIUM > LOW`) preceded by conservative `HIGH` guards (`R-D04-00a..00d`). | Overlapping traits resolve upward; `R-D04-10` catch-all guarantees completeness. |
| `D05` Underwriting Decision | `FIRST (F)` | Strict underwriting hierarchy **`DECLINE > REFER > ACCEPT`**, independent of `coverType`. | `R-D05-01..03` (`DECLINE`) precede `R-D05-04..08` (`REFER`), then `R-D05-09` (`ACCEPT`) and `R-D05-10` fallback. |
| `D06` Inspection Decision | `FIRST (F)` | `DECLINE -> NOT_APPLICABLE` short-circuits inspection triggers; missing cover/value falls back conservatively to `REQUIRED`. | `R-D06-01` precedes `>=Rp500M` (`R-D06-02`) and older `COMPREHENSIVE` (`R-D06-03`). |
| `D07` Base Premium Calculation | `FIRST (F)` | 12 mutually exclusive `(vehicleType, engineCC, coverType)` tariff cells (`TPO` & `THIRD_PARTY_ONLY` mapped identically) + `null` guards (`R-D07-00`, `R-D07-13`). | Invalid/missing pricing inputs return `null`, never `0`. |
| `D08` Risk Loading Calculation | `COLLECT SUM (C+)` | Additive stacking of 4 orthogonal dimensions (`driverRisk`, `claimsRisk`, `vehicleRisk`, `performanceClass`). | Each dimension is mutually exclusive and exhaustive (always 4 hits). |
| `D09` Final Premium Calculation | `FIRST (F)` | Enforces `D05 = "ACCEPT"` **and** `D10 = "READY"` **and** `D07 > 0` before computing `decimal(basePremium * (1 + totalRiskLoading), 0)`. | `DECLINE`, `REFER`, non-`READY`, and invalid `basePremium` strictly return `null` (`6` rules). |
| `D10` Quote Readiness Assessment | `FIRST (F)` | Short-circuits `DECLINE` (`NOT_APPLICABLE`), then checks missing/blank inputs (`PENDING_INFORMATION`) **before** `not(...)` invalid-enum checks (`INVALID_INPUT`), then `READY`. | Explicit ordering prevents `null`/`""` from colliding with `not(...)` negation; `R-D10-12` guarantees completeness (`12` rules). |

---

## Complete Decision Tables

### D01 — Driver Risk Assessment (`UNIQUE`, 6 rules)
- **Input:** `driverAge = calculateAgeInYears(dateOfBirth, evaluationDate)` (`number`)
- **Output:** `driverRisk` (`tDriverRisk`: `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"INELIGIBLE"`, `"UNKNOWN"`)

| Rule | `driverAge` (`number`) | `driverRisk` (`tDriverRisk`) | Annotation |
|---|---|---|---|
| `R-D01-01` | `null` | `"UNKNOWN"` | Missing or malformed DOB or evaluationDate |
| `R-D01-02` | `< 0` | `"INELIGIBLE"` | Explicit invalid future DOB sentinel (`-1`) |
| `R-D01-03` | `[0..17)` | `"INELIGIBLE"` | Underage (`<17` min SIM A/C per UU No. 22/2009 Art. 81(2)(a)) |
| `R-D01-04` | `[17..24]` | `"HIGH"` | Young driver (17–24 inclusive) |
| `R-D01-05` | `[25..65]` | `"LOW"` | Prime adult driver (25–65 inclusive) |
| `R-D01-06` | `> 65` | `"MEDIUM"` | Senior driver (>65) |

### D02 — Claims Risk Assessment (`FIRST`, 5 rules)
- **Inputs:** `claimsHistoryAvailable` (`boolean`), `recentClaims = countRecentClaims(claimDates, evaluationDate, 24)` (`number`)
- **Output:** `claimsRisk` (`tClaimsRisk`: `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"UNKNOWN"`)

| Rule | `claimsHistoryAvailable` (`boolean`) | `recentClaims` (`number`) | `claimsRisk` (`tClaimsRisk`) | Annotation |
|---|---|---|---|---|
| `R-D02-01` | `not(true)` | `-` | `"UNKNOWN"` | Missing/false history never treated as clean |
| `R-D02-02` | `true` | `null` | `"UNKNOWN"` | Null `claimDates` or missing `evaluationDate` |
| `R-D02-03` | `true` | `0` | `"LOW"` | Verified 0 claims in 24 months |
| `R-D02-04` | `true` | `1` | `"MEDIUM"` | Verified 1 claim in 24 months |
| `R-D02-05` | `true` | `>= 2` | `"HIGH"` | Verified 2+ claims in 24 months |

### D03 — Vehicle Eligibility Assessment (`FIRST`, 7 rules)
- **Inputs:** `vehicleType` (`tVehicleType`), `vehicleAge = calculateAgeInYears(vehicleManufactureDate, evaluationDate)` (`number`), `engineCC` (`number`), `insuredValue` (`number`)
- **Output:** `vehicleEligibility` (`tVehicleEligibility`: `"ELIGIBLE"`, `"INELIGIBLE"`)

| Rule | `vehicleType` (`tVehicleType`) | `vehicleAge` (`number`) | `engineCC` (`number`) | `insuredValue` (`number`) | `vehicleEligibility` (`tVehicleEligibility`) | Annotation |
|---|---|---|---|---|---|---|
| `R-D03-01` | `not("MOTORCYCLE", "CAR")` | `-` | `-` | `-` | `"INELIGIBLE"` | Unsupported or null vehicle type |
| `R-D03-02` | `-` | `null` | `-` | `-` | `"INELIGIBLE"` | Missing date |
| `R-D03-03` | `-` | `< 0` | `-` | `-` | `"INELIGIBLE"` | Future manufacture date |
| `R-D03-04` | `-` | `> 15` | `-` | `-` | `"INELIGIBLE"` | Very old vehicle (>15 years) |
| `R-D03-05` | `-` | `-` | `null, <= 0` | `-` | `"INELIGIBLE"` | Invalid engine capacity |
| `R-D03-06` | `-` | `-` | `-` | `<= 0` | `"INELIGIBLE"` | Invalid non-positive valuation (`null` deferred to `D10`) |
| `R-D03-07` | `"MOTORCYCLE", "CAR"` | `[0..15]` | `> 0` | `null, > 0` | `"ELIGIBLE"` | Eligible vehicle |

### D04 — Vehicle Risk Assessment (`FIRST`, 14 rules)
- **Inputs:** `vehicleType` (`tVehicleType`), `engineCC` (`number`), `performanceClass` (`tPerformanceClass`), `vehicleAge = calculateAgeInYears(vehicleManufactureDate, evaluationDate)` (`number`)
- **Output:** `vehicleRisk` (`tVehicleRisk`: `"LOW"`, `"MEDIUM"`, `"HIGH"`)

| Rule | `vehicleType` (`tVehicleType`) | `engineCC` (`number`) | `performanceClass` (`tPerformanceClass`) | `vehicleAge` (`number`) | `vehicleRisk` (`tVehicleRisk`) | Annotation |
|---|---|---|---|---|---|---|
| `R-D04-00a` | `not("MOTORCYCLE", "CAR")` | `-` | `-` | `-` | `"HIGH"` | Guard: missing/invalid vehicleType |
| `R-D04-00b` | `-` | `null, <= 0` | `-` | `-` | `"HIGH"` | Guard: missing/non-positive engineCC |
| `R-D04-00c` | `-` | `-` | `not("STANDARD", "SPORT", "HIGH_PERFORMANCE")` | `-` | `"HIGH"` | Guard: missing/invalid performanceClass |
| `R-D04-00d` | `-` | `-` | `-` | `null, < 0` | `"HIGH"` | Guard: missing/future vehicleAge (`-1`) |
| `R-D04-01` | `-` | `-` | `"HIGH_PERFORMANCE"` | `-` | `"HIGH"` | High-performance classification |
| `R-D04-02` | `"MOTORCYCLE"` | `> 250` | `-` | `-` | `"HIGH"` | Large motorcycle (>250cc) |
| `R-D04-03` | `"CAR"` | `> 2500` | `-` | `-` | `"HIGH"` | Large car (>2500cc) |
| `R-D04-04` | `"MOTORCYCLE"` | `(150..250]` | `"SPORT"` | `-` | `"HIGH"` | Mid-size sport motorcycle |
| `R-D04-05` | `"MOTORCYCLE"` | `(150..250]` | `-` | `-` | `"MEDIUM"` | Mid-size motorcycle |
| `R-D04-06` | `"CAR"` | `(1500..2500]` | `-` | `-` | `"MEDIUM"` | Mid-size car / SUV |
| `R-D04-07` | `-` | `-` | `"SPORT"` | `-` | `"MEDIUM"` | Sport trim on compact engine |
| `R-D04-08` | `-` | `-` | `-` | `> 10` | `"MEDIUM"` | Older vehicle (>10 years) |
| `R-D04-09` | `"MOTORCYCLE", "CAR"` | `> 0` | `"STANDARD"` | `[0..10]` | `"LOW"` | Standard compact vehicle <=10 yrs |
| `R-D04-10` | `-` | `-` | `-` | `-` | `"HIGH"` | Conservative fallback |

### D05 — Underwriting Decision (`FIRST`, 10 rules)
- **Inputs:** `driverRisk` (`tDriverRisk`), `claimsRisk` (`tClaimsRisk`), `vehicleEligibility` (`tVehicleEligibility`), `vehicleRisk` (`tVehicleRisk`)
- **Output:** `underwritingDecision` (`tUnderwritingDecision`: `"ACCEPT"`, `"REFER"`, `"DECLINE"`)

| Rule | `driverRisk` | `claimsRisk` | `vehicleEligibility` | `vehicleRisk` | `underwritingDecision` |
|---|---|---|---|---|---|
| `R-D05-01` | `-` | `-` | `"INELIGIBLE"` | `-` | `"DECLINE"` |
| `R-D05-02` | `"INELIGIBLE"` | `-` | `-` | `-` | `"DECLINE"` |
| `R-D05-03` | `"HIGH"` | `"HIGH"` | `"ELIGIBLE"` | `"HIGH"` | `"DECLINE"` |
| `R-D05-04` | `"UNKNOWN"` | `-` | `"ELIGIBLE"` | `-` | `"REFER"` |
| `R-D05-05` | `-` | `"UNKNOWN"` | `"ELIGIBLE"` | `-` | `"REFER"` |
| `R-D05-06` | `-` | `"HIGH"` | `"ELIGIBLE"` | `-` | `"REFER"` |
| `R-D05-07` | `"HIGH"` | `-` | `"ELIGIBLE"` | `"HIGH"` | `"REFER"` |
| `R-D05-08` | `"HIGH"` | `"MEDIUM"` | `"ELIGIBLE"` | `-` | `"REFER"` |
| `R-D05-09` | `"LOW", "MEDIUM", "HIGH"` | `"LOW", "MEDIUM"` | `"ELIGIBLE"` | `"LOW", "MEDIUM", "HIGH"` | `"ACCEPT"` |
| `R-D05-10` | `-` | `-` | `-` | `-` | `"REFER"` |

### D06 — Inspection Decision (`FIRST`, 6 rules)
- **Inputs:** `underwritingDecision` (`tUnderwritingDecision`), `insuredValue` (`number`), `coverType` (`tCoverType`), `vehicleAge = calculateAgeInYears(vehicleManufactureDate, evaluationDate)` (`number`)
- **Output:** `inspectionDecision` (`tInspectionDecision`: `"REQUIRED"`, `"NOT_REQUIRED"`, `"NOT_APPLICABLE"`)

| Rule | `underwritingDecision` | `insuredValue` (`number`) | `coverType` (`tCoverType`) | `vehicleAge` (`number`) | `inspectionDecision` |
|---|---|---|---|---|---|
| `R-D06-01` | `"DECLINE"` | `-` | `-` | `-` | `"NOT_APPLICABLE"` |
| `R-D06-02` | `"ACCEPT", "REFER"` | `>= 500000000` | `-` | `-` | `"REQUIRED"` |
| `R-D06-03` | `"ACCEPT", "REFER"` | `-` | `"COMPREHENSIVE"` | `> 10` | `"REQUIRED"` |
| `R-D06-04` | `"ACCEPT", "REFER"` | `< 500000000` | `"TPO", "THIRD_PARTY_ONLY", "COMPREHENSIVE"` | `[0..10]` | `"NOT_REQUIRED"` |
| `R-D06-05` | `"ACCEPT", "REFER"` | `< 500000000` | `"TPO", "THIRD_PARTY_ONLY"` | `> 10` | `"NOT_REQUIRED"` |
| `R-D06-06` | `-` | `-` | `-` | `-` | `"REQUIRED"` |

### D07 — Base Premium Calculation (`FIRST`, 14 rules)
- **Inputs:** `vehicleType` (`tVehicleType`), `engineCC` (`number`), `coverType` (`tCoverType`), `insuredValue` (`number`, IDR)
- **Output:** `basePremium` (`number`, IDR — or `null` if uncalculable)

| Rule | `vehicleType` | `engineCC` | `coverType` | `insuredValue` | `basePremium` (FEEL Expression) |
|---|---|---|---|---|---|
| `R-D07-00` | `-` | `-` | `-` | `null, <= 0` | `null` |
| `R-D07-01` | `"MOTORCYCLE"` | `(0..150]` | `"TPO", "THIRD_PARTY_ONLY"` | `> 0` | `decimal(max(150000, insuredValue * 0.005), 0)` |
| `R-D07-02` | `"MOTORCYCLE"` | `(0..150]` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(300000, insuredValue * 0.020), 0)` |
| `R-D07-03` | `"MOTORCYCLE"` | `(150..250]` | `"TPO", "THIRD_PARTY_ONLY"` | `> 0` | `decimal(max(200000, insuredValue * 0.007), 0)` |
| `R-D07-04` | `"MOTORCYCLE"` | `(150..250]` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(450000, insuredValue * 0.025), 0)` |
| `R-D07-05` | `"MOTORCYCLE"` | `> 250` | `"TPO", "THIRD_PARTY_ONLY"` | `> 0` | `decimal(max(350000, insuredValue * 0.010), 0)` |
| `R-D07-06` | `"MOTORCYCLE"` | `> 250` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(750000, insuredValue * 0.032), 0)` |
| `R-D07-07` | `"CAR"` | `(0..1500]` | `"TPO", "THIRD_PARTY_ONLY"` | `> 0` | `decimal(max(500000, insuredValue * 0.004), 0)` |
| `R-D07-08` | `"CAR"` | `(0..1500]` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(1500000, insuredValue * 0.018), 0)` |
| `R-D07-09` | `"CAR"` | `(1500..2500]` | `"TPO", "THIRD_PARTY_ONLY"` | `> 0` | `decimal(max(650000, insuredValue * 0.005), 0)` |
| `R-D07-10` | `"CAR"` | `(1500..2500]` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(2000000, insuredValue * 0.022), 0)` |
| `R-D07-11` | `"CAR"` | `> 2500` | `"TPO", "THIRD_PARTY_ONLY"` | `> 0` | `decimal(max(850000, insuredValue * 0.006), 0)` |
| `R-D07-12` | `"CAR"` | `> 2500` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(2500000, insuredValue * 0.028), 0)` |
| `R-D07-13` | `-` | `-` | `-` | `-` | `null` |

### D08 — Risk Loading Calculation (`COLLECT SUM / C+`, 14 rules)
- **Inputs:** `driverRisk` (`tDriverRisk`), `claimsRisk` (`tClaimsRisk`), `vehicleRisk` (`tVehicleRisk`), `performanceClass` (`tPerformanceClass`)
- **Output:** `totalRiskLoading` (`number`, decimal fraction summed via `C+`)

| Rule | `driverRisk` | `claimsRisk` | `vehicleRisk` | `performanceClass` | `totalRiskLoading` |
|---|---|---|---|---|---|
| `R-D08-01` | `"HIGH"` | `-` | `-` | `-` | `0.25` |
| `R-D08-02` | `"MEDIUM"` | `-` | `-` | `-` | `0.10` |
| `R-D08-03` | `"LOW", "INELIGIBLE", "UNKNOWN"` | `-` | `-` | `-` | `0.00` |
| `R-D08-04` | `-` | `"MEDIUM"` | `-` | `-` | `0.20` |
| `R-D08-05` | `-` | `"HIGH"` | `-` | `-` | `0.40` |
| `R-D08-06` | `-` | `"UNKNOWN"` | `-` | `-` | `0.25` |
| `R-D08-07` | `-` | `"LOW"` | `-` | `-` | `0.00` |
| `R-D08-08` | `-` | `-` | `"MEDIUM"` | `-` | `0.10` |
| `R-D08-09` | `-` | `-` | `"HIGH"` | `-` | `0.20` |
| `R-D08-10` | `-` | `-` | `"LOW"` | `-` | `0.00` |
| `R-D08-11` | `-` | `-` | `-` | `"SPORT"` | `0.15` |
| `R-D08-12` | `-` | `-` | `-` | `"HIGH_PERFORMANCE"` | `0.30` |
| `R-D08-13` | `-` | `-` | `-` | `"STANDARD"` | `0.00` |
| `R-D08-14` | `-` | `-` | `-` | `not("STANDARD", "SPORT", "HIGH_PERFORMANCE")` | `0.30` |

### D09 — Final Premium Calculation (`FIRST`, 6 rules)
- **Inputs:** `underwritingDecision` (`tUnderwritingDecision`), `quoteReadiness` (`tQuoteReadiness`), `basePremium` (`number`, uses `totalRiskLoading`)
- **Output:** `finalPremium` (`number`, IDR — or `null`)

| Rule | `underwritingDecision` (`tUnderwritingDecision`) | `quoteReadiness` (`tQuoteReadiness`) | `basePremium` (`number`) | `finalPremium` (`number`) | Annotation |
|---|---|---|---|---|---|
| `R-D09-01` | `"DECLINE"` | `-` | `-` | `null` | Declined policy produces no issued premium |
| `R-D09-02` | `"REFER"` | `-` | `-` | `null` | Referred application never auto-approves final quote |
| `R-D09-03` | `"ACCEPT"` | `not("READY")` | `-` | `null` | Pending or invalid pricing inputs prevent premium calculation |
| `R-D09-04` | `"ACCEPT"` | `"READY"` | `null, <= 0` | `null` | Guard on missing/non-positive intermediate basePremium |
| `R-D09-05` | `"ACCEPT"` | `"READY"` | `> 0` | `decimal(basePremium * (1 + totalRiskLoading), 0)` | Approved annual premium with additive risk loading |
| `R-D09-06` | `-` | `-` | `-` | `null` | Defensive fallback returning `null` |

### D10 — Quote Readiness Assessment (`FIRST`, 12 rules)
- **Inputs:** `underwritingDecision` (`tUnderwritingDecision`), `vehicleType` (`tVehicleType`), `engineCC` (`number`), `coverType` (`tCoverType`), `insuredValue` (`number`), `basePremium` (`number`)
- **Output:** `quoteReadiness` (`tQuoteReadiness`: `"READY"`, `"PENDING_INFORMATION"`, `"INVALID_INPUT"`, `"NOT_APPLICABLE"`)

| Rule | `underwritingDecision` | `vehicleType` | `engineCC` | `coverType` | `insuredValue` | `basePremium` | `quoteReadiness` | Annotation |
|---|---|---|---|---|---|---|---|---|
| `R-D10-01` | `"DECLINE"` | `-` | `-` | `-` | `-` | `-` | `"NOT_APPLICABLE"` | Declined risk excluded from quotation |
| `R-D10-02` | `"ACCEPT", "REFER"` | `null, ""` | `-` | `-` | `-` | `-` | `"PENDING_INFORMATION"` | Missing or blank vehicleType |
| `R-D10-03` | `"ACCEPT", "REFER"` | `-` | `null` | `-` | `-` | `-` | `"PENDING_INFORMATION"` | Missing engineCC |
| `R-D10-04` | `"ACCEPT", "REFER"` | `-` | `-` | `null, ""` | `-` | `-` | `"PENDING_INFORMATION"` | Missing/blank coverType (risk stays independent) |
| `R-D10-05` | `"ACCEPT", "REFER"` | `-` | `-` | `-` | `null` | `-` | `"PENDING_INFORMATION"` | Missing insuredValue |
| `R-D10-06` | `"ACCEPT", "REFER"` | `not("MOTORCYCLE", "CAR")` | `-` | `-` | `-` | `-` | `"INVALID_INPUT"` | Unsupported vehicleType |
| `R-D10-07` | `"ACCEPT", "REFER"` | `-` | `<= 0` | `-` | `-` | `-` | `"INVALID_INPUT"` | Non-positive engineCC |
| `R-D10-08` | `"ACCEPT", "REFER"` | `-` | `-` | `not("TPO", "THIRD_PARTY_ONLY", "COMPREHENSIVE")` | `-` | `-` | `"INVALID_INPUT"` | Unsupported coverType |
| `R-D10-09` | `"ACCEPT", "REFER"` | `-` | `-` | `-` | `<= 0` | `-` | `"INVALID_INPUT"` | Non-positive insuredValue |
| `R-D10-10` | `"ACCEPT", "REFER"` | `-` | `-` | `-` | `-` | `null, <= 0` | `"INVALID_INPUT"` | Uncalculable basePremium |
| `R-D10-11` | `"ACCEPT", "REFER"` | `"MOTORCYCLE", "CAR"` | `> 0` | `"TPO", "THIRD_PARTY_ONLY", "COMPREHENSIVE"` | `> 0` | `> 0` | `"READY"` | Complete, valid pricing inputs |
| `R-D10-12` | `-` | `-` | `-` | `-` | `-` | `-` | `"INVALID_INPUT"` | Defensive fallback |
