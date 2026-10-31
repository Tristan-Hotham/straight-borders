## Title

[OC] Where the borders are straight: 19% of the world's land border length is ruler-straight. Africa has 54% of it, but North America is straighter by share (46% vs 30%)

## Body

I classified every international land border in Natural Earth's 1:10 million map (233,534 km) into ruler-straight (every point within 1 km of a great circle or a line of constant bearing such as a parallel, for at least 50 km), river or lake, through mountains, and other. Then I looked up the treaty behind each of the 40 longest straight lines. The longest is the 49th parallel between Canada and the US (2,020 km, 1818 and 1846), then the Alaska and Yukon meridian (1,042 km, 1825). 21 of the 40 dated lines were drawn between 1880 and 1914. Africa has the most straight border by far, but only 30% of its border length is straight; take out Canada and the US and North America drops to 29%. Europe: 1.5%. Caveat: straightness depends on the map. On Natural Earth's small-scale 1:110 million map the same method says 84%. Interactive map, click any border for its type, length and treaty: https://maps.tristanhotham.com/straight-borders/

## Source comment

Source: Natural Earth admin-0 boundary lines, rivers, lakes and mountain ranges (public domain), https://www.naturalearthdata.com/; ETOPO5 elevation (NOAA, public domain). Treaties compiled by hand from Brownlie (1979) African Boundaries, Biger (1995) Encyclopedia of International Boundaries, the US State Department's International Boundary Studies and Wikipedia; each line has a confidence rating, and 1 of the 40 are marked uncertain. Sensitivity: with other tolerances the world figure is 18% to 24%, and North America beats Africa in all 12 settings.

Tools: Python (shapely, pyproj, scipy, matplotlib); Leaflet for the interactive map.

Interactive version: https://maps.tristanhotham.com/straight-borders/
Paper: https://doi.org/10.5281/zenodo.23847974
Blog post: https://blog.tristanhotham.com/2026/10/31/straight-borders/
