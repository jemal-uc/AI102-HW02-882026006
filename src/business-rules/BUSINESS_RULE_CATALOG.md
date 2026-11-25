# Business Rule Catalog — Scenario B (`AsuransiNusantara`)

Total rules across `D01`–`D09`: **79 decision table rules** + **2 BKM FEEL functions** (`BKM01`, `BKM02`).

| Rule Range | Decision Node | Hit Policy | Rule Count | Source Traceability |
|---|---|---|---|---|
| `R-BKM01-01` | `BKM01: calculateAgeInYears` | Literal FEEL Function | 1 | `AMB-01`, `AMB-04`, `BR-02`, `BR-04` |
| `R-BKM02-01` | `BKM02: countRecentClaims` | Literal FEEL Function | 1 | `AMB-02`, `AMB-03`, `BR-03` |
| `R-D01-01` .. `R-D01-06` | `D01: Driver Risk Assessment` | `UNIQUE` | 6 | `AMB-01`, `KS03`, `BR-02` |
| `R-D02-01` .. `R-D02-05` | `D02: Claims Risk Assessment` | `FIRST` | 5 | `AMB-02`, `AMB-03`, `BR-03` |
| `R-D03-01` .. `R-D03-07` | `D03: Vehicle Eligibility Assessment` | `FIRST` | 7 | `AMB-04`, `AMB-11`, `BR-01`, `BR-04` |
| `R-D04-00a` .. `R-D04-10` | `D04: Vehicle Risk Assessment` | `FIRST` | 14 | `AMB-06`, `AMB-07`, `BR-05` |
| `R-D05-01` .. `R-D05-10` | `D05: Underwriting Decision` | `FIRST` | 10 | `AMB-10`, `BR-06` |
| `R-D06-01` .. `R-D06-06` | `D06: Inspection Decision` | `FIRST` | 6 | `AMB-05`, `BR-07` |
| `R-D07-00` .. `R-D07-13` | `D07: Base Premium Calculation` | `FIRST` | 14 | `AMB-07`, `AMB-08`, `BR-08` |
| `R-D08-01` .. `R-D08-14` | `D08: Risk Loading Calculation` | `COLLECT (SUM)` | 14 | `AMB-09`, `BR-09` |
| `R-D09-01` .. `R-D09-03` | `D09: Final Premium Calculation` | `UNIQUE` | 3 | `AMB-09`, `AMB-10`, `BR-10` |
| **Total** | **2 BKMs + 9 Decisions** | — | **79 table rules + 2 BKM functions** | **100% mapped** |
