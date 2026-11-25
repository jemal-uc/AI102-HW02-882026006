# End-to-End Case Tracing — Scenario B (`AsuransiNusantara`)

All 10 representative and edge test cases below were independently computed from `src/specification/CANONICAL_DECISION_SPECIFICATION.json` and executed directly against `src/decision-model/AsuransiNusantara.dmn` using `dmn-moddle@12.2.1` + `feelin@8.2.2`. **Result: 10 / 10 PASS (zero mismatches).** *(Extended 18-case audit results are in `tests/test-results/INDEPENDENT_EXECUTION_RESULTS.json`.)*

---

## Summary Matrix

| Case | Category | Key Inputs (`evalDate = 2026-11-25`) | `D01` | `D02` | `D03` | `D04` | `D05` | `D06` | `D07` (IDR) | `D08` | `D09` (IDR) | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `TC-01` | Normal Acceptance | DOB `1990-05-15` (36y), Car 1496cc, Std, Comp, Rp250M, 1 old claim `2023-01-10` | `LOW` | `LOW` | `ELIGIBLE` | `LOW` | `ACCEPT` | `NOT_REQUIRED` | 4,500,000 | 0% | **4,500,000** | PASS |
| `TC-02` | Borderline Thresholds | DOB `2001-11-26` (24y), MC 250cc, Std, Comp, Rp40M, Veh `2011-11-25` (15y) | `HIGH` | `LOW` | `ELIGIBLE` | `MEDIUM` | `ACCEPT` | `REQUIRED` | 1,000,000 | +35% | **1,350,000** | PASS |
| `TC-03` | High Risk (Refer) | DOB `2004-06-10` (22y), MC 600cc, HighPerf, Comp, Rp350M, 1 recent claim | `HIGH` | `MEDIUM` | `ELIGIBLE` | `HIGH` | `REFER` | `NOT_REQUIRED` | 11,200,000 | +95% | **21,840,000** | PASS |
| `TC-04` | Decline (Vehicle Age) | DOB `1985-08-20` (41y), Car 1500cc, Std, TPO, Rp80M, Veh `2010-11-25` (16y) | `LOW` | `LOW` | `INELIGIBLE` | `MEDIUM` | `DECLINE` | `NOT_APPLICABLE` | 500,000 | +10% | **0** | PASS |
| `TC-05` | Missing Claims History | DOB `1988-02-10` (38y), `claimsHistoryAvailable=false`, Car 2000cc, TPO, Rp550M | `LOW` | `UNKNOWN` | `ELIGIBLE` | `MEDIUM` | `REFER` | `REQUIRED` | 2,750,000 | +35% | **3,712,500** | PASS |
| `TC-06` | Inspection Value Boundary | DOB `1992-07-01` (34y), Car 2500cc, Sport, Comp, Rp500M (`= threshold`) | `LOW` | `LOW` | `ELIGIBLE` | `MEDIUM` | `ACCEPT` | `REQUIRED` | 11,000,000 | +25% | **13,750,000** | PASS |
| `TC-07` | 24M Recency & Senior | DOB `1959-10-01` (67y), claims `["2024-11-25","2024-11-24"]`, MC 150cc, TPO, Rp25M | `MEDIUM` | `MEDIUM` | `ELIGIBLE` | `LOW` | `ACCEPT` | `NOT_REQUIRED` | 150,000 | +30% | **195,000** | PASS |
| `TC-08` | Decline (Compound Risk) | DOB `2005-01-10` (21y), 2 recent claims, MC 251cc, Sport, Comp, Rp120M | `HIGH` | `HIGH` | `ELIGIBLE` | `HIGH` | `DECLINE` | `NOT_APPLICABLE` | 3,840,000 | +100% | **0** | PASS |
| `TC-09` | Decline (Underage) | DOB `2010-03-01` (16y `< 17`), MC 125cc, Std, TPO, Rp20M | `INELIGIBLE` | `LOW` | `ELIGIBLE` | `LOW` | `DECLINE` | `NOT_APPLICABLE` | 150,000 | 0% | **0** | PASS |
| `TC-10` | Missing DOB (Null) | `dateOfBirth=null`, Car 1500cc, Std, Comp, Rp200M | `UNKNOWN` | `LOW` | `ELIGIBLE` | `LOW` | `REFER` | `NOT_REQUIRED` | 3,600,000 | 0% | **3,600,000** | PASS |

