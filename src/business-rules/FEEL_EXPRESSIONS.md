# FEEL Expressions & Engine Validation — Scenario B

**FEEL Engine:** `feelin@8.2.2` (the official bpmn-io / Camunda DMN 1.3 FEEL engine)  
**Note on Duration Semantics:** In DMN 1.3 FEEL, `date(a) - date(b)` yields a *days-and-time duration* (`P...D`), which suffers leap-year drift when divided by `365.25` (e.g., `2026-11-25 - 2001-11-25 = 9131 days`, `floor(9131 / 365.25) = 24` instead of `25`). Therefore, `BKM01` uses `years and months duration(date(targetDate), date(referenceDate)).years`, while `BKM02` subtracts calendar duration `duration("P" + string(windowMonths) + "M")` for exact month-boundary recency.

---

## 1. Six Distinct FEEL Expressions Covering All Five Categories (`18 / 18` Tests)

| ID | Category | Location | Exact FEEL Expression | Output Type |
|---|---|---|---|---|
| **FEEL-01** | Range condition (interval notation) | `D01` (`R-D01-03`, `R-D01-04`) & `D04` (`R-D04-05`) | `driverAge in [17..24]` | `boolean` |
| **FEEL-02** | List membership condition | `D03` (`R-D03-01`), `D07`, & Vehicle Risk | `(vehicleType in ["MOTORCYCLE", "CAR"]) and (performanceClass in ["SPORT", "HIGH_PERFORMANCE"])` | `boolean` |
| **FEEL-03** | Built-in function call (`max`, `decimal`) | `D07` & `D09` (`R-D09-05`) | `decimal(max(450000, insuredValue * 0.025) * (1 + totalRiskLoading), 0)` | `number` |
| **FEEL-04** | Date/duration arithmetic (`years and months duration`) | `BKM01` (`calculateAgeInYears`) | `if targetDate = null or referenceDate = null then null else if date(targetDate) > date(referenceDate) then -1 else years and months duration(date(targetDate), date(referenceDate)).years` | `number` |
| **FEEL-05** | Date/duration arithmetic + Built-in `count` (`P24M`) | `BKM02` (`countRecentClaims`) | `count(claimDates[date(item) >= (date(referenceDate) - duration("P24M")) and date(item) <= date(referenceDate)])` | `number` |
| **FEEL-06** | Compound expression (`if ... then ... else` + logical ops) | `D05` hierarchical policy expression | `if vehicleEligibility = "INELIGIBLE" or driverRisk = "INELIGIBLE" then "DECLINE" else if claimsRisk = "UNKNOWN" or driverRisk = "UNKNOWN" or claimsRisk = "HIGH" or (driverRisk = "HIGH" and (vehicleRisk = "HIGH" or claimsRisk = "MEDIUM")) then "REFER" else "ACCEPT"` | `string` |

---

## 2. Stage 5 Edge-Case & Null Propagation Verification (`feelin@8.2.2`)

- **Future DOB (`dateOfBirth > evaluationDate`):** `BKM01` returns `-1`, mapped explicitly by `D01` `R-D01-02 (< 0)` to `"INELIGIBLE"` -> `"DECLINE"` (never treated as a valid age).
- **Missing DOB (`dateOfBirth = null`):** `BKM01` returns `null`, mapped by `D01` `R-D01-01 (null)` to `"UNKNOWN"` -> `"REFER"`.
- **Claim Recency Boundary (`referenceDate = "2026-11-25"`, `P24M = 2024-11-25`):** `"2024-11-26"` (inside) -> counted; `"2024-11-25"` (exact boundary) -> counted; `"2024-11-24"` (1 day older, outside) -> excluded (`0` counted).
- **Null / Empty / Unsupported `coverType`:** `unaryTest('null, ""', {"?": ...})` matches both `null` and blank string `""` (`PENDING_INFORMATION`) with `0` warnings prior to `not("TPO", "THIRD_PARTY_ONLY", "COMPREHENSIVE")` (`INVALID_INPUT`). Output `null` evaluates with `0` warnings.
- **Numeric Precision:** `decimal(..., 0)` prevents IEEE-754 under-truncation (`200M * 0.018 = 3,599,999.9999999995 -> 3600000`).

*(Full test contexts and pass results are recorded in `tests/test-results/TEST_RESULTS.json` and `tests/test-results/INDEPENDENT_EXECUTION_RESULTS.json`.)*
