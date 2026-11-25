# Motor Insurance Underwriting Decision Model (DMN 1.3) — AsuransiNusantara

**Course Context:** AI102 — Decision Intelligence (Master of Artificial Intelligence, FTI UKSW)  
**Scenario:** Scenario B — Motor Insurance Underwriting (`AsuransiNusantara`)  
**Standard:** OMG DMN 1.3 (`https://www.omg.org/spec/DMN/20191111/MODEL/`)

---

## 1. Project Overview & Problem Statement

Motor insurance underwriting narratives often leave critical business boundaries ambiguous—such as what defines a "young driver," how "recent claims" are counted, how motorcycle and car engine displacements differ, how missing claims history is treated, and whether surcharges stack additively. Burying such rules in imperative application code creates opacity and maintenance debt.

This project formalizes the **AsuransiNusantara** motorcycle and car underwriting domain as an executable, deterministic **OMG DMN 1.3** decision model derived from a single canonical JSON specification (`src/specification/CANONICAL_DECISION_SPECIFICATION.json`).

## 2. Objectives

1. Elicit and document every narrative ambiguity with transparent educational thresholds.
2. Construct a 4-tier acyclic Decision Requirements Diagram (DRD) with typed dependencies (`information`, `knowledge`, `authority`).
3. Engineer complete decision tables with justified hit policies (`UNIQUE`, `FIRST`, `COLLECT SUM`) and zero silent fall-throughs.
4. Implement and execute FEEL expressions across all five DMN expression categories (intervals, list membership, built-in functions, calendar date-duration arithmetic, compound `if...then...else` logic).
5. Validate the exported DMN 1.3 XML against official OMG `DMN13.xsd`, `dmn-moddle`, `dmn-js`, and automated end-to-end test suites.

---

## 3. DMN Architecture & Decision Overview

### 3.1 DRD Elements
- **Input Data (`10`):** `dateOfBirth`, `evaluationDate`, `claimsHistoryAvailable`, `claimDates`, `vehicleManufactureDate`, `vehicleType`, `engineCC`, `performanceClass`, `coverType`, `insuredValue`.
- **Business Knowledge Models (`2`):**
  - `BKM01: calculateAgeInYears(targetDate, referenceDate)` — uses calendar `years and months duration(...).years` with explicit malformed/future-date (`-1`) guards.
  - `BKM02: countRecentClaims(claimDates, referenceDate, windowMonths)` — evaluates `[referenceDate - P24M, referenceDate]` inclusive with null-item short-circuiting.
- **Knowledge Sources (`3`):** Educational Underwriting Policy (`KS01`), Illustrative Motor Tariff & Loading Schedule (`KS02`), and Indonesian Traffic Law UU No. 22/2009 (`KS03`, minimum SIM age 17).
- **Decisions (`9` nodes, `79` rules):**

| ID | Decision | Hit Policy | Rules | Responsibility |
|---|---|---|---|---|
| `D01` | Driver Risk Assessment | `UNIQUE` | 6 | Classifies driver risk (`LOW`, `MEDIUM`, `HIGH`, `INELIGIBLE`, `UNKNOWN`) from age (`<0`, `[0..17)`, `[17..24]`, `[25..65]`, `>65`). |
| `D02` | Claims Risk Assessment | `FIRST` | 5 | Guards missing history (`UNKNOWN`) before scoring 24-month claims (`0 -> LOW`, `1 -> MEDIUM`, `>=2 -> HIGH`). |
| `D03` | Vehicle Eligibility Assessment | `FIRST` | 7 | Hard eligibility gate enforcing supported type, age `<= 15` years, and positive `engineCC` / `insuredValue`. |
| `D04` | Vehicle Risk Assessment | `FIRST` | 14 | Grades vehicle risk (`LOW`, `MEDIUM`, `HIGH`) by vehicle type, displacement tier, performance class, and age `>10`, with conservative guards. |
| `D05` | Underwriting Decision | `FIRST` | 10 | Enforces strict precedence **`DECLINE > REFER > ACCEPT`** across eligibility, unknown history, and compound risks. |
| `D06` | Inspection Decision | `FIRST` | 6 | Assigns `NOT_APPLICABLE` if declined; `REQUIRED` if `insuredValue >= Rp500M` or older (`>10y`) `COMPREHENSIVE`; else `NOT_REQUIRED`. |
| `D07` | Base Premium Calculation | `FIRST` | 14 | Computes illustrative IDR base premium by `(vehicleType, engineCC, coverType, insuredValue)` guaranteeing `COMPREHENSIVE > TPO`. |
| `D08` | Risk Loading Calculation | `COLLECT (SUM)` | 14 | Sums four orthogonal additive loading components (`driverRisk`, `claimsRisk`, `vehicleRisk`, `performanceClass`). |
| `D09` | Final Premium Calculation | `UNIQUE` | 3 | Outputs `0` if `DECLINE`, else `decimal(basePremium * (1 + totalRiskLoading), 0)`. |

