"""Build the paper: fill code/paper_template.tex from data/results.json, add the tables, compile with xelatex.
Output: release/paper/Hotham_Where_the_Borders_Are_Straight.tex and .pdf (figures f_*.png beside them)."""
import subprocess, csv
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Where_the_Borders_Are_Straight"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
tfmt = lambda v, f: tex(fmt(v, f or "raw"))
SEG = list(csv.DictReader(open(f"{DATA}/straight_segments.csv", encoding="utf-8")))

rows = ""
for c in R["continents"]:
    rows += (f"{c['name']} & {c['n_borders']} & {c['km']:,} & {c['straight_pct']:.1f} & {c['water_pct']:.1f} & {c['mountain_pct']:.1f} & "
             f"{c['other_pct']:.1f} & {c['astro_pct']:.1f} & {c['mostly_straight_pct']:.1f}\\\\\n")
w = R["world"]
rows += f"\\midrule World & {w['n_borders']} & {w['km']:,} & {w['straight_pct']:.1f} & {w['water_pct']:.1f} & {w['mountain_pct']:.1f} & {w['other_pct']:.1f} & {R['straight']['astro_pct_of_world']:.1f} & {R['borders']['mostly_straight_pct']:.1f}\\\\\n"
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{Land borders by continent: number of borders, length and share of length by kind (\\%); "
      "parallels and meridians as a share of length; and the share of borders at least half straight.}\\label{tab:cont}\\setlength{\\tabcolsep}{4pt}"
      "\\begin{tabular}{lrrrrrrrr}\\toprule Continent & Borders & km & Straight & Water & Mountain & Other & Par./mer. & Mostly straight\\\\\\midrule\n" + rows +
      "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for t in SEG[:R["top_n"]]:
    rows += (f"{t['rank']} & {tex(t['name'])} & {int(t['km']):,} & {tex(t['year_label'])} & {tex(t['treaty'])} & {tex(t['powers'])} & {t['conf']}\\\\\n")
TT = ("{\\footnotesize\\setlength{\\tabcolsep}{3pt}\\begin{longtable}{r>{\\raggedright\\arraybackslash}p{2.6cm}r>{\\raggedright\\arraybackslash}p{1.5cm}"
      ">{\\raggedright\\arraybackslash}p{5.2cm}>{\\raggedright\\arraybackslash}p{3.1cm}l}"
      f"\\caption{{The {R['top_n']} longest straight segments and the agreements that set them. Confidence: high, a well-known treaty set this line; "
      "medium, the treaty is known but the instrument or date for this stretch is less certain; low, an administrative line or uncertain origin. "
      "Sources are listed for each line in data/straight\\_segments.csv.}\\label{tab:top}\\\\\\toprule "
      "\\# & Border & km & Year & Agreement & Agreed by & Conf.\\\\\\midrule\\endfirsthead\\toprule \\# & Border & km & Year & Agreement & Agreed by & Conf.\\\\\\midrule\\endhead\n"
      + rows + "\\bottomrule\\end{longtable}}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("\\url{{{meta.page}}}", "\\url{%s}" % URL).replace("\\url{{{meta.repo}}}", "\\url{%s}" % REPO)
t = fill(t, R, tfmt)
t = t.replace("{{TABLE_CONT}}", TC).replace("{{TABLE_TOP}}", TT)
assert not re.search(r"\{\{(?!DOI\}\})", t), re.findall(r"\{\{[^}]*\}\}", t)[:5]
check_dashes(t, "paper"); check_words(t, "paper")
assert AI in t.replace("\n", " ")
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or l.startswith("!")][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
