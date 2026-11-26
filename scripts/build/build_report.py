import html
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "src" / "specification" / "CANONICAL_DECISION_SPECIFICATION.json"
RES_PATH = ROOT / "tests" / "test-results" / "TEST_RESULTS.json"
IND_PATH = ROOT / "tests" / "test-results" / "INDEPENDENT_EXECUTION_RESULTS.json"
DRD_IMG = ROOT / "outputs" / "diagrams" / "DRD_DIAGRAM.png"
DMNJS_IMG = ROOT / "tests" / "validation-evidence" / "dmnjs_drd_verify.png"
OUT_HTML = ROOT / "reports" / "AI102_HW02_AsuransiNusantara_Report.html"
OUT_PDF = ROOT / "reports" / "AI102_HW02_AsuransiNusantara_Report.pdf"
SUBMISSION_PDF = ROOT / "submission" / "AI102_HW02_AsuransiNusantara_Report.pdf"
IDENTITY_PATH = ROOT / ".submission_identity.json"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def esc(val):
    return html.escape(str(val))


def fmt_idr(v):
    if v is None:
        return "<code>null</code>"
    return f"Rp{int(round(v)):,}"


def fmt_idr_plain(v):
    if v is None:
        return "null"
    return f"Rp{int(round(v)):,}"


def fmt_val(v):
    if v is None:
        return "null"
    return str(v)


