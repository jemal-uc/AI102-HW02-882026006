# Source Inventory — AI102 Homework-02 (Decision Modeling with DMN)

**Inspection Date:** 2026-11-25  
**Workspace:** Project root (`.`)  
**Selected Business Scenario:** Scenario B — Motor Insurance Underwriting (`AsuransiNusantara`)

---

## 1. Existing Workspace File Inventory

| Filename | File Type | Purpose | Key Requirements / Observations |
|---|---|---|---|
| `AI102_Homework-02_Decision-Modeling-DMN_Assignment.docx.pdf` *(local-only)* | PDF (5 pages) | Official lecturer assignment specification for AI102 Homework-02 | Course: AI102 — Decision Intelligence (3 SKS), Master of Artificial Intelligence, FTI UKSW; Lecturer: Teguh Indra Bayu, S.Kom., M.Cs., Ph.D.; Odd Semester 2026/2027; Group work (2–3 members per RPS); Deliverables: `AI102-HW02-<LeaderNIM>.dmn` (DMN 1.3 XML) + PDF Design Documentation Report (**2–3 pages main text + appendices**, cover metadata, division of labor, AI disclosure appendix). Tasks 1–4 totaling 100 pts. |
| `ACADEMIC-REPORT-STANDARD/ACADEMIC_REPORT_STYLE_GUIDE.md` *(local-only)* | Markdown | Global academic report visual and structural standard | A4 portrait; clean white background; navy-blue & muted-blue hierarchy; Times New Roman 9–9.5 pt justified body; Arial Bold uppercase main headings (10–10.5 pt); Arial Bold blue subheadings (9–9.5 pt); compact tables (~7.3–7.8 pt); running headers & footers (`Page X of Y`); italic captions below figures/tables; compact academic opening (no standalone decorative cover page). |
| `ACADEMIC-REPORT-STANDARD/Example-1.pdf` *(local-only)* | PDF (10 pages) | Visual design reference | Demonstrates navy header bars, crisp rule-separated tables, restrained panel diagrams, running headers/footers, and AI assistance disclosure log. |
| `ACADEMIC-REPORT-STANDARD/Example-2.pdf` *(local-only)* | PDF (2 pages) | Visual design reference | Demonstrates high-density 2-page A4 academic layout, Times New Roman body, Arial Bold navy headings, compact tables, `Figure` panels, and concise AI disclosure + numbered references. |

---

## 2. Extracted Authoritative Requirements Summary

### 2.1 Required Deliverables & Naming Conventions
1. **DMN 1.3 XML Model:** Canonical public file `src/decision-model/AsuransiNusantara.dmn` (locally exported as `AI102-HW02-<LeaderNIM>.dmn` in `submission/`, excluded from public Git).
   - Must conform to DMN 1.3 XML namespace `https://www.omg.org/spec/DMN/20191111/MODEL/`.
   - Must include DRD, Input Data, Decisions, Business Knowledge Models (where applicable), Knowledge Sources, typed dependency edges, complete decision tables with justified hit policies, and valid FEEL expressions.
   - **Privacy Separation:** Student names and NIMs are stored in local-only submission configuration (`.submission_identity.json`) and local PDF deliverables, and omitted from public Git-tracked artifacts.
2. **Design Documentation Report (PDF):**
   - **Page budget:** Strictly **2–3 pages main text**, excluding appendices.
   - **Language:** English (matching the assignment specification and `Example-2.pdf`).
   - **Main text mandatory sections:**
     1. Model overview with DRD figure.
     2. Decision decomposition rationale (why these decisions, this granularity).
     3. Ambiguity-resolution table summary (Task 1).
     4. Decision table logic, hit-policy rationale, and representative trace results (Tasks 2 and 4).
     5. FEEL expressions and validation evidence (Task 3).
     6. Known limitations, including where a machine-learned score could be integrated per Session 03 (as a BKM or input data).
     7. Division of labor among group members.
   - **Mandatory appendices:**
     - Complete ambiguity-resolution register, full data dictionary, complete decision tables, complete FEEL expressions, all validation cases & end-to-end traces, FEEL engine & XML validation evidence, and truthful **AI-Assistance Disclosure**.
