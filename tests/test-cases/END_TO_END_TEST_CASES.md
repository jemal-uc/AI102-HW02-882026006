# End-to-End Case Tracing — Scenario B (`AsuransiNusantara`)

All **19 canonical & regression scenarios** (`TC-01`–`TC-10` original baseline updated for Stage 5 `null`-safe final premiums + `TC-11`–`TC-19` boundary/invalid-input regressions) were independently derived from business specifications and executed directly against `src/decision-model/AsuransiNusantara.dmn` using `dmn-moddle@12.2.1` + `feelin@8.2.2`. **Result: 19 / 19 PASS (zero mismatches).** *(Combined 27-case suite including preserved Stage 2 adversarial cases `TC-20`–`TC-27` is recorded in `tests/test-results/INDEPENDENT_EXECUTION_RESULTS.json` with `27 / 27 PASS`.)*

---

## Summary Matrix (`TC-01`–`TC-19`)

| Case | Category | Key Inputs (`evalDate = 2026-11-25`) | `D01` | `D02` | `D03` | `D04` | `D05` | `D06` | `D10` | `D07` (IDR) | `D08` | `D09` (IDR) | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `TC-01` | Normal Acceptance | DOB `1990-05-15` (36y), Car 1496cc, Std, Comp, Rp250M, 1 old claim | `LOW` | `LOW` | `ELIGIBLE` | `LOW` | `ACCEPT` | `NOT_REQUIRED` | `READY` | 4,500,000 | 0% | **4,500,000** | PASS |
| `TC-02` | Borderline Thresholds | DOB `2001-11-26` (24y), MC 250cc, Std, Comp, Rp40M, Veh 15y | `HIGH` | `LOW` | `ELIGIBLE` | `MEDIUM` | `ACCEPT` | `REQUIRED` | `READY` | 1,000,000 | +35% | **1,350,000** | PASS |
| `TC-03` | High Risk (Refer) | DOB `2004-06-10` (22y), MC 600cc, HighPerf, Comp, Rp350M, 1 claim | `HIGH` | `MEDIUM` | `ELIGIBLE` | `HIGH` | `REFER` | `NOT_REQUIRED` | `READY` | 11,200,000 | +95% | **`null`** *(Pending review)* | PASS |
| `TC-04` | Decline (Vehicle Age) | DOB `1985-08-20` (41y), Car 1500cc, Std, TPO, Rp80M, Veh 16y | `LOW` | `LOW` | `INELIGIBLE` | `MEDIUM` | `DECLINE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` | 500,000 | +10% | **`null`** *(Declined)* | PASS |
| `TC-05` | Missing Claims History | DOB `1988-02-10` (38y), `claimsHistoryAvailable=false`, Car 2000cc, TPO, Rp550M | `LOW` | `UNKNOWN` | `ELIGIBLE` | `MEDIUM` | `REFER` | `REQUIRED` | `READY` | 2,750,000 | +35% | **`null`** *(Pending review)* | PASS |
| `TC-06` | Inspection Value Boundary | DOB `1992-07-01` (34y), Car 2500cc, Sport, Comp, Rp500M | `LOW` | `LOW` | `ELIGIBLE` | `MEDIUM` | `ACCEPT` | `REQUIRED` | `READY` | 11,000,000 | +25% | **13,750,000** | PASS |
| `TC-07` | 24M Recency & Senior | DOB `1959-10-01` (67y), claims `["2024-11-25","2024-11-24"]`, MC 150cc, TPO, Rp25M | `MEDIUM` | `MEDIUM` | `ELIGIBLE` | `LOW` | `ACCEPT` | `NOT_REQUIRED` | `READY` | 150,000 | +30% | **195,000** | PASS |
| `TC-08` | Decline (Compound Risk) | DOB `2005-01-10` (21y), 2 recent claims, MC 251cc, Sport, Comp, Rp120M | `HIGH` | `HIGH` | `ELIGIBLE` | `HIGH` | `DECLINE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` | 3,840,000 | +100% | **`null`** *(Declined)* | PASS |
| `TC-09` | Decline (Underage) | DOB `2010-03-01` (16y `< 17`), MC 125cc, Std, TPO, Rp20M | `INELIGIBLE` | `LOW` | `ELIGIBLE` | `LOW` | `DECLINE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` | 150,000 | 0% | **`null`** *(Declined)* | PASS |
| `TC-10` | Missing DOB (Null) | `dateOfBirth=null`, Car 1500cc, Std, Comp, Rp200M | `UNKNOWN` | `LOW` | `ELIGIBLE` | `LOW` | `REFER` | `NOT_REQUIRED` | `READY` | 3,600,000 | 0% | **`null`** *(Pending review)* | PASS |
| `TC-11` | Missing Cover Type (`null`) | Prime Car 1496cc, Std, `coverType=null`, Rp250M | `LOW` | `LOW` | `ELIGIBLE` | `LOW` | `ACCEPT` | `REQUIRED` | `PENDING_INFORMATION` | **`null`** | 0% | **`null`** | PASS |
| `TC-12` | Unsupported Cover Type | Prime Car 1496cc, Std, `coverType="ALL_RISK_UNSUPPORTED"`, Rp250M | `LOW` | `LOW` | `ELIGIBLE` | `LOW` | `ACCEPT` | `REQUIRED` | `INVALID_INPUT` | **`null`** | 0% | **`null`** | PASS |
| `TC-13` | Empty Cover Type (`""`) | Prime Car 1496cc, Std, `coverType=""`, Rp250M | `LOW` | `LOW` | `ELIGIBLE` | `LOW` | `ACCEPT` | `REQUIRED` | `PENDING_INFORMATION` | **`null`** | 0% | **`null`** | PASS |
| `TC-14` | Valid Comprehensive | Prime Car 2000cc, Std, `coverType="COMPREHENSIVE"`, Rp300M | `LOW` | `LOW` | `ELIGIBLE` | `MEDIUM` | `ACCEPT` | `NOT_REQUIRED` | `READY` | 6,600,000 | +10% | **7,260,000** | PASS |
| `TC-15` | Valid Third-Party-Only | Prime Car 2000cc, Std, `coverType="THIRD_PARTY_ONLY"`, Rp300M | `LOW` | `LOW` | `ELIGIBLE` | `MEDIUM` | `ACCEPT` | `NOT_REQUIRED` | `READY` | 1,500,000 | +10% | **1,650,000** | PASS |
| `TC-16` | Missing Insured Value | Prime Car 1500cc, Std, Comp, `insuredValue=null` | `LOW` | `LOW` | `ELIGIBLE` | `LOW` | `ACCEPT` | `REQUIRED` | `PENDING_INFORMATION` | **`null`** | 0% | **`null`** | PASS |
| `TC-17` | Declined Application | DOB `2011-05-01` (15y), Car 1500cc, Std, Comp, Rp200M | `INELIGIBLE` | `LOW` | `ELIGIBLE` | `LOW` | `DECLINE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` | 3,600,000 | 0% | **`null`** | PASS |
| `TC-18` | Referred Application | DOB `1991-04-12` (35y), 2 recent claims, Car 1500cc, Comp, Rp200M | `LOW` | `HIGH` | `ELIGIBLE` | `LOW` | `REFER` | `NOT_REQUIRED` | `READY` | 3,600,000 | +40% | **`null`** | PASS |
| `TC-19` | Missing Insured Value (TPO) | Prime Car 1500cc, Std, `coverType="TPO"`, `insuredValue=null` | `LOW` | `LOW` | `ELIGIBLE` | `LOW` | `ACCEPT` | `REQUIRED` | `PENDING_INFORMATION` | **`null`** | 0% | **`null`** | PASS |