### 3.2 Highlighted FEEL Constructs
Six validated FEEL expressions (`FEEL-01`–`FEEL-06`) cover interval ranges (`[17..24]`), parenthesized list membership (`(vehicleType in ["MOTORCYCLE", "CAR"]) and ...`), built-ins (`max`, `decimal`, `count`), calendar date-duration arithmetic (`years and months duration`, `duration("P24M")` avoiding `365.25`-day leap-year drift), and compound conditional precedence.

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
│   └── business-rules/               # Decision tables, FEEL catalog, business rule catalog
├── tests/
│   ├── test-cases/                   # Documented end-to-end case traces
│   ├── test-results/                 # Stage 1 & Stage 2 machine-readable JSON validation outputs
│   └── validation-evidence/          # Official OMG DMN 1.3 XSDs, dmn-js screenshot, validation report
├── scripts/
│   ├── build/                        # build_dmn.py, build_report.py
│   ├── validation/                   # validate_xml.py, validate_all.js, independent_dmn_executor.js, audit_probe.py, security_scan.py
│   └── rendering/                    # render_drd_figure.py, capture_dmnjs.py, render_dmnjs.html
├── outputs/
│   └── diagrams/                     # DRD_DIAGRAM.png
├── docs/
│   └── REPOSITORY_DOCUMENTATION_POLICY.md  # Public vs. private/archived artifact policy
└── tests/validation-evidence/
    └── VALIDATION_SUMMARY.md         # Consolidated XML/XSD, DRD, FEEL, and E2E validation summary
```

*(Note: Local academic submission artifacts—including the original lecturer assignment PDF, `ACADEMIC-REPORT-STANDARD/`, `.submission_identity.json`, `reports/final-report/` with required academic AI disclosure, `outputs/generated-artifacts/`, and `submission/`—are retained locally and excluded from public Git tracking via `.gitignore`. Internal development/audit history logs are archived externally outside the repository.)*

---

## 5. Technology, Tooling & Installation

### Verified Environment & Dependencies
- **Python 3.11.9:** `defusedxml==0.7.1`, `lxml==6.1.1`, `networkx==3.6.1`, `matplotlib==3.9.2`, `PyMuPDF==2.0`
- **Node.js v24.15.0:** `feelin@8.2.2` (FEEL engine), `dmn-moddle@12.2.1` (DMN 1.3 XML parser), `dmn-js@18.1.0` (DRD viewer)
- **External Optional Tools:** Microsoft Edge (`msedge.exe`, headless PDF compilation and `dmn-js` capture); OMG DMN 1.3 XSDs cached offline under `tests/validation-evidence/xsd/`.

### Installation (Isolated Environments Recommended)
```powershell
python -m pip install -r requirements.txt
npm ci
```

---

## 6. Build, Validation & Test Instructions

Run all commands from the project root:

```powershell
# 1. Regenerate public DMN 1.3 XML from canonical specification
python scripts\build\build_dmn.py

# 2. Validate XML structure, references, and DRD DAG acyclicity
python scripts\validation\validate_xml.py

# 3. Execute Stage 1 FEEL (15/15) & End-to-End (10/10) validation via feelin@8.2.2
node scripts\validation\validate_all.js

# 4. Execute Stage 2 independent XML-driven DMN executor (18/18, zero warnings, pure-JS arithmetic check)
node scripts\validation\independent_dmn_executor.js

# 5. Validate against official OMG DMN13.xsd & cross-check spec-vs-XML parity
python scripts\validation\audit_probe.py

# 6. Run security, secret, absolute-path, and PII hygiene scan across public trackable files
python scripts\validation\security_scan.py

# 7. Regenerate DRD figure (outputs/diagrams/DRD_DIAGRAM.png)
python scripts\rendering\render_drd_figure.py
```

### Reproducibility Notes
- All date-dependent rules accept an explicit `evaluationDate` input rather than calling `today()`, ensuring deterministic test replay across any execution date.
- `node scripts\validation\independent_dmn_executor.js` derives evaluation order dynamically from XML `<informationRequirement>` via Kahn's algorithm and binds `<businessKnowledgeModel>` functions directly into `feelin@8.2.2`.

---

## 7. Business Assumptions, Limitations & Disclaimers

- **Educational & Non-Production Disclaimer:** All age bands, displacement cutoffs, Rp500M inspection threshold, base premium rates, and additive loading percentages are **illustrative educational assumptions**. They are **not** actuarially calibrated commercial tariffs and must **not** be used for production insurance pricing or underwriting.
- **Tooling Scope:** Standalone desktop Camunda Modeler was not used locally; structural and visual DMN 1.3 verification relied on `DMN13.xsd`, `dmn-moddle@12.2.1`, and `dmn-js@18.1.0` (the underlying DMN library used by Camunda Modeler).
- **Licensing & Attribution:** No permissive open-source `LICENSE` file is attached because course assignment framing and third-party OMG/tooling materials carry separate ownership/redistribution terms (`feelin`, `dmn-moddle`, and `dmn-js` are third-party npm packages governed by their respective licenses in `package-lock.json`).
- **AI Assistance Disclosure:** Generative AI coding assistance was utilized for requirements structuring, DMN 1.3 XML generation scripting, automated validation harness development, defect diagnosis, and technical report formatting, with all modeling assumptions and verification results independently audited.
