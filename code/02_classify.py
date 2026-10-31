"""Classify every stretch of every border as ruler-straight, river or lake, through mountains, or other.

1. Straight. Walking along each border from vertex i, the run is extended vertex by vertex for as long as every vertex
   between i and j lies within TOL km of the great circle through i and j, or of the rhumb line (line of constant
   compass bearing, which includes every parallel) through them, and the path is no more than 1% longer than the
   chord (so it cannot double back). A run of at least LMIN km is a straight segment; the next search starts at its
   end, otherwise at i + 1. Straight segments are typed as a parallel (latitude constant to within TOL), a meridian
   (longitude constant to within TOL) or another straight line.
2. River or lake. The border is resampled every 1 km. A sample follows water if it lies within RIVER km of a Natural
   Earth 10m river centre line or lake shore, inside a lake, or on a line Natural Earth marks as a water boundary.
   Gaps of up to 3 km are filled and runs shorter than WMIN km are dropped (so a river crossing does not count).
3. Mountains. A sample is in mountains if ETOPO5 gives it at least 2500 m, or at least MTN_LOW m with a local
   elevation range of at least MTN_REL m within about MTN_R grid cells (radius 2 is about 18 km north to south),
   a simplified form of the UNEP-WCMC mountain definition (Kapos et al. 2000). Gaps of up to 3 km are filled and runs
   shorter than MMIN km dropped. Most such borders follow crests or watersheds, but a 9 km elevation grid cannot show
   which: an explicit crest test (border higher than both sides) found crests on only 14% of the Chile and Argentina
   border, so it was not used, and the class is "through mountains", not "on the crest".
4. Everything else is other or irregular.
Priority is straight, then water, then mountains: a straight line across a lake is straight (Lake Victoria's parallel),
except on lines Natural Earth marks as water boundaries (the Great Lakes, estuaries), whose straight stretches only join
turning points in the water and count as water.

Output: WORK/classified.json (pieces with class and length), WORK/segments.json (straight segments),
WORK/sensitivity.json (world shares under other settings, and on the coarser 50m and 110m lines)."""
import numpy as np, netCDF4
from scipy import ndimage
from scipy.spatial import cKDTree
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from shapely.prepared import prep
from pyproj import Geod
from common import *

R_E = 6371.0088
G = Geod(ellps="WGS84")


def unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def edge_km(lon, lat):
    _, _, d = G.inv(lon[:-1], lat[:-1], lon[1:], lat[1:])
    return d / 1000


# ---------------------------------------------------------------- 1. straight runs
def dev_ok(X, lon, lat, my, i, j, tol):
    """True if vertices i..j lie within tol km of the great circle or the rhumb line through i and j."""
    if j - i < 2:
        return True
    k = slice(i + 1, j)
    n = np.cross(X[i], X[j]); nn = np.linalg.norm(n)
    if nn > 1e-12:
        d = R_E * np.abs(np.arcsin(np.clip(X[k] @ (n / nn), -1, 1)))
        if d.max() <= tol:
            return True
    # rhumb: a straight line in Mercator coordinates; distance scaled back by cos(latitude)
    x0, y0, x1, y1 = np.radians(lon[i]), my[i], np.radians(lon[j]), my[j]
    dx, dy = x1 - x0, y1 - y0; L = np.hypot(dx, dy)
    if L < 1e-12:
        return False
    px, py = np.radians(lon[k]) - x0, my[k] - y0
    dm = np.abs(px * dy - py * dx) / L
    d = dm * R_E * np.cos(np.radians(lat[k]))
    return d.max() <= tol


def straight_runs(lon, lat, ekm, tol, lmin):
    X = unit(lon, lat); my = np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
    cum = np.concatenate([[0], np.cumsum(ekm)])
    n = len(lon); runs = []; i = 0
    while i < n - 1:
        j = i + 1
        while j + 1 < n:
            chord = R_E * np.arccos(np.clip(X[i] @ X[j + 1], -1, 1))
            if cum[j + 1] - cum[i] > 1.01 * chord + tol or not dev_ok(X, lon, lat, my, i, j + 1, tol):
                break
            j += 1
        if cum[j] - cum[i] >= lmin:
            runs.append((i, j)); i = j
        else:
            i += 1
    return runs


