"""House style for static figures: fonts (a static Fraunces Black cut from the variable font, written to memory), colours,
and a world map of classified borders in the Equal Earth projection."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import LineCollection, PatchCollection
import matplotlib.patheffects as pe
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape
from common import *

FONTS = "/home/claude/ref/fonts"
FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": 900, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-Black.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERB = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Semibold.ttf")
SERI = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-It.ttf")
fm.fontManager.addfont(f"{FONTS}/IBMPlexMono-Regular.ttf")
fm.fontManager.addfont(f"{FONTS}/IBMPlexMono-Medium.ttf")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": "#646875", "axes.labelcolor": "#1E2430",
                     "xtick.color": "#646875", "ytick.color": "#646875"})
BG, FG, MUT, LAND, RULE, SEA = "#F7F3EA", "#1E2430", "#646875", "#E9E2D2", "#E2DACA", "#F7F3EA"
HOT, COOL, GOLD, GREY = CCOL["straight"], CCOL["water"], CCOL["mountain"], CCOL["other"]
LW = {"straight": 1.5, "water": 1.1, "mountain": 1.1, "other": .85}
tr = Transformer.from_crs(4326, 8857, always_xy=True)
WORLD_EXT = (-13.2e6, 16.2e6, -6.3e6, 8.5e6)
HALO = [pe.withStroke(linewidth=3.2, foreground=BG)]


def xy(lon, lat):
    return tr.transform(lon, lat)


_LAND = None


def land_patches():
    global _LAND
    if _LAND is None:
        _LAND = []
        for f in jload("/home/claude/newdata/raw/geo/ne_50m_land.geojson")["features"]:
            g = shape(f["geometry"])
            for p in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
                c = np.array(p.exterior.coords)
                if c[:, 1].max() < -60: continue
                x, y = tr.transform(np.clip(c[:, 0], -179.9, 179.9), c[:, 1])
                _LAND.append(np.column_stack([x, y]))
    return _LAND


_CO = None


def coast_lines():
    """Country outlines (thin, for context)."""
    global _CO
    if _CO is None:
        _CO = []
        for f in jload(f"{DATA}/countries_lite.json")["features"]:
            g = shape(f["geometry"])
            for p in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
                c = np.array(p.exterior.coords)
                if c[:, 1].max() < -60: continue
                x, y = tr.transform(np.clip(c[:, 0], -179.9, 179.9), c[:, 1]); _CO.append(np.column_stack([x, y]))
    return _CO


_BL = None


def border_lines():
    global _BL
    if _BL is None:
        _BL = {k: [] for k in CLASSES}
        for f in jload(f"{DATA}/borders_classified.geojson")["features"]:
            c = np.array(f["geometry"]["coordinates"])
            x, y = tr.transform(c[:, 0], c[:, 1])
            _BL[f["properties"]["class"]].append(np.column_stack([x, y]))
    return _BL


def world_borders(ax, extent=WORLD_EXT, scale=1.0, land=LAND, only=None):
    ax.add_collection(PatchCollection([MPoly(p, closed=True) for p in land_patches()], fc=land, ec="none", zorder=1))
    ax.add_collection(LineCollection(coast_lines(), colors="#D3C9B5", linewidths=.25 * scale, zorder=2))
    BL = border_lines()
    for k in ["other", "mountain", "water", "straight"]:
        if only and k not in only: continue
        ax.add_collection(LineCollection(BL[k], colors=CCOL[k], linewidths=LW[k] * scale, capstyle="round", zorder=3 + CLASSES[::-1].index(k)))
    ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3]); ax.set_aspect("equal"); ax.axis("off")


def mix(a, b, t):
    A = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; B = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(A, B))


def save(fig, name, dpi=200):
    fig.savefig(name, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
