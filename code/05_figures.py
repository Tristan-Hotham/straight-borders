"""Static figures: header.png (1200 x 630), paper figures (release/paper/f_*.png) and blog figures (release/blog/b_*.png).
All numbers from data/results.json."""
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from figstyle import *

R = jload(f"{DATA}/results.json")
PAP = os.path.join(ROOT, "release", "paper"); BLG = os.path.join(ROOT, "release", "blog")
os.makedirs(PAP, exist_ok=True); os.makedirs(BLG, exist_ok=True)
LAB = {"straight": "Ruler-straight (parallel, meridian or other straight line)", "water": "River or lake",
       "mountain": "Through mountains", "other": "Other or irregular"}
PER = [(0, 1879, "#6E5A8A", "before 1880"), (1880, 1914, HOT, "1880 to 1914"), (1915, 1945, GOLD, "1915 to 1945"), (1946, 3000, COOL, "after 1945")]


def per_col(y):
    if not y: return "#BDB6AA"
    return next(c for a, b, c, _ in PER if a <= y <= b)


def handles(scale=1):
    return [Line2D([0], [0], color=CCOL[k], lw=3 * scale if k == "straight" else 2.2 * scale, label=LAB[k]) for k in CLASSES]


def fig_map(path, w=12, legend=True, dpi=200):
    fig = plt.figure(figsize=(w, w * .54), facecolor=BG); ax = fig.add_axes([0, .06 if legend else 0, 1, .94 if legend else 1])
    world_borders(ax, scale=w / 12)
    if legend:
        fig.legend(handles=handles(), loc="lower center", ncol=4, frameon=False, fontsize=9.5, bbox_to_anchor=(.5, 0))
    save(fig, path, dpi=dpi)


def fig_africa(path):
    fig = plt.figure(figsize=(10, 9.4), facecolor=BG); ax = fig.add_axes([0, .05, 1, .95])
    x0, _ = xy(-19, 0); x1, _ = xy(61, 0); _, y0 = xy(20, -36); _, y1 = xy(20, 38)
    world_borders(ax, extent=(x0, x1, y0, y1), scale=1.5)
    for (lon, lat, t) in ((-28, 8, "Atlantic\nOcean"), (66, -12, "Indian\nOcean"), (38, -30, "")):
        if t:
            x, y = xy(lon, lat); ax.text(x, y, t, fontsize=10, color=MUT, ha="center", style="italic", path_effects=HALO)
    fig.legend(handles=handles(), loc="lower center", ncol=2, frameon=False, fontsize=10, bbox_to_anchor=(.5, 0))
    save(fig, path, dpi=170)


def fig_continents(path):
    C = R["continents"]
    fig, ax = plt.subplots(figsize=(10, 4.4), facecolor=BG); ax.set_facecolor(BG)
    for i, c in enumerate(C):
        left = 0
        for k in CLASSES:
            v = c[k + "_pct"]
            ax.barh(i, v, left=left, color=CCOL[k], height=.62, edgecolor=BG, linewidth=1.5)
            left += v
        lab = c["name"] + (" (one border)" if c["name"] == "Oceania" else "")
        ax.text(-1.5, i, lab, ha="right", va="center", fontsize=11, color=FG)
        ax.text(c["straight_pct"] / 2, i, f"{c['straight_pct']:.0f}%", ha="center", va="center", fontsize=10, color="white", fontweight="medium") if c["straight_pct"] >= 6 else None
        ax.text(101.5, i, f"{c['km']:,} km", va="center", fontsize=9.5, color=MUT)
    ax.set_xlim(0, 100); ax.set_ylim(len(C) - .5, -.5); ax.set_yticks([]); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    clean(ax); ax.spines["left"].set_visible(False)
    ax.legend(handles=[Patch(fc=CCOL[k], label=CNAME[k]) for k in CLASSES], loc="upper center", bbox_to_anchor=(.45, -.1), ncol=4, frameon=False, fontsize=9.5)
    fig.subplots_adjust(left=.24, right=.86, top=.97, bottom=.2)
    save(fig, path, dpi=180)


