from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon

ROOT = Path(__file__).resolve().parents[2]
OUT_PNG = ROOT / "outputs" / "diagrams" / "DRD_DIAGRAM.png"

fig, ax = plt.subplots(figsize=(13.5, 6.4), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 56)
ax.axis("off")
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Palette aligned with ACADEMIC_REPORT_STYLE_GUIDE.md
NAVY = "#1B365D"
BLUE = "#2B5B9E"
LIGHT_DEC = "#EEF4FB"
LIGHT_INP = "#F4F6F9"
LIGHT_BKM = "#E8F4EE"
BKM_EDGE = "#1F6F4A"
LIGHT_KS = "#FFF7E6"
KS_EDGE = "#8C5A00"
TEXT_DARK = "#1A202C"

# Node definitions: (cx, cy, w, h, label)
INPUTS = {
    "I01": (5.5, 5.5, 8.6, 4.0, "I01\ndateOfBirth"),
    "I02": (15.0, 5.5, 9.0, 4.0, "I02\nevaluationDate"),
    "I03": (25.2, 5.5, 10.2, 4.0, "I03\nclaimsHistoryAvail."),
    "I04": (35.5, 5.5, 8.4, 4.0, "I04\nclaimDates"),
    "I05": (45.8, 5.5, 10.4, 4.0, "I05\nvehicleMfgDate"),
    "I06": (56.0, 5.5, 8.2, 4.0, "I06\nvehicleType"),
    "I07": (65.2, 5.5, 8.2, 4.0, "I07\nengineCC"),
    "I08": (74.8, 5.5, 9.2, 4.0, "I08\nperformanceClass"),
    "I09": (84.4, 5.5, 8.0, 4.0, "I09\ncoverType"),
    "I10": (94.0, 5.5, 8.8, 4.0, "I10\ninsuredValue"),
}

BKMS = {
    "BKM01": (29.0, 15.0, 14.5, 4.5, "BKM01: calculateAgeInYears"),
    "BKM02": (46.5, 15.0, 14.5, 4.5, "BKM02: countRecentClaims"),
}

KSS = {
    "KS03": (7.5, 24.0, 12.8, 5.2, "KS03: UU 22/2009 &\nPerpol 5/2021 (SIM)"),
    "KS01": (7.5, 34.5, 12.8, 5.2, "KS01: Underwriting\nPolicy (Educ.)"),
    "KS02": (92.0, 34.5, 12.8, 5.2, "KS02: Illus. Tariff &\nLoading Schedule"),
}

DECS = {
    "D01": (21.5, 24.0, 12.0, 5.0, "D01: Driver Risk\n[UNIQUE]"),
    "D02": (36.0, 24.0, 12.0, 5.0, "D02: Claims Risk\n[FIRST]"),
    "D03": (51.0, 24.0, 12.8, 5.0, "D03: Vehicle Eligibility\n[FIRST]"),
    "D04": (66.0, 24.0, 12.0, 5.0, "D04: Vehicle Risk\n[FIRST]"),
    "D07": (83.0, 24.0, 13.0, 5.0, "D07: Base Premium\n[FIRST]"),
    "D05": (41.0, 34.5, 13.8, 5.0, "D05: Underwriting Decision\n[FIRST]"),
    "D08": (73.5, 34.5, 13.8, 5.0, "D08: Risk Loading\n[COLLECT SUM]"),
    "D06": (41.0, 44.5, 14.2, 5.0, "D06: Inspection Decision\n[FIRST]"),
    "D10": (68.0, 44.5, 14.8, 5.0, "D10: Quote Readiness\n[FIRST]"),
    "D09": (86.0, 51.8, 14.4, 5.0, "D09: Final Premium\n[FIRST]"),
}

ALL_NODES = {**INPUTS, **BKMS, **KSS, **DECS}


def boundary_pt(src_id, dst_id):
    sx, sy, sw, sh, _ = ALL_NODES[src_id]
    dx, dy, dw, dh, _ = ALL_NODES[dst_id]
    # Pick clean top/bottom or left/right attachment
    if abs(sy - dy) < 2.0:
        if sx < dx:
            return (sx + sw / 2, sy), (dx - dw / 2, dy)
        return (sx - sw / 2, sy), (dx + dw / 2, dy)
    if sy < dy:
        return (sx, sy + sh / 2), (dx, dy - dh / 2)
    return (sx, sy - sh / 2), (dx, dy + dh / 2)


def draw_edge(src, dst, kind):
    p1, p2 = boundary_pt(src, dst)
    if kind == "info":
        ax.annotate("", xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.25",
                                    color=NAVY, lw=0.95, shrinkA=1, shrinkB=1), zorder=1)
    elif kind == "know":
        ax.annotate("", xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="->,head_length=0.45,head_width=0.28",
                                    color=BKM_EDGE, lw=1.0, ls="--", shrinkA=1, shrinkB=1), zorder=1)
    elif kind == "auth":
        ax.annotate("", xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle="-", color=KS_EDGE, lw=0.85, ls=":", shrinkA=1, shrinkB=2), zorder=1)
        ax.plot(p2[0], p2[1], marker="o", markersize=3.2, color=KS_EDGE, zorder=2)


