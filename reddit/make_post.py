"""Writes reddit/post.md from data/results.json."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(ROOT, "data", "results.json"))); B = R["body"]; F = R["far"]; W = R["women"]; MT = R["mars_towns"]
post = f"""**Title:** [OC] Who's on the Moon? {B['moon']['europe_pct']:.0f}% of the people lunar craters are named after were born in Europe, and Paris ({R['moon']['paris_n']}) beats Africa, South America and Oceania combined ({R['moon']['south_n']})

**Body:**

I linked every feature on the Moon (and Mercury, Venus and Mars) that Wikidata says is named after a person to that person's birthplace on Earth.

- {B['moon']['europe_pct']:.0f}% of the Moon's namesakes with a known birthplace were born in Europe. Mercury, whose craters go to artists, writers and composers, is the least European at {B['mercury']['europe_pct']:.0f}%.
- Paris has {R['moon']['paris_n']} lunar features; Africa, South America and Oceania together have {R['moon']['south_n']}.
- Only {W['moon']['pct']:.1f}% of the Moon's namesakes are women ({W['mercury']['pct']:.1f}% on Mercury, {W['mars']['pct']:.1f}% on Mars; Venus is women by rule).
- The far side, first photographed by the Soviet Luna 3 in 1959, has {F['far']['ussr_pct']:.1f}% namesakes born in the former Soviet Union, against {F['near']['ussr_pct']:.1f}% on the near side.
- Mars's small craters are named after towns and villages on Earth: Wikidata maps {MT['features']} Martian features to places in {MT['countries']} countries ({MT['towns']} of them towns and villages), only {MT['europe_pct']:.0f}% in Europe.

Interactive version (click a crater, fly to its namesake's home town): https://maps.tristanhotham.com/moon-names/

**Source comment:**

Data: Wikidata "named after" (P138) statements for features with coordinates on the Moon, Mercury, Venus and Mars, with each person's birthplace (P19) and sex (P21), queried through QLever (CC0). Countries and continents are modern, from Natural Earth. Wikidata is not the IAU's official gazetteer and has gaps and some errors (a few birthplaces, names and place links corrected in documented overrides files). Tools: Python (pandas, geopandas, matplotlib), MapLibre. Paper, data and code: https://github.com/Tristan-Hotham/moon-names
"""
open(os.path.join(ROOT, "reddit", "post.md"), "w").write(post)