def fig_top(path, n=40):
    T = R["top"][:n]
    fig, ax = plt.subplots(figsize=(10, .27 * n + 1.3), facecolor=BG); ax.set_facecolor(BG)
    mx = max(t["km"] for t in T)
    for i, t in enumerate(T):
        col = per_col(t["year"])
        ax.barh(i, t["km"], color=col if t["conf"] != "low" else mix(BG, col, .45), height=.7, edgecolor=col, linewidth=.8)
        ax.text(-20, i, t["name"], ha="right", va="center", fontsize=8.6, color=FG)
        ax.text(t["km"] + 15, i, f"{t['km']:,} km · {t['year_label']}", va="center", fontsize=8.2, color=MUT)
    ax.set_ylim(n - .4, -.6); ax.set_xlim(0, mx * 1.32); ax.set_yticks([]); clean(ax); ax.spines["left"].set_visible(False)
    ax.set_xlabel("Length of the straight segment (km)", fontsize=9.5, color=MUT)
    hs = [Patch(fc=c, ec=c, label=l) for _, _, c, l in PER] + [Patch(fc=mix(BG, "#777777", .45), ec="#777777", label="origin uncertain")]
    ax.legend(handles=hs, loc="center right", frameon=False, fontsize=8.6, title="Year the line was drawn", title_fontsize=8.6)
    fig.subplots_adjust(left=.34, right=.98, top=.99, bottom=.9 / (.27 * n + 1.3))
    save(fig, path, dpi=180)


def fig_timeline(path):
    T = [t for t in R["top"] if t["year"]]
    fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=BG); ax.set_facecolor(BG)
    ax.axvspan(1880, 1914, color=mix(BG, HOT, .12), lw=0)
    ax.text(1897, 2120, "Scramble for Africa\n1880 to 1914", ha="center", va="top", fontsize=9, color=HOT)
    for t in T:
        c = COOL if t["cont"] != "Africa" else HOT
        ax.scatter(t["year"], t["km"], s=40 + t["km"] / 14, color=c if t["conf"] != "low" else BG, edgecolor=c, linewidth=1.3, zorder=3, alpha=.9)
    lab = {1: ("49th parallel", 9, 2), 2: ("141st meridian", 9, 2), 5: ("Egypt and Libya", 9, 2), 7: ("Egypt and Sudan", -9, 10), 30: ("Saudi Arabia and Yemen", -8, 10),
           3: ("Mali and Mauritania", 9, 2), 39: ("Tierra del Fuego", -8, 6), 20: ("Gadsden line", 0, 12), 4: ("Libya and Chad", -9, 8)}
    for t in T:
        if t["rank"] in lab:
            n, dx, dy = lab[t["rank"]]
            ax.annotate(n, (t["year"], t["km"]), xytext=(dx, dy), textcoords="offset points", fontsize=8.5, color=FG, path_effects=HALO, ha="left" if dx > 0 else "right")
    ax.set_xlim(1770, 2010); ax.set_ylim(100, 2200); clean(ax)
    ax.set_ylabel("Length (km)", fontsize=9.5, color=MUT); ax.grid(axis="y", color=RULE, lw=.6); ax.set_axisbelow(True)
    ax.legend(handles=[Line2D([0], [0], marker="o", ls="", color=HOT, label="In Africa"), Line2D([0], [0], marker="o", ls="", color=COOL, label="Elsewhere"),
                       Line2D([0], [0], marker="o", ls="", mfc=BG, mec=MUT, label="Origin uncertain")], loc="upper right", frameon=False, fontsize=9)
    fig.subplots_adjust(left=.09, right=.98, top=.96, bottom=.1)
    save(fig, path, dpi=180)


