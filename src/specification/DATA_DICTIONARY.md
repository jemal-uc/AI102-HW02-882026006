# Data Dictionary — Scenario B: Motor Insurance Underwriting (`AsuransiNusantara`)

**Canonical Model Version:** 1.1 (Stage 5)  
**Reference Date Convention:** All temporal calculations use the explicit `evaluationDate` input rather than `today()` to guarantee deterministic, reproducible evaluation.

---

## 1. Input Data Elements (10 Nodes)

| ID | Variable Name | DMN TypeRef | Domain / Allowed Values | Null / Missing Handling | Business Meaning & Unit |
|---|---|---|---|---|---|
| `I01` | `dateOfBirth` | `date` | ISO-8601 date string (`YYYY-MM-DD`), `<= evaluationDate` | `null` -> `D01 = "UNKNOWN"` -> `REFER`; future (`> evaluationDate`) -> `-1` -> `INELIGIBLE` | Applicant driver's birth date. |
| `I02` | `evaluationDate` | `date` | ISO-8601 date string (`YYYY-MM-DD`) | `null` -> `D01 = "UNKNOWN"`, `D02 = "UNKNOWN"`, `D03 = "INELIGIBLE"` | Reference underwriting date for age and recency checks. |
| `I03` | `claimsHistoryAvailable` | `boolean` | `true`, `false` | `null` or `false` -> `D02 = "UNKNOWN"` -> `REFER` | Indicates whether verified prior claims history is available. Distinguishes missing records from confirmed zero claims. |
| `I04` | `claimDates` | `tDateList` (`list<date>`) | List of ISO-8601 date strings (may be empty `[]`) | `null` (when `claimsHistoryAvailable = true`) -> `D02 = "UNKNOWN"`; `null` items ignored cleanly | Dates of historical motor claims. `[]` with `claimsHistoryAvailable = true` means confirmed clean record. |
| `I05` | `vehicleManufactureDate` | `date` | ISO-8601 date string (`YYYY-MM-DD`), `<= evaluationDate` | `null` or `> evaluationDate` -> `D03 = "INELIGIBLE"` -> `DECLINE` | Manufacture / registration reference date of the insured vehicle. |
| `I06` | `vehicleType` | `tVehicleType` (`string`) | `"MOTORCYCLE"`, `"CAR"` | `null` or outside enum -> `D03 = "INELIGIBLE"` -> `DECLINE` | Primary motor vehicle category. |
| `I07` | `engineCC` | `number` | Real/integer `> 0` (unit: $\text{cm}^3$ / cc) | `null` or `<= 0` -> `D03 = "INELIGIBLE"` -> `DECLINE` | Engine cylinder displacement in cubic centimeters. |
| `I08` | `performanceClass` | `tPerformanceClass` (`string`) | `"STANDARD"`, `"SPORT"`, `"HIGH_PERFORMANCE"` | `null` or outside enum -> treated conservatively as `"HIGH"` in `D04` and `+30%` in `D08` | Underwriting performance tier of the vehicle model. |
| `I09` | `coverType` | `tCoverType` (`string`) | `"TPO"`, `"THIRD_PARTY_ONLY"`, `"COMPREHENSIVE"` | `null` or `""` -> `D10 = "PENDING_INFORMATION"`, `D07 = null`, `D09 = null`; unsupported string -> `D10 = "INVALID_INPUT"`, `D07 = null`, `D09 = null` | Requested policy coverage (`TPO` / `THIRD_PARTY_ONLY` = Third-Party Only; `COMPREHENSIVE` = All-Risk / Comprehensive). |
| `I10` | `insuredValue` | `number` | Numeric `> 0` (unit: IDR / Indonesian Rupiah) | `<= 0` -> `D03 = "INELIGIBLE"` -> `DECLINE`, `D07 = null`; `null` -> `D03 = "ELIGIBLE"` (risk remains separate), `D10 = "PENDING_INFORMATION"`, `D07 = null`, `D09 = null` | Declared sum insured / market valuation of the vehicle in IDR. |

