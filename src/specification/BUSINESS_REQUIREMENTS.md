# Business Requirements — Scenario B: Motor Insurance Underwriting (`AsuransiNusantara`)

**Version:** 1.0 (Canonical Baseline)  
**Source Narrative:** `AI102_Homework-02_Decision-Modeling-DMN_Assignment.docx.pdf`, Section 4 (Scenario B)

---

## 1. Original Business Narrative

> “When someone requests a motorcycle or car policy, we decide whether to accept the risk; if accepted, we set the premium and decide whether a physical inspection is required before cover starts. Young drivers and those with recent claims are riskier, so they pay more. Very old vehicles are hard to insure — beyond some age we just decline. Sporty/high-performance vehicles attract a loading. Engine size matters somehow, especially for motorcycles. Comprehensive cover costs more than third-party-only. Very high vehicle value means an inspection. Some risks are too bad — maybe decline, maybe refer to a senior underwriter; the rules should decide.”

---

## 2. Functional Requirements Matrix

| Req ID | Requirement Statement | Source Narrative Clause | Target Decision / BKM |
|---|---|---|---|
| **BR-01** | The system shall restrict underwriting to supported motor vehicle categories (`MOTORCYCLE`, `CAR`) and reject unsupported or invalid requests. | "requests a motorcycle or car policy" | `D03` (Vehicle Eligibility) |
| **BR-02** | The system shall compute driver age deterministically from `dateOfBirth` and an explicit `evaluationDate` and classify driver risk (`LOW`, `MEDIUM`, `HIGH`, `INELIGIBLE`, `UNKNOWN`). | "Young drivers ... are riskier, so they pay more." | `BKM01`, `D01` (Driver Risk) |
| **BR-03** | The system shall evaluate prior claims recency within a defined lookback window using `claimsHistoryAvailable` and `claimDates` relative to `evaluationDate`, distinguishing missing history from zero claims. | "those with recent claims are riskier ... missing claims history" | `BKM02`, `D02` (Claims Risk) |
| **BR-04** | The system shall compute vehicle age from `vehicleManufactureDate` and `evaluationDate` and decline vehicles exceeding maximum insurable age. | "Very old vehicles are hard to insure — beyond some age we just decline." | `BKM01`, `D03` (Vehicle Eligibility), `D05` |
| **BR-05** | The system shall classify vehicle technical risk (`LOW`, `MEDIUM`, `HIGH`) incorporating vehicle type, engine displacement (`engineCC` with motorcycle-specific sensitivity), performance classification, and vehicle age. | "Sporty/high-performance vehicles attract a loading. Engine size matters somehow, especially for motorcycles." | `D04` (Vehicle Risk) |
| **BR-06** | The system shall determine the underwriting disposition (`ACCEPT`, `REFER`, `DECLINE`) enforcing strict precedence (`DECLINE > REFER > ACCEPT`) across eligibility, missing history, and compound risk factors. | "decide whether to accept the risk ... Some risks are too bad — maybe decline, maybe refer to a senior underwriter; the rules should decide." | `D05` (Underwriting Decision) |
| **BR-07** | The system shall determine whether a pre-cover physical inspection is required (`REQUIRED`, `NOT_REQUIRED`, `NOT_APPLICABLE`), mandating inspection for high-value vehicles and older comprehensive risks, and marking declined risks `NOT_APPLICABLE`. | "decide whether a physical inspection is required before cover starts ... Very high vehicle value means an inspection." | `D06` (Inspection Decision) |
| **BR-08** | The system shall compute an illustrative annual base premium (`D07`) reflecting vehicle type, engine displacement, coverage type (`COMPREHENSIVE > TPO`), and insured value. | "Comprehensive cover costs more than third-party-only. Engine size matters somehow..." | `D07` (Base Premium Calculation) |
| **BR-09** | The system shall compute cumulative additive risk loading (`D08`) across driver risk, claims risk, vehicle risk, and sporty/high-performance classification. | "Young drivers and those with recent claims are riskier, so they pay more ... Sporty/high-performance vehicles attract a loading." | `D08` (Risk Loading Calculation) |
| **BR-10** | The system shall compute the final annual premium (`D09`) as `Base Premium * (1 + Total Risk Loading)` for `ACCEPT` (and indicative provisional quote for `REFER`), and `0` for `DECLINE`. | "if accepted, we set the premium..." | `D09` (Final Premium Calculation) |

---

## 3. Non-Functional & Modeling Governance Requirements

| Req ID | Requirement | Verification Method |
|---|---|---|
| **NFR-01** | **DMN 1.3 Conformance:** Model uses namespace `http://www.omg.org/spec/DMN/20191111/MODEL/` with valid DMNDI diagram interchange, typed edges, and acyclic DAG structure. | `dmn-moddle@12.2.1` + `lxml` + `dmn-js@18.1.0` |
| **NFR-02** | **Completeness:** Every decision table handles all valid, boundary, and missing/invalid inputs with zero silent fall-throughs. | Decision table overlap/completeness audit + boundary tests |
| **NFR-03** | **Reproducibility:** No reliance on non-deterministic system clock (`today()`); `evaluationDate` is an explicit model input. | Canonical JSON & test suite (`feelin@8.2.2`) |
| **NFR-04** | **Educational Transparency:** All thresholds, base rates, and loading percentages are explicitly documented as illustrative educational assumptions, not commercial actuarial tariffs. | `AMBIGUITY_REGISTER.md` & Report Sec. 3 & 6 |
