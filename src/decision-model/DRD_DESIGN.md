# Decision Requirements Diagram (DRD) Design — Scenario B

**DMN Standard:** OMG DMN 1.3 (`http://www.omg.org/spec/DMN/20191111/MODEL/`)  
**Graph Topology:** 4-Tier Directed Acyclic Graph (DAG) — 10 Input Data nodes, 2 BKMs, 3 Knowledge Sources, 9 Decisions.

---

## 1. DMN Element Inventory & Node Coordinates (DMNDI Layout)

| Element ID | DMN Type | Label | Coordinates (`x, y, w, h`) |
|---|---|---|---|
| `I01` | `inputData` | `dateOfBirth` | `(60, 620, 135, 45)` |
| `I02` | `inputData` | `evaluationDate` | `(230, 620, 135, 45)` |
| `I03` | `inputData` | `claimsHistoryAvailable` | `(400, 620, 155, 45)` |
| `I04` | `inputData` | `claimDates` | `(585, 620, 135, 45)` |
| `I05` | `inputData` | `vehicleManufactureDate` | `(750, 620, 165, 45)` |
| `I06` | `inputData` | `vehicleType` | `(945, 620, 135, 45)` |
| `I07` | `inputData` | `engineCC` | `(1110, 620, 135, 45)` |
| `I08` | `inputData` | `performanceClass` | `(1275, 620, 145, 45)` |
| `I09` | `inputData` | `coverType` | `(1450, 620, 135, 45)` |
| `I10` | `inputData` | `insuredValue` | `(1615, 620, 135, 45)` |
| `BKM01` | `businessKnowledgeModel` | `calculateAgeInYears` | `(430, 490, 170, 50)` |
| `BKM02` | `businessKnowledgeModel` | `countRecentClaims` | `(650, 490, 170, 50)` |
| `KS01` | `knowledgeSource` | `Underwriting Policy (Educational)` | `(60, 220, 170, 60)` |
| `KS02` | `knowledgeSource` | `Motor Tariff & Loading Schedule` | `(1580, 220, 170, 60)` |
| `KS03` | `knowledgeSource` | `UU No. 22/2009 (Min SIM Age 17)` | `(60, 380, 170, 60)` |
| `D01` | `decision` | `D01: Driver Risk Assessment` | `(160, 370, 180, 65)` |
| `D02` | `decision` | `D02: Claims Risk Assessment` | `(440, 370, 180, 65)` |
| `D03` | `decision` | `D03: Vehicle Eligibility Assessment` | `(730, 370, 190, 65)` |
| `D04` | `decision` | `D04: Vehicle Risk Assessment` | `(1030, 370, 180, 65)` |
| `D05` | `decision` | `D05: Underwriting Decision` | `(520, 220, 190, 65)` |
| `D06` | `decision` | `D06: Inspection Decision` | `(850, 80, 190, 65)` |
| `D07` | `decision` | `D07: Base Premium Calculation` | `(1330, 370, 190, 65)` |
| `D08` | `decision` | `D08: Risk Loading Calculation` | `(1240, 220, 190, 65)` |
| `D09` | `decision` | `D09: Final Premium Calculation` | `(1140, 80, 190, 65)` |

---

## 2. Typed Dependency Specification

### 2.1 Information Requirements (`inputData -> decision` and `decision -> decision`)

| Target Decision | Required Inputs / Decisions | Business Justification |
|---|---|---|
| `D01` | `I01 (dateOfBirth)`, `I02 (evaluationDate)` | Driver age is computed deterministically between birth date and evaluation date. |
| `D02` | `I02 (evaluationDate)`, `I03 (claimsHistoryAvailable)`, `I04 (claimDates)` | Claims risk checks history availability and counts claims inside the 24M window ending at `evaluationDate`. |
| `D03` | `I02 (evaluationDate)`, `I05 (vehicleManufactureDate)`, `I06 (vehicleType)`, `I07 (engineCC)`, `I10 (insuredValue)` | Eligibility verifies supported vehicle type, `<= 15` year age limit, and positive engine displacement and insured value. |
| `D04` | `I02 (evaluationDate)`, `I05 (vehicleManufactureDate)`, `I06 (vehicleType)`, `I07 (engineCC)`, `I08 (performanceClass)` | Vehicle technical risk evaluates motorcycle/car displacement tiers, performance class, and vehicle aging (`>10` years). |
| `D05` | `D01`, `D02`, `D03`, `D04` | Underwriting disposition aggregates driver, claims, eligibility, and vehicle risk under strict `DECLINE > REFER > ACCEPT` precedence. |
| `D06` | `D05`, `I02 (evaluationDate)`, `I05 (vehicleManufactureDate)`, `I09 (coverType)`, `I10 (insuredValue)` | Inspection checks declined status first (`NOT_APPLICABLE`), then Rp500M threshold and older comprehensive policy rule. |
| `D07` | `I06 (vehicleType)`, `I07 (engineCC)`, `I09 (coverType)`, `I10 (insuredValue)` | Base tariff depends solely on vehicle category, engine capacity band, cover type, and sum insured. |
| `D08` | `D01`, `D02`, `D04`, `I08 (performanceClass)` | Additive loading sums driver, claims, vehicle technical, and performance class surcharges. |
| `D09` | `D05`, `D07`, `D08` | Final premium applies `Base * (1 + Loading)` for accepted/referred risks and `0` when declined. |

### 2.2 Knowledge Requirements (`BKM -> decision`)
- `BKM01 (calculateAgeInYears)` → `D01`, `D03`, `D04`, `D06`
- `BKM02 (countRecentClaims)` → `D02`

### 2.3 Authority Requirements (`knowledgeSource -> decision / BKM`)
- `KS01 (Underwriting Policy)` → `D01`, `D02`, `D03`, `D04`, `D05`, `D06`, `BKM01`, `BKM02`
- `KS02 (Tariff & Loading Schedule)` → `D07`, `D08`, `D09`
- `KS03 (UU No. 22/2009 — Min SIM Age 17)` → `D01`, `BKM01`

---

## 3. DAG & Structural Invariants Verification

- **Acyclicity:** Tier 0 (`Inputs`, `BKMs`, `KS`) → Tier 1 (`D01`, `D02`, `D03`, `D04`, `D07`) → Tier 2 (`D05`, `D08`) → Tier 3 (`D06`, `D09`). Strictly monotonic tier transitions guarantee zero cycles.
- **Minimum information requirement:** Every decision `D01`–`D09` receives between 2 and 5 information requirements (none has zero).
- **No direct bypass:** Pricing (`D09`) cannot execute independently of underwriting (`D05`), ensuring declined policies never receive a positive premium.
