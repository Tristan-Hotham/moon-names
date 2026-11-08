"""Shared paths, groupings and helpers for the moon-names study ("Who's on the Moon?").

Raw inputs (read in place, never modified):
  RAW   /home/claude/newdata/raw_new8/moon_names.tsv
        Wikidata, queried through QLever (CC0). One row per combination of: a named surface feature (?f, label ?fl) of
        the Moon (Q405), Mars (Q111), Mercury (Q308) or Venus (Q313) (?body), its type (P31, ?type/?typel), its
        coordinates on that body (P625, ?fcoord, WKT "Point(lon lat)"), diameter (P2386, ?diam, km), what it is named
        after (P138, ?p/?pl) and that namesake's instance of (?ptype, Q5 = human), birthplace (P19, ?bp/?bpl),
        the birthplace's coordinates (?bpcoord) and country (P17, ?bpc/?bpcl), date of birth and death (?bd, ?dd),
        occupations (P106, ?occl) and the namesake's number of Wikipedia sitelinks (?sl). Rows repeat for every
        type and occupation; 01_clean.py deduplicates.
  SEX   /home/claude/newdata/raw_new8/moon_namesake_sex.tsv: Wikidata (CC0), namesake, sex or gender (P21) QID and label.
  PLACES /home/claude/newdata/raw_new8/planet_place_namesakes.tsv: Wikidata (CC0), features on the four bodies named after
        things that are not people and have coordinates: feature, label, body, namesake, label, coordinates (on Earth
        when the WKT has no body prefix), country and type.
  GEO   /home/claude/newdata/raw/geo/ne_10m_admin_0_countries.geojson (Natural Earth, public domain): modern country
        and continent of each birthplace, by point in polygon.
  FONTS /home/claude/ref/fonts (Fraunces, Source Serif 4, IBM Plex Mono)
  INK   /home/claude/studies/colour-names (js/, fonts/ and the base data files of the Inked World map style)
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("MN_RAW", "/home/claude/newdata/raw_new8/moon_names.tsv")
SEX = os.environ.get("MN_SEX", "/home/claude/newdata/raw_new8/moon_namesake_sex.tsv")
PLACES = os.environ.get("MN_PLACES", "/home/claude/newdata/raw_new8/planet_place_namesakes.tsv")
GEO = os.environ.get("MN_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("MN_FONTS", "/home/claude/ref/fonts")
INK = os.environ.get("MN_INK", "/home/claude/studies/colour-names")
DATA = os.path.join(ROOT, "data")
WORK = os.environ.get("MN_WORK", "/tmp/claude-0/s/moon-names-work")   # intermediates, not in the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "moon-names"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
WD = "https://www.wikidata.org/wiki/"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
OPM_ATT = "OpenPlanetaryMap basemaps (OpenPlanetary), from NASA and USGS data"
TILES = {"moon": "https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-moon-basemap-v0-1/all/{z}/{x}/{y}.png",
         "mars": "https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mars-basemap-v0-2/all/{z}/{x}/{y}.png"}

BODIES = [("moon", "Q405", "Moon", "#6E6A63"), ("mercury", "Q308", "Mercury", "#8A5A2B"),
          ("venus", "Q313", "Venus", "#C08A1E"), ("mars", "Q111", "Mars", "#B0301F")]
BODY_OF = {q: k for k, q, _, _ in BODIES}
BNAME = {k: n for k, _, n, _ in BODIES}
BCOL = {k: c for k, _, _, c in BODIES}

# What the namesake did: the first group (in this order) that any of their Wikidata occupations falls in.
OCC = [
    ("space", "Astronauts and cosmonauts", r"astronaut|cosmonaut"),
    ("astro", "Astronomers", r"astronom|astrophysic|selenograph|cosmolog"),
    ("science", "Other scientists, mathematicians and engineers",
     r"physic|mathemat|chemist|engineer|inventor|geolog|geophysic|naturalist|botan|zoolog|biolog|geograph|cartograph|"
     r"meteorolog|scientist|physician|surveyor|geodes|seismolog|mineralog|crystallograph|statistic|anatom|"
     r"oceanograph|biochem|optician|instrument maker|clockmaker|geneticist|polymath|computer|science"),
    ("arts", "Writers, artists and musicians",
     r"writer|poet|novelist|painter|composer|playwright|artist|sculptor|musician|singer|photograph|architect|actor|actress|"
     r"illustrat|printmaker|draftsperson|dramatist|librettist|essayist|film|dancer|choreograph|pianist|calligraph|"
     r"musicolog|conductor|lyricist|author|storyteller|designer|craft|potter|weaver|songwriter|organist|violin|"
     r"cartoonist|comics|engraver|literary|translator|journalist"),
    ("explore", "Explorers, navigators and aviators", r"explorer|navigator|sailor|naval officer|mountaineer|polar|aviator|pilot"),
    ("thought", "Philosophers, scholars and religious figures",
     r"philosoph|theolog|priest|monk|historian|scholar|classicist|astrolog|teacher|professor|cleric|bishop|jesuit|rabbi|saint"),
    ("other", "Rulers, politicians and others", r"."),
]
OCC_NAME = {k: n for k, n, _ in OCC}
OCC_COL = {"space": "#2F5FA7", "astro": "#1F2F4D", "science": "#2E9A8C", "arts": "#C8322B", "explore": "#E0A11B",
           "thought": "#7B57A8", "other": "#8C8478"}

# The former Soviet Union, by modern country (ISO 3166 alpha-3, as Natural Earth gives them)
USSR = set("RUS UKR BLR KAZ UZB TKM KGZ TJK AZE ARM GEO MDA LTU LVA EST".split())
CONT_ORDER = ["Europe", "North America", "Asia", "South America", "Africa", "Oceania"]


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def nonan(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, dict):
        return {str(k): nonan(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "word": return WORDS[int(v)] if int(v) < len(WORDS) else f"{int(v):,}"
    if f == "Word": return (WORDS[int(v)] if int(v) < len(WORDS) else f"{int(v):,}").capitalize()
    raise ValueError(f)


def fill(tpl, R, keep=("DOI", "DOI_URL", "BLOG_URL")):
    return re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}",
                  lambda m: m.group(0) if m.group(1) in keep else fmt(get(R, m.group(1)), m.group(3)), tpl)
