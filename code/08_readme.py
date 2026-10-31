"""README.md and LICENSE, numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
w, a, C, ty = R["world"], R["africa"], R["cont"], R["top_years"]
size = lambda f: f"{os.path.getsize(os.path.join(DATA, f)) / 1e6:.1f} MB"
readme = f"""# Where the borders are straight

Every international land border in the world, {w['km']:,} km in Natural Earth's 1:10 million boundary lines, classified kilometre by kilometre as ruler-straight (a parallel, a meridian or another straight line), river or lake, through mountains, or other. For the {R['top_n']} longest straight segments, a hand-compiled, cited table of the treaty or agreement that set each line, its year and the powers involved. Plus a test of the popular claim that Africa's borders are the straightest.

Interactive page: {URL}
Paper: {DOI_URL}
Blog post: {BLOG}

## Headline results

- {w['straight_pct']:.1f}% of the world's land border length is ruler-straight ({w['straight']:,} km in {R['straight']['n_segments']} segments of at least 50 km); {w['water_pct']:.1f}% follows rivers or lakes, {w['mountain_pct']:.1f}% runs through mountains and {w['other_pct']:.1f}% is other.
- Africa has the most straight border, {a['share_of_world_straight']:.1f}% of the world's, and the largest share of mostly straight borders. But by share of length North America ({C['North_America']['straight_pct']:.1f}%) is straighter than Africa ({C['Africa']['straight_pct']:.1f}%) under all {a['n_settings']} settings tested, mainly because of the border between Canada and the United States ({R['ex']['us_ca_pct']:.1f}% straight). Without it North America is {a['na_without_usca_pct']:.1f}%. Europe is {C['Europe']['straight_pct']:.1f}% straight.
- The longest straight segment is the 49th parallel between Canada and the United States ({R['ex']['us49']['km']:,} km; 1818 and 1846), then the 141st meridian between Alaska and Yukon ({R['ex']['us141']['km']:,} km; 1825), Mali and Mauritania ({R['ex']['ml']['km']} km), Libya and Chad ({R['ex']['ly']['km']} km) and Egypt and Libya's 25th meridian ({R['ex']['eg25']['km']} km; 1925).
- Of the {ty['n_dated']} dated lines among the {R['top_n']} longest, {ty['n_1880_1914']} were set between 1880 and 1914; the United Kingdom was a party to {R['top_powers']['United Kingdom']}, France to {R['top_powers']['France']}. {ty['n_low']} attributions are marked low confidence.
- Map scale matters: the same method finds {R['scale']['50m']['straight_pct']:.1f}% straight on Natural Earth's 1:50 million lines and {R['scale']['110m']['straight_pct']:.1f}% on its 1:110 million lines.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/06_build_site.py`; loads `data/site.json`, `data/map_lines.json`, `data/countries_lite.json`). |
| `header.png` | Social card, 1200 x 630. |
| `data/borders_classified.geojson` | Every border as classified pieces: country codes, class, length, legal status, straight segment rank ({size('borders_classified.geojson')}). |
| `data/borders.csv` | {w['n_borders']} borders (country pairs): length and share by class. |
| `data/countries.csv` | {R['countries']['n']} countries and territories: border length and share by class. |
| `data/straight_segments.csv` | All {R['straight']['n_segments']} straight segments, ranked, with type (parallel, meridian, line), end points and, for the longest, treaty, year, powers, confidence and sources. |
| `data/treaties.csv` | The hand-compiled treaty table. |
| `data/sensitivity.csv` | World and continent straight shares under twelve settings. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/site.json`, `data/map_lines.json`, `data/countries_lite.json`, `data/cities.json` | Page data. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. `code/treaties.py` holds the treaty table with its sources. |
| `release/` | Paper PDF and LaTeX source, blog post and figures, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots from the browser check. |

## Method in brief

- Borders: Natural Earth 1:10 million admin-0 land boundary lines (version {R['meta']['ne_version']}): international boundaries plus disputed, indefinite and line-of-control lines; UN buffer zones, demilitarised zones and leased bases left out.
- Straight: every vertex within 1 km of one great circle or rhumb line (which includes parallels), for at least 50 km, without doubling back. Typed as parallel, meridian or other straight line. Lines Natural Earth marks as water boundaries count as water.
- River or lake: within 3 km of a Natural Earth river centre line or lake shore, or inside a lake, for at least 15 km.
- Mountains: ETOPO5 elevation of at least 2,500 m, or at least 300 m with 300 m of local relief within about 18 km (simplified from the UNEP-WCMC definition, Kapos et al. 2000), for at least 20 km. This says the border runs through mountains, not that it follows a crest.
- Priority: straight, then water, then mountains, then other. Sensitivity tests in `code/02_classify.py` and the paper.
- Treaties: compiled by hand from Brownlie (1979) African Boundaries, Biger (1995) The Encyclopedia of International Boundaries, the US State Department's International Boundary Studies, the ICJ judgment on Libya and Chad (1994), the boundary commissions, and Wikipedia's border articles. Corrections welcome.
- Caveats: a measure of a generalised map, not the ground; small border rivers are missing from Natural Earth's rivers; the treaty table is secondary and marked by confidence.

## How to rerun

Needs Python 3 with numpy, scipy, shapely, pyproj, netCDF4, matplotlib, fontTools and Pillow; xelatex and pdftotext; node with Playwright for QA. Raw inputs are read in place (paths in `code/common.py`): Natural Earth GeoJSON from https://github.com/nvkelso/natural-earth-vector (`geojson/`), saved in `/home/claude/newdata/raw3/borders/`, and ETOPO5 (`data/etopo5.cdf` from https://github.com/NOAA-PMEL/FerretDatasets), saved in `/home/claude/newdata/raw3/dem/`. Intermediate files go to `/dev/shm/borders` (set `BORDERTMP` to change).

```
python3 code/01_borders.py      # read and join the boundary lines
python3 code/02_classify.py     # classify, sensitivity, map scale (about 7 minutes)
python3 code/03_results.py      # results.json and data files
python3 code/04_geo.py          # page outlines and city names
python3 code/05_figures.py      # header, blog and paper figures
python3 code/06_build_site.py   # index.html (checks every fact stated in words)
python3 code/07_paper.py        # paper PDF
python3 code/08_readme.py       # README and LICENSE
python3 code/09_release.py      # blog post, Zenodo files
python3 code/10_post.py         # reddit/post.md
python3 reddit/collage.py       # collage
node code/11_qa.js              # browser check and screenshots
```

## Sources and licences

- Natural Earth (https://www.naturalearthdata.com/), boundary lines, countries, rivers, lakes, physical regions and populated places. Public domain.
- ETOPO5 5 arc-minute global relief, NOAA National Geophysical Data Center (1988). Public domain.
- Treaty facts from the published sources above; Wikipedia used for facts only (CC BY-SA 4.0 text is not reproduced).
- Base map tiles on the page: © Esri.

Code is MIT; text, figures and derived data are CC BY 4.0 (see LICENSE).

## Citation

Hotham, T. (2026) Where the borders are straight: ruler lines, rivers and mountains on every international land border, and who drew the longest straight lines. Zenodo. {DOI_URL}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
check_dashes(readme.replace("|---|---|", ""), "readme"); check_words(readme, "readme")
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, the paper, the figures and the derived data in data/ are
released under the Creative Commons Attribution 4.0 International licence
(CC BY 4.0), https://creativecommons.org/licenses/by/4.0/. They are derived
from Natural Earth and ETOPO5 (NOAA), both in the public domain.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
print("README", len(readme.split()), "words")
