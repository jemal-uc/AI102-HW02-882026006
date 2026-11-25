# Validation Report — AI102 Homework-02 (`AsuransiNusantara`)

**Model Artifact:** `src/decision-model/AsuransiNusantara.dmn`  
**Validation Evidence File:** `tests/test-results/TEST_RESULTS.json`

---

## 1. Multi-Level Validation Summary

| Level | Scope | Tool & Version | Result | Key Evidence |
|---|---|---|---|---|
| **Level 1 — XML & Structural** | Well-formedness, DMN 1.3 namespace, ID/href integrity, DAG acyclicity | `defusedxml 0.7.1`, `lxml 6.1.1`, `networkx 3.6.1` | **PASS** | 0 broken refs; `isDAG = true`; min 2 info reqs per decision; 73 rules, 53 DMNDI edges. |
| **Level 2 — DMN 1.3 Editor Load** | Schema deserialization & DRD visual rendering | `dmn-moddle@12.2.1`, `dmn-js@18.1.0` in Microsoft Edge | **PASS** | `warnings = 0`; DRD rendered with all 24 shapes and 53 typed connectors (`tests/validation-evidence/dmnjs_drd_verify.png`). *(Note: standalone desktop Camunda Modeler binary was not installed locally; `dmn-js` is the official engine inside Camunda Modeler).* |
| **Level 3 — FEEL Execution** | 6 FEEL expressions across all 5 assignment categories (15 test cases incl. edge cases) | `feelin@8.2.2` (`Node v24.15.0`) | **PASS (15/15)** | Leap-year `years and months duration` vs `days/365.25` verified (`25` vs `24` on exact birthday). |
| **Level 4 — Business Logic Audit** | Completeness, hit policies, priority ordering, boundary values, missingness | `validate_xml.py` + `validate_all.js` | **PASS** | Zero fall-throughs; `not(true)` and `null` unary tests verified on `null` inputs. |
| **Level 5 — End-to-End Execution** | 10 full cases (`TC-01`–`TC-10`) executed directly from `.dmn` XML | `dmn-moddle@12.2.1` + `feelin@8.2.2` | **PASS (10/10)** | 100% agreement between independent calculations and DMN XML execution (`tests/test-results/TEST_RESULTS.json`). |

---

## 2. Defects Discovered & Resolved During Validation

1. **Defect #1 — DMN 1.3 Namespace Scheme (`http://` vs `https://`):**
   - *Discovery:* The assignment text cited `http://www.omg.org/spec/DMN/20191111/MODEL/`, which failed `dmn-moddle@12.2.1` parsing (`failed to parse document as <dmn:Definitions>`).
   - *Fix:* Used the normative OMG DMN 1.3 URI `https://www.omg.org/spec/DMN/20191111/MODEL/` (`0` warnings in `dmn-moddle` and `dmn-js`).
2. **Defect #2 — Future Date Return Value in `BKM01`:**
   - *Discovery:* Probing `feelin@8.2.2` showed `years and months duration(date("2027-01-01"), date("2026-11-25")).years` evaluates to `0` rather than a negative integer.
   - *Fix:* Added explicit pre-check `if date(targetDate) > date(referenceDate) then -1` in `BKM01` so future dates trigger `INELIGIBLE` (`< 0` / `< 17`) instead of age `0`.
3. **Defect #3 — Unparenthesized `in` List Membership Precedence (`FEEL-02`):**
   - *Discovery:* Initial run returned `null` (`13/15` pass) for `vehicleType in ["MOTORCYCLE", "CAR"] and performanceClass in ["SPORT", "HIGH_PERFORMANCE"]` due to FEEL `in ... and ...` binding ambiguity.
   - *Fix:* Parenthesized both clauses: `(vehicleType in ["MOTORCYCLE", "CAR"]) and (performanceClass in ["SPORT", "HIGH_PERFORMANCE"])` → `15/15` pass.
4. **Defect #4 — IEEE-754 Binary Float Truncation (`TC-10`):**
   - *Discovery:* Initial run failed `TC-10` (`9/10` pass): `200000000 * 0.018` evaluated to `3599999.9999999995`, causing `floor(...)` to output `3,599,999` instead of `3,600,000` (Rp1 under-pricing defect).
   - *Fix:* Replaced `floor(...)` in `D07`, `D09`, and `FEEL-03` with DMN built-in `decimal(..., 0)` → `10/10` pass.
