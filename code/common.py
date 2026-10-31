"""Shared paths and helpers for the straight-borders project.

Raw inputs (read in place, never copied into the repo):
  NE      /home/claude/newdata/raw3/borders/  Natural Earth vector 5.x (public domain), fetched raw from
          https://github.com/nvkelso/natural-earth-vector/tree/master/geojson :
            ne_10m_admin_0_boundary_lines_land.geojson   the borders analysed (also the 50m and 110m versions,
                                                          used only for the generalisation test)
            ne_10m_rivers_lake_centerlines.geojson, ne_10m_rivers_europe.geojson, ne_10m_rivers_north_america.geojson
            ne_10m_lakes.geojson, ne_10m_lakes_europe.geojson, ne_10m_lakes_north_america.geojson
            ne_10m_geography_regions_polys.geojson       named mountain ranges (FEATURECLA Range/mtn), a cross-check
            ne_10m_admin_0_countries.geojson              names, continents, outlines
  DEM     /home/claude/newdata/raw3/dem/etopo5.cdf  ETOPO5 5 arc-minute global relief (NOAA NGDC, 1988; public domain),
          as distributed in https://github.com/NOAA-PMEL/FerretDatasets (data/etopo5.cdf)
  PLACES  /home/claude/newdata/raw/geo/ne_10m_populated_places_simple.geojson (Natural Earth, public domain)
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NE = "/home/claude/newdata/raw3/borders"
DEM = "/home/claude/newdata/raw3/dem/etopo5.cdf"
PLACES = "/home/claude/newdata/raw/geo/ne_10m_populated_places_simple.geojson"
NE_URL = "https://github.com/nvkelso/natural-earth-vector"
DATA = os.path.join(ROOT, "data")
WORK = os.environ.get("BORDERTMP", "/dev/shm/borders")   # intermediates live in memory, not in the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "straight-borders"
URL = "https://maps.tristanhotham.com/straight-borders/"
REPO = "https://github.com/Tristan-Hotham/straight-borders"
DOI = "10.5281/zenodo.23847974"            # filled by the publisher
DOI_URL = "https://doi.org/10.5281/zenodo.23847974"
BLOG = "https://blog.tristanhotham.com/2026/10/31/straight-borders/"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

# Main settings of the classification (sensitivity is tested in 02_classify.py)
MAIN = dict(tol=1.0,      # km: every vertex of a straight run lies within this distance of a great circle or rhumb line
            lmin=50.0,    # km: shortest run counted as a straight segment
            river=3.0,    # km: border within this distance of a mapped river centre line counts as following it
            wmin=15.0,    # km: shortest run of river or lake border counted
            mtn_low=300.0,  # m: mountain terrain is >= 2500 m, or >= mtn_low m with local relief >= mtn_rel m
            mtn_rel=300.0,
            mtn_r=2,        # DEM cells: radius of the local relief window (2 cells, about 18 km north to south)
            mmin=20.0)    # km: shortest run of mountain border counted
CLASSES = ["straight", "water", "mountain", "other"]
CNAME = {"straight": "Ruler-straight", "water": "River or lake", "mountain": "Through mountains", "other": "Other or irregular"}
CCOL = {"straight": "#C2362B", "water": "#2F6FB0", "mountain": "#A3681A", "other": "#8F8A80"}


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "yr": return str(int(v))
    if f == "pc": return f"{round(float(v))}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "k1": return f"{float(v) / 1000:.1f}"   # km to thousand km
    raise ValueError(f)


def fill(text, R, f=fmt):
    return re.sub(r"\{\{(?!IMG|DOI|BLOG_URL|DOI_URL|TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: f(get(R, m.group(1)), m.group(3)), text)


def check_dashes(text, where):
    for bad in ("—", "–", "--"):
        assert bad not in text, (where, bad, text[max(0, text.find(bad) - 80):text.find(bad) + 80])


def check_words(text, where):
    for bad in ("DSIT", "DCMS", "civil serv", "Civil Serv"):
        assert bad not in text, (where, bad)
