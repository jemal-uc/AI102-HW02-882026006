# Requirements Traceability Matrix — AI102 Homework-02 (Scenario B)

Every assignment requirement, business rule, and validation obligation is traced below from its source document to its implementation artifact and verification mechanism.

---

## 1. Assignment & Deliverable Traceability

| Trace ID | Requirement Source | Requirement Description | Implementation Artifact(s) | Validation Method |
|---|---|---|---|---|
| **TR-01** | Assignment PDF Sec. 1 & 2 | Inspect all workspace sources, document inventory, resolve conflicts | `src/specification/SOURCE_INVENTORY.md`, `src/specification/BUSINESS_REQUIREMENTS.md` | Manual audit against source PDF & style guide |
| **TR-02** | Assignment PDF Task 1.1 | Complete ambiguity register with open questions, resolutions, and justifications | `src/specification/AMBIGUITY_REGISTER.md`, Report Sec. 3 & App. A | Cross-check all narrative clauses & edge cases |
| **TR-03** | Assignment PDF Task 1.2 | Construct DMN 1.3 DRD (correct shapes, typed edges: info/knowledge/authority, DAG, >=1 info req per decision) | `src/decision-model/DRD_DESIGN.md`, `outputs/diagrams/DRD_DIAGRAM.png`, `src/decision-model/AsuransiNusantara.dmn` | `dmn-moddle@12.2.1` + `dmn-js@18.1.0` + Python DAG verifier |
| **TR-04** | Assignment PDF Task 1.3 | One-sentence requirement for every decision node | `src/specification/DECISION_DECOMPOSITION.md`, `src/decision-model/DRD_DESIGN.md` | Cross-check 9/9 nodes (`D01`–`D09`) |
| **TR-05** | Assignment PDF Task 2.1–2.3 | Decision tables for every decision node (`D01`–`D09`), explicit types, justified hit policies, completeness, overlap resolution | `src/business-rules/DECISION_TABLES.md`, `src/specification/CANONICAL_DECISION_SPECIFICATION.json`, `.dmn` XML | Exhaustive completeness/overlap audit & `feelin@8.2.2` table executor |
| **TR-06** | Assignment PDF Task 2.4 & Prompt Sec. 9 | At least 4 representative end-to-end traces + missing/boundary edge cases (8 cases total), intermediate outputs shown | `tests/test-cases/END_TO_END_TEST_CASES.md`, `tests/test-results/TEST_RESULTS.json`, Report Sec. 4 & App. E | Independent expected calculation vs. `feelin@8.2.2` actual execution |
| **TR-07** | Assignment PDF Task 3 | >= 5 distinct FEEL expressions covering all 5 required categories, each with >= 2 sample inputs incl. edge case | `src/business-rules/FEEL_EXPRESSIONS.md`, `tests/test-results/TEST_RESULTS.json`, Report Sec. 5 & App. D | Executed directly in `feelin@8.2.2` engine |
| **TR-08** | Assignment PDF Task 4.1 | Model validation (simulation/engine trace, edge cases, defects & fixes) | `tests/validation-evidence/VALIDATION_SUMMARY.md`, `tests/validation-evidence/VALIDATION_REPORT.md` | Automated XML/XSD + FEEL + End-to-End test suites + `dmn-js` load test |
| **TR-09** | Assignment PDF Task 4.2 & Sec. 6 | Valid DMN 1.3 XML (`https://www.omg.org/spec/DMN/20191111/MODEL/`) | `src/decision-model/AsuransiNusantara.dmn` (local submission export excluded from public Git) | `lxml`/`defusedxml` parse + `DMN13.xsd` + `dmn-moddle@12.2.1` + `dmn-js@18.1.0` |
| **TR-10** | Assignment PDF Task 4.3 & Style Guide | Academic PDF design documentation (**2–3 pages main text** + appendices; all required sections, ML integration note, AI disclosure) | `reports/final-report/AI102_HW02_AsuransiNusantara_Report.pdf` & `submission/` | Page-by-page visual render & inspection (`pymupdf` -> PNG) |

---

## 2. Business Rule & Decision Node Traceability

| Rule Group | Decision / BKM | Business Rules Covered | Originating Narrative / Ambiguity | Verification Test Cases |
|---|---|---|---|---|
| `BKM01` | `calculateAgeInYears` | `R-BKM01-01` | `AMB-01`, `AMB-04` | `FEEL-04`, `TC-01`–`TC-08` |
| `BKM02` | `countRecentClaims` | `R-BKM02-01` | `AMB-02`, `AMB-03` | `FEEL-03`, `FEEL-04b`, `TC-01`–`TC-08` |
| `D01` | Driver Risk Assessment | `R-D01-01` to `R-D01-06` | `AMB-01` ("Young drivers..."), `AMB-11` | `TC-01`, `TC-02` (age 24/25), `TC-03` (age 22), `TC-08` (senior), `TC-11` (future DOB) |
| `D02` | Claims Risk Assessment | `R-D02-01` to `R-D02-05` | `AMB-02` ("recent claims"), `AMB-03` ("missing claims history") | `TC-01` (0), `TC-03` (1), `TC-05` (missing), `TC-07` (exact 24M boundary) |
| `D03` | Vehicle Eligibility Assessment | `R-D03-01` to `R-D03-07` | `AMB-04` ("Very old vehicles... decline"), `BR-01` | `TC-02` (age 15 eligible), `TC-04` (age 16 decline) |
| `D04` | Vehicle Risk Assessment | `R-D04-00a` to `R-D04-10` | `AMB-06` ("Sporty"), `AMB-07` ("Engine size, especially motorcycles") | `TC-01`–`TC-08`, `TC-14` (`performanceClass=null`) |
| `D05` | Underwriting Decision | `R-D05-01` to `R-D05-10` | `AMB-10` ("decline vs refer vs accept") | `TC-01` (`ACCEPT`), `TC-03` (`REFER`), `TC-04`/`TC-08` (`DECLINE`), `TC-05` (`REFER`) |
| `D06` | Inspection Decision | `R-D06-01` to `R-D06-06` | `AMB-05` ("Very high vehicle value means an inspection") | `TC-01` (`NOT_REQUIRED`), `TC-04` (`NOT_APPLICABLE`), `TC-06` (`insuredValue = 500M -> REQUIRED`) |
| `D07` | Base Premium Calculation | `R-D07-00` to `R-D07-13` | `AMB-07`, `AMB-08` ("Comprehensive > TPO") | `TC-01`–`TC-08`, `TC-13` (`insuredValue=null`) |
| `D08` | Risk Loading Calculation | `R-D08-01` to `R-D08-14` | `AMB-09` ("whether loadings stack") | `TC-01` (0%), `TC-02` (+40%), `TC-03` (+95%), `TC-05` (+25%), `TC-07` (+20%) |
| `D09` | Final Premium Calculation | `R-D09-01` to `R-D09-03` | `BR-10`, `AMB-10` | `TC-01`–`TC-08` |
