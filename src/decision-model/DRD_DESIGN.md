# Decision Requirements Diagram (DRD) Design — Scenario B

**DMN Standard:** OMG DMN 1.3 (`https://www.omg.org/spec/DMN/20191111/MODEL/`)  
**Graph Topology:** 5-Tier Directed Acyclic Graph (DAG) — 10 Input Data nodes, 2 BKMs, 3 Knowledge Sources, **10 Decisions (`D01`–`D10`)**.

---

## 1. DMN Element Inventory & Node Coordinates (DMNDI Layout)

| Element ID | DMN Type | Label | Coordinates (`x, y, w, h`) |
|---|---|---|---|
| `I01` | `inputData` | `dateOfBirth` | `(60, 650, 145, 45)` |
| `I02` | `inputData` | `evaluationDate` | `(230, 650, 145, 45)` |
| `I03` | `inputData` | `claimsHistoryAvailable` | `(400, 650, 165, 45)` |
| `I04` | `inputData` | `claimDates` | `(590, 650, 140, 45)` |
| `I05` | `inputData` | `vehicleManufactureDate` | `(755, 650, 175, 45)` |
| `I06` | `inputData` | `vehicleType` | `(955, 650, 140, 45)` |
| `I07` | `inputData` | `engineCC` | `(1120, 650, 140, 45)` |
| `I08` | `inputData` | `performanceClass` | `(1285, 650, 155, 45)` |
| `I09` | `inputData` | `coverType` | `(1465, 650, 140, 45)` |
| `I10` | `inputData` | `insuredValue` | `(1630, 650, 145, 45)` |
| `BKM01` | `businessKnowledgeModel` | `calculateAgeInYears` | `(390, 515, 185, 55)` |
| `BKM02` | `businessKnowledgeModel` | `countRecentClaims` | `(630, 515, 185, 55)` |
| `KS03` | `knowledgeSource` | `UU No. 22/2009 Pasal 81(2)(a) — Min SIM A/C Age 17` | `(40, 365, 175, 65)` |
| `KS01` | `knowledgeSource` | `AsuransiNusantara Underwriting Policy (Educational)` | `(40, 235, 175, 65)` |
| `KS02` | `knowledgeSource` | `Illustrative Motor Tariff & Loading Schedule (Not SEOJK 6/2017)` | `(1620, 235, 175, 65)` |
| `D01` | `decision` | `Driver Risk Assessment` | `(250, 365, 190, 68)` |
| `D02` | `decision` | `Claims Risk Assessment` | `(480, 365, 190, 68)` |
| `D03` | `decision` | `Vehicle Eligibility Assessment` | `(720, 365, 200, 68)` |
| `D04` | `decision` | `Vehicle Risk Assessment` | `(970, 365, 190, 68)` |
| `D07` | `decision` | `Base Premium Calculation` | `(1370, 365, 200, 68)` |
| `D05` | `decision` | `Underwriting Decision` | `(560, 235, 200, 68)` |
| `D08` | `decision` | `Risk Loading Calculation` | `(1190, 235, 200, 68)` |
| `D06` | `decision` | `Inspection Decision` | `(560, 120, 200, 68)` |
| `D10` | `decision` | `Quote Readiness Assessment` | `(1180, 120, 210, 68)` |
| `D09` | `decision` | `Final Premium Calculation` | `(1030, 15, 200, 68)` |

---

## 2. Typed Dependency Specification (`62` Edges Total)

### 2.1 Information Requirements (`42` edges: `inputData -> decision` and `decision -> decision`)

| Target Decision | Required Inputs / Decisions | Business Justification |
|---|---|---|
| `D01` | `I01 (dateOfBirth)`, `I02 (evaluationDate)` | Driver age computed deterministically between birth date and evaluation date. |
| `D02` | `I02`, `I03 (claimsHistoryAvailable)`, `I04 (claimDates)` | Verifies history availability and counts claims inside the 24M window ending at `evaluationDate`. |
| `D03` | `I02`, `I05`, `I06`, `I07`, `I10` | Enforces supported vehicle type, `<= 15` year age limit, positive `engineCC`, and non-invalid (`> 0` or `null`) valuation. |
| `D04` | `I02`, `I05`, `I06`, `I07`, `I08` | Grades vehicle technical risk across displacement bands, performance tier, and vehicle age (`> 10`). |
| `D05` | `D01`, `D02`, `D03`, `D04` | Determines `DECLINE > REFER > ACCEPT` risk disposition independently of `coverType`. |
| `D06` | `D05`, `I02`, `I05`, `I09`, `I10` | Checks `DECLINE -> NOT_APPLICABLE`, `>= Rp500M`, and older `COMPREHENSIVE` inspection triggers. |
| `D07` | `I06`, `I07`, `I09`, `I10` | Computes tariff base premium or `null` if pricing inputs are missing/invalid. |
| `D08` | `D01`, `D02`, `D04`, `I08` | Sums orthogonal additive risk surcharges via `COLLECT (SUM)`. |
| `D10` | `D05`, `I06`, `I07`, `I09`, `I10`, `D07` | Separately evaluates commercial/pricing readiness (`READY`, `PENDING_INFORMATION`, `INVALID_INPUT`, `NOT_APPLICABLE`). |
| `D09` | `D05`, `D10`, `D07`, `D08` | Produces approved final premium strictly when `D05 = ACCEPT`, `D10 = READY`, and `D07 > 0` (otherwise `null`). |

### 2.2 Knowledge Requirements (`5` edges: `BKM -> decision`)
- `BKM01 (calculateAgeInYears)` -> `D01`, `D03`, `D04`, `D06`
- `BKM02 (countRecentClaims)` -> `D02`

### 2.3 Authority Requirements (`15` edges: `knowledgeSource -> decision / BKM`)
- `KS03` -> `D01`, `BKM01` (Regulatory SIM A/C minimum age 17)
- `KS01` -> `D01`, `D02`, `D03`, `D04`, `D05`, `D06`, `D10`, `BKM01`, `BKM02` (Educational Underwriting Policy)
- `KS02` -> `D07`, `D08`, `D09`, `D10` (Illustrative Tariff & Loading Schedule)

---

## 3. DAG & Structural Invariants Verification

- **Acyclicity:** Strictly monotonic 5-tier flow (`Tier 0 -> 0.5 -> 1 -> 2 -> 3 -> 4`) guarantees `isDAG = true`.
- **Minimum information requirement:** Every decision `D01`–`D10` receives between `2` and `6` information requirements (`min = 2`).
- **Safety Gate:** `D09` requires both `D05 (ACCEPT)` and `D10 (READY)`, guaranteeing declined, referred, or incomplete applications never yield an auto-approved or `Rp0` premium.
