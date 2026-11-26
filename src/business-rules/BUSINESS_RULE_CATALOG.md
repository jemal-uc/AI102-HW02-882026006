# Business Rule Catalog — Scenario B (`AsuransiNusantara`)

**Authoritative Logic Inventory (`AsuransiNusantara.dmn` v1.1):**  
- **Decision Table Rules:** **`94`** rules across **10 decision tables** (`D01`–`D10`)  
- **BKM FEEL Functions:** **`2`** (`BKM01`, `BKM02`)  
- **Other Decision Logic Units:** `0` (`10` decision tables + `2` BKM literal FEEL expressions = `12` logic elements total)

---

## 1. Per-Decision XML Rule Count Reconciliation (`D01`–`D10`)

| Decision ID | Decision Name | Logic Type & Hit Policy | Stage 1 Baseline | Stage 2 Hardening | XML Rule Count (Current) | Source Traceability |
|---|---|---|---:|---:|---:|---|
| `D01` | Driver Risk Assessment | Decision Table (`UNIQUE`) | 5 | 6 | **6** | `AMB-01`, `KS03`, `BR-02` |
| `D02` | Claims Risk Assessment | Decision Table (`FIRST`) | 5 | 5 | **5** | `AMB-02`, `AMB-03`, `BR-03` |
| `D03` | Vehicle Eligibility Assessment | Decision Table (`FIRST`) | 7 | 7 | **7** | `AMB-04`, `AMB-11`, `BR-01`, `BR-04` |
| `D04` | Vehicle Risk Assessment | Decision Table (`FIRST`) | 10 | 14 | **14** | `AMB-06`, `AMB-07`, `BR-05` |
| `D05` | Underwriting Decision | Decision Table (`FIRST`) | 10 | 10 | **10** | `AMB-10`, `BR-06` |
| `D06` | Inspection Decision | Decision Table (`FIRST`) | 6 | 6 | **6** | `AMB-05`, `BR-07` |
| `D07` | Base Premium Calculation | Decision Table (`FIRST`) | 13 | 14 | **14** | `AMB-07`, `AMB-08`, `AMB-12`, `BR-08` |
| `D08` | Risk Loading Calculation | Decision Table (`COLLECT SUM`) | 14 | 14 | **14** | `AMB-09`, `BR-09` |
| `D09` | Final Premium Calculation | Decision Table (`FIRST`) | 3 (`UNIQUE`) | 3 (`UNIQUE`) | **6** | `AMB-09`, `AMB-10`, `AMB-12`, `BR-11` |
| `D10` | Quote Readiness Assessment | Decision Table (`FIRST`) | 0 *(N/A)* | 0 *(N/A)* | **12** | `AMB-12`, `BR-10` |
| **Sum** | **10 Decision Tables (`D01`–`D10`)** | — | **73** | **79** | **94** | **100% verified against `.dmn` XML** |

*Plus **2 BKM Literal FEEL Functions** (`BKM01: calculateAgeInYears`, `BKM02: countRecentClaims`), bringing total modeled logic units to `10` decision tables (`94` rules) + `2` BKM functions.*

---

## 2. Source of Historical Discrepancy (`73` vs `79` vs `94`)

1. **Stage 1 (`73` table rules):** Initial implementation had `5` rules in `D01` (lumping `< 0` and `[0..17)` as `< 17`), `10` rules in `D04` (`R-D04-01..10`), and `13` rules in `D07` (`R-D07-01..13` without an `insuredValue` guard row).
2. **Stage 2 (`79` table rules, `+6` defensive guards):** Independent audit added `+1` explicit future-DOB rule in `D01` (`R-D01-02: < 0`), `+4` conservative missing/invalid input guards in `D04` (`R-D04-00a..00d`), and `+1` `insuredValue` guard in `D07` (`R-D07-00`). Stale text in `VALIDATION_REPORT.md` temporarily retained `73` after the XML grew to `79`.
3. **Stage 5 (`94` table rules, `+15` safety/readiness rules):** Added `D10: Quote Readiness Assessment` (**`+12` rules**) and expanded `D09: Final Premium Calculation` from `3` (`UNIQUE`) to **`6` rules** (`FIRST`, adding `REFER`, non-`READY`, and `basePremium <= 0 / null` guards). In numerical ID order (`D01`–`D10`), counts are `6 + 5 + 7 + 14 + 10 + 6 + 14 + 14 + 6 + 12 = 94`.