*(Stage 5 Semantic Update Note: For declined risks `TC-04`/`TC-08`/`TC-09` and unapproved referred risks `TC-03`/`TC-05`/`TC-10`, expected `finalPremium` was corrected from numeric `0`/auto-computed amounts to `null`, eliminating the unsafe `Rp0` fallback and unapproved-referral quotation defects while preserving `basePremium` and `totalRiskLoading` diagnostic visibility.)*

---

## Detailed Node-by-Node Trace Tables (`TC-01`–`TC-04` Primary & `TC-11`–`TC-18` Regressions)

### TC-01 — Normal Acceptance (Prime Adult Standard Car)
- **Inputs:** `dateOfBirth="1990-05-15"`, `evaluationDate="2026-11-25"`, `claimsHistoryAvailable=true`, `claimDates=["2023-01-10"]`, `vehicleManufactureDate="2022-03-01"`, `vehicleType="CAR"`, `engineCC=1496`, `performanceClass="STANDARD"`, `coverType="COMPREHENSIVE"`, `insuredValue=250000000`.
- **Intermediate BKMs:** `driverAge = 36`, `recentClaims = 0`, `vehicleAge = 4`.

| Node | Inputs Evaluated | Matched Rule(s) | Output |
|---|---|---|---|
| `D01` | `driverAge = 36` | `R-D01-05` | `"LOW"` |
| `D02` | `avail = true`, `recent = 0` | `R-D02-03` | `"LOW"` |
| `D03` | `"CAR"`, `4`, `1496`, `250000000` | `R-D03-07` | `"ELIGIBLE"` |
| `D04` | `"CAR"`, `1496`, `"STANDARD"`, `4` | `R-D04-09` | `"LOW"` |
| `D05` | `"LOW"`, `"LOW"`, `"ELIGIBLE"`, `"LOW"` | `R-D05-09` | `"ACCEPT"` |
| `D06` | `"ACCEPT"`, `250000000`, `"COMPREHENSIVE"`, `4` | `R-D06-04` | `"NOT_REQUIRED"` |
| `D07` | `"CAR"`, `1496`, `"COMPREHENSIVE"`, `250000000` | `R-D07-08` | `4500000` |
| `D08` | `"LOW"`, `"LOW"`, `"LOW"`, `"STANDARD"` | `R-D08-03, 07, 10, 13` | `0` (`0%`) |
| `D10` | `"ACCEPT"`, `"CAR"`, `1496`, `"COMPREHENSIVE"`, `250M`, `4.5M` | `R-D10-11` | `"READY"` |
| `D09` | `"ACCEPT"`, `"READY"`, `4500000` (`* 1.00`) | `R-D09-05` | `4500000` |

