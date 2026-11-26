# Motor Insurance Underwriting Decision Model (DMN 1.3) — AsuransiNusantara

**Course Context:** AI102 — Decision Intelligence (Master of Artificial Intelligence, FTI UKSW)  
**Scenario:** Scenario B — Motor Insurance Underwriting (`AsuransiNusantara`)  
**Standard:** OMG DMN 1.3 (`https://www.omg.org/spec/DMN/20191111/MODEL/`)

---

## 1. Project Overview & Problem Statement

Motor insurance underwriting narratives often leave critical business boundaries ambiguous—such as what defines a "young driver," how "recent claims" are counted, how motorcycle and car engine displacements differ, how missing claims history is treated, how incomplete commercial quotation inputs (e.g., missing cover type) differ from risk acceptance, and whether surcharges stack additively. Burying such rules in imperative application code creates opacity and maintenance debt.

This project formalizes the **AsuransiNusantara** motorcycle and car underwriting domain as an executable, deterministic **OMG DMN 1.3** decision model derived from a single canonical JSON specification (`src/specification/CANONICAL_DECISION_SPECIFICATION.json`).

## 2. Objectives

1. Elicit and document every narrative ambiguity while distinguishing statutory Indonesian law (`UU No. 22/2009 Pasal 81(2)(a)`) from illustrative educational underwriting assumptions (`KS01`/`KS02`).
2. Construct a 5-tier acyclic Decision Requirements Diagram (DRD) with typed dependencies (`information`, `knowledge`, `authority`).
3. Separate underwriting risk acceptance (`D05`) from commercial quote readiness (`D10`) and approved final premium issuance (`D09`), eliminating unsafe `Rp0` fallbacks on incomplete/invalid inputs.
4. Implement and execute FEEL expressions across all five DMN expression categories (intervals, list membership, built-in functions, calendar date-duration arithmetic, compound `if...then...else` logic).
5. Validate exported DMN 1.3 XML against official OMG `DMN13.xsd`, `dmn-moddle`, `dmn-js`, and XML-driven `feelin@8.2.2` harnesses.

---

## 3. DMN Architecture & Decision Overview

### 3.1 DRD Elements
- **Input Data (`10`):** `dateOfBirth`, `evaluationDate`, `claimsHistoryAvailable`, `claimDates`, `vehicleManufactureDate`, `vehicleType`, `engineCC`, `performanceClass`, `coverType` (`TPO`, `THIRD_PARTY_ONLY`, `COMPREHENSIVE`), `insuredValue`.
- **Business Knowledge Models (`2`):**
  - `BKM01: calculateAgeInYears(targetDate, referenceDate)` — uses calendar `years and months duration(...).years` with explicit malformed/`null`/future-date (`-1`) guards.
  - `BKM02: countRecentClaims(claimDates, referenceDate, windowMonths)` — evaluates `[referenceDate - P24M, referenceDate]` inclusive with null-item short-circuiting.
- **Knowledge Sources (`3`):** Educational Underwriting Policy (`KS01`), Illustrative Motor Tariff & Loading Schedule (`KS02`, simplified model not implementing regional OJK SEOJK 6/2017 tables), and Indonesian Statutory Licensing Reference (`KS03`: **UU No. 22/2009 Pasal 81(2)(a)** & **Perpol No. 5/2021 Pasal 3, 8**, enforcing the `<17` base floor while noting `SIM CI`/`CII` displacement-age rules as a model limitation).
- **Decisions (`10` nodes, `94` decision table rules):**

| ID | Decision | Hit Policy | Rules | Responsibility |
|---|---|---|---|---|
| `D01` | Driver Risk Assessment | `UNIQUE` | 6 | Classifies driver risk (`LOW`, `MEDIUM`, `HIGH`, `INELIGIBLE`, `UNKNOWN`) from age (`<0`, `[0..17)`, `[17..24]`, `[25..65]`, `>65`). |
| `D02` | Claims Risk Assessment | `FIRST` | 5 | Guards missing history (`UNKNOWN`) before scoring 24-month claims (`0 -> LOW`, `1 -> MEDIUM`, `>=2 -> HIGH`). |
| `D03` | Vehicle Eligibility Assessment | `FIRST` | 7 | Hard eligibility gate enforcing supported type, age `<= 15` years, positive `engineCC`, and non-invalid `insuredValue` (deferring `null` valuation to `D10`). |
| `D04` | Vehicle Risk Assessment | `FIRST` | 14 | Grades vehicle risk (`LOW`, `MEDIUM`, `HIGH`) by vehicle type, displacement tier, performance class, and age `>10`, with conservative guards. |
| `D05` | Underwriting Decision | `FIRST` | 10 | Enforces strict precedence **`DECLINE > REFER > ACCEPT`** strictly on risk factors, independently of commercial `coverType`. |
| `D06` | Inspection Decision | `FIRST` | 6 | Assigns `NOT_APPLICABLE` if declined; `REQUIRED` if `insuredValue >= Rp500M`, older (`>10y`) `COMPREHENSIVE`, or incomplete data (never silently `NOT_REQUIRED` on `null` valuation); else `NOT_REQUIRED`. |
| `D07` | Base Premium Calculation | `FIRST` | 14 | Computes illustrative IDR base premium guaranteeing `COMPREHENSIVE > TPO / THIRD_PARTY_ONLY`, or returns `null` when pricing inputs are incomplete/invalid. |
| `D08` | Risk Loading Calculation | `COLLECT (SUM)` | 14 | Sums four orthogonal additive loading components (`driverRisk`, `claimsRisk`, `vehicleRisk`, `performanceClass`). |
| `D09` | Final Premium Calculation | `FIRST` | 6 | Outputs `decimal(basePremium * (1 + totalRiskLoading), 0)` strictly when `D05="ACCEPT"`, `D10="READY"`, and `basePremium > 0`; else `null`. |
| `D10` | Quote Readiness Assessment | `FIRST` | 12 | Separates commercial/pricing readiness (`READY`, `PENDING_INFORMATION`, `INVALID_INPUT`, `NOT_APPLICABLE`) from risk acceptance (`D05`). |

