"""reddit/post.md: title, body and source comment, numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
w, a, C = R["world"], R["africa"], R["cont"]
t = f"""## Title

[OC] Where the borders are straight: {w['straight_pct']:.0f}% of the world's land border length is ruler-straight. Africa has {a['share_of_world_straight']:.0f}% of it, but North America is straighter by share ({C['North_America']['straight_pct']:.0f}% vs {C['Africa']['straight_pct']:.0f}%)

## Body

I classified every international land border in Natural Earth's 1:10 million map ({w['km']:,} km) into ruler-straight (every point within 1 km of a great circle or a line of constant bearing such as a parallel, for at least 50 km), river or lake, through mountains, and other. Then I looked up the treaty behind each of the {R['top_n']} longest straight lines. The longest is the 49th parallel between Canada and the US ({R['ex']['us49']['km']:,} km, 1818 and 1846), then the Alaska and Yukon meridian ({R['ex']['us141']['km']:,} km, 1825). {R['top_years']['n_1880_1914']} of the {R['top_years']['n_dated']} dated lines were drawn between 1880 and 1914. Africa has the most straight border by far, but only {C['Africa']['straight_pct']:.0f}% of its border length is straight; take out Canada and the US and North America drops to {a['na_without_usca_pct']:.0f}%. Europe: {C['Europe']['straight_pct']:.1f}%. Caveat: straightness depends on the map. On Natural Earth's small-scale 1:110 million map the same method says {R['scale']['110m']['straight_pct']:.0f}%. Interactive map, click any border for its type, length and treaty: {URL}

## Source comment

Source: Natural Earth admin-0 boundary lines, rivers, lakes and mountain ranges (public domain), https://www.naturalearthdata.com/; ETOPO5 elevation (NOAA, public domain). Treaties compiled by hand from Brownlie (1979) African Boundaries, Biger (1995) Encyclopedia of International Boundaries, the US State Department's International Boundary Studies and Wikipedia; each line has a confidence rating, and {R['top_years']['n_low']} of the {R['top_n']} are marked uncertain. Sensitivity: with other tolerances the world figure is {R['sens_summary']['lmin50_min']:.0f}% to {R['sens_summary']['lmin50_max']:.0f}%, and North America beats Africa in all {a['n_settings']} settings.

Tools: Python (shapely, pyproj, scipy, matplotlib); Leaflet for the interactive map.

Interactive version: {URL}
Paper: {{https://doi.org/10.5281/zenodo.23847974}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/straight-borders/}}
"""
check_dashes(t, "post"); check_words(t, "post")
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(t)
print("post.md written")
