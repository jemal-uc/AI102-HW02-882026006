# Decision Decomposition & Node Specifications — Scenario B

**Architecture Summary:** 10 Input Data nodes, 9 Decision nodes (`D01`–`D09`), 2 Business Knowledge Models (`BKM01`–`BKM02`), and 3 Knowledge Sources (`KS01`–`KS03`) organized into a 4-tier acyclic Decision Requirements Graph (DRD).

---

## 1. One-Sentence Node Requirements (Task 1.3)

- **D01 — Driver Risk Assessment:** Computes the applicant driver's risk tier (`LOW`, `MEDIUM`, `HIGH`, `INELIGIBLE`, or `UNKNOWN`) from `dateOfBirth` and `evaluationDate` via `BKM01`.
- **D02 — Claims Risk Assessment:** Computes prior claims frequency risk (`LOW`, `MEDIUM`, `HIGH`, or `UNKNOWN`) from `claimsHistoryAvailable`, `claimDates`, and `evaluationDate` via `BKM02`.
- **D03 — Vehicle Eligibility Assessment:** Determines whether the requested vehicle is insurable (`ELIGIBLE` or `INELIGIBLE`) from `vehicleType`, `vehicleManufactureDate`, `evaluationDate`, `engineCC`, and `insuredValue` via `BKM01`.
- **D04 — Vehicle Risk Assessment:** Classifies vehicle technical risk (`LOW`, `MEDIUM`, or `HIGH`) from `vehicleType`, `engineCC`, `performanceClass`, `vehicleManufactureDate`, and `evaluationDate` via `BKM01`.
- **D05 — Underwriting Decision:** Determines the final underwriting disposition (`ACCEPT`, `REFER`, or `DECLINE`) by aggregating `D01` (Driver Risk), `D02` (Claims Risk), `D03` (Vehicle Eligibility), and `D04` (Vehicle Risk) under strict precedence.
- **D06 — Inspection Decision:** Determines pre-cover physical inspection status (`REQUIRED`, `NOT_REQUIRED`, or `NOT_APPLICABLE`) from `D05` (Underwriting Decision), `insuredValue`, `coverType`, `vehicleManufactureDate`, and `evaluationDate` via `BKM01`.
- **D07 — Base Premium Calculation:** Computes the illustrative annual base premium in IDR from `vehicleType`, `engineCC`, `coverType`, and `insuredValue`.
- **D08 — Risk Loading Calculation:** Computes the total additive risk surcharge fraction by summing independent risk loadings from `D01` (Driver Risk), `D02` (Claims Risk), `D04` (Vehicle Risk), and `performanceClass`.
- **D09 — Final Premium Calculation:** Computes the final annual policy premium in IDR (`0` when declined; `Base Premium * (1 + Total Risk Loading)` when accepted or provisionally quoted on referral) from `D05`, `D07`, and `D08`.

---

## 2. Decomposition Rationale

1. **Separation of Concerns (Eligibility vs. Risk vs. Disposition vs. Pricing):**
   - Splitting `D03` (hard eligibility gate) from `D04` (graduated technical vehicle risk) ensures that age-ineligible (`> 15` years) or invalid vehicles are blocked unconditionally before pricing or risk trade-offs occur.
   - Separating `D01` (driver), `D02` (claims), and `D04` (vehicle) prevents an unmaintainable monolithic underwriting table (which would require $5 \times 4 \times 2 \times 3 = 120+$ raw combinations) and makes each risk factor independently explainable, auditable, and replaceable (e.g., swapping `D02` or `D01` for an ML score in future iterations).
2. **Pricing Modularity (`D07`, `D08`, `D09`):**
   - Separating base tariff (`D07`) from additive risk surcharges (`D08` using `C+`) and final disposition gating (`D09`) isolates commercial rate-table updates from risk-loading policy changes and makes additive surcharge stacking explicit.
3. **Reusable Logic via BKMs (`BKM01`, `BKM02`):**
   - Age calculation (`BKM01`) is shared across `D01`, `D03`, `D04`, and `D06`, eliminating duplicate date-duration expressions and guaranteeing uniform calendar-year semantics.
   - Claims recency counting (`BKM02`) encapsulates the 24-month calendar-duration window in one reusable function.
