# Data Dictionary — Scenario B: Motor Insurance Underwriting (`AsuransiNusantara`)

**Canonical Model Version:** 1.0  
**Reference Date Convention:** All temporal calculations use the explicit `evaluationDate` input rather than `today()` to guarantee deterministic, reproducible evaluation.

---

## 1. Input Data Elements (10 Nodes)

| ID | Variable Name | DMN TypeRef | Domain / Allowed Values | Null / Missing Handling | Business Meaning & Unit |
|---|---|---|---|---|---|
| `I01` | `dateOfBirth` | `date` | ISO-8601 date string (`YYYY-MM-DD`), `<= evaluationDate` | `null` → `D01 = "UNKNOWN"` → `REFER` | Applicant driver's birth date. |
| `I02` | `evaluationDate` | `date` | ISO-8601 date string (`YYYY-MM-DD`) | `null` → `D01 = "UNKNOWN"`, `D02 = "UNKNOWN"`, `D03 = "INELIGIBLE"` | Reference underwriting date for age and recency checks. |
| `I03` | `claimsHistoryAvailable` | `boolean` | `true`, `false` | `null` or `false` → `D02 = "UNKNOWN"` → `REFER` | Indicates whether verified prior claims history is available. Distinguishes missing records from confirmed zero claims. |
| `I04` | `claimDates` | `list<date>` | List of ISO-8601 date strings (may be empty `[]`) | `null` (when `claimsHistoryAvailable = true`) → `D02 = "UNKNOWN"` | Dates of historical motor claims. `[]` with `claimsHistoryAvailable = true` means confirmed clean record. |
| `I05` | `vehicleManufactureDate` | `date` | ISO-8601 date string (`YYYY-MM-DD`), `<= evaluationDate` | `null` or `> evaluationDate` → `D03 = "INELIGIBLE"` → `DECLINE` | Manufacture / registration reference date of the insured vehicle. |
| `I06` | `vehicleType` | `string` | `"MOTORCYCLE"`, `"CAR"` | `null` or outside enum → `D03 = "INELIGIBLE"` → `DECLINE` | Primary motor vehicle category. |
| `I07` | `engineCC` | `number` | Real/integer `> 0` (unit: $\text{cm}^3$ / cc) | `null` or `<= 0` → `D03 = "INELIGIBLE"` → `DECLINE` | Engine cylinder displacement in cubic centimeters. |
| `I08` | `performanceClass` | `string` | `"STANDARD"`, `"SPORT"`, `"HIGH_PERFORMANCE"` | `null` or outside enum → treated conservatively as `"HIGH_PERFORMANCE"` in `D04`/`D08` or fallback `HIGH` | Underwriting performance tier of the vehicle model. |
| `I09` | `coverType` | `string` | `"TPO"`, `"COMPREHENSIVE"` | `null` or outside enum → `D07 = 0`, `D06 = "REQUIRED"` fallback | Requested policy coverage (`TPO` = Third-Party Only; `COMPREHENSIVE` = All-Risk / Comprehensive). |
| `I10` | `insuredValue` | `number` | Numeric `> 0` (unit: IDR / Indonesian Rupiah) | `null` or `<= 0` → `D03 = "INELIGIBLE"` → `DECLINE` | Declared sum insured / market valuation of the vehicle in IDR. |

---

## 2. Derived Intermediate Values & Decision Outputs

| ID | Decision / BKM | DMN TypeRef | Allowed Values / Domain | Business Semantics |
|---|---|---|---|---|
| `BKM01` | `Calculate Age in Years` | `number` | Integer $\ge 0$ (or `null` if invalid/future date) | Completed calendar years between `targetDate` and `referenceDate` using `years and months duration(date(targetDate), date(referenceDate)).years`. |
| `BKM02` | `Count Recent Claims` | `number` | Integer $\ge 0$ (or `null` if `claimDates` is `null`) | Count of `claimDates` falling in `[referenceDate - P24M, referenceDate]` inclusive. |
| `D01` | `Driver Risk Assessment` | `string` | `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"INELIGIBLE"`, `"UNKNOWN"` | Driver risk tier based on completed age at `evaluationDate`. |
| `D02` | `Claims Risk Assessment` | `string` | `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"UNKNOWN"` | Claims frequency risk tier with strict missing-history guard. |
| `D03` | `Vehicle Eligibility Assessment` | `string` | `"ELIGIBLE"`, `"INELIGIBLE"` | Hard gate checking vehicle type, positive displacement/value, and age `<= 15` years. |
| `D04` | `Vehicle Risk Assessment` | `string` | `"LOW"`, `"MEDIUM"`, `"HIGH"` | Technical vehicle risk from `vehicleType`, `engineCC`, `performanceClass`, and `vehicleAge`. |
| `D05` | `Underwriting Decision` | `string` | `"ACCEPT"`, `"REFER"`, `"DECLINE"` | Final underwriting disposition enforcing `DECLINE > REFER > ACCEPT`. |
| `D06` | `Inspection Decision` | `string` | `"REQUIRED"`, `"NOT_REQUIRED"`, `"NOT_APPLICABLE"` | Pre-cover physical inspection requirement before policy inception. |
| `D07` | `Base Premium Calculation` | `number` | Numeric $\ge 0$ (IDR) | Annual illustrative base premium prior to risk loadings. |
| `D08` | `Risk Loading Calculation` | `number` | Numeric $\ge 0$ (decimal fraction, e.g., `0.35` = +35%) | Additive sum of applicable percentage risk loadings (`C+`). |
| `D09` | `Final Premium Calculation` | `number` | Numeric $\ge 0$ (IDR) | Final annual premium (`0` if `DECLINE`; `D07 * (1 + D08)` for `ACCEPT` and indicative `REFER`). |

---

## 3. Custom DMN `itemDefinition` Types

All inputs and decision outputs above are declared as explicit DMN 1.3 `<itemDefinition>` elements inside `AsuransiNusantara.dmn`, including enumerated `<allowedValues>` constraints for `tVehicleType`, `tPerformanceClass`, `tCoverType`, `tDriverRisk`, `tClaimsRisk`, `tVehicleEligibility`, `tVehicleRisk`, `tUnderwritingDecision`, and `tInspectionDecision`, plus collection type `tDateList` (`isCollection="true"`).