3. **Submission packaging:** Google Classroom (one submission per group; optional ZIP if a single upload is required). GitHub is **not** required.

---

## 3. Group Identity Separation & Conflicts Resolution

### 3.1 Local vs. Public Identity Handling
- Two-author academic group metadata is maintained locally in `.submission_identity.json` and local `submission/` PDF/DMN deliverables (excluded from public Git via `.gitignore`).

### 3.2 Potential Conflicts Between Documents & Resolutions

| Conflict ID | Source A | Source B | Nature of Conflict | Resolution Adopted |
|---|---|---|---|---|
| **CONF-01** | `AI102_Homework-02...pdf` (Sec. 6: "with all members' names and NIMs on the cover") | `ACADEMIC_REPORT_STYLE_GUIDE.md` (Sec. 3: "Do not create an unnecessary standalone cover page"; Sec. 7: Assignment instructions take Priority 1) | Standalone cover page vs. compact academic opening on Page 1. | Use a **compact academic title & metadata header block on Page 1** that displays Course, Assignment, Selected Scenario, Group Names & NIMs (populated locally from `.submission_identity.json`), Lecturer, Semester, and University directly on Page 1 without wasting a standalone title page. Main text spans Pages 1–3; Appendices begin cleanly on Page 4. |
| **CONF-02** | `AI102_Homework-02...pdf` (Task 2.4: "at least 3 representative end-to-end cases") | Master Execution Prompt (Phase 5: "at least four representative end-to-end scenarios" + edge cases) | Minimum case count (3 vs. 4+). | Adopt the stricter requirement: engineer and validate **8 comprehensive end-to-end test cases** (Cases 01–04 covering Normal Acceptance, Borderline, High-Risk/Refer, and Decline, plus Cases 05–08 covering Missing Claims History, Inspection Value Threshold Boundary, Claims Recency 24-Month Boundary, and Engine Capacity Boundary). Present the 4 primary traces in the main text (or full summary) and all 8 complete traces in the Appendix. |
| **CONF-03** | `ACADEMIC_REPORT_STYLE_GUIDE.md` (mentions `AI104_HW03_Threat_Analysis_Report.pdf`, i.e. `Example-1.pdf` in Indonesian) | `AI102_Homework-02...pdf` (written in English; `Example-2.pdf` in English) | Report language (Indonesian vs. English). | Use **English** throughout the report, matching the assignment specification and `Example-2.pdf`. |
| **CONF-04** | `AI102_Homework-02...pdf` (Sec. 5 recommends desktop Camunda Modeler) | Local Windows environment check (Camunda Modeler desktop binary is not installed; `dmn-js@18.1.0`, `dmn-moddle@12.2.1`, and `feelin@8.2.2` are available via Node.js + Edge) | Local availability of desktop Camunda Modeler vs. `dmn-js` / `feelin` engine. | Validate DMN 1.3 XML using `dmn-moddle@12.2.1` + `lxml` + `defusedxml`, visually open/render the `.dmn` DRD in `dmn-js@18.1.0` (the exact library powering Camunda Modeler's DMN editor) via headless Microsoft Edge, and execute FEEL/decision logic via `feelin@8.2.2` (Camunda's official JS FEEL engine). Document this transparently without claiming desktop Camunda Modeler was executed locally. |
| **CONF-05** | `AI102_Homework-02...pdf` (Task 4.2 & Sec. 5 cite `http://www.omg.org/spec/DMN/20191111/MODEL/`) | OMG DMN 1.3 normative XSD & `dmn-moddle@12.2.1` (`https://www.omg.org/spec/DMN/20191111/MODEL/`) | `http://` vs `https://` scheme in DMN 1.3 namespace URI. | Empirical test in `dmn-moddle@12.2.1` proved `http://` fails to parse (`failed to parse document as <dmn:Definitions>`), whereas `https://www.omg.org/spec/DMN/20191111/MODEL/` parses with 0 errors/warnings. Use the normative `https://` URI so the `.dmn` file opens cleanly in Camunda Modeler and `dmn-js`, and document this verification explicitly. |
