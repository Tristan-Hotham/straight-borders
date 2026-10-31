"""r/dataisbeautiful collage for straight-borders: 2400 x 3200 px on a light background. Numbers from data/results.json.
Labels sit on open sea with a white halo; leader lines run from each label to its line and cross no other label."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figstyle import *
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

R = jload(f"{DATA}/results.json")
BGc = "#FAF7F0"
WH = [pe.withStroke(linewidth=4, foreground="white")]
fig = plt.figure(figsize=(12, 16), dpi=200, facecolor=BGc)
fig.text(.04, .978, "Where the borders are straight", fontproperties=DISP, fontsize=50, color=FG, va="top")
w, a, C = R["world"], R["africa"], R["cont"]
fig.text(.04, .932, f"Every international land border on Earth ({w['km']:,} km), sorted kilometre by kilometre into ruler-straight lines,\n"
         "rivers and lakes, mountains and the rest; with who drew the longest straight lines, and when.",
         fontproperties=SERP, fontsize=15, color=FG, va="top", linespacing=1.4)

# ---- the map
ax = fig.add_axes([0, .535, 1, .345]); ax.set_facecolor(BGc)
ext = (-19.2e6, 18.6e6, -6.6e6, 8.7e6)
world_borders(ax, extent=ext, scale=1.25, land="#ECE5D6")
for lon, lat, t in ((-140, 5, "Pacific\nOcean"), (-32, -8, "Atlantic\nOcean"), (80, -30, "Indian\nOcean")):
    x, y = xy(lon, lat); ax.text(x, y, t, fontproperties=SERI, fontsize=13, color="#9A938A", ha="center", va="center", linespacing=1.1)
T = {t["rank"]: t for t in R["top"]}
eg = R["ex"]["eg22_total"]
X0 = -19.0e6
LBL = [  # (label x or lon, lat, text, target lon, lat); x given directly for labels on the paper margin
    (X0, 63, f"141st meridian, Alaska\n{T[2]['km']:,} km · 1825", -141, 66),
    (X0, 44, f"49th parallel, Canada and US\n{T[1]['km']:,} km · 1818 and 1846", -112, 48.99),
    (X0, 22, f"Gadsden line, Mexico and US\n{T[20]['km']} km · 1853", -113, 31.9),
    (X0, -48, f"Tierra del Fuego meridian\n{T[39]['km']} km · 1881", -68.6, -53.5),
    (-73, 31, f"Mali and Mauritania\n{T[3]['km']} km · 1944", -6.1, 21),
    (-57, 17, f"Libya and Chad\n{T[4]['km']} km · 1899", 20.5, 21.2),
    (-44, -27, f"Namibia's meridians\n{T[18]['km'] + T[19]['km'] + T[29]['km']:,} km · 1890", 19.98, -26),
    (55, -11, f"Kenya and Tanzania\n{T[9]['km']} km · 1886", 36.5, -2.4),
    (60, 2, f"Egypt and Sudan\n{eg:,} km · 1899", 33.5, 22),
    (128, 13, f"New Guinea, 141st meridian\n{T[13]['km'] + T[38]['km']} km · {T[13]['year_label']}", 141, -4.5),
]
for lon, lat, txt, tl, tt in LBL:
    if lon == X0:
        x = X0; y = xy(-180, lat)[1]
    else:
        x, y = xy(lon, lat)
    x1, y1 = xy(tl, tt)
    tx = ax.text(x, y, txt, fontsize=9.4, color=FG, ha="left", va="center", zorder=10, path_effects=WH, linespacing=1.25)
    fig.canvas.draw(); bb = tx.get_window_extent().transformed(ax.transData.inverted())
    sx = bb.x1 + 1.5e5 if x1 > bb.x1 else bb.x0 - 1.5e5
    sy = y1 if bb.y0 <= y1 <= bb.y1 else (bb.y1 if y1 > bb.y1 else bb.y0)
    if x1 > bb.x1: sy = y
    ax.plot([sx, x1], [sy, y1], color=FG, lw=.7, zorder=8, solid_capstyle="round")
    ax.plot([x1], [y1], "o", ms=4, mfc="white", mec=FG, mew=.9, zorder=9)
leg = [Line2D([0], [0], color=CCOL["straight"], lw=4, label=f"Ruler-straight: parallel, meridian or straight line, 50 km or more ({w['straight_pct']:.1f}%)"),
       Line2D([0], [0], color=CCOL["water"], lw=3, label=f"Following a river or lake ({w['water_pct']:.1f}%)"),
       Line2D([0], [0], color=CCOL["mountain"], lw=3, label=f"Through mountains ({w['mountain_pct']:.1f}%)"),
       Line2D([0], [0], color=CCOL["other"], lw=2.4, label=f"Other or irregular ({w['other_pct']:.1f}%)")]
fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(.04, .535), ncol=2, frameon=False, fontsize=10.5, handlelength=2.2, columnspacing=2.2)

# ---- big numbers
nums = [(f"{w['straight_pct']:.0f}%", CCOL["straight"], "of the world's land\nborder is straight"),
        (f"{a['share_of_world_straight']:.0f}%", CCOL["straight"], "of all straight border\nis in Africa"),
        (f"{C['North_America']['straight_pct']:.0f}%", CCOL["water"], f"of North America's border\nis straight; Africa's: {C['Africa']['straight_pct']:.0f}%"),
        (f"{R['top_years']['n_1880_1914']} of {R['top_years']['n_dated']}", FG, f"of the longest straight\nlines were drawn in\n1880 to 1914")]
for i, (big, col, txt) in enumerate(nums):
    x = .04 + i * .238
    fig.text(x, .47, big, fontproperties=DISP, fontsize=36, color=col, va="top")
    fig.text(x, .43, txt, fontsize=10, color=FG, va="top", linespacing=1.25)

# ---- panel: share by continent
ax = fig.add_axes([.17, .095, .3, .25]); ax.set_facecolor(BGc)
CL = [c for c in R["continents"]]
for i, c in enumerate(CL):
    left = 0
    for k in CLASSES:
        v = c[k + "_pct"]; ax.barh(i, v, left=left, color=CCOL[k], height=.66, edgecolor=BGc, linewidth=1.5); left += v
    ax.text(-2, i, c["name"] + ("*" if c["name"] == "Oceania" else ""), ha="right", va="center", fontsize=10, color=FG)
    ax.text(103, i, f"{c['straight_pct']:.0f}%", ha="left", va="center", fontsize=10, color=CCOL["straight"], fontweight="medium")
ax.set_xlim(0, 100); ax.set_ylim(len(CL) - .5, -.5); ax.axis("off")
fig.text(.04, .375, "Share of each continent's border length\nthat is straight (red), river, mountain, other", fontproperties=SERB, fontsize=13, color=FG, va="top")
fig.text(.04, .083, f"* Oceania has one land border, across New Guinea. North America beats Africa under all {a['n_settings']} definitions tested.", fontsize=8.6, color=MUT, va="top")

# ---- panel: longest straight lines with year drawn
PER = [(0, 1879, "#6E5A8A"), (1880, 1914, HOT), (1915, 1945, GOLD), (1946, 3000, COOL)]
pc = lambda y: "#BDB6AA" if not y else next(c for a_, b_, c in PER if a_ <= y <= b_)
ax = fig.add_axes([.74, .095, .2, .235]); ax.set_facecolor(BGc)
top = R["top"][:12]
for i, t in enumerate(top):
    c = pc(t["year"]); ax.barh(i, t["km"], color=c if t["conf"] != "low" else mix(BGc, c, .45), height=.66, edgecolor=c, linewidth=.6)
    ax.text(-30, i, f"{t['rank']}. {t['name'].replace('United States', 'US')}", ha="right", va="center", fontsize=8.8, color=FG)
    ax.text(t["km"] + 30, i, f"{t['km']:,} km · {t['year_label']}", va="center", fontsize=8, color=MUT)
ax.set_xlim(0, 2100 * 2.0); ax.set_ylim(len(top) - .5, -.6); ax.axis("off")
fig.text(.53, .375, "The longest straight lines, and the year drawn", fontproperties=SERB, fontsize=13, color=FG, va="top")
hs = [Patch(fc="#6E5A8A", label="before 1880"), Patch(fc=HOT, label="1880 to 1914"), Patch(fc=GOLD, label="1915 to 1945"), Patch(fc=COOL, label="after 1945"),
      Patch(fc=mix(BGc, "#888888", .45), ec="#888888", label="origin uncertain")]
fig.legend(handles=hs, loc="upper left", bbox_to_anchor=(.52, .36), ncol=3, frameon=False, fontsize=8.6, handlelength=1.3, columnspacing=.8)

fig.text(.04, .012, "Data: Natural Earth 1:10m admin-0 boundary lines, rivers and lakes (public domain); ETOPO5 elevation (NOAA). Straight: within 1 km of a great circle or\n"
         "line of constant bearing for 50 km or more. Treaties compiled from Brownlie (1979), Biger (1995), US boundary studies and Wikipedia; uncertain ones marked.\n"
         "Measured on a generalised world map, not the ground. Dr Tristan Hotham · maps.tristanhotham.com/straight-borders",
         fontsize=8.6, color=MUT, va="bottom", linespacing=1.45)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "where_the_borders_are_straight.png")
fig.savefig(out, dpi=200, facecolor=BGc)
print("collage done", out)
