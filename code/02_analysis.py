"""Step 2: every number quoted anywhere goes into data/results.json; the page data goes into data/site.json.
Unit of the main counts: a feature and a person it is named after (a "naming"). A person honoured on two worlds counts
twice; a feature named after two people counts once for each. Shares are of namings whose namesake has a located
birthplace unless said otherwise. Continents and countries are modern (Natural Earth), whatever the birthplace was
called when the person was born."""
import pandas as pd, numpy as np
from common import *

F = pd.read_csv(f"{DATA}/features.csv", keep_default_na=False, na_values=[""])
P = pd.read_csv(f"{DATA}/people.csv", keep_default_na=False, na_values=[""])
CM = jload(f"{WORK}/clean_meta.json")
H = F[F.human == 1].merge(P, on="pid", how="left", suffixes=("", "_p"))
L = H[H.continent.notna()]
R = {"meta": {"page": PAGE, "repo": REPO, "att": OPM_ATT}}
pc = lambda a, b: round(100 * a / b, 2) if b else None

R["source"] = {"rows": CM["rows"], "features": int(F.fid.nunique()), "pairs": len(F), "quad": CM["quad_features"],
               "human_pairs": len(H), "people": len(P), "people_located": int(P.blat.notna().sum()),
               "people_unlocated": int(P.blat.isna().sum()), "located_pairs": len(L),
               "located_pct": pc(len(L), len(H)), "multi_namesake": int((F.groupby("fid").size() > 1).sum()),
               "multi_bp": int((P.n_bp > 1).sum()), "no_coords": int(F.drop_duplicates("fid").lon.isna().sum()),
               "no_label": int(F.drop_duplicates("fid").noname.sum())}

def century(y):
    if pd.isna(y): return None
    y = int(y)
    return (y - 1) // 100 + 1 if y > 0 else -((-y - 1) // 100 + 1)

B = {}
for b, _, nm, _ in BODIES:
    f = F[F.body == b]; h = H[H.body == b]; l = L[L.body == b]
    cont = l.continent.value_counts()
    cty = l.country.value_counts()
    occ = h.occ.value_counts()
    cen = h.born.map(century).value_counts()
    B[b] = {"name": nm, "features": int(f.fid.nunique()), "human_features": int(f[f.human == 1].fid.nunique()),
            "human_pct": pc(f[f.human == 1].fid.nunique(), f.fid.nunique()), "namings": len(h), "located": len(l),
            "people": int(h.pid.nunique()),
            "cont": {c: {"n": int(cont.get(c, 0)), "pct": pc(cont.get(c, 0), len(l))} for c in CONT_ORDER},
            "europe_pct": pc(cont.get("Europe", 0), len(l)),
            "top": [{"country": c, "n": int(n), "pct": pc(n, len(l))} for c, n in cty.head(12).items()],
            "n_countries": int(cty.size),
            "occ": {k: {"n": int(occ.get(k, 0)), "pct": pc(occ.get(k, 0), len(h) - occ.get("unknown", 0))} for k, *_ in OCC}, "occ_unknown": int(occ.get("unknown", 0)),
            "arts_any_pct": pc(h.arts_any.sum(), len(h)),
            "born_median": int(h.born.median()), "born_known": int(h.born.notna().sum()),
            "cent": {int(c): int(n) for c, n in cen.sort_index().items()},
            "born_1800_pct": pc((h.born > 1800).sum(), h.born.notna().sum()),
            "born_before_1500": int((h.born < 1500).sum()),
            "ussr_pct": pc(l.iso3.isin(USSR).sum(), len(l)),
            "famous": [{"name": r.namesake, "feature": r["name"], "sitelinks": int(r.sitelinks)} for _, r in h.sort_values("sitelinks", ascending=False).drop_duplicates("pid").head(8).iterrows()],
            "nonhuman": int(f[f.human == 0].fid.nunique())}
    if b == "moon":
        B[b]["far_features"] = int(f[f.far == 1].fid.nunique()); B[b]["near_features"] = int(f[f.far == 0].fid.nunique())
R["body"] = B
R["all"] = {"namings": len(H), "located": len(L), "europe_pct": pc((L.continent == "Europe").sum(), len(L)),
            "n_countries": int(L.country.nunique())}