### TC-02 — Borderline Thresholds (Age 24, Vehicle Age 15, 250cc Motorcycle)
- **Intermediate BKMs:** `driverAge = 24`, `recentClaims = 0`, `vehicleAge = 15`.
- **Trace:** `D01="HIGH"` (`R-D01-04`), `D02="LOW"` (`R-D02-03`), `D03="ELIGIBLE"` (`R-D03-07`), `D04="MEDIUM"` (`R-D04-05`), `D05="ACCEPT"` (`R-D05-09`), `D06="REQUIRED"` (`R-D06-03`), `D07=1000000` (`R-D07-04`), `D08=0.35` (`R-D08-01,07,08,13`), `D10="READY"` (`R-D10-11`), `D09=1350000` (`R-D09-05`).

### TC-03 — High-Risk Referral (`REFER` Blocks Auto-Approved Quote)
- **Intermediate BKMs:** `driverAge = 22`, `recentClaims = 1`, `vehicleAge = 2`.
- **Trace:** `D01="HIGH"`, `D02="MEDIUM"`, `D03="ELIGIBLE"`, `D04="HIGH"`, `D05="REFER"` (`R-D05-07`), `D06="NOT_REQUIRED"` (`R-D06-04`), `D07=11200000` (`R-D07-06`), `D08=0.95`, `D10="READY"` (`R-D10-11`), `D09=null` (`R-D09-02`).

