#!/usr/bin/env python3
"""Draw the WP-C-05 risk-reduction figure.

  fig-c05-5-1-allocation.svg   Figure 5-1  one row per rated row of WP-C-03 §5: PLr, the measures per ISO 12100 step, the residual class

The source of record is ../WP-C-05-risk-reduction-concept.md §5 (the allocation table). The check also reads
../WP-C-03-risk-assessment.md: the §5 rated rows (label, PLr adopted) and the §6 measure register (ID, hazards it
reduces). `--check` fails when the SVG is stale, when the §5 rows here are not exactly the rated rows of WP-C-03 §5
in the same order, when a row's PLr disagrees, when a measure ID is not in the WP-C-03 §6 register, when a
hazard-measure pair here is missing from the register (or a register pair is missing here), when a row rated c
or higher has no step 1 or step 2 measure, or when a residual class is not S, D, I, E or O.

    python3 fig_c05.py            # regenerate
    python3 fig_c05.py --check    # fail if the source changed or the SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "WP-C-05-risk-reduction-concept.md"
WP_C03 = HERE.parent / "WP-C-03-risk-assessment.md"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "stroke": "#D3DDE2", "line": "#7E949B", "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#B86F0C", "amber_bg": "#FFF6E8", "teal": "#00938B", "teal_bg": "#E9F7F5", "red": "#D64535", "red_bg": "#FDEDEB",
  "green": "#2C9A58", "green_bg": "#E8F6EC", "grey_bg": "#EDF2F4", "white": "#FFFFFF",
}
PL_FILL = {"a": "#EAF6F5", "b": "#C9ECE8", "c": "#8FD3CC", "d": "#2FA69C", "e": "#D64535"}
PL_INK = {"a": C["ink"], "b": C["ink"], "c": C["ink"], "d": C["white"], "e": C["white"]}
PL_RANK = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}

MEASURE_RE = r"(?:DM|OL|SF|IFU)-\d\d"
CONDITION_RE = r"(?:AOU|CA|HR)-\d\d"
KINDS = {"DM": ("design or complementary measure", C["muted"], C["grey_bg"]), "OL": ("operating-environment limit", C["amber"], C["amber_bg"]),
         "SF": ("safety function", C["teal"], C["teal_bg"]), "IFU": ("information for use", C["green"], C["green_bg"])}
CLASSES = {"S": ("safeguarded at the PLr", C["teal"]), "D": ("reduced by design", C["green"]), "I": ("carried by information for use", C["amber"]),
           "E": ("excluded from the environment", C["dim"]), "O": ("open: no adequate measure yet", C["red"])}
STEPS = ["Step 1 design", "Step 2 safeguarding", "Step 3 information"]


def _table(text: str, heading: str) -> list[list[str]]:
  i = text.index(heading)
  rows = []
  for line in text[i:].splitlines()[1:]:
    if line.startswith("|"):
      rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    elif rows:
      break
  return rows[2:]


def _clean(cell: str) -> str:
  return re.sub(r"\*\*|~~|`", "", cell).strip()


def _plr(cell: str) -> str:
  m = re.search(r"\*\*([a-e]|excluded)\*\*", cell)
  if m:
    return m.group(1)
  c = _clean(cell)
  if c.startswith("n/a"):
    return "n/a"
  return c.split()[0] if c else ""


def _classes(cell: str) -> list[str]:
  m = re.match(r"\*\*([A-Z])(?:, then ([A-Z]))?\.\*\*", cell.strip())
  if not m:
    return []
  return [m.group(1)] + ([m.group(2)] if m.group(2) else [])


def load_source() -> dict:
  text = SOURCE.read_text(encoding="utf-8")
  rows = []
  for r in _table(text, "## 5. Allocation table"):
    if len(r) < 7:
      rows.append({"label": r[0], "ncells": len(r)})
      continue
    steps = [{"measures": re.findall(MEASURE_RE, r[k]), "conditions": re.findall(CONDITION_RE, r[k])} for k in (2, 3, 4)]
    m = re.match(r"(H-\d\d)", r[0])
    rows.append({"label": r[0], "hazard": m.group(1) if m else "", "plr": _plr(r[1]), "steps": steps, "classes": _classes(r[5]),
                 "residual": _clean(r[5]), "verification": _clean(r[6]), "ncells": len(r), "cfg2": "CFG-002" in r[0]})
  c03 = WP_C03.read_text(encoding="utf-8")
  rated = [{"label": r[0], "plr": _plr(r[7])} for r in _table(c03, "## 5. Risk estimation") if r[0].startswith("H-")]
  register = {}
  for r in _table(c03, "## 6. Risk evaluation and reduction"):
    m = re.match(MEASURE_RE, r[0])
    if m:
      register[m.group(0)] = {"name": _clean(r[0])[len(m.group(0)):].strip(), "reduces": re.findall(r"H-\d\d", r[2]), "kind": m.group(0).split("-")[0]}
  hazards = [r[0] for r in _table(c03, "## 4. Hazard identification") if re.match(r"H-\d\d$", r[0])]
  return {"rows": rows, "rated": rated, "register": register, "hazards": hazards}


def _w(s: str, size: float) -> float:
  return len(s) * size * 0.56


def _ell(s: str, width: float, size: float) -> str:
  if _w(s, size) <= width:
    return s
  while s and _w(s + "…", size) > width:
    s = s[:-1]
  return s.rstrip(" ,;:(") + "…"


def text(x, y, s, size=12, fill=C["ink"], weight=400, anchor="start", family=FONT, extra=""):
  return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
          f'fill="{fill}" text-anchor="{anchor}"{extra}>{escape(s)}</text>')


def rect(x, y, w, h, fill, stroke=C["stroke"], r=6, sw=1, dash="", extra=""):
  d = f' stroke-dasharray="{dash}"' if dash else ""
  return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>'


def svg(w, h, uid, title, desc, body):
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
          f'<title id="{uid}-t">{escape(title)}</title>\n<desc id="{uid}-d">{escape(desc)}</desc>\n'
          f'<rect x="0" y="0" width="{w}" height="{h}" fill="{C["bg"]}"/>\n' + "\n".join(body) + "\n</svg>\n")


def _pl_badge(x, y, plr, size=22):
  if plr in PL_FILL:
    return [rect(x, y, size, size, PL_FILL[plr], stroke=PL_FILL[plr], r=5), text(x + size / 2, y + size * 0.7, plr, 11, PL_INK[plr], 700, "middle")]
  label = "e" if plr == "excluded" else "—"
  if plr == "excluded":
    return [rect(x, y, size, size, C["white"], stroke=C["red"], r=5, sw=1.4, dash="3,2"), text(x + size / 2, y + size * 0.7, "e", 11, C["red"], 700, "middle")]
  return [rect(x, y, size, size, C["grey_bg"], r=5), text(x + size / 2, y + size * 0.7, label, 11, C["dim"], 600, "middle")]


def _chip(x, y, mid, w=42, h=20):
  kind = mid.split("-")[0]
  if kind in KINDS:
    _, hue, tint = KINDS[kind]
    return [rect(x, y, w, h, tint, stroke=hue, r=4, sw=1.2), text(x + w / 2, y + h * 0.68, mid, 8.5, hue, 600, "middle", MONO)]
  return [rect(x, y, w, h, C["white"], stroke=C["dim"], r=4, sw=1, dash="2,2"), text(x + w / 2, y + h * 0.68, mid, 8.5, C["muted"], 500, "middle", MONO)]


def _class_marker(x, y, cls, r=9):
  name, hue = CLASSES[cls]
  return [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{hue}"/>', text(x, y + 3.8, cls, 10, C["white"], 700, "middle")]


def fig_allocation(src: dict) -> str:
  rows = src["rows"]
  W = 1200
  labelx, labelw = 24, 286
  badgex = labelx + labelw + 6
  colx = [badgex + 36, 0, 0]
  colw = [270, 270, 135]
  colx[1] = colx[0] + colw[0] + 10
  colx[2] = colx[1] + colw[1] + 10
  resx = colx[2] + colw[2] + 14
  rowh = 32
  top = 92
  n = len(rows)
  legend_y = top + n * rowh + 16
  H = legend_y + 64
  uid = "c05-5-1"
  n_open = sum(1 for r in rows if r["classes"][:1] == ["O"])
  body = [text(24, 28, f"Figure 5-1  Risk reduction allocated to the three steps of ISO 12100 §6: {n} rated rows, {len(src['hazards'])} hazards", 15, C["ink"], 700),
          text(24, 46, f"Left to right is the order of the method; the marker on the right is the residual-risk class of WP-C-05 §1.1. {n_open} rows are open (CFG-002 or no design yet), one is excluded", 11, C["muted"])]
  for k, s in enumerate(STEPS):
    body.append(text(colx[k], top - 12, s, 10.5, C["muted"], 700))
  body.append(text(badgex, top - 12, "PLr", 10.5, C["muted"], 700))
  body.append(text(resx, top - 12, "Residual", 10.5, C["muted"], 700))
  prev_h = None
  group = 0
  for i, r in enumerate(rows):
    y = top + i * rowh
    if r["hazard"] != prev_h:
      group += 1
      prev_h = r["hazard"]
      if i:
        body.append(f'<line x1="16" y1="{y - 1:.1f}" x2="{W - 16}" y2="{y - 1:.1f}" stroke="{C["stroke"]}" stroke-width="1"/>')
    if group % 2 == 0:
      body.append(rect(16, y, W - 32, rowh, C["panel"], stroke="none", r=0))
    situation = r["label"][len(r["hazard"]):].lstrip(" ·")
    body.append(text(labelx, y + rowh * 0.64, r["hazard"], 11, C["ink"], 700, family=MONO))
    body.append(text(labelx + 44, y + rowh * 0.64, _ell(situation, labelw - 44, 10), 10, C["muted"]))
    body += _pl_badge(badgex, y + 5, r["plr"])
    for k, step in enumerate(r["steps"]):
      ids = step["measures"] + step["conditions"]
      x = colx[k]
      if not ids:
        body.append(text(x + 6, y + rowh * 0.64, "—", 11, C["dim"]))
      for mid in ids:
        if x + 42 > colx[k] + colw[k]:
          body.append(text(x + 2, y + rowh * 0.64, "…", 11, C["dim"]))
          break
        body += _chip(x, y + 6, mid)
        x += 45
    x = resx + 10
    for cls in r["classes"]:
      body += _class_marker(x, y + rowh / 2, cls)
      x += 24
    if r["cfg2"]:
      body.append(text(resx + 62, y + rowh * 0.64, "CFG-002", 9, C["amber"], 600))
  # legend
  x = 24
  body.append(text(x, legend_y + 12, "Chips", 10.5, C["muted"], 700))
  x += 44
  for kind, (name, hue, tint) in KINDS.items():
    body.append(rect(x, legend_y + 1, 30, 15, tint, stroke=hue, r=4, sw=1.2))
    body.append(text(x + 15, legend_y + 12, kind, 8.5, hue, 600, "middle", MONO))
    body.append(text(x + 36, legend_y + 12.5, name, 10.5, C["ink"]))
    x += 36 + _w(name, 10.5) + 16
  body.append(rect(x, legend_y + 1, 30, 15, C["white"], stroke=C["dim"], r=4, sw=1, dash="2,2"))
  body.append(text(x + 15, legend_y + 12, "AOU", 8.5, C["muted"], 500, "middle", MONO))
  body.append(text(x + 36, legend_y + 12.5, "condition (assumption of use, collaborative rule, derived requirement), not a measure", 10.5, C["ink"]))
  y2 = legend_y + 30
  x = 24
  body.append(text(x, y2 + 12, "Residual", 10.5, C["muted"], 700))
  x += 60
  for cls, (name, hue) in CLASSES.items():
    body += _class_marker(x + 9, y2 + 8, cls)
    body.append(text(x + 24, y2 + 12.5, name, 10.5, C["ink"]))
    x += 24 + _w(name, 10.5) + 18
  return svg(W, H, uid, "Risk reduction allocation of WP-C-05",
             "One row per rated row of the risk assessment, grouped by hazard: the adopted Performance Level, then the measures of each of the three "
             "steps of ISO 12100 as chips coloured by kind, and the residual-risk class as a marker on the right.", body)


OUTPUTS = {"fig-c05-5-1-allocation.svg": fig_allocation}


def check_source(src: dict) -> list[str]:
  errs = []
  rows, rated, reg = src["rows"], src["rated"], src["register"]
  labels = [r["label"] for r in rows]
  want = [r["label"] for r in rated]
  if labels != want:
    missing = [l for l in want if l not in labels]
    extra = [l for l in labels if l not in want]
    errs.append(f"§5 rows are not the rated rows of WP-C-03 §5 in order; missing {missing}, extra {extra}" if missing or extra
                else "§5 rows are the rated rows of WP-C-03 §5 but in a different order")
  plr_c03 = {r["label"]: r["plr"] for r in rated}
  seen_pairs = set()
  for r in rows:
    if r["ncells"] != 7:
      errs.append(f"{r['label'][:40]}: {r['ncells']} cells, expected 7")
      continue
    if r["label"] in plr_c03 and plr_c03[r["label"]] != r["plr"]:
      errs.append(f"{r['label'][:40]}: PLr {r['plr']!r}, WP-C-03 §5 adopts {plr_c03[r['label']]!r}")
    if not r["classes"] or any(c not in CLASSES for c in r["classes"]):
      errs.append(f"{r['label'][:40]}: residual class {r['classes']} is not one of {''.join(CLASSES)} (bold 'X.' or 'X, then Y.' at the start)")
    if r["plr"] == "excluded" and r["classes"][:1] != ["E"]:
      errs.append(f"{r['label'][:40]}: excluded row must be class E")
    if r["classes"][:1] == ["E"] and r["plr"] != "excluded":
      errs.append(f"{r['label'][:40]}: class E on a row that WP-C-03 §5 does not exclude")
    for k, step in enumerate(r["steps"]):
      for mid in step["measures"]:
        if mid not in reg:
          errs.append(f"{r['label'][:40]}: {mid} is not in the WP-C-03 §6 register")
        elif r["hazard"] not in reg[mid]["reduces"]:
          errs.append(f"{r['label'][:40]}: {mid} does not list {r['hazard']} under 'Reduces' in WP-C-03 §6")
        else:
          seen_pairs.add((mid, r["hazard"]))
        if k == 2 and mid.split("-")[0] != "IFU":
          errs.append(f"{r['label'][:40]}: {mid} in step 3 is not information for use")
        if k < 2 and mid.split("-")[0] == "IFU":
          errs.append(f"{r['label'][:40]}: {mid} in step {k + 1} is information for use")
    if r["plr"] in PL_RANK and PL_RANK[r["plr"]] >= PL_RANK["c"]:
      if not (r["steps"][0]["measures"] or r["steps"][1]["measures"]):
        errs.append(f"{r['label'][:40]}: rated {r['plr']} with no step 1 or step 2 measure (information for use alone)")
  for mid, m in reg.items():
    for h in m["reduces"]:
      if (mid, h) not in seen_pairs:
        errs.append(f"WP-C-03 §6 says {mid} reduces {h}, but no §5 row of {h} allocates it")
  return errs


def main(argv: list[str]) -> int:
  check = "--check" in argv
  src = load_source()
  errs = check_source(src)
  if errs:
    for e in errs:
      print(f"ERROR {e}")
    return 1
  stale = []
  for name, fn in OUTPUTS.items():
    out = fn(src)
    p = HERE / name
    if check:
      if not p.exists() or p.read_text(encoding="utf-8") != out:
        stale.append(name)
    else:
      p.write_text(out, encoding="utf-8")
      print(f"wrote {p.relative_to(HERE.parent.parent.parent)}")
  if stale:
    for s in stale:
      print(f"STALE {s}: run python3 {Path(__file__).name}")
    return 1
  if check:
    print(f"fig_c05: {len(OUTPUTS)} figure current; {len(src['rows'])} rows, {len(src['register'])} measures checked against WP-C-03")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