# Edges
INFO_EDGES = [
    ("I01", "D01"), ("I02", "D01"),
    ("I02", "D02"), ("I03", "D02"), ("I04", "D02"),
    ("I02", "D03"), ("I05", "D03"), ("I06", "D03"), ("I07", "D03"), ("I10", "D03"),
    ("I02", "D04"), ("I05", "D04"), ("I06", "D04"), ("I07", "D04"), ("I08", "D04"),
    ("I06", "D07"), ("I07", "D07"), ("I09", "D07"), ("I10", "D07"),
    ("D01", "D05"), ("D02", "D05"), ("D03", "D05"), ("D04", "D05"),
    ("D01", "D08"), ("D02", "D08"), ("D04", "D08"), ("I08", "D08"),
    ("D05", "D06"), ("I02", "D06"), ("I05", "D06"), ("I09", "D06"), ("I10", "D06"),
    ("D05", "D10"), ("I06", "D10"), ("I07", "D10"), ("I09", "D10"), ("I10", "D10"), ("D07", "D10"),
    ("D05", "D09"), ("D10", "D09"), ("D07", "D09"), ("D08", "D09"),
]
KNOW_EDGES = [
    ("BKM01", "D01"), ("BKM01", "D03"), ("BKM01", "D04"), ("BKM01", "D06"),
    ("BKM02", "D02"),
]
AUTH_EDGES = [
    ("KS03", "D01"), ("KS03", "BKM01"),
    ("KS01", "D01"), ("KS01", "D02"), ("KS01", "D03"), ("KS01", "D04"), ("KS01", "D05"), ("KS01", "D06"), ("KS01", "D10"),
    ("KS02", "D07"), ("KS02", "D08"), ("KS02", "D09"), ("KS02", "D10"),
]

for s, d in AUTH_EDGES:
    draw_edge(s, d, "auth")
for s, d in KNOW_EDGES:
    draw_edge(s, d, "know")
for s, d in INFO_EDGES:
    draw_edge(s, d, "info")

# Draw Input Data (rounded pill)
for nid, (cx, cy, w, h, lbl) in INPUTS.items():
    box = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                         boxstyle="round,pad=0.1,rounding_size=1.8",
                         facecolor=LIGHT_INP, edgecolor="#4A5568", linewidth=1.1, zorder=3)
    ax.add_patch(box)
    ax.text(cx, cy, lbl, ha="center", va="center", fontsize=6.6, fontweight="bold", color=TEXT_DARK, zorder=4)

# Draw BKMs (clipped-corner rectangle)
for nid, (cx, cy, w, h, lbl) in BKMS.items():
    x0, y0, x1, y1 = cx - w/2, cy - h/2, cx + w/2, cy + h/2
    c = 1.1
    pts = [(x0+c, y0), (x1, y0), (x1, y1-c), (x1-c, y1), (x0, y1), (x0, y0+c)]
    poly = Polygon(pts, closed=True, facecolor=LIGHT_BKM, edgecolor=BKM_EDGE, linewidth=1.2, zorder=3)
    ax.add_patch(poly)
    ax.text(cx, cy, lbl, ha="center", va="center", fontsize=6.9, fontweight="bold", color=BKM_EDGE, zorder=4)

# Draw Knowledge Sources (document-like box)
for nid, (cx, cy, w, h, lbl) in KSS.items():
    box = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                         boxstyle="round,pad=0.1,rounding_size=0.4",
                         facecolor=LIGHT_KS, edgecolor=KS_EDGE, linewidth=1.1, linestyle="-", zorder=3)
    ax.add_patch(box)
    ax.text(cx, cy, lbl, ha="center", va="center", fontsize=6.6, fontweight="bold", color=KS_EDGE, zorder=4)

# Draw Decisions (sharp rectangle with header accent)
for nid, (cx, cy, w, h, lbl) in DECS.items():
    rect = patches.Rectangle((cx - w/2, cy - h/2), w, h,
                             facecolor=LIGHT_DEC, edgecolor=NAVY, linewidth=1.35, zorder=3)
    ax.add_patch(rect)
    ax.text(cx, cy, lbl, ha="center", va="center", fontsize=7.2, fontweight="bold", color=NAVY, zorder=4)

# Legend box
leg_x, leg_y = 1.5, 46.5
ax.add_patch(FancyBboxPatch((leg_x, leg_y), 25.5, 8.8, boxstyle="round,pad=0.2,rounding_size=0.4",
                            facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=0.9, zorder=3))
ax.text(leg_x + 0.8, leg_y + 7.2, "DMN 1.3 DRD Legend (Acyclic 5-Tier DAG)", fontsize=7.2, fontweight="bold", color=NAVY, zorder=4)
ax.annotate("", xy=(leg_x + 5.5, leg_y + 5.2), xytext=(leg_x + 0.8, leg_y + 5.2),
            arrowprops=dict(arrowstyle="-|>,head_length=0.4,head_width=0.2", color=NAVY, lw=1.0), zorder=4)
ax.text(leg_x + 6.2, leg_y + 5.2, "Information Requirement (42 edges)", fontsize=6.6, va="center", color=TEXT_DARK, zorder=4)
ax.annotate("", xy=(leg_x + 5.5, leg_y + 3.2), xytext=(leg_x + 0.8, leg_y + 3.2),
            arrowprops=dict(arrowstyle="->,head_length=0.4,head_width=0.25", color=BKM_EDGE, lw=1.0, ls="--"), zorder=4)
ax.text(leg_x + 6.2, leg_y + 3.2, "Knowledge Requirement (5 edges)", fontsize=6.6, va="center", color=TEXT_DARK, zorder=4)
ax.plot([leg_x + 0.8, leg_x + 5.2], [leg_y + 1.3, leg_y + 1.3], color=KS_EDGE, lw=1.0, ls=":", zorder=4)
ax.plot(leg_x + 5.3, leg_y + 1.3, marker="o", markersize=3.2, color=KS_EDGE, zorder=4)
ax.text(leg_x + 6.2, leg_y + 1.3, "Authority Requirement (13+2 BKM)", fontsize=6.6, va="center", color=TEXT_DARK, zorder=4)

plt.tight_layout(pad=0.3)
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
print("Saved", OUT_PNG)