def build():
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    res = json.loads(RES_PATH.read_text(encoding="utf-8"))
    ind = json.loads(IND_PATH.read_text(encoding="utf-8")) if IND_PATH.exists() else {}

    ident = {
        "dmnFilename": "AsuransiNusantara.dmn",
        "authors": [{"name": "Author 1", "nim": "LOCAL"}, {"name": "Author 2", "nim": "LOCAL"}],
    }
    if IDENTITY_PATH.exists():
        ident = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
    authors = ident.get("authors", [])
    dmn_label = ident.get("dmnFilename", "AsuransiNusantara.dmn")
    a1_name = authors[0]["name"] if len(authors) > 0 else "Author 1"
    a1_nim = authors[0]["nim"] if len(authors) > 0 else "LOCAL"
    a2_name = authors[1]["name"] if len(authors) > 1 else "Author 2"
    a2_nim = authors[1]["nim"] if len(authors) > 1 else "LOCAL"
    author_meta = ", ".join(f"{a['name']} ({a['nim']})" for a in authors)
    footer_left = f"{dmn_label} | " + " & ".join(f"{a['name']} ({a['nim']})" for a in authors)
    drd_rel = os.path.relpath(DRD_IMG, OUT_HTML.parent).replace("\\", "/")
    dmnjs_rel = os.path.relpath(DMNJS_IMG, OUT_HTML.parent).replace("\\", "/")

    total_table_rules = sum(len(d["rules"]) for d in spec["decisions"])
    num_decisions = len(spec["decisions"])
    num_bkms = len(spec["bkms"])
    e2e_total = res["endToEndValidation"]["total"]
    e2e_passed = res["endToEndValidation"]["passed"]
    ind_total = ind.get("totalCases", e2e_total)
    ind_passed = ind.get("passedCases", e2e_passed)

    decisions_sorted = sorted(spec["decisions"], key=lambda d: int(d["id"][1:]))

    # Per-decision rule count reconciliation rows for Appendix C (strict D01..D10 numerical order)
    stage1_counts = {"D01": 5, "D02": 5, "D03": 7, "D04": 10, "D05": 10, "D06": 6, "D07": 13, "D08": 14, "D09": 3, "D10": 0}
    stage2_counts = {"D01": 6, "D02": 5, "D03": 7, "D04": 14, "D05": 10, "D06": 6, "D07": 14, "D08": 14, "D09": 3, "D10": 0}
    recon_rows = []
    for dec in decisions_sorted:
        did = dec["id"]
        hp = dec["hitPolicy"] + (f" ({dec['aggregation']})" if "aggregation" in dec else "")
        recon_rows.append(
            f"<tr><td><b>{esc(did)}</b></td><td>{esc(dec['label'])}</td><td><code>{esc(hp)}</code></td>"
            f"<td>{stage1_counts.get(did, 0)}</td><td>{stage2_counts.get(did, 0)}</td><td><b>{len(dec['rules'])}</b></td>"
            f"<td>{esc(dec['outputName'])} (<code>{esc(dec['outputTypeRef'])}</code>)</td></tr>"
        )

    # Decision Responsibility Summary rows for Appendix B
    resp_rows = []
    for dec in decisions_sorted:
        reqs = ", ".join(dec["informationRequirements"] + dec["knowledgeRequirements"])
        resp_rows.append(
            f"<tr><td><b>{esc(dec['id'])}</b></td><td>{esc(dec['label'])}</td>"
            f"<td>{esc(dec.get('description', ''))}</td>"
            f"<td><code>{esc(reqs)}</code></td>"
            f"<td><code>{esc(dec['outputName'])}</code> (<code>{esc(dec['outputTypeRef'])}</code>)</td></tr>"
        )

    # Build Decision Tables HTML for Appendix C
    dt_blocks = []
    for dec in decisions_sorted:
        hp = dec["hitPolicy"] + (f" ({dec['aggregation']})" if "aggregation" in dec else "")
        headers = "".join(
            f"<th>{esc(inp['label'])}<br/><span class='subth'>{esc(inp['expression'])} (<code>{esc(inp['typeRef'])}</code>)</span></th>"
            for inp in dec["inputs"]
        )
        rows_html = []
        for r in dec["rules"]:
            cells = "".join(f"<td><code>{esc(c)}</code></td>" for c in r["inputs"])
            rows_html.append(
                f"<tr><td><b>{esc(r['id'])}</b></td>{cells}<td><code>{esc(r['output'])}</code></td><td>{esc(r['annotation'])}</td></tr>"
            )
        dt_blocks.append(f"""
        <div class="avoid-break">
          <h3>{esc(dec['id'])}: {esc(dec['label'])} &mdash; Hit Policy: <code>{esc(hp)}</code> | Output: <code>{esc(dec['outputName'])}: {esc(dec['outputTypeRef'])}</code> ({len(dec['rules'])} rules)</h3>
          <table class="compact-tbl">
            <thead><tr><th style="width:10%">Rule ID</th>{headers}<th>{esc(dec['outputName'])}</th><th style="width:24%">Business Annotation</th></tr></thead>
            <tbody>{''.join(rows_html)}</tbody>
          </table>
        </div>
        """)

    # Build FEEL validation rows for Appendix D
    feel_rows = []
    for expr in res["feelValidation"]["expressions"]:
        for t in expr["tests"]:
            status = "<span class='pass'>PASS</span>" if t["pass"] else "<span class='fail'>FAIL</span>"
            edge_lbl = " [Edge]" if t["isEdgeCase"] else ""
            feel_rows.append(
                f"<tr><td><b>{esc(expr['id'])}</b></td><td>{esc(expr['category'])}</td>"
                f"<td><code>{esc(expr['expression'])}</code></td>"
                f"<td>{esc(t['name'])}{edge_lbl}<br/><span class='muted'><code>{esc(json.dumps(t['context']))}</code></span></td>"
                f"<td><code>{esc(fmt_val(t['expected']))}</code></td><td><code>{esc(fmt_val(t['actual']))}</code></td><td>{status}</td></tr>"
            )

    # Build all 18 E2E rows for Appendix E
    e2e_rows = []
    for tc in res["endToEndValidation"]["cases"]:
        a = tc["actual"]
        status = "<span class='pass'>PASS</span>" if tc["pass"] else "<span class='fail'>FAIL</span>"
        rules_str = ", ".join(f"{k}:{'+'.join(v['matchedRuleIds'])}" for k, v in tc["trace"].items())
        ct_val = tc["inputs"]["coverType"]
        ct_lbl = '""' if ct_val == "" else ("null" if ct_val is None else ct_val)
        e2e_rows.append(
            f"<tr><td><b>{esc(tc['id'])}</b><br/><span class='muted'>{esc(tc['category'])}</span></td>"
            f"<td>Age {esc(fmt_val(a['driverAge']))}; Clm {esc(fmt_val(a['recentClaimsCount']))} (avail={esc(tc['inputs']['claimsHistoryAvailable'])}); "
            f"{esc(tc['inputs']['vehicleType'])} {esc(tc['inputs']['engineCC'])}cc ({esc(tc['inputs']['performanceClass'])}); "
            f"VehAge {esc(fmt_val(a['vehicleAge']))}; Cover=<code>{esc(ct_lbl)}</code>; {fmt_idr(tc['inputs']['insuredValue'])}</td>"
            f"<td>{esc(a['driverRisk'])} / {esc(a['claimsRisk'])} / {esc(a['vehicleEligibility'])} / {esc(a['vehicleRisk'])}</td>"
            f"<td><b>{esc(a['underwritingDecision'])}</b><br/>Insp: {esc(a['inspectionDecision'])}<br/>Quote: <code>{esc(a['quoteReadiness'])}</code></td>"
            f"<td>Base: {fmt_idr(a['basePremium'])}<br/>Load: +{int(round(a['totalRiskLoading']*100))}%<br/><b>Final: {fmt_idr(a['finalPremium'])}</b></td>"
            f"<td><span class='tiny-code'>{esc(rules_str)}</span></td><td>{status}</td></tr>"
        )

    # Main-text compact trace table: key representative & Stage 5 regression cases (6 rows fit cleanly in <= 3 pages)
    main_tc_rows = []
    for tc_id in ["TC-01", "TC-02", "TC-03", "TC-04", "TC-11", "TC-12"]:
        tc = next(c for c in res["endToEndValidation"]["cases"] if c["id"] == tc_id)
        a = tc["actual"]
        ct_val = tc["inputs"]["coverType"]
        ct_disp = "null" if ct_val is None else ('""' if ct_val == "" else ("COMP" if ct_val == "COMPREHENSIVE" else ("UNSUP" if ct_val.startswith("ALL_RISK") else ct_val)))
        iv_disp = fmt_idr_plain(tc["inputs"]["insuredValue"]).replace(",000,000", "M")
        main_tc_rows.append(
            f"<tr><td><b>{esc(tc['id'])}</b></td><td>{esc(tc['category'].replace('Stage 5 Regression ', 'Reg: '))}</td>"
            f"<td>Age {esc(a['driverAge'])}, {esc(tc['inputs']['vehicleType'][:2])} {esc(tc['inputs']['engineCC'])}cc, Veh {esc(a['vehicleAge'])}y, {esc(ct_disp)}, {esc(iv_disp)}</td>"
            f"<td>{esc(a['driverRisk'])}</td><td>{esc(a['claimsRisk'])}</td><td>{esc(a['vehicleEligibility'][:4])}.</td><td>{esc(a['vehicleRisk'])}</td>"
            f"<td><b>{esc(a['underwritingDecision'])}</b></td><td><code>{esc(a['quoteReadiness'].replace('PENDING_INFORMATION', 'PENDING_INFO'))}</code></td>"
            f"<td>{fmt_idr(a['basePremium'])}</td><td>+{int(round(a['totalRiskLoading']*100))}%</td><td><b>{fmt_idr(a['finalPremium'])}</b></td></tr>"
        )

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="author" content="{esc(author_meta)}" />
<title>AI102 Homework-02 — Decision Modeling with DMN (AsuransiNusantara)</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 14mm 12.5mm 14mm 12.5mm;
    @top-left {{
      content: "AI102 Decision Intelligence (3 SKS) — Master of Artificial Intelligence, FTI UKSW";
      font-family: Arial, Helvetica, sans-serif;
      font-size: 6.9pt;
      color: #4A5568;
      border-bottom: 0.5pt solid #CBD5E1;
      padding-bottom: 2pt;
    }}
    @top-right {{
      content: "Homework-02: DMN 1.3 (Scenario B)";
      font-family: Arial, Helvetica, sans-serif;
      font-size: 6.9pt;
      color: #1B365D;
      font-weight: bold;
      border-bottom: 0.5pt solid #CBD5E1;
      padding-bottom: 2pt;
    }}
    @bottom-left {{
      content: "{footer_left.replace('"', '')}";
      font-family: Arial, Helvetica, sans-serif;
      font-size: 6.6pt;
      color: #4A5568;
      border-top: 0.5pt solid #CBD5E1;
      padding-top: 2pt;
    }}
    @bottom-right {{
      content: "Page " counter(page) " of " counter(pages);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 6.9pt;
      color: #1B365D;
      font-weight: bold;
      border-top: 0.5pt solid #CBD5E1;
      padding-top: 2pt;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Times New Roman", Times, serif;
    font-size: 8.75pt;
    line-height: 1.28;
    color: #1A202C;
    margin: 0;
    padding: 0;
    text-align: justify;
  }}
  .header-block {{
    border-bottom: 1.4pt solid #1B365D;
    padding-bottom: 4pt;
    margin-bottom: 5pt;
    text-align: left;
  }}
  .kicker {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 7.2pt;
    font-weight: bold;
    color: #2B5B9E;
    letter-spacing: 0.35pt;
    text-transform: uppercase;
    margin-bottom: 1.5pt;
  }}
  h1.doc-title {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 12.8pt;
    font-weight: bold;
    color: #1B365D;
    text-align: center;
    margin: 2pt 0 3.5pt 0;
    line-height: 1.18;
  }}
  .meta-grid {{
    width: 100%;
    border-collapse: collapse;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 7.1pt;
    background: #F4F7FB;
    border: 0.6pt solid #CBD5E1;
  }}
  .meta-grid td {{
    padding: 1.8pt 4.5pt;
    border: 0.4pt solid #CBD5E1;
    vertical-align: top;
    text-align: left;
  }}
  .meta-lbl {{ font-weight: bold; color: #1B365D; width: 15%; }}
  h2 {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 9.4pt;
    font-weight: bold;
    text-transform: uppercase;
    color: #1B365D;
    border-bottom: 0.85pt solid #1B365D;
    margin: 5pt 0 3pt 0;
    padding-bottom: 1.2pt;
    text-align: left;
    page-break-after: avoid;
  }}
  h3 {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 8.3pt;
    font-weight: bold;
    color: #2B5B9E;
    margin: 4.5pt 0 2pt 0;
    text-align: left;
    page-break-after: avoid;
  }}
  p {{ margin: 0 0 3pt 0; }}
  code {{
    font-family: Consolas, "Courier New", monospace;
    font-size: 7.1pt;
    background: #F1F5F9;
    padding: 0.4pt 1.8pt;
    border-radius: 1.5pt;
  }}
  .fig-box {{
    text-align: center;
    border: 0.6pt solid #CBD5E1;
    background: #FFFFFF;
    padding: 2.5pt;
    margin: 3pt 0 3.5pt 0;
    page-break-inside: avoid;
  }}
  .fig-box img {{
    max-width: 100%;
    max-height: 70mm;
    height: auto;
    display: block;
    margin: 0 auto;
  }}
  .caption {{
    font-family: "Times New Roman", Times, serif;
    font-style: italic;
    font-size: 7.2pt;
    color: #4A5568;
    text-align: center;
    margin-top: 1.5pt;
  }}
  table.compact-tbl {{
    width: 100%;
    border-collapse: collapse;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 6.95pt;
    line-height: 1.18;
    margin: 2.5pt 0 3.5pt 0;
    text-align: left;
  }}
  table.compact-tbl thead {{ display: table-header-group; }}
  table.compact-tbl th {{
    background: #1B365D;
    color: #FFFFFF;
    font-weight: bold;
    padding: 2pt 3.5pt;
    border: 0.4pt solid #1B365D;
    vertical-align: bottom;
  }}
  table.compact-tbl th code {{
    background: rgba(255, 255, 255, 0.18);
    color: #FFFFFF;
  }}
  table.compact-tbl td {{
    padding: 1.7pt 3.5pt;
    border: 0.4pt solid #CBD5E1;
    vertical-align: top;
  }}
  table.compact-tbl tbody tr:nth-child(even) {{ background: #F8FAFC; }}
  .subth {{ font-weight: normal; font-size: 6.1pt; color: #DBEAFE; }}
  .formula-box {{
    background: #F4F7FB;
    border-left: 2.5pt solid #1B365D;
    padding: 2.5pt 5.5pt;
    margin: 2.5pt 0 3pt 0;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 7.5pt;
    text-align: left;
  }}
  .two-col {{ display: flex; gap: 7pt; align-items: flex-start; }}
  .col-half {{ flex: 1; }}
  .page-break {{ page-break-before: always; }}
  .avoid-break {{ page-break-inside: avoid; }}
  .pass {{ color: #166534; font-weight: bold; }}
  .fail {{ color: #991B1B; font-weight: bold; }}
  .muted {{ color: #4A5568; font-size: 6.5pt; }}
  .tiny-code {{ font-family: Consolas, monospace; font-size: 6.1pt; color: #334155; }}
</style>
</head>
<body>

<!-- ==================== PAGES 1-3: MAIN REPORT (STRICTLY <= 3 PAGES) ==================== -->
<div class="header-block">
  <div class="kicker">AI102 &mdash; Decision Intelligence (3 SKS) | Chapter 03: Decision Model and Notation (DMN 1.3) | Scenario B</div>
  <h1 class="doc-title">Formal DMN 1.3 Underwriting &amp; Pricing Architecture for Motor Insurance (AsuransiNusantara)</h1>
  <table class="meta-grid">
    <tr>
      <td class="meta-lbl">Course &amp; Task</td><td>AI102 &mdash; Decision Intelligence | Homework-02: Decision Modeling with DMN (CPMK-02)</td>
      <td class="meta-lbl">Scenario</td><td><b>Scenario B &mdash; Motor Insurance Underwriting (AsuransiNusantara)</b></td>
    </tr>
    <tr>
      <td class="meta-lbl">Group</td><td>1. <b>{esc(a1_name)}</b> &mdash; {esc(a1_nim)}<br/>2. <b>{esc(a2_name)}</b> &mdash; {esc(a2_nim)}</td>
      <td class="meta-lbl">Lecturer</td><td>Teguh Indra Bayu, S.Kom., M.Cs., Ph.D. | Odd Semester 2026/2027</td>
    </tr>
    <tr>
      <td class="meta-lbl">Program / Univ.</td><td>Master of Artificial Intelligence, FTI, Universitas Kristen Satya Wacana (UKSW)</td>
      <td class="meta-lbl">Model File</td><td><code>{esc(dmn_label)}</code> (DMN 1.3 XML, {num_decisions} decisions, {total_table_rules} rules, {num_bkms} BKMs)</td>
    </tr>
  </table>
</div>

<h2>1. Model Overview &amp; Decision Requirements Diagram (DRD)</h2>
<p>We formalize motor underwriting for <b>AsuransiNusantara</b> as a deterministic OMG DMN 1.3 decision architecture (Taylor &amp; Purchase, 2019). From ten typed inputs (<code>I01</code>&ndash;<code>I10</code>, using an explicit <code>evaluationDate</code> to eliminate clock non-determinism), the model evaluates <b>ten decisions</b> (<code>D01</code>&ndash;<code>D10</code>) supported by two Business Knowledge Models (<code>BKM01</code>, <code>BKM02</code>) and three Knowledge Sources (<code>KS01</code>&ndash;<code>KS03</code>). All 42 information, 5 knowledge, and 15 authority requirements form a verified 5-tier directed acyclic graph (DAG) with at least two information requirements per decision (Figure 1).</p>

<div class="fig-box">
  <img src="{esc(drd_rel)}" alt="DMN 1.3 DRD for AsuransiNusantara" />
  <div class="caption">Figure 1: Complete 5-tier DMN 1.3 Decision Requirements Diagram (DRD) for Scenario B (10 inputs, 2 BKMs, 3 Knowledge Sources, 10 decisions, 62 typed edges).</div>
</div>

<h2>2. Decision Decomposition Rationale &amp; Underwriting vs. Quote Separation</h2>
<p>Rather than collapsing underwriting into a monolithic 120+-combination matrix, decomposition isolates four distinct operational responsibilities (complete one-sentence specifications in Appendix B): (1) <b>Independent Risk &amp; Eligibility (Tier 1: <code>D01</code>&ndash;<code>D04</code>, <code>D07</code>)</b> separates driver age risk (<code>D01</code>), claims recency (<code>D02</code>), hard vehicle eligibility (<code>D03</code>), technical vehicle risk (<code>D04</code>), and tariff lookup (<code>D07</code>). Splitting <code>D03</code> from <code>D04</code> prevents invalid or &gt;15-year vehicles from being accepted via low driver risk, while deferring missing <code>insuredValue</code> (<code>null</code>) out of hard decline. (2) <b>Risk Disposition &amp; Additive Loading (Tier 2: <code>D05</code>, <code>D08</code>)</b> computes <code>DECLINE &gt; REFER &gt; ACCEPT</code> purely on underwriting risk—independent of commercial <code>coverType</code>—and sums orthogonal surcharges in <code>D08</code>. (3) <b>Inspection &amp; Quote Readiness (Tier 3: <code>D06</code>, <code>D10</code>)</b> separates physical inspection (<code>D06</code>) and commercial pricing completeness (<code>D10</code>: <code>READY</code>, <code>PENDING_INFORMATION</code>, <code>INVALID_INPUT</code>, <code>NOT_APPLICABLE</code>). (4) <b>Premium Safety Gate (Tier 4: <code>D09</code>)</b> outputs a positive IDR premium <i>only</i> when <code>D05="ACCEPT"</code>, <code>D10="READY"</code>, and <code>D07 &gt; 0</code>, returning <code>null</code> (never <code>Rp0</code>) on declined, referred, pending, or invalid cases.</p>

<h2>3. Narrative Ambiguities &amp; Regulatory vs. Educational Attribution</h2>
<p>Only the baseline <code>&lt;17</code> minimum age traces to statutory Indonesian law: <b>UU No. 22/2009 Art. 81(2)(a)</b> (min age 17 for SIM A/C) and Korlantas Polri <b>Perpol No. 5/2021 Art. 3 &amp; 8</b> (SIM C &le;250cc min age <b>17</b>; SIM CI &gt;250&ndash;500cc min age <b>18</b>; SIM CII &gt;500cc min age <b>19</b>). Thus <code>UU 22/2009</code> alone does not cover high-displacement motorcycles (Sec. 6 limitation). All other cutoffs, tariffs, and loadings are <b>illustrative educational assumptions</b> (<code>KS01</code>/<code>KS02</code>), distinct from OJK tariff bands in <b>SEOJK No. 6/SEOJK.05/2017</b> (Appendix A).</p>

<table class="compact-tbl">
  <thead>
    <tr><th style="width:9%">ID</th><th style="width:22%">Narrative Term / Clause</th><th style="width:41%">Adopted Rule / Threshold &amp; Origin Type</th><th style="width:28%">Rationale</th></tr>
  </thead>
  <tbody>
    <tr><td><b>AMB-01</b></td><td>"Young drivers" &amp; age</td><td><b>[Legal+Educ.]</b> <code>&lt;17</code>: <code>INELIGIBLE</code> (<code>UU 22/2009</code> &amp; <code>Perpol 5/2021</code> SIM C base); <code>[17..24]</code>: <code>HIGH</code> (+25%); <code>[25..65]</code>: <code>LOW</code>; <code>&gt;65</code>: <code>MEDIUM</code> (+10%); <code>null</code>: <code>UNKNOWN</code>.</td><td>Applies universal age-17 floor without a full SIM CI/CII compliance engine.</td></tr>
    <tr><td><b>AMB-02/03</b></td><td>"Recent claims" / missing</td><td><b>[Educ. Policy]</b> Inclusive 24M window <code>[eval-P24M, eval]</code>: 0&rarr;<code>LOW</code>, 1&rarr;<code>MED</code> (+20%), &ge;2&rarr;<code>HIGH</code> (+40%, <code>REFER</code>); missing&rarr;<code>UNKNOWN</code> (<code>REFER</code>, +25%).</td><td>Never equates unavailable history with zero claims.</td></tr>
    <tr><td><b>AMB-04/05</b></td><td>Old vehicles &amp; inspection</td><td><b>[Educ. Policy]</b> Age <code>&gt;15</code>y &rarr; <code>INELIGIBLE</code> (<code>DECLINE</code>); <code>[11..15]</code>y raises <code>D04</code> &ge;<code>MED</code>. <code>DECLINE</code>&rarr;<code>NOT_APPL</code>; else <code>REQUIRED</code> if <code>&ge;Rp500M</code> or (<code>COMP</code> &amp; <code>&gt;10</code>y).</td><td>Controls obsolescence and high-value fraud exposure.</td></tr>
    <tr><td><b>AMB-06/07</b></td><td>Sporty &amp; cc bands</td><td><b>[Educ. Policy]</b> <code>STANDARD</code> (+0%), <code>SPORT</code> (+15%), <code>HIGH_PERF</code> (+30%). MC: <code>(0..150]</code>, <code>(150..250]</code>, <code>&gt;250</code>cc; Car: <code>(0..1500]</code>, <code>(1500..2500]</code>, <code>&gt;2500</code>cc.</td><td>Prevents cross-class cc distortion vs. car displacements.</td></tr>
    <tr><td><b>AMB-08/09</b></td><td>Cover types &amp; stacking</td><td><b>[Educ.+Design]</b> Comp (1.8&ndash;3.2%) &gt; <code>TPO</code>/<code>THIRD_PARTY_ONLY</code> (0.4&ndash;1.0%) across all tiers. Additive <code>C+</code> loadings; <code>Base*(1+Loading)</code>.</td><td>Guarantees <code>Comp &gt; TPO</code> and transparent surcharge sum.</td></tr>
    <tr><td><b>AMB-10/12</b></td><td>Decline/Refer &amp; cover missing</td><td><b>[Design Safety]</b> <code>D05</code> ignores <code>coverType</code>. Missing/<code>""</code> cover or missing value &rarr; <code>D10=PENDING_INFO</code>; unsupported &rarr; <code>INVALID_INPUT</code>. <code>DECLINE</code>/<code>REFER</code>/non-<code>READY</code> &rarr; <code>D09=null</code>.</td><td>Eliminates unsafe <code>Rp0</code> quote fallback and auto-quoted referrals.</td></tr>
  </tbody>
</table>

<h2>4. Decision Tables, Hit Policies &amp; Representative Traces</h2>
<p>All ten decision tables (<b>{total_table_rules} rules</b> reconciled from Stage 1's 73 and Stage 2's 79 rules via Stage 2 guard additions and Stage 5's <code>D10</code>/<code>D09</code> safety gates; Appendix C) guarantee <b>zero silent fall-throughs</b>. <code>D01</code> uses <b><code>UNIQUE (U)</code></b> on disjoint intervals; <code>D02</code>&ndash;<code>D07</code>, <code>D09</code>, and <code>D10</code> use <b><code>FIRST (F)</code></b> for strict precedence (<code>null</code>/blank checks precede <code>not(...)</code> invalid checks); and <code>D08</code> uses <b><code>COLLECT SUM (C+)</code></b>:</p>
<div class="formula-box"><b>Null-Safe Additive Pricing:</b> &nbsp; <code>finalPremium = decimal(basePremium * (1 + totalRiskLoading), 0)</code> &nbsp; if <code>D05="ACCEPT" and D10="READY" and D07&gt;0</code>; &nbsp; else <code>null</code></div>

<table class="compact-tbl">
  <thead>
    <tr><th>Case</th><th>Profile</th><th>Key Inputs (<code>evalDate=2026-11-25</code>)</th><th>D01</th><th>D02</th><th>D03</th><th>D04</th><th>D05</th><th>D10</th><th>D07 (Base)</th><th>D08</th><th>D09 (Final)</th></tr>
  </thead>
  <tbody>{''.join(main_tc_rows)}</tbody>
</table>
<div class="caption">Table 1: Representative acceptance, borderline, referral, decline, and Stage 5 cover-missing/unsupported regression traces (full {e2e_total} canonical/regression + 8 preserved Stage 2 adversarial cases in Appendix E).</div>

<h2>5. FEEL Expressions, Engine Audit &amp; Defect Resolution</h2>
<p>All 6 canonical FEEL expressions covering all 5 required categories passed <b>18 / 18</b> tests in <code>feelin@8.2.2</code> (Node.js v24.15.0; Table 2 &amp; Appendix D), verifying calendar-aware <code>years and months duration</code> on leap-year boundaries (returning <code>25</code> on 25th birthday where naive <code>days/365.25</code> returns <code>24</code>), future-DOB <code>-1</code> sentinels, 3-point 24-month recency boundaries (<code>2024-11-24/25/26</code>), <code>null</code>/empty unary guards, and IEEE-754-safe <code>decimal(..., 0)</code>. <b>Execution Method Transparency:</b> Neither standalone Camunda Modeler nor Java Camunda DMN Engine is installed locally; <code>dmn-js@18.1.0</code> validates diagram loading only, while <code>validate_all.js</code> (<b>{e2e_passed}/{e2e_total} PASS</b>) and <code>independent_dmn_executor.js</code> (<b>{ind_passed}/{ind_total} PASS, 0 warnings</b>) operate as <b>hybrid test harnesses</b> pairing <code>dmn-moddle@12.2.1</code> XML deserialization + Kahn topological orchestration + <code>feelin@8.2.2</code> FEEL evaluation against independent pure-JS arithmetic checks.</p>

<table class="compact-tbl">
  <thead>
    <tr><th style="width:8%">ID</th><th style="width:19%">FEEL Category</th><th style="width:45%">Canonical Expression (Executed in <code>feelin@8.2.2</code>)</th><th style="width:28%">Sample &amp; Edge Verification</th></tr>
  </thead>
  <tbody>
    <tr><td><b>FEEL-01</b></td><td>Range interval</td><td><code>driverAge in [17..24]</code></td><td>17&rarr;<code>true</code>, 24&rarr;<code>true</code>, 25&rarr;<code>false</code> (3/3 PASS)</td></tr>
    <tr><td><b>FEEL-02</b></td><td>List membership</td><td><code>(vehicleType in ["MOTORCYCLE","CAR"]) and (performanceClass in ["SPORT","HIGH_PERFORMANCE"])</code></td><td>MC+SPORT&rarr;<code>true</code>, TRUCK/null&rarr;<code>false</code> (3/3 PASS)</td></tr>
    <tr><td><b>FEEL-03</b></td><td>Built-in functions</td><td><code>decimal(max(450000, insuredValue * 0.025) * (1 + totalRiskLoading), 0)</code></td><td>10M@35%&rarr;<code>607500</code>, 40M@35%&rarr;<code>1350000</code> (2/2 PASS)</td></tr>
    <tr><td><b>FEEL-04</b></td><td>Date/duration (age)</td><td><code>if targetDate=null or referenceDate=null then null else if date(targetDate)&gt;date(referenceDate) then -1 else years and months duration(...).years</code></td><td><code>2001-11-25</code>&rarr;<code>25</code>, <code>11-26</code>&rarr;<code>24</code>, future&rarr;<code>-1</code>, null&rarr;<code>null</code> (4/4)</td></tr>
    <tr><td><b>FEEL-05</b></td><td>Duration + <code>count</code></td><td><code>count(claimDates[date(item)&gt;=(date(referenceDate)-duration("P24M")) and date(item)&lt;=date(referenceDate)])</code></td><td><code>[26,25,24 Nov 24]</code>&rarr;<code>2</code>, <code>[24 Nov]</code>&rarr;<code>0</code>, <code>[]</code>&rarr;<code>0</code> (3/3)</td></tr>
    <tr><td><b>FEEL-06</b></td><td>Compound <code>if/else</code></td><td><code>if vehicleEligibility="INELIGIBLE" or driverRisk="INELIGIBLE" then "DECLINE" else if ... then "REFER" else "ACCEPT"</code></td><td>Ineligible&rarr;<code>DECLINE</code>, Unknown&rarr;<code>REFER</code>, Clean&rarr;<code>ACCEPT</code> (3/3)</td></tr>
  </tbody>
</table>

<h2>6. Known Limitations &amp; Machine-Learning Integration (Session 03)</h2>
<p><b>Limitations:</b> (1) Tariffs/cutoffs are educational assumptions rather than actuarial or SEOJK 6/2017 tables; (2) <b>motorcycle licensing verification is simplified</b>&mdash;under Korlantas Polri <b>Perpol No. 5/2021</b> Art. 3 &amp; 8, SIM CI (&gt;250&ndash;500cc) requires age &ge;18 and SIM CII (&gt;500cc) requires age &ge;19 (plus prior license tenure), whereas <code>D01</code> enforces only the baseline <code>&lt;17</code> SIM A/C floor; and (3) execution uses hybrid <code>feelin@8.2.2</code> table orchestration rather than Java Camunda Engine. <b>ML Integration:</b> A calibrated loss-propensity score <i>p</i> &isin; [0, 1] (Pratt &amp; Malcolm, 2023; Molnar, 2024) can plug cleanly into <code>D05</code> as an <code>inputData</code> escalation trigger (<code>REFER</code> if <i>p</i> &ge; &tau;) or a <code>BKM</code> scorecard so statutory (<code>KS03</code>), eligibility (<code>D03</code>), and readiness (<code>D10</code>) gates retain strict override control.</p>

<div class="two-col">
  <div class="col-half" style="flex:1.18;">
    <h2>7. Division of Labor</h2>
    <table class="compact-tbl">
      <thead><tr><th style="width:36%">Name &amp; NIM</th><th style="width:64%">Assigned Responsibilities</th></tr></thead>
      <tbody>
        <tr>
          <td><b>{esc(a1_name)}</b><br/>{esc(a1_nim)}</td>
          <td>Scenario elicitation, regulatory source check, DRD &amp; Quote Readiness architecture (<code>D10</code>), canonical specification, DMN 1.3 XML generation, and final integration.</td>
        </tr>
        <tr>
          <td><b>{esc(a2_name)}</b><br/>{esc(a2_nim)}</td>
          <td>Ambiguity register, data dictionary, decision tables (<code>D01</code>&ndash;<code>D10</code>), hit-policy reconciliation, FEEL edge verification, regression test suite, and report audit.</td>
        </tr>
      </tbody>
    </table>
    <div class="muted" style="margin-top:1.5pt;">Both authors reviewed all corrected rules, validation logs, and final submission deliverables.</div>
  </div>
  <div class="col-half" style="flex:0.82;">
    <h2>8. Key References</h2>
    <p style="font-size:6.9pt; line-height:1.18; text-align:left;">
      1. OMG. (2021). <i>Decision Model and Notation (DMN) Specification v1.3</i>. Object Management Group.<br/>
      2. RI. (2009). <i>UU No. 22 Tahun 2009 (UU LLAJ), Pasal 81 ayat (2) huruf a</i> (Min age 17 for SIM A/C/D).<br/>
      3. Polri / Korlantas. (2021). <i>Perpol No. 5 Tahun 2021 tentang Penerbitan &amp; Penandaan SIM</i>, Art. 3 &amp; 8 (SIM C/CI/CII ages 17/18/19; JDIH Polri).<br/>
      4. OJK. (2017). <i>SEOJK No. 6/SEOJK.05/2017</i> (Motor tariff benchmark; simplified in model).<br/>
      5. Pratt &amp; Malcolm (2023) <i>The Decision Intelligence Handbook</i>; Taylor &amp; Purchase (2019) <i>Real-World Decision Modeling with DMN</i>; Molnar (2024) <i>Interpretable ML</i>.
    </p>
  </div>
</div>

<!-- ==================== APPENDICES (PAGE 4+) ==================== -->
<div class="page-break"></div>
<h2>Appendix A &mdash; Complete Ambiguity-Resolution Register (12 Items)</h2>
<table class="compact-tbl">
  <thead><tr><th style="width:7%">ID</th><th style="width:17%">Ambiguous Clause</th><th style="width:19%">Open Question</th><th style="width:31%">Selected Rule / Threshold</th><th style="width:26%">Source Class &amp; Impact</th></tr></thead>
  <tbody>
    <tr><td><b>AMB-01</b></td><td>"Young drivers"</td><td>Age band &amp; min/senior limits?</td><td>&lt;17: <code>INELIGIBLE</code>; [17..24]: <code>HIGH</code> (+25%); [25..65]: <code>LOW</code>; &gt;65: <code>MEDIUM</code> (+10%); null: <code>UNKNOWN</code>; &lt;0: <code>INELIGIBLE</code>.</td><td><b>Legal (UU 22/2009 &amp; Perpol 5/2021 SIM C) + Policy:</b> Tiered SIM CI/CII (&gt;250cc) noted as limitation.</td></tr>
    <tr><td><b>AMB-02</b></td><td>"Recent claims"</td><td>Lookback window &amp; count tiers?</td><td><code>[evalDate - P24M, evalDate]</code>: 0&rarr;<code>LOW</code>; 1&rarr;<code>MEDIUM</code> (+20%); &ge;2&rarr;<code>HIGH</code> (+40%, <code>REFER</code>).</td><td><b>Educ. Policy:</b> Feeds <code>BKM02</code>, <code>D02</code>, <code>D05</code>, <code>D08</code>.</td></tr>
    <tr><td><b>AMB-03</b></td><td>"Missing claims history"</td><td>Treat missing as 0 claims?</td><td><code>claimsHistoryAvailable != true</code> or <code>claimDates = null</code> &rarr; <code>UNKNOWN</code> &rarr; <code>REFER</code> + 25% provisional loading.</td><td><b>Educ. Policy:</b> Prevents adverse selection.</td></tr>
    <tr><td><b>AMB-04</b></td><td>"Very old vehicles"</td><td>Max insurable age &amp; aging tier?</td><td><code>vehicleAge &gt; 15</code> &rarr; <code>INELIGIBLE</code> (<code>DECLINE</code>); <code>[11..15]</code> elevates <code>D04</code> &ge; <code>MEDIUM</code>.</td><td><b>Educ. Policy:</b> Feeds <code>D03</code>, <code>D04</code>, <code>D06</code>.</td></tr>
    <tr><td><b>AMB-05</b></td><td>"Very high value inspection"</td><td>IDR threshold &amp; TPO/Declined?</td><td><code>DECLINE</code>&rarr;<code>NOT_APPL</code>; else <code>REQUIRED</code> if <code>&ge;Rp500M</code>, (<code>COMPREHENSIVE</code> &amp; <code>age&gt;10</code>), or incomplete data.</td><td><b>Educ. Policy:</b> Anti-fraud valuation gate (<code>D06</code>).</td></tr>
    <tr><td><b>AMB-06</b></td><td>"Sporty/high-performance"</td><td>Classified without vehicle DB?</td><td><code>STANDARD</code> (+0%), <code>SPORT</code> (&ge;<code>MEDIUM</code>, +15%), <code>HIGH_PERFORMANCE</code> (<code>HIGH</code>, +30%).</td><td><b>Technical Choice:</b> Feeds <code>D04</code>, <code>D08</code>.</td></tr>
    <tr><td><b>AMB-07</b></td><td>"Engine size, esp. motorcycles"</td><td>CC cutoffs per vehicle type?</td><td>MC: <code>(0..150]</code>, <code>(150..250]</code>, <code>&gt;250</code>; Car: <code>(0..1500]</code>, <code>(1500..2500]</code>, <code>&gt;2500</code>.</td><td><b>Educ. Policy:</b> Not statutory PPnBM/OJK tiers.</td></tr>
    <tr><td><b>AMB-08</b></td><td>"Comprehensive &gt; TPO"</td><td>Rate structure &amp; TPO naming?</td><td>Comp (1.8&ndash;3.2%, floor Rp300k&ndash;2.5M) &gt; <code>TPO</code>/<code>THIRD_PARTY_ONLY</code> (0.4&ndash;1.0%, floor Rp150k&ndash;850k).</td><td><b>Educ. Policy:</b> Guarantees <code>Comp &gt; TPO</code>.</td></tr>
    <tr><td><b>AMB-09</b></td><td>"Whether loadings stack"</td><td>Additive vs. multiplicative?</td><td>Additive sum via <code>COLLECT SUM</code> (<code>D08</code>): <code>Base * (1 + Sum(Loadings))</code>.</td><td><b>Technical Choice:</b> Transparent <code>C+</code> auditability.</td></tr>
    <tr><td><b>AMB-10</b></td><td>"Decline vs. Refer"</td><td>Can <code>REFER</code> auto-issue quote?</td><td><code>DECLINE</code> &gt; <code>REFER</code> &gt; <code>ACCEPT</code> in <code>D05</code>. Neither <code>DECLINE</code> nor unapproved <code>REFER</code> issues <code>finalPremium</code> (<code>null</code>).</td><td><b>Safety Control:</b> Preserves <code>D07</code>/<code>D08</code> for review.</td></tr>
    <tr><td><b>AMB-11</b></td><td>"Borderline &amp; invalid inputs"</td><td>Boundary inclusivity &amp; nulls?</td><td>Inclusive thresholds; future dates return <code>-1</code>; non-positive valuation <code>&le;0</code> rejected; null DOB &rarr; <code>UNKNOWN</code>.</td><td><b>Technical Choice:</b> Zero silent fall-throughs.</td></tr>
    <tr><td><b>AMB-12</b></td><td>Underwriting vs. Quote Readiness</td><td>Missing/blank/bad <code>coverType</code> or missing <code>insuredValue</code>?</td><td><code>D05</code> remains risk-only; <code>D10</code> yields <code>PENDING_INFORMATION</code> (<code>null</code>/<code>""</code>) or <code>INVALID_INPUT</code>; <code>D07</code>/<code>D09</code> return <code>null</code> (no <code>Rp0</code>).</td><td><b>Architectural Fix:</b> Added <code>D10</code>, updated <code>D03</code>/<code>D07</code>/<code>D09</code>.</td></tr>
  </tbody>
</table>

<h2>Appendix B &mdash; Decision Responsibility Summary (<code>D01</code>&ndash;<code>D10</code>) &amp; Data Dictionary</h2>
<table class="compact-tbl">
  <thead><tr><th style="width:7%">ID</th><th style="width:19%">Decision Name</th><th style="width:40%">What It Computes (One-Sentence Specification)</th><th style="width:17%">Inputs / Upstream</th><th style="width:17%">Output &amp; Type</th></tr></thead>
  <tbody>{''.join(resp_rows)}</tbody>
</table>
<table class="compact-tbl">
  <thead><tr><th>ID</th><th>Variable / Node</th><th>DMN TypeRef</th><th>Domain / Allowed Values</th><th>Missing / Edge Handling</th></tr></thead>
  <tbody>
    <tr><td><code>I01</code></td><td><code>dateOfBirth</code></td><td><code>date</code></td><td>ISO-8601 <code>YYYY-MM-DD</code> &le; <code>evaluationDate</code></td><td><code>null</code> &rarr; <code>D01=UNKNOWN</code>; future &rarr; <code>-1</code> &rarr; <code>INELIGIBLE</code></td></tr>
    <tr><td><code>I02</code></td><td><code>evaluationDate</code></td><td><code>date</code></td><td>ISO-8601 <code>YYYY-MM-DD</code></td><td><code>null</code> &rarr; <code>UNKNOWN</code> / <code>INELIGIBLE</code></td></tr>
    <tr><td><code>I03</code></td><td><code>claimsHistoryAvailable</code></td><td><code>boolean</code></td><td><code>true</code>, <code>false</code></td><td><code>false</code>/<code>null</code> &rarr; <code>D02=UNKNOWN</code> &rarr; <code>REFER</code></td></tr>
    <tr><td><code>I04</code></td><td><code>claimDates</code></td><td><code>tDateList</code></td><td>Collection of <code>date</code> (<code>[]</code> = clean if <code>I03=true</code>)</td><td><code>null</code> &rarr; <code>D02=UNKNOWN</code>; null items filtered</td></tr>
    <tr><td><code>I05</code></td><td><code>vehicleManufactureDate</code></td><td><code>date</code></td><td>ISO-8601 <code>YYYY-MM-DD</code> &le; <code>evaluationDate</code></td><td><code>null</code> or future &rarr; <code>D03=INELIGIBLE</code> &rarr; <code>DECLINE</code></td></tr>
    <tr><td><code>I06</code></td><td><code>vehicleType</code></td><td><code>tVehicleType</code></td><td><code>"MOTORCYCLE"</code>, <code>"CAR"</code></td><td>Outside enum / <code>null</code> &rarr; <code>D03=INELIGIBLE</code></td></tr>
    <tr><td><code>I07</code></td><td><code>engineCC</code></td><td><code>number</code></td><td>Numeric <code>&gt; 0</code> (cc)</td><td><code>null</code> or <code>&le; 0</code> &rarr; <code>D03=INELIGIBLE</code></td></tr>
    <tr><td><code>I08</code></td><td><code>performanceClass</code></td><td><code>tPerformanceClass</code></td><td><code>"STANDARD"</code>, <code>"SPORT"</code>, <code>"HIGH_PERFORMANCE"</code></td><td>Invalid/null &rarr; conservative fallback (<code>HIGH</code> / +30%)</td></tr>
    <tr><td><code>I09</code></td><td><code>coverType</code></td><td><code>tCoverType</code></td><td><code>"TPO"</code>, <code>"THIRD_PARTY_ONLY"</code>, <code>"COMPREHENSIVE"</code></td><td><code>null</code>/<code>""</code> &rarr; <code>D10=PENDING_INFORMATION</code>; unsupported &rarr; <code>INVALID_INPUT</code>; <code>D07=null</code></td></tr>
    <tr><td><code>I10</code></td><td><code>insuredValue</code></td><td><code>number</code></td><td>Numeric <code>&gt; 0</code> (IDR)</td><td><code>&le; 0</code> &rarr; <code>D03=INELIGIBLE</code>; <code>null</code> &rarr; <code>D10=PENDING_INFORMATION</code>, <code>D07=null</code></td></tr>
    <tr><td><code>BKM01</code></td><td><code>calculateAgeInYears</code></td><td><code>number</code></td><td><code>(targetDate, referenceDate) &rarr; int &ge; -1 | null</code></td><td>Calendar <code>years and months duration(...).years</code></td></tr>
    <tr><td><code>BKM02</code></td><td><code>countRecentClaims</code></td><td><code>number</code></td><td><code>(claimDates, referenceDate, windowMonths) &rarr; int &ge; 0 | null</code></td><td>Filter <code>[refDate - P24M, refDate]</code></td></tr>
  </tbody>
</table>

<div class="page-break"></div>
<h2>Appendix C &mdash; Rule Count Reconciliation &amp; Complete Decision Tables (10 Tables, {total_table_rules} Rules)</h2>
<p>Reconciles historical documentation (Stage 1: <code>73</code> rules; Stage 2 security/null hardening: <code>79</code> rules via <code>+1 D01</code>, <code>+4 D04</code>, <code>+1 D07</code>; Stage 5 architecture &amp; safety update: <b>{total_table_rules} decision table rules</b> + <b>{num_bkms} BKM FEEL functions</b> via <code>+12 D10</code> Quote Readiness and <code>+3 D09</code> safety gates):</p>
<table class="compact-tbl">
  <thead><tr><th>ID</th><th>Decision Name</th><th>Hit Policy</th><th>Stage 1</th><th>Stage 2</th><th>Stage 5 (Current)</th><th>Output &amp; TypeRef</th></tr></thead>
  <tbody>
    {''.join(recon_rows)}
    <tr style="font-weight:bold; background:#EEF4FB;"><td colspan="3">Total Decision Table Rules (+ 2 BKM FEEL Functions)</td><td>73</td><td>79</td><td>{total_table_rules} (+ 2 BKMs)</td><td>100% matched in XML &amp; Spec</td></tr>
  </tbody>
</table>
{''.join(dt_blocks)}

<div class="page-break"></div>
<h2>Appendix D &mdash; Complete FEEL Expressions &amp; <code>feelin@8.2.2</code> Validation Evidence (18/18 PASS)</h2>
<table class="compact-tbl">
  <thead><tr><th>ID</th><th>Category</th><th>FEEL Expression</th><th>Test Case &amp; Input Context</th><th>Expected</th><th>Actual</th><th>Status</th></tr></thead>
  <tbody>{''.join(feel_rows)}</tbody>
</table>
<div class="formula-box">
  <b>Duration Semantics Evidence (<code>feelin@8.2.2</code>):</b> On exact 25th birthday (<code>dob="2001-11-25"</code>, <code>evalDate="2026-11-25"</code>), days-and-time approximation <code>floor((date(evalDate) - date(dob)).days / 365.25)</code> returned <b>{res['durationPitfallVerification']['daysAndTimeAge']}</b> (off-by-one leap-year error), whereas calendar-aware <code>years and months duration(date(dob), date(evalDate)).years</code> returned <b>{res['durationPitfallVerification']['yearsAndMonthsAge']}</b>.
</div>

<h2>Appendix E &mdash; Canonical &amp; Regression End-to-End Traces (<code>TC-01</code>&ndash;<code>TC-{e2e_total}</code>) &amp; Stage 2 Adversarial Suite</h2>
<p>All <b>{e2e_total}</b> canonical/regression scenarios below (<code>validate_all.js</code>, including <code>TC-16</code> &amp; <code>TC-19</code> proving <code>insuredValue=null</code> keeps inspection <code>REQUIRED</code> rather than silently <code>NOT_REQUIRED</code>) and all <b>{ind_total}</b> combined XML-driven scenarios (<code>TC-01</code>&ndash;<code>TC-{ind_total}</code> in <code>independent_dmn_executor.js</code>, preserving Stage 2 adversarial cases as <code>TC-20</code>&ndash;<code>TC-27</code>) achieved <b>{ind_passed} / {ind_total} PASS</b> with <b>0 FEEL warnings</b> and exact match against independent pure-JS arithmetic checks.</p>
<table class="compact-tbl">
  <thead><tr><th>Case</th><th>Input Profile</th><th>Tier 1 (D01/D02/D03/D04)</th><th>D05, D06 &amp; D10</th><th>Pricing (D07 / D08 / D09)</th><th>Matched Rules</th><th>Result</th></tr></thead>
  <tbody>{''.join(e2e_rows)}</tbody>
</table>

<h2>Appendix F &mdash; XML, XSD, <code>dmn-js</code> Verification &amp; Execution Method Audit</h2>
<p><b>XML, XSD &amp; DAG Verification:</b> <code>defusedxml 0.7.1</code> + <code>lxml 6.1.1</code> + <code>networkx 3.6.1</code> verified well-formed OMG DMN 1.3 XML (<code>https://www.omg.org/spec/DMN/20191111/MODEL/</code>, <b>0 errors against official <code>DMN13.xsd</code></b>), 11 <code>itemDefinition</code>s, 10 <code>inputData</code>, 2 BKMs, 3 <code>knowledgeSource</code>s, 10 decisions, <b>{total_table_rules} decision table rules</b>, 881 unique IDs, 25 non-overlapping DMNDI shapes, 62 DMNDI edges, 0 broken refs, and <code>isDAG = true</code>. <code>dmn-moddle@12.2.1</code> loaded the DMN with <b>0 warnings</b> and <code>dmn-js@18.1.0</code> rendered the complete 5-tier DRD (Figure F1).</p>
<p><b>Execution Harness Audit (Option C — Hybrid Test Harness):</b> Because neither desktop Camunda Modeler nor a Java Camunda DMN Engine runtime is installed locally, <code>dmn-js@18.1.0</code> proves diagram interchange only. End-to-end execution uses two Node.js hybrid harnesses pairing <code>dmn-moddle@12.2.1</code> XML parsing with genuine <b><code>feelin@8.2.2</code></b> FEEL/unary evaluation: <code>validate_all.js</code> runs fixed topological order over 18 canonical cases, while <code>independent_dmn_executor.js</code> dynamically resolves topological order via Kahn's algorithm, binds BKM formal parameters, checks enum <code>allowedValues</code>, enforces 0 warnings, and cross-verifies <code>null</code>/rounded IDR arithmetic across all 26 cases. Limitation: boxed contexts, relation literals, and rule/output-order sorting extensions outside the modeled tables are not exercised.</p>
<div class="fig-box">
  <img src="{esc(dmnjs_rel)}" alt="dmn-js 18.1.0 DRD Verification Render" style="max-height:66mm;" />
  <div class="caption">Figure F1: Live verification render of <code>{esc(dmn_label)}</code> in <code>dmn-js@18.1.0</code> (warnings=0, 25 shapes, 62 edges, view=drd).</div>
</div>

<h2>Appendix G &mdash; Academic Integrity &amp; Truthful AI-Assistance Disclosure</h2>
<p>In strict compliance with FTI UKSW academic integrity rules and AI102 Homework-02 Section 7, generative AI assistance was utilized transparently during development as follows: <b>ChatGPT</b> assisted with initial assignment interpretation, decision-architecture discussion, business-rule edge critique, agent instruction design, and technical review; and the <b>Antigravity AI coding assistant</b> assisted with canonical specification synchronization, DMN 1.3 XML generation scripting, automated <code>feelin@8.2.2</code>/<code>dmn-moddle</code>/<code>dmn-js</code> validation harness implementation, regression testing, defect diagnosis, validation interpretation, and HTML-to-PDF typesetting. No human reviews or unsupported tool executions are claimed beyond the recorded automated logs. All domain assumptions, illustrative tariffs, independent expected outcomes, validation evidence verification, and final academic accountability remain exclusively the responsibility of the authors: <b>{esc(a1_name)}</b> ({esc(a1_nim)}) and <b>{esc(a2_name)}</b> ({esc(a2_nim)}).</p>

</body>
</html>
"""

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html_doc, encoding="utf-8")
    cmd = [
        EDGE,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUT_PDF}",
        OUT_HTML.as_uri(),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0 and OUT_PDF.exists():
        SUBMISSION_PDF.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(OUT_PDF, SUBMISSION_PDF)
        sub_dmn = ROOT / "submission" / dmn_label
        zip_name = dmn_label.replace(".dmn", "_Submission.zip")
        zip_path = ROOT / "submission" / zip_name
        if sub_dmn.exists():
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                zf.write(sub_dmn, arcname=dmn_label)
                zf.write(SUBMISSION_PDF, arcname=SUBMISSION_PDF.name)
            print("ZIP rebuilt:", zip_path, "size:", zip_path.stat().st_size)
    print("HTML written:", OUT_HTML)
    print("PDF compile exit:", proc.returncode, "exists:", OUT_PDF.exists(), "size:", OUT_PDF.stat().st_size if OUT_PDF.exists() else 0)


if __name__ == "__main__":
    build()
