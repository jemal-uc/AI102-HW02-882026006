# Decision Tables Specification — Scenario B (`AsuransiNusantara`)

All 9 decision tables (`D01`–`D09`) below are derived identically from `src/specification/CANONICAL_DECISION_SPECIFICATION.json`. Every table guarantees **100% completeness** (zero silent fall-throughs) and deliberate **hit-policy semantics**.

---

## Summary of Hit Policies & Justifications

| Decision | Hit Policy | Rationale | Completeness & Overlap Handling |
|---|---|---|---|
| `D01` Driver Risk Assessment | `UNIQUE (U)` | Age intervals `null`, `<17`, `[17..24]`, `[25..65]`, `>65` are strictly disjoint. | Zero overlaps; `null` and negative (`-1` future DOB) explicitly handled. |
| `D02` Claims Risk Assessment | `FIRST (F)` | Missing-history guard (`not(true)`) must precede claim-count rules so `false`/`null` is never treated as `0` claims. | `R-D02-01` catches `false`/`null`; `R-D02-02` catches `null` list; `0`, `1`, `>=2` cover all non-negative integers. |
| `D03` Vehicle Eligibility Assessment | `FIRST (F)` | Hard rejection gates (`type`, `null`, `<0`, `>15`, `<=0` cc/value) short-circuit before `ELIGIBLE`. | Multi-column `INELIGIBLE` gates overlap intentionally (e.g., old + invalid cc); `FIRST` ensures deterministic rejection. |
| `D04` Vehicle Risk Assessment | `FIRST (F)` | Risk escalation hierarchy: `HIGH` (`HIGH_PERFORMANCE`, `>250cc` MC, `>2500cc` Car, `SPORT` 151–250cc MC) precedes `MEDIUM` (`151–250cc`, `1501–2500cc`, `SPORT`, `>10` yrs) and `LOW`. | Overlapping risk traits resolve upward to the highest matching severity; `R-D04-10` catch-all ensures completeness. |
| `D05` Underwriting Decision | `FIRST (F)` | Strict underwriting hierarchy **`DECLINE > REFER > ACCEPT`**. Ineligible vehicles/drivers cannot be accepted by downstream rows. | `R-D05-01..03` (`DECLINE`) precede `R-D05-04..08` (`REFER`), followed by `R-D05-09` (`ACCEPT`) and `R-D05-10` fallback. |
| `D06` Inspection Decision | `FIRST (F)` | `DECLINE -> NOT_APPLICABLE` must short-circuit value/age inspection triggers. | `R-D06-01` precedes Rp500M (`R-D06-02`) and older Comprehensive (`R-D06-03`); `R-D06-04..05` cover `NOT_REQUIRED`; `R-D06-06` fallback. |
| `D07` Base Premium Calculation | `FIRST (F)` | 12 mutually exclusive `(vehicleType, engineCC, coverType)` tariff cells + 1 fallback row (`0`) for invalid inputs. | `R-D07-01..12` partition valid domain `(0..150]`, `(150..250]`, `>250` (MC) and `(0..1500]`, `(1500..2500]`, `>2500` (Car); `R-D07-13` catches invalid data. |
| `D08` Risk Loading Calculation | `COLLECT SUM (C+)` | Additive stacking of 4 orthogonal loading components (`driverRisk`, `claimsRisk`, `vehicleRisk`, `performanceClass`). | Each dimension has mutually exclusive exhaustive rows (including explicit `0.00` rows), guaranteeing exactly 4 hits summed deterministically. |
| `D09` Final Premium Calculation | `UNIQUE (U)` | Three mutually exclusive dispositions (`DECLINE`, `ACCEPT`, `REFER`). | Exhaustive over `tUnderwritingDecision`. |

---

## Complete Decision Tables

### D01 — Driver Risk Assessment (`UNIQUE`)
- **Input:** `driverAge = calculateAgeInYears(dateOfBirth, evaluationDate)` (`number`)
- **Output:** `driverRisk` (`tDriverRisk`: `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"INELIGIBLE"`, `"UNKNOWN"`)

| Rule | `driverAge` | `driverRisk` | Annotation |
|---|---|---|---|
| `R-D01-01` | `null` | `"UNKNOWN"` | Missing or malformed DOB or evaluationDate |
| `R-D01-02` | `< 0` | `"INELIGIBLE"` | Explicit invalid future DOB sentinel (`-1`) |
| `R-D01-03` | `[0..17)` | `"INELIGIBLE"` | Underage (`<17` Indonesian SIM A/C minimum) |
| `R-D01-04` | `[17..24]` | `"HIGH"` | Young driver (17–24 inclusive) |
| `R-D01-05` | `[25..65]` | `"LOW"` | Prime adult driver (25–65 inclusive) |
| `R-D01-06` | `> 65` | `"MEDIUM"` | Senior driver (>65) |

### D02 — Claims Risk Assessment (`FIRST`)
- **Inputs:** `claimsHistoryAvailable` (`boolean`), `recentClaims = countRecentClaims(claimDates, evaluationDate, 24)` (`number`)
- **Output:** `claimsRisk` (`tClaimsRisk`: `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"UNKNOWN"`)

