# Decision Decomposition & Responsibility Summary — Scenario B

**Architecture Summary:** 10 Input Data nodes (`I01`–`I10`), **10 Decision nodes (`D01`–`D10`)**, 2 Business Knowledge Models (`BKM01`–`BKM02`), and 3 Knowledge Sources (`KS01`–`KS03`) organized into a **5-tier acyclic Decision Requirements Graph (DRD)**.

---

## 1. Decision Responsibility Matrix (All 10 Decisions)

| Decision ID | Decision Name | What the Decision Computes (One-Sentence Description) | Input Data & Upstream Decisions | Output Variable | Output Type |
|---|---|---|---|---|---|
| `D01` | Driver Risk Assessment | Computes the applicant driver risk classification (`LOW`, `MEDIUM`, `HIGH`, `INELIGIBLE`, or `UNKNOWN`) from driver age derived via `BKM01` using `dateOfBirth` and `evaluationDate`. | `I01 (dateOfBirth)`, `I02 (evaluationDate)`, `BKM01` | `driverRisk` | `tDriverRisk` |
| `D02` | Claims Risk Assessment | Computes prior claims frequency risk (`LOW`, `MEDIUM`, `HIGH`, or `UNKNOWN`) from `claimsHistoryAvailable` and 24-month claims counted via `BKM02` from `claimDates` and `evaluationDate`. | `I02 (evaluationDate)`, `I03 (claimsHistoryAvailable)`, `I04 (claimDates)`, `BKM02` | `claimsRisk` | `tClaimsRisk` |
| `D03` | Vehicle Eligibility Assessment | Computes technical vehicle insurability (`ELIGIBLE` or `INELIGIBLE`) from `vehicleType`, vehicle age via `BKM01` (`vehicleManufactureDate`, `evaluationDate`), `engineCC`, and invalid non-positive `insuredValue`. | `I02`, `I05`, `I06`, `I07`, `I10`, `BKM01` | `vehicleEligibility` | `tVehicleEligibility` |
| `D04` | Vehicle Risk Assessment | Computes vehicle technical risk tier (`LOW`, `MEDIUM`, or `HIGH`) from `vehicleType`, `engineCC`, `performanceClass`, and vehicle age derived via `BKM01`. | `I02`, `I05`, `I06`, `I07`, `I08`, `BKM01` | `vehicleRisk` | `tVehicleRisk` |
| `D05` | Underwriting Decision | Computes the underwriting risk disposition (`ACCEPT`, `REFER`, or `DECLINE`) solely from `D01` (`driverRisk`), `D02` (`claimsRisk`), `D03` (`vehicleEligibility`), and `D04` (`vehicleRisk`), independent of commercial `coverType`. | `D01`, `D02`, `D03`, `D04` | `underwritingDecision` | `tUnderwritingDecision` |
| `D06` | Inspection Decision | Determines whether pre-cover physical vehicle inspection is required (`REQUIRED`, `NOT_REQUIRED`, or `NOT_APPLICABLE`) from `D05` (`underwritingDecision`), `insuredValue`, `coverType`, and vehicle age via `BKM01`. | `D05`, `I02`, `I05`, `I09`, `I10`, `BKM01` | `inspectionDecision` | `tInspectionDecision` |
| `D07` | Base Premium Calculation | Computes the illustrative annual base premium in IDR (or `null` when pricing inputs are incomplete or invalid) from `vehicleType`, `engineCC`, `coverType`, and `insuredValue`. | `I06`, `I07`, `I09`, `I10` | `basePremium` | `number` |
| `D08` | Risk Loading Calculation | Computes the total additive risk loading fraction by summing independent surcharges from `D01` (`driverRisk`), `D02` (`claimsRisk`), `D04` (`vehicleRisk`), and `performanceClass`. | `D01`, `D02`, `D04`, `I08` | `totalRiskLoading` | `number` |
| `D09` | Final Premium Calculation | Computes the approved annual final premium in IDR strictly when `D05` is `ACCEPT`, `D10` (`quoteReadiness`) is `READY`, and `D07` (`basePremium`) is positive (applying `D08` `totalRiskLoading`), otherwise returning `null`. | `D05`, `D10`, `D07`, `D08` | `finalPremium` | `number` |
| `D10` | Quote Readiness Assessment | Determines commercial and technical quotation readiness (`READY`, `PENDING_INFORMATION`, `INVALID_INPUT`, or `NOT_APPLICABLE`) from `D05` (`underwritingDecision`), `vehicleType`, `engineCC`, `coverType`, `insuredValue`, and `D07` (`basePremium`). | `D05`, `D07`, `I06`, `I07`, `I09`, `I10` | `quoteReadiness` | `tQuoteReadiness` |

---

## 2. Decomposition Rationale

1. **Underwriting Risk vs. Quote Readiness vs. Final Premium Separation (`D05` vs. `D10` vs. `D09`):**
   - Earlier 9-node drafts allowed an acceptable driver/vehicle with a missing `coverType` to receive `D05 = ACCEPT`, `D07 = 0`, and `D09 = Rp0`—conflating incomplete commercial input with a zero-rupiah premium.
   - Introducing `D10` (`QuoteReadinessAssessment`) as a single minimal architectural addition isolates *risk acceptability* (`D05`) from *commercial/pricing completeness* (`D10`) and *approved premium calculation* (`D09`), without adding redundant inputs to `D05` or distorting `ACCEPT`/`REFER`/`DECLINE` underwriting semantics.
2. **Hard Eligibility Gate vs. Graduated Technical Risk (`D03` vs. `D04`):**
   - Splitting `D03` (hard eligibility gate) from `D04` (graduated technical risk) ensures that age-ineligible (`> 15` years) or invalid-displacement vehicles are declined unconditionally rather than offset by low driver risk, while `insuredValue = null` is deferred to `D10` (`PENDING_INFORMATION`) rather than triggering an improper risk decline.
3. **Domain Factor Isolation & Modular Pricing (`D01`, `D02`, `D04`, `D07`, `D08`):**
   - Separating driver, claims, and vehicle risk avoids an unmanageable $5 \times 4 \times 2 \times 3 = 120+$ rule underwriting monolith and cleanly isolates commercial tariff rates (`D07`) from additive loading surcharges (`D08`).
4. **Reusable Logic via BKMs (`BKM01`, `BKM02`):**
   - Centralizing calendar-year age (`BKM01`) and 24-month claims counting (`BKM02`) prevents duplicated date-duration logic across `D01`, `D02`, `D03`, `D04`, and `D06`.
