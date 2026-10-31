"""Totals by world, continent, country and border; the longest straight segments joined to the treaty table; the test of
"Africa's borders are the straightest"; sensitivity. Writes data/results.json (every number quoted anywhere) and the
reusable data files in data/."""
import csv, math
from collections import defaultdict
import numpy as np
from shapely.geometry import shape, Point, LineString
from shapely.strtree import STRtree
from shapely.prepared import prep
from common import *
import treaties as TR

B = jload(f"{WORK}/borders_10m.json")
PC = jload(f"{WORK}/classified.json")
SEG = jload(f"{WORK}/segments.json")
SENS = jload(f"{WORK}/sensitivity.json")
NM = jload(f"{WORK}/names.json")
NAME = NM["name"]
nm = lambda k: NAME.get(k, k)
CONTS = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]
r1 = lambda x: round(float(x), 1)
pct = lambda a, b: round(100.0 * a / b, 1) if b else 0.0

# ---------------------------------------------------------------- totals
world = {k: 0.0 for k in CLASSES}
byc = {c: {k: 0.0 for k in CLASSES} for c in CONTS}
dy = defaultdict(lambda: {k: 0.0 for k in CLASSES})
fcw = defaultdict(lambda: {k: 0.0 for k in CLASSES})
for p in PC:
    b = B[p["path"]]
    world[p["cls"]] += p["km"]; byc[b["cont"]][p["cls"]] += p["km"]
    dy[(b["a"], b["b"])][p["cls"]] += p["km"]
    fcw[b["fc"]][p["cls"]] += p["km"]
WT = sum(world.values())
assert abs(WT - sum(b["km"] for b in B)) / WT < 0.002, (WT, sum(b["km"] for b in B))
R = {"meta": {"page": URL, "repo": REPO, "ne_version": open(f"{NE}/VERSION").read().strip(), "settings": MAIN}}
R["world"] = {"km": round(WT), "n_borders": len(dy), "n_countries": len({k for d in dy for k in d}),
              **{k: round(v) for k, v in world.items()}, **{k + "_pct": pct(v, WT) for k, v in world.items()}}
# by legal status of the line
intl = fcw["International boundary"]; it = sum(intl.values())
R["world"]["intl_only_straight_pct"] = pct(intl["straight"], it)
R["world"]["non_intl_km"] = round(WT - it)
R["world"]["non_intl_pct"] = pct(WT - it, WT)

# straight segments by type
kinds = defaultdict(float)
for s in SEG:
    kinds[s["kind"]] += s["km"]
assert abs(sum(kinds.values()) - world["straight"]) < 1, (sum(kinds.values()), world["straight"])
R["straight"] = {"n_segments": len(SEG), "km": round(world["straight"]),
                 **{k + "_km": round(v) for k, v in kinds.items()}, **{k + "_pct_of_straight": pct(v, world["straight"]) for k, v in kinds.items()},
                 "astro_pct_of_world": pct(kinds["parallel"] + kinds["meridian"], WT)}

# continents
cont = []
for c in CONTS:
    t = sum(byc[c].values())
    a = {"name": c, "km": round(t), **{k: round(v) for k, v in byc[c].items()}, **{k + "_pct": pct(v, t) for k, v in byc[c].items()},
         "share_of_world_straight": pct(byc[c]["straight"], world["straight"])}
    sk = defaultdict(float)
    for s in SEG:
        if s["cont"] == c: sk[s["kind"]] += s["km"]
    a["astro_pct"] = pct(sk["parallel"] + sk["meridian"], t)
    cont.append(a)
cont.sort(key=lambda a: -a["straight_pct"])
R["continents"] = cont
CT = {a["name"]: a for a in cont}

# borders (country pairs)
bt = {}
for (a, b), v in dy.items():
    t = sum(v.values())
    bt[(a, b)] = {"a": a, "b": b, "name": f"{nm(a)} and {nm(b)}", "cont": next(x["cont"] for x in B if (x["a"], x["b"]) == (a, b)),
                  "km": round(t, 1), **{k: round(x, 1) for k, x in v.items()}, **{k + "_pct": pct(x, t) for k, x in v.items()}}