---

## Detailed Node-by-Node Trace Tables

### TC-01 — Normal Acceptance (Prime Adult Standard Car)
- **Inputs:** `dateOfBirth="1990-05-15"`, `evaluationDate="2026-11-25"`, `claimsHistoryAvailable=true`, `claimDates=["2023-01-10"]`, `vehicleManufactureDate="2022-03-01"`, `vehicleType="CAR"`, `engineCC=1496`, `performanceClass="STANDARD"`, `coverType="COMPREHENSIVE"`, `insuredValue=250000000`.
- **Intermediate BKMs:** `driverAge = 36`, `recentClaims = 0` (`2023-01-10 < 2024-11-25`), `vehicleAge = 4`.

| Node | Inputs Evaluated | Matched Rule(s) | Output |
|---|---|---|---|
| `D01` | `driverAge = 36` | `R-D01-05` (`[25..65]`) | `"LOW"` |
| `D02` | `avail = true`, `recent = 0` | `R-D02-03` | `"LOW"` |
| `D03` | `"CAR"`, `4`, `1496`, `250000000` | `R-D03-07` | `"ELIGIBLE"` |
| `D04` | `"CAR"`, `1496`, `"STANDARD"`, `4` | `R-D04-09` | `"LOW"` |
| `D05` | `"LOW"`, `"LOW"`, `"ELIGIBLE"`, `"LOW"` | `R-D05-09` | `"ACCEPT"` |
| `D06` | `"ACCEPT"`, `250000000`, `"COMPREHENSIVE"`, `4` | `R-D06-04` | `"NOT_REQUIRED"` |
| `D07` | `"CAR"`, `1496`, `"COMPREHENSIVE"` | `R-D07-08` | `4500000` |
| `D08` | `"LOW"`, `"LOW"`, `"LOW"`, `"STANDARD"` | `R-D08-03, R-D08-07, R-D08-10, R-D08-13` | `0` (`0%`) |
| `D09` | `"ACCEPT"` (`4500000 * 1.00`) | `R-D09-02` | `4500000` |

### TC-02 — Borderline Thresholds (Age 24, Vehicle Age 15, 250cc Motorcycle)
- **Inputs:** `dateOfBirth="2001-11-26"` (1 day before 25th birthday), `evaluationDate="2026-11-25"`, `claimsHistoryAvailable=true`, `claimDates=[]`, `vehicleManufactureDate="2011-11-25"` (exact 15y), `vehicleType="MOTORCYCLE"`, `engineCC=250`, `performanceClass="STANDARD"`, `coverType="COMPREHENSIVE"`, `insuredValue=40000000`.
- **Intermediate BKMs:** `driverAge = 24`, `recentClaims = 0`, `vehicleAge = 15`.

