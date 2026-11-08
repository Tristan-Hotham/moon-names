"""Step 7: README.md from data/results.json."""
from common import *
R = jload(f"{DATA}/results.json"); B, M, FS = R["body"], R["moon"], R["far"]
t = f"""# Who's on the Moon? The birthplaces of the people other worlds are named after

A map and analysis of {R['source']['features']:,} named features on the Moon, Mercury, Venus and Mars, {R['all']['namings']:,} of them named after {R['source']['people']:,} people, linked through Wikidata to the {R['n_birthplaces']:,} places on Earth where those people were born. Two linked maps: click a crater and fly to its namesake's home town, or click a town and see everything named after the people born there.

Interactive page: {PAGE}
Paper: https://doi.org/{{10.5281/zenodo.24055578}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/moon-names/}}

## Headline results

- Europe: {B['moon']['europe_pct']:.1f}% of lunar features named after a person with a known birthplace honour someone born in Europe ({B['moon']['cont']['North America']['pct']:.1f}% North America, {B['moon']['cont']['Asia']['pct']:.1f}% Asia). Mercury is the least European ({B['mercury']['europe_pct']:.1f}%, with {B['mercury']['cont']['Asia']['pct']:.1f}% Asia); Venus {B['venus']['europe_pct']:.1f}%, Mars {B['mars']['europe_pct']:.1f}%.
- Paris: {M['paris_n']} lunar features honour people born in Paris; Africa ({M['africa_n']}), South America ({M['sam_n']}) and Oceania ({M['oce_n']}) together have {M['south_n']}.
- Countries: on the Moon the United States ({B['moon']['top'][0]['pct']:.1f}%), Germany ({B['moon']['top'][1]['pct']:.1f}%), the UK ({B['moon']['top'][2]['pct']:.1f}%) and France ({B['moon']['top'][3]['pct']:.1f}%) lead; the US leads Venus ({B['venus']['top'][0]['pct']:.1f}%) and Mars ({B['mars']['top'][0]['pct']:.1f}%).
- Occupations follow the IAU's rules: {B['moon']['occ']['astro']['pct']:.1f}% of lunar namesakes were astronomers; {R['mercury']['arts_any_pct']:.1f}% of Mercury's had an artistic or literary occupation.
- Far side: {FS['far']['ussr_pct']:.1f}% of far-side namesakes were born in the former Soviet Union, against {FS['near']['ussr_pct']:.1f}% on the near side; median birth year {FS['far']['born_median']} against {FS['near']['born_median']}; {FS['far']['space_people']} astronauts and cosmonauts.
- Women: {R['women']['moon']['pct']:.1f}% of lunar namesakes with a recorded sex are women, {R['women']['mercury']['pct']:.1f}% on Mercury and {R['women']['mars']['pct']:.1f}% on Mars (Venus {R['women']['venus']['pct']:.1f}%, by IAU rule); {R['women']['by_birth_three']['3']['pct'] if False else R['women']['by_birth_three'][3]['pct']:.1f}% of namesakes born since 1940 on those three worlds.
- Mars's villages: {R['mars_towns']['features']} Martian features are named after places on Earth in {R['mars_towns']['countries']} countries; {R['mars_towns']['europe_pct']:.1f}% are in Europe, against {B['mars']['europe_pct']:.1f}% of Mars's people.
- Birthplaces: Paris ({R['towns'][0]['n']} features across four worlds), London ({R['towns'][1]['n']}), Saint Petersburg ({R['towns'][2]['n']}), Moscow ({R['towns'][3]['n']}).

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/03_build_site.py`): two linked MapLibre maps, the body on parchment (optional OpenPlanetaryMap imagery for the Moon and Mars) and Earth in the Inked World style. |
| `header.png` | Social card, 1200 x 630. |
| `data/features.csv` | One row per feature and namesake: Wikidata id, name, body, kind, longitude, latitude, diameter, far side flag, namesake. |
| `data/place_namesakes.csv` | Features named after places on Earth: feature, body, place, coordinates, country, continent, kind. |
| `data/overrides_birthplaces.csv` | Documented corrections to Wikidata birthplaces and sex values (applied by `code/01_clean.py`). |
| `data/overrides_labels.csv` | Names supplied for people whose English label was missing from the query extract. |
| `data/audit_sample_40.csv` | Post-fix check of 40 namesakes chosen at random, with the verdict for each. |
| `data/overrides_places.csv` | Corrections to Earth place namesakes: country or island links moved to the named town, ships dropped. |
| `data/people.csv` | One row per person: sex, dates, birthplace and coordinates, Wikidata country, modern country and continent (Natural Earth), occupation group and occupations, sitelinks, features per body. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/site.json` | Page data. Other files in `data/`, `js/` and `fonts/` belong to the Inked World map style. |
| `code/` | Scripts, run in order, and the page, paper and blog templates; `qa.js` for screenshots. |
| `release/` | Paper PDF and LaTeX (`paper/`), blog post, figures and meta (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots at desktop and phone widths. |

## Method in brief

- One Wikidata query (through QLever) for items with coordinates on the Moon, Mercury, Venus or Mars and a "named after" (P138) statement, with the namesake's birthplace (P19), dates, occupations and sitelinks. {R['source']['rows']:,} rows, deduplicated to {R['source']['features']:,} features ({R['source']['quad']} map quadrangles excluded).
- Birthplaces placed in modern Natural Earth countries and continents by point in polygon; "former Soviet Union" is the fifteen former Soviet republics. People with two birthplaces keep the first with coordinates.
- Occupations grouped by keyword into seven groups in priority order (astronauts, astronomers, other scientists, arts, explorers, scholars, others).
- Far side: longitude beyond 90 degrees east or west.
- Sex (P21) and places on Earth that features are named after come from two further Wikidata queries. Shares of women are among namesakes recorded as female or male.
- Overrides: full checks of every birthplace given as a country, empire or region, every Wikidata/map country mismatch, every missing name or contradictory sex value and every Mars place namesake. {R['overrides_bp']} birthplaces corrected (e.g. Maclaurin, Edna Manley, Gavriil Tikhov), {R['overrides_unk']} left unmapped rather than plotted at a centroid, {R['overrides_sex']} sex values, {R['overrides_link']} wrong links, {R['overrides_labels']} missing names and {R['overrides_places']} place links fixed. A fresh random sample of 40 namesakes after the fixes found {R['audit_faults']} with a remaining fault (Lucretius's conjectural birthplace, since removed). Other errors will remain.
- Correction: one vandalised namesake label in Wikidata ("Lady Jane Greykjbh") is corrected to Lady Jane Grey.

## Caveats

Wikidata is not the IAU Gazetteer of Planetary Nomenclature; coverage of "named after" is uneven. On Mars most features ({R['mars_places']['nonhuman']} of {B['mars']['features']}) are named after places rather than people; {R['mars_towns']['features']} of them have an Earth namesake with coordinates and are mapped. Wikidata contains some errors; documented corrections are listed in the overrides files. Modern borders are applied to all birthplaces. Sex is as recorded in Wikidata.

## Sources and licences

- Wikidata contributors, Wikidata (CC0), queried with QLever.
- IAU WGPSN, Gazetteer of Planetary Nomenclature (USGS), for the naming rules: https://planetarynames.wr.usgs.gov/
- Natural Earth (public domain). Map style on OpenStreetMap data (ODbL) via OpenFreeMap. Moon and Mars imagery on the page: {OPM_ATT}.
- Text, figures and derived data CC BY 4.0; code MIT (see LICENSE).

## How to rerun

```
cd code
python3 01_clean.py && python3 02_analysis.py && python3 03_build_site.py && python3 04_figures.py && python3 05_paper.py
cd .. && python3 reddit/collage.py && python3 code/07_readme.py && cd code && python3 06_release.py
```
Raw input paths are documented in `code/common.py`.

## Citation

Hotham, T. (2026) Who's on the Moon? The birthplaces of the people the Moon, Mercury, Venus and Mars are named after. Zenodo. https://doi.org/{{10.5281/zenodo.24055578}}

{AI}
"""
for bad in ("—", "–", "--"): assert bad not in t.replace("|---|---|", ""), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(t)
print("README", len(t.split()), "words")