| Rule | `claimsHistoryAvailable` | `recentClaims` | `claimsRisk` | Annotation |
|---|---|---|---|---|
| `R-D02-01` | `not(true)` | `-` | `"UNKNOWN"` | Missing/false history never treated as clean |
| `R-D02-02` | `true` | `null` | `"UNKNOWN"` | Null `claimDates` or missing `evaluationDate` |
| `R-D02-03` | `true` | `0` | `"LOW"` | Verified 0 claims in 24 months |
| `R-D02-04` | `true` | `1` | `"MEDIUM"` | Verified 1 claim in 24 months |
| `R-D02-05` | `true` | `>= 2` | `"HIGH"` | Verified 2+ claims in 24 months |

### D03 — Vehicle Eligibility Assessment (`FIRST`)
- **Inputs:** `vehicleType` (`tVehicleType`), `vehicleAge = calculateAgeInYears(vehicleManufactureDate, evaluationDate)` (`number`), `engineCC` (`number`), `insuredValue` (`number`)
- **Output:** `vehicleEligibility` (`tVehicleEligibility`: `"ELIGIBLE"`, `"INELIGIBLE"`)

| Rule | `vehicleType` | `vehicleAge` | `engineCC` | `insuredValue` | `vehicleEligibility` | Annotation |
|---|---|---|---|---|---|---|
| `R-D03-01` | `not("MOTORCYCLE", "CAR")` | `-` | `-` | `-` | `"INELIGIBLE"` | Unsupported or null vehicle type |
| `R-D03-02` | `-` | `null` | `-` | `-` | `"INELIGIBLE"` | Missing date |
| `R-D03-03` | `-` | `< 0` | `-` | `-` | `"INELIGIBLE"` | Future manufacture date |
| `R-D03-04` | `-` | `> 15` | `-` | `-` | `"INELIGIBLE"` | Very old vehicle (>15 years) |
| `R-D03-05` | `-` | `-` | `null, <= 0` | `-` | `"INELIGIBLE"` | Invalid engine capacity |
| `R-D03-06` | `-` | `-` | `-` | `null, <= 0` | `"INELIGIBLE"` | Invalid insured value |
| `R-D03-07` | `"MOTORCYCLE", "CAR"` | `[0..15]` | `> 0` | `> 0` | `"ELIGIBLE"` | Eligible vehicle |

### D04 — Vehicle Risk Assessment (`FIRST`)
- **Inputs:** `vehicleType`, `engineCC`, `performanceClass`, `vehicleAge = calculateAgeInYears(vehicleManufactureDate, evaluationDate)`
- **Output:** `vehicleRisk` (`tVehicleRisk`: `"LOW"`, `"MEDIUM"`, `"HIGH"`)

| Rule | `vehicleType` | `engineCC` | `performanceClass` | `vehicleAge` | `vehicleRisk` | Annotation |
|---|---|---|---|---|---|---|
| `R-D04-00a` | `not("MOTORCYCLE", "CAR")` | `-` | `-` | `-` | `"HIGH"` | Conservative guard for missing/invalid vehicleType |
| `R-D04-00b` | `-` | `null, <= 0` | `-` | `-` | `"HIGH"` | Conservative guard for missing/non-positive engineCC |
| `R-D04-00c` | `-` | `-` | `not("STANDARD", "SPORT", "HIGH_PERFORMANCE")` | `-` | `"HIGH"` | Conservative guard for missing/invalid performanceClass |
| `R-D04-00d` | `-` | `-` | `-` | `null, < 0` | `"HIGH"` | Conservative guard for missing/future vehicleAge (`-1`) |
| `R-D04-01` | `-` | `-` | `"HIGH_PERFORMANCE"` | `-` | `"HIGH"` | High-performance classification |
| `R-D04-02` | `"MOTORCYCLE"` | `> 250` | `-` | `-` | `"HIGH"` | Big-bike (>250cc) |
| `R-D04-03` | `"CAR"` | `> 2500` | `-` | `-` | `"HIGH"` | Large-displacement car (>2500cc) |
| `R-D04-04` | `"MOTORCYCLE"` | `(150..250]` | `"SPORT"` | `-` | `"HIGH"` | Mid-size sport motorcycle |
| `R-D04-05` | `"MOTORCYCLE"` | `(150..250]` | `-` | `-` | `"MEDIUM"` | Mid-size motorcycle |
| `R-D04-06` | `"CAR"` | `(1500..2500]` | `-` | `-` | `"MEDIUM"` | Mid-size car / SUV |
| `R-D04-07` | `-` | `-` | `"SPORT"` | `-` | `"MEDIUM"` | Sport trim on compact engine |
| `R-D04-08` | `-` | `-` | `-` | `> 10` | `"MEDIUM"` | Older vehicle (>10 years) |
| `R-D04-09` | `"MOTORCYCLE", "CAR"` | `> 0` | `"STANDARD"` | `[0..10]` | `"LOW"` | Standard compact vehicle <=10 yrs |
| `R-D04-10` | `-` | `-` | `-` | `-` | `"HIGH"` | Conservative fallback |

