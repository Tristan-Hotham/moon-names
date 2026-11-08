"""Step 4: static figures for the blog (release/blog/b_*.png, 1800 px wide), the paper (release/paper/f_*.png) and the
social card (header.png). House style: parchment paper, ink, Fraunces titles, IBM Plex Mono labels; labels sit on the
paper or the sea, never over the data."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Circle
import numpy as np, pandas as pd, geopandas as gpd
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
plt.rcParams.update({"font.family": "IBM Plex Mono", "font.size": 12, "axes.edgecolor": "#6E604E", "xtick.color": "#6E604E", "ytick.color": "#6E604E"})
BG, FG, MUT, RULE, SEA, LAND = "#F6EED8", "#2B2119", "#6E604E", "#E2D3AE", "#DCE6E4", "#EFE2BF"
CCOL = dict(zip(CONT_ORDER, ["#2F5FA7", "#C8322B", "#E0A11B", "#2E9A8C", "#7B57A8", "#B4532A"]))
R = jload(f"{DATA}/results.json")
F = pd.read_csv(f"{DATA}/features.csv"); P = pd.read_csv(f"{DATA}/people.csv")
H = F[F.human == 1].merge(P, on="pid", how="left", suffixes=("", "_p"))
L = H[H.continent.notna()]
BL = os.path.join(ROOT, "release", "blog"); PA = os.path.join(ROOT, "release", "paper")
for d in (BL, PA): os.makedirs(d, exist_ok=True)
BODS = [b for b, *_ in BODIES]


def save(fig, name, paper=True):
    fig.savefig(f"{BL}/b_{name}.png", dpi=200, facecolor=BG)
    if paper: fig.savefig(f"{PA}/f_{name}.png", dpi=150, facecolor=BG)
    plt.close(fig)


import textwrap
def title(fig, t, sub, y=.965):
    h = fig.get_size_inches()[1]
    fig.text(.03, y, t, fontproperties=DISP, fontsize=25, color=FG, va="top")
    fig.text(.03, y - .5 / h, "\n".join(textwrap.wrap(sub, 84)), fontsize=11.5, color=MUT, va="top", linespacing=1.35)


def foot(fig, s="Data: Wikidata (CC0); Natural Earth. maps.tristanhotham.com/moon-names"):
    fig.text(.03, .015, s, fontsize=9.5, color=MUT)


land = gpd.read_file(f"{GEO}/ne_50m_land.geojson")


def earth(ax, ext=(-170, 180, -58, 85)):
    ax.set_facecolor(SEA)
    land.plot(ax=ax, color=LAND, edgecolor="#8C7A58", linewidth=.35, zorder=1)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    for s in ax.spines.values(): s.set_edgecolor(FG); s.set_linewidth(1)


# 1. the world of birthplaces
def world():
    fig = plt.figure(figsize=(9, 5.4)); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([.03, .11, .94, .68]); earth(ax)
    g = L.groupby(["bpid"]).agg(lon=("blon", "first"), lat=("blat", "first"), n=("fid", "size"), b=("body", lambda s: s.value_counts().index[0])).reset_index().sort_values("n", ascending=False)
    g = g.sort_values("n", ascending=False)
    ax.scatter(g.lon, g.lat, s=6 + 9 * g.n, c=[BCOL[b] if b != "moon" else "#8E8A80" for b in g.b], edgecolor=FG, linewidth=.3, alpha=.85, zorder=3)
    nm = L[["bpid", "birthplace"]].drop_duplicates("bpid").set_index("bpid").birthplace
    for place, tx, ty in (("Paris", -25, 43), ("London", -25, 53), ("Saint Petersburg", 0, 82.3), ("Moscow", 72, 82.3)):
        r = g[g.bpid.map(nm) == place].iloc[0]
        ax.annotate(f"{place} {int(r.n)}", (r.lon, r.lat), (tx, ty), fontsize=9.5, color=FG, ha="right" if tx < r.lon - 10 else "left", va="center",
                    arrowprops=dict(arrowstyle="-", color=FG, lw=.6, shrinkB=2), bbox=dict(boxstyle="round,pad=.15", fc=SEA, ec="none", alpha=.9), zorder=5)
    title(fig, "Where the people on other worlds were born", f"{R['all']['located']:,} features on the Moon, Mercury, Venus and Mars named after a person, at the birthplace. Size: number of features. Colour: the world with the most.")
    hs = [plt.scatter([], [], s=60, c=BCOL[b] if b != "moon" else "#8E8A80", edgecolor=FG, linewidth=.3, label=BNAME[b]) for b in BODS]
    fig.legend(handles=hs, loc="lower right", frameon=False, fontsize=10, ncol=4, bbox_to_anchor=(.97, .035))
    foot(fig); save(fig, "world")


# 2. continents and 5. occupations: stacked bars
def stack(name, keys, cols, names, getv, t, sub, ncol=3, hgt=4.6):
    fig = plt.figure(figsize=(9, hgt)); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([.12, 1.05 / hgt + (.06 if ncol == 2 else 0), .85, 1 - 2.2 / hgt - (.06 if ncol == 2 else 0)]); ax.set_facecolor(BG)
    for i, b in enumerate(BODS):
        v = np.array([getv(b, k) for k in keys], float); v = 100 * v / v.sum(); x = 0
        for j, k in enumerate(keys):
            ax.barh(i, v[j], left=x, color=cols[j], edgecolor=BG, height=.72)
            if v[j] >= 6: ax.text(x + 1, i, f"{v[j]:.0f}%", va="center", fontsize=10, color="#fff")
            x += v[j]
    ax.set_yticks(range(4)); ax.set_yticklabels([BNAME[b] for b in BODS], fontsize=12); ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
    hs = [plt.Rectangle((0, 0), 1, 1, color=c) for c in cols]
    fig.legend(hs, names, loc="lower center", ncol=ncol, frameon=False, fontsize=9.5, bbox_to_anchor=(.53, .03))
    title(fig, t, sub); save(fig, name)


# 3. countries
def countries():
    fig, axs = plt.subplots(2, 2, figsize=(9, 6.6)); fig.patch.set_facecolor(BG)
    plt.subplots_adjust(left=.17, right=.96, top=.8, bottom=.07, wspace=.62, hspace=.35)
    mx = max(R["body"][b]["top"][0]["pct"] for b in BODS)
    for ax, b in zip(axs.flat, BODS):
        t = R["body"][b]["top"][:8]; ax.set_facecolor(BG)
        ax.barh(range(len(t)), [x["pct"] for x in t], color=BCOL[b], height=.7)
        for i, x in enumerate(t): ax.text(x["pct"] + .4, i, f"{x['pct']:.0f}%", va="center", fontsize=9.5)
        ax.set_yticks(range(len(t))); ax.set_yticklabels([x["country"].replace("United Kingdom", "UK").replace("United States", "US") for x in t], fontsize=10)
        ax.invert_yaxis(); ax.set_xlim(0, mx * 1.2); ax.set_xticks([]); ax.tick_params(length=0)
        for s in ax.spines.values(): s.set_visible(False)
        ax.set_title(f"{BNAME[b]}", fontproperties=DISPB, fontsize=15, loc="left", color=FG)
    title(fig, "The top countries on each world", "Share of features named after a person with a known birthplace, by modern country of birth.")
    foot(fig); save(fig, "countries")


# 4. centuries
def centuries():
    C = [c for c in range(-6, 21) if c != 0]
    fig, axs = plt.subplots(4, 1, figsize=(9, 6.4), sharex=True); fig.patch.set_facecolor(BG)
    plt.subplots_adjust(left=.13, right=.97, top=.8, bottom=.1, hspace=.25)
    for ax, b in zip(axs, BODS):
        cen = {int(k): v for k, v in R["body"][b]["cent"].items()}
        v = [sum(n for k, n in cen.items() if k <= -6) if c == -6 else cen.get(c, 0) for c in C]
        ax.bar(range(len(C)), v, color=BCOL[b], width=.8); ax.set_facecolor(BG)
        ax.set_ylabel(BNAME[b], rotation=0, ha="right", va="center", fontsize=11, color=FG)
        ax.set_yticks([]); [s.set_visible(False) for k, s in ax.spines.items() if k != "bottom"]
        ax.text(len(C) - .6, max(v) * .9, f"{max(v)}", ha="right", fontsize=9, color=MUT)
    lab = {-5: "5th c. BC", 1: "1st c. AD", 10: "10th", 15: "15th", 19: "19th"}
    axs[-1].set_xticks([C.index(c) for c in lab]); axs[-1].set_xticklabels(list(lab.values()), fontsize=10)
    title(fig, "Namesakes by century of birth", "Features named after a person with a known date of birth. Each world on its own scale; the leftmost column is the 6th century BC or earlier.")
    foot(fig); save(fig, "centuries")


# 6. the two faces of the Moon
def faces():
    fig = plt.figure(figsize=(9, 5.6)); fig.patch.set_facecolor(BG)
    m = H[(H.body == "moon") & H.lon.notna()]
    for k, (lon0, t, key) in enumerate(((0, "Near side", "near"), (180, "Far side", "far"))):
        ax = fig.add_axes([.04 + k * .48, .09, .44, .64]); ax.set_xlim(-1.08, 1.08); ax.set_ylim(-1.08, 1.12); ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(Circle((0, 0), 1, fc="#ECE6D6", ec=FG, lw=1.3))
        for la in range(-60, 61, 30):
            l = np.radians(np.arange(-90, 91, 5)); ph = np.radians(la); ax.plot(np.cos(ph) * np.sin(l), np.full_like(l, np.sin(ph)), color="#B9AC8E", lw=.5)
        for lo in range(-60, 61, 30):
            ph = np.radians(np.arange(-90, 91, 5)); ax.plot(np.cos(ph) * np.sin(np.radians(lo)), np.sin(ph), color="#B9AC8E", lw=.5)
        dl = ((m.lon - lon0 + 540) % 360) - 180; v = m[dl.abs() <= 90]; dl = dl[dl.abs() <= 90]
        x = np.cos(np.radians(v.lat)) * np.sin(np.radians(dl)); y = np.sin(np.radians(v.lat))
        sov = v.iso3.isin(USSR).values
        ax.scatter(x[~sov], y[~sov], s=9, c=[CCOL.get(c, "#BBB3A6") for c in v.continent[~sov]], edgecolor=FG, linewidth=.2, zorder=3)
        ax.scatter(x[sov], y[sov], s=24, c=[CCOL.get(c, "#BBB3A6") for c in v.continent[sov]], edgecolor=FG, linewidth=1.3, zorder=4)
        f = R["far"][key]
        ax.text(0, 1.1, f"{t}: {f['ussr_pct']:.1f}% born in the former USSR", ha="center", fontsize=11.5, color=FG, fontweight="medium")
    hs = [plt.scatter([], [], s=40, c=CCOL[c], edgecolor=FG, linewidth=.2) for c in CONT_ORDER] + [plt.scatter([], [], s=40, c="#fff", edgecolor=FG, linewidth=1.4)]
    fig.legend(hs, [f"Born in {c}" for c in CONT_ORDER] + ["Heavy ring: former USSR"], loc="lower center", ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(.5, .0))
    title(fig, "The Soviet far side", "Every lunar feature named after a person, seen from in front of each face. Colour: continent of birth.")
    save(fig, "faces")


# 7. the most lunar towns
def towns():
    T = R["towns"][:12][::-1]
    fig = plt.figure(figsize=(9, 5.6)); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([.27, .1, .68, .68]); ax.set_facecolor(BG)
    for i, t in enumerate(T):
        x = 0
        for b in BODS:
            ax.barh(i, t[b], left=x, color=BCOL[b], edgecolor=BG, height=.72); x += t[b]
        ax.text(x + .6, i, str(t["n"]), va="center", fontsize=10)
    ax.set_yticks(range(len(T))); ax.set_yticklabels([f"{t['place']}, {t['country'].replace('United Kingdom', 'UK').replace('United States', 'US')}" for t in T], fontsize=10.5)
    ax.set_xticks([]); ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
    hs = [plt.Rectangle((0, 0), 1, 1, color=BCOL[b]) for b in BODS]
    ax.legend(hs, [BNAME[b] for b in BODS], loc="lower right", frameon=False, fontsize=10)
    title(fig, "The most honoured birthplaces", "Features on the four worlds named after people born in each town.")
    foot(fig); save(fig, "towns")


def women():
    W = R["women"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.6)); fig.patch.set_facecolor(BG)
    plt.subplots_adjust(left=.14, right=.95, top=.63, bottom=.1, wspace=.55)
    for ax, rows, t in ((axs[0], [(BNAME[b], W[b]["pct"], BCOL[b]) for b in BODS], "By world"),
                        (axs[1], [(r["label"], r["pct"], "#A3261B") for r in W["by_birth_three"]], "Moon, Mercury, Mars: by birth")):
        ax.set_facecolor(BG); ax.barh(range(len(rows)), [100] * len(rows), color=RULE, height=.62)
        ax.barh(range(len(rows)), [r[1] for r in rows], color=[r[2] for r in rows], height=.62)
        for i, r in enumerate(rows): ax.text(min(r[1], 80) + 2, i, f"{r[1]:.1f}%", va="center", fontsize=10)
        ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=10.5); ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xticks([])
        ax.tick_params(length=0); [x.set_visible(False) for x in ax.spines.values()]; ax.set_title(t, fontproperties=DISPB, fontsize=14, loc="left", color=FG)
    title(fig, "Women among the namesakes", "Share of features named after a person recorded in Wikidata as female, among those recorded as female or male. Venus's features honour women by rule.")
    foot(fig); save(fig, "women")


def marsplaces():
    Q = pd.read_csv(f"{DATA}/place_namesakes.csv"); q = Q[Q.body == "mars"]
    fig = plt.figure(figsize=(9, 5.4)); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([.03, .13, .94, .62]); earth(ax, (-170, 180, -58, 80))
    KC = {"town or village": "#A3261B", "district or region": "#E0A11B", "water or valley": "#2F5FA7", "mountain or island": "#55803A", "other place": "#8C8478"}
    for k, c in KC.items():
        x = q[q.pkind == k]; ax.scatter(x.plon, x.plat, s=16, c=c, edgecolor=FG, linewidth=.3, zorder=3, label=f"{k.capitalize()} ({len(x)})")
    fig.legend(loc="lower center", ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(.5, .0))
    title(fig, "The villages of Mars", f"The {R['mars_towns']['features']} features on Mars that Wikidata says are named after a place on Earth, in {R['mars_towns']['countries']} countries. Most are small craters named after towns and villages.")
    save(fig, "marsplaces")


def header():
    fig = plt.figure(figsize=(12, 6.3), dpi=100); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([.43, .1, .55, .8]); earth(ax, (-130, 150, -45, 75))
    g = L[L.body == "moon"].groupby("bpid").agg(lon=("blon", "first"), lat=("blat", "first"), n=("fid", "size"), c=("continent", "first"))
    ax.scatter(g.lon, g.lat, s=5 + 10 * g.n, c=[CCOL[c] for c in g.c], edgecolor=FG, linewidth=.3, alpha=.9, zorder=3)
    fig.text(.04, .8, "Who's on", fontproperties=DISP, fontsize=50, color=FG)
    fig.text(.04, .66, "the Moon?", fontproperties=DISP, fontsize=50, color="#A3261B")
    fig.text(.04, .52, f"{R['body']['moon']['europe_pct']:.0f}% of the Moon's people\nwere born in Europe", fontsize=17, color=FG, va="top", linespacing=1.4)
    fig.text(.04, .32, f"Paris: {R['moon']['paris_n']} lunar features.\nAfrica, South America and\nOceania together: {R['moon']['south_n']}.", fontsize=14, color=MUT, va="top", linespacing=1.4)
    fig.text(.04, .06, "maps.tristanhotham.com/moon-names", fontsize=11, color=MUT)
    fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG); plt.close(fig)


world()
stack("continents", CONT_ORDER, [CCOL[c] for c in CONT_ORDER], CONT_ORDER, lambda b, k: R["body"][b]["cont"][k]["n"],
      "Whose world? Continent of birth", "Features named after a person with a known birthplace, by the modern continent of that birthplace.")
ks = [k for k, *_ in OCC]
stack("occupations", ks, [OCC_COL[k] for k in ks], [OCC_NAME[k].replace(", mathematicians and engineers", ", engineers") for k in ks], lambda b, k: R["body"][b]["occ"][k]["n"],
      "What the namesakes did", "Each person in the first group that any of their Wikidata occupations falls in, in legend order.", ncol=2, hgt=5.4)
countries(); centuries(); faces(); towns(); women(); marsplaces(); header()
from PIL import Image
im = Image.open(os.path.join(ROOT, "header.png")); assert im.size == (1200, 630), im.size
print("figures:", sorted(os.listdir(BL)))
