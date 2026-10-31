"""Page geometry: simplified Natural Earth 50m country outlines (data/countries_lite.json) for the country layer and the
search highlight, and the larger Natural Earth populated places as city labels (data/cities.json)."""
from shapely.geometry import shape, mapping
from common import *

GEO = "/home/claude/newdata/raw/geo"
NM = jload(f"{WORK}/names.json")["name"]
out = []
for f in jload(f"{GEO}/ne_50m_admin_0_countries.geojson")["features"]:
    p = f["properties"]; iso = p["ADM0_A3"]
    g = shape(f["geometry"]).simplify(0.04, preserve_topology=True)
    if g.is_empty:
        continue
    m = mapping(g)
    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 3), round(c[1], 3)]
    out.append({"type": "Feature", "properties": {"iso": iso, "n": NM.get(iso, p["NAME_EN"])}, "geometry": {"type": m["type"], "coordinates": rnd(m["coordinates"])}})
jsave({"type": "FeatureCollection", "features": out}, f"{DATA}/countries_lite.json")
ci = []
for f in jload(PLACES)["features"]:
    p = f["properties"]
    if (p.get("pop_max") or 0) >= 300000:
        ci.append({"name": p["name"], "lat": round(p["latitude"], 3), "lon": round(p["longitude"], 3), "pop": int(p["pop_max"])})
ci.sort(key=lambda c: -c["pop"])
jsave(ci, f"{DATA}/cities.json")
print(len(out), "countries", os.path.getsize(f"{DATA}/countries_lite.json") // 1024, "KB;", len(ci), "cities")