def run_kind(lon, lat, i, j, tol):
    la, lo = lat[i:j + 1], lon[i:j + 1]
    if np.abs(np.radians(la - la.mean())).max() * R_E <= tol:
        return "parallel", float(round(la.mean(), 3))
    if (np.abs(np.radians(lo - lo.mean())) * np.cos(np.radians(la))).max() * R_E <= tol:
        return "meridian", float(round(lo.mean(), 3))
    return "line", None


# ---------------------------------------------------------------- 2 and 3. water and mountains, on 1 km samples
def resample(lon, lat, step=1.0):
    """Points every ~step km along the path; returns lon, lat, and the original edge index of each sample edge."""
    ekm = edge_km(lon, lat)
    LO, LA, E = [lon[0]], [lat[0]], []
    for e in range(len(ekm)):
        m = max(1, int(np.ceil(ekm[e] / step)))
        if m > 1:
            pts = G.npts(lon[e], lat[e], lon[e + 1], lat[e + 1], m - 1)
            for x, y in pts:
                LO.append(x); LA.append(y); E.append(e)
        LO.append(lon[e + 1]); LA.append(lat[e + 1]); E.append(e)
    return np.array(LO), np.array(LA), np.array(E)


def water_tree():
    pts = []
    def add_line(c):
        c = np.asarray(c, float)
        if len(c) < 2: return
        lo, la = c[:, 0], c[:, 1]
        km = edge_km(lo, la)
        for e in range(len(km)):
            m = max(1, int(np.ceil(km[e] / 0.5)))
            t = np.linspace(0, 1, m, endpoint=False)
            pts.append(np.column_stack([lo[e] + t * (lo[e + 1] - lo[e]), la[e] + t * (la[e + 1] - la[e])]))
        pts.append(c[-1:])
    for fn in ("ne_10m_rivers_lake_centerlines", "ne_10m_rivers_europe", "ne_10m_rivers_north_america"):
        for f in jload(f"{NE}/{fn}.geojson")["features"]:
            g = f["geometry"]
            if not g: continue
            for c in ([g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]):
                add_line(c)
    lakes = []
    for fn in ("ne_10m_lakes", "ne_10m_lakes_europe", "ne_10m_lakes_north_america"):
        for f in jload(f"{NE}/{fn}.geojson")["features"]:
            g = f["geometry"]
            if not g: continue
            polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            for p in polys:
                for ring in p:
                    add_line(ring)
            lakes.append(shape(g).buffer(0))
    P = np.concatenate(pts)
    return cKDTree(unit(P[:, 0], P[:, 1])), lakes


class DEMgrid:
    def __init__(self):
        d = netCDF4.Dataset(DEM)
        self.z = np.asarray(d.variables["ROSE"][:], dtype=np.float32)   # rows: lat -90..90, cols: lon 0..359.917
        self.z = np.concatenate([self.z, self.z[:, :1]], axis=1)
        self.dl = 1 / 12

    def __call__(self, lon, lat):
        x = (np.mod(lon, 360)) / self.dl; y = (lat + 90) / self.dl
        x0 = np.floor(x).astype(int); y0 = np.clip(np.floor(y).astype(int), 0, self.z.shape[0] - 2)
        fx, fy = x - x0, y - y0
        z = self.z
        return ((1 - fx) * (1 - fy) * z[y0, x0] + fx * (1 - fy) * z[y0, x0 + 1] + (1 - fx) * fy * z[y0 + 1, x0] + fx * fy * z[y0 + 1, x0 + 1])


def relief_grids(dem):
    """Local elevation range (max minus min) around every DEM cell, for circular windows of radius 1, 2 and 3 cells
    (about 9, 18 and 28 km north to south; narrower east to west away from the equator)."""
    out = {}
    for r in (1, 2, 3):
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]; fp = (yy ** 2 + xx ** 2) <= r * r + .5
        g = DEMgrid.__new__(DEMgrid); g.dl = dem.dl
        g.z = (ndimage.maximum_filter(dem.z, footprint=fp, mode="wrap") - ndimage.minimum_filter(dem.z, footprint=fp, mode="wrap")).astype(np.float32)
        out[r] = g
    return out