---

## 2. Derived Intermediate Values & Decision Outputs

| ID | Decision / BKM | DMN TypeRef | Allowed Values / Domain | Business Semantics |
|---|---|---|---|---|
| `BKM01` | `calculateAgeInYears` | `number` | Integer `>= 0`, `-1` if future date, or `null` if missing/malformed | Completed calendar years between `targetDate` and `referenceDate` using `years and months duration(date(targetDate), date(referenceDate)).years`. |
| `BKM02` | `countRecentClaims` | `number` | Integer `>= 0` (or `null` if `claimDates`/`referenceDate` is `null`) | Count of `claimDates` falling in `[referenceDate - P24M, referenceDate]` inclusive. |
| `D01` | `driverRisk` | `tDriverRisk` | `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"INELIGIBLE"`, `"UNKNOWN"` | Driver risk tier based on completed age at `evaluationDate`. |
| `D02` | `claimsRisk` | `tClaimsRisk` | `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"UNKNOWN"` | Claims frequency risk tier with strict missing-history guard. |
| `D03` | `vehicleEligibility` | `tVehicleEligibility` | `"ELIGIBLE"`, `"INELIGIBLE"` | Hard gate checking vehicle type, positive displacement, non-negative/<=15 age, and non-invalid (`<=0`) valuation. |
| `D04` | `vehicleRisk` | `tVehicleRisk` | `"LOW"`, `"MEDIUM"`, `"HIGH"` | Technical vehicle risk from `vehicleType`, `engineCC`, `performanceClass`, and `vehicleAge`. |
| `D05` | `underwritingDecision` | `tUnderwritingDecision` | `"ACCEPT"`, `"REFER"`, `"DECLINE"` | Underwriting risk disposition enforcing `DECLINE > REFER > ACCEPT`, independent of commercial `coverType`. |
| `D06` | `inspectionDecision` | `tInspectionDecision` | `"REQUIRED"`, `"NOT_REQUIRED"`, `"NOT_APPLICABLE"` | Pre-cover physical inspection requirement before policy inception. |
| `D07` | `basePremium` | `number` | Positive integer IDR or `null` when uncalculable | Annual illustrative base premium prior to risk loadings; returns `null` if any pricing input is missing or invalid. |
| `D08` | `totalRiskLoading` | `number` | Numeric `>= 0` (decimal fraction, e.g., `0.35` = +35%) | Additive sum of applicable percentage risk loadings (`C+`). |
| `D10` | `quoteReadiness` | `tQuoteReadiness` | `"READY"`, `"PENDING_INFORMATION"`, `"INVALID_INPUT"`, `"NOT_APPLICABLE"` | Commercial/technical readiness to produce a valid premium quotation (`NOT_APPLICABLE` if declined; `PENDING_INFORMATION` if missing/empty; `INVALID_INPUT` if malformed/unsupported; `READY` if valid). |
| `D09` | `finalPremium` | `number` | Positive integer IDR when `D05="ACCEPT"` and `D10="READY"`, else `null` | Approved annual policy premium (`null` for `DECLINE`, `REFER`, pending, or invalid inputs; never defaults to `0`). |

---

## 3. Custom DMN `itemDefinition` Types (`11` Custom Types)

All inputs and decision outputs above are declared as explicit DMN 1.3 `<itemDefinition>` elements inside `AsuransiNusantara.dmn`:
- Enumerated string constraints (`allowedValues`): `tVehicleType`, `tPerformanceClass`, `tCoverType`, `tDriverRisk`, `tClaimsRisk`, `tVehicleEligibility`, `tVehicleRisk`, `tUnderwritingDecision`, `tInspectionDecision`, `tQuoteReadiness`.
- Collection type: `tDateList` (`isCollection="true"`, `typeRef="date"`).
