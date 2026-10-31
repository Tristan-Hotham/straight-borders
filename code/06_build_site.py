"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; results and city names are embedded; data/site.json, data/map_lines.json and data/countries_lite.json
are loaded by the page. Facts stated in words are checked here against the data (the blog, paper and post reuse them).
The full-screen map snippet (from the drinks-map reference, code/fullscreen_snippet.html) goes before </body>.
10.5281/zenodo.23847974, https://doi.org/10.5281/zenodo.23847974 and https://blog.tristanhotham.com/2026/10/31/straight-borders/ are left for the publisher to fill."""
import csv
from common import *

R = jload(f"{DATA}/results.json")
SEG = list(csv.DictReader(open(f"{DATA}/straight_segments.csv", encoding="utf-8")))
BRD = {(r["iso_a"], r["iso_b"]): r for r in csv.DictReader(open(f"{DATA}/borders.csv", encoding="utf-8"))}
CT, AF = R["cont"], R["africa"]
C5 = ["Africa", "Asia", "Europe", "North_America", "South_America"]


def facts():
    """Every fact stated in words on the page, blog, paper or post."""
    assert R["continents"][0]["name"] == "Oceania" and AF["oceania_n_borders"] == 1 and CT["Oceania"]["n_borders"] == 1
    assert {(r["iso_a"], r["iso_b"]) for r in BRD.values() if r["continent"] == "Oceania"} == {("IDN", "PNG")}
    assert max(C5, key=lambda c: CT[c]["straight_pct"]) == "North_America" and AF["rank_share5"] == 2
    assert min(C5, key=lambda c: CT[c]["straight_pct"]) == "Europe"
    assert AF["most_straight_km"] == "Africa" and AF["rank_mostly_straight5"] == 1
    assert AF["n_settings_na_first5"] == AF["n_settings"] == 12 and AF["n_settings_second5"] == 12
    assert AF["na_without_usca_pct"] < CT["Africa"]["straight_pct"]           # "just below Africa"
    assert CT["Africa"]["straight_pct"] - AF["na_without_usca_pct"] < 3
    assert CT["Africa"]["astro_pct"] < 44
    assert max(C5, key=lambda c: CT[c]["mountain_pct"]) == "Asia"
    # Europe: five short pieces, the longest Poland and Russia
    eu = sorted([s for s in SEG if s["cont"] == "Europe"], key=lambda s: -int(s["km"]))
    assert len(eu) == 5 and {eu[0]["iso_a"], eu[0]["iso_b"]} == {"POL", "RUS"}
    # longest segments named in words
    t = R["top"]
    assert t[0]["name"] == "Canada and United States" and t[0]["kind"] == "parallel" and t[0]["year"] == 1818
    assert t[1]["name"] == "Canada and United States" and t[1]["kind"] == "meridian" and t[1]["year"] == 1825
    assert [x["name"] for x in t[2:5]] == ["Mali and Mauritania", "Libya and Chad", "Egypt and Libya"] and t[4]["kind"] == "meridian"
    assert R["ex"]["eg22"]["year"] == 1899 and len([s for s in SEG if {s["iso_a"], s["iso_b"]} == {"EGY", "SDN"}]) == 3
    assert R["top_years"]["n_before_1880"] == 6 and all(x["cont"] == "North America" for x in t if x["year"] and x["year"] < 1880)
    late = [x for x in t if x["year"] and x["year"] > 1945]
    assert R["top_years"]["n_after_1945"] == 4 and sum(1 for x in late if {"SAU", "OMN", "YEM", "ARE"} & {x["a"], x["b"]}) == 3 and any({x["a"], x["b"]} == {"ETH", "SOM"} for x in late)
    assert R["top_years"]["n_low"] == 1 and [x for x in t if x["conf"] == "low"][0]["name"] == "Ethiopia and Somalia"
    arab = {x["year"] for x in t if "SAU" in (x["a"], x["b"])}
    assert min(arab) == 1974 and max(arab) == 2000
    assert any(x["year"] == 1881 and x["a"] == "ARG" for x in t) and any(x["year"] == 1853 for x in t)
    # rivers and mountains
    w = R["borders"]["top_water_km"]; m = R["borders"]["top_mountain_km"]
    assert w[0]["name"] == "China and Russia" and m[0]["name"] == "Argentina and Chile"
    assert float(BRD[("ARG", "PRY")]["water_pct"]) == 100.0 and float(BRD[("CHN", "IND")]["mountain_pct"]) == 100.0
    for k, col in ((("CAF", "COD"), "water_pct"), (("COD", "COG"), "water_pct"), (("BWA", "ZAF"), "water_pct")):
        assert float(BRD[k][col]) > 70, k
    # countries
    cy = R["countries"]
    assert [x["iso"] for x in cy["top_straight_pct"][:4]] == ["SOM", "EGY", "SOL", "SAU"]
    assert cy["FRA"]["straight"] == 0 and cy["DEU"]["straight"] == 0 and cy["GBR"]["straight"] == 0
    s = R["sens_straight"]
    assert max(r["world_pct"] for r in s) == next(r["world_pct"] for r in s if r["tol"] == 2.0 and r["lmin"] == 25.0)
    assert R["scale"]["10m"]["straight_pct"] < R["scale"]["50m"]["straight_pct"] < R["scale"]["110m"]["straight_pct"]
    assert R["ranges"]["mountain_in_range_pct"] > 3 * R["ranges"]["other_in_range_pct"]


def build():
    facts()
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = fill(tpl, R)
    assert not re.search(r"\{\{(?!DOI\}\}|DOI_URL\}\}|BLOG_URL\}\})", html), re.findall(r"\{\{[^}]*\}\}", html)[:5]
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    cities = [c for c in jload(f"{DATA}/cities.json")][:900]
    html = html.replace("/*RESULTS*/", J(R)).replace("/*CITIES*/", J(cities))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    check_dashes(vis, "page text")
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    check_words(html, "page")
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
