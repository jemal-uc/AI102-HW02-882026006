# Requirements Traceability Matrix — AI102 Homework-02 (Scenario B)

Every assignment requirement, business rule, Stage 5 correction, and validation obligation is traced below from its source requirement to its implementation artifact and verification mechanism.

---

## 1. Assignment & Deliverable Traceability

| Trace ID | Requirement Source | Requirement Description | Implementation Artifact(s) | Validation Method |
|---|---|---|---|---|
| **TR-01** | Assignment PDF Sec. 1 & 2 | Inspect all workspace sources, document inventory, resolve conflicts | `src/specification/SOURCE_INVENTORY.md`, `src/specification/BUSINESS_REQUIREMENTS.md` | Audit against source PDF & style guide |
| **TR-02** | Assignment PDF Task 1.1 & Stage 5 Sec. 9 / 5.1 Sec. 3 | Complete ambiguity register with explicit regulatory vs. educational policy vs. design attribution | `src/specification/AMBIGUITY_REGISTER.md`, Report Sec. 3 & App. A | Cross-check 12 clauses against `UU 22/2009` Art. 81(2)(a), `Perpol 5/2021` Art. 3 & 8, and `SEOJK 6/2017` |
| **TR-03** | Assignment PDF Task 1.2 | Construct DMN 1.3 DRD (10 decisions, 2 BKMs, 3 KS, typed edges, 5-tier acyclic DAG, >=2 info reqs per decision) | `src/decision-model/DRD_DESIGN.md`, `outputs/diagrams/DRD_DIAGRAM.png`, `src/decision-model/AsuransiNusantara.dmn` | `dmn-moddle@12.2.1` + `dmn-js@18.1.0` + `validate_xml.py` (`networkx` DAG verifier) |
| **TR-04** | Assignment PDF Task 1.3 & Stage 5 Sec. 5 | Concise decision responsibility table + one-sentence description for every decision (`D01`–`D10`) | `src/specification/DECISION_DECOMPOSITION.md`, `src/decision-model/DRD_DESIGN.md`, `<decision>/<description>` in XML | Cross-check `10/10` nodes (`D01`–`D10`) |
| **TR-05** | Assignment PDF Task 2.1–2.3 & Stage 5 Sec. 3/6 | Complete decision tables (`D01`–`D10`, `94` rules total), explicit input/output types, justified hit policies, no `Rp0` fallback on invalid/missing inputs | `src/business-rules/DECISION_TABLES.md`, `src/business-rules/BUSINESS_RULE_CATALOG.md`, `CANONICAL_DECISION_SPECIFICATION.json`, `.dmn` XML | `audit_probe.py` (spec-vs-XML `0` mismatches) + `feelin@8.2.2` execution |
| **TR-06** | Assignment PDF Task 2.4 & Stage 5 Sec. 4 / 5.1 Sec. 4 | Original 10 E2E scenarios (`TC-01`–`TC-10`) + Stage 5/5.1 regression cases (`TC-11`–`TC-19`) + preserved Stage 2 cases (`TC-20`–`TC-27`) | `tests/test-cases/END_TO_END_TEST_CASES.md`, `tests/test-results/TEST_RESULTS.json`, `INDEPENDENT_EXECUTION_RESULTS.json` | Independent pure-JS reference arithmetic vs. DMN XML execution (`27/27 PASS`) |
| **TR-07** | Assignment PDF Task 3 & Stage 5 Sec. 7 | >= 5 distinct FEEL expressions covering all 5 required categories, each with >= 2 examples incl. future/null DOB and recency boundaries | `src/business-rules/FEEL_EXPRESSIONS.md`, `tests/test-results/TEST_RESULTS.json` | Executed directly in `feelin@8.2.2` (`18/18 PASS`) |
| **TR-08** | Assignment PDF Task 4.1 & Stage 5 Sec. 8 | Transparent validation evidence documenting exact XML-driven harness architecture, `feelin` usage, and non-engine limitations | `tests/validation-evidence/VALIDATION_SUMMARY.md`, `tests/validation-evidence/VALIDATION_REPORT.md` | `validate_all.js` + `independent_dmn_executor.js` + `audit_probe.py` + `dmn-js` |
| **TR-09** | Assignment PDF Task 4.2 & Sec. 6 | Valid DMN 1.3 XML (`https://www.omg.org/spec/DMN/20191111/MODEL/`) synchronized across public & local submission `.dmn` | `src/decision-model/AsuransiNusantara.dmn`, local `submission/AI102-HW02-<LeaderNIM>.dmn` | `lxml`/`defusedxml` + `DMN13.xsd` (`0` errors) + `dmn-moddle` (`0` warnings) |
| **TR-10** | Assignment PDF Task 4.3 & Stage 5 Sec. 10–12 | Academic PDF report (**2–3 pages main text** + Appendices A–G, two-member identity without role labels, truthful Antigravity + ChatGPT disclosure) | `reports/AI102_HW02_AsuransiNusantara_Report.pdf` & `submission/` | Page-by-page visual render & inspection (`pymupdf` -> PNG) |

