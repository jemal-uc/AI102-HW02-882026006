# Architecture Rationale — Motor Insurance Underwriting DMN

## 1. Granularity and Modularity Principles

The `AsuransiNusantara` underwriting architecture adopts a **9-decision, 2-BKM** decomposition rather than a single monolithic decision table or fragmented micro-tables:

1. **Risk-Domain Isolation (`D01`, `D02`, `D04`):** Driver demographics, prior claims behavior, and vehicle technical risk represent distinct underwriting evidence streams. Isolating them keeps each decision table compact (5–10 rules), domain-expert readable, and independently auditable.
2. **Hard Eligibility vs. Graduated Pricing (`D03` vs. `D04`/`D07`):** Separating hard insurability (`D03: ELIGIBLE/INELIGIBLE`) from graduated vehicle risk (`D04`) prevents an ineligible 16-year-old vehicle from being mistakenly priced and accepted through risk-tier trade-offs.
3. **Explicit Underwriting Gate (`D05`) Downstream Control:** Both `D06` (Inspection) and `D09` (Final Premium) depend directly on `D05`. Consequently, a `DECLINE` decision cleanly forces `NOT_APPLICABLE` inspection and `Rp0` premium without duplicating eligibility rules across downstream tables.
4. **Additive Pricing Transparency (`D07`, `D08`, `D09`):** Separating base tariff (`D07`) from additive surcharge aggregation (`D08`, `C+`) allows actuarial or commercial updates to base rates without altering risk-loading logic.

## 2. Future Machine-Learning Integration Pathway (Session 03 Alignment)

Per Session 03 (Decision Intelligence hybrid rule + ML integration), predictive analytics should augment—not replace—transparent underwriting rules:

- **Option A — ML Risk Score as `inputData` (`mlLossPropensityScore`):** An external calibrated Gradient Boosted / GLM claim-propensity score $p \in [0, 1]$ (with SHAP reason codes) can be introduced as an `<inputData>` node feeding `D05` (triggering `REFER` when rule risk is `LOW` but $p \ge \tau_{\text{refer}}$) and `D08` (adding a bounded behavioral adjustment).
- **Option B — ML Scoring Wrapper as a `BKM` (`scoreTelemetryRisk`):** Encapsulating a monotonic scorecard or predictive endpoint invocation inside a DMN `businessKnowledgeModel` preserves explainable policy overrides (`DECLINE` gates and regulatory SIM age constraints remain deterministic DMN rules), ensuring full auditability and governance.
