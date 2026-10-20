#!/usr/bin/env python3
"""Draw the WP-C-03 risk-assessment figures.

  fig-c03-3-1-situations-zones.svg   Figure 3-1  situations OS-nn by zone, coloured by the people class of the zone
  fig-c03-5-1-risk-graph.svg         Figure 5-1  the ISO 13849-1 risk graph with every rated row placed at its leaf
  fig-c03-6-1-hazard-measures.svg    Figure 6-1  hazard-to-measure matrix in the ISO 12100 order

The source of record is ../WP-C-03-risk-assessment.md: situations from the §3 table; the eight graph paths from
the §2.2 table; the rated rows (S, F, P, graph value, PLr adopted) from the §5 table; measures and what they
reduce from the §6 table. `--check` fails when an SVG is stale, when a §5 row's S, F and P do not reach the graph
value written in the row, or when a measure reduces a hazard that §4 does not list.

    python3 fig_c03.py            # regenerate
    python3 fig_c03.py --check    # fail if the source changed or an SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "WP-C-03-risk-assessment.md"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "stroke": "#D3DDE2", "line": "#7E949B", "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#B86F0C", "amber_bg": "#FFF6E8", "teal": "#00938B", "teal_bg": "#E9F7F5", "red": "#D64535", "red_bg": "#FDEDEB",
  "green": "#2C9A58", "green_bg": "#E8F6EC", "grey_bg": "#EDF2F4", "white": "#FFFFFF",
}
# one-hue ramp for the Performance Levels a…e (light to dark); e is the level no bench-build function is designed for
PL_FILL = {"a": "#EAF6F5", "b": "#C9ECE8", "c": "#8FD3CC", "d": "#2FA69C", "e": "#D64535"}
PL_INK = {"a": C["ink"], "b": C["ink"], "c": C["ink"], "d": C["white"], "e": C["white"]}

ZONE_ORDER = ["Z1", "Z2", "Z3", "Z4", "Z5", "bench"]
ZONE_NAMES = {"Z1": "test area", "Z2": "transport aisle", "Z3": "dock lane", "Z4": "charging bay", "Z5": "public floor (excluded)", "bench": "bench"}
MEASURE_GROUPS = [("DM", "Inherently safe design and complementary"), ("OL", "Operating-environment limits"), ("SF", "Safety functions"), ("IFU", "Information for use")]


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


def load_source() -> dict:
  text = SOURCE.read_text(encoding="utf-8")
  graph = {(r[0], r[1], r[2]): r[3] for r in _table(text, "### 2.2 Risk graph")}
  situations = {r[0]: {"text": r[1], "zone": r[2], "task": r[3], "people": r[4], "modes": r[5], "scenarios": r[6], "misuse": r[7]}
                for r in _table(text, "## 3. Situations")}
  hazards = {r[0]: {"title": r[1]} for r in _table(text, "## 4. Hazard identification")}
  rated = []
  for r in _table(text, "## 5. Risk estimation"):
    label = _clean(r[0])
    m = re.match(r"(H-\d\d)\s*·\s*(.*)", label)
    rated.append({"label": label, "hazard": m.group(1) if m else label[:4], "short": m.group(2) if m else label,
                  "zone": r[1], "S": r[2], "F": r[3], "P": r[4], "graph": _clean(r[6]), "adopted": _clean(r[7])})
  measures = []
  for r in _table(text, "## 6. Risk evaluation and reduction"):
    name = _clean(r[0])
    mid = name.split()[0]
    measures.append({"id": mid, "name": name, "type": r[1], "reduces": re.findall(r"H-\d\d", r[2]), "group": re.match(r"[A-Z]+", mid).group(0)})
  return {"graph": graph, "situations": situations, "hazards": hazards, "rated": rated, "measures": measures}


def _w(s: str, size: float) -> float:
  return len(s) * size * 0.56


def text(x, y, s, size=12, fill=C["ink"], weight=400, anchor="start", family=FONT, extra=""):
  return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
          f'fill="{fill}" text-anchor="{anchor}"{extra}>{escape(s)}</text>')


def rect(x, y, w, h, fill, stroke=C["stroke"], r=6, sw=1, dash="", extra=""):
  d = f' stroke-dasharray="{dash}"' if dash else ""
  return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>'


def wrap(s: str, width: float, size: float) -> list[str]:
  out, cur = [], ""
  for word in s.split():
    cand = (cur + " " + word).strip()
    if _w(cand, size) > width and cur:
      out.append(cur)
      cur = word
    else:
      cur = cand
  if cur:
    out.append(cur)
  return out


def svg(w, h, uid, title, desc, body):
  defs = f"""<defs>
  <pattern id="{uid}-hatch" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="8" stroke="{C['dim']}" stroke-width="1"/></pattern>
