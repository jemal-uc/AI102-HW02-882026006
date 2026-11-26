# Architecture Rationale — Motor Insurance Underwriting DMN

## 1. Granularity and Modularity Principles

The `AsuransiNusantara` underwriting architecture adopts a **10-decision, 2-BKM** decomposition separating underwriting risk evaluation from commercial quotation readiness and final premium issuance:

1. **Risk-Domain Isolation (`D01`, `D02`, `D04`):** Driver demographics, prior claims behavior, and vehicle technical risk represent distinct underwriting evidence streams. Isolating them keeps each decision table compact (`5–14` rules), readable, and independently auditable.
2. **Hard Eligibility vs. Graduated Pricing (`D03` vs. `D04`/`D07`):** Separating hard insurability (`D03: ELIGIBLE/INELIGIBLE`) from graduated vehicle risk (`D04`) prevents an ineligible >15-year vehicle from being offset by a low driver risk tier. Missing `insuredValue` (`null`) is kept distinct from non-positive valuation (`<= 0`) so an unquoted valuation routes to pending information rather than wrongful risk decline.
3. **Underwriting Disposition vs. Quote Readiness Separation (`D05` vs. `D10`):** Underwriting acceptance (`ACCEPT / REFER / DECLINE`) depends strictly on risk characteristics, never on whether the applicant already selected `coverType`. Introducing `D10` (`QuoteReadinessAssessment`) as the smallest clean structural addition ensures a missing, blank, or unsupported `coverType` yields `PENDING_INFORMATION` or `INVALID_INPUT` instead of causing a false `Rp0` quote under an `ACCEPT` decision.
4. **Premium Safety Gating (`D07`, `D08`, `D09`):** `D07` returns `null` rather than `0` whenever commercial tariff inputs are incomplete or invalid; `D08` sums four orthogonal surcharges via `COLLECT (SUM)`; and `D09` issues a positive final premium strictly when `D05 = "ACCEPT"`, `D10 = "READY"`, and `basePremium > 0`, returning `null` for declined, referred, pending, or invalid applications.

## 2. Future Machine-Learning Integration Pathway (Session 03 Alignment)

Per Session 03 (hybrid rule + ML Decision Intelligence architecture), predictive models should augment—not replace—transparent underwriting rules:

- **Option A — ML Risk Score as `inputData` (`mlLossPropensityScore`):** An external calibrated Gradient Boosted / GLM claim-propensity score $p \in [0, 1]$ (with SHAP reason codes) can feed `D05` (triggering `REFER` when deterministic risk is `LOW` but $p \ge \tau_{\text{refer}}$) and `D08` (adding a bounded behavioral adjustment).
- **Option B — ML Scoring Wrapper as a `BKM` (`scoreTelemetryRisk`):** Encapsulating a monotonic scorecard inside a DMN `businessKnowledgeModel` preserves deterministic statutory (`KS03`), eligibility (`D03`), and quote-readiness (`D10`) overrides so invalid or unapproved applications remain safely gated (`D09 = null`).