### D05 — Underwriting Decision (`FIRST`)
- **Inputs:** `driverRisk`, `claimsRisk`, `vehicleEligibility`, `vehicleRisk`
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

### D06 — Inspection Decision (`FIRST`)
- **Inputs:** `underwritingDecision`, `insuredValue`, `coverType`, `vehicleAge = calculateAgeInYears(vehicleManufactureDate, evaluationDate)`
- **Output:** `inspectionDecision` (`tInspectionDecision`: `"REQUIRED"`, `"NOT_REQUIRED"`, `"NOT_APPLICABLE"`)

| Rule | `underwritingDecision` | `insuredValue` | `coverType` | `vehicleAge` | `inspectionDecision` |
|---|---|---|---|---|---|
| `R-D06-01` | `"DECLINE"` | `-` | `-` | `-` | `"NOT_APPLICABLE"` |
| `R-D06-02` | `"ACCEPT", "REFER"` | `>= 500000000` | `-` | `-` | `"REQUIRED"` |
| `R-D06-03` | `"ACCEPT", "REFER"` | `-` | `"COMPREHENSIVE"` | `> 10` | `"REQUIRED"` |
| `R-D06-04` | `"ACCEPT", "REFER"` | `< 500000000` | `"TPO", "COMPREHENSIVE"` | `[0..10]` | `"NOT_REQUIRED"` |
| `R-D06-05` | `"ACCEPT", "REFER"` | `< 500000000` | `"TPO"` | `> 10` | `"NOT_REQUIRED"` |
| `R-D06-06` | `-` | `-` | `-` | `-` | `"REQUIRED"` |

### D07 — Base Premium Calculation (`FIRST`)
- **Inputs:** `vehicleType`, `engineCC`, `coverType`, `insuredValue` (`number`, IDR)
- **Output:** `basePremium` (`number`, IDR)

| Rule | `vehicleType` | `engineCC` | `coverType` | `insuredValue` | `basePremium` (FEEL Expression) |
|---|---|---|---|---|---|
| `R-D07-00` | `-` | `-` | `-` | `null, <= 0` | `0` |
| `R-D07-01` | `"MOTORCYCLE"` | `(0..150]` | `"TPO"` | `> 0` | `decimal(max(150000, insuredValue * 0.005), 0)` |
| `R-D07-02` | `"MOTORCYCLE"` | `(0..150]` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(300000, insuredValue * 0.020), 0)` |
| `R-D07-03` | `"MOTORCYCLE"` | `(150..250]` | `"TPO"` | `> 0` | `decimal(max(200000, insuredValue * 0.007), 0)` |
| `R-D07-04` | `"MOTORCYCLE"` | `(150..250]` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(450000, insuredValue * 0.025), 0)` |
| `R-D07-05` | `"MOTORCYCLE"` | `> 250` | `"TPO"` | `> 0` | `decimal(max(350000, insuredValue * 0.010), 0)` |
| `R-D07-06` | `"MOTORCYCLE"` | `> 250` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(750000, insuredValue * 0.032), 0)` |
| `R-D07-07` | `"CAR"` | `(0..1500]` | `"TPO"` | `> 0` | `decimal(max(500000, insuredValue * 0.004), 0)` |
| `R-D07-08` | `"CAR"` | `(0..1500]` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(1500000, insuredValue * 0.018), 0)` |
| `R-D07-09` | `"CAR"` | `(1500..2500]` | `"TPO"` | `> 0` | `decimal(max(650000, insuredValue * 0.005), 0)` |
| `R-D07-10` | `"CAR"` | `(1500..2500]` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(2000000, insuredValue * 0.022), 0)` |
| `R-D07-11` | `"CAR"` | `> 2500` | `"TPO"` | `> 0` | `decimal(max(850000, insuredValue * 0.006), 0)` |
| `R-D07-12` | `"CAR"` | `> 2500` | `"COMPREHENSIVE"` | `> 0` | `decimal(max(2500000, insuredValue * 0.028), 0)` |
| `R-D07-13` | `-` | `-` | `-` | `-` | `0` |

### D08 — Risk Loading Calculation (`COLLECT SUM / C+`)
- **Inputs:** `driverRisk`, `claimsRisk`, `vehicleRisk`, `performanceClass`
- **Output:** `totalRiskLoading` (`number`, decimal fraction summed via `C+`)

| Rule | `driverRisk` | `claimsRisk` | `vehicleRisk` | `performanceClass` | Loading |
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

### D09 — Final Premium Calculation (`UNIQUE`)
- **Input:** `underwritingDecision` (uses `basePremium`, `totalRiskLoading`)
- **Output:** `finalPremium` (`number`, IDR)

| Rule | `underwritingDecision` | `finalPremium` (FEEL Expression) |
|---|---|---|
| `R-D09-01` | `"DECLINE"` | `0` |
| `R-D09-02` | `"ACCEPT"` | `decimal(basePremium * (1 + totalRiskLoading), 0)` |
| `R-D09-03` | `"REFER"` | `decimal(basePremium * (1 + totalRiskLoading), 0)` |
