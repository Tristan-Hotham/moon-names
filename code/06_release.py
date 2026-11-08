"""Step 6: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24055578, https://doi.org/10.5281/zenodo.24055578 and https://blog.tristanhotham.com/2026/10/31/moon-names/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Moon_Names"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}

# facts in words in the blog and alt text
P = pd.read_csv(f"{DATA}/people.csv"); F = pd.read_csv(f"{DATA}/features.csv")
H = F[F.human == 1].merge(P, on="pid")
merc = set(H[H.body == "mercury"].namesake)
assert {"Johann Sebastian Bach", "Ludwig van Beethoven", "Leo Tolstoy", "Katsushika Hokusai", "Tyagaraja", "Tansen", "Li Qingzhao"} <= merc
paris = set(H[(H.body == "moon") & (H.birthplace == "Paris")].namesake)
assert {"Léon Foucault", "Hippolyte Fizeau", "Antoine Lavoisier", "Cyrano de Bergerac"} <= paris
B = R["body"]
assert [round(B[b]["europe_pct"]) for b in ("moon", "mercury", "venus", "mars")] == [75, 55, 61, 65]
assert [round(B[b]["cont"]["North America"]["pct"]) for b in ("moon", "mercury", "venus", "mars")] == [16, 16, 24, 29]
assert [round(B[b]["top"][0]["pct"]) for b in ("moon", "mercury", "venus", "mars")] == [15, 14, 23, 28]
assert round(B["moon"]["occ"]["astro"]["pct"]) == 52 and round(B["mercury"]["occ"]["arts"]["pct"]) == 90 and round(B["venus"]["occ"]["arts"]["pct"]) == 66
assert [t["n"] for t in R["towns"][:12]] == [69, 40, 37, 29, 18, 17, 16, 14, 13, 13, 13, 12]
assert R["moon"]["asia_pre1500"] > B["moon"]["cont"]["Asia"]["n"] / 2
W = R["women"]; assert [round(W[b]["pct"], 1) for b in ("moon", "mercury", "venus", "mars")] == [2.8, 17.8, 99.8, 5.5]
assert [round(x["pct"], 1) for x in W["by_birth_three"]] == [2.6, 4.8, 16.7, 30.9]

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = fill(post, R)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
from PIL import Image
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used: os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Who's on the Moon? The birthplaces of the people we named other worlds after",
        "slug": "moon-names",
        "excerpt": f"I traced {R['all']['namings']:,} names on the Moon, Mercury, Venus and Mars back to the towns where those people were born. {B['moon']['europe_pct']:.0f}% of the Moon's people were born in Europe, and Paris alone outnumbers Africa, South America and Oceania.",
        "seo_description": f"Whose names are on the Moon? {B['moon']['europe_pct']:.0f}% of lunar namesakes were born in Europe. A map linking craters to birthplaces on Earth.",
        "tags": ["maps", "Moon", "space", "planetary names", "Wikidata", "data visualisation", "history of science", "geography"],
        "header_alt": f"Title card reading 'Who's on the Moon?' in black and red on parchment, beside a world map with coloured dots at the birthplaces of the people lunar craters are named after, densest in Europe, with the lines '{B['moon']['europe_pct']:.0f}% of the Moon's people were born in Europe' and 'Paris: {R['moon']['paris_n']} lunar features. Africa, South America and Oceania together: {R['moon']['south_n']}.'"}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z): os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(os.path.join(ROOT, "code"))):
        if fn.endswith(".pyc") or fn == "__pycache__": continue
        z.write(os.path.join(ROOT, "code", fn), f"{SLUG}/code/{fn}")
    for fn in ("features.csv", "people.csv", "place_namesakes.csv", "overrides_birthplaces.csv", "overrides_labels.csv", "overrides_places.csv", "audit_sample_40.csv", "results.json", "site.json"):
        z.write(os.path.join(DATA, fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&")
ab = re.sub(r"\\textit\{([^}]*)\}", r"\1", ab)
zmeta = {"title": "Who's on the Moon? The Birthplaces of the People that Features on the Moon, Mercury, Venus and Mars Are Named After",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/moon-names/}}.</p><p>Sources: Wikidata (CC0), queried with QLever; Natural Earth (public domain); map style on OpenStreetMap data (ODbL) via OpenFreeMap. Derived data and text CC BY 4.0, code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["planetary nomenclature", "Moon", "Mercury", "Venus", "Mars", "toponymy", "commemoration", "Wikidata", "maps", "open data"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