# Europe in numbers, the Moon
m = L[L.body == "moon"]
south = m.continent.isin(["Africa", "South America", "Oceania"]).sum()
paris_moon = int((m.bpid == m[m.birthplace == "Paris"].bpid.iloc[0]).sum())
R["moon"] = {"south_n": int(south), "africa_n": int((m.continent == "Africa").sum()), "sam_n": int((m.continent == "South America").sum()),
             "oce_n": int((m.continent == "Oceania").sum()), "asia_n": int((m.continent == "Asia").sum()),
             "paris_n": paris_moon, "egypt_n": int((m.country == "Egypt").sum()),
             "alex_n": int((m.birthplace == "Alexandria").sum()),
             "europe_n": int((m.continent == "Europe").sum()), "na_n": int((m.continent == "North America").sum()),
             "de_fr_uk_n": int(m.country.isin(["Germany", "France", "United Kingdom"]).sum()),
             "de_fr_uk_pct": pc(m.country.isin(["Germany", "France", "United Kingdom"]).sum(), len(m)),
             "china_n": int((m.country == "China").sum()), "india_n": int((m.country == "India").sum()),
             "japan_n": int((m.country == "Japan").sum()),
             "asia_pre1500": int(((m.continent == "Asia") & (m.born < 1500)).sum()), "turkey_n": int((m.country == "Turkey").sum()),
             "asia_top": m[m.continent == "Asia"].country.value_counts().index[0]}
assert R["moon"]["paris_n"] > R["moon"]["south_n"]          # "more than Africa, South America and Oceania together"

# Near side and far side of the Moon
FS = {}
for k, v in (("near", 0), ("far", 1)):
    h = H[(H.body == "moon") & (H.far == v)]; l = h[h.continent.notna()]
    FS[k] = {"namings": len(h), "located": len(l), "ussr_n": int(l.iso3.isin(USSR).sum()), "ussr_pct": pc(l.iso3.isin(USSR).sum(), len(l)),
             "europe_pct": pc((l.continent == "Europe").sum(), len(l)), "us_pct": pc((l.country == "United States").sum(), len(l)),
             "born_median": int(h.born.median()), "born_1800_pct": pc((h.born > 1800).sum(), h.born.notna().sum()),
             "astro_pct": h.occ.eq("astro").mean() * 100, "science_pct": h.occ.eq("science").mean() * 100,
             "space_n": int(h.occ.eq("space").sum()), "space_people": int(h[h.occ.eq("space")].pid.nunique()), "russia_n": int((l.country == "Russia").sum())}
FS["near_1in"] = round(100 / FS["near"]["ussr_pct"]); FS["far_1in"] = round(100 / FS["far"]["ussr_pct"])
FS["ussr_ratio"] = round(FS["far"]["ussr_pct"] / FS["near"]["ussr_pct"], 1)
FS["far_ussr_names"] = H[(H.body == "moon") & (H.far == 1) & H.iso3.isin(USSR)].sort_values("sitelinks", ascending=False).namesake.head(8).tolist()
FS["far_space"] = H[(H.body == "moon") & (H.far == 1) & (H.occ == "space")].sort_values("sitelinks", ascending=False).namesake.tolist()
R["far"] = FS

# The most honoured birthplaces
g = L.groupby(["bpid", "birthplace", "country"])
T = g.agg(n=("fid", "size"), moon=("body", lambda s: int((s == "moon").sum())), people=("pid", "nunique"),
          lon=("blon", "first"), lat=("blat", "first")).reset_index().sort_values(["n", "moon"], ascending=False)
R["towns"] = [{"place": r.birthplace, "country": r.country, "n": int(r.n), "moon": int(r.moon), "people": int(r.people),
               **{b: int(((L.bpid == r.bpid) & (L.body == b)).sum()) for b, *_ in BODIES}} for r in T.head(15).itertuples()]