| Node | Inputs Evaluated | Matched Rule(s) | Output |
|---|---|---|---|
| `D01` | `driverAge = 24` | `R-D01-04` (`[17..24]`) | `"HIGH"` |
| `D02` | `avail = true`, `recent = 0` | `R-D02-03` | `"LOW"` |
| `D03` | `"MOTORCYCLE"`, `15`, `250`, `40000000` | `R-D03-07` (`[0..15]`) | `"ELIGIBLE"` |
| `D04` | `"MOTORCYCLE"`, `250`, `"STANDARD"`, `15` | `R-D04-05` (`(150..250]`) | `"MEDIUM"` |
| `D05` | `"HIGH"`, `"LOW"`, `"ELIGIBLE"`, `"MEDIUM"` | `R-D05-09` | `"ACCEPT"` |
| `D06` | `"ACCEPT"`, `40000000`, `"COMPREHENSIVE"`, `15` | `R-D06-03` (`> 10` Comp) | `"REQUIRED"` |
| `D07` | `"MOTORCYCLE"`, `250`, `"COMPREHENSIVE"` | `R-D07-04` | `1000000` |
| `D08` | `"HIGH"`, `"LOW"`, `"MEDIUM"`, `"STANDARD"` | `R-D08-01(+0.25), R-D08-07(0), R-D08-08(+0.10), R-D08-13(0)` | `0.35` (`+35%`) |
| `D09` | `"ACCEPT"` (`1000000 * 1.35`) | `R-D09-02` | `1350000` |

### TC-03 — High-Risk Referral (Young Driver + 1 Recent Claim + 600cc High-Performance Motorcycle)
- **Inputs:** `dateOfBirth="2004-06-10"`, `evaluationDate="2026-11-25"`, `claimsHistoryAvailable=true`, `claimDates=["2026-03-15"]`, `vehicleManufactureDate="2024-01-15"`, `vehicleType="MOTORCYCLE"`, `engineCC=600`, `performanceClass="HIGH_PERFORMANCE"`, `coverType="COMPREHENSIVE"`, `insuredValue=350000000`.
- **Intermediate BKMs:** `driverAge = 22`, `recentClaims = 1`, `vehicleAge = 2`.

| Node | Inputs Evaluated | Matched Rule(s) | Output |
|---|---|---|---|
| `D01` | `driverAge = 22` | `R-D01-04` | `"HIGH"` |
| `D02` | `avail = true`, `recent = 1` | `R-D02-04` | `"MEDIUM"` |
| `D03` | `"MOTORCYCLE"`, `2`, `600`, `350000000` | `R-D03-07` | `"ELIGIBLE"` |
| `D04` | `"MOTORCYCLE"`, `600`, `"HIGH_PERFORMANCE"`, `2` | `R-D04-01` | `"HIGH"` |
| `D05` | `"HIGH"`, `"MEDIUM"`, `"ELIGIBLE"`, `"HIGH"` | `R-D05-07` (first match of `REFER`) | `"REFER"` |
| `D06` | `"REFER"`, `350000000`, `"COMPREHENSIVE"`, `2` | `R-D06-04` | `"NOT_REQUIRED"` |
| `D07` | `"MOTORCYCLE"`, `600`, `"COMPREHENSIVE"` | `R-D07-06` | `11200000` |
| `D08` | `"HIGH"`, `"MEDIUM"`, `"HIGH"`, `"HIGH_PERFORMANCE"` | `R-D08-01(+0.25), R-D08-04(+0.20), R-D08-09(+0.20), R-D08-12(+0.30)` | `0.95` (`+95%`) |
| `D09` | `"REFER"` (`11200000 * 1.95`) | `R-D09-03` | `21840000` |

### TC-04 — Decline (Very Old Vehicle > 15 Years)
- **Inputs:** `dateOfBirth="1985-08-20"`, `evaluationDate="2026-11-25"`, `claimsHistoryAvailable=true`, `claimDates=[]`, `vehicleManufactureDate="2010-11-25"` (16y), `vehicleType="CAR"`, `engineCC=1500`, `performanceClass="STANDARD"`, `coverType="TPO"`, `insuredValue=80000000`.
- **Intermediate BKMs:** `driverAge = 41`, `recentClaims = 0`, `vehicleAge = 16`.

