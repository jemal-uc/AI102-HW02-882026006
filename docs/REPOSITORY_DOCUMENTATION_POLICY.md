# Repository Documentation Policy — AI102 Homework-02

This repository separates public DMN engineering artifacts from local-only academic submission deliverables and internal development history.

---

## 1. Document Classification

1. **Source Documentation (`src/`, `README.md`):** Canonical decision specification (`CANONICAL_DECISION_SPECIFICATION.json`), sanitized DMN 1.3 model (`AsuransiNusantara.dmn`), requirements, ambiguity register, data dictionary, decision tables, FEEL catalog, and DRD architecture. Tracked in Git.
2. **Technical Validation Evidence (`tests/`, `outputs/diagrams/`):** Reproducible test cases, machine-readable JSON results (`TEST_RESULTS.json`, `INDEPENDENT_EXECUTION_RESULTS.json`), official OMG `DMN13.xsd` schemas, `dmn-js` render proof (`dmnjs_drd_verify.png`), `VALIDATION_REPORT.md`, and the consolidated `VALIDATION_SUMMARY.md`. Tracked in Git.
3. **Private Academic Materials (Gitignored, Local Only):** Original lecturer assignment brief, `ACADEMIC-REPORT-STANDARD/`, `.submission_identity.json`, `src/decision-model/AI102-HW02-*.dmn`, `reports/final-report/` (containing the academic PDF with author identities and truthful AI-assistance disclosure), `outputs/generated-artifacts/`, and `submission/` (`.dmn`, `.pdf`, `_Submission.zip`). Preserved locally for grading and excluded from public Git.
4. **Internal Development History (Archived Outside Repo):** Stage-by-stage AI-agent workflow logs, refactoring manifests, defect tracking logs, and pre-cleanup checklists were moved out of the workspace to a local external archive (`_LOCAL_ARCHIVES/Homework-02-Audit-History/`) so the public repository remains focused on engineering artifacts rather than process logs.

---

## 2. Stage 4.2 Artifact Minimization Record

- **Archived Outside Repository (`15` files from removed `reports/audit/`):**
  `DEFECT_REGISTER.md`, `EXECUTION_METHOD_AUDIT.md`, `FINAL_AUDIT.md`, `GITHUB_READINESS_CHECKLIST.md`, `GROUP_IDENTITY_CORRECTION_REPORT.md`, `INDEPENDENT_AUDIT_REPORT.md`, `PREMIUM_RECALCULATION.md`, `RELEASE_GATE.json`, `REPOSITORY_CLEANUP_BASELINE.md`, `REPOSITORY_CLEANUP_MANIFEST.md`, `REPOSITORY_CLEANUP_REPORT.md`, `REPOSITORY_FILE_CLASSIFICATION.csv`, `SECURITY_AND_PRIVACY_AUDIT.md`, `WORKSPACE_REFACTORING_MANIFEST.md`, `XSD_VALIDATION_RESULTS.md`.
- **Added (`2` files):** `tests/validation-evidence/VALIDATION_SUMMARY.md` (consolidated technical evidence) and `docs/REPOSITORY_DOCUMENTATION_POLICY.md` (this policy).
- **Retained & Excluded:** All source, test, script, and diagram files remain tracked; all private academic/submission files remain preserved locally and excluded via `.gitignore`.