def fig_sens(path):
    S = R["sens_straight"]; tols = sorted({s["tol"] for s in S}); lms = sorted({s["lmin"] for s in S})
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.9), facecolor=BG, gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axs[0]; ax.set_facecolor(BG)
    for i, t in enumerate(tols):
        for j, l in enumerate(lms):
            s = next(x for x in S if x["tol"] == t and x["lmin"] == l)
            v = s["world_pct"]; main = t == MAIN["tol"] and l == MAIN["lmin"]
            ax.add_patch(Rectangle((j, i), .96, .92, color=mix("#F3E9DD", HOT, min(1, v / 55)), ec=FG if main else "none", lw=1.6))
            ax.text(j + .48, i + .46, f"{v:.0f}%", ha="center", va="center", fontsize=11, color="white" if v > 30 else FG)
    ax.set_xlim(0, len(lms)); ax.set_ylim(len(tols), 0); ax.set_xticks([j + .48 for j in range(len(lms))]); ax.set_xticklabels([f"{l:.0f} km" for l in lms])
    ax.set_yticks([i + .46 for i in range(len(tols))]); ax.set_yticklabels([f"{t:g} km" for t in tols]); clean(ax)
    for s_ in ax.spines.values(): s_.set_visible(False)
    ax.set_xlabel("shortest straight segment", fontsize=9, color=MUT); ax.set_ylabel("tolerance", fontsize=9, color=MUT)
    ax.set_title("World share straight", fontsize=10, color=FG, loc="left")
    ax = axs[1]; ax.set_facecolor(BG)
    x = np.arange(len(S)); order = sorted(S, key=lambda s: (s["tol"], s["lmin"]))
    for c, col, mk in (("North America", COOL, "o"), ("Africa", HOT, "s"), ("South America", GOLD, "^"), ("Asia", "#6E5A8A", "D"), ("Europe", GREY, "v")):
        ax.plot(x, [s[c] for s in order], marker=mk, color=col, lw=1.6, ms=5, label=c)
    ax.set_xticks(x); ax.set_xticklabels([f"{s['tol']:g}/{s['lmin']:.0f}" for s in order], rotation=60, fontsize=7.5)
    ax.set_ylabel("Share straight (%)", fontsize=9, color=MUT); clean(ax); ax.grid(axis="y", color=RULE, lw=.6)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper left"); ax.set_ylim(0, 75)
    ax.set_title("By continent, each setting (tolerance km / shortest km)", fontsize=10, color=FG, loc="left")
    fig.subplots_adjust(left=.11, right=.99, top=.9, bottom=.25, wspace=.3)
    save(fig, path, dpi=180)


def fig_scale(path):
    """The same stretch of the Pyrenees at three Natural Earth scales, and the world share straight at each."""
    fig = plt.figure(figsize=(10.5, 4.4), facecolor=BG)
    ext = (-2.2, 3.4, 42.1, 43.45)
    for i, sc in enumerate(("10m", "50m", "110m")):
        ax = fig.add_axes([.01 + i * .225, .14, .215, .74]); ax.set_facecolor(mix(BG, LAND, .6))
        Bs = jload(f"{WORK}/borders_{sc}.json")
        for b in Bs:
            c = np.array(b["c"])
            m = (c[:, 0] > ext[0] - 1) & (c[:, 0] < ext[1] + 1) & (c[:, 1] > ext[2] - 1) & (c[:, 1] < ext[3] + 1)
            if m.any():
                ax.plot(c[:, 0], c[:, 1], color=FG, lw=1.3)
                if sc != "10m":
                    ax.plot(c[:, 0], c[:, 1], "o", color=HOT, ms=2.5)
        ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1 / np.cos(np.radians(42.8))); ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values(): s_.set_color(RULE)
        ax.set_title(f"1:{ {'10m': '10', '50m': '50', '110m': '110'}[sc]} million", fontsize=10, color=FG)
    fig.text(.01, .06, "France and Spain in the Pyrenees, as Natural Earth draws them (dots: vertices at the coarser scales)", fontsize=8.5, color=MUT)
    ax = fig.add_axes([.74, .2, .24, .66]); ax.set_facecolor(BG)
    v = [R["scale"][s]["straight_pct"] for s in ("10m", "50m", "110m")]
    ax.bar([0, 1, 2], v, color=[HOT, mix(BG, HOT, .6), mix(BG, HOT, .35)], width=.62)
    for i, x in enumerate(v): ax.text(i, x + 2, f"{x:.0f}%", ha="center", fontsize=10.5, color=FG)
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["1:10m", "1:50m", "1:110m"], fontsize=9); ax.set_yticks([]); clean(ax); ax.spines["left"].set_visible(False)
    ax.set_title("World border length\ncounted as straight", fontsize=9.5, color=FG); ax.set_ylim(0, 100)
    save(fig, path, dpi=180)