| Node | Inputs Evaluated | Matched Rule(s) | Output |
|---|---|---|---|
| `D01` | `driverAge = 41` | `R-D01-05` | `"LOW"` |
| `D02` | `avail = true`, `recent = 0` | `R-D02-03` | `"LOW"` |
| `D03` | `"CAR"`, `16`, `1500`, `80000000` | `R-D03-04` (`> 15`) | `"INELIGIBLE"` |
| `D04` | `"CAR"`, `1500`, `"STANDARD"`, `16` | `R-D04-08` (`> 10`) | `"MEDIUM"` |
| `D05` | `"LOW"`, `"LOW"`, `"INELIGIBLE"`, `"MEDIUM"` | `R-D05-01` | `"DECLINE"` |
| `D06` | `"DECLINE"`, `80000000`, `"TPO"`, `16` | `R-D06-01` | `"NOT_APPLICABLE"` |
| `D07` | `"CAR"`, `1500`, `"TPO"` | `R-D07-07` (`max(500k, 320k)`) | `500000` |
| `D08` | `"LOW"`, `"LOW"`, `"MEDIUM"`, `"STANDARD"` | `R-D08-03, R-D08-07, R-D08-08(+0.10), R-D08-13` | `0.1` (`+10%`) |
| `D09` | `"DECLINE"` | `R-D09-01` | `0` |

### TC-05 to TC-10 — Edge & Boundary Traces

| Case | `D01` (Rule) | `D02` (Rule) | `D03` (Rule) | `D04` (Rule) | `D05` (Rule) | `D06` (Rule) | `D07` (Rule) | `D08` (Rules) | `D09` (Rule) |
|---|---|---|---|---|---|---|---|---|---|
| `TC-05` | `LOW` (`R-D01-05`) | `UNKNOWN` (`R-D02-01`) | `ELIGIBLE` (`R-D03-07`) | `MEDIUM` (`R-D04-06`) | `REFER` (`R-D05-05`) | `REQUIRED` (`R-D06-02`) | `2750000` (`R-D07-09`) | `0.35` (`03,06,08,13`) | `3712500` (`R-D09-03`) |
| `TC-06` | `LOW` (`R-D01-05`) | `LOW` (`R-D02-03`) | `ELIGIBLE` (`R-D03-07`) | `MEDIUM` (`R-D04-06`) | `ACCEPT` (`R-D05-09`) | `REQUIRED` (`R-D06-02`) | `11000000` (`R-D07-10`) | `0.25` (`03,07,08,11`) | `13750000` (`R-D09-02`) |
| `TC-07` | `MEDIUM` (`R-D01-06`) | `MEDIUM` (`R-D02-04`) | `ELIGIBLE` (`R-D03-07`) | `LOW` (`R-D04-09`) | `ACCEPT` (`R-D05-09`) | `NOT_REQUIRED` (`R-D06-04`) | `150000` (`R-D07-01`) | `0.30` (`02,04,10,13`) | `195000` (`R-D09-02`) |
| `TC-08` | `HIGH` (`R-D01-04`) | `HIGH` (`R-D02-05`) | `ELIGIBLE` (`R-D03-07`) | `HIGH` (`R-D04-02`) | `DECLINE` (`R-D05-03`) | `NOT_APPLICABLE` (`R-D06-01`) | `3840000` (`R-D07-06`) | `1.00` (`01,05,09,11`) | `0` (`R-D09-01`) |
| `TC-09` | `INELIGIBLE` (`R-D01-03`) | `LOW` (`R-D02-03`) | `ELIGIBLE` (`R-D03-07`) | `LOW` (`R-D04-09`) | `DECLINE` (`R-D05-02`) | `NOT_APPLICABLE` (`R-D06-01`) | `150000` (`R-D07-01`) | `0.00` (`03,07,10,13`) | `0` (`R-D09-01`) |
| `TC-10` | `UNKNOWN` (`R-D01-01`) | `LOW` (`R-D02-03`) | `ELIGIBLE` (`R-D03-07`) | `LOW` (`R-D04-09`) | `REFER` (`R-D05-04`) | `NOT_REQUIRED` (`R-D06-04`) | `3600000` (`R-D07-08`) | `0.00` (`03,07,10,13`) | `3600000` (`R-D09-03`) |
