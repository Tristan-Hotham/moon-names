"""Step 1: parse the Wikidata TSV, deduplicate, and write the clean tables.

Outputs
  data/features.csv  one row per named feature and namesake (a feature named after two people has two rows):
                     feature id, name, body, kind, longitude (-180..180, east positive), latitude, diameter,
                     far side (Moon only), namesake id, namesake name, whether the namesake is a person.
  data/people.csv    one row per person who has a feature named after them: birth and death years, birthplace,
                     its coordinates, Wikidata's country for it, the modern country and continent it falls in
                     (Natural Earth), occupation group and occupations, Wikipedia sitelinks, features per body.
Quadrangles (map sheets named after a feature on them) are left out: they are charts, not places on the surface.
"""
import pandas as pd, numpy as np, geopandas as gpd
from shapely.geometry import Point
from common import *

d = pd.read_csv(RAW, sep="\t", dtype=str, quoting=3)
d.columns = [c.lstrip("?") for c in d.columns]
n_rows = len(d)
for c in d.columns:
    d[c] = (d[c].fillna("").str.replace(r"^<http://www\.wikidata\.org/entity/(Q\d+)>$", r"\1", regex=True)
            .str.replace(r'^"(.*)"(@[\w-]+|\^\^.*)?$', r"\1", regex=True))
d["body"] = d["body"].map(BODY_OF)
assert d.body.notna().all()

# ---------- features ----------
d["quad"] = d.typel.str.contains("quadrangle")
quad_ids = set(d.loc[d.quad, "f"])
f = d[~d.f.isin(quad_ids)].copy()
xy = f.fcoord.str.extract(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)").astype(float)
f["lon"] = ((xy[0] + 180) % 360) - 180
f["lat"] = xy[1]


def kind(types):
    t = " ".join(types).lower()
    if "crater chain" in t or "catena" in t: return "chain"
    if "crater" in t or "patera" in t: return "crater"
    if re.search(r"mons|montes|mountain|tholus|colles|promontor", t): return "mountain"
    if re.search(r"rille|rima|vallis|valles|fossa|chasma|labyrinth", t): return "valley"
    if re.search(r"mare|lacus|sinus|palus|planitia|planum|oceanus|terra|regio|basin", t): return "plain"
    if re.search(r"rupes|dorsum|dorsa|scarp|ridge|corona|tessera|arachnoid|farrum|undae", t): return "ridge"
    return "other"


KIND = {"crater": "Craters", "chain": "Crater chains", "mountain": "Mountains and domes", "valley": "Valleys and rilles",
        "plain": "Seas, plains and regions", "ridge": "Scarps, ridges and coronae", "other": "Other features"}
types = f.groupby("f").typel.apply(lambda s: sorted(set(s)))
feat = (f.sort_values(["f", "p"]).drop_duplicates(["f", "p"])
        [["f", "fl", "body", "lon", "lat", "diam", "p", "pl", "ptype"]].copy())
feat["kind"] = feat.f.map(types).map(kind)
feat["types"] = feat.f.map(types).map("; ".join)
feat["diam"] = pd.to_numeric(feat.diam, errors="coerce")
feat["human"] = (feat.ptype == "Q5").astype(int)
feat["far"] = np.where(feat.body == "moon", (feat.lon.abs() > 90).astype(int), -1)
feat.loc[feat.lon.isna(), "far"] = -1
# a feature with no English label takes its namesake's name, flagged
feat["noname"] = (feat.fl == "").astype(int)
feat.loc[feat.fl == "", "fl"] = feat.pl
feat = feat.rename(columns={"f": "fid", "fl": "name", "p": "pid", "pl": "namesake"})
# wrong "named after" links removed (data/overrides_birthplaces.csv, field "link": the feature id is in wikidata_value)
for o in pd.read_csv(f"{DATA}/overrides_birthplaces.csv").query("field == 'link'").itertuples():
    m = (feat.fid == o.wikidata_value) & (feat.pid == o.pid); assert m.sum() == 1, o
    feat = feat[~m]