BT = sorted(bt.values(), key=lambda d: -d["km"])


def top(cls, n=15, minkm=0):
    return [{"name": d["name"], "a": d["a"], "b": d["b"], "km": round(d[cls]), "pct": d[cls + "_pct"], "total": round(d["km"])}
            for d in sorted(BT, key=lambda d: -d[cls]) if d["km"] >= minkm][:n]


R["borders"] = {"top_straight_km": top("straight"), "top_water_km": top("water"), "top_mountain_km": top("mountain"),
                "n_mostly_straight": sum(1 for d in BT if d["straight_pct"] >= 50),
                "n_all_straight": sum(1 for d in BT if d["straight_pct"] >= 95 and d["km"] >= 100),
                "n_any_straight": sum(1 for d in BT if d["straight"] > 0),
                "longest": [{"name": d["name"], "km": round(d["km"])} for d in BT[:5]]}
R["borders"]["mostly_straight_pct"] = pct(R["borders"]["n_mostly_straight"], len(BT))
for c in CONTS:
    ds = [d for d in BT if d["cont"] == c]
    CT[c]["n_borders"] = len(ds); CT[c]["n_mostly_straight"] = sum(1 for d in ds if d["straight_pct"] >= 50)
    CT[c]["mostly_straight_pct"] = pct(CT[c]["n_mostly_straight"], len(ds))
    CT[c]["median_border_straight_pct"] = r1(np.median([d["straight_pct"] for d in ds]))

# countries
cy = defaultdict(lambda: {k: 0.0 for k in CLASSES})
for d in BT:
    for k in (d["a"], d["b"]):
        for c in CLASSES: cy[k][c] += d[c]
CY = []
for k, v in cy.items():
    t = sum(v.values())
    CY.append({"iso": k, "name": nm(k), "cont": NM["cont"].get(k), "km": round(t), **{c: round(x) for c, x in v.items()},
               **{c + "_pct": pct(x, t) for c, x in v.items()}, "n_neighbours": sum(1 for d in BT if k in (d["a"], d["b"]))})
CY.sort(key=lambda d: -d["straight_pct"])
big = [d for d in CY if d["km"] >= 1000]
R["countries"] = {"n": len(CY), "n_1000": len(big),
                  "top_straight_pct": [{"name": d["name"], "iso": d["iso"], "pct": d["straight_pct"], "km": d["km"]} for d in big[:12]],
                  "n_no_straight": sum(1 for d in CY if d["straight"] == 0),
                  "n_half_straight": sum(1 for d in CY if d["straight_pct"] >= 50)}
cyd = {d["iso"]: d for d in CY}
for iso in ("USA", "CAN", "EGY", "LBY", "DZA", "MLI", "MRT", "SDN", "TCD", "NER", "NAM", "BWA", "SAU", "CHL", "ARG", "FRA", "DEU", "GBR", "CHN", "RUS", "IND", "BRA"):
    if iso in cyd:
        R["countries"][iso] = {k: cyd[iso][k] for k in ("km", "straight_pct", "water_pct", "mountain_pct", "other_pct", "straight")}

# ---------------------------------------------------------------- longest straight segments and who drew them
SEG.sort(key=lambda s: -s["km"])
NTOP = 40
rows = []
for i, s in enumerate(SEG):
    t = TR.match(s)
    k = s["kind"]
    if k == "parallel":
        desc = f"Parallel {abs(s['val']):.2f} degrees {'N' if s['val'] >= 0 else 'S'}"
    elif k == "meridian":
        desc = f"Meridian {abs(s['val']):.2f} degrees {'E' if s['val'] >= 0 else 'W'}"
    else:
        desc = "Straight line (not a parallel or meridian)"
    rows.append({"rank": i + 1, "a": s["a"], "b": s["b"], "name": f"{nm(s['a'])} and {nm(s['b'])}", "cont": s["cont"], "km": round(s["km"]),
                 "kind": k, "value": s["val"], "desc": desc, "status": s["fc"],
                 "lon0": round(s["c"][0][0], 4), "lat0": round(s["c"][0][1], 4), "lon1": round(s["c"][1][0], 4), "lat1": round(s["c"][1][1], 4),
                 "mid": s["mid"], "path": s["path"],
                 "treaty": t["treaty"] if t else "", "year": t["year"] if t else None, "year_label": t["year_label"] if t else "",
                 "powers": t["powers"] if t else "", "later": t["later"] if t else "", "conf": t["conf"] if t else "",
                 "src": t["src"] if t else "", "line": t["line"] if t else "", "note": t.get("note", "") if t else ""})
