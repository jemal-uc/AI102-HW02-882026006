import json
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "src" / "specification" / "CANONICAL_DECISION_SPECIFICATION.json"
OUT_DMN = ROOT / "src" / "decision-model" / "AsuransiNusantara.dmn"
IDENTITY_PATH = ROOT / ".submission_identity.json"

NS_DMN = "https://www.omg.org/spec/DMN/20191111/MODEL/"
NS_DMNDI = "https://www.omg.org/spec/DMN/20191111/DMNDI/"
NS_DC = "http://www.omg.org/spec/DMN/20180521/DC/"
NS_DI = "http://www.omg.org/spec/DMN/20180521/DI/"

ET.register_namespace("", NS_DMN)
ET.register_namespace("dmndi", NS_DMNDI)
ET.register_namespace("dc", NS_DC)
ET.register_namespace("di", NS_DI)

# Clean non-overlapping 4-tier DRD coordinates (wide landscape layout for crisp Camunda/dmn-js rendering)
LAYOUT = {
    # Tier 0: Inputs (y=650)
    "I01": (60, 650, 145, 45),
    "I02": (230, 650, 145, 45),
    "I03": (400, 650, 165, 45),
    "I04": (590, 650, 140, 45),
    "I05": (755, 650, 175, 45),
    "I06": (955, 650, 140, 45),
    "I07": (1120, 650, 140, 45),
    "I08": (1285, 650, 155, 45),
    "I09": (1465, 650, 140, 45),
    "I10": (1630, 650, 145, 45),
    # Tier 0.5: BKMs (y=515)
    "BKM01": (390, 515, 185, 55),
    "BKM02": (630, 515, 185, 55),
    # Knowledge Sources
    "KS03": (40, 365, 170, 65),
    "KS01": (40, 200, 170, 65),
    "KS02": (1620, 200, 175, 65),
    # Tier 1 Decisions (y=365)
    "D01": (250, 365, 190, 68),
    "D02": (480, 365, 190, 68),
    "D03": (720, 365, 200, 68),
    "D04": (970, 365, 190, 68),
    "D07": (1370, 365, 200, 68),
    # Tier 2 Decisions (y=200)
    "D05": (560, 200, 200, 68),
    "D08": (1190, 200, 200, 68),
    # Tier 3 Decisions (y=50)
    "D06": (720, 50, 200, 68),
    "D09": (1120, 50, 200, 68),
}


def qname(ns, tag):
    return f"{{{ns}}}{tag}"


def center(box):
    x, y, w, h = box
    return (int(round(x + w / 2)), int(round(y + h / 2)))


def edge_points(src_id, dst_id):
    sx, sy, sw, sh = LAYOUT[src_id]
    dx, dy, dw, dh = LAYOUT[dst_id]
    scx, scy = sx + sw / 2, sy + sh / 2
    dcx, dcy = dx + dw / 2, dy + dh / 2
    # Vertical flow bottom-to-top when source is below target
    if sy > dy + dh:
        return [(int(scx), int(sy)), (int(dcx), int(dy + dh))]
    if dy > sy + sh:
        return [(int(scx), int(sy + sh)), (int(dcx), int(dy))]
    # Horizontal side connection
    if sx + sw < dx:
        return [(int(sx + sw), int(scy)), (int(dx), int(dcy))]
    return [(int(sx), int(scy)), (int(dx + dw), int(dcy))]


