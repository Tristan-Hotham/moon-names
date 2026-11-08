"""Step 3: build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json (embedded in the page); the feature and people data (data/site.json) are fetched when the page loads.
Facts stated in words are checked here. The full-screen snippet (code/fullscreen_snippet.html) goes before </body>.
10.5281/zenodo.24055578 and https://blog.tristanhotham.com/2026/10/31/moon-names/ stay as placeholders for the publisher."""
import json
from common import *

R = jload(f"{DATA}/results.json")
B, M, FS = R["body"], R["moon"], R["far"]

# facts stated in words (page, blog, paper, collage)
assert [t["country"] for t in B["moon"]["top"][:4]] == ["United States", "Germany", "United Kingdom", "France"]
assert {t["country"] for t in B["moon"]["top"][4:6]} == {"Italy", "Russia"}
assert B["venus"]["top"][0]["country"] == B["mars"]["top"][0]["country"] == "United States"
assert B["venus"]["top"][0]["pct"] > B["moon"]["top"][0]["pct"] and B["mars"]["top"][0]["pct"] > B["moon"]["top"][0]["pct"]
assert M["paris_n"] > M["south_n"] and M["egypt_n"] > M["africa_n"] / 2 and M["alex_n"] >= 5           # "mostly ... Alexandria"
assert B["mercury"]["europe_pct"] == min(B[b]["europe_pct"] for b in B)                                   # Mercury least European
assert B["moon"]["born_before_1500"] > 100 and M["asia_top"] == "Turkey" and M["asia_pre1500"] > B["moon"]["cont"]["Asia"]["n"] / 2
assert max(B["moon"]["cent"], key=lambda c: B["moon"]["cent"][c]) == "19"                                 # biggest cohort 19th century
assert B["moon"]["occ"]["astro"]["pct"] > 50 and B["mercury"]["occ"]["arts"]["pct"] > 85
assert B["venus"]["occ"]["other"]["pct"] == max(B[b]["occ"]["other"]["pct"] for b in B)
assert FS["far_1in"] == 5                # pull quote
assert FS["far"]["born_median"] > FS["near"]["born_median"] and FS["far"]["us_pct"] > FS["near"]["us_pct"]
for n in ("Yuri Gagarin", "Valentina Tereshkova", "Gus Grissom", "Ed White", "Roger Bruce Chaffee", "Dick Scobee", "Christa McAuliffe", "Rick Husband", "Kalpana Chawla"):
    assert n in FS["far_space"], n                                                                      # Apollo 1, Challenger, Columbia
assert [t["place"] for t in R["towns"][:4]] == ["Paris", "London", "Saint Petersburg", "Moscow"]
assert len(R["multi"]["three"]) == 3
W, MT = R["women"], R["mars_towns"]
assert W["venus_men"] == ["James Clerk Maxwell"] and W["venus"]["women"] == W["venus"]["n"] - 1
assert 1 / 36 < W["moon"]["women"] / W["moon"]["n"] < 1 / 30                                          # "fewer than one in thirty"
assert {"Hypatia", "Hildegard of Bingen", "Lise Meitner", "Emmy Noether", "Valentina Tereshkova"} <= set(W["moon_women_examples"])
import pandas as pd
_F = pd.read_csv(f"{DATA}/features.csv"); _P = pd.read_csv(f"{DATA}/people.csv"); _H = _F[_F.human == 1].merge(_P, on="pid")
_y = _H[(_H.body != "venus") & (_H.born >= 1940) & (_H.sexg == "female")].namesake
assert {"Judith Resnik", "Christa McAuliffe", "Kalpana Chawla", "Laurel Clark"} <= set(_y), set(_y)
assert [t["country"] for t in MT["top"][:3]] == ["United States", "India", "China"] and {"Crewe", "Corby", "Maidstone", "Kilkhampton"} <= set(MT["uk"])
assert MT["europe_pct"] < R["body"]["mars"]["europe_pct"] / 2 + 1
assert {"Alps", "Apennines", "Carpathians", "Caucasus Mountains"} <= set(R["moon_earth_places"])
assert M["paris_n"] > M["south_n"]


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = fill(tpl, R)
    left = set(re.findall(r"\{\{[^}]*\}\}", html))
    assert left <= {"10.5281/zenodo.24055578", "https://blog.tristanhotham.com/2026/10/31/moon-names/"}, left
    html = html.replace("/*RESULTS*/", json.dumps(R, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv", "Civil Serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
