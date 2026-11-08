# Who's on the Moon? The birthplaces of the people other worlds are named after

A map and analysis of 3,471 named features on the Moon, Mercury, Venus and Mars, 2,718 of them named after 2,560 people, linked through Wikidata to the 1,661 places on Earth where those people were born. Two linked maps: click a crater and fly to its namesake's home town, or click a town and see everything named after the people born there.

Interactive page: https://maps.tristanhotham.com/moon-names/
Paper: https://doi.org/10.5281/zenodo.24055578
Blog post: https://blog.tristanhotham.com/2026/10/31/moon-names/

## Headline results

- Europe: 75.3% of lunar features named after a person with a known birthplace honour someone born in Europe (16.1% North America, 6.6% Asia). Mercury is the least European (54.9%, with 19.7% Asia); Venus 61.5%, Mars 64.8%.
- Paris: 38 lunar features honour people born in Paris; Africa (19), South America (6) and Oceania (6) together have 31.
- Countries: on the Moon the United States (15.1%), Germany (13.1%), the UK (12.4%) and France (10.8%) lead; the US leads Venus (23.2%) and Mars (28.2%).
- Occupations follow the IAU's rules: 52.0% of lunar namesakes were astronomers; 97.6% of Mercury's had an artistic or literary occupation.
- Far side: 19.9% of far-side namesakes were born in the former Soviet Union, against 3.5% on the near side; median birth year 1874 against 1784; 35 astronauts and cosmonauts.
- Women: 2.8% of lunar namesakes with a recorded sex are women, 17.8% on Mercury and 5.5% on Mars (Venus 99.8%, by IAU rule); 30.9% of namesakes born since 1940 on those three worlds.
- Mars's villages: 279 Martian features are named after places on Earth in 102 countries; 30.4% are in Europe, against 64.8% of Mars's people.
- Birthplaces: Paris (69 features across four worlds), London (40), Saint Petersburg (37), Moscow (29).

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

- One Wikidata query (through QLever) for items with coordinates on the Moon, Mercury, Venus or Mars and a "named after" (P138) statement, with the namesake's birthplace (P19), dates, occupations and sitelinks. 19,194 rows, deduplicated to 3,471 features (90 map quadrangles excluded).
- Birthplaces placed in modern Natural Earth countries and continents by point in polygon; "former Soviet Union" is the fifteen former Soviet republics. People with two birthplaces keep the first with coordinates.
- Occupations grouped by keyword into seven groups in priority order (astronauts, astronomers, other scientists, arts, explorers, scholars, others).
- Far side: longitude beyond 90 degrees east or west.
- Sex (P21) and places on Earth that features are named after come from two further Wikidata queries. Shares of women are among namesakes recorded as female or male.
- Overrides: full checks of every birthplace given as a country, empire or region, every Wikidata/map country mismatch, every missing name or contradictory sex value and every Mars place namesake. 18 birthplaces corrected (e.g. Maclaurin, Edna Manley, Gavriil Tikhov), 31 left unmapped rather than plotted at a centroid, 2 sex values, 3 wrong links, 41 missing names and 10 place links fixed. A fresh random sample of 40 namesakes after the fixes found 1 with a remaining fault (Lucretius's conjectural birthplace, since removed). Other errors will remain.
- Correction: one vandalised namesake label in Wikidata ("Lady Jane Greykjbh") is corrected to Lady Jane Grey.

## Caveats

Wikidata is not the IAU Gazetteer of Planetary Nomenclature; coverage of "named after" is uneven. On Mars most features (350 of 584) are named after places rather than people; 279 of them have an Earth namesake with coordinates and are mapped. Wikidata contains some errors; documented corrections are listed in the overrides files. Modern borders are applied to all birthplaces. Sex is as recorded in Wikidata.

## Sources and licences

- Wikidata contributors, Wikidata (CC0), queried with QLever.
- IAU WGPSN, Gazetteer of Planetary Nomenclature (USGS), for the naming rules: https://planetarynames.wr.usgs.gov/
- Natural Earth (public domain). Map style on OpenStreetMap data (ODbL) via OpenFreeMap. Moon and Mars imagery on the page: OpenPlanetaryMap basemaps (OpenPlanetary), from NASA and USGS data.
- Text, figures and derived data CC BY 4.0; code MIT (see LICENSE).

## How to rerun

```
cd code
python3 01_clean.py && python3 02_analysis.py && python3 03_build_site.py && python3 04_figures.py && python3 05_paper.py
cd .. && python3 reddit/collage.py && python3 code/07_readme.py && cd code && python3 06_release.py
```
Raw input paths are documented in `code/common.py`.

## Citation

Hotham, T. (2026) Who's on the Moon? The birthplaces of the people the Moon, Mercury, Venus and Mars are named after. Zenodo. https://doi.org/10.5281/zenodo.24055578

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