def build_dmn():
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))

    defs = ET.Element(
        qname(NS_DMN, "definitions"),
        {
            "id": "Definitions_AsuransiNusantara",
            "name": "AsuransiNusantara Motor Insurance Underwriting",
            "namespace": "https://asuransinusantara.example.edu/dmn/ai102-hw02",
            "exporter": "Canonical-Spec-Generator",
            "exporterVersion": "1.0.0",
        },
    )

    # 1. ItemDefinitions
    enum_types = [
        ("tVehicleType", "string", ["\"MOTORCYCLE\"", "\"CAR\""]),
        ("tPerformanceClass", "string", ["\"STANDARD\"", "\"SPORT\"", "\"HIGH_PERFORMANCE\""]),
        ("tCoverType", "string", ["\"TPO\"", "\"COMPREHENSIVE\""]),
        ("tDriverRisk", "string", ["\"LOW\"", "\"MEDIUM\"", "\"HIGH\"", "\"INELIGIBLE\"", "\"UNKNOWN\""]),
        ("tClaimsRisk", "string", ["\"LOW\"", "\"MEDIUM\"", "\"HIGH\"", "\"UNKNOWN\""]),
        ("tVehicleEligibility", "string", ["\"ELIGIBLE\"", "\"INELIGIBLE\""]),
        ("tVehicleRisk", "string", ["\"LOW\"", "\"MEDIUM\"", "\"HIGH\""]),
        ("tUnderwritingDecision", "string", ["\"ACCEPT\"", "\"REFER\"", "\"DECLINE\""]),
        ("tInspectionDecision", "string", ["\"REQUIRED\"", "\"NOT_REQUIRED\"", "\"NOT_APPLICABLE\""]),
    ]
    for tid, base, vals in enum_types:
        idef = ET.SubElement(defs, qname(NS_DMN, "itemDefinition"), {"id": f"ItemDef_{tid}", "name": tid})
        tr = ET.SubElement(idef, qname(NS_DMN, "typeRef"))
        tr.text = base
        av = ET.SubElement(idef, qname(NS_DMN, "allowedValues"), {"id": f"Allowed_{tid}"})
        t = ET.SubElement(av, qname(NS_DMN, "text"))
        t.text = ", ".join(vals)

    tdate_list = ET.SubElement(defs, qname(NS_DMN, "itemDefinition"), {
        "id": "ItemDef_tDateList",
        "name": "tDateList",
        "isCollection": "true",
    })
    ET.SubElement(tdate_list, qname(NS_DMN, "typeRef")).text = "date"

    edges_for_di = []

    # 2. InputData
    for inp in spec["inputs"]:
        el = ET.SubElement(defs, qname(NS_DMN, "inputData"), {"id": inp["id"], "name": inp["name"]})
        ET.SubElement(el, qname(NS_DMN, "variable"), {
            "id": f"Var_{inp['id']}",
            "name": inp["name"],
            "typeRef": inp["typeRef"],
        })

    # 3. KnowledgeSources
    for ks in spec["knowledgeSources"]:
        ET.SubElement(defs, qname(NS_DMN, "knowledgeSource"), {
            "id": ks["id"],
            "name": ks["name"],
        })

    # 4. BusinessKnowledgeModels
    for bkm in spec["bkms"]:
        bel = ET.SubElement(defs, qname(NS_DMN, "businessKnowledgeModel"), {
            "id": bkm["id"],
            "name": bkm["name"],
        })
        ET.SubElement(bel, qname(NS_DMN, "variable"), {
            "id": f"Var_{bkm['id']}",
            "name": bkm["name"],
            "typeRef": bkm["returnType"],
        })
        logic = ET.SubElement(bel, qname(NS_DMN, "encapsulatedLogic"), {
            "id": f"Logic_{bkm['id']}",
            "kind": "FEEL",
        })
        for idx, p in enumerate(bkm["parameters"], start=1):
            ET.SubElement(logic, qname(NS_DMN, "formalParameter"), {
                "id": f"Param_{bkm['id']}_{idx}",
                "name": p["name"],
                "typeRef": p["typeRef"],
            })
        lexp = ET.SubElement(logic, qname(NS_DMN, "literalExpression"), {
            "id": f"Expr_{bkm['id']}",
            "typeRef": bkm["returnType"],
        })
        ET.SubElement(lexp, qname(NS_DMN, "text")).text = bkm["feelBody"]

        for ksid in bkm["knowledgeSources"]:
            req_id = f"AuthReq_{bkm['id']}_{ksid}"
            ar = ET.SubElement(bel, qname(NS_DMN, "authorityRequirement"), {"id": req_id})
            ET.SubElement(ar, qname(NS_DMN, "requiredAuthority"), {"href": f"#{ksid}"})
            edges_for_di.append((req_id, ksid, bkm["id"]))

    # 5. Decisions
    for dec in spec["decisions"]:
        del_el = ET.SubElement(defs, qname(NS_DMN, "decision"), {
            "id": dec["id"],
            "name": dec["label"],
        })
        ET.SubElement(del_el, qname(NS_DMN, "variable"), {
            "id": f"Var_{dec['id']}",
            "name": dec["outputName"],
            "typeRef": dec["outputTypeRef"],
        })

        for src_id in dec["informationRequirements"]:
            req_id = f"InfoReq_{dec['id']}_{src_id}"
            ir = ET.SubElement(del_el, qname(NS_DMN, "informationRequirement"), {"id": req_id})
            if src_id.startswith("I"):
                ET.SubElement(ir, qname(NS_DMN, "requiredInput"), {"href": f"#{src_id}"})
            else:
                ET.SubElement(ir, qname(NS_DMN, "requiredDecision"), {"href": f"#{src_id}"})
            edges_for_di.append((req_id, src_id, dec["id"]))

        for bkm_id in dec["knowledgeRequirements"]:
            req_id = f"KnowReq_{dec['id']}_{bkm_id}"
            kr = ET.SubElement(del_el, qname(NS_DMN, "knowledgeRequirement"), {"id": req_id})
            ET.SubElement(kr, qname(NS_DMN, "requiredKnowledge"), {"href": f"#{bkm_id}"})
            edges_for_di.append((req_id, bkm_id, dec["id"]))

        for ks_id in dec["authorityRequirements"]:
            req_id = f"AuthReq_{dec['id']}_{ks_id}"
            ar = ET.SubElement(del_el, qname(NS_DMN, "authorityRequirement"), {"id": req_id})
            ET.SubElement(ar, qname(NS_DMN, "requiredAuthority"), {"href": f"#{ks_id}"})
            edges_for_di.append((req_id, ks_id, dec["id"]))

        dt_attrs = {
            "id": f"DT_{dec['id']}",
            "hitPolicy": dec["hitPolicy"],
            "outputLabel": dec["outputName"],
        }
        if "aggregation" in dec:
            dt_attrs["aggregation"] = dec["aggregation"]
        dt = ET.SubElement(del_el, qname(NS_DMN, "decisionTable"), dt_attrs)

        for din in dec["inputs"]:
            inp_el = ET.SubElement(dt, qname(NS_DMN, "input"), {
                "id": din["id"],
                "label": din["label"],
            })
            iexp = ET.SubElement(inp_el, qname(NS_DMN, "inputExpression"), {
                "id": f"{din['id']}_expr",
                "typeRef": din["typeRef"],
            })
            ET.SubElement(iexp, qname(NS_DMN, "text")).text = din["expression"]

        out_attrs = {
            "id": f"{dec['id']}_out",
            "name": dec["outputName"],
            "typeRef": dec["outputTypeRef"],
        }
        out_el = ET.SubElement(dt, qname(NS_DMN, "output"), out_attrs)
        if "allowedValues" in dec:
            ov = ET.SubElement(out_el, qname(NS_DMN, "outputValues"), {"id": f"{dec['id']}_outVals"})
            ET.SubElement(ov, qname(NS_DMN, "text")).text = ", ".join(f'"{v}"' for v in dec["allowedValues"])

        for r_idx, rule in enumerate(dec["rules"], start=1):
            rel = ET.SubElement(dt, qname(NS_DMN, "rule"), {"id": rule["id"]})
            ET.SubElement(rel, qname(NS_DMN, "description")).text = f"{rule['id']}: {rule['annotation']}"
            for c_idx, cell in enumerate(rule["inputs"], start=1):
                ie = ET.SubElement(rel, qname(NS_DMN, "inputEntry"), {"id": f"{rule['id']}_in{c_idx}"})
                ET.SubElement(ie, qname(NS_DMN, "text")).text = cell
            oe = ET.SubElement(rel, qname(NS_DMN, "outputEntry"), {"id": f"{rule['id']}_out1"})
            ET.SubElement(oe, qname(NS_DMN, "text")).text = rule["output"]

    # 6. DMNDI
    dmndi = ET.SubElement(defs, qname(NS_DMNDI, "DMNDI"))
    diag = ET.SubElement(dmndi, qname(NS_DMNDI, "DMNDiagram"), {"id": "DMNDiagram_DRD"})

    for el_id, (x, y, w, h) in LAYOUT.items():
        shape = ET.SubElement(diag, qname(NS_DMNDI, "DMNShape"), {
            "id": f"Shape_{el_id}",
            "dmnElementRef": el_id,
        })
        ET.SubElement(shape, qname(NS_DC, "Bounds"), {
            "x": str(x),
            "y": str(y),
            "width": str(w),
            "height": str(h),
        })

    for edge_id, src_id, dst_id in edges_for_di:
        edge = ET.SubElement(diag, qname(NS_DMNDI, "DMNEdge"), {
            "id": f"Edge_{edge_id}",
            "dmnElementRef": edge_id,
        })
        for wx, wy in edge_points(src_id, dst_id):
            ET.SubElement(edge, qname(NS_DI, "waypoint"), {"x": str(wx), "y": str(wy)})

    raw = ET.tostring(defs, encoding="utf-8")
    pretty = minidom.parseString(raw).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
    # Remove blank lines introduced by toprettyxml
    lines = [ln for ln in pretty.splitlines() if ln.strip()]
    OUT_DMN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    synced = []
    if IDENTITY_PATH.exists():
        ident = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
        sub_name = ident.get("dmnFilename")
        if sub_name:
            for dst in (ROOT / "src" / "decision-model" / sub_name, ROOT / "submission" / sub_name):
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(OUT_DMN, dst)
                synced.append(str(dst.relative_to(ROOT)))
    print(f"Generated {OUT_DMN} ({len(lines)} lines, {len(edges_for_di)} DRD edges); synced={synced}")


if __name__ == "__main__":
    build_dmn()