# ---------- people ----------
h = d[(d.ptype == "Q5") & ~d.f.isin(quad_ids)].copy()
bxy = h.bpcoord.str.extract(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)").astype(float)
h["blon"], h["blat"] = bxy[0], bxy[1]


def year(s):
    m = re.match(r"^(-?)(\d+)-", s or "")
    if not m: return None
    y = int(m.group(2)); return -y if m.group(1) else y


rows = []
for pid, g in h.groupby("p", sort=True):
    g = g.sort_values(["blat", "bp"], na_position="last")
    bp = g[g.blat.notna()].iloc[0] if g.blat.notna().any() else g.iloc[0]
    occs = [o for o in g.occl.value_counts().index if o]
    grp = "other"
    occ_txt = " | ".join(o.lower() for o in occs)
    for k, _, rx in OCC:
        if any(re.search(rx, o.lower()) for o in occs):
            grp = k; break
    if not occs: grp = "unknown"
    arts_any = int(any(re.search(dict((k, rx) for k, _, rx in OCC)["arts"], o.lower()) for o in occs))
    # Wikidata's country for the birthplace: several values (historical states) are joined; the modern country comes
    # from Natural Earth below
    wdc = "; ".join(sorted(set(c for c in g[g.bp == bp.bp].bpcl if c)))
    rows.append(dict(pid=pid, name=g.pl.iloc[0], born=year(g.bd.iloc[0]), died=year(g.dd.iloc[0]),
                     bpid=bp.bp, birthplace=bp.bpl, blon=bp.blon, blat=bp.blat, wd_country=wdc,
                     occ=grp, occupations="; ".join(occs[:6]), sitelinks=int(g.sl.iloc[0] or 0),
                     n_bp=g.bp[g.bp != ""].nunique(), arts_any=arts_any))
P = pd.DataFrame(rows)
# obvious label vandalism in Wikidata, corrected (listed in the README)
FIX = {"Lady Jane Greykjbh": "Lady Jane Grey"}
# documented corrections of wrong birthplaces (data/overrides_birthplaces.csv), applied before countries are assigned
OV = pd.read_csv(f"{DATA}/overrides_birthplaces.csv")
for o in OV[OV.field == "birthplace"].itertuples():
    m = P.pid == o.pid; assert m.sum() == 1, o.pid
    P.loc[m, ["birthplace", "blon", "blat", "wd_country"]] = [o.corrected_value.split(",")[0], o.blon, o.blat, f"{o.country} (override)"]
    P.loc[m, "bpid"] = "override:" + o.pid
# an override that lands on a birthplace already in the data (same name, within about 30 km) joins it
for o in OV[OV.field == "birthplace"].itertuples():
    nm = o.corrected_value.split(",")[0]
    same = P[(P.birthplace == nm) & ~P.bpid.astype(str).str.startswith("override:") & ((P.blon - o.blon).abs() < .3) & ((P.blat - o.blat).abs() < .3)]
    if len(same): P.loc[P.pid == o.pid, ["bpid", "blon", "blat"]] = [same.bpid.iloc[0], same.blon.iloc[0], same.blat.iloc[0]]
for o in OV[OV.field == "birthplace_unknown"].itertuples():   # a country, empire or region: left unmapped, not plotted at a centroid
    m = P.pid == o.pid; assert m.sum() == 1, o.pid
    P.loc[m, ["blon", "blat"]] = [np.nan, np.nan]
    P.loc[m, "birthplace"] = P.loc[m, "birthplace"] + " (not mapped)"
# sex of each namesake (P21), from a second Wikidata query; contradictory values corrected in the overrides file
SX = pd.read_csv(SEX, sep="\t", dtype=str, quoting=3); SX.columns = [c.lstrip("?") for c in SX.columns]
SX["p"] = SX.p.str.extract(r"(Q\d+)"); SX["sexl"] = SX.sexl.str.extract(r'^"(.*)"')
sx = SX.groupby("p").sexl.apply(lambda s: "; ".join(sorted(set(s))))
P["sex"] = P.pid.map(sx)
for o in OV[OV.field == "sex"].itertuples():
    m = P.pid == o.pid; assert m.sum() == 1 and P.loc[m, "sex"].iloc[0] == o.wikidata_value, o.pid
    P.loc[m, "sex"] = o.corrected_value