def mountain(z, rel, low, rel_min, high=2500.0):
    """Mountain terrain, adapted from the UNEP-WCMC definition (Kapos et al. 2000): at least `high` m, or at least `low` m
    with a local elevation range of at least rel_min m."""
    return (z >= high) | ((z >= low) & (rel >= rel_min))


def runs_filter(flag, skm, gap, minlen):
    """Fill gaps of at most gap km between flagged sample edges, then drop runs shorter than minlen km."""
    f = flag.copy(); n = len(f)
    i = 0
    while i < n:                       # fill gaps
        if not f[i]:
            j = i
            while j < n and not f[j]: j += 1
            if i > 0 and j < n and skm[i:j].sum() <= gap:
                f[i:j] = True
            i = j
        else:
            i += 1
    i = 0
    while i < n:                       # drop short runs
        if f[i]:
            j = i
            while j < n and f[j]: j += 1
            if skm[i:j].sum() < minlen:
                f[i:j] = False
            i = j
        else:
            i += 1
    return f


# ---------------------------------------------------------------- driver
def prepare(B, with_terrain=True):
    """Per path: vertices, edge lengths, 1 km samples and (optionally) the river distance, elevation and local relief."""
    P = []
    if with_terrain:
        tree, lakes = water_tree(); lt = STRtree(lakes); lp = [prep(l) for l in lakes]; dem = DEMgrid(); RG = relief_grids(dem)
    for b in B:
        c = np.array(b["c"], float); lon, lat = c[:, 0], c[:, 1]
        p = {"lon": lon, "lat": lat, "ekm": edge_km(lon, lat)}
        if with_terrain:
            slo, sla, se = resample(lon, lat)
            mlo, mla = (slo[:-1] + slo[1:]) / 2, (sla[:-1] + sla[1:]) / 2      # sample-edge midpoints
            skm = edge_km(slo, sla)
            d, _ = tree.query(unit(mlo, mla), k=1)
            dkm = 2 * R_E * np.arcsin(np.clip(d / 2, 0, 1))
            inlake = np.zeros(len(mlo), bool)
            for q in range(len(mlo)):
                pt = Point(mlo[q], mla[q])
                for li in lt.query(pt):
                    if lp[li].contains(pt):
                        inlake[q] = True; break
            dkm[inlake] = 0
            if b["water"]:
                dkm[:] = 0
            z = dem(mlo, mla); rel = {r: g(mlo, mla) for r, g in RG.items()}
            p.update(slo=slo, sla=sla, se=se, skm=skm, dkm=dkm, z=z, rel=rel, mlo=mlo, mla=mla)
        P.append(p)
    return P


_RUNS = {}