### 3.2 Highlighted FEEL Constructs
Six validated FEEL expressions (`FEEL-01`–`FEEL-06`, `18/18` passing unit tests) cover interval ranges, parenthesized list membership, built-ins (`max`, `decimal`, `count`), calendar date-duration arithmetic avoiding `365.25`-day leap-year drift, and compound conditional precedence.

---

## 4. Repository Structure

```text
.
├── .gitignore                        # Excludes private submission, lecturer PDFs, caches, and node_modules
├── .gitattributes                    # Consistent LF/binary handling across platforms
├── README.md                         # Public project documentation (sanitized)
├── requirements.txt                  # Python dependencies
├── package.json / package-lock.json  # Node.js DMN/FEEL dependencies
├── src/
│   ├── specification/                # Canonical JSON spec, requirements, ambiguity register, data dictionary
│   ├── decision-model/               # Sanitized public AsuransiNusantara.dmn, DRD design, architecture rationale
│   └── business-rules/               # Decision tables, FEEL catalog, business rule catalog (94 rules + 2 BKMs)
├── tests/
│   ├── test-cases/                   # Documented end-to-end case traces (TC-01..TC-18)
│   ├── test-results/                 # Automated JSON validation outputs (TEST_RESULTS.json, INDEPENDENT_EXECUTION_RESULTS.json)
│   └── validation-evidence/          # Official OMG DMN 1.3 XSDs, dmn-js screenshot, VALIDATION_REPORT.md, VALIDATION_SUMMARY.md
├── scripts/
│   ├── build/                        # build_dmn.py, build_report.py
│   ├── validation/                   # validate_xml.py, validate_all.js, independent_dmn_executor.js, audit_probe.py, security_scan.py
│   └── rendering/                    # render_drd_figure.py, capture_dmnjs.py, render_dmnjs.html
├── outputs/
│   └── diagrams/                     # DRD_DIAGRAM.png
└── docs/
    └── REPOSITORY_DOCUMENTATION_POLICY.md  # Public vs. private/archived artifact policy
```

*(Note: Local academic submission artifacts—including `.submission_identity.json`, `reports/AI102_HW02_AsuransiNusantara_Report.{html,pdf}`, `submission/`, and external historical audit logs—are governed according to repository documentation and privacy policies.)*

---

## 5. Technology, Tooling & Installation

- **Python 3.11.9:** `defusedxml==0.7.1`, `lxml==6.1.1`, `networkx==3.6.1`, `matplotlib==3.9.2`, `PyMuPDF==2.0`
- **Node.js v24.15.0:** `feelin@8.2.2` (FEEL engine), `dmn-moddle@12.2.1` (DMN 1.3 XML parser), `dmn-js@18.1.0` (DRD viewer)

```powershell
python -m pip install -r requirements.txt
npm ci
```

---

## 6. Build, Validation & Test Instructions

```powershell
python scripts\build\build_dmn.py
python scripts\validation\validate_xml.py
node scripts\validation\validate_all.js
node scripts\validation\independent_dmn_executor.js
python scripts\validation\audit_probe.py
python scripts\validation\security_scan.py
python scripts\rendering\render_drd_figure.py
```

---

## 7. Business Assumptions, Limitations & AI Assistance Disclosure

- **Regulatory vs. Educational Scope:** Only the baseline `<17` minimum driver age traces to statutory Indonesian law (**UU No. 22/2009 Pasal 81(2)(a)** & **Perpol No. 5/2021 Pasal 3, 8**, Korlantas Polri). Note that `Perpol No. 5/2021` requires age `17` for `SIM C` (`<=250 cc`), `18` for `SIM CI` (`>250–500 cc`), and `19` for `SIM CII` (`>500 cc`); motorcycle `SIM CI`/`CII` displacement-age validation is documented as a model limitation. Displacement bands, `15`-year vehicle limit, `24`-month lookback, `Rp500M` inspection trigger, base tariff tables, and additive surcharges are **illustrative educational assumptions** (not official OJK tariffs under SEOJK No. 6/SEOJK.05/2017).
- **Execution Harness Scope:** End-to-end tests execute via a **hybrid JS test harness** combining `dmn-moddle@12.2.1` XML parsing with **`feelin@8.2.2`** FEEL evaluation and custom topological/hit-policy orchestration (`UNIQUE`, `FIRST`, `COLLECT SUM`); neither desktop Camunda Modeler nor Java Camunda DMN Engine is installed locally.
- **AI Assistance Disclosure:** Generative AI assistance (ChatGPT for assignment interpretation, architectural review, and business-rule critique; Antigravity AI coding assistant for DMN XML generation scripting, automated validation harness construction, defect resolution, and typesetting) was utilized, with all modeling semantics and validation outputs reviewed by the project team.