P["name"] = P.name.replace(FIX)
# people whose English label did not come back in the extract: labels supplied by hand (data/overrides_labels.csv),
# otherwise the name of the feature named after them
LB = pd.read_csv(f"{DATA}/overrides_labels.csv").set_index("pid").label
P.loc[P.name.isna() | (P.name == ""), "name"] = P.pid.map(LB)
_fn = feat[feat.human == 1].groupby("pid")["name"].first()
P.loc[P.name.isna() | (P.name == ""), "name"] = P.pid.map(_fn)
_nm = (feat.human == 1) & ((feat.namesake == "") | feat.namesake.isna())
feat.loc[_nm, "namesake"] = feat.loc[_nm, "pid"].map(dict(zip(P.pid, P.name)))

ne = gpd.read_file(f"{GEO}/ne_10m_admin_0_countries.geojson")[["ADM0_A3", "ADMIN", "CONTINENT", "geometry"]]
has = P.blat.notna()
pts = gpd.GeoDataFrame(P[has][["pid"]], geometry=[Point(x, y) for x, y in zip(P[has].blon, P[has].blat)], crs=ne.crs)
j = gpd.sjoin(pts, ne, how="left", predicate="within").drop_duplicates("pid")
miss = j[j.ADM0_A3.isna()][["pid", "geometry"]]
if len(miss):   # on the coast or offshore: nearest country within about 30 km
    jn = gpd.sjoin_nearest(miss.to_crs(3857), ne.to_crs(3857), how="left", max_distance=30000).drop_duplicates("pid")
    j = j.set_index("pid"); jn = jn.set_index("pid")
    for c in ("ADM0_A3", "ADMIN", "CONTINENT"):
        j.loc[jn.index, c] = jn[c]
    j = j.reset_index()
j = j.set_index("pid")
P["iso3"] = P.pid.map(j.ADM0_A3); P["country"] = P.pid.map(j.ADMIN); P["continent"] = P.pid.map(j.CONTINENT)
P.loc[P.continent == "Seven seas (open ocean)", "continent"] = None
# Crimea: Natural Earth's default view places it in Russia; counted as Ukraine, as internationally recognised
cri = (P.iso3 == "RUS") & P.blon.between(32.4, 36.7) & P.blat.between(44.3, 46.25)
P.loc[cri, ["iso3", "country"]] = ["UKR", "Ukraine"]
# Natural Earth's codes for a few countries differ from ISO; names kept as Natural Earth gives them, shortened
P["country"] = P.country.replace({"United States of America": "United States", "United Republic of Tanzania": "Tanzania",
                                   "Republic of Serbia": "Serbia", "Czechia": "Czech Republic", "The Bahamas": "Bahamas"})
for k, _, _, _ in BODIES:
    P["n_" + k] = P.pid.map(feat[(feat.human == 1) & (feat.body == k)].groupby("pid").size()).fillna(0).astype(int)
P["n_far"] = P.pid.map(feat[(feat.human == 1) & (feat.far == 1)].groupby("pid").size()).fillna(0).astype(int)
P["n_near"] = P.pid.map(feat[(feat.human == 1) & (feat.far == 0)].groupby("pid").size()).fillna(0).astype(int)
P = P[P[["n_" + k for k, *_ in BODIES]].sum(axis=1) > 0]

feat["namesake"] = feat.namesake.replace(FIX)
P["sexg"] = P.sex.map(lambda x: "female" if x == "female" else "male" if x == "male" else "other" if isinstance(x, str) else "")

# ---------- features named after places on Earth (second query) ----------
q = pd.read_csv(PLACES, sep="\t", dtype=str, quoting=3); q.columns = [c.lstrip("?") for c in q.columns]
for c in q.columns:
    q[c] = (q[c].fillna("").str.replace(r"^<http://www\.wikidata\.org/entity/(Q\d+)>$", r"\1", regex=True)
            .str.replace(r'^"(.*)"(@[\w-]+|\^\^.*)?$', r"\1", regex=True))
