"""Reddit collage (r/dataisbeautiful style): a light parchment poster, 2560 x 1760 px. Run from the study root after
code/02_analysis.py. Labels sit on open sea or on the paper with a halo, never over land or the data."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.patches import Circle
import numpy as np, pandas as pd, geopandas as gpd
from common import *

FD = os.path.join(WORK, "fonts")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf"); DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"): fm.fontManager.addfont(f"{FONTS}/{f}")
plt.rcParams.update({"font.family": "IBM Plex Mono"})
BG, FG, MUT, SEA, LAND = "#F7F0DC", "#2B2119", "#6E604E", "#DDE7E5", "#EFE2BF"
CC = dict(zip(CONT_ORDER, ["#2F5FA7", "#C8322B", "#E0A11B", "#2E9A8C", "#7B57A8", "#B4532A"]))
HALO = [pe.withStroke(linewidth=4, foreground="white")]
R = jload(f"{DATA}/results.json")
F = pd.read_csv(f"{DATA}/features.csv"); P = pd.read_csv(f"{DATA}/people.csv")
H = F[(F.human == 1) & (F.body == "moon")].merge(P, on="pid", how="left", suffixes=("", "_p"))
L = H[H.continent.notna()]

fig = plt.figure(figsize=(16, 11), dpi=160); fig.patch.set_facecolor(BG)
fig.text(.03, .955, "Who's on the Moon?", fontproperties=DISP, fontsize=44, color=FG, va="top")
fig.text(.03, .885, f"Where the people behind {R['body']['moon']['located']:,} lunar craters, mountains and valleys were born, from Wikidata",
         fontsize=14, color=MUT, va="top")

# world map of birthplaces
ax = fig.add_axes([.03, .43, .64, .43]); ax.set_facecolor(SEA)
land = gpd.read_file(f"{GEO}/ne_50m_land.geojson"); land.plot(ax=ax, color=LAND, edgecolor="#8C7A58", linewidth=.4)
ax.set_xlim(-130, 150); ax.set_ylim(-50, 85); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
for s in ax.spines.values(): s.set_edgecolor(FG)
g = L.groupby("bpid").agg(lon=("blon", "first"), lat=("blat", "first"), n=("fid", "size"), c=("continent", "first"), nm=("birthplace", "first")).sort_values("n", ascending=False)
ax.scatter(g.lon, g.lat, s=10 + 16 * g.n, c=[CC[c] for c in g.c], edgecolor=FG, linewidth=.35, alpha=.9, zorder=3)
for nm, tx, ty in (("Paris", -32, 44), ("London", -32, 55), ("Saint Petersburg", 0, 82.4), ("Moscow", 47, 82.4), ("Boston", -62, 30), ("Alexandria", -20, 21)):
    r = g[g.nm == nm].iloc[0]
    left = tx < r.lon
    ax.annotate(f"{nm} {int(r.n)}", (r.lon, r.lat), (tx, ty), fontsize=12, color=FG, ha="right" if left else "left", va="center", path_effects=HALO,
                arrowprops=dict(arrowstyle="-", color=FG, lw=.8, shrinkB=1), zorder=6)
ax.text(-125, -45, "Circle area: lunar features named after people born there", fontsize=11, color=MUT, path_effects=HALO)

# the two faces
for k, (lon0, t, key) in enumerate(((0, "Near side", "near"), (180, "Far side", "far"))):
    a = fig.add_axes([.03 + k * .23, .07, .21, .29]); a.set_xlim(-1.1, 1.1); a.set_ylim(-1.1, 1.1); a.set_aspect("equal"); a.axis("off")
    a.add_patch(Circle((0, 0), 1, fc="#EAE4D3", ec=FG, lw=1.4))
    m = H[H.lon.notna()]; dl = ((m.lon - lon0 + 540) % 360) - 180; v = m[dl.abs() <= 90]; dl = dl[dl.abs() <= 90]
    x = np.cos(np.radians(v.lat)) * np.sin(np.radians(dl)); y = np.sin(np.radians(v.lat)); sov = v.iso3.isin(USSR).values
    a.scatter(x[~sov], y[~sov], s=9, c=[CC.get(c, "#BBB3A6") for c in v.continent[~sov]], edgecolor=FG, linewidth=.2)
    a.scatter(x[sov], y[sov], s=26, c=[CC.get(c, "#BBB3A6") for c in v.continent[sov]], edgecolor=FG, linewidth=1.4)
    fig.text(.03 + k * .23 + .105, .375, f"{t}\n{R['far'][key]['ussr_pct']:.1f}% born in the former USSR", ha="center", va="bottom", fontsize=12.5, color=FG, fontweight="medium", linespacing=1.4)

# numbers panel
x0 = .72
def stat(y, big, small, col="#A3261B"):
    fig.text(x0, y, big, fontproperties=DISP, fontsize=40, color=col, va="top")
    fig.text(x0, y - .065, small, fontsize=13, color=FG, va="top", linespacing=1.4)
stat(.85, f"{R['body']['moon']['europe_pct']:.0f}%", "of the Moon's people were\nborn in Europe; Mercury's: " + f"{R['body']['mercury']['europe_pct']:.0f}%")
stat(.68, f"{R['moon']['paris_n']} vs {R['moon']['south_n']}", "lunar features for people born\nin Paris, and in Africa, South\nAmerica and Oceania together")
stat(.48, f"{R['far']['ussr_ratio']:.1f}x", "as many far-side as near-side\nnamesakes born in the former\nSoviet Union (photographed\nfirst by Luna 3, 1959)")
stat(.255, f"{R['women']['moon']['pct']:.1f}%", "of lunar namesakes are\nwomen (Mars " + f"{R['women']['mars']['pct']:.1f}%, Mercury\n{R['women']['mercury']['pct']:.1f}%)")

# legend
fig.text(.50, .345, "Colour: birthplace", fontsize=13, color=FG, fontweight="medium")
for i, c in enumerate(CONT_ORDER):
    yy = .305 - i * .033
    fig.patches.append(Circle((.508, yy + .006), .0065, transform=fig.transFigure, fc=CC[c], ec=FG, lw=.5))
    fig.text(.52, yy, c, fontsize=12.5, color=FG)
yy = .305 - 6 * .033
fig.patches.append(Circle((.508, yy + .006), .0065, transform=fig.transFigure, fc="#BBB3A6", ec=FG, lw=.5))
fig.text(.52, yy, "Birthplace not known", fontsize=12.5, color=FG)
yy = .305 - 7.3 * .033
fig.patches.append(Circle((.508, yy + .006), .0065, transform=fig.transFigure, fc="white", ec=FG, lw=1.8))
fig.text(.52, yy, "Heavy ring: born in the\nformer Soviet Union", fontsize=12.5, color=FG, va="center")
fig.text(.03, .022, "Source: Wikidata (CC0) via QLever; Natural Earth. Modern countries and continents.   Dr Tristan Hotham · maps.tristanhotham.com/moon-names",
         fontsize=11, color=MUT)
out = os.path.join(ROOT, "reddit", "moon_names_collage.png")
fig.savefig(out, dpi=160, facecolor=BG); plt.close(fig)
from PIL import Image
print(out, Image.open(out).size)