TM = T.sort_values(["moon", "n"], ascending=False)
R["towns_moon"] = [{"place": r.birthplace, "country": r.country, "moon": int(r.moon)} for r in TM.head(12).itertuples()]
R["n_birthplaces"] = int(T.shape[0]); R["n_birthplaces_moon"] = int((T.moon > 0).sum())
R["paris_names_moon"] = H[(H.body == "moon") & (H.birthplace == "Paris")].sort_values("sitelinks", ascending=False).namesake.dropna().head(6).tolist()
# small places: birthplaces that are not big cities but are honoured three or more times
R["one_town_two_worlds"] = int(L.groupby("bpid").body.nunique().ge(2).sum())

# people on several worlds
nb = (P[["n_" + b for b, *_ in BODIES]] > 0).sum(axis=1)
R["multi"] = {"two_plus": int((nb >= 2).sum()), "three": P[nb >= 3].name.tolist(),
              "moon_mars": int(((P.n_moon > 0) & (P.n_mars > 0)).sum())}

# Mercury: the arts; Venus: the IAU's rule for women
R["mercury"] = {"arts_any_pct": B["mercury"]["arts_any_pct"], "asia_pct": B["mercury"]["cont"]["Asia"]["pct"],
                "japan_n": int((L[L.body == "mercury"].country == "Japan").sum()), "china_n": int((L[L.body == "mercury"].country == "China").sum())}
R["venus"] = {"us_pct": B["venus"]["top"][0]["pct"], "top": B["venus"]["top"][0]["country"]}
assert R["venus"]["top"] == "United States"
R["mars_places"] = {"nonhuman": B["mars"]["nonhuman"], "pct": pc(B["mars"]["nonhuman"], B["mars"]["features"])}

# women: share of namings of people whose Wikidata sex is female, among those recorded as female or male
def wshare(h):
    k = h[h.sexg.isin(["female", "male"])]
    return {"n": len(k), "women": int((k.sexg == "female").sum()), "pct": pc((k.sexg == "female").sum(), len(k))}
W = {b: wshare(H[H.body == b]) for b, *_ in BODIES}
nv = H[H.body != "venus"]
W["three"] = wshare(nv)
W["venus_men"] = H[(H.body == "venus") & (H.sexg == "male")].namesake.tolist()
W["no_sex"] = int((H.sexg == "").sum()); W["other_sex"] = int((H.sexg == "other").sum())
bins = [(-9999, 1799, "before 1800"), (1800, 1899, "1800s"), (1900, 1939, "1900 to 1939"), (1940, 2100, "1940 or later")]
W["by_birth"] = {b: [dict(label=l, **wshare(H[(H.body == b) & H.born.between(a, z)])) for a, z, l in bins] for b in ("moon", "mercury", "mars")}
W["by_birth_three"] = [dict(label=l, **wshare(nv[nv.born.between(a, z)])) for a, z, l in bins]
W["far"] = wshare(H[(H.body == "moon") & (H.far == 1)]); W["near"] = wshare(H[(H.body == "moon") & (H.far == 0)])
W["moon_women_examples"] = H[(H.body == "moon") & (H.sexg == "female")].sort_values("sitelinks", ascending=False).namesake.dropna().head(8).tolist()
R["women"] = W

# features named after places on Earth (second query), above all Mars's small craters
Q = pd.read_csv(f"{DATA}/place_namesakes.csv", keep_default_na=False, na_values=[""])
mq = Q[Q.body == "mars"]; mcont = mq[mq.continent.isin(CONT_ORDER)].continent.value_counts()
R["mars_towns"] = {"n": len(mq), "features": int(mq.fid.nunique()), "towns": int((mq.pkind == "town or village").sum()),
                   "countries": int(mq.country.nunique()), "top": [{"country": c, "n": int(n)} for c, n in mq.country.value_counts().head(8).items()],
                   "europe_pct": pc(mcont.get("Europe", 0), mcont.sum()), "asia_pct": pc(mcont.get("Asia", 0), mcont.sum()),
                   "africa_pct": pc(mcont.get("Africa", 0), mcont.sum()), "sam_pct": pc(mcont.get("South America", 0), mcont.sum()),
                   "cont": {c: int(mcont.get(c, 0)) for c in CONT_ORDER}, "nonhuman_pct": pc(mq.fid.nunique(), B["mars"]["nonhuman"]),
                   "uk": mq[mq.iso3 == "GBR"].place.dropna().tolist()}
