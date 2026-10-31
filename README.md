# Where the borders are straight

Every international land border in the world, 233,534 km in Natural Earth's 1:10 million boundary lines, classified kilometre by kilometre as ruler-straight (a parallel, a meridian or another straight line), river or lake, through mountains, or other. For the 40 longest straight segments, a hand-compiled, cited table of the treaty or agreement that set each line, its year and the powers involved. Plus a test of the popular claim that Africa's borders are the straightest.

Interactive page: https://maps.tristanhotham.com/straight-borders/
Paper: https://doi.org/10.5281/zenodo.23847974
Blog post: https://blog.tristanhotham.com/2026/10/31/straight-borders/

## Headline results

- 19.4% of the world's land border length is ruler-straight (45,232 km in 312 segments of at least 50 km); 20.9% follows rivers or lakes, 24.7% runs through mountains and 35.0% is other.
- Africa has the most straight border, 53.8% of the world's, and the largest share of mostly straight borders. But by share of length North America (45.9%) is straighter than Africa (30.2%) under all 12 settings tested, mainly because of the border between Canada and the United States (59.3% straight). Without it North America is 28.9%. Europe is 1.5% straight.
- The longest straight segment is the 49th parallel between Canada and the United States (2,020 km; 1818 and 1846), then the 141st meridian between Alaska and Yukon (1,042 km; 1825), Mali and Mauritania (945 km), Libya and Chad (812 km) and Egypt and Libya's 25th meridian (803 km; 1925).
- Of the 40 dated lines among the 40 longest, 21 were set between 1880 and 1914; the United Kingdom was a party to 21, France to 11. 1 attributions are marked low confidence.
- Map scale matters: the same method finds 25.4% straight on Natural Earth's 1:50 million lines and 83.6% on its 1:110 million lines.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/06_build_site.py`; loads `data/site.json`, `data/map_lines.json`, `data/countries_lite.json`). |
| `header.png` | Social card, 1200 x 630. |
| `data/borders_classified.geojson` | Every border as classified pieces: country codes, class, length, legal status, straight segment rank (5.8 MB). |
| `data/borders.csv` | 332 borders (country pairs): length and share by class. |
| `data/countries.csv` | 170 countries and territories: border length and share by class. |
| `data/straight_segments.csv` | All 312 straight segments, ranked, with type (parallel, meridian, line), end points and, for the longest, treaty, year, powers, confidence and sources. |
| `data/treaties.csv` | The hand-compiled treaty table. |
| `data/sensitivity.csv` | World and continent straight shares under twelve settings. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/site.json`, `data/map_lines.json`, `data/countries_lite.json`, `data/cities.json` | Page data. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. `code/treaties.py` holds the treaty table with its sources. |
| `release/` | Paper PDF and LaTeX source, blog post and figures, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots from the browser check. |

## Method in brief

- Borders: Natural Earth 1:10 million admin-0 land boundary lines (version 5.2.0-pre): international boundaries plus disputed, indefinite and line-of-control lines; UN buffer zones, demilitarised zones and leased bases left out.
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

Hotham, T. (2026) Where the borders are straight: ruler lines, rivers and mountains on every international land border, and who drew the longest straight lines. Zenodo. https://doi.org/10.5281/zenodo.23847974

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
