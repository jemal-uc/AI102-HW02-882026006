import json
from pathlib import Path
import defusedxml.ElementTree as DET
from lxml import etree
import networkx as nx

ROOT = Path(__file__).resolve().parents[2]
DMN_PATH = ROOT / "src" / "decision-model" / "AsuransiNusantara.dmn"
SPEC_PATH = ROOT / "src" / "specification" / "CANONICAL_DECISION_SPECIFICATION.json"

NS = {
    "dmn": "https://www.omg.org/spec/DMN/20191111/MODEL/",
    "dmndi": "https://www.omg.org/spec/DMN/20191111/DMNDI/",
    "dc": "http://www.omg.org/spec/DMN/20180521/DC/",
    "di": "http://www.omg.org/spec/DMN/20180521/DI/",
}


def validate():
    raw_bytes = DMN_PATH.read_bytes()
    # Safe parse via defusedxml
    DET.fromstring(raw_bytes)
    tree = etree.fromstring(raw_bytes)

    root_ns = etree.QName(tree.tag).namespace
    assert root_ns == NS["dmn"], f"Unexpected root namespace: {root_ns}"

    inputs = tree.xpath("dmn:inputData", namespaces=NS)
    bkms = tree.xpath("dmn:businessKnowledgeModel", namespaces=NS)
    kss = tree.xpath("dmn:knowledgeSource", namespaces=NS)
    decs = tree.xpath("dmn:decision", namespaces=NS)
    item_defs = tree.xpath("dmn:itemDefinition", namespaces=NS)
    shapes = tree.xpath("//dmndi:DMNShape", namespaces=NS)
    edges = tree.xpath("//dmndi:DMNEdge", namespaces=NS)

    all_ids = set(tree.xpath("//@id"))
    # Verify all href references exist
    broken_refs = []
    for href in tree.xpath("//@href"):
        target = href.lstrip("#")
        if target not in all_ids:
            broken_refs.append(href)
    for dref in tree.xpath("//@dmnElementRef"):
        if dref not in all_ids:
            broken_refs.append(dref)
    assert not broken_refs, f"Broken references: {broken_refs}"

    # Build DAG of information & knowledge dependencies
    G = nx.DiGraph()
    for el in inputs + bkms + decs:
        G.add_node(el.get("id"))

    info_counts = {}
    for d in decs:
        did = d.get("id")
        ireqs = d.xpath("dmn:informationRequirement", namespaces=NS)
        info_counts[did] = len(ireqs)
        assert len(ireqs) >= 1, f"Decision {did} has 0 informationRequirements"
        for req in ireqs:
            for ref in req.xpath("dmn:requiredInput/@href | dmn:requiredDecision/@href", namespaces=NS):
                G.add_edge(ref.lstrip("#"), did, type="information")
        for req in d.xpath("dmn:knowledgeRequirement", namespaces=NS):
            for ref in req.xpath("dmn:requiredKnowledge/@href", namespaces=NS):
                G.add_edge(ref.lstrip("#"), did, type="knowledge")

    is_dag = nx.is_directed_acyclic_graph(G)
    assert is_dag, "DRD contains a cycle!"

    rules = tree.xpath("//dmn:rule", namespaces=NS)
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    expected_rules = sum(len(d["rules"]) for d in spec["decisions"])
    assert len(rules) == expected_rules, f"Rule count mismatch: {len(rules)} vs {expected_rules}"

    report = {
        "xmlWellFormed": True,
        "namespace": root_ns,
        "itemDefinitions": len(item_defs),
        "inputData": len(inputs),
        "businessKnowledgeModels": len(bkms),
        "knowledgeSources": len(kss),
        "decisions": len(decs),
        "decisionTables": len(tree.xpath("//dmn:decisionTable", namespaces=NS)),
        "rules": len(rules),
        "dmndiShapes": len(shapes),
        "dmndiEdges": len(edges),
        "brokenReferences": broken_refs,
        "isDAG": is_dag,
        "minInfoRequirementsPerDecision": min(info_counts.values()),
        "infoRequirementsByDecision": info_counts,
        "topologicalOrder": list(nx.topological_sort(G)),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    validate()
