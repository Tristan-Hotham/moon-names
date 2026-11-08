"""Step 5: the paper. Fills code/paper_template.tex from data/results.json, adds tables and compiles with xelatex.
Output: release/paper/Hotham_Moon_Names.pdf and .tex beside the f_*.png figures. The DOI stays as 10.5281/zenodo.24055578."""
import subprocess
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Moon_Names"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "f1": return f"{float(v):.1f}"
    return tex(str(v))


B = R["body"]; bods = ["moon", "mercury", "venus", "mars"]
row = lambda lab, f: f"{lab} & " + " & ".join(f(B[b]) for b in bods) + "\\\\\n"
TB = ("\\begin{table}[tbp]\\centering\\small\\caption{The four bodies. Namings: feature and person pairs; located: with a birthplace with coordinates.}\\label{tab:bodies}"
      "\\begin{tabular}{lrrrr}\\toprule & Moon & Mercury & Venus & Mars\\\\\\midrule\n"
      + row("Named features", lambda x: f"{x['features']:,}") + row("Named after a person (\\%)", lambda x: f"{x['human_pct']:.1f}")
      + row("Namings", lambda x: f"{x['namings']:,}") + row("Located namings", lambda x: f"{x['located']:,}")
      + row("Born in Europe (\\%)", lambda x: f"{x['europe_pct']:.1f}") + row("Modern countries", lambda x: f"{x['n_countries']}")
      + row("Median year of birth", lambda x: f"{x['born_median']}") + row("Top country", lambda x: tex(x['top'][0]['country']).replace("United ", "U. "))
      + "\\bottomrule\\end{tabular}\\end{table}")
fr = R["far"]
r2 = lambda lab, k, f: f"{lab} & {f(fr['near'][k])} & {f(fr['far'][k])}\\\\\n"
TF = ("\\begin{table}[tbp]\\centering\\small\\caption{Near side and far side of the Moon.}\\label{tab:far}\\begin{tabular}{lrr}\\toprule & Near side & Far side\\\\\\midrule\n"
      + r2("Namings", "namings", lambda v: f"{v:,}") + r2("Located", "located", lambda v: f"{v:,}")
      + r2("Born in former USSR (\\%)", "ussr_pct", lambda v: f"{v:.1f}") + r2("Born in Russia", "russia_n", str)
      + r2("Born in Europe (\\%)", "europe_pct", lambda v: f"{v:.1f}") + r2("Born in the United States (\\%)", "us_pct", lambda v: f"{v:.1f}")
      + r2("Median year of birth", "born_median", str) + r2("Astronomers (\\%)", "astro_pct", lambda v: f"{v:.1f}")
      + r2("Other scientists (\\%)", "science_pct", lambda v: f"{v:.1f}") + r2("Astronauts and cosmonauts", "space_n", str)
      + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(t['place'])} & {tex(t['country'])} & {t['n']} & {t['moon']} & {t['mercury']} & {t['venus']} & {t['mars']} & {t['people']}\\\\\n" for t in R["towns"])
TT = ("\\begin{table}[tbp]\\centering\\small\\caption{The fifteen birthplaces with the most namings.}\\label{tab:towns}\\begin{tabular}{llrrrrrr}\\toprule "
      "Birthplace & Country & All & Moon & Mercury & Venus & Mars & People\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")

t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("\\url{{{meta.page}}}", "\\url{%s}" % PAGE).replace("\\url{{{meta.repo}}}", "\\url{%s}" % REPO)
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
for k, v in (("BODIES", TB), ("FAR", TF), ("TOWNS", TT)):
    t = t.replace("{{TABLE_%s}}" % k, v)
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:4]
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:10])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