missing = [r for r in rows[:NTOP] if not r["treaty"]]
assert not missing, [(r["rank"], r["name"], r["km"]) for r in missing]
top40 = rows[:NTOP]
R["top"] = [{k: r[k] for k in ("rank", "name", "a", "b", "km", "kind", "value", "desc", "treaty", "year", "year_label", "powers", "conf", "cont", "mid")} for r in top40]
R["top_n"] = NTOP
R["top_km"] = sum(r["km"] for r in top40)
R["top_pct_of_straight"] = pct(R["top_km"], world["straight"])
yrs = [r["year"] for r in top40 if r["year"]]
R["top_years"] = {"n_dated": len(yrs), "first": min(yrs), "last": max(yrs), "median": int(np.median(yrs)),
                  "n_1880_1914": sum(1 for y in yrs if 1880 <= y <= 1914), "n_before_1880": sum(1 for y in yrs if y < 1880),
                  "n_1915_1945": sum(1 for y in yrs if 1915 <= y <= 1945), "n_after_1945": sum(1 for y in yrs if y > 1945),
                  "km_1880_1914": sum(r["km"] for r in top40 if r["year"] and 1880 <= r["year"] <= 1914),
                  "n_low": sum(1 for r in top40 if r["conf"] == "low"), "n_medium": sum(1 for r in top40 if r["conf"] == "medium"),
                  "n_high": sum(1 for r in top40 if r["conf"] == "high"), "n_undated": sum(1 for r in top40 if not r["year"])}
R["top_years"]["pct_1880_1914_km"] = pct(R["top_years"]["km_1880_1914"], R["top_km"])
POW = ["United Kingdom", "France", "Germany", "Italy", "Portugal", "Spain", "United States", "Russian", "Soviet", "Netherlands", "Egypt", "Saudi"]
R["top_powers"] = {p: sum(1 for r in top40 if p in r["powers"]) for p in POW}
R["top_africa_n"] = sum(1 for r in top40 if r["cont"] == "Africa")
R["top_africa_km"] = sum(r["km"] for r in top40 if r["cont"] == "Africa")
R["top_europe_powers_n"] = sum(1 for r in top40 if any(p in r["powers"] for p in ("United Kingdom", "France", "Germany", "Italy", "Portugal", "Spain", "Netherlands", "Russian", "Congo Free State")))
R["seg_longest"] = R["top"][0]

# named examples quoted in words
def seg_of(a, b, kind=None, lo=None, hi=None):
    c = [r for r in rows if {r["a"], r["b"]} == {a, b} and (kind is None or (r["kind"] == kind and lo <= r["value"] <= hi))]
    return max(c, key=lambda r: r["km"])
EX = {"us49": seg_of("CAN", "USA", "parallel", 48.5, 49.5), "us141": seg_of("CAN", "USA", "meridian", -141.5, -140.5),
      "eg25": seg_of("EGY", "LBY"), "eg22": seg_of("EGY", "SDN", "parallel", 21.5, 22.5), "ly": seg_of("LBY", "TCD"),
      "ml": seg_of("MLI", "MRT"), "tf": seg_of("ARG", "CHL", "meridian", -69, -68), "ng": seg_of("IDN", "PNG"),
      "kt": seg_of("KEN", "TZA"), "mx": seg_of("MEX", "USA")}
R["ex"] = {k: {"km": v["km"], "rank": v["rank"], "year": v["year"], "desc": v["desc"]} for k, v in EX.items()}
R["ex"]["eg22_total"] = round(sum(r["km"] for r in rows if {r["a"], r["b"]} == {"EGY", "SDN"}))
R["ex"]["us_ca_straight"] = round(bt[("CAN", "USA")]["straight"]); R["ex"]["us_ca_total"] = round(bt[("CAN", "USA")]["km"])
R["ex"]["us_ca_pct"] = bt[("CAN", "USA")]["straight_pct"]

