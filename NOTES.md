# moon-names: working notes
- Pipeline: code/01_clean.py -> 02_analysis.py -> 03_build_site.py -> 04_figures.py -> 05_paper.py -> 06_release.py -> 07_readme.py; reddit/collage.py; code/qa.js (server on 8801).
- Ink map assets (js/, fonts/, data/ ink files) copied from colour-names.
- Data gaps: no namesake sex (P21) in the extract; no coordinates for Mars place namesakes (351 features).
- Wikidata errors seen: Colin Maclaurin birthplace "The Manse" in Australia; "Lady Jane Greykjbh" label vandalism.
- Status: page built and QA passing (desktop and phone). Next: figures, paper, blog, release, collage, README.
- DONE: page, figures, paper (9 pp), blog (6 figs), zenodo, collage, post, README. QA 26/26 ok both widths. Study ~32 MB.
- UPDATE: added sex (women share), Mars place-namesakes layer/section, birthplace overrides file (Maclaurin), Crimea as Ukraine; all rebuilt, QA ok.
- REVIEW (independent): sample audit 60 people (7 with a fault, 1 wrong birthplace) and 30 Mars places (3 faults); added overrides_labels.csv, overrides_places.csv, sex/link rows in overrides_birthplaces.csv; fixed wording (Soviet Union, Alexandria, astronaut count 35, Reddit Mars line), alt text, collage label/legend; all rebuilt, QA 30/30.
- FULL PASS: all region/country birthplaces, country mismatches, names/sex, all Mars places checked; 21 birthplace fixes, 31 unmapped, 3 link removals (incl. Barlow), 10 place overrides; post-fix audit 40 (data/audit_sample_40.csv): 1 fault (Lucretius), fixed. Rebuilt, QA ok.