def classify(B, P, tol, lmin, river, wmin, mtn_low, mtn_rel, mtn_r, mmin, keep=False):
    """World totals by class, totals by continent and class, and (keep=True) the classified pieces and straight segments."""
    tot = {k: 0.0 for k in CLASSES}; byc = {}; out = []; segs = []
    for bi, (b, p) in enumerate(zip(B, P)):
        lon, lat, ekm = p["lon"], p["lat"], p["ekm"]
        ck = (id(p), tol, lmin)
        if ck not in _RUNS:   # water boundaries are water, even if drawn straight
            _RUNS[ck] = [] if b["water"] else straight_runs(lon, lat, ekm, tol, lmin)
        runs = _RUNS[ck]
        se_str = np.zeros(len(ekm), bool)
        for i, j in runs:
            se_str[i:j] = True
            if keep:
                kind, val = run_kind(lon, lat, i, j, tol)
                segs.append({"path": bi, "a": b["a"], "b": b["b"], "cont": b["cont"], "km": float(ekm[i:j].sum()), "kind": kind, "val": val,
                             "n_vertices": j - i + 1, "c": [[float(lon[i]), float(lat[i])], [float(lon[j]), float(lat[j])]],
                             "mid": [float(lon[(i + j) // 2]), float(lat[(i + j) // 2])], "fc": b["fc"]})
        if "skm" not in p:          # coarser scales: straightness only
            s = float(ekm[se_str].sum()); tot["straight"] += s; tot["other"] += float(ekm.sum()) - s
            continue
        skm, se = p["skm"], p["se"]
        st = se_str[se]
        wat = runs_filter(p["dkm"] <= river, skm, 3.0, wmin)
        rid = runs_filter(mountain(p["z"], p["rel"][mtn_r], mtn_low, mtn_rel), skm, 3.0, mmin)
        cls = np.where(st, 0, np.where(wat, 1, np.where(rid, 2, 3)))
        bc = byc.setdefault(b["cont"], {k: 0.0 for k in CLASSES})
        for k, name in enumerate(CLASSES):
            v = float(skm[cls == k].sum()); tot[name] += v; bc[name] += v
        if keep:
            # pieces: consecutive sample edges of one class, as polylines
            pts_lo, pts_la = p["slo"], p["sla"]
            i = 0; n = len(cls)
            while i < n:
                j = i
                while j < n and cls[j] == cls[i]: j += 1
                out.append({"path": bi, "cls": CLASSES[cls[i]], "km": float(skm[i:j].sum()),
                            "c": [[float(x), float(y)] for x, y in zip(pts_lo[i:j + 1], pts_la[i:j + 1])]})
                i = j
    if keep:
        return tot, out, segs
    return tot, byc, segs


if __name__ == "__main__":
    import time, itertools
    t0 = time.time()
    B = jload(f"{WORK}/borders_10m.json")
    P = prepare(B)
    print("prepared", round(time.time() - t0), "s")
    tot, pieces, segs = classify(B, P, keep=True, **MAIN)
    T = sum(tot.values())
    print({k: f"{v:,.0f} km ({100 * v / T:.1f}%)" for k, v in tot.items()}, "segments", len(segs))
    jsave(pieces, f"{WORK}/classified.json"); jsave(segs, f"{WORK}/segments.json")
    # sensitivity: straightness settings
    sens = {"straight": [], "water": [], "mountain": [], "scale": []}
    for tol, lmin in itertools.product((0.25, 0.5, 1.0, 2.0), (25.0, 50.0, 100.0)):
        st = dict(MAIN, tol=tol, lmin=lmin)
        t, byc, _ = classify(B, P, **st)
        sens["straight"].append({"tol": tol, "lmin": lmin, **t, "cont": byc})
        print("straight", tol, lmin, round(100 * t["straight"] / T, 1))
    for river, wmin in itertools.product((1.5, 3.0, 5.0), (10.0, 15.0, 30.0)):
        t, byc, _ = classify(B, P, **dict(MAIN, river=river, wmin=wmin))
        sens["water"].append({"river": river, "wmin": wmin, **t, "cont": byc})
        print("water", river, wmin, round(100 * t["water"] / T, 1))
    for rel, r in itertools.product((200.0, 300.0, 500.0), (1, 2, 3)):
        t, byc, _ = classify(B, P, **dict(MAIN, mtn_rel=rel, mtn_r=r))
        sens["mountain"].append({"rel": rel, "r": r, **t, "cont": byc})
        print("mountain", rel, r, round(100 * t["mountain"] / T, 1))
    for scale in ("50m", "110m"):
        Bs = jload(f"{WORK}/borders_{scale}.json"); Ps = prepare(Bs, with_terrain=False)
        for tol, lmin in ((1.0, 50.0), (0.5, 50.0), (2.0, 50.0)):
            t, _, _ = classify(Bs, Ps, **dict(MAIN, tol=tol, lmin=lmin))
            sens["scale"].append({"scale": scale, "tol": tol, "lmin": lmin, "total": t["straight"] + t["other"], "straight": t["straight"]})
            print(scale, tol, lmin, round(100 * t["straight"] / (t["straight"] + t["other"]), 1))
    jsave(sens, f"{WORK}/sensitivity.json")
    print("done", round(time.time() - t0), "s")
