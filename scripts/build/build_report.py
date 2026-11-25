import html
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "src" / "specification" / "CANONICAL_DECISION_SPECIFICATION.json"
RES_PATH = ROOT / "tests" / "test-results" / "TEST_RESULTS.json"
DRD_IMG = ROOT / "outputs" / "diagrams" / "DRD_DIAGRAM.png"
DMNJS_IMG = ROOT / "tests" / "validation-evidence" / "dmnjs_drd_verify.png"
OUT_HTML = ROOT / "reports" / "final-report" / "AI102_HW02_AsuransiNusantara_Report.html"
OUT_PDF = ROOT / "reports" / "final-report" / "AI102_HW02_AsuransiNusantara_Report.pdf"
SUBMISSION_PDF = ROOT / "submission" / "AI102_HW02_AsuransiNusantara_Report.pdf"
IDENTITY_PATH = ROOT / ".submission_identity.json"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def esc(val):
    return html.escape(str(val))


def fmt_idr(v):
    if v is None:
        return "null"
    return f"Rp{int(round(v)):,}"


def build():
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    res = json.loads(RES_PATH.read_text(encoding="utf-8"))
    ident = {"dmnFilename": "AsuransiNusantara.dmn", "authors": [{"name": "Author 1", "nim": "LOCAL"}, {"name": "Author 2", "nim": "LOCAL"}]}
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

    # Build Decision Tables HTML for Appendix C
    dt_blocks = []
    for dec in spec["decisions"]:
        hp = dec["hitPolicy"] + (f" ({dec['aggregation']})" if "aggregation" in dec else "")
        headers = "".join(f"<th>{esc(inp['label'])}<br/><span class='subth'>{esc(inp['expression'])}</span></th>" for inp in dec["inputs"])
        rows_html = []
        for r in dec["rules"]:
            cells = "".join(f"<td><code>{esc(c)}</code></td>" for c in r["inputs"])
            rows_html.append(
                f"<tr><td><b>{esc(r['id'])}</b></td>{cells}<td><code>{esc(r['output'])}</code></td><td>{esc(r['annotation'])}</td></tr>"
            )
        dt_blocks.append(f"""
        <div class="avoid-break">
          <h3>{esc(dec['id'])}: {esc(dec['label'])} &mdash; Hit Policy: <code>{esc(hp)}</code> | Output: <code>{esc(dec['outputName'])}: {esc(dec['outputTypeRef'])}</code></h3>
          <table class="compact-tbl">
            <thead><tr><th style="width:11%">Rule ID</th>{headers}<th>{esc(dec['outputName'])}</th><th style="width:28%">Business Annotation</th></tr></thead>
            <tbody>{''.join(rows_html)}</tbody>
          </table>
        </div>
        """)

    # Build FEEL validation rows for Appendix D
    feel_rows = []
    for expr in res["feelValidation"]["expressions"]:
        for idx, t in enumerate(expr["tests"]):
            status = "<span class='pass'>PASS</span>" if t["pass"] else "<span class='fail'>FAIL</span>"
            edge_lbl = " [Edge]" if t["isEdgeCase"] else ""
            feel_rows.append(
                f"<tr><td><b>{esc(expr['id'])}</b></td><td>{esc(expr['category'])}</td>"
                f"<td><code>{esc(expr['expression'])}</code></td>"
                f"<td>{esc(t['name'])}{edge_lbl}<br/><span class='muted'><code>{esc(json.dumps(t['context']))}</code></span></td>"
                f"<td><code>{esc(t['expected'])}</code></td><td><code>{esc(t['actual'])}</code></td><td>{status}</td></tr>"
            )

    # Build 10 E2E rows for Appendix E
    e2e_rows = []
    for tc in res["endToEndValidation"]["cases"]:
        a = tc["actual"]
        status = "<span class='pass'>PASS</span>" if tc["pass"] else "<span class='fail'>FAIL</span>"
        rules_str = ", ".join(f"{k}:{'+'.join(v['matchedRuleIds'])}" for k, v in tc["trace"].items())
        e2e_rows.append(
            f"<tr><td><b>{esc(tc['id'])}</b><br/><span class='muted'>{esc(tc['category'])}</span></td>"
            f"<td>Age {esc(a['driverAge'])}; Clm {esc(a['recentClaimsCount'])} (avail={esc(tc['inputs']['claimsHistoryAvailable'])}); "
            f"{esc(tc['inputs']['vehicleType'])} {esc(tc['inputs']['engineCC'])}cc ({esc(tc['inputs']['performanceClass'])}); "
            f"VehAge {esc(a['vehicleAge'])}; {esc(tc['inputs']['coverType'])}; {fmt_idr(tc['inputs']['insuredValue'])}</td>"
            f"<td>{esc(a['driverRisk'])} / {esc(a['claimsRisk'])} / {esc(a['vehicleEligibility'])} / {esc(a['vehicleRisk'])}</td>"
            f"<td><b>{esc(a['underwritingDecision'])}</b><br/>Insp: {esc(a['inspectionDecision'])}</td>"
            f"<td>Base: {fmt_idr(a['basePremium'])}<br/>Load: +{int(round(a['totalRiskLoading']*100))}%<br/><b>Final: {fmt_idr(a['finalPremium'])}</b></td>"
            f"<td><span class='tiny-code'>{esc(rules_str)}</span></td><td>{status}</td></tr>"
        )

    # Build main-text representative 4-case trace rows (TC-01, TC-02, TC-03, TC-04) + TC-05/06 note
    main_tc_rows = []
    for tc_id in ["TC-01", "TC-02", "TC-03", "TC-04", "TC-05", "TC-06"]:
        tc = next(c for c in res["endToEndValidation"]["cases"] if c["id"] == tc_id)
        a = tc["actual"]
        main_tc_rows.append(
            f"<tr><td><b>{esc(tc['id'])}</b></td><td>{esc(tc['category'])}</td>"
            f"<td>Age {esc(a['driverAge'])}, Clm {esc(a['recentClaimsCount'])} ({'avail' if tc['inputs']['claimsHistoryAvailable'] else 'missing'}), "
            f"{esc(tc['inputs']['vehicleType'][:2])} {esc(tc['inputs']['engineCC'])}cc, Veh {esc(a['vehicleAge'])}y, {esc(tc['inputs']['coverType'][:4])}, {fmt_idr(tc['inputs']['insuredValue'])}</td>"
            f"<td>{esc(a['driverRisk'])}</td><td>{esc(a['claimsRisk'])}</td><td>{esc(a['vehicleEligibility'][:4])}.</td><td>{esc(a['vehicleRisk'])}</td>"
            f"<td><b>{esc(a['underwritingDecision'])}</b></td><td>{esc(a['inspectionDecision'])}</td>"
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
    margin: 15mm 13mm 15mm 13mm;
    @top-left {{
      content: "AI102 Decision Intelligence (3 SKS) — Master of Artificial Intelligence, FTI UKSW";
      font-family: Arial, Helvetica, sans-serif;
      font-size: 7pt;
      color: #4A5568;
      border-bottom: 0.5pt solid #CBD5E1;
      padding-bottom: 2pt;
    }}
    @top-right {{
      content: "Homework-02: DMN 1.3 (Scenario B)";
      font-family: Arial, Helvetica, sans-serif;
      font-size: 7pt;
      color: #1B365D;
      font-weight: bold;
      border-bottom: 0.5pt solid #CBD5E1;
      padding-bottom: 2pt;
    }}
    @bottom-left {{
      content: "{esc(footer_left)}";
      font-family: Arial, Helvetica, sans-serif;
      font-size: 6.7pt;
      color: #4A5568;
      border-top: 0.5pt solid #CBD5E1;
      padding-top: 2pt;
    }}
    @bottom-right {{
      content: "Page " counter(page) " of " counter(pages);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 7pt;
      color: #1B365D;
      font-weight: bold;
      border-top: 0.5pt solid #CBD5E1;
      padding-top: 2pt;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Times New Roman", Times, serif;
    font-size: 9pt;
    line-height: 1.32;
    color: #1A202C;
    margin: 0;
    padding: 0;
    text-align: justify;
  }}
  .header-block {{
    border-bottom: 1.5pt solid #1B365D;
    padding-bottom: 5pt;
    margin-bottom: 6pt;
    text-align: left;
  }}
  .kicker {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 7.5pt;
    font-weight: bold;
    color: #2B5B9E;
    letter-spacing: 0.4pt;
    text-transform: uppercase;
    margin-bottom: 2pt;
  }}
  h1.doc-title {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 13.5pt;
    font-weight: bold;
    color: #1B365D;
    text-align: center;
    margin: 2pt 0 4pt 0;
    line-height: 1.2;
  }}
  .meta-grid {{
    width: 100%;
    border-collapse: collapse;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 7.3pt;
    background: #F4F7FB;
    border: 0.6pt solid #CBD5E1;
  }}
  .meta-grid td {{
    padding: 2pt 5pt;
    border: 0.4pt solid #CBD5E1;
    vertical-align: top;
    text-align: left;
  }}
  .meta-lbl {{ font-weight: bold; color: #1B365D; width: 16%; }}
  h2 {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 9.8pt;
    font-weight: bold;
    text-transform: uppercase;
    color: #1B365D;
    border-bottom: 0.9pt solid #1B365D;
    margin: 6pt 0 3.5pt 0;
    padding-bottom: 1.5pt;
    text-align: left;
    page-break-after: avoid;
  }}
  h3 {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 8.6pt;
    font-weight: bold;
    color: #2B5B9E;
    margin: 5pt 0 2.5pt 0;
    text-align: left;
    page-break-after: avoid;
  }}
  p {{ margin: 0 0 3.5pt 0; }}
  ul {{ margin: 2pt 0 4pt 14pt; padding: 0; }}
  li {{ margin-bottom: 1.5pt; }}
  code {{
    font-family: Consolas, "Courier New", monospace;
    font-size: 7.4pt;
    background: #F1F5F9;
    padding: 0.5pt 2pt;
    border-radius: 1.5pt;
  }}
  .fig-box {{
    text-align: center;
    border: 0.6pt solid #CBD5E1;
    background: #FFFFFF;
    padding: 3pt;
    margin: 3.5pt 0 4pt 0;
    page-break-inside: avoid;
  }}
  .fig-box img {{
    max-width: 100%;
    max-height: 76mm;
    height: auto;
    display: block;
    margin: 0 auto;
  }}
  .caption {{
    font-family: "Times New Roman", Times, serif;
    font-style: italic;
    font-size: 7.5pt;
    color: #4A5568;
    text-align: center;
    margin-top: 2pt;
  }}
  table.compact-tbl {{
    width: 100%;
    border-collapse: collapse;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 7.2pt;
    line-height: 1.22;
    margin: 3pt 0 4pt 0;
    text-align: left;
  }}
  table.compact-tbl thead {{ display: table-header-group; }}
  table.compact-tbl th {{
    background: #1B365D;
    color: #FFFFFF;
    font-weight: bold;
    padding: 2.5pt 4pt;
    border: 0.4pt solid #1B365D;
    vertical-align: bottom;
  }}
  table.compact-tbl th code {{
    background: rgba(255, 255, 255, 0.18);
    color: #FFFFFF;
  }}
  table.compact-tbl td {{
    padding: 2pt 4pt;
    border: 0.4pt solid #CBD5E1;
    vertical-align: top;
  }}
  table.compact-tbl tbody tr:nth-child(even) {{ background: #F8FAFC; }}
  .subth {{ font-weight: normal; font-size: 6.4pt; color: #DBEAFE; }}
  .formula-box {{
    background: #F4F7FB;
    border-left: 2.5pt solid #1B365D;
    padding: 3pt 6pt;
    margin: 3pt 0 4pt 0;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 8pt;
    text-align: left;
  }}
  .two-col {{
    display: flex;
    gap: 8pt;
    align-items: flex-start;
  }}
  .col-half {{ flex: 1; }}
  .page-break {{ page-break-before: always; }}
  .avoid-break {{ page-break-inside: avoid; }}
  .pass {{ color: #166534; font-weight: bold; }}
  .fail {{ color: #991B1B; font-weight: bold; }}
  .muted {{ color: #4A5568; font-size: 6.8pt; }}
  .tiny-code {{ font-family: Consolas, monospace; font-size: 6.3pt; color: #334155; }}
  .pending {{ color: #9A3412; font-weight: bold; }}
</style>
</head>
<body>

<!-- ==================== PAGE 1-3: MAIN REPORT (STRICTLY <= 3 PAGES) ==================== -->
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
      <td class="meta-lbl">Model File</td><td><code>{esc(dmn_label)}</code> (DMN 1.3 XML, 79 rules, 2 BKMs)</td>
    </tr>
  </table>
</div>

<h2>1. Model Overview &amp; Decision Requirements Diagram (DRD)</h2>
<p>We formalize motor underwriting for <b>AsuransiNusantara</b> as a deterministic, two-tiered OMG DMN 1.3 decision model separating structural dependencies (DRD) from executable tabular and FEEL logic (Taylor &amp; Purchase, 2019). From ten explicit inputs (<code>I01</code>&ndash;<code>I10</code>, including an explicit <code>evaluationDate</code> to eliminate system-clock non-determinism), the model evaluates nine decisions (<code>D01</code>&ndash;<code>D09</code>) supported by two reusable Business Knowledge Models (<code>BKM01</code>, <code>BKM02</code>) and three Knowledge Sources (<code>KS01</code>&ndash;<code>KS03</code>). All 35 information requirements, 5 knowledge requirements, and 13 authority requirements form a verified 4-tier directed acyclic graph (DAG) in which every decision receives at least two information requirements (Figure 1).</p>

<div class="fig-box">
  <img src="{esc(drd_rel)}" alt="DMN 1.3 DRD for AsuransiNusantara" />
  <div class="caption">Figure 1: Complete 4-tier DMN 1.3 Decision Requirements Diagram (DRD) for Scenario B (10 inputs, 2 BKMs, 3 Knowledge Sources, 9 decisions, 53 typed edges).</div>
</div>

<h2>2. Decision Decomposition Rationale</h2>
<p>Rather than collapsing underwriting into a single opaque matrix (5 &times; 4 &times; 2 &times; 3 = 120+ combinations), decomposition isolates orthogonal concerns across four tiers: (1) <b>Independent Risk &amp; Eligibility Assessment (Tier 1)</b> separates driver age risk (<code>D01</code>), claims recency risk (<code>D02</code>), hard vehicle eligibility (<code>D03</code>), technical vehicle risk (<code>D04</code>), and base tariff pricing (<code>D07</code>). Splitting <code>D03</code> from <code>D04</code> guarantees that vehicles older than 15 years or with invalid inputs are rejected unconditionally rather than traded off against low driver risk. (2) <b>Disposition &amp; Additive Loading (Tier 2)</b> aggregates <code>D01</code>&ndash;<code>D04</code> in <code>D05</code> under strict precedence, while <code>D08</code> sums independent surcharge components. (3) <b>Downstream Gating (Tier 3)</b> wires <code>D05</code> directly into <code>D06</code> (Inspection) and <code>D09</code> (Final Premium) so declined policies yield <code>NOT_APPLICABLE</code> and <code>Rp0</code>. Reusable date logic is centralized in <code>BKM01</code> and <code>BKM02</code> to prevent duplicated duration formulas.</p>

<h2>3. Summary of Narrative Ambiguity Resolution</h2>
<p>All numerical thresholds, tariff rates, and loading percentages below are <b>illustrative educational assumptions</b> (not commercial OJK actuarial tariffs) established to make every fuzzy narrative clause executable and auditable (full 11-item register in Appendix A):</p>

<table class="compact-tbl">
  <thead>
    <tr><th style="width:9%">ID</th><th style="width:23%">Ambiguous Narrative Term</th><th style="width:36%">Adopted Educational Threshold / Rule</th><th style="width:32%">Business Rationale</th></tr>
  </thead>
  <tbody>
    <tr><td><b>AMB-01</b></td><td>"Young drivers" &amp; min/max age</td><td><code>&lt;17</code>: <code>INELIGIBLE</code>; <code>[17..24]</code>: <code>HIGH</code> (+25%); <code>[25..65]</code>: <code>LOW</code>; <code>&gt;65</code>: <code>MEDIUM</code> (+10%); null: <code>UNKNOWN</code>.</td><td>Aligns with Indonesian SIM A/C minimum age (17) and standard age-curve risk.</td></tr>
    <tr><td><b>AMB-02/03</b></td><td>"Recent claims" &amp; missing history</td><td>24-month inclusive window <code>[evalDate - P24M, evalDate]</code>: 0&rarr;<code>LOW</code>, 1&rarr;<code>MEDIUM</code> (+20%), &ge;2&rarr;<code>HIGH</code> (+40%, <code>REFER</code>). <code>claimsHistoryAvailable!=true</code>&rarr;<code>UNKNOWN</code> (<code>REFER</code>, +25%).</td><td>Prevents adverse selection by never equating unavailable history with a clean record.</td></tr>
    <tr><td><b>AMB-04</b></td><td>"Very old vehicles... decline"</td><td>Completed vehicle age <code>&gt;15</code> yrs &rarr; <code>INELIGIBLE</code> (<code>DECLINE</code>); <code>[11..15]</code> yrs elevates <code>D04</code> to &ge;<code>MEDIUM</code>.</td><td>Parts obsolescence and moral hazard rise sharply after 15 years.</td></tr>
    <tr><td><b>AMB-05</b></td><td>"Very high value means inspection"</td><td><code>DECLINE</code>&rarr;<code>NOT_APPLICABLE</code>; else <code>REQUIRED</code> if <code>insuredValue &ge; Rp500M</code> (any cover) OR (<code>COMPREHENSIVE</code> and <code>age &gt; 10</code>).</td><td>Protects against valuation fraud on high-value assets and pre-existing damage.</td></tr>
    <tr><td><b>AMB-06/07</b></td><td>"Sporty" &amp; motorcycle engine size</td><td><code>performanceClass</code> &isin; {{<code>STANDARD</code>, <code>SPORT</code> (+15%), <code>HIGH_PERFORMANCE</code> (+30%)}}. MC bands: <code>(0..150]</code>, <code>(150..250]</code>, <code>&gt;250</code>cc; Car: <code>(0..1500]</code>, <code>(1500..2500]</code>, <code>&gt;2500</code>cc.</td><td>Separates motorcycle vs. car displacement physics; prevents cross-class distortion.</td></tr>
    <tr><td><b>AMB-08/09</b></td><td>Cover pricing &amp; loading stacking</td><td>Comprehensive rates (1.8%&ndash;3.2%, floor Rp300k&ndash;2.5M) strictly exceed TPO (0.4%&ndash;1.0%, floor Rp150k&ndash;850k). Loadings stack <b>additively</b> via <code>C+</code>.</td><td>Guarantees <code>Comp &gt; TPO</code> for all positive values and transparent surcharge stacking.</td></tr>
    <tr><td><b>AMB-10/11</b></td><td>Decline vs. Refer &amp; boundaries</td><td>Strict <code>FIRST</code> hierarchy: <code>DECLINE &gt; REFER &gt; ACCEPT</code>. Inclusive bounds (<code>24</code> young, <code>15</code> eligible, <code>Rp500M</code> inspect) and null guards.</td><td>Eliminates off-by-one ambiguity and ensures ineligible inputs never accept.</td></tr>
  </tbody>
</table>

<h2>4. Decision Table Design, Hit-Policy Rationale &amp; Trace Results</h2>
<p>All nine decision tables (79 rules total; Appendix C) guarantee <b>zero silent fall-throughs</b>. <code>D01</code> (Driver Risk) and <code>D09</code> (Final Premium) use <b><code>UNIQUE (U)</code></b> because their intervals/enums are strictly disjoint. <code>D02</code>&ndash;<code>D07</code> use <b><code>FIRST (F)</code></b> to enforce explicit priority ordering: <code>D02</code> guards missing history before counting claims; <code>D03</code> short-circuits invalid/old vehicles; <code>D04</code> resolves overlapping technical risks upward (<code>HIGH &gt; MEDIUM &gt; LOW</code>); <code>D05</code> enforces <code>DECLINE &gt; REFER &gt; ACCEPT</code>; <code>D06</code> short-circuits declined risks before inspection triggers; and <code>D07</code> includes a defensive fallback row. <code>D08</code> uses <b><code>COLLECT SUM (C+)</code></b> across four orthogonal dimensions (4 hits always) to implement:</p>
<div class="formula-box"><b>Additive Pricing Formula:</b> &nbsp; <code>finalPremium = decimal(basePremium * (1 + totalRiskLoading), 0)</code> &nbsp; (if <code>D05 &isin; {{ACCEPT, REFER}}</code>; else <code>0</code>)</div>

<table class="compact-tbl">
  <thead>
    <tr><th>Case</th><th>Profile</th><th>Key Inputs (<code>evalDate = 2026-11-25</code>)</th><th>D01</th><th>D02</th><th>D03</th><th>D04</th><th>D05</th><th>D06</th><th>D07 (Base)</th><th>D08</th><th>D09 (Final)</th></tr>
  </thead>
  <tbody>{''.join(main_tc_rows)}</tbody>
</table>
<div class="caption">Table 1: Representative end-to-end traces executed against <code>{esc(dmn_label)}</code> (full 10-case trace including <code>TC-07..TC-10</code> in Appendix E).</div>

<h2>5. FEEL Expressions, Engine Validation &amp; Defect Resolution</h2>
<p>Six distinct FEEL expressions covering all five required categories passed <b>15 / 15</b> unit tests and <b>10 / 10</b> end-to-end DMN cases in <code>feelin@8.2.2</code> + <code>dmn-moddle@12.2.1</code> (0 warnings), with <code>dmn-js@18.1.0</code> visually verifying all 24 DRD shapes and 53 edges (Table 2; full cases in Appendix D). Probing <code>feelin</code> confirmed why <code>years and months duration(dob, evalDate).years</code> is essential: naive days-and-time arithmetic <code>floor((evalDate - dob).days / 365.25)</code> returns <code>24</code> instead of <code>25</code> on exact 25th birthday <code>2001-11-25</code> (<code>9131 / 365.25 = 24.9993</code>). Validation also caught and fixed three real defects: (1) normative DMN 1.3 namespace requires <code>https://</code> rather than <code>http://</code> for <code>dmn-moddle</code>/Camunda compatibility; (2) unparenthesized <code>in ... and ...</code> in <code>FEEL-02</code> returned <code>null</code> until parenthesized; and (3) IEEE-754 float <code>200M * 0.018 = 3,599,999.9999999995</code> caused a Rp1 <code>floor()</code> truncation bug in <code>TC-10</code>, resolved via <code>decimal(..., 0)</code>.</p>

<table class="compact-tbl">
  <thead>
    <tr><th style="width:8%">ID</th><th style="width:20%">FEEL Category</th><th style="width:45%">Canonical Expression (Executed in <code>feelin@8.2.2</code>)</th><th style="width:27%">Sample &amp; Edge Verification</th></tr>
  </thead>
  <tbody>
    <tr><td><b>FEEL-01</b></td><td>Range condition (interval)</td><td><code>driverAge in [17..24]</code></td><td>17&rarr;<code>true</code>, 24&rarr;<code>true</code>, 25&rarr;<code>false</code> (3/3 PASS)</td></tr>
    <tr><td><b>FEEL-02</b></td><td>List membership</td><td><code>(vehicleType in ["MOTORCYCLE","CAR"]) and (performanceClass in ["SPORT","HIGH_PERFORMANCE"])</code></td><td>MC+SPORT&rarr;<code>true</code>, TRUCK&rarr;<code>false</code> (2/2 PASS)</td></tr>
    <tr><td><b>FEEL-03</b></td><td>Built-in functions</td><td><code>decimal(max(450000, insuredValue * 0.025) * (1 + totalRiskLoading), 0)</code></td><td>10M@35%&rarr;<code>607500</code>, 40M@35%&rarr;<code>1350000</code> (2/2 PASS)</td></tr>
    <tr><td><b>FEEL-04</b></td><td>Date/duration (age)</td><td><code>if date(targetDate) &gt; date(referenceDate) then -1 else years and months duration(date(targetDate), date(referenceDate)).years</code></td><td><code>2001-11-25</code>&rarr;<code>25</code>, <code>11-26</code>&rarr;<code>24</code>, future&rarr;<code>-1</code> (3/3 PASS)</td></tr>
    <tr><td><b>FEEL-05</b></td><td>Date/duration + <code>count</code></td><td><code>count(claimDates[date(item) &gt;= (date(referenceDate) - duration("P24M")) and date(item) &lt;= date(referenceDate)])</code></td><td><code>["2024-11-25","2024-11-24"]</code>&rarr;<code>1</code>, <code>[]</code>&rarr;<code>0</code> (2/2 PASS)</td></tr>
    <tr><td><b>FEEL-06</b></td><td>Compound <code>if/else</code> + logic</td><td><code>if vehicleEligibility="INELIGIBLE" or driverRisk="INELIGIBLE" then "DECLINE" else if claimsRisk="UNKNOWN" ... then "REFER" else "ACCEPT"</code></td><td>Ineligible&rarr;<code>DECLINE</code>, Unknown&rarr;<code>REFER</code>, Clean&rarr;<code>ACCEPT</code> (3/3 PASS)</td></tr>
  </tbody>
</table>
<div class="caption">Table 2: Summary of validated FEEL expressions covering all five required DMN categories (15/15 PASS in <code>feelin@8.2.2</code>).</div>

<h2>6. Known Limitations &amp; Machine-Learning Integration (Session 03)</h2>
<p><b>Limitations:</b> (1) Rates and thresholds are illustrative educational assumptions rather than actuarially calibrated claim-severity tables; (2) <code>performanceClass</code> relies on manual/external vehicle lookup; and (3) standalone desktop Camunda Modeler was not installed locally, so editor verification relied on Camunda's underlying <code>dmn-js@18.1.0</code> engine and official OMG <code>DMN13.xsd</code> validation. <b>ML Integration (Session 03):</b> Rather than replacing transparent underwriting gates, a calibrated ML claim-propensity score <i>p</i> &isin; [0, 1] (Pratt &amp; Malcolm, 2023; Molnar, 2024) can be integrated cleanly either as an <code>inputData</code> node feeding <code>D05</code> (referring borderline low-rule-risk cases where <i>p</i> &ge; &tau;<sub>refer</sub>) or encapsulated inside a <code>BKM</code> scorecard so deterministic statutory rules (age &lt;17, vehicle &gt;15 yrs) retain absolute override authority.</p>

<div class="two-col">
  <div class="col-half" style="flex:1.25;">
    <h2>7. Division of Labor</h2>
    <table class="compact-tbl">
      <thead><tr><th style="width:37%">Name &amp; NIM</th><th style="width:63%">Assigned Responsibilities</th></tr></thead>
      <tbody>
        <tr>
          <td><b>{esc(a1_name)}</b><br/>{esc(a1_nim)}</td>
          <td>Scenario elicitation, business requirements integration, DRD architecture, canonical decision specification, DMN 1.3 XML generation, and final technical integration.</td>
        </tr>
        <tr>
          <td><b>{esc(a2_name)}</b><br/>{esc(a2_nim)}</td>
          <td>Ambiguity register, data dictionary, decision tables (<code>D01</code>&ndash;<code>D09</code>), hit-policy analysis, FEEL expressions, validation case preparation, testing evidence, and academic report audit.</td>
        </tr>
      </tbody>
    </table>
    <div class="muted" style="margin-top:2pt;">Both authors reviewed the final model and validated the academic submission.</div>
  </div>
  <div class="col-half" style="flex:0.75;">
    <h2>8. Key References</h2>
    <p style="font-size:7.6pt; line-height:1.25; text-align:left;">
      1. OMG. (2021). <i>Decision Model and Notation (DMN) Specification v1.3</i>. Object Management Group.<br/>
      2. Pratt, L., &amp; Malcolm, N. (2023). <i>The Decision Intelligence Handbook</i>. O'Reilly Media.<br/>
      3. Taylor, J., &amp; Purchase, J. (2019). <i>Real-World Decision Modeling with DMN</i>. Meghan-Kiffer Press.<br/>
      4. Molnar, C. (2024). <i>Interpretable Machine Learning</i> (2nd ed.). Leanpub.<br/>
      5. Tooling: <code>feelin@8.2.2</code>, <code>dmn-moddle@12.2.1</code>, <code>dmn-js@18.1.0</code> (Node.js v24.15.0; Python 3.11.9).
    </p>
  </div>
</div>

<!-- ==================== APPENDICES (PAGE 4+) ==================== -->
<div class="page-break"></div>
<h2>Appendix A &mdash; Complete Ambiguity-Resolution Register (11 Items)</h2>
<table class="compact-tbl">
  <thead><tr><th style="width:7%">ID</th><th style="width:18%">Ambiguous Clause</th><th style="width:20%">Open Question</th><th style="width:30%">Selected Rule / Threshold</th><th style="width:25%">Justification &amp; Model Impact</th></tr></thead>
  <tbody>
    <tr><td><b>AMB-01</b></td><td>"Young drivers"</td><td>Age band &amp; min/senior limits?</td><td>&lt;17: <code>INELIGIBLE</code>; [17..24]: <code>HIGH</code> (+25%); [25..65]: <code>LOW</code>; &gt;65: <code>MEDIUM</code> (+10%); null: <code>UNKNOWN</code>.</td><td>UU 22/2009 SIM min 17; feeds <code>BKM01</code>, <code>D01</code>, <code>D05</code>, <code>D08</code>.</td></tr>
    <tr><td><b>AMB-02</b></td><td>"Recent claims"</td><td>Lookback window &amp; count tiers?</td><td><code>[evalDate - P24M, evalDate]</code>: 0&rarr;<code>LOW</code>; 1&rarr;<code>MEDIUM</code> (+20%); &ge;2&rarr;<code>HIGH</code> (+40%, <code>REFER</code>).</td><td>24-month behavioral window; feeds <code>BKM02</code>, <code>D02</code>, <code>D05</code>, <code>D08</code>.</td></tr>
    <tr><td><b>AMB-03</b></td><td>"Missing claims history"</td><td>Treat missing as 0 claims?</td><td><code>claimsHistoryAvailable != true</code> or <code>claimDates = null</code> &rarr; <code>UNKNOWN</code> &rarr; <code>REFER</code> + 25% provisional loading.</td><td>Prevents adverse selection; never equates missing with clean.</td></tr>
    <tr><td><b>AMB-04</b></td><td>"Very old vehicles"</td><td>Max insurable age &amp; aging tier?</td><td><code>vehicleAge &gt; 15</code> &rarr; <code>INELIGIBLE</code> (<code>DECLINE</code>); <code>[11..15]</code> elevates <code>D04</code> &ge; <code>MEDIUM</code>.</td><td>Parts obsolescence &amp; mechanical wear; feeds <code>D03</code>, <code>D04</code>, <code>D06</code>.</td></tr>
    <tr><td><b>AMB-05</b></td><td>"Very high value inspection"</td><td>IDR threshold &amp; TPO/Declined?</td><td><code>DECLINE</code>&rarr;<code>NOT_APPLICABLE</code>; else <code>REQUIRED</code> if <code>&ge;Rp500M</code> (all covers) or (<code>COMPREHENSIVE</code> &amp; <code>age&gt;10</code>).</td><td>Anti-fraud valuation check; feeds <code>D06</code>.</td></tr>
    <tr><td><b>AMB-06</b></td><td>"Sporty/high-performance"</td><td>How classified without spec DB?</td><td><code>STANDARD</code> (+0%), <code>SPORT</code> (&ge;<code>MEDIUM</code>, +15%), <code>HIGH_PERFORMANCE</code> (<code>HIGH</code>, +30%).</td><td>Separates sport trims from superbikes/supercars; feeds <code>D04</code>, <code>D08</code>.</td></tr>
    <tr><td><b>AMB-07</b></td><td>"Engine size, esp. motorcycles"</td><td>CC cutoffs per vehicle type?</td><td>MC: <code>(0..150]</code>, <code>(150..250]</code>, <code>&gt;250</code>; Car: <code>(0..1500]</code>, <code>(1500..2500]</code>, <code>&gt;2500</code>.</td><td>Prevents cross-class cc distortion; feeds <code>D04</code>, <code>D07</code>.</td></tr>
    <tr><td><b>AMB-08</b></td><td>"Comprehensive &gt; TPO"</td><td>Rate structure invariant?</td><td>Comp (1.8%&ndash;3.2%, floor Rp300k&ndash;2.5M) strictly exceeds TPO (0.4%&ndash;1.0%, floor Rp150k&ndash;850k) per tier.</td><td>Guarantees <code>Comp &gt; TPO</code> for all <code>insuredValue &gt; 0</code>.</td></tr>
    <tr><td><b>AMB-09</b></td><td>"Whether loadings stack"</td><td>Additive vs. multiplicative?</td><td>Additive sum via <code>COLLECT SUM</code> (<code>D08</code>): <code>Base * (1 + Sum(Loadings))</code>.</td><td>Transparent, non-explosive stacking; feeds <code>D08</code>, <code>D09</code>.</td></tr>
    <tr><td><b>AMB-10</b></td><td>"Decline vs. Refer"</td><td>Precedence &amp; compound rules?</td><td><code>DECLINE</code> (ineligible or 3x <code>HIGH</code>) &gt; <code>REFER</code> (<code>UNKNOWN</code>, <code>D02=HIGH</code>, <code>D01=HIGH &amp; (D04=HIGH|D02=MED)</code>) &gt; <code>ACCEPT</code>.</td><td>Enforces hard gates first via <code>FIRST</code> in <code>D05</code>.</td></tr>
    <tr><td><b>AMB-11</b></td><td>"Borderline &amp; invalid inputs"</td><td>Boundary inclusivity &amp; nulls?</td><td>Inclusive thresholds (<code>17</code>, <code>24</code>, <code>15</code>, <code>Rp500M</code>, <code>P24M</code>); future dates return <code>-1</code>; null/negative guards in all tables.</td><td>Zero silent fall-throughs; verified in <code>TC-02..TC-10</code>.</td></tr>
  </tbody>
</table>

<h2>Appendix B &mdash; Full Data Dictionary (10 Inputs, 2 BKMs, 9 Outputs)</h2>
<table class="compact-tbl">
  <thead><tr><th>ID</th><th>Variable / Node</th><th>DMN TypeRef</th><th>Domain / Allowed Values</th><th>Missing / Edge Handling</th></tr></thead>
  <tbody>
    <tr><td><code>I01</code></td><td><code>dateOfBirth</code></td><td><code>date</code></td><td>ISO-8601 <code>YYYY-MM-DD</code> &le; <code>evaluationDate</code></td><td><code>null</code> &rarr; <code>D01=UNKNOWN</code>; future &rarr; <code>-1</code> &rarr; <code>INELIGIBLE</code></td></tr>
    <tr><td><code>I02</code></td><td><code>evaluationDate</code></td><td><code>date</code></td><td>ISO-8601 <code>YYYY-MM-DD</code></td><td><code>null</code> &rarr; <code>UNKNOWN</code> / <code>INELIGIBLE</code></td></tr>
    <tr><td><code>I03</code></td><td><code>claimsHistoryAvailable</code></td><td><code>boolean</code></td><td><code>true</code>, <code>false</code></td><td><code>false</code>/<code>null</code> &rarr; <code>D02=UNKNOWN</code> &rarr; <code>REFER</code></td></tr>
    <tr><td><code>I04</code></td><td><code>claimDates</code></td><td><code>tDateList</code></td><td>Collection of <code>date</code> (<code>[]</code> = clean if <code>I03=true</code>)</td><td><code>null</code> &rarr; <code>D02=UNKNOWN</code></td></tr>
    <tr><td><code>I05</code></td><td><code>vehicleManufactureDate</code></td><td><code>date</code></td><td>ISO-8601 <code>YYYY-MM-DD</code> &le; <code>evaluationDate</code></td><td><code>null</code> or future &rarr; <code>D03=INELIGIBLE</code> &rarr; <code>DECLINE</code></td></tr>
    <tr><td><code>I06</code></td><td><code>vehicleType</code></td><td><code>tVehicleType</code></td><td><code>"MOTORCYCLE"</code>, <code>"CAR"</code></td><td>Outside enum / <code>null</code> &rarr; <code>D03=INELIGIBLE</code></td></tr>
    <tr><td><code>I07</code></td><td><code>engineCC</code></td><td><code>number</code></td><td>Numeric <code>&gt; 0</code> (cc)</td><td><code>null</code> or <code>&le; 0</code> &rarr; <code>D03=INELIGIBLE</code></td></tr>
    <tr><td><code>I08</code></td><td><code>performanceClass</code></td><td><code>tPerformanceClass</code></td><td><code>"STANDARD"</code>, <code>"SPORT"</code>, <code>"HIGH_PERFORMANCE"</code></td><td>Invalid/null &rarr; conservative fallback (+30% / <code>HIGH</code>)</td></tr>
    <tr><td><code>I09</code></td><td><code>coverType</code></td><td><code>tCoverType</code></td><td><code>"TPO"</code>, <code>"COMPREHENSIVE"</code></td><td>Invalid/null &rarr; <code>D07=0</code>, <code>D06=REQUIRED</code></td></tr>
    <tr><td><code>I10</code></td><td><code>insuredValue</code></td><td><code>number</code></td><td>Numeric <code>&gt; 0</code> (IDR)</td><td><code>null</code> or <code>&le; 0</code> &rarr; <code>D03=INELIGIBLE</code></td></tr>
    <tr><td><code>BKM01</code></td><td><code>calculateAgeInYears</code></td><td><code>number</code></td><td><code>(targetDate, referenceDate) &rarr; integer &ge; -1</code></td><td>Exact <code>years and months duration(...).years</code></td></tr>
    <tr><td><code>BKM02</code></td><td><code>countRecentClaims</code></td><td><code>number</code></td><td><code>(claimDates, referenceDate, windowMonths) &rarr; int &ge; 0</code></td><td>Filter <code>[refDate - P24M, refDate]</code></td></tr>
    <tr><td><code>D01..D09</code></td><td>Decision Outputs</td><td>Custom Enums &amp; <code>number</code></td><td><code>D01</code> (5), <code>D02</code> (4), <code>D03</code> (2), <code>D04</code> (3), <code>D05</code> (3), <code>D06</code> (3), <code>D07..D09</code> (<code>number</code>)</td><td>100% bounded with explicit fallback rows</td></tr>
  </tbody>
</table>

<div class="page-break"></div>
<h2>Appendix C &mdash; Complete Decision Tables (D01&ndash;D09, 79 Rules)</h2>
{''.join(dt_blocks)}

<div class="page-break"></div>
<h2>Appendix D &mdash; Complete FEEL Expressions &amp; <code>feelin@8.2.2</code> Validation Evidence</h2>
<table class="compact-tbl">
  <thead><tr><th>ID</th><th>Category</th><th>FEEL Expression</th><th>Test Case &amp; Input Context</th><th>Expected</th><th>Actual</th><th>Status</th></tr></thead>
  <tbody>{''.join(feel_rows)}</tbody>
</table>
<div class="formula-box">
  <b>Duration Semantics Evidence (<code>feelin@8.2.2</code>):</b> On exact 25th birthday (<code>dob="2001-11-25"</code>, <code>evalDate="2026-11-25"</code>), days-and-time approximation <code>floor((date(evalDate) - date(dob)).days / 365.25)</code> returned <b>{res['durationPitfallVerification']['daysAndTimeAge']}</b> (off-by-one leap-year error), whereas calendar-aware <code>years and months duration(date(dob), date(evalDate)).years</code> returned <b>{res['durationPitfallVerification']['yearsAndMonthsAge']}</b>.
</div>

<h2>Appendix E &mdash; Complete 10-Case End-to-End Execution Traces (<code>TC-01</code>&ndash;<code>TC-10</code>)</h2>
<table class="compact-tbl">
  <thead><tr><th>Case</th><th>Input Profile</th><th>Tier 1 (D01/D02/D03/D04)</th><th>D05 &amp; D06</th><th>Pricing (D07 / D08 / D09)</th><th>Matched Rules</th><th>Result</th></tr></thead>
  <tbody>{''.join(e2e_rows)}</tbody>
</table>

<h2>Appendix F &mdash; XML, DAG, <code>dmn-js</code> Verification &amp; Defect Log</h2>
<p><b>Automated Checks:</b> <code>defusedxml 0.7.1</code> + <code>lxml 6.1.1</code> + <code>networkx 3.6.1</code> confirmed well-formed DMN 1.3 XML (<code>https://www.omg.org/spec/DMN/20191111/MODEL/</code>) and <b>0 errors against official OMG <code>DMN13.xsd</code></b>, with 10 <code>itemDefinition</code>s, 10 <code>inputData</code>, 2 BKMs, 3 <code>knowledgeSource</code>s, 9 decisions, 79 rules, 24 DMNDI shapes, 53 DMNDI edges, 0 broken references, and <code>isDAG = true</code>. <code>dmn-moddle@12.2.1</code> deserialized the exported <code>.dmn</code> with <b>0 warnings</b>, and <code>dmn-js@18.1.0</code> rendered the complete DRD (Figure F1). Standalone desktop Camunda Modeler was not installed locally; <code>dmn-js</code> is Camunda Modeler's underlying DMN 1.3 renderer.</p>
<p><b>Defects Found &amp; Fixed:</b> (1) Normative DMN 1.3 requires <code>https://</code> namespace URI (<code>http://</code> rejected by <code>dmn-moddle</code>); (2) <code>BKM01</code> future-date check added (<code>&gt; referenceDate &rarr; -1</code>); (3) <code>FEEL-02</code> parenthesized around <code>in</code> clauses; (4) <code>decimal(..., 0)</code> applied in <code>D07</code>/<code>D09</code> to eliminate IEEE-754 Rp1 truncation on <code>200M * 0.018</code>.</p>
<div class="fig-box">
  <img src="{esc(dmnjs_rel)}" alt="dmn-js 18.1.0 DRD Verification Render" style="max-height:70mm;" />
  <div class="caption">Figure F1: Live verification screenshot of <code>{esc(dmn_label)}</code> rendered in <code>dmn-js@18.1.0</code> (warnings=0, view=drd).</div>
</div>

<h2>Appendix G &mdash; Academic Integrity &amp; AI-Assistance Disclosure</h2>
<p>In strict compliance with FTI UKSW academic integrity rules and AI102 Homework-02 Section 7, generative AI assistance (<b>Antigravity AI coding assistant</b>) was used during this project for requirements structuring, DMN 1.3 XML generation scripting, automated <code>feelin</code>/<code>dmn-moddle</code>/<code>dmn-js</code> validation harness development, defect diagnosis, and HTML-to-PDF typesetting. All modeling assumptions, ambiguity thresholds, illustrative tariff schedules, validation verification against <code>tests/test-results/TEST_RESULTS.json</code> and <code>tests/test-results/INDEPENDENT_EXECUTION_RESULTS.json</code>, and final academic accountability remain exclusively the responsibility of the authors: <b>{esc(a1_name)}</b> ({esc(a1_nim)}) and <b>{esc(a2_name)}</b> ({esc(a2_nim)}).</p>

</body>
</html>
"""

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
        shutil.copy2(OUT_PDF, SUBMISSION_PDF)
    print("HTML written:", OUT_HTML)
    print("PDF compile exit:", proc.returncode, "exists:", OUT_PDF.exists(), "size:", OUT_PDF.stat().st_size if OUT_PDF.exists() else 0)


if __name__ == "__main__":
    build()