### TC-04 — Decline (Very Old Vehicle > 15 Years)
- **Intermediate BKMs:** `driverAge = 41`, `recentClaims = 0`, `vehicleAge = 16`.
- **Trace:** `D01="LOW"`, `D02="LOW"`, `D03="INELIGIBLE"` (`R-D03-04`), `D04="MEDIUM"` (`R-D04-08`), `D05="DECLINE"` (`R-D05-01`), `D06="NOT_APPLICABLE"` (`R-D06-01`), `D07=500000` (`R-D07-07`), `D08=0.1`, `D10="NOT_APPLICABLE"` (`R-D10-01`), `D09=null` (`R-D09-01`).

### TC-11 to TC-19 — Stage 5 / 5.1 Regression Traces (`D01`–`D10`)

| Case | `D01..D04` Summary | `D05` (Rule) | `D06` (Rule) | `D07` (Rule) | `D09` (Rule) | `D10` (Rule) |
|---|---|---|---|---|---|---|
| `TC-11` | `LOW/LOW/ELIGIBLE/LOW` | `ACCEPT` (`R-D05-09`) | `REQUIRED` (`R-D06-06`) | `null` (`R-D07-13`) | `null` (`R-D09-03`) | `PENDING_INFORMATION` (`R-D10-04`) |
| `TC-12` | `LOW/LOW/ELIGIBLE/LOW` | `ACCEPT` (`R-D05-09`) | `REQUIRED` (`R-D06-06`) | `null` (`R-D07-13`) | `null` (`R-D09-03`) | `INVALID_INPUT` (`R-D10-08`) |
| `TC-13` | `LOW/LOW/ELIGIBLE/LOW` | `ACCEPT` (`R-D05-09`) | `REQUIRED` (`R-D06-06`) | `null` (`R-D07-13`) | `null` (`R-D09-03`) | `PENDING_INFORMATION` (`R-D10-04`) |
| `TC-14` | `LOW/LOW/ELIGIBLE/MEDIUM` | `ACCEPT` (`R-D05-09`) | `NOT_REQUIRED` (`R-D06-04`) | `6600000` (`R-D07-10`) | `7260000` (`R-D09-05`) | `READY` (`R-D10-11`) |
| `TC-15` | `LOW/LOW/ELIGIBLE/MEDIUM` | `ACCEPT` (`R-D05-09`) | `NOT_REQUIRED` (`R-D06-04`) | `1500000` (`R-D07-09`) | `1650000` (`R-D09-05`) | `READY` (`R-D10-11`) |
| `TC-16` | `LOW/LOW/ELIGIBLE/LOW` | `ACCEPT` (`R-D05-09`) | `REQUIRED` (`R-D06-06`) | `null` (`R-D07-00`) | `null` (`R-D09-03`) | `PENDING_INFORMATION` (`R-D10-05`) |
| `TC-17` | `INELIGIBLE/LOW/ELIGIBLE/LOW` | `DECLINE` (`R-D05-02`) | `NOT_APPLICABLE` (`R-D06-01`) | `3600000` (`R-D07-08`) | `null` (`R-D09-01`) | `NOT_APPLICABLE` (`R-D10-01`) |
| `TC-18` | `LOW/HIGH/ELIGIBLE/LOW` | `REFER` (`R-D05-06`) | `NOT_REQUIRED` (`R-D06-04`) | `3600000` (`R-D07-08`) | `null` (`R-D09-02`) | `READY` (`R-D10-11`) |
| `TC-19` | `LOW/LOW/ELIGIBLE/LOW` | `ACCEPT` (`R-D05-09`) | `REQUIRED` (`R-D06-06`) | `null` (`R-D07-00`) | `null` (`R-D09-03`) | `PENDING_INFORMATION` (`R-D10-05`) |