# ---------------------------------------------------------------- Is Africa the straightest?
af = CT["Africa"]
R["africa"] = {"rank_share": [a["name"] for a in cont].index("Africa") + 1, "straight_pct": af["straight_pct"], "straight_km": af["straight"],
               "share_of_world_straight": af["share_of_world_straight"], "astro_pct": af["astro_pct"],
               "most_straight_km": max(cont, key=lambda a: a["straight"])["name"],
               "top_share_name": cont[0]["name"], "top_share_pct": cont[0]["straight_pct"],
               "second_share_name": cont[1]["name"], "second_share_pct": cont[1]["straight_pct"]}
# North America without the United States and Canada border
na = CT["North America"]; usca = bt[("CAN", "USA")]
R["africa"]["na_without_usca_pct"] = pct(na["straight"] - usca["straight"], na["km"] - usca["km"])
R["africa"]["na_usca_share_of_na_straight"] = pct(usca["straight"], na["straight"])
# rank of Africa under every straightness setting
ranks = []
for s in SENS["straight"]:
    sh = {c: 100 * s["cont"][c]["straight"] / sum(s["cont"][c].values()) for c in CONTS}
    order = sorted(CONTS, key=lambda c: -sh[c])
    ranks.append({"tol": s["tol"], "lmin": s["lmin"], "world_pct": pct(s["straight"], sum(s[k] for k in CLASSES)),
                  "africa_pct": r1(sh["Africa"]), "first": order[0], "first_pct": r1(sh[order[0]]), "africa_rank": order.index("Africa") + 1,
                  **{c: r1(sh[c]) for c in CONTS}})
R["sens_straight"] = ranks
R["africa"]["n_settings"] = len(ranks)
R["africa"]["n_settings_first"] = sum(1 for r in ranks if r["africa_rank"] == 1)
R["africa"]["n_settings_top2"] = sum(1 for r in ranks if r["africa_rank"] <= 2)
# by count of borders, median border
R["africa"]["mostly_straight_pct"] = af["mostly_straight_pct"]; R["africa"]["n_borders"] = af["n_borders"]
R["africa"]["n_mostly_straight"] = af["n_mostly_straight"]
R["africa"]["rank_mostly_straight"] = sorted(CONTS, key=lambda c: -CT[c]["mostly_straight_pct"]).index("Africa") + 1
R["africa"]["rank_astro"] = sorted(CONTS, key=lambda c: -CT[c]["astro_pct"]).index("Africa") + 1
# Oceania has a single land border (New Guinea), so the fair comparison is among the five other continents
C5 = [c for c in CONTS if c != "Oceania"]
for r in ranks:
    o5 = sorted(C5, key=lambda c: -r[c]); r["first5"] = o5[0]; r["africa_rank5"] = o5.index("Africa") + 1
R["africa"]["rank_share5"] = sorted(C5, key=lambda c: -CT[c]["straight_pct"]).index("Africa") + 1
R["africa"]["n_settings_first5"] = sum(1 for r in ranks if r["africa_rank5"] == 1)
R["africa"]["n_settings_second5"] = sum(1 for r in ranks if r["africa_rank5"] == 2)
R["africa"]["n_settings_na_first5"] = sum(1 for r in ranks if r["first5"] == "North America")
R["africa"]["rank_mostly_straight5"] = sorted(C5, key=lambda c: -CT[c]["mostly_straight_pct"]).index("Africa") + 1
R["africa"]["rank_astro5"] = sorted(C5, key=lambda c: -CT[c]["astro_pct"]).index("Africa") + 1
R["africa"]["first_mostly_straight5"] = sorted(C5, key=lambda c: -CT[c]["mostly_straight_pct"])[0]
R["africa"]["first_astro5"] = sorted(C5, key=lambda c: -CT[c]["astro_pct"])[0]
R["africa"]["oceania_n_borders"] = CT["Oceania"]["n_borders"]
w50 = [r for r in ranks if r["lmin"] == 50.0]
R["sens_summary"] = {"lmin50_min": min(r["world_pct"] for r in w50), "lmin50_max": max(r["world_pct"] for r in w50),
                     "lmin100_min": min(r["world_pct"] for r in ranks if r["lmin"] == 100.0), "lmin100_max": max(r["world_pct"] for r in ranks if r["lmin"] == 100.0),
                     "all_min": min(r["world_pct"] for r in ranks), "all_max": max(r["world_pct"] for r in ranks)}
