# Validation Report — AI102 Homework-02 (`AsuransiNusantara`)

**Model Artifact:** `src/decision-model/AsuransiNusantara.dmn`  
**Validation Evidence Files:** `tests/test-results/TEST_RESULTS.json`, `tests/test-results/INDEPENDENT_EXECUTION_RESULTS.json`

---

## 1. Multi-Level Validation Summary

| Level | Scope | Tool & Version | Result | Key Evidence |
|---|---|---|---|---|
| **Level 1 — XML & Structural** | Well-formedness, DMN 1.3 `https://` namespace, ID/`href` integrity, 5-tier DAG acyclicity | `defusedxml 0.7.1`, `lxml 6.1.1`, `networkx 3.6.1` (`validate_xml.py`) | **PASS** | `0` broken refs; `isDAG = true`; min `2` info reqs per decision; **94 decision table rules** + **2 BKM FEEL functions**, `62` DMNDI edges, `25` shapes. |
| **Level 2 — XSD & DMN 1.3 Load** | Official OMG `DMN13.xsd` validation & `dmn-js` DRD visual rendering | `lxml` (`DMN13.xsd`), `dmn-moddle@12.2.1`, `dmn-js@18.1.0` | **PASS** | `DMN13.xsd` errors = `0`; `dmn-moddle` warnings = `0`; DRD rendered with `25` non-overlapping shapes & `62` edges (`dmnjs_drd_verify.png`). |
| **Level 3 — FEEL Execution** | 6 FEEL expressions across all 5 categories (`18` tests incl. future/null DOB and 3-point recency bounds) | `feelin@8.2.2` (`Node v24.15.0`) | **PASS (18/18)** | `years and months duration` vs `days/365.25` verified (`25` vs `24` on exact birthday); 0 warnings on `null`/`""`. |
| **Level 4 — Business Logic & Premium Safety** | Completeness, hit policies, underwriting vs. quote readiness separation (`D05` vs `D10`), `null` premium safety | `audit_probe.py` + `feelin@8.2.2` | **PASS** | `0` spec-vs-XML mismatches; `coverType` missing/empty/unsupported and `insuredValue=null` never yield `Rp0`; `REFER`/`DECLINE` return `finalPremium=null`. |
| **Level 5 — End-to-End Execution** | `19` canonical/regression cases (`validate_all.js`) & `27` XML-driven cases (`independent_dmn_executor.js`) | **Hybrid JS Harness** (`dmn-moddle@12.2.1` + `feelin@8.2.2`) | **PASS (19/19 & 27/27)** | 100% agreement between independent pure-JS arithmetic & XML-driven FEEL execution (`0` runtime warnings). |

---

## 2. Historical & Stage 5 Defects Resolved

1. **Stage 1/2 Defects Fixed:**
   - Normative DMN 1.3 namespace changed from `http://` to `https://www.omg.org/spec/DMN/20191111/MODEL/` (`DMN13.xsd`: `0` errors).
   - Future-date sentinel `-1` added in `BKM01` and isolated as `R-D01-02 (< 0)` in `D01`; null-list-item guards added in `BKM02`; conservative missing-input guards (`R-D04-00a..00d`, `R-D07-00`) added (`73 -> 79` rules).
   - `FEEL-02` parenthesized around `in` clauses; `decimal(..., 0)` applied in `D07`/`D09` to eliminate IEEE-754 Rp1 under-truncation on `200M * 0.018`.
2. **Stage 5 Critical Architectural & QA Defects Resolved (`79 -> 94` rules):**
   - **Underwriting vs. Quote Readiness Conflation:** Missing/empty/unsupported `coverType` previously allowed `D05 = ACCEPT` alongside `D07 = Rp0` and `D09 = Rp0`. Added `D10: Quote Readiness Assessment` (`12` rules) and changed `D07`/`D09` uncalculable/non-`ACCEPT` outputs from `0` to explicit `null` (`D09` expanded from `3` `UNIQUE` rules to `6` `FIRST` rules; `D03` updated to defer `insuredValue = null` to `D10`; `"THIRD_PARTY_ONLY"` supported alongside `"TPO"`).
   - **Rule Count Reconciliation:** Documented exact progression `73` (Stage 1) -> `79` (Stage 2, `+6` guards) -> `94` (Stage 5, `+12` `D10` + `+3` `D09` safety gates) + `2` BKM FEEL functions.
