# Validation Summary — AsuransiNusantara DMN 1.3 Model

**Canonical Model:** `src/decision-model/AsuransiNusantara.dmn`  
**Canonical Specification:** `src/specification/CANONICAL_DECISION_SPECIFICATION.json`  
**DMN Standard & Namespace:** OMG DMN 1.3 (`https://www.omg.org/spec/DMN/20191111/MODEL/`)  
*(Note: The assignment text cited `http://www.omg.org/spec/DMN/20191111/MODEL/`, which fails `dmn-moddle@12.2.1` deserialization; the normative OMG DMN 1.3 `https://` URI is used so DMN 1.3 editors and XSD validators load the model cleanly.)*

---

## 1. XML, Schema & DRD Structural Validation

| Check | Tooling & Method | Result | Evidence Artifact |
|---|---|---|---|
| **Well-Formedness & Reference Integrity** | `defusedxml 0.7.1`, `lxml 6.1.1` (`validate_xml.py`) | **PASS** | `2,573` XML lines; `881` unique `xs:ID`s (`0` duplicates); `0` broken `@href` / `@dmnElementRef` pointers. |
| **Official OMG `DMN13.xsd` Validation** | `lxml.etree.XMLSchema` against local cached `DMN13.xsd`, `DMNDI13.xsd`, `DC.xsd`, `DI.xsd` (`audit_probe.py`) | **PASS (`0` errors)** | `Valid against DMN13.xsd: True | Error count: 0`. |
| **DRD DAG & Requirement Typing** | `networkx 3.6.1` directed graph check (`validate_xml.py`) | **PASS (`isDAG = true`)** | `10` `inputData`, `2` BKMs, `3` `knowledgeSource`s, **`10` decisions (`D01`–`D10`)**; `42` information, `5` knowledge, `15` authority edges (`62` total); min `2` info reqs per decision. |
| **DMNDI Diagram & Editor Load** | `dmn-moddle@12.2.1` + `dmn-js@18.1.0` in headless Microsoft Edge (`capture_dmnjs.py`) | **PASS (`0` warnings)** | `25` non-overlapping `DMNShape`s, `62` `DMNEdge`s (`tests/validation-evidence/dmnjs_drd_verify.png`). |

---

## 2. Rule Count Reconciliation & FEEL Validation

- **Decision Table Rule Reconciliation (Explicit XML Counts `D01`–`D10`):**

| Decision ID | Decision Name | XML Rule Count |
|---|---|---:|
| `D01` | Driver Risk Assessment | 6 |
| `D02` | Claims Risk Assessment | 5 |
| `D03` | Vehicle Eligibility Assessment | 7 |
| `D04` | Vehicle Risk Assessment | 14 |
| `D05` | Underwriting Decision | 10 |
| `D06` | Inspection Decision | 6 |
| `D07` | Base Premium Calculation | 14 |
| `D08` | Risk Loading Calculation | 14 |
| `D09` | Final Premium Calculation | 6 |
| `D10` | Quote Readiness Assessment | 12 |
| **Total** | **10 Decision Tables** | **94** |

- **Progression Explained:** `73` (Stage 1 initial tables) -> `79` (Stage 2 hardening: `+1 D01`, `+4 D04`, `+1 D07`) -> **`94` XML decision table rules** (Stage 5: `+3 D09` safety gates, `+12 D10` quote readiness) + **`2` BKM FEEL functions** (`BKM01`, `BKM02`). `0` spec-vs-XML mismatches (`audit_probe.py`).
- **FEEL Engine & Runtime:** `feelin@8.2.2` on Node.js `v24.15.0`.
- **FEEL Unit Suite (`validate_all.js`):** **`18 / 18` PASS** across 6 expressions (`FEEL-01`–`FEEL-06`) covering all 5 required DMN categories, leap-year birthday accuracy (`25` vs `24`), missing/future DOB, 3-point claim recency boundary (`2024-11-24`, `2024-11-25`, `2024-11-26`), `null`/empty unary tests (`null, ""`), and IEEE-754-safe `decimal(..., 0)` rounding.

---

## 3. End-to-End Execution & Execution Method Audit (Classification: Option C)

| Suite | Orchestrator | Cases Executed | Result | Output Artifact |
|---|---|---|---|---|
| **Canonical & Regression Suite** | `scripts/validation/validate_all.js` | `19` (`TC-01`–`TC-19`) | **`19 / 19` PASS (`0` warnings)** | `tests/test-results/TEST_RESULTS.json` |
| **Combined XML-Driven Suite** | `scripts/validation/independent_dmn_executor.js` | `27` (`TC-01`–`TC-27`) | **`27 / 27` PASS (`0` warnings)** | `tests/test-results/INDEPENDENT_EXECUTION_RESULTS.json` |

### Execution Mechanism Classification & Limitations
1. **Honest Classification — Option C (Hybrid Test Harness over FEEL Engine + Custom DMN Table Orchestrator):**  
   Neither standalone desktop Camunda Modeler nor a Java Camunda DMN Engine runtime (nor Drools/KIE DMN) is installed locally. Visual parsing in `dmn-js@18.1.0` validates diagram interchange only, **not** decision execution.
2. **Exact Architecture & Coverage:**
   - **XML Deserialization:** `dmn-moddle@12.2.1` reads decision tables, hit policies, formal parameters, `itemDefinition` constraints, and dependency `<informationRequirement>`s directly from `src/decision-model/AsuransiNusantara.dmn`.
   - **FEEL Evaluation:** All BKM bodies, table `inputExpression`s, unary test cells, and `outputEntry` expressions run inside **`feelin@8.2.2`** (`Node.js v24.15.0`).
   - **Topological & Hit-Policy Orchestration:** `independent_dmn_executor.js` builds topological order dynamically via Kahn's algorithm, binds `<businessKnowledgeModel>` parameters as JS closures calling `feelin.evaluate()`, implements `UNIQUE`, `FIRST`, `ANY`, `PRIORITY`, and `COLLECT` (`SUM`/`MIN`/`MAX`/`COUNT`), enforces zero `feelin` warnings, checks outputs against `<itemDefinition>/<allowedValues>`, and cross-verifies premiums against an independent pure-JS arithmetic reference (`0` discrepancies across all `26` cases).
   - **Null & Precision Semantics:** `null` returns natively as JS `null`; `COLLECT SUM` rounds accumulated decimals via `Math.round(sum * 1e6) / 1e6`; individual rules use FEEL `decimal(..., 0)`.
   - **Unsupported DMN Features / Limitations:** Custom JS table orchestration covers decision tables and BKMs modeled here, but does **not** implement boxed contexts, relation literals, generalized `RULE ORDER` / `OUTPUT ORDER` sorting, external Java service invocations, or engine-level input `typeRef` coercion outside table guards.

---

## 4. Reproducible Commands

```powershell
python scripts\validation\validate_xml.py
python scripts\validation\audit_probe.py
node scripts\validation\validate_all.js
node scripts\validation\independent_dmn_executor.js
python scripts\validation\security_scan.py
```