q = q[~q.ncoord.str.contains("entity/Q") & (q.ncoord != "")]          # coordinates on Earth only
q = q[~q.ntypel.str.contains("language|biodiversity", case=False)]       # languages are not places
q["body"] = q.body.map(BODY_OF); q = q[~q.f.isin(quad_ids)]
qt = q.groupby(["f", "n"]).agg(fl=("fl", "first"), body=("body", "first"), nl=("nl", "first"), ncoord=("ncoord", "first"),
                                ncl=("ncl", lambda s: "; ".join(sorted(set(x for x in s if x)))), types=("ntypel", lambda s: "; ".join(sorted(set(x for x in s if x))[:4]))).reset_index()
nxy = qt.ncoord.str.extract(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)", flags=re.I).astype(float)
qt["plon"], qt["plat"] = nxy[0], nxy[1]
# documented corrections (data/overrides_places.csv): ships dropped, country-level links moved to the named town
OP = pd.read_csv(f"{DATA}/overrides_places.csv")
for o in OP.itertuples():
    m = qt.f == o.fid; assert m.sum() >= 1, o.fid
    if o.action == "drop": qt = qt[~m]
    elif o.action == "rename": qt.loc[m, "nl"] = o.place
    else: qt.loc[m, ["nl", "plon", "plat", "types"]] = [o.place, o.plon, o.plat, "town (override)"]
qt = qt[qt.plat.notna()].copy()
gq = gpd.GeoDataFrame(qt[["f", "n"]].reset_index(drop=True), geometry=[Point(x, y) for x, y in zip(qt.plon, qt.plat)], crs=ne.crs)
jq = gpd.sjoin(gq, ne, how="left", predicate="within").drop_duplicates(["f", "n"])
qt = qt.merge(jq[["f", "n", "ADM0_A3", "ADMIN", "CONTINENT"]], on=["f", "n"], how="left")
qt["country"] = qt.ADMIN.replace({"United States of America": "United States", "Czechia": "Czech Republic", "United Republic of Tanzania": "Tanzania", "Republic of Serbia": "Serbia"}).fillna(qt.ncl.str.split("; ").str[0])
cri = (qt.ADM0_A3 == "RUS") & qt.plon.between(32.4, 36.7) & qt.plat.between(44.3, 46.25)
qt.loc[cri, ["ADM0_A3", "country"]] = ["UKR", "Ukraine"]
t = qt.types.str.lower()
qt["pkind"] = np.where(t.str.contains("river|lake|valley|sea|bay|strait|spring|stream|main stem"), "water or valley",
              np.where(t.str.contains("mountain|massif|peak|summit|volcan|archipelago|island|four-thousander|fold"), "mountain or island",
              np.where(t.str.contains("city|town|village|settlement|municipal|commune|comune|community|hamlet|capital|seat|parish|locality|township|suburb|borough"), "town or village", np.where(t.str.contains("county|district|upazila|ortsteil|neighbo|reserve|region|province"), "district or region", "other place"))))
qt["fl"] = np.where(qt.fl == "", qt.nl, qt.fl)
Q = qt.rename(columns={"f": "fid", "fl": "feature", "n": "nid", "nl": "place", "ADM0_A3": "iso3", "CONTINENT": "continent", "ncl": "wd_country"})[
    ["fid", "feature", "body", "nid", "place", "plon", "plat", "country", "iso3", "continent", "wd_country", "pkind", "types"]]
Q.to_csv(f"{DATA}/place_namesakes.csv", index=False)
print("place namesakes:", Q.groupby("body").size().to_dict(), Q[Q.body == "mars"].pkind.value_counts().to_dict())
feat.drop(columns=["ptype"]).to_csv(f"{DATA}/features.csv", index=False)
P.to_csv(f"{DATA}/people.csv", index=False)
jsave({"rows": n_rows, "quad_features": len(quad_ids), "kind_names": KIND}, f"{WORK}/clean_meta.json")
print(n_rows, "rows;", feat.fid.nunique(), "features;", len(feat), "feature-namesake pairs;", len(P), "people;",
      int(P.blat.isna().sum()), "without birthplace coords;", int(P.country.isna().sum() - P.blat.isna().sum()), "unmatched to a country")
print(P.occ.value_counts())
