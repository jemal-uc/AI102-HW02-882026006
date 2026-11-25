# Validation Summary — AsuransiNusantara DMN 1.3 Model

**Canonical Model:** `src/decision-model/AsuransiNusantara.dmn`  
**Canonical Specification:** `src/specification/CANONICAL_DECISION_SPECIFICATION.json`  
**DMN Standard & Namespace:** OMG DMN 1.3 (`https://www.omg.org/spec/DMN/20191111/MODEL/`)  
*(Note: The assignment text cited `http://www.omg.org/spec/DMN/20191111/MODEL/`, which fails `dmn-moddle@12.2.1` deserialization; the normative OMG DMN 1.3 `https://` URI is used so DMN 1.3 editors and XSD validators load the model cleanly.)*

---

## 1. XML, Schema & DRD Structural Validation

| Check | Tooling & Method | Result | Evidence Artifact |
|---|---|---|---|
| **Well-Formedness & Reference Integrity** | `defusedxml 0.7.1`, `lxml 6.1.1` (`validate_xml.py`) | **PASS** | `2,090` XML lines; `722` unique `xs:ID`s (`0` duplicates); `0` broken `@href` / `@dmnElementRef` pointers. |
| **Official OMG `DMN13.xsd` Validation** | `lxml.etree.XMLSchema` against local cached `DMN13.xsd`, `DMNDI13.xsd`, `DC.xsd`, `DI.xsd` (`audit_probe.py`) | **PASS (`0` errors)** | `Valid against DMN13.xsd: True | Error count: 0`. |
| **DRD DAG & Requirement Typing** | `networkx 3.6.1` directed graph check (`validate_xml.py`) | **PASS (`isDAG = true`)** | `10` `inputData`, `2` BKMs, `3` `knowledgeSource`s, `9` decisions; `35` information, `5` knowledge, `13` authority edges; min `2` info reqs per decision. |
| **DMNDI Diagram & Editor Load** | `dmn-moddle@12.2.1` + `dmn-js@18.1.0` in headless Microsoft Edge (`capture_dmnjs.py`) | **PASS (`0` warnings)** | `24` non-overlapping `DMNShape`s, `53` `DMNEdge`s (`tests/validation-evidence/dmnjs_drd_verify.png`). |

---

## 2. FEEL Expression & Decision Table Validation

- **FEEL Engine & Runtime:** `feelin@8.2.2` on Node.js `v24.15.0`.
- **FEEL Unit Suite (`validate_all.js`):** **`15 / 15` PASS** across 6 expressions (`FEEL-01`–`FEEL-06`) covering all 5 required DMN categories: interval ranges (`[17..24]`), parenthesized list membership, built-in functions (`max`, `decimal`, `count`), calendar date-duration arithmetic (`years and months duration`, `duration("P24M")`), and compound `if...then...else` logic.
  - *Duration Semantics Check:* On exact 25th birthday (`2001-11-25` to `2026-11-25`), naive `floor((evalDate - dob).days / 365.25)` yields `24` (leap-year drift), whereas `years and months duration(...).years` yields `25`.
- **Decision Table Completeness & Parity (`audit_probe.py`):** **`0` spec-vs-XML mismatches** across all `9` tables (`79` rules total: `2 UNIQUE`, `6 FIRST`, `1 COLLECT SUM`), enforcing `DECLINE > REFER > ACCEPT` precedence, missing-claims `UNKNOWN -> REFER` guards, conservative invalid-input guards in `D04`/`D07`, and IEEE-754-safe `decimal(..., 0)` rounding.

---

## 3. End-to-End Execution & Interpreter Limitations

| Suite | Orchestrator | Cases Executed | Result | Output Artifact |
|---|---|---|---|---|
| **Stage 1 Representative Suite** | `scripts/validation/validate_all.js` | `10` (`TC-01`–`TC-10`) | **`10 / 10` PASS** | `tests/test-results/TEST_RESULTS.json` |
| **Stage 2 XML-Driven Suite** | `scripts/validation/independent_dmn_executor.js` | `18` (`TC-01`–`TC-18`) | **`18 / 18` PASS (`0` warnings)** | `tests/test-results/INDEPENDENT_EXECUTION_RESULTS.json` |

### Execution Harness Scope & Limitations
1. **Custom Table Orchestrators over Genuine FEEL:** Neither standalone desktop Camunda Modeler nor a Java Camunda DMN Engine runtime is installed locally. XML parsing uses `dmn-moddle@12.2.1` and all FEEL expressions/unary tests execute in `feelin@8.2.2`, while decision-table routing is orchestrated in Node.js:
   - `validate_all.js` uses a fixed decision order and regex BKM dispatch, and implements `UNIQUE`, `FIRST`, and `COLLECT (SUM)`.
   - `independent_dmn_executor.js` eliminates those shortcuts by deriving topological order via Kahn's algorithm from `<informationRequirement>`, dynamically binding `<businessKnowledgeModel>` formal parameters as JS functions inside `feelin@8.2.2`, validating outputs against `<itemDefinition>/<allowedValues>`, enforcing zero `feelin` runtime warnings, and cross-checking every premium against an independent pure-JS arithmetic reference (`0` discrepancies across all 18 cases).

---

## 4. Reproducible Commands

```powershell
python scripts\validation\validate_xml.py
python scripts\validation\audit_probe.py
node scripts\validation\validate_all.js
node scripts\validation\independent_dmn_executor.js
python scripts\validation\security_scan.py
```