R["moon_earth_places"] = Q[Q.body == "moon"].place.dropna().tolist(); R["moon_earth_n"] = int(Q[Q.body == "moon"].fid.nunique())
_ov = pd.read_csv(f"{DATA}/overrides_birthplaces.csv")
R["overrides"] = int(len(_ov)); R["overrides_bp"] = int((_ov.field == "birthplace").sum()); R["overrides_sex"] = int((_ov.field == "sex").sum()); R["overrides_unk"] = int((_ov.field == "birthplace_unknown").sum()); R["overrides_link"] = int((_ov.field == "link").sum())
_au = pd.read_csv(f"{DATA}/audit_sample_40.csv"); R["audit_n"] = len(_au); R["audit_faults"] = int((_au.verdict == "fault").sum())
R["overrides_places"] = int(len(pd.read_csv(f"{DATA}/overrides_places.csv"))); R["overrides_labels"] = int(len(pd.read_csv(f"{DATA}/overrides_labels.csv")))

# continents table for every body (in order) and occupation table, for figures
R["occ_names"] = OCC_NAME; R["occ_cols"] = OCC_COL
R["checks"] = {"moon_europe_gt_70": B["moon"]["europe_pct"] > 70, "mercury_most_diverse": all(B["mercury"]["europe_pct"] < B[b]["europe_pct"] for b in ("moon", "venus", "mars"))}
assert all(R["checks"].values()), R["checks"]
jsave(R, f"{DATA}/results.json", indent=1)

# ---------- page data ----------
cont_i = {c: i for i, c in enumerate(CONT_ORDER)}
occ_k = [k for k, *_ in OCC] + ["unknown"]
pp = P.reset_index(drop=True); pidx = {p: i for i, p in enumerate(pp.pid)}
r6 = lambda v: None if pd.isna(v) else round(float(v), 3)
people = [[r.pid, r.name if isinstance(r.name, str) else r.pid, None if pd.isna(r.born) else int(r.born), None if pd.isna(r.died) else int(r.died),
           r.birthplace if isinstance(r.birthplace, str) else "", r6(r.blon), r6(r.blat), r.country if isinstance(r.country, str) else "",
           cont_i.get(r.continent, -1), occ_k.index(r.occ), int(r.sitelinks), r.occupations if isinstance(r.occupations, str) else "", r.sexg if isinstance(r.sexg, str) else ""] for r in pp.itertuples()]
kinds = list(CM["kind_names"]); bodies = [b for b, *_ in BODIES]
feats = [[r.fid, r.name, bodies.index(r.body), kinds.index(r.kind), r6(r.lon), r6(r.lat), None if pd.isna(r.diam) else round(float(r.diam), 1),
          pidx.get(r.pid, -1), "" if r.human else (r.namesake if isinstance(r.namesake, str) else ""), int(r.far)] for r in F.itertuples()]
site = {"pcols": ["pid", "name", "born", "died", "bp", "lon", "lat", "country", "cont", "occ", "sl", "occs", "sex"],
        "fcols": ["fid", "name", "body", "kind", "lon", "lat", "diam", "p", "namesake", "far"],
        "people": people, "features": feats,
        "pcols2": ["fid", "feature", "body", "place", "lon", "lat", "country", "kind", "nid"],
        "places": [[r.fid, r.feature, bodies.index(r.body), r.place, r6(r.plon), r6(r.plat), r.country if isinstance(r.country, str) else "", r.pkind, r.nid] for r in Q.itertuples()], "bodies": [[b, BNAME[b], BCOL[b]] for b in bodies],
        "kinds": [[k, CM["kind_names"][k]] for k in kinds], "conts": CONT_ORDER,
        "cont_cols": ["#2F5FA7", "#C8322B", "#E0A11B", "#2E9A8C", "#7B57A8", "#B4532A"],
        "occ": [[k, OCC_NAME.get(k, "Occupation not recorded"), OCC_COL.get(k, "#BBB3A6")] for k in occ_k],
        "tiles": TILES, "att": OPM_ATT}
jsave(site, f"{DATA}/site.json")
print("results:", {b: (v["namings"], v["europe_pct"]) for b, v in B.items()}, "far", FS["far"]["ussr_pct"], FS["near"]["ussr_pct"], "site", os.path.getsize(f"{DATA}/site.json") // 1024, "KB")