for key_, rows_ in (("water", SENS["water"]), ("mountain", SENS["mountain"])):
    v = [pct(r[key_], sum(r[k] for k in CLASSES)) for r in rows_]
    R["sens_summary"][key_ + "_min"] = min(v); R["sens_summary"][key_ + "_max"] = max(v)
R["sens_water"] = [{"river": r["river"], "wmin": r["wmin"], "pct": pct(r["water"], sum(r[k] for k in CLASSES))} for r in SENS["water"]]
R["sens_mountain"] = [{"rel": r["rel"], "r": r["r"], "pct": pct(r["mountain"], sum(r[k] for k in CLASSES))} for r in SENS["mountain"]]
sc = {"10m": {"total": round(WT), "straight_pct": pct(world["straight"], WT)}}
for s in SENS["scale"]:
    if s["tol"] == MAIN["tol"]:
        sc[s["scale"]] = {"total": round(s["total"]), "straight_pct": pct(s["straight"], s["total"])}
R["scale"] = sc

# ---------------------------------------------------------------- cross-check: mountain borders inside Natural Earth's named ranges
rg = [f for f in jload(f"{NE}/ne_10m_geography_regions_polys.geojson")["features"] if f["properties"].get("FEATURECLA") == "Range/mtn"]
RG = [shape(f["geometry"]).buffer(0) for f in rg]; RT = STRtree(RG); RP = [prep(g) for g in RG]
inr = defaultdict(float)
for p in PC:
    c = p["c"]; m = c[len(c) // 2]; pt = Point(m)
    hit = any(RP[i].contains(pt) for i in RT.query(pt))
    if hit: inr[p["cls"]] += p["km"]
R["ranges"] = {"n": len(rg), **{k + "_in_range_pct": pct(inr[k], world[k]) for k in CLASSES}}

# ---------------------------------------------------------------- rivers named in the top water borders (a few, for the text)
R["water_examples"] = top("water", 10)
R["mountain_examples"] = top("mountain", 10)
R["retrieved"] = "2026"

# ---------------------------------------------------------------- data files
with open(f"{DATA}/borders.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["iso_a", "country_a", "iso_b", "country_b", "continent", "km", "straight_km", "water_km", "mountain_km", "other_km",
                                   "straight_pct", "water_pct", "mountain_pct", "other_pct"])
    for d in BT:
        w.writerow([d["a"], nm(d["a"]), d["b"], nm(d["b"]), d["cont"], d["km"], d["straight"], d["water"], d["mountain"], d["other"],
                    d["straight_pct"], d["water_pct"], d["mountain_pct"], d["other_pct"]])
with open(f"{DATA}/countries.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["iso", "country", "continent", "border_km", "neighbours", "straight_km", "water_km", "mountain_km", "other_km",
                                   "straight_pct", "water_pct", "mountain_pct", "other_pct"])
    for d in sorted(CY, key=lambda d: d["name"]):
        w.writerow([d["iso"], d["name"], d["cont"], d["km"], d["n_neighbours"], d["straight"], d["water"], d["mountain"], d["other"],
                    d["straight_pct"], d["water_pct"], d["mountain_pct"], d["other_pct"]])
with open(f"{DATA}/straight_segments.csv", "w", newline="", encoding="utf-8") as f:
    cols = ["rank", "a", "b", "name", "cont", "km", "kind", "value", "status", "lon0", "lat0", "lon1", "lat1", "treaty", "year", "year_label", "powers", "later", "conf", "src", "note"]
    w = csv.writer(f); w.writerow([c if c not in ("a", "b") else "iso_" + c for c in cols])
    for r in rows:
        w.writerow([dash(r[c]) if isinstance(r[c], str) else ("" if r[c] is None else r[c]) for c in cols])
