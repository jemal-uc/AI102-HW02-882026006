# Business Requirements — Scenario B: Motor Insurance Underwriting (`AsuransiNusantara`)

**Version:** 1.1 (Stage 5 Targeted Correction)  
**Source Narrative:** `AI102_Homework-02_Decision-Modeling-DMN_Assignment.docx.pdf`, Section 4 (Scenario B)

---

## 1. Original Business Narrative

> “When someone requests a motorcycle or car policy, we decide whether to accept the risk; if accepted, we set the premium and decide whether a physical inspection is required before cover starts. Young drivers and those with recent claims are riskier, so they pay more. Very old vehicles are hard to insure — beyond some age we just decline. Sporty/high-performance vehicles attract a loading. Engine size matters somehow, especially for motorcycles. Comprehensive cover costs more than third-party-only. Very high vehicle value means an inspection. Some risks are too bad — maybe decline, maybe refer to a senior underwriter; the rules should decide.”

---

## 2. Functional Requirements Matrix

| Req ID | Requirement Statement | Source Narrative Clause | Target Decision / BKM |
|---|---|---|---|
| **BR-01** | The system shall restrict underwriting to supported motor vehicle categories (`MOTORCYCLE`, `CAR`) and reject unsupported or invalid requests. | "requests a motorcycle or car policy" | `D03` (Vehicle Eligibility) |
| **BR-02** | The system shall compute driver age deterministically from `dateOfBirth` and an explicit `evaluationDate` and classify driver risk (`LOW`, `MEDIUM`, `HIGH`, `INELIGIBLE`, `UNKNOWN`). The universal `< 17` floor aligns with Indonesian `UU No. 22/2009` Art. 81(2)(a) and `Perpol No. 5/2021` Art. 3 & 8 (`SIM C <= 250cc` min age 17); higher `SIM CI`/`CII` displacement-age rules (`18`/`19` yrs) are outside this simplified educational scope. | "Young drivers ... are riskier, so they pay more." | `BKM01`, `D01` (Driver Risk) |
| **BR-03** | The system shall evaluate prior claims recency within a defined 24-month lookback window using `claimsHistoryAvailable` and `claimDates` relative to `evaluationDate`, distinguishing missing history (`UNKNOWN`) from verified zero claims (`LOW`). | "those with recent claims are riskier ... missing claims history" | `BKM02`, `D02` (Claims Risk) |
| **BR-04** | The system shall compute vehicle age from `vehicleManufactureDate` and `evaluationDate` and decline vehicles exceeding the maximum insurable age (`> 15` completed years) or invalid non-positive valuations (`<= 0`). Missing `insuredValue` (`null`) is deferred to quote readiness (`D10`) rather than misclassified as a risk decline. | "Very old vehicles are hard to insure — beyond some age we just decline." | `BKM01`, `D03` (Vehicle Eligibility), `D05`, `D10` |
| **BR-05** | The system shall classify vehicle technical risk (`LOW`, `MEDIUM`, `HIGH`) incorporating vehicle type, engine displacement (`engineCC` with motorcycle-specific sensitivity), performance classification, and vehicle age. | "Sporty/high-performance vehicles attract a loading. Engine size matters somehow..." | `D04` (Vehicle Risk) |
| **BR-06** | The system shall determine underwriting risk disposition (`ACCEPT`, `REFER`, `DECLINE`) enforcing strict precedence (`DECLINE > REFER > ACCEPT`) independently of commercial `coverType`. | "decide whether to accept the risk ... Some risks are too bad — maybe decline, maybe refer..." | `D05` (Underwriting Decision) |
| **BR-07** | The system shall determine pre-cover physical inspection status (`REQUIRED`, `NOT_REQUIRED`, `NOT_APPLICABLE`), mandating inspection for high-value vehicles (`>= Rp500M`), older `COMPREHENSIVE` vehicles (`> 10` years), and incomplete pricing data, while marking `DECLINE` as `NOT_APPLICABLE`. | "decide whether a physical inspection is required before cover starts ... Very high vehicle value means an inspection." | `D06` (Inspection Decision) |
| **BR-08** | The system shall compute an illustrative annual base premium (`D07`) reflecting vehicle type, engine displacement, coverage type (`COMPREHENSIVE > TPO / THIRD_PARTY_ONLY`), and `insuredValue`, returning `null` (never `0`) when any pricing input is missing or invalid. | "Comprehensive cover costs more than third-party-only. Engine size matters somehow..." | `D07` (Base Premium Calculation) |
| **BR-09** | The system shall compute cumulative additive risk loading (`D08`) via `COLLECT (SUM)` across driver risk, claims risk, vehicle risk, and sporty/high-performance classification. | "Young drivers and those with recent claims ... Sporty/high-performance vehicles attract a loading." | `D08` (Risk Loading Calculation) |
| **BR-10** | The system shall separate commercial/technical **Quote Readiness** (`D10`: `READY`, `PENDING_INFORMATION`, `INVALID_INPUT`, `NOT_APPLICABLE`) from **Underwriting Decision** (`D05`), so missing/invalid cover type or missing valuation never produces a `Rp0` fallback. | Policy vs. underwriting separation & premium safety | `D10` (Quote Readiness Assessment), `D07`, `D09` |
| **BR-11** | The system shall compute an approved `finalPremium` (`D09`) equal to `decimal(Base Premium * (1 + Total Risk Loading), 0)` **strictly when** `D05 = "ACCEPT"`, `D10 = "READY"`, and `D07 > 0`; otherwise (`DECLINE`, `REFER`, pending, or invalid inputs) `D09` outputs `null`. | "if accepted, we set the premium..." | `D09` (Final Premium Calculation) |

---

## 3. Non-Functional & Modeling Governance Requirements

| Req ID | Requirement | Verification Method |
|---|---|---|
| **NFR-01** | **DMN 1.3 Conformance:** Model uses normative namespace `https://www.omg.org/spec/DMN/20191111/MODEL/` with valid DMNDI diagram interchange, typed edges, and 5-tier acyclic DAG structure. | `DMN13.xsd` + `dmn-moddle@12.2.1` + `lxml` + `dmn-js@18.1.0` |
| **NFR-02** | **Completeness & Premium Safety:** Every decision table handles all valid, boundary, and missing/invalid inputs (`null`, `""`, unsupported enums) with zero silent fall-throughs and zero `Rp0` premium fallbacks. | Decision table completeness audit + boundary regression suite (`TC-01`–`TC-26`) |
| **NFR-03** | **Reproducibility:** No reliance on non-deterministic `today()`; `evaluationDate` is an explicit model input. | Canonical JSON & test suites (`feelin@8.2.2`) |
| **NFR-04** | **Regulatory & Educational Transparency:** Distinguishes real statutory regulations (`UU No. 22/2009` Art. 81(2)(a) + Korlantas/Polri `Perpol No. 5/2021` Art. 3 & 8 `SIM C/CI/CII` rules, explicitly flagging `SIM CI`/`CII` as a model limitation) from illustrative educational assumptions (`KS01`/`KS02`, simplified cc tariffs rather than `SEOJK 6/2017`) and DMN technical design choices. | `AMBIGUITY_REGISTER.md` & Report Sec. 3, 6, 8 |