def fig_water_mtn(path):
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), facecolor=BG)
    for ax, k, ttl in ((axs[0], "water", "Most border along rivers and lakes"), (axs[1], "mountain", "Most border through mountains")):
        T = R["borders"]["top_" + k + "_km"][:10]; ax.set_facecolor(BG)
        for i, t in enumerate(T):
            ax.barh(i, t["total"], color=mix(BG, CCOL[k], .18), height=.66)
            ax.barh(i, t["km"], color=CCOL[k], height=.66)
            ax.text(t["total"] + 60, i, f"{t['km']:,} of {t['total']:,} km", va="center", fontsize=8, color=MUT)
            ax.text(-60, i, t["name"], ha="right", va="center", fontsize=8.4, color=FG)
        ax.set_ylim(9.5, -.6); ax.set_yticks([]); ax.set_xlim(0, max(t["total"] for t in T) * 1.7); clean(ax); ax.spines["left"].set_visible(False)
        ax.set_title(ttl, fontsize=10.5, color=FG, loc="left"); ax.tick_params(labelsize=8)
    fig.subplots_adjust(left=.235, right=.985, wspace=1.15, top=.92, bottom=.08)
    save(fig, path, dpi=180)


def header(path):
    fig = plt.figure(figsize=(12, 6.3), facecolor=BG)
    ax = fig.add_axes([.25, .02, .76, .8]); world_borders(ax, scale=.9)
    fig.text(.035, .93, "Where the borders\nare straight", fontproperties=DISP, fontsize=38, color=FG, va="top", linespacing=.95)
    w = R["world"]
    fig.text(.035, .58, f"{w['straight_pct']:.0f}%", fontproperties=DISP, fontsize=46, color=HOT, va="top")
    fig.text(.035, .46, "of the world's land border\nlength is ruler-straight", fontsize=11, color=FG, va="top", linespacing=1.3)
    fig.text(.035, .33, f"Africa holds {R['africa']['share_of_world_straight']:.0f}% of it.\nNorth America is straighter\nby share: {R['continents'][1]['straight_pct']:.0f}%.", fontsize=10.5, color=MUT, va="top", linespacing=1.35)
    y = .14
    for k in CLASSES:
        fig.add_artist(Line2D([.035, .06], [y + .008, y + .008], color=CCOL[k], lw=3.5, transform=fig.transFigure))
        fig.text(.067, y, CNAME[k], fontsize=9.5, color=FG); y -= .035
    save(fig, path, dpi=100)


if __name__ == "__main__":
    assert R["continents"][1]["name"] == "North America" and R["continents"][0]["name"] == "Oceania"
    header(os.path.join(ROOT, "header.png"))
    for d, pre in ((PAP, "f_"), (BLG, "b_")):
        fig_map(f"{d}/{pre}map.png")
        fig_africa(f"{d}/{pre}africa.png")
        fig_continents(f"{d}/{pre}continents.png")
        fig_top(f"{d}/{pre}top.png", 40 if pre == "f_" else 30)
        fig_timeline(f"{d}/{pre}timeline.png")
        fig_scale(f"{d}/{pre}scale.png")
        fig_water_mtn(f"{d}/{pre}rivers.png")
    fig_sens(f"{PAP}/f_sens.png")
    print("figures done")