with open(f"{DATA}/treaties.csv", "w", newline="", encoding="utf-8") as f:
    cols = ["k", "line", "treaty", "year", "year_label", "powers", "later", "conf", "src", "note"]
    w = csv.writer(f); w.writerow(["border"] + cols[1:])
    for t in TR.T:
        w.writerow([dash(str(t.get(c, "") if t.get(c) is not None else "")) for c in cols])
with open(f"{DATA}/sensitivity.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["tol_km", "min_length_km", "world_straight_pct"] + [c + "_straight_pct" for c in CONTS] + ["first", "africa_rank"])
    for r in ranks:
        w.writerow([r["tol"], r["lmin"], r["world_pct"]] + [r[c] for c in CONTS] + [r["first"], r["africa_rank"]])

# classified lines for reuse (GeoJSON, 5 decimals) and for the page (simplified, 4 decimals)
feats, web = [], []
segpath = defaultdict(list)
for r in rows:
    segpath[r["path"]].append(r)
for i, p in enumerate(PC):
    b = B[p["path"]]
    ls = LineString(p["c"])
    pr = {"a": b["a"], "b": b["b"], "class": p["cls"], "km": round(p["km"], 1), "status": b["fc"], "water_line": b["water"]}
    if p["cls"] == "straight":
        # which straight segment is this piece? the segment whose midpoint lies on it
        best = None
        for r in segpath[p["path"]]:
            d = ls.distance(Point(r["mid"]))
            if best is None or d < best[0]: best = (d, r)
        if best and best[0] < 0.01:
            pr["seg"] = best[1]["rank"]
    feats.append({"type": "Feature", "properties": pr, "geometry": {"type": "LineString", "coordinates": [[round(x, 5), round(y, 5)] for x, y in p["c"]]}})
    sl = ls.simplify(0.003, preserve_topology=False)
    cc = [[round(x, 4), round(y, 4)] for x, y in sl.coords]
    web.append({"type": "Feature", "properties": {"d": f"{b['a']}-{b['b']}", "c": CLASSES.index(p["cls"]), "km": round(p["km"]), **({"s": pr["seg"]} if "seg" in pr else {})},
                "geometry": {"type": "LineString", "coordinates": cc}})
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/borders_classified.geojson")
jsave({"type": "FeatureCollection", "features": web}, f"{DATA}/map_lines.json")
# page data: borders, segments with treaties, countries
site = {"borders": {f"{d['a']}-{d['b']}": [d["name"], d["cont"], round(d["km"]), d["straight_pct"], d["water_pct"], d["mountain_pct"], d["other_pct"]] for d in BT},
        "segs": {r["rank"]: {k: r[k] for k in ("name", "km", "desc", "treaty", "year_label", "powers", "later", "conf", "src", "note", "status", "line")} for r in rows},
        "countries": {d["iso"]: [d["name"], d["cont"], d["km"], d["straight_pct"], d["water_pct"], d["mountain_pct"], d["other_pct"], d["n_neighbours"]] for d in CY}}
jsave(site, f"{DATA}/site.json")
from pyproj import Geod
_G = Geod(ellps="WGS84")
R["edges_over_50"] = int(sum((np.array(_G.inv(*np.array(b["c"])[:-1].T, *np.array(b["c"])[1:].T)[2]) > 50000).sum() for b in B))
R["cont"] = {a["name"].replace(" ", "_"): a for a in cont}
jsave(R, f"{DATA}/results.json", indent=1)
print("world", R["world"]); print("continents", [(a["name"], a["straight_pct"], a["water_pct"], a["mountain_pct"]) for a in cont])
print("africa", R["africa"]); print("top years", R["top_years"], R["top_powers"]); print("scale", R["scale"], "ranges", R["ranges"])
print("sizes", {f: os.path.getsize(f"{DATA}/{f}") // 1024 for f in os.listdir(DATA)})
