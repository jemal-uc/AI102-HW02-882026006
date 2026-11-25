import json
import zipfile
from pathlib import Path
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
XSD_DIR = ROOT / "tests" / "validation-evidence" / "xsd"
DMN_PATH = ROOT / "src" / "decision-model" / "AsuransiNusantara.dmn"
SPEC_PATH = ROOT / "src" / "specification" / "CANONICAL_DECISION_SPECIFICATION.json"
RES_PATH = ROOT / "tests" / "test-results" / "TEST_RESULTS.json"
IDENTITY_PATH = ROOT / ".submission_identity.json"
PDF_PATH = ROOT / "reports" / "final-report" / "AI102_HW02_AsuransiNusantara_Report.pdf"
SUB_PDF_PATH = ROOT / "submission" / "AI102_HW02_AsuransiNusantara_Report.pdf"


class LocalResolver(etree.Resolver):
    def resolve(self, url, pubid, context):
        fname = url.rsplit("/", 1)[-1]
        local = XSD_DIR / fname
        if local.exists():
            return self.resolve_filename(str(local), context)
        return None


def check_xsd():
    parser = etree.XMLParser()
    parser.resolvers.add(LocalResolver())
    schema_doc = etree.parse(str(XSD_DIR / "DMN13.xsd"), parser)
    schema = etree.XMLSchema(schema_doc)
    dmn_doc = etree.parse(str(DMN_PATH))
    valid = schema.validate(dmn_doc)
    errors = [
        {"line": e.line, "col": e.column, "level": e.level_name, "message": e.message}
        for e in schema.error_log
    ]
    print("=== XSD VALIDATION ===")
    print("Valid against DMN13.xsd:", valid, "| Error count:", len(errors))
    for err in errors[:30]:
        print(" ", err)
    return valid, errors


def check_ids_and_dmndi():
    tree = etree.parse(str(DMN_PATH)).getroot()
    ids = tree.xpath("//@id")
    dups = [x for x in set(ids) if ids.count(x) > 1]
    # Verify NCName validity and DMNDI bounds
    ns = {
        "dmn": "https://www.omg.org/spec/DMN/20191111/MODEL/",
        "dmndi": "https://www.omg.org/spec/DMN/20191111/DMNDI/",
        "dc": "http://www.omg.org/spec/DMN/20180521/DC/",
        "di": "http://www.omg.org/spec/DMN/20180521/DI/",
    }
    drg_ids = set(tree.xpath("dmn:inputData/@id | dmn:decision/@id | dmn:businessKnowledgeModel/@id | dmn:knowledgeSource/@id", namespaces=ns))
    shape_refs = set(tree.xpath("//dmndi:DMNShape/@dmnElementRef", namespaces=ns))
    req_ids = set(tree.xpath("//dmn:informationRequirement/@id | //dmn:knowledgeRequirement/@id | //dmn:authorityRequirement/@id", namespaces=ns))
    edge_refs = set(tree.xpath("//dmndi:DMNEdge/@dmnElementRef", namespaces=ns))

    # Check overlapping shapes
    boxes = []
    for sh in tree.xpath("//dmndi:DMNShape", namespaces=ns):
        b = sh.find("dc:Bounds", namespaces=ns)
        boxes.append((
            sh.get("dmnElementRef"),
            float(b.get("x")), float(b.get("y")),
            float(b.get("width")), float(b.get("height")),
        ))
    overlaps = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            n1, x1, y1, w1, h1 = boxes[i]
            n2, x2, y2, w2, h2 = boxes[j]
            if x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2:
                overlaps.append((n1, n2))

    print("=== ID & DMNDI CHECKS ===")
    print("Total IDs:", len(ids), "| Duplicate IDs:", dups)
    print("Missing DMNShapes for DRG nodes:", drg_ids - shape_refs)
    print("Extra DMNShapes:", shape_refs - drg_ids)
    print("Missing DMNEdges for Requirements:", req_ids - edge_refs)
    print("Extra DMNEdges:", edge_refs - req_ids)
    print("Overlapping DMNShapes:", overlaps)


def check_zip_and_cross_artifacts():
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    res = json.loads(RES_PATH.read_text(encoding="utf-8"))
    tree = etree.parse(str(DMN_PATH)).getroot()
    ns = {"dmn": "https://www.omg.org/spec/DMN/20191111/MODEL/"}

    # Compare every decision & rule in spec vs DMN XML
    mismatches = []
    for dec in spec["decisions"]:
        xel = tree.xpath(f"dmn:decision[@id='{dec['id']}']", namespaces=ns)
        if not xel:
            mismatches.append(f"Missing decision {dec['id']} in XML")
            continue
        xel = xel[0]
        dt = xel.find("dmn:decisionTable", namespaces=ns)
        if dt.get("hitPolicy") != dec["hitPolicy"]:
            mismatches.append(f"{dec['id']} hitPolicy mismatch")
        if dec.get("aggregation") != dt.get("aggregation"):
            mismatches.append(f"{dec['id']} aggregation mismatch")
        xrules = dt.findall("dmn:rule", namespaces=ns)
        if len(xrules) != len(dec["rules"]):
            mismatches.append(f"{dec['id']} rule count mismatch")
        for r_spec, r_xml in zip(dec["rules"], xrules):
            if r_spec["id"] != r_xml.get("id"):
                mismatches.append(f"Rule id mismatch: {r_spec['id']} vs {r_xml.get('id')}")
            x_ins = [ie.find("dmn:text", namespaces=ns).text for ie in r_xml.findall("dmn:inputEntry", namespaces=ns)]
            x_out = r_xml.find("dmn:outputEntry/dmn:text", namespaces=ns).text
            if x_ins != r_spec["inputs"] or x_out != r_spec["output"]:
                mismatches.append(f"Rule content mismatch in {r_spec['id']}")

    print("=== CROSS-ARTIFACT INTEGRITY ===")
    print("Spec vs XML mismatches:", mismatches)
    if IDENTITY_PATH.exists():
        ident = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
        sub_name = ident.get("dmnFilename")
        sub_dmn = ROOT / "submission" / sub_name if sub_name else None
        zip_name = sub_name.replace(".dmn", "_Submission.zip") if sub_name else None
        zip_path = ROOT / "submission" / zip_name if zip_name else None
        if sub_dmn and sub_dmn.exists():
            print("Public DMN == Submission DMN:", DMN_PATH.read_bytes() == sub_dmn.read_bytes())
        if PDF_PATH.exists() and SUB_PDF_PATH.exists():
            print("Authoritative PDF == Submission PDF:", PDF_PATH.read_bytes() == SUB_PDF_PATH.read_bytes())
        if zip_path and zip_path.exists():
            with zipfile.ZipFile(zip_path, "r") as zf:
                znames = zf.namelist()
                print("ZIP entries:", znames)
                for zn in znames:
                    zbytes = zf.read(zn)
                    if zn.endswith(".dmn"):
                        print("ZIP .dmn byte-identical:", zbytes == DMN_PATH.read_bytes())
                    elif zn.endswith(".pdf") and PDF_PATH.exists():
                        print("ZIP .pdf byte-identical:", zbytes == PDF_PATH.read_bytes())


if __name__ == "__main__":
    check_xsd()
    check_ids_and_dmndi()
    check_zip_and_cross_artifacts()