---

## 2. Business Rule & Decision Node Traceability

| Rule Group | Decision / BKM | Business Rules Covered | Originating Narrative / Ambiguity | Verification Test Cases |
|---|---|---|---|---|
| `BKM01` | `calculateAgeInYears` | Literal FEEL Function (`1`) | `AMB-01`, `AMB-04`, `KS03` | `FEEL-04`, `TC-01`–`TC-27` |
| `BKM02` | `countRecentClaims` | Literal FEEL Function (`1`) | `AMB-02`, `AMB-03` | `FEEL-05`, `TC-01`–`TC-27` |
| `D01` | Driver Risk Assessment | `R-D01-01` .. `R-D01-06` (`6`) | `AMB-01`, `AMB-11`, `BR-02` | `TC-01`–`TC-04`, `TC-07`, `TC-09`, `TC-10`, `TC-17`, `TC-20`, `TC-26` |
| `D02` | Claims Risk Assessment | `R-D02-01` .. `R-D02-05` (`5`) | `AMB-02`, `AMB-03`, `BR-03` | `TC-01`, `TC-03`, `TC-05`, `TC-07`, `TC-18`, `TC-24`, `TC-25` |
| `D03` | Vehicle Eligibility Assessment | `R-D03-01` .. `R-D03-07` (`7`) | `AMB-04`, `AMB-11`, `AMB-12`, `BR-01`, `BR-04` | `TC-02`, `TC-04`, `TC-16`, `TC-19`, `TC-21`, `TC-22` |
| `D04` | Vehicle Risk Assessment | `R-D04-00a` .. `R-D04-10` (`14`) | `AMB-06`, `AMB-07`, `BR-05` | `TC-01`–`TC-08`, `TC-23`, `TC-27` |
| `D05` | Underwriting Decision | `R-D05-01` .. `R-D05-10` (`10`) | `AMB-10`, `AMB-12`, `BR-06` | `TC-01`–`TC-27` |
| `D06` | Inspection Decision | `R-D06-01` .. `R-D06-06` (`6`) | `AMB-05`, `BR-07` | `TC-01`, `TC-02`, `TC-04`–`TC-06`, `TC-11`–`TC-13`, `TC-16`, `TC-19` |
| `D07` | Base Premium Calculation | `R-D07-00` .. `R-D07-13` (`14`) | `AMB-07`, `AMB-08`, `AMB-12`, `BR-08` | `TC-01`–`TC-22` (`null` safety) |
| `D08` | Risk Loading Calculation | `R-D08-01` .. `R-D08-14` (`14`) | `AMB-09`, `BR-09` | `TC-01`–`TC-08`, `TC-14`, `TC-15`, `TC-23` |
| `D09` | Final Premium Calculation | `R-D09-01` .. `R-D09-06` (`6`) | `AMB-09`, `AMB-10`, `AMB-12`, `BR-11` | `TC-01`–`TC-27` (`DECLINE`/`REFER`/pending -> `null`) |
| `D10` | Quote Readiness Assessment | `R-D10-01` .. `R-D10-12` (`12`) | `AMB-12`, `BR-10` | `TC-01`–`TC-19` (esp. `TC-11`–`TC-16`, `TC-19`) |
