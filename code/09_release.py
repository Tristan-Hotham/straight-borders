"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.23847974, https://doi.org/10.5281/zenodo.23847974 and https://blog.tristanhotham.com/2026/10/31/straight-borders/ are left for the publisher to fill."""
import shutil, zipfile, json as _json
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release")
NAME = "Hotham_Where_the_Borders_Are_Straight"

# facts written out in words in the blog (alt text included); the page build checks the rest
import importlib.util
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "06_build_site.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); m.facts()
st = R["straight"]
assert 30 <= st["parallel_pct_of_straight"] + st["meridian_pct_of_straight"] <= 40          # "about a third"
assert [round(R["scale"][s]["straight_pct"]) for s in ("10m", "50m", "110m")] == [19, 25, 84]
C = R["cont"]
assert [round(C[c]["straight_pct"]) for c in ("Oceania", "North_America", "Africa", "South_America", "Asia")] == [88, 46, 30, 13, 12] and C["Europe"]["straight_pct"] < 2
t = R["top"]
assert [x["km"] for x in t[:5]] == [2020, 1042, 945, 812, 803]
assert [b["name"] for b in R["borders"]["top_water_km"][:4]] == ["China and Russia", "Canada and United States", "Argentina and Paraguay", "Mexico and United States"]
assert [b["name"] for b in R["borders"]["top_mountain_km"][:3]] == ["Argentina and Chile", "China and India", "Afghanistan and Pakistan"]

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = fill(post, R)
assert not re.search(r"\{\{(?!IMG\||DOI_URL\}\}|BLOG_URL\}\})", post), re.findall(r"\{\{[^}]*\}\}", post)[:5]
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, used
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for line in post.splitlines():                       # each image token on its own line, not wrapped in a block
    if "{{IMG|" in line:
        assert line.startswith("{{IMG|") and line.endswith("}}"), line[:60]
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
check_dashes(vis, "blog"); check_words(post, "blog")
assert AI in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Where the borders are straight: who drew the world's ruler lines, and is Africa really the straightest?",
        "slug": "straight-borders",
        "excerpt": f"I measured every land border on Earth. {R['world']['straight_pct']:.0f}% is ruler-straight, and Africa holds {R['africa']['share_of_world_straight']:.0f}% of it, but North America is straighter by share. Plus the treaties behind the {R['top_n']} longest straight lines.",
        "seo_description": "Every land border in the world classified as straight, river, mountain or other, with the treaties behind the longest straight lines.",
        "tags": ["borders", "maps", "geography", "Africa", "colonialism", "treaties", "data visualisation", "Natural Earth"],
        "header_alt": f"Title card reading 'Where the borders are straight' in black on cream, beside a world map of land borders coloured by kind: red straight lines across the Sahara, Arabia, southern Africa and the 49th parallel, blue rivers, ochre mountains and grey other lines. Text: {R['world']['straight_pct']:.0f}% of the world's land border length is ruler-straight; Africa holds {R['africa']['share_of_world_straight']:.0f}% of it; North America is straighter by share, {R['cont']['North_America']['straight_pct']:.0f}%."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/straight-borders_code_and_data.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            p = os.path.join(ROOT, d, fn)
            if os.path.isdir(p) or fn.endswith(".pyc"):
                continue
            z.write(p, f"straight-borders/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        if os.path.exists(os.path.join(ROOT, fn)):
            z.write(os.path.join(ROOT, fn), f"straight-borders/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&")
assert "\\" not in ab, ab
zmeta = {"title": "Where the Borders Are Straight: Ruler Lines, Rivers and Mountains on Every International Land Border, and Who Drew the Longest Straight Lines",
         "upload_type": "publication", "publication_type": "workingpaper",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{URL}\">{URL}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {BLOG}.</p>"
                        "<p>Licences: text, figures and derived data CC BY 4.0; code MIT. Natural Earth and ETOPO5 are public domain.</p>"
                        f"<p>{AI}</p>",
         "keywords": ["international boundaries", "borders", "geometric boundaries", "straight borders", "Africa", "colonialism", "treaties",
                      "cartographic generalisation", "Natural Earth", "maps"],
         "license": "cc-by-4.0",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": URL, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://github.com/nvkelso/natural-earth-vector", "relation": "isDerivedFrom", "resource_type": "dataset"}]}
jsave(zmeta, f"{Z}/metadata.json", indent=2)
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
check_dashes(s, "metadata"); check_words(s, "metadata")
print("blog words", words, "; images", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