</defs>"""
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
          f'<title id="{uid}-t">{escape(title)}</title>\n<desc id="{uid}-d">{escape(desc)}</desc>\n{defs}\n'
          f'<rect x="0" y="0" width="{w}" height="{h}" fill="{C["bg"]}"/>\n' + "\n".join(body) + "\n</svg>\n")


# ---------------------------------------------------------------- Figure 3-1 situations by zone


def _people_class(people: str) -> str:
  p = people.lower()
  if "public" in p or "anyone" in p:
    return "public"
  if "none" in p:
    return "none"
  if "parent" in p:
    return "parent"
  return "briefed"


def _zones_of(zone_cell: str) -> list[str]:
  z = zone_cell.lower()
  if "any" in z or "parent" in z:
    return list(ZONE_ORDER)
  out = [zid for zid in ZONE_ORDER if zid != "bench" and zid.lower() in z]
  if "bench" in z:
    out.append("bench")
  return out


def fig_situations(src: dict) -> str:
  sits = src["situations"]
  W = 1180
  rowh, colw, x0, y0 = 50, 118, 300, 112
  sx = x0 + colw * len(ZONE_ORDER) + 16      # scenarios column
  H = y0 + rowh * len(sits) + 78
  fills = {"none": (C["green_bg"], C["green"]), "briefed": (C["teal_bg"], C["teal"]), "public": (C["red_bg"], C["red"]), "parent": (C["grey_bg"], C["stroke"])}
  body = [text(32, 34, "Figure 3-1  Situations by zone, coloured by who is exposed there", 15, C["ink"], 700),
          text(32, 52, "A cell is filled where the situation of §3 occurs in that zone of WP-C-02; the task IDs are written in it. The public floor is hatched: excluded at BL-001.", 11, C["muted"])]
  for j, zid in enumerate(ZONE_ORDER):
    x = x0 + j * colw
    body.append(text(x + colw / 2, y0 - 26, zid, 12, C["ink"], 700, "middle"))
    body.append(text(x + colw / 2, y0 - 11, ZONE_NAMES[zid], 10, C["muted"], anchor="middle"))
  body.append(text(sx, y0 - 11, "WP-C-06 scenarios", 10, C["muted"], 700))
  for i, (sid, s) in enumerate(sits.items()):
    y = y0 + i * rowh
    body.append(text(32, y + 24, sid, 11, C["ink"], 700, family=MONO))
    all_lines = wrap(s["text"], 212, 10)
    lines = all_lines[:3]
    if len(all_lines) > 3:
      lines[2] = lines[2][:-1].rstrip(" ,;") + "…"
    for k, ln in enumerate(lines):
      body.append(text(84, y + 16 + k * 12, ln, 10, C["muted"]))
    cls = _people_class(s["people"])
    zones = _zones_of(s["zone"])
    tasks = ", ".join(re.findall(r"T-\d\d", s["task"])) or ("—" if "parent" not in s["task"] and "any" not in s["task"] else "as parent")
    for j, zid in enumerate(ZONE_ORDER):
      x = x0 + j * colw
      if zid in zones:
        fill, stroke = fills[cls]
        body.append(rect(x + 3, y + 3, colw - 6, rowh - 6, fill, stroke, 4))
        body.append(text(x + colw / 2, y + rowh / 2 + 4, tasks, 10, C["ink"] if cls != "parent" else C["dim"], 600 if cls != "parent" else 400, "middle"))
      else:
        body.append(rect(x + 3, y + 3, colw - 6, rowh - 6, C["white"], C["stroke"], 4))
      if zid == "Z5":
        body.append(rect(x + 3, y + 3, colw - 6, rowh - 6, f"url(#sit-hatch)", "none", 4, 0, extra=' fill-opacity="0.45"'))
    sc = s["scenarios"] if s["scenarios"] != "—" else ""
    body.append(text(sx, y + rowh / 2 + 4, sc, 10, C["ink"] if sc else C["dim"]))
  ly = y0 + rowh * len(sits) + 22
  for k, (cls, label) in enumerate([("none", "none: the zone is empty of people while the robot moves"), ("briefed", "briefed staff or a technician"), ("public", "public, or anyone"), ("parent", "as the parent situation")]):
    fill, stroke = fills[cls]
    dx = [0, 360, 580, 760][k]
    body.append(rect(32 + dx, ly, 18, 14, fill, stroke, 2))
    body.append(text(58 + dx, ly + 11, label, 10.5, C["muted"]))
  body.append(text(W - 32, H - 12, "Generated by figures/fig_c03.py from WP-C-03 §3", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "sit", "Figure 3-1: situations by zone",
             "A grid with the eighteen situations down the side and the zones across: cells filled green where nobody is exposed, teal where briefed staff are, red where the public is, grey where the situation inherits its parent; the public-floor column is hatched as excluded; the WP-C-06 scenarios of each situation are listed at the right.", body)


# ---------------------------------------------------------------- Figure 5-1 risk graph


def _short(row: dict, width: float = 200.0, size: float = 10.0) -> str:
  s = re.sub(r"\s*\(.*?\)", "", row["short"]).strip()
  label = f"{row['hazard']} {s}"
  if _w(label, size) <= width:
    return label
  while label and _w(label + "…", size) > width:
    label = label[:-1]
  return label.rstrip(" ,;") + "…"


def fig_risk_graph(src: dict) -> str:
  graph = src["graph"]
  rated = src["rated"]
  paths = [("S1", "F1", "P1"), ("S1", "F1", "P2"), ("S1", "F2", "P1"), ("S1", "F2", "P2"), ("S2", "F1", "P1"), ("S2", "F1", "P2"), ("S2", "F2", "P1"), ("S2", "F2", "P2")]
  W = 1180
  xs = {"start": 64, "S": 214, "F": 364, "P": 514, "PL": 628}
  leaf_h, gap = 106, 10
  y0 = 96
  H = y0 + 8 * (leaf_h + gap) + 90
  nodes = {}   # (level, key) -> (x, y)
  body_lines, body_nodes = [], []
  for i, (s, f, p) in enumerate(paths):
    nodes[("P", (s, f, p))] = (xs["P"], y0 + i * (leaf_h + gap) + leaf_h / 2)
  for s in ("S1", "S2"):
    for f in ("F1", "F2"):
      ys = [nodes[("P", (s, f, p))][1] for p in ("P1", "P2")]
      nodes[("F", (s, f))] = (xs["F"], sum(ys) / 2)
    ys = [nodes[("F", (s, f))][1] for f in ("F1", "F2")]
    nodes[("S", s)] = (xs["S"], sum(ys) / 2)
  nodes[("start", "start")] = (xs["start"], sum(nodes[("S", s)][1] for s in ("S1", "S2")) / 2)

  def elbow(x1, y1, x2, y2, color=C["line"], sw=1.4):
    xm = (x1 + x2) / 2
    return f'<path d="M{x1:.1f},{y1:.1f} L{xm:.1f},{y1:.1f} L{xm:.1f},{y2:.1f} L{x2:.1f},{y2:.1f}" fill="none" stroke="{color}" stroke-width="{sw}"/>'

  # which paths are used (drawn darker)
  used = {(r["S"], r["F"], r["P"]) for r in rated}
  sx, sy = nodes[("start", "start")]
  for s in ("S1", "S2"):
    x, y = nodes[("S", s)]
    hot = any(k[0] == s for k in used)
    body_lines.append(elbow(sx + 44, sy, x - 44, y, C["ink"] if hot else C["stroke"], 1.8 if hot else 1.2))
    for f in ("F1", "F2"):
      fx, fy = nodes[("F", (s, f))]
      hot = any(k[:2] == (s, f) for k in used)
      body_lines.append(elbow(x + 44, y, fx - 44, fy, C["ink"] if hot else C["stroke"], 1.8 if hot else 1.2))
      for p in ("P1", "P2"):
        px, py = nodes[("P", (s, f, p))]
        hot = (s, f, p) in used
        body_lines.append(elbow(fx + 44, fy, px - 38, py, C["ink"] if hot else C["stroke"], 1.8 if hot else 1.2))

  def node(x, y, label, sub):
    out = [rect(x - 44, y - 20, 88, 40, C["white"], C["ink"], 6, 1.2)]
    out.append(text(x, y - 2, label, 12, C["ink"], 700, "middle"))
    out.append(text(x, y + 13, sub, 9, C["muted"], 400, "middle"))
    return out

  body_nodes += [rect(sx - 44, sy - 20, 88, 40, C["ink"], C["ink"], 6), text(sx, sy + 4, "start", 12, C["white"], 700, "middle")]
  subs = {"S1": "slight, reversible", "S2": "serious, irreversible", "F1": "seldom, short", "F2": "frequent, long", "P1": "avoidable", "P2": "hard to avoid"}
  for s in ("S1", "S2"):
    x, y = nodes[("S", s)]
    body_nodes += node(x, y, s, subs[s])
    for f in ("F1", "F2"):
      fx, fy = nodes[("F", (s, f))]
      body_nodes += node(fx, fy, f, subs[f])
  for s, f, p in paths:
    px, py = nodes[("P", (s, f, p))]
    body_nodes.append(rect(px - 38, py - 20, 76, 40, C["white"], C["ink"], 6, 1.2))
    body_nodes.append(text(px, py - 2, p, 12, C["ink"], 700, "middle"))
    body_nodes.append(text(px, py + 13, subs[p], 8.5, C["muted"], 400, "middle"))
    pl = graph[(s, f, p)]
    lx, ly = xs["PL"], py - leaf_h / 2
    body_lines.append(f'<line x1="{px + 38}" y1="{py:.1f}" x2="{lx}" y2="{py:.1f}" stroke="{C["ink"] if (s, f, p) in used else C["stroke"]}" stroke-width="1.6"/>')
    body_nodes.append(rect(lx, ly, 54, leaf_h, PL_FILL[pl], PL_FILL[pl] if pl != "a" else C["stroke"], 6))
    body_nodes.append(text(lx + 27, py + 7, pl, 22, PL_INK[pl], 700, "middle"))
    rows = [r for r in rated if (r["S"], r["F"], r["P"]) == (s, f, p)]
    body_nodes.append(rect(lx + 62, ly, W - 32 - (lx + 62), leaf_h, C["panel"], C["stroke"], 6))
    if not rows:
      body_nodes.append(text(lx + 74, py + 4, "no row of §5 on this path", 10, C["dim"]))
    colw_ = (W - 32 - (lx + 74)) / 2
    for k, r in enumerate(rows):
      col = k // 5
      yy = ly + 18 + (k % 5) * 18
      xx = lx + 74 + col * colw_
      adopted = r["adopted"].lower()
      tag = " · excluded" if "excluded" in adopted else (" · n/a" if adopted.startswith("n/a") else "")
      label = _short(r, colw_ - 12 - _w(tag, 10))
      body_nodes.append(text(xx, yy, label + tag, 10, C["ink"], 600 if not tag else 400))
  body = [text(32, 34, "Figure 5-1  The ISO 13849-1 risk graph with the rated rows of §5 at their leaves", 15, C["ink"], 700),
          text(32, 52, "Paths that at least one row takes are drawn in ink; the leaf gives the required Performance Level of §2.2. The e leaf is the one no bench-build function is designed for: its row is excluded by zone.", 11, C["muted"])]
  body += body_lines + body_nodes
  body.append(text(xs["S"], y0 - 16, "severity", 10.5, C["muted"], 700, "middle"))
  body.append(text(xs["F"], y0 - 16, "frequency / exposure", 10.5, C["muted"], 700, "middle"))
  body.append(text(xs["P"], y0 - 16, "avoidance", 10.5, C["muted"], 700, "middle"))
  body.append(text(xs["PL"] + 27, y0 - 16, "PLr", 10.5, C["muted"], 700, "middle"))
  body.append(text(xs["PL"] + 74, y0 - 16, "rows of §5 that take this path", 10.5, C["muted"], 700))
  body.append(text(32, H - 36, "Clause references to be checked against a licensed copy of ISO 13849-1; the mapping drawn is the §2.2 table and CI fails if a §5 row disagrees with it.", 10, C["muted"]))
  body.append(text(W - 32, H - 16, "Generated by figures/fig_c03.py from WP-C-03 §2.2 and §5", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "rg", "Figure 5-1: the risk graph with the rated rows at their leaves",
             "A tree from a start box through severity S1 or S2, frequency F1 or F2 and avoidance P1 or P2 to eight leaves labelled a to e in a teal ramp with e in red; beside each leaf the hazard rows that reach it, the e leaf holding the public-floor row marked excluded and the two d leaves holding the stop-function rows.", body)


# ---------------------------------------------------------------- Figure 6-1 hazard-to-measure matrix


def _adopted_pl(rated: list[dict], hid: str) -> str:
  best = ""
  for r in rated:
    if r["hazard"] != hid:
      continue
    a = r["adopted"].lower()
    if "excluded" in a or a.startswith("n/a"):
      continue
    m = re.match(r"([a-e])\b", a)
    if m and m.group(1) > best:
      best = m.group(1)
  return best or "—"


def fig_measures(src: dict) -> str:
  hazards = list(src["hazards"])
  measures = src["measures"]
  groups = [(g, [m for m in measures if m["group"] == g]) for g, _ in MEASURE_GROUPS]
  x0, y0, rowh, colw, ggap = 250, 156, 34, 33, 12
  W = x0 + sum(colw * len(ms) + ggap for _, ms in groups) + 40
  H = y0 + rowh * len(hazards) + 92
  body = [text(32, 34, "Figure 6-1  Which measure reduces which hazard, in the ISO 12100 order", 15, C["ink"], 700),
          text(32, 52, "A dot where the §6 table says the measure reduces the hazard. Left to right: inherently safe design and complementary measures, operating-environment limits, safety functions, information for use.", 11, C["muted"])]
  xcol = {}
  x = x0
  gfill = {"DM": C["grey_bg"], "OL": C["amber_bg"], "SF": C["teal_bg"], "IFU": C["grey_bg"]}
  gstroke = {"DM": C["stroke"], "OL": C["amber"], "SF": C["teal"], "IFU": C["stroke"]}
  for g, ms in groups:
    gw = colw * len(ms)
    body.append(rect(x, y0 - 70, gw, 24, gfill[g], gstroke[g], 4))
    title = dict(MEASURE_GROUPS)[g]
    body.append(text(x + gw / 2, y0 - 54, title if _w(title, 9.5) < gw - 6 else g, 9.5, C["ink"], 700, "middle"))
    for m in ms:
      xcol[m["id"]] = x + colw / 2
      ax = x + colw / 2 - 6
      body.append(text(ax, y0 - 10, m["id"], 9.5, C["ink"], 600, "start", family=MONO, extra=f' transform="rotate(-60 {ax:.1f} {y0 - 10})"'))
      x += colw
    x += ggap
  for i, hid in enumerate(hazards):
    y = y0 + i * rowh
    if i % 2 == 0:
      body.append(rect(28, y, W - 56, rowh, C["panel"], "none", 0, 0))
    body.append(text(32, y + 21, hid, 11, C["ink"], 700, family=MONO))
    title = src["hazards"][hid]["title"].split(":", 1)[-1].strip()
    first = wrap(title, 132, 10)
    body.append(text(80, y + 21, first[0] + ("…" if len(first) > 1 else ""), 10, C["muted"]))
    pl = _adopted_pl(src["rated"], hid)
    if pl != "—":
      body.append(rect(x0 - 40, y + 8, 22, 18, PL_FILL[pl], PL_FILL[pl] if pl != "a" else C["stroke"], 4))
      body.append(text(x0 - 29, y + 21, pl, 10.5, PL_INK[pl], 700, "middle"))
    else:
      body.append(text(x0 - 29, y + 21, "—", 10.5, C["dim"], 400, "middle"))
    for m in measures:
      if hid in m["reduces"]:
        cx = xcol[m["id"]]
        body.append(f'<circle cx="{cx:.1f}" cy="{y + rowh / 2:.1f}" r="6" fill="{gstroke[m["group"]] if m["group"] in ("OL", "SF") else C["ink"]}"/>')
  body.append(text(x0 - 29, y0 - 8, "PLr", 9.5, C["muted"], 700, "middle"))
  ly = y0 + rowh * len(hazards) + 22
  body.append(text(32, ly + 11, "PLr: the highest adopted in §5 for the hazard (rows that are excluded or not a control function do not count).", 10.5, C["muted"]))
  body.append(text(32, ly + 28, "The legend of the measure IDs is the §6 table; the hazards rated d each have at least one safety-function dot.", 10.5, C["muted"]))
  body.append(text(W - 32, H - 12, "Generated by figures/fig_c03.py from WP-C-03 §4, §5 and §6", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "hm", "Figure 6-1: hazard-to-measure matrix",
             "A grid with the fifteen hazards down the side, each with its adopted Performance Level in a coloured chip, and the measures across in four groups: design and complementary measures, operating-environment limits, safety functions and information for use; a dot marks each pair where the measure reduces the hazard.", body)


OUTPUTS = {"fig-c03-3-1-situations-zones.svg": fig_situations, "fig-c03-5-1-risk-graph.svg": fig_risk_graph, "fig-c03-6-1-hazard-measures.svg": fig_measures}


def check_source(src: dict) -> list[str]:
  errs = []
  if len(src["graph"]) != 8:
    errs.append(f"WP-C-03 §2.2 has {len(src['graph'])} graph paths, expected 8")
  for r in src["rated"]:
    key = (r["S"], r["F"], r["P"])
    if key not in src["graph"]:
      errs.append(f"{r['label']}: S/F/P {key} is not a path of §2.2")
    elif src["graph"][key] != r["graph"]:
      errs.append(f"{r['label']}: {key} gives {src['graph'][key]} on the graph, the row says {r['graph']}")
    if r["hazard"] not in src["hazards"]:
      errs.append(f"{r['label']}: hazard {r['hazard']} is not in §4")
  for m in src["measures"]:
    for h in m["reduces"]:
      if h not in src["hazards"]:
        errs.append(f"{m['id']} reduces {h}, which §4 does not list")
    if m["group"] not in dict(MEASURE_GROUPS):
      errs.append(f"{m['id']}: unknown measure group")
  for sid, s in src["situations"].items():
    if not _zones_of(s["zone"]):
      errs.append(f"{sid}: zone cell {s['zone']!r} names no zone of WP-C-02")
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
    print(f"fig_c03: {len(OUTPUTS)} figures current; {len(src['rated'])} rated rows agree with the risk graph")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
