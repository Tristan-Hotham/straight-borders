"""Read the Natural Earth 10m land boundary lines, keep international borders, join the pieces of each border (country pair)
into continuous paths, and give each border a continent. Output: WORK/borders.json (and the same for 50m and 110m,
used only for the generalisation test).

Kept: FEATURECLA International boundary, Disputed, Indefinite, Line of control and Indeterminant frontier, TYPE Land or
Water Indicator (boundaries through lakes and estuaries). Left out: Overlay limit (UN buffer and demilitarised zones,
drawn on top of other borders), Lease limit (Guantanamo, Baikonur), Unrecognized, lines with no country on one side,
lines with the same country on both sides, and lines to the United Nations buffer zone in Cyprus, Brazilian Island,
Baikonur and Guantanamo (zones rather than countries)."""
import sys
from collections import defaultdict
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge
from pyproj import Geod
from common import *

G = Geod(ellps="WGS84")
KEEP = {"International boundary (verify)", "Disputed (please verify)", "Indefinite (please verify)",
        "Line of control (please verify)", "Indeterminant frontier"}
ZONES = {"CNM", "BRI", "KAB", "USG", None}
C = jload(f"{NE}/ne_10m_admin_0_countries.geojson")["features"]
CP = {f["properties"]["ADM0_A3"]: f["properties"] for f in C}
NAME = {k: p["NAME_EN"] for k, p in CP.items()}
NAME.update({"USA": "United States", "SDS": "South Sudan", "PSX": "Palestine", "KAS": "Siachen Glacier", "SAH": "Western Sahara",
             "SOL": "Somaliland", "COD": "DR Congo", "COG": "Republic of the Congo", "CZE": "Czechia", "TZA": "Tanzania",
             "ESB": "Dhekelia (UK base)", "WSB": "Akrotiri (UK base)", "GMB": "The Gambia", "BHS": "The Bahamas", "CYN": "Northern Cyprus",
             "MKD": "North Macedonia", "SWZ": "Eswatini", "CIV": "Ivory Coast", "KOS": "Kosovo", "SRB": "Serbia", "RUS": "Russia",
             "PRK": "North Korea", "KOR": "South Korea", "LAO": "Laos", "VNM": "Vietnam", "SYR": "Syria", "IRN": "Iran", "BOL": "Bolivia",
             "VEN": "Venezuela", "MDA": "Moldova", "MAF": "Saint Martin (France)", "SXM": "Sint Maarten (Netherlands)",
             "GIB": "Gibraltar", "BRN": "Brunei", "TLS": "Timor-Leste", "CPV": "Cape Verde", "FRA": "France", "NLD": "Netherlands", "CHN": "China", "TWN": "Taiwan", "BIH": "Bosnia and Herzegovina", "GNB": "Guinea-Bissau", "GNQ": "Equatorial Guinea", "CAF": "Central African Republic"})
CONT = {k: p["CONTINENT"] for k, p in CP.items()}
# Borders between countries that Natural Earth puts in different continents, placed by where the line lies.
MIXED = {("ESP", "MAR"): "Africa",            # Ceuta and Melilla
         ("BRA", "FRA"): "South America", ("FRA", "SUR"): "South America",   # French Guiana
         ("MAF", "SXM"): "North America",
         ("BGR", "TUR"): "Europe", ("GRC", "TUR"): "Europe",                  # Thrace
         ("EGY", "ISR"): "Asia", ("EGY", "PSX"): "Asia",                      # Sinai and Gaza
         ("COL", "PAN"): "North America",                                     # the isthmus (conventional limit)
         ("IDN", "PNG"): "Oceania"}                                           # New Guinea


def continent(a, b):
    ca, cb = CONT.get(a), CONT.get(b)
    if ca == cb:
        return ca
    k = tuple(sorted((a, b)))
    if k in MIXED:
        return MIXED[k]
    if "RUS" in k:                       # Russia's borders with Asian countries lie in Asia (Caucasus, Kazakhstan, China ...)
        return cb if a == "RUS" else ca
    if {"ESB", "WSB"} & set(k) or "CYP" in k or "CYN" in k:
        return "Asia"
    raise ValueError((a, b, ca, cb))


def parts(geom):
    return [geom["coordinates"]] if geom["type"] == "LineString" else geom["coordinates"]


def build(scale):
    F = jload(f"{NE}/ne_{scale}_admin_0_boundary_lines_land.geojson")["features"]
    grp = defaultdict(list); dropped = defaultdict(float)
    for f in F:
        p = f["properties"]; a, b = p.get("ADM0_A3_L"), p.get("ADM0_A3_R")
        L = sum(G.line_length(*zip(*c)) for c in parts(f["geometry"])) / 1000
        if scale != "10m":                # the 50m and 110m lines carry no country names: world totals only
            a, b = "?", "?!"
        if p["FEATURECLA"] not in KEEP or a in ZONES or b in ZONES or a == b:
            dropped[p["FEATURECLA"] if p["FEATURECLA"] not in KEEP else "zone or same country"] += L
            continue
        k = tuple(sorted((a, b)))
        water = p.get("TYPE") == "Water Indicator"
        fc = p["FEATURECLA"].replace(" (please verify)", "").replace(" (verify)", "")
        grp[(k, water, fc)].extend(LineString(c) for c in parts(f["geometry"]) if len(c) > 1)
    out = []
    for (k, water, fc), lines in sorted(grp.items()):
        m = linemerge(MultiLineString(lines))
        ls = [m] if m.geom_type == "LineString" else list(m.geoms)
        for l in ls:
            co = [[round(x, 6), round(y, 6)] for x, y in l.coords]
            out.append({"a": k[0], "b": k[1], "water": water, "fc": fc, "cont": continent(*k) if scale == "10m" else None,
                        "km": G.line_length(*zip(*co)) / 1000, "c": co})
    return out, dropped


if __name__ == "__main__":
    for scale in ("10m", "50m", "110m"):
        B, dropped = build(scale)
        jsave(B, f"{WORK}/borders_{scale}.json")
        tot = sum(b["km"] for b in B)
        print(scale, len(B), "paths", len({(b['a'], b['b']) for b in B}), "borders", f"{tot:,.0f} km", "dropped",
              {k: round(v) for k, v in dropped.items()})
    jsave({"name": NAME, "cont": CONT}, f"{WORK}/names.json")
