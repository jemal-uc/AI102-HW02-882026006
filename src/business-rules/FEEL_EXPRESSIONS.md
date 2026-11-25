# FEEL Expressions & Engine Validation — Scenario B

**FEEL Engine:** `feelin@8.2.2` (the official bpmn-io / Camunda DMN 1.3 FEEL engine)  
**Note on Duration Semantics:** In DMN 1.3 FEEL, `date(a) - date(b)` yields a *days-and-time duration* (`P...D`), which suffers leap-year drift when divided by `365.25` (e.g., `2026-11-25 - 2001-11-25 = 9131 days`, `floor(9131 / 365.25) = 24` instead of `25`). Therefore, `BKM01` uses `years and months duration(date(targetDate), date(referenceDate)).years`, while `BKM02` subtracts calendar duration `duration("P" + string(windowMonths) + "M")` for exact month-boundary recency.

---

## 1. Six Distinct FEEL Expressions Covering All Five Categories

| ID | Category | Location | Exact FEEL Expression | Output Type |
|---|---|---|---|---|
| **FEEL-01** | Range condition (interval notation) | `D01` (`R-D01-03`), `D04` (`R-D04-05`) | `driverAge in [17..24]` (and unary intervals `[17..24]`, `(150..250]`, `[0..15]`) | `boolean` |
| **FEEL-02** | List membership condition | `D03` (`R-D03-01`), Vehicle Risk | `(vehicleType in ["MOTORCYCLE", "CAR"]) and (performanceClass in ["SPORT", "HIGH_PERFORMANCE"])` | `boolean` |
| **FEEL-03** | Built-in function call (`max`, `decimal`) | `D07` (`R-D07-04`), `D09` (`R-D09-02`) | `decimal(max(450000, insuredValue * 0.025) * (1 + totalRiskLoading), 0)` | `number` |
| **FEEL-04** | Date/duration arithmetic (`years and months duration`) | `BKM01` (`calculateAgeInYears`) | `if date(targetDate) > date(referenceDate) then -1 else years and months duration(date(targetDate), date(referenceDate)).years` | `number` |
| **FEEL-05** | Date/duration arithmetic + Built-in `count` (`P24M`) | `BKM02` (`countRecentClaims`) | `count(claimDates[date(item) >= (date(referenceDate) - duration("P24M")) and date(item) <= date(referenceDate)])` | `number` |
| **FEEL-06** | Compound expression (`if ... then ... else` + logical ops) | `D05` hierarchical policy expression | `if vehicleEligibility = "INELIGIBLE" or driverRisk = "INELIGIBLE" then "DECLINE" else if claimsRisk = "UNKNOWN" or driverRisk = "UNKNOWN" or claimsRisk = "HIGH" or (driverRisk = "HIGH" and (vehicleRisk = "HIGH" or claimsRisk = "MEDIUM")) then "REFER" else "ACCEPT"` | `string` |

*(Actual execution outputs against `feelin@8.2.2` are recorded in `tests/test-results/TEST_RESULTS.json`, `tests/test-results/INDEPENDENT_EXECUTION_RESULTS.json`, and `tests/validation-evidence/VALIDATION_REPORT.md`.)*
