#!/usr/bin/env python3
"""Draw the WP-S-04 stopping-budget figure.

  fig-s04-2-1-loop-sf02-scanner.svg       Figure 2-1  SF-02 by the scanner: demand to standstill, the distance ledger of FS-1b
  fig-s04-2-2-loop-sf02-bumper.svg        Figure 2-2  SF-02 by the rear bumper at the crawl limit: contact to standstill against the overtravel
  fig-s04-2-3-loop-sf03.svg               Figure 2-3  SF-03 at the channel 1 ceiling: the field sized for 0.20 m/s against the stop from 0.25
  fig-s04-2-4-loop-sf04-fault.svg         Figure 2-4  SF-04 fault path: channel 1 dead, the hardware watchdog, the drive-on distance
  fig-s04-2-5-loop-sf11.svg               Figure 2-5  SF-11 at the station: the workspace ring as reach plus walk
  fig-s04-2-6-loop-sf12.svg               Figure 2-6  SF-12 at the lift: the keep-clear ring against the walk during the stop
  fig-s04-4-1-field-length-vs-speed.svg   Figure 4-1  minimum detection distance L against speed for the planning decelerations
  fig-s04-4-2-side-elevation.svg          Figure 4-2  side elevation: the scan plane against low objects; the CFG-002 envelope, workspace and keep-clear

The source of record is ../WP-S-04-response-time-and-stopping-budget.md: the §1 conventions table (K, Z), the §2
response budget (every field-sizing path), the §3.1 planning cases, the §3.2 stopping-distance table, the §4.1
field-set table, the §4.3 bumper paragraph, the §4.5 arm and lift paragraph and the §5 zone table; for Figure 4-2
also WP-C-01 §4 (heights, scan planes) and WP-S-02 SR-02.03. The check recomputes every t_b, d_s and L of §4.1 and
every d_s of §3.2 from L = v·t_r + v²/(2a) + K·(t_r + v/a) + Z, the bumper stopping distances of §4.3, the walk
terms of §4.5 and the lift travel, and fails when a stated value differs from the formula by more than the
rounding, when a §2 row's stages do not add up to its t_r, when a row's t_r exceeds its target, or when an SVG is
stale. The loop diagrams and the elevation carry the simulation track's band: drawn to planning values, synthetic,
no evidence credit (assurance/sim/ideas-2d-views.md §7).

    python3 fig_s04.py            # regenerate
    python3 fig_s04.py --check    # fail if the source changed or the SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "WP-S-04-response-time-and-stopping-budget.md"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "stroke": "#D3DDE2", "line": "#7E949B", "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#B86F0C", "amber_bg": "#FFF6E8", "teal": "#00938B", "teal_bg": "#E9F7F5", "red": "#D64535", "red_bg": "#FDEDEB",
  "green": "#2C9A58", "green_bg": "#E8F6EC", "grey_bg": "#EDF2F4", "white": "#FFFFFF",
}
CASES = [(0.1, "coast slow 0.1 m/s²", C["red"]), (0.5, "coast fast 0.5 m/s²", C["amber"]), (1.0, "braked 1.0 m/s²", C["teal"]), (2.0, "braked 2.0 m/s²", C["green"])]
SPEEDS = [(0.05, "crawl"), (0.20, "navigation"), (0.25, "ceiling"), (0.30, "person in zone / carry"), (1.50, "2.0 software ceiling")]
FIELDS = [(1.0, "1.0 m starting field (WP-H-02 §3.3)"), (2.0, "2.0 m protective field (TiM-S)"), (3.0, "3.0 m protective field (nanoScan3 Core)")]


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


def _num(s: str) -> float | None:
  m = re.search(r"-?[0-9]+(?:\.[0-9]+)?", _clean(s))
  return float(m.group(0)) if m else None


def load_source() -> dict:
  text = SOURCE.read_text(encoding="utf-8")
  conv = {r[0]: r for r in _table(text, "## 1. Purpose, inputs and conventions")}
  K = _num(conv["K"][1]) if "K" in conv else None
  Z = _num(conv["Z"][1]) if "Z" in conv else None
  budget = []
  for r in _table(text, "## 2. Response time budget per safety function"):
    budget.append({"sf": r[0], "path": _clean(r[1]), "det": _num(r[2]), "logic": _num(r[3]), "power": _num(r[4]), "tr": _num(r[6]),
                   "target": _num(r[7]), "config": _clean(r[9]) if len(r) > 9 else ""})
  scanner = next((b for b in budget if b["sf"] == "SF-02" and "scanner" in b["path"]), None)
  t_r = scanner["tr"] / 1000.0 if scanner and scanner["tr"] else None
  stop_rows = []
  for r in _table(text, "### 3.2 Stopping distance per speed and stop path"):
    v = _num(r[0])
    cases = []
    for k, a in zip((3, 4, 5), (0.1, 0.5, 1.0)):
      nums = re.findall(r"[0-9]+\.[0-9]+", r[k])
      cases.append((a, float(nums[0]), float(nums[1])) if len(nums) == 2 else None)
    stop_rows.append({"v": v, "d_r": _num(r[2]), "cases": cases})
  fields = []
  for r in _table(text, "### 4.1 Field length per field set"):
    if re.match(r"(FS|CK)-\d", r[0]):
      fields.append({"id": r[0], "set": _clean(r[1]), "v": _num(r[2]), "case": _clean(r[3]), "a": _num(r[4]), "t_b": _num(r[5]),
                     "d_s": _num(r[6]), "L": _num(r[7]), "config": _clean(r[8])})
  src = {"K": K, "Z": Z, "t_r": t_r, "budget": budget, "stop_rows": stop_rows, "fields": fields}
  # §3.1: the three planning cases named in the text
  m = re.search(r"coast slow\*\* \(a = ([0-9.]+) m/s²\), \*\*coast fast\*\* \(a = ([0-9.]+) m/s²\) and \*\*braked\*\*\s*\(a = ([0-9.]+) m/s²\)", text)
  src["cases"] = {"coast slow": float(m.group(1)), "coast fast": float(m.group(2)), "braked": float(m.group(3))} if m else {}
  # §4.3: the bumper path's stopping distances as the text states them, and the edge's overtravel
  sec = _section(text, "### 4.3 Reverse and the bumper")
  m = re.search(r"\*\*([0-9]+) mm\*\* on the slow coast and \*\*([0-9]+) mm\*\* on the fast", sec)
  src["bumper_mm"] = (float(m.group(1)), float(m.group(2))) if m else None
  m = re.search(r"overtravel of about ([0-9]+) to ([0-9]+) mm", sec)
  src["overtravel_mm"] = (float(m.group(1)), float(m.group(2))) if m else None
  # §4.5: the walk terms per total stopping time, the reach, the lift speed and its travel in the SR-12.04 time, the keep-clear radius
  sec = _section(text, "### 4.5 The arm workspace and the lift")
  src["walk_terms"] = [(float(t), float(d)) for d, t in re.findall(r"([0-9.]+) m at ([0-9.]+) s", sec)]
  m = re.search(r"reach of the OpenArm 2.0 is about ([0-9.]+) m", sec)
  src["reach"] = float(m.group(1)) if m else None
  m = re.search(r"lift moves at ([0-9.]+) mm/s", sec)
  src["lift_mm_s"] = float(m.group(1)) if m else None
  m = re.search(r"within the ([0-9]+) ms of\s+SR-12.04 travels ([0-9.]+) mm", sec)
  src["lift_stop"] = (float(m.group(1)), float(m.group(2))) if m else None
  m = re.search(r"draws it at ([0-9.]+) m", sec)
  src["keep_clear"] = float(m.group(1)) if m else None
  # §5: the channel 1 ceiling and the trip margin
  zones = {_clean(r[0]): r for r in _table(text, "## 5. Speed limits per zone")}
  src["ceiling"] = _num(zones["Channel 1 ceiling"][1]) if "Channel 1 ceiling" in zones else None
  m = re.search(r"proposed \*\*limit \+ ([0-9]+) %\*\*", text)
  src["trip_margin"] = float(m.group(1)) / 100.0 if m else None
  # WP-C-01 §4 and WP-S-02 SR-02.03 for the elevation
  c01 = (HERE.parent.parent / "02-concept" / "WP-C-01-item-definition.md").read_text(encoding="utf-8")
  m = re.search(r"LiDAR ([0-9.]+) m above the floor \(A1.*?S3 at ([0-9.]+) m", c01)
  src["planes"] = {"A1": float(m.group(1)), "S3": float(m.group(2))} if m else {}
  m = re.search(r"at most ([0-9]+) mm high at full lift extension", c01)
  src["envelope"] = float(m.group(1)) / 1000.0 if m else None
  m = re.search(r"with a ([0-9]+) mm deck", c01)
  src["deck"] = float(m.group(1)) / 1000.0 if m else None
  s02 = (HERE.parent / "WP-S-02-safety-requirements.md").read_text(encoding="utf-8")
  m = re.search(r"\| SR-02\.03 \| Detection shall cover objects from the floor to at least ([0-9.]+) m", s02)
  src["detect_height"] = float(m.group(1)) if m else None
  return src


def _section(text: str, heading: str) -> str:
  i = text.index(heading)
  j = text.find("\n#", i + len(heading))
  return text[i:j if j > 0 else None]


def model(v: float, a: float, t_r: float, K: float, Z: float) -> tuple[float, float, float]:
  t_b = v / a
  d_s = v * t_r + v * v / (2 * a)
  L = d_s + K * (t_r + t_b) + Z
  return t_b, d_s, L


def _w(s: str, size: float) -> float:
  return len(s) * size * 0.56


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


def fig_field(src: dict) -> str:
  K, Z, t_r = src["K"], src["Z"], src["t_r"]
  W, H = 1180, 600
  x0, y0, pw, ph = 90, 100, 780, 420
  vmax, Lmax = 1.6, 5.0

  def X(v):
    return x0 + v / vmax * pw

  def Y(L):
    return y0 + ph - min(L, Lmax) / Lmax * ph

  body = [text(32, 34, "Figure 4-1  Minimum detection distance L against speed, for the planning decelerations of §3.1", 15, C["ink"], 700),
          text(32, 52, f"L = v·t_r + v²/(2a) + K·(t_r + v/a) + Z with t_r = {t_r:g} s (scanner path), K = {K:g} m/s, Z = {Z:g} m, C = 0 (§4.2). Dots are the rows of the §4.1 table.", 11, C["muted"])]
  body.append(rect(x0, y0, pw, ph, C["white"], C["stroke"], 0))
  for L in range(0, 6):
    body.append(f'<line x1="{x0}" y1="{Y(L):.1f}" x2="{x0 + pw}" y2="{Y(L):.1f}" stroke="{C["stroke"]}" stroke-width="1"/>')
    body.append(text(x0 - 10, Y(L) + 4, f"{L} m", 10.5, C["muted"], anchor="end"))
  for v in (0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5):
    body.append(text(X(v), y0 + ph + 18, f"{v:g}", 10.5, C["muted"], anchor="middle"))
  body.append(text(x0 + pw / 2, y0 + ph + 40, "robot speed v (m/s)", 11, C["muted"], anchor="middle"))
  body.append(text(x0 - 60, y0 - 14, "L, minimum detection distance ahead of the robot", 11, C["muted"]))
  for F, label in FIELDS:
    body.append(f'<line x1="{x0}" y1="{Y(F):.1f}" x2="{x0 + pw}" y2="{Y(F):.1f}" stroke="{C["dim"]}" stroke-width="1.2" stroke-dasharray="6,4"/>')
    body.append(text(x0 + pw - 8, Y(F) - 5, label, 10, C["muted"], anchor="end"))
  for v, label in SPEEDS:
    body.append(f'<line x1="{X(v):.1f}" y1="{y0}" x2="{X(v):.1f}" y2="{y0 + ph}" stroke="{C["stroke"]}" stroke-width="1" stroke-dasharray="2,3"/>')
    body.append(text(X(v) + 3, y0 + 12, label, 9.5, C["dim"], extra=f' transform="rotate(90 {X(v) + 3:.1f} {y0 + 12})" paint-order="stroke" stroke="{C["white"]}" stroke-width="3"'))
  steps = [i * vmax / 160 for i in range(161)]
  for a, label, color in CASES:
    pts = []
    for v in steps:
      _, _, L = model(v, a, t_r, K, Z)
      if L > Lmax * 1.02:
        break
      pts.append((X(v), Y(L)))
    body.append('<path d="M' + " L".join(f"{p:.1f},{q:.1f}" for p, q in pts) + f'" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/>')
    xe, ye = pts[-1]
    body.append(f'<circle cx="{xe:.1f}" cy="{ye:.1f}" r="3.5" fill="{color}" stroke="{C["white"]}" stroke-width="1.5"/>')
  for f in src["fields"]:
    if f["L"] is None or f["L"] > Lmax:
      continue
    color = next((c for a, _, c in CASES if abs(a - f["a"]) < 1e-9), C["ink"])
    body.append(f'<circle cx="{X(f["v"]):.1f}" cy="{Y(f["L"]):.1f}" r="4.5" fill="{C["white"]}" stroke="{color}" stroke-width="2"/>')
  lx, ly = x0 + pw + 24, y0 + 20
  body.append(text(lx, ly, "KEY", 10.5, C["ink"], 700, extra=' letter-spacing="1"'))
  for i, (a, label, color) in enumerate(CASES):
    yy = ly + 22 + i * 24
    body.append(f'<line x1="{lx}" y1="{yy - 3}" x2="{lx + 24}" y2="{yy - 3}" stroke="{color}" stroke-width="2.2"/>')
    body.append(text(lx + 30, yy, label, 10, C["muted"]))
  yy = ly + 22 + len(CASES) * 24 + 6
  body.append(f'<circle cx="{lx + 12}" cy="{yy - 3}" r="4.5" fill="{C["white"]}" stroke="{C["ink"]}" stroke-width="2"/>')
  body.append(text(lx + 30, yy, "a row of the §4.1 table", 10, C["muted"]))
  yy += 24
  body.append(f'<line x1="{lx}" y1="{yy - 3}" x2="{lx + 24}" y2="{yy - 3}" stroke="{C["dim"]}" stroke-width="1.2" stroke-dasharray="6,4"/>')
  body.append(text(lx + 30, yy, "field a scanner provides", 10, C["muted"]))
  body.append(text(W - 32, H - 16, "Generated by figures/fig_s04.py from the WP-S-04 §1, §2 and §4.1 tables", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "s04-4-1", "Figure 4-1: minimum detection distance against speed",
             "A line chart with the robot speed from zero to 1.6 metres per second across and the minimum detection distance from zero to five metres up: four "
             "curves for decelerations of 0.1, 0.5, 1.0 and 2.0 metres per second squared, steepest for the slow coast; dashed horizontal lines at one, two and "
             "three metres for the starting field and the two candidate scanners; dotted vertical markers at the crawl, navigation, ceiling, person-in-zone and "
             "2.0 ceiling speeds; hollow dots on each row of the field-set table.", body)



# ------------------------------------------------------------------------------------------------- the loop diagrams (§2.1)
# One diagram per field-sizing path of §2 (assurance/sim/ideas-2d-views.md §4). Every number drawn comes from the §2 row
# named by (sf, match), the §4.1 rows named, the §1 conventions, the §3.1 cases or the §4.3 / §4.5 sentences that
# check_source() re-derives. The floor strips are scale drawings with the drawn footprint; the Blender companions of
# assurance/sim/blender/renders show the same standstill moment.
LOOPS = [
  dict(n=1, key="sf02-scanner", sf="SF-02", match="scanner", config="CFG-001", field="FS-1b", alts=("FS-1a", "FS-1c"), stop="coast", ledger="field", floor="approach",
       title="SF-02 by the scanner at navigation speed: demand to standstill, with the distance ledger of field set FS-1b",
       demand=("Demand", "a person enters the field")),
  dict(n=2, key="sf02-bumper", sf="SF-02", match="bumper", config="CFG-001", v=0.05, stop="coast", ledger="bumper", floor="reverse",
       title="SF-02 by the rear bumper, reversing at the crawl limit: contact to standstill against the edge's overtravel",
       demand=("Demand", "the edge meets a person's shin")),
  dict(n=3, key="sf03", sf="SF-03", match="window", config="CFG-001", field="FS-1b", ceiling_row="CK-1b", alts=("CK-1a",), stop="coast", ledger="ceiling", floor="approach",
       title="SF-03 at the channel 1 ceiling: a stop from 0.25 m/s against a field sized for 0.20 m/s",
       demand=("Demand", "speed above the trip threshold")),
  dict(n=4, key="sf04-fault", sf="SF-04", match="silent", config="CFG-001", v=0.20, field="FS-1b", stop="coast", ledger="drive-on", floor="drive-on",
       title="SF-04 fault path: channel 1 dead with PWM applied, the hardware watchdog trips the chain",
       demand=("Fault", "channel 1 stops updating")),
  dict(n=5, key="sf11", sf="SF-11", match="station", config="CFG-002", stop="arm", ledger="workspace", floor="station",
       title="SF-11 at the station: a person crosses the workspace ring and the arm stops; the ring as reach plus walk",
       demand=("Demand", "a person crosses the ring")),
  dict(n=6, key="sf12", sf="SF-12", match="keep-clear", config="CFG-002", stop="lift", ledger="keep-clear", floor="lift",
       title="SF-12 at the lift: a person steps onto the keep-clear zone and the lift stops; the zone against the walk",
       demand=("Demand", "someone steps onto the zone")),
]
BAND = "SYNTHETIC: pictures only, no evidence credit"
ROBOT_L, ROBOT_W = 0.78, 0.58     # WP-C-01 §4: 780 × 582 mm chassis


def budget_row(src: dict, sf: str, match: str) -> dict | None:
  return next((b for b in src["budget"] if b["sf"] == sf and match in b["path"]), None)


def field_row(src: dict, fid: str) -> dict:
  return next(f for f in src["fields"] if f["id"] == fid)


def band(w, h, note):
  return [rect(0, h - 44, w, 44, C["amber_bg"], "none", 0), text(16, h - 26, BAND, 11, C["amber"], 700, family=MONO), text(16, h - 11, note, 10, C["amber"])]


def hatch_defs(uid):
  return (f'<defs><pattern id="{uid}-hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          f'<line x1="0" y1="0" x2="0" y2="8" stroke="{C["amber"]}" stroke-width="1.2" opacity="0.7"/></pattern>'
          f'<pattern id="{uid}-hatchred" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          f'<line x1="0" y1="0" x2="0" y2="8" stroke="{C["red"]}" stroke-width="1.2" opacity="0.5"/></pattern>'
          f'<marker id="{uid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{C["ink"]}"/></marker></defs>')


def line(x1, y1, x2, y2, stroke, sw=1.2, dash="", extra=""):
  d = f' stroke-dasharray="{dash}"' if dash else ""
  return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>'


def circle(cx, cy, r, fill, stroke="none", sw=1, dash="", extra=""):
  d = f' stroke-dasharray="{dash}"' if dash else ""
  return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>'


def footprint(cx, cy, M, heading=1, opacity=1.0, ghost=False):
  """The base from above at M px/m: deck, bumper ends, drive wheels, castors, the scanner dot; +x is the heading."""
  rl, rw = ROBOT_L * M, ROBOT_W * M
  stroke, fill = (C["green"], "none") if ghost else ("#1B1F22", "#F4F6F7")
  g = [f'<g opacity="{opacity}" transform="translate({cx:.1f},{cy:.1f}) scale({heading},1)">',
       rect(-rl / 2, -rw / 2, rl, rw, fill, stroke, 0.07 * M, 1.6, "4,3" if ghost else "")]
  if not ghost:
    for sx in (-rl / 2, rl / 2 - 0.05 * M):
      g.append(rect(sx, -rw / 2, 0.05 * M, rw, "#1B1F22", "none", 0.03 * M))
    for sy in (-rw / 2 - 0.03 * M, rw / 2 - 0.03 * M):
      g.append(rect(-0.2 * M, sy, 0.2 * M, 0.06 * M, "#15181A", "#2F3A44", 2))
    for (qx, qy) in ((-0.25 * M, 0.0), (0.27 * M, -0.19 * M), (0.27 * M, 0.19 * M)):
      g.append(circle(qx, qy, 0.05 * M, "#9AA3AB", "#2F6DB5", 1))
    g.append(circle(rl / 2 - 0.1 * M, 0, 0.035 * M, C["teal"]))
    g.append(rect(-rl / 2 - 0.045 * M, -rw / 2 + 0.02 * M, 0.04 * M, rw - 0.04 * M, C["red"], "none", 2))
  g.append("</g>")
  return g


def person(cx, cy, M, col, ghost=False, label="", anchor="middle", dy=None):
  out = [circle(cx, cy, 0.14 * M, "none" if ghost else col, col, 1.6, "3,2" if ghost else "")]
  if label:
    out.append(text(cx, cy + (dy if dy is not None else -0.14 * M - 8), label, 9.5, col, 700, anchor))
  return out


def stage_boxes(y, stages):
  """Six boxes across: (title, line 2, line 3, kind) with kind in demand, chain, stop, end."""
  out = []
  n = len(stages)
  x = 28
  for i, (t1, t2, t3, kind) in enumerate(stages):
    w = 114 if i == n - 1 else 150
    fill, stroke, dash = {"demand": (C["red_bg"], C["red"], ""), "chain": (C["teal_bg"], C["teal"], ""), "stop": (C["amber_bg"], C["amber"], "5,3"),
                          "end": (C["green_bg"], C["green"], ""), "tbc": (C["grey_bg"], C["dim"], "5,3")}[kind]
    out.append(rect(x, y, w, 58, fill, stroke, 6, 1.4, dash))
    out += [text(x + w / 2, y + 22, t1, 11.5, C["ink"], 700, "middle"), text(x + w / 2, y + 38, t2, 10, C["muted"], anchor="middle"),
            text(x + w / 2, y + 52, t3, 10, C["amber"] if kind == "stop" else C["muted"], 700 if kind == "stop" else 400, "middle")]
    if i < n - 1:
      out += [line(x + w, y + 29, x + w + 36, y + 29, C["ink"], 1.4), f'<polygon points="{x + w + 36:.0f},{y + 25} {x + w + 44:.0f},{y + 29} {x + w + 36:.0f},{y + 33}" fill="{C["ink"]}"/>']
    x += w + 40
  return out


def time_axis(uid, y, t_end, phases, marks):
  """phases: (t0, t1, label, kind) bars above the axis; marks: (t, label, colour) vertical lines."""
  x0, x1 = 120, 1092
  X = lambda t: x0 + (x1 - x0) * t / t_end  # noqa: E731
  out = [text(28, y - 8, "Time", 11.5, C["ink"], 700), line(x0, y, x1, y, C["line"], 1)]
  step = 0.1 if t_end <= 0.8 else 0.25
  n = int(round(t_end / step))
  for i in range(n + 1):
    t = i * step
    out += [line(X(t), y - 4, X(t), y + 4, C["line"], 1), text(X(t), y + 18, f"{t:g} s" if i else "0", 10, C["muted"], anchor="middle")]
  for t0, t1, label, kind in phases:
    fill, stroke = {"chain": (C["teal_bg"], C["teal"]), "stop": (f"url(#{uid}-hatch)", C["amber"]), "fault": (C["red_bg"], C["red"]), "tbc": (C["grey_bg"], C["dim"])}[kind]
    out.append(rect(X(t0), y - 28, X(t1) - X(t0), 14, fill, stroke, 0, 1, "4,3" if kind in ("stop", "tbc") else ""))
    if X(t1) - X(t0) > _w(label, 9) + 8:
      out.append(text((X(t0) + X(t1)) / 2, y - 17, label, 9, stroke if kind != "stop" else C["amber"], 600, "middle"))
    else:
      narrow = sum(1 for q in phases[:phases.index((t0, t1, label, kind))] if X(q[1]) - X(q[0]) <= _w(q[2], 9) + 8)
      out.append(text((X(t0) + X(t1)) / 2, y - 32 - 10 * (narrow % 2), label, 8.5, stroke, 600, "middle"))
  for i, (t, label, col) in enumerate(sorted(marks)):
    yy = y - 52 - 12 * (i % 2)
    out.append(line(X(t), yy + 4, X(t), y + 4, col, 1.2))
    out.append(text(X(t) - 4, yy, label, 9.5, col, 600, "end") if X(t) > 930 else text(X(t) + 4, yy, label, 9.5, col, 600))
  return out


def ledger_bar(uid, y, M, x0, terms, total_label=""):
  """Stacked distance bar at M px/m: terms are (length_m, kind, label); kinds solid-teal, hatch, walk, tol, red."""
  out = []
  x = x0
  labels = []
  for length, kind, label in terms:
    w = length * M
    if kind == "teal":
      out.append(rect(x, y, w, 30, C["teal"], "none", 0))
    elif kind == "hatch":
      out.append(rect(x, y, w, 30, f"url(#{uid}-hatch)", C["amber"], 0, 1))
    elif kind == "walk":
      out.append(rect(x, y, w, 30, "#2FA69C", "none", 0, 1, "", ' opacity="0.55"'))
    elif kind == "tol":
      out.append(rect(x, y, w, 30, C["grey_bg"], C["line"], 0, 1))
    elif kind == "red":
      out.append(rect(x, y, w, 30, f"url(#{uid}-hatchred)", C["red"], 0, 1))
    elif kind == "redsolid":
      out.append(rect(x, y, w, 30, C["red"], "none", 0))
    labels.append((x, w, label, kind))
    x += w
  if total_label:
    out += [line(x0, y - 10, x, y - 10, C["ink"], 1), line(x0, y - 14, x0, y - 6, C["ink"], 1), line(x, y - 14, x, y - 6, C["ink"], 1),
            text((x0 + x) / 2, y - 14, total_label, 10, C["ink"], 700, "middle")]
  # labels: wide terms inside, narrow ones staggered below
  k = 0
  for lx, w, label, kind in labels:
    if not label:
      continue
    if w > _w(label, 10) + 10:
      out.append(text(lx + w / 2, y + 19, label, 10, C["white"] if kind in ("teal", "walk", "redsolid") else C["ink"], 700, "middle"))
    else:
      col = {"teal": C["teal"], "hatch": C["amber"], "tol": C["muted"], "red": C["red"], "redsolid": C["red"]}.get(kind, C["ink"])
      out.append(text(lx + w / 2, y + 44 + 13 * (k % 2), label, 9.5, col, 600, "middle"))
      k += 1
  return out, x


def floor_strip(uid, y, M, x0, x1, label, h=90):
  """The strip's frame, grid and title; the caller wraps its drawing in clip(uid) ... '</g>' so nothing spills out."""
  out = [text(28, y - 22, label, 11.5, C["ink"], 700), f'<clipPath id="{uid}-strip"><rect x="{x0 - 30}" y="{y}" width="{x1 - x0 + 30}" height="{h}"/></clipPath>',
         line(x0, y + h, x1, y + h, C["stroke"], 1)]
  for i in range(1, int((x1 - x0) / M) + 1):
    out.append(line(x0 + i * M, y, x0 + i * M, y + h, C["grey_bg"], 1))
    out.append(text(x0 + i * M, y + h + 12, f"{i} m", 9, C["dim"], anchor="middle"))
  return out


def clip(uid):
  return f'<g clip-path="url(#{uid}-strip)">'


def fig_loop(src: dict, lp: dict) -> str:
  K, Z, t_r0 = src["K"], src["Z"], src["t_r"]
  b = budget_row(src, lp["sf"], lp["match"])
  t_det, t_logic, t_pow, t_r = b["det"] / 1000.0, b["logic"] / 1000.0, b["power"] / 1000.0, b["tr"] / 1000.0
  cases = src["cases"]
  a_fast, a_slow = cases["coast fast"], cases["coast slow"]
  W, H = 1120, 720
  uid = f"s04-2-{lp['n']}"
  path = [p.strip() for p in b["path"].split("→")]
  det_name, logic_name, pow_name = path[0], " → ".join(path[1:-1]) or "logic", path[-1]
  body = [hatch_defs(uid), text(28, 34, f"Figure 2-{lp['n']}  {lp['title']}", 15, C["ink"], 700)]
  M = 400.0     # px per metre on the ledger
  Mf = 200.0    # px per metre on the floor strip
  desc = ""
  if lp["ledger"] in ("field", "ceiling", "drive-on"):
    f = field_row(src, lp["field"])
    v = f["v"] if lp["ledger"] != "ceiling" else src["ceiling"]
    v_cmd = f["v"]
    t_b = v / a_fast
    d_r, d_b = v * t_r, v * v / (2 * a_fast)
    walk = K * (t_r + t_b)
    L = d_r + d_b + walk + Z
    t_s = t_r + t_b
    body.append(text(28, 54, f"§2 row {lp['sf']} ({lp['match']} path): {b['det']:g} + {b['logic']:g} + {b['power']:g} = {b['tr']:g} ms against the {b['target']:g} ms target; "
                     f"{lp['config']}, {f['case']} planning case a = {a_fast:g} m/s² (unmeasured, WP-V-02); K = {K:g} m/s, Z = {Z:g} m, C = 0 (§4.2).", 11, C["muted"]))
    if lp["ledger"] == "field":
      stages = [(lp["demand"][0], lp["demand"][1], "t = 0", "demand"), (det_name, "OSSDs open", f"{b['det']:g} ms (datasheet)", "chain"),
                (logic_name, "speed monitor and relay", f"{b['logic']:g} ms", "chain"), (pow_name, "power removed, category 0", f"{b['power']:g} ms · t_r = {b['tr']:g} ms", "chain"),
                ("Coast", "no brake on CFG-001", f"t_b {t_b:.2f} s at a = {a_fast:g} m/s²", "stop"), ("Standstill", f"t = {t_s:.2f} s", "latched, SF-05 reset", "end")]
      phases = [(0, t_det, f"{det_name} {b['det']:g} ms", "chain"), (t_det, t_det + t_logic, f"logic {b['logic']:g}", "chain"), (t_det + t_logic, t_r, f"K {b['power']:g}", "chain"),
                (t_r, t_s, f"coast {t_b:.2f} s, unmeasured (WP-V-02 ST-01)", "stop")]
      marks = [(t_r, f"power removed, {t_r:.2f} s", C["red"]), (t_s, f"standstill {t_s:.2f} s", C["green"])]
      t_end = 0.6
    elif lp["ledger"] == "ceiling":
      thr = v_cmd * (1 + src["trip_margin"])
      stages = [(lp["demand"][0], f"speed over {thr:.2f} m/s", f"limit + {src['trip_margin'] * 100:.0f} %; the cap is {v:g} m/s", "demand"), (f"E6 window", "speed held above the limit", f"{b['det']:g} ms", "chain"),
                (logic_name, "speed monitor and relay", f"{b['logic']:g} ms", "chain"), (pow_name, "power removed, category 0", f"{b['power']:g} ms · t_r = {b['tr']:g} ms", "chain"),
                ("Coast", f"from {v:g} m/s, no brake", f"t_b {t_b:.2f} s at a = {a_fast:g} m/s²", "stop"), ("Standstill", f"t = {t_s:.2f} s", "latched, SF-05 reset", "end")]
      phases = [(0, t_det, f"window {b['det']:g} ms", "chain"), (t_det, t_det + t_logic, f"logic {b['logic']:g}", "chain"), (t_det + t_logic, t_r, f"K {b['power']:g}", "chain"),
                (t_r, t_s, f"coast {t_b:.2f} s from {v:g} m/s, unmeasured", "stop")]
      marks = [(t_r, f"power removed, {t_r:.2f} s", C["red"]), (t_s, f"standstill {t_s:.2f} s", C["green"])]
      t_end = 0.8
    else:  # drive-on: the fault path
      t_dead = t_det + t_logic + t_pow
      stages = [(lp["demand"][0], lp["demand"][1], "t = 0, PWM held", "demand"), ("No command", "drives hold the last PWM", f"{b['det']:g} ms watchdog window", "chain"),
                (logic_name, "watchdog output, relay", f"{b['logic']:g} ms", "chain"), (pow_name, "power removed, category 0", f"{b['power']:g} ms · t_r = {b['tr']:g} ms", "chain"),
                ("Coast", "no brake on CFG-001", f"t_b {t_b:.2f} s at a = {a_fast:g} m/s²", "stop"), ("Standstill", f"t = {t_s:.2f} s", "latched, SF-05 reset", "end")]
      phases = [(0, t_det, f"hardware watchdog window {b['det']:g} ms: the robot drives on at {v:g} m/s", "fault"), (t_det, t_det + t_logic, f"logic {b['logic']:g}", "chain"), (t_det + t_logic, t_r, f"K {b['power']:g}", "chain"),
                (t_r, t_s, f"coast {t_b:.2f} s", "stop")]
      marks = [(t_r, f"power removed, {t_r:.2f} s", C["red"]), (t_s, f"standstill {t_s:.2f} s", C["green"])]
      t_end = 1.5
    body += stage_boxes(92, stages)
    body += time_axis(uid, 222, t_end, phases, marks)
    # the ledger
    body.append(text(28, 272, "Distance ledger: what makes the field length L" if lp["ledger"] == "field" else
                     ("Distance ledger: the field the stop from the ceiling needs, against the field the robot carries" if lp["ledger"] == "ceiling" else "Distance ledger: how far a faulty drive carries the robot"), 11.5, C["ink"], 700))
    body.append(text(28, 288, f"drawn to scale, 1 m = {M:.0f} px; the person walks toward the robot at K = {K:g} m/s for the whole stopping time", 10, C["muted"]))
    if lp["ledger"] == "field":
      bar, xe = ledger_bar(uid, 318, M, 120, [(d_r, "teal", f"d_r {d_r:.3f}"), (d_b, "hatch", f"d_b {d_b:.3f} coast"), (walk, "walk", f"person's walk K·(t_r + t_b) = {walk:.2f} m"), (Z, "tol", f"Z {Z:g}")],
                           f"L = {L:.2f} m ({lp['field']})")
      body += bar
      body.append(rect(xe, 318, 2, 30, C["red"], "none", 0)); body.append(text(xe + 6, 363, f"C = 0 (§4.2, planning)", 9.5, C["red"], 600))
      alt_a = field_row(src, lp["alts"][0]); alt_c = field_row(src, lp["alts"][1])
      body += [text(120, 396, f"d_r = v·t_r = {v:g} × {t_r:g} = {d_r:.3f} m   ·   d_b = v²/2a = {d_b:.3f} m (coast fast; {v * v / (2 * a_slow):.3f} m on the slow coast)   ·   d_s = {d_r + d_b:.3f} m", 10.5, C["ink"]),
               text(120, 414, f"L = {d_r:.3f} + {d_b:.3f} + {walk:.2f} + {Z:g} + 0 = {L:.2f} m ({lp['field']}). Slow coast (a = {a_slow:g} m/s²): t_b = {v / a_slow:.1f} s, the walk {K * (t_r + v / a_slow):.1f} m, L = {alt_a['L']:.2f} m ({alt_a['id']}); braked at {alt_c['a']:g} m/s² ({alt_c['config']}): L = {alt_c['L']:.2f} m ({alt_c['id']}).", 10.5, C["ink"])]
      desc = (f"Six boxes from the demand through the scanner, the logic, the contactors, the coast and the standstill with the times of the budget row; a time axis to {t_end:g} s with the "
              f"phases and the power-removed and standstill marks; a distance bar to scale adding the reaction travel, the hatched coast, the person's walk and the tolerance to the field length {L:.2f} m; "
              f"a floor strip with the robot, its field, the standstill ghost and the person at the demand and at standstill.")
    elif lp["ledger"] == "ceiling":
      ck = field_row(src, lp["ceiling_row"]); short = L - f["L"]
      body.append(rect(120, 298, f["L"] * M, 10, C["teal"], "none", 0))
      body.append(text(120 + f["L"] * M + 8, 307, f"the field carried: {lp['field']}, {f['L']:.2f} m at {v_cmd:g} m/s", 9.5, C["teal"], 600))
      bar, xe = ledger_bar(uid, 330, M, 120, [(d_r, "teal", f"d_r {d_r:.3f}"), (d_b, "hatch", f"d_b {d_b:.3f}"), (walk, "walk", f"walk K·(t_r + t_b) = {walk:.2f} m at {v:g} m/s"), (Z, "tol", f"Z {Z:g}")],
                           f"needed from {v:g} m/s: L = {L:.2f} m ({ck['id']})")
      body += bar
      body.append(rect(120 + f["L"] * M, 326, short * M, 38, f"url(#{uid}-hatchred)", C["red"], 0, 1.2))
      body.append(text(120 + f["L"] * M + short * M + 6, 349, f"short {short:.2f} m", 10, C["red"], 700))
      alt = field_row(src, lp["alts"][0])
      body += [text(120, 400, f"At the {v:g} m/s cap (DQ-006 A) the fast coast needs {L:.2f} m ({ck['id']}), the slow coast {alt['L']:.2f} m ({alt['id']}); {lp['field']} carries {f['L']:.2f} m: in the planning case the person reaches the robot {short - Z:.2f} m before it stops.", 10, C["ink"]),
               text(120, 418, f"The cap and the trip at limit + {src['trip_margin'] * 100:.0f} % within the {b['det']:g} ms window bound this case, not the field (§5). Whether FS-1 is sized for the cap is OI-8.", 10, C["ink"])]
      desc = (f"Six boxes from the overspeed demand through the monitor window, the logic, the contactors, the coast from {v:g} m/s and the standstill; a time axis to {t_end:g} s; the field carried as a thin bar over "
              f"the distance bar the stop from the ceiling needs, with the {short:.2f} m shortfall hatched red; a floor strip with the robot, the field, the standstill ghost and the person reaching the front.")
    else:
      d_dead = v * t_dead
      walk_n = 0.0
      bar, xe = ledger_bar(uid, 318, M, 120, [(d_dead, "redsolid", f"no command {d_dead:.2f} m"), (d_b, "hatch", f"coast {d_b:.3f}")], f"drive-on {d_dead + d_b:.2f} m (fast coast)")
      body += bar
      body.append(rect(120, 382, (d_dead + v * v / (2 * a_slow)) * M, 10, f"url(#{uid}-hatch)", C["amber"], 0, 1))
      body.append(text(120 + (d_dead + v * v / (2 * a_slow)) * M + 8, 391, f"slow coast: {d_dead:.2f} + {v * v / (2 * a_slow):.2f} = {d_dead + v * v / (2 * a_slow):.2f} m", 9.5, C["amber"], 600))
      body += [text(120, 412, f"Channel 1 died with PWM applied: no demand, no controlled stop. The hardware watchdog (SR-04.04) trips the chain {t_dead:.2f} s after the last update ({b['det']:g} + {b['logic']:g} + {b['power']:g} ms): {t_dead:.2f} × {v:g} = {d_dead:.2f} m driven, then the coast.", 10, C["ink"]),
               text(120, 428, f"No person is in this ledger: the SF-02 scanner path stays live through channel 2 ({lp['field']} ahead, teal on the floor). This path bounds how far a faulty drive carries the robot; the window is a parameter (WP-W-09).", 10, C["ink"])]
      desc = (f"Six boxes from the fault through the watchdog window, the logic, the contactors, the coast and the standstill; a time axis to {t_end:g} s with the window red; a distance bar of the {d_dead:.2f} m driven with no "
              f"command and the coast; a floor strip with the robot at the fault, its still-live field and the standstill ghost.")
    # the floor strip
    fy = 486
    body += floor_strip(uid, fy, Mf, 120, 1092, f"The same numbers on the floor (1 m = {Mf:.0f} px)")
    body.append(clip(uid))
    rx, ry = 140 + ROBOT_L / 2 * Mf, fy + 45
    fx = rx + ROBOT_L / 2 * Mf
    if lp["ledger"] in ("field", "ceiling"):
      body.append(rect(fx, ry - (ROBOT_W / 2 + Z) * Mf, f["L"] * Mf, (ROBOT_W + 2 * Z) * Mf, C["teal_bg"], C["teal"], 0, 1.2))
      body.append(text(fx + f["L"] * Mf / 2, ry - (ROBOT_W / 2 + Z) * Mf - 6, f"field {lp['field']}, {f['L']:.2f} m", 10, C["teal"], 700, "middle"))
      if lp["ledger"] == "ceiling":
        body.append(rect(fx + f["L"] * Mf, ry - (ROBOT_W / 2 + Z) * Mf, short * Mf, (ROBOT_W + 2 * Z) * Mf, f"url(#{uid}-hatchred)", C["red"], 0, 1))
        body.append(text(fx + f["L"] * Mf + short * Mf + 4, ry - (ROBOT_W / 2 + Z) * Mf - 6, f"needed from {v:g} m/s: {L:.2f} m", 10, C["red"], 700))
      d_s = d_r + d_b
      body += footprint(rx, ry, Mf) + footprint(rx + d_s * Mf, ry, Mf, ghost=True)
      body.append(text(rx + d_s * Mf + ROBOT_L / 2 * Mf + 4, ry + ROBOT_W / 2 * Mf + 14, f"standstill ghost, +{d_s:.3f} m", 9.5, C["green"], 600))
      px0 = fx + f["L"] * Mf
      px1 = max(px0 - walk * Mf, rx + d_s * Mf + ROBOT_L / 2 * Mf + 0.14 * Mf) if lp["ledger"] == "ceiling" else px0 - walk * Mf
      body += person(px0, ry, Mf, C["amber"], label="person at t = 0") + person(px1, ry, Mf, C["amber"], ghost=True)
      body.append(line(px0 - 0.14 * Mf, ry, px1 + 0.14 * Mf, ry, C["amber"], 1.4, "6,4"))
      body.append(text((px0 + px1) / 2, ry + 0.14 * Mf + 14, f"walks {walk:.2f} m at {K:g} m/s", 9.5, C["amber"], 600, "middle"))
      body.append("</g>")
      gap = f["L"] - walk - d_s
      note = (f"closest approach in the planning case: {gap:.2f} m (= Z + C) between the standstill ghost and the person" if gap >= 0 else
              f"planning case: the person reaches the robot's front {-gap:.2f} m before the standstill; the field is {short:.2f} m short of {ck['id']}")
      body.append(text(1092, fy + 118, note, 10, C["red"] if gap < Z - 1e-6 and lp["ledger"] == "ceiling" else C["teal"], 600, "end"))
    else:
      body.append(rect(fx + d_dead * Mf + d_b * Mf, ry - (ROBOT_W / 2 + Z) * Mf, f["L"] * Mf, (ROBOT_W + 2 * Z) * Mf, C["teal_bg"], C["teal"], 0, 1.2, "5,3"))
      body.append(text(fx + (d_dead + d_b) * Mf + f["L"] * Mf / 2, ry - (ROBOT_W / 2 + Z) * Mf - 6, f"field {lp['field']} stays live (channel 2), {f['L']:.2f} m", 10, C["teal"], 700, "middle"))
      body.append(rect(rx - ROBOT_L / 2 * Mf, ry + ROBOT_W / 2 * Mf + 6, d_dead * Mf, 8, C["red"], "none", 0))
      body.append(rect(rx - ROBOT_L / 2 * Mf + d_dead * Mf, ry + ROBOT_W / 2 * Mf + 6, d_b * Mf, 8, f"url(#{uid}-hatch)", C["amber"], 0, 1))
      body += footprint(rx, ry, Mf, opacity=0.35) + footprint(rx + (d_dead + d_b) * Mf, ry, Mf)
      body.append("</g>")
      body.append(text(rx - ROBOT_L / 2 * Mf, fy + 118, f"at the fault (faded) → no command {d_dead:.2f} m (red) → coast {d_b:.3f} m (hatched) → standstill", 9.5, C["ink"], 600))
    body.append(text(W - 32, H - 52, "Generated by assurance/03-system/figures/fig_s04.py from the WP-S-04 §1, §2, §3.1, §4.1 and §5 tables", 9.5, C["dim"], anchor="end"))
    body += band(W, H, f"Drawn to WP-S-04 v0.2 planning values (t_r {t_r:g} s, a = {a_fast:g} m/s² unmeasured, C = 0, K = {K:g} m/s). A loop diagram shows the arithmetic of a stop; it does not show that a measure works.")
    return svg(W, H, uid, f"Figure 2-{lp['n']}: {lp['title']}", desc, body)

  if lp["ledger"] == "bumper":
    v = lp["v"]
    mm_slow, mm_fast = src["bumper_mm"]
    ot = src["overtravel_mm"]
    d_r = v * t_r
    d_b_f, d_b_s = v * v / (2 * a_fast), v * v / (2 * a_slow)
    t_b_f, t_b_s = v / a_fast, v / a_slow
    body.append(text(28, 54, f"§2 row {lp['sf']} ({lp['match']} path): {b['det']:g} + {b['logic']:g} + {b['power']:g} = {b['tr']:g} ms against the {b['target']:g} ms target; reverse at the crawl limit {v:g} m/s (DQ-018 A), {lp['config']}; "
                     f"the edge detects by contact, so there is no distance before it (§4.3).", 11, C["muted"]))
    stages = [(lp["demand"][0], lp["demand"][1], "t = 0, the edge compresses", "demand"), (det_name, "contact detected", f"{b['det']:g} ms (TBC: unit)", "chain"),
              (logic_name, "unit, speed monitor, relay", f"{b['logic']:g} ms", "chain"), (pow_name, "power removed, category 0", f"{b['power']:g} ms · t_r = {b['tr']:g} ms", "chain"),
              ("Coast", "no brake on CFG-001", f"t_b {t_b_f:.2f} s fast, {t_b_s:.2f} slow", "stop"), ("Standstill", f"t = {t_r + t_b_f:.2f} / {t_r + t_b_s:.2f} s", "inside the overtravel", "end")]
    body += stage_boxes(92, stages)
    phases = [(0, t_det, f"edge {b['det']:g}", "chain"), (t_det, t_det + t_logic, f"logic {b['logic']:g}", "chain"), (t_det + t_logic, t_r, f"K {b['power']:g}", "chain"),
              (t_r, t_r + t_b_f, f"coast fast {t_b_f:.2f} s", "stop"), (t_r + t_b_f, t_r + t_b_s, f"coast slow, to {t_r + t_b_s:.2f} s (unmeasured)", "stop")]
    marks = [(t_r, f"power removed, {t_r:.2f} s", C["red"]), (t_r + t_b_f, f"standstill (fast) {t_r + t_b_f:.2f} s", C["green"]), (t_r + t_b_s, f"standstill (slow) {t_r + t_b_s:.2f} s", C["green"])]
    body += time_axis(uid, 222, 0.6, phases, marks)
    Mm = 20.0   # px per mm
    body += [text(28, 272, "Distance ledger: the stopping distance after contact against the edge's overtravel", 11.5, C["ink"], 700),
             text(28, 288, f"drawn to scale, 1 mm = {Mm:.0f} px; the edge must still be compressing when the robot stops, or the force rises to the wheel torque", 10, C["muted"])]
    body.append(rect(120, 306, ot[1] * Mm, 116, C["green_bg"], C["green"], 0, 1, "5,3"))
    body.append(rect(120, 306, ot[0] * Mm, 116, C["green_bg"], C["green"], 0, 1))
    body += [text(120 + ot[1] * Mm + 10, 360, f"edge overtravel {ot[0]:g} mm (solid)", 9.5, C["green"], 700), text(120 + ot[1] * Mm + 10, 374, f"to {ot[1]:g} mm (dashed; TBC: datasheet)", 9.5, C["green"], 600)]
    bar, xe = ledger_bar(uid, 326, Mm * 1000, 120, [(d_r, "teal", f"d_r {d_r * 1000:.1f} mm"), (d_b_f, "hatch", f"{d_b_f * 1000:.1f}")], f"{mm_fast:g} mm, fast coast: d_r + coast {d_b_f * 1000:.1f} mm")
    body += bar
    bar2, xe2 = ledger_bar(uid, 386, Mm * 1000, 120, [(d_r, "teal", f"d_r {d_r * 1000:.1f} mm"), (d_b_s, "hatch", f"coast slow {d_b_s * 1000:.1f} mm")], f"{mm_slow:g} mm, slow coast")
    body += bar2
    body += [text(120, 436, f"d_s = v·t_r + v²/2a = {v:g} × {t_r:g} + {v:g}²/(2 × {a_fast:g}) = {mm_fast:g} mm on the fast coast, {mm_slow:g} mm on the slow one (a = {a_slow:g}): inside the {ot[0]:g} to {ot[1]:g} mm overtravel of a Mayser SL/BK class edge (TBC).", 10, C["ink"]),
             text(120, 452, f"Above about 0.1 m/s the slow-coast stop ({0.1 * t_r * 1000 + 0.1 * 0.1 / (2 * a_slow) * 1000:.0f} mm) outruns the overtravel: the speed monitor's direction-and-speed rule (SR-03.02) keeps the bumper adequate; the reverse limit is a safety parameter (§4.3).", 10, C["ink"])]
    fy = 486
    body += floor_strip(uid, fy, Mf, 120, 1092, f"The same numbers on the floor (1 m = {Mf:.0f} px): the undock reverse toward the dock, rear sector masked")
    body.append(clip(uid))
    rx, ry = 140 + 1.2 * Mf, fy + 45
    body.append(rect(rx + ROBOT_L / 2 * Mf, ry - ROBOT_W / 2 * Mf, 0.7 * Mf, ROBOT_W * Mf, f"url(#{uid}-hatchred)", C["red"], 0, 1))
    body.append(text(rx + ROBOT_L / 2 * Mf + 0.35 * Mf, ry - ROBOT_W / 2 * Mf - 6, "blind reverse 0.7 m, bumper only (GAP-35, DQ-018 A)", 9.5, C["red"], 700, "middle"))
    body += footprint(rx, ry, Mf, heading=-1)
    body.append(text(rx, ry + 0.04 * Mf, f"← {v:g} m/s", 10, C["ink"], 700, "middle"))
    body.append(rect(rx + ROBOT_L / 2 * Mf + 0.7 * Mf, ry - 0.3 * Mf, 0.35 * Mf, 0.6 * Mf, "#DCE8F5", "#1E4A80", 2, 1.5))
    body.append(text(rx + ROBOT_L / 2 * Mf + 0.7 * Mf + 0.175 * Mf, ry + 4, "dock", 9.5, "#1E4A80", 700, "middle"))
    px = rx + ROBOT_L / 2 * Mf + 0.045 * Mf + 0.14 * Mf
    body += person(px, ry, Mf, C["amber"], label="person behind, shin at the edge", anchor="start", dy=-0.14 * Mf - 8)
    body.append("</g>")
    body.append(text(1092, fy + 118, f"the stop after contact is {mm_fast:g} to {mm_slow:g} mm: smaller than the edge's travel, invisible at this scale", 10, C["teal"], 600, "end"))
    body.append(text(W - 32, H - 52, "Generated by assurance/03-system/figures/fig_s04.py from the WP-S-04 §1, §2, §3.1 tables and §4.3", 9.5, C["dim"], anchor="end"))
    body += band(W, H, f"Drawn to WP-S-04 v0.2 planning values (t_r {t_r:g} s, a = {a_fast:g} and {a_slow:g} m/s² unmeasured). A loop diagram shows the arithmetic of a stop; it does not show that a measure works.")
    return svg(W, H, uid, f"Figure 2-{lp['n']}: {lp['title']}",
               f"Six boxes from contact through the edge, the monitoring unit and relay, the contactors, the coast and the standstill; a time axis to 0.6 s with both coast cases; a millimetre-scale ledger with the "
               f"{mm_fast:g} mm fast-coast and {mm_slow:g} mm slow-coast stopping distances inside the {ot[0]:g} to {ot[1]:g} mm overtravel band; a floor strip with the robot reversing toward the dock over the blind 0.7 m path and a person behind it.", body)

  if lp["ledger"] == "workspace":
    reach = src["reach"]
    terms = dict((t, d) for t, d in src["walk_terms"])
    t_total = 0.3
    t_b = t_total - t_r
    walk = K * t_total
    body.append(text(28, 54, f"§2 row {lp['sf']}: {b['det']:g} + {b['logic']:g} + {b['power']:g} = {b['tr']:g} ms against the {b['target']:g} ms target, {lp['config']}; the arm's stopping time is unknown (WP-C-01 OI-6): "
                     f"drawn at {t_b:.2f} s so that t_r + t_b = {t_total:g} s, the middle case of §4.5; K = {K:g} m/s.", 11, C["muted"]))
    stages = [(lp["demand"][0], lp["demand"][1], "t = 0", "demand"), ("Station device", "scanner field or mat", f"{b['det']:g} ms", "chain"),
              (logic_name, "logic", f"{b['logic']:g} ms", "chain"), (pow_name, "STO path (TBC)", f"{b['power']:g} ms · t_r = {b['tr']:g} ms", "chain"),
              ("Arm stop", "joint brakes (TBC)", f"t_b = {t_b:.2f} s assumed", "tbc"), ("Standstill", f"t = {t_total:g} s", "arm at rest, SF-11", "end")]
    body += stage_boxes(92, stages)
    phases = [(0, t_det, f"device {b['det']:g}", "chain"), (t_det, t_det + t_logic, f"logic {b['logic']:g}", "chain"), (t_det + t_logic, t_r, f"STO {b['power']:g}", "chain"), (t_r, t_total, f"arm stop {t_b:.2f} s, TBC", "tbc")]
    marks = [(t_r, f"torque off, {t_r:.2f} s", C["red"]), (t_total, f"standstill {t_total:g} s (assumed)", C["green"])]
    body += time_axis(uid, 222, 0.6, phases, marks)
    body += [text(28, 272, "Distance ledger: what makes the workspace boundary of SR-11.02", 11.5, C["ink"], 700),
             text(28, 288, f"drawn to scale, 1 m = {M:.0f} px, from the shoulder axis outward; the person walks in at K for the whole stopping time", 10, C["muted"])]
    bar, xe = ledger_bar(uid, 318, M, 120, [(reach, "teal", f"reach {reach:g} m (planning value)"), (walk, "walk", f"walk K·(t_r + t_b) = {walk:.2f} m")], f"boundary {reach + walk:.2f} m from the shoulder")
    body += bar
    alts = ", ".join(f"{d:.2f} m at {t:g} s" for t, d in sorted(terms.items()) if abs(t - t_total) > 1e-9)
    body += [text(120, 380, f"Reach {reach:g} m: shoulder to fingertip, read from the OpenArm 2.0 description package's joint offsets (assurance/sim/blender), not measured. Walk {walk:.2f} m = {K:g} × ({t_r:g} + {t_b:.2f}).", 10, C["ink"]),
             text(120, 396, f"Other stopping times: {alts}. The boundary is provisional (AOU-10) until upstream publishes the arm's reach and stopping time (WP-S-02 OI-8); a 0.5 s stop moves it to {reach + terms.get(0.5, 0.80):.2f} m.", 10, C["ink"])]
    fy = 436
    body += floor_strip(uid, fy, Mf, 120, 1092, f"The same numbers on the floor (1 m = {Mf:.0f} px): the station seen from above, a slice through the ring", h=180)
    body.append(clip(uid))
    sx, sy = 140 + 1.6 * Mf, fy + 90
    body.append(circle(sx, sy, (reach + walk) * Mf, C["amber_bg"], C["amber"], 1.2, "4,3"))
    body += footprint(sx - 0.24 * Mf, sy, Mf)
    body.append(circle(sx, sy, reach * Mf, "none", C["teal"], 1.2, "4,3"))
    body.append(circle(sx, sy, 4, C["teal"]))
    body += [text(sx - (reach + walk) * Mf + 6, fy + 16, f"ring {reach + walk:.2f} m: reach + walk", 9.5, C["amber"], 700), text(sx + 0.05 * Mf, sy - reach * Mf + 14, f"reach {reach:g} m", 9.5, C["teal"], 700)]
    body.append(rect(sx + 0.6 * Mf, sy - 0.9 * Mf, 0.5 * Mf, 1.8 * Mf, "#C9CDD1", "#7A8187", 2))
    body.append(text(sx + 0.85 * Mf, fy + 16, "shelf", 9, C["muted"], 600, "middle"))
    px0 = sx - (reach + walk) * Mf - 0.14 * Mf
    px1 = sx - reach * Mf - 0.14 * Mf
    body += person(px0, sy, Mf, C["amber"], label="person at t = 0") + person(px1, sy, Mf, C["amber"], ghost=True)
    body.append(line(px0 + 0.14 * Mf, sy, px1 - 0.14 * Mf, sy, C["amber"], 1.4, "6,4"))
    body.append(text((px0 + px1) / 2, sy + 0.14 * Mf + 14, f"walks {walk:.2f} m", 9.5, C["amber"], 600, "middle"))
    body.append("</g>")
    body.append(text(1092, fy + 208, "planning case: the arm reaches standstill as the person reaches the fingertip radius; no margin is added beyond Z", 10, C["teal"], 600, "end"))
    body.append(text(W - 32, H - 52, "Generated by assurance/03-system/figures/fig_s04.py from the WP-S-04 §1, §2 tables and §4.5", 9.5, C["dim"], anchor="end"))
    body += band(W, H, f"Drawn to WP-S-04 v0.2 planning values (t_r {t_r:g} s, arm stop {t_b:.2f} s assumed, reach {reach:g} m read from a description file). A loop diagram shows the arithmetic of a stop; it does not show that a measure works.")
    return svg(W, H, uid, f"Figure 2-{lp['n']}: {lp['title']}",
               f"Six boxes from the ring crossing through the station device, the logic, the safe-torque-off path, the arm's assumed stop and the standstill; a time axis to 0.6 s; a distance bar adding the {reach:g} m reach and the "
               f"{walk:.2f} m walk to the {reach + walk:.2f} m boundary; a top view of the station with the base, the reach circle, the ring, the shelf and the person at the ring and at the reach radius.", body)

  if lp["ledger"] == "keep-clear":
    kc = src["keep_clear"]
    ms_target, mm_lift = src["lift_stop"]
    walk_r = K * t_r
    t_b = 0.05
    walk_b = K * t_b
    body.append(text(28, 54, f"§2 row {lp['sf']}: {b['det']:g} + {b['logic']:g} + {b['power']:g} = {b['tr']:g} ms against the {b['target']:g} ms target, {lp['config']}; the lift brake's engagement time is unknown: drawn at {t_b:g} s. "
                     f"The lift moves at {src['lift_mm_s']:g} mm/s and travels {mm_lift:g} mm in the {ms_target:g} ms of SR-12.04; K = {K:g} m/s.", 11, C["muted"]))
    stages = [(lp["demand"][0], lp["demand"][1], "t = 0", "demand"), ("Keep-clear device", "safety mat or field", f"{b['det']:g} ms", "chain"),
              (logic_name, "logic", f"{b['logic']:g} ms", "chain"), ("Lift power", "actuator power removed", f"{b['power']:g} ms · t_r = {b['tr']:g} ms", "chain"),
              ("Lift brake", "engagement (TBC)", f"t_b = {t_b:g} s assumed", "tbc"), ("Standstill", f"t = {t_r + t_b:.2f} s", f"lift moved {src['lift_mm_s'] * (t_r + t_b):.1f} mm", "end")]
    body += stage_boxes(92, stages)
    phases = [(0, t_det, f"device {b['det']:g}", "chain"), (t_det, t_det + t_logic, f"logic {b['logic']:g}", "chain"), (t_det + t_logic, t_r, f"power {b['power']:g}", "chain"), (t_r, t_r + t_b, f"brake {t_b:g} s, TBC", "tbc")]
    marks = [(t_r, f"power removed, {t_r:.2f} s", C["red"]), (t_r + t_b, f"standstill {t_r + t_b:.2f} s (assumed)", C["green"]), (ms_target / 1000.0, f"target {ms_target:g} ms", C["dim"])]
    body += time_axis(uid, 222, 0.4, phases, marks)
    body += [text(28, 272, "Distance ledger: the keep-clear radius against the walk during the stop", 11.5, C["ink"], 700),
             text(28, 288, f"drawn to scale, 1 m = {M:.0f} px, from the zone's edge inward; the person walks at K for the whole stopping time", 10, C["muted"])]
    body.append(rect(120, 310, kc * M, 46, C["amber_bg"], C["amber"], 0, 1, "5,3"))
    body.append(text(120 + kc * M + 10, 337, f"keep-clear radius {kc:g} m (SR-12.03; assumed, not yet sized)", 9.5, C["amber"], 700))
    bar, xe = ledger_bar(uid, 318, M, 120, [(walk_r, "walk", f"t_r walk {walk_r:.2f}"), (walk_b, "hatch", f"brake {walk_b:.2f}")], f"walk {walk_r + walk_b:.2f} m: {walk_r:.2f} in t_r, {walk_b:.2f} during the brake")
    body += bar
    margin = kc - walk_r - walk_b
    body.append(rect(120 + (walk_r + walk_b) * M, 318, margin * M, 30, C["grey_bg"], C["line"], 0, 1))
    body.append(text(120 + (walk_r + walk_b + margin / 2) * M, 337, f"margin {margin:.2f} m", 10, C["muted"], 700, "middle"))
    body += [text(120, 384, f"A person stepping onto the zone's edge walks {walk_r:.2f} m before power is removed and {walk_b:.2f} m more while the brake engages ({t_b:g} s assumed): {walk_r + walk_b:.2f} m of the {kc:g} m radius, leaving {margin:.2f} m to the column.", 10, C["ink"]),
             text(120, 400, f"The lift itself moves {mm_lift:g} mm in the {ms_target:g} ms target: the zone's radius and the brake's time size the hazard, not the lift's speed (§4.5). The radius is the simulation track's assumption until SR-12.03's device is chosen.", 10, C["ink"])]
    fy = 436
    body += floor_strip(uid, fy, Mf, 120, 1092, f"The same numbers on the floor (1 m = {Mf:.0f} px): the lift column seen from above, a slice through the zone", h=180)
    body.append(clip(uid))
    sx, sy = 140 + 1.4 * Mf, fy + 90
    body.append(circle(sx, sy, kc * Mf, f"url(#{uid}-hatch)", C["amber"], 1.2))
    body += footprint(sx - 0.06 * Mf, sy, Mf)
    body.append(rect(sx - 0.12 * Mf, sy - 0.08 * Mf, 0.24 * Mf, 0.16 * Mf, "#F4F6F7", "#1B1F22", 1, 1.2))
    body.append(text(sx, sy + 3, "column", 8, C["ink"], 600, "middle"))
    body.append(text(sx - kc * Mf + 6, fy + 16, f"keep-clear {kc:g} m (assumed)", 9.5, C["amber"], 700))
    px0 = sx + kc * Mf + 0.14 * Mf
    px1 = px0 - (walk_r + walk_b) * Mf
    body += person(px0, sy, Mf, C["amber"], label="person at t = 0") + person(px1, sy, Mf, C["amber"], ghost=True)
    body.append(line(px0 - 0.14 * Mf, sy, px1 + 0.14 * Mf, sy, C["amber"], 1.4, "6,4"))
    body.append(text((px0 + px1) / 2, sy + 0.14 * Mf + 14, f"walks {walk_r + walk_b:.2f} m", 9.5, C["amber"], 600, "middle"))
    body.append("</g>")
    body.append(text(1092, fy + 208, f"planning case: {margin:.2f} m between the person and the column when the lift stops; the brake's time decides whether that holds", 10, C["teal"], 600, "end"))
    body.append(text(W - 32, H - 52, "Generated by assurance/03-system/figures/fig_s04.py from the WP-S-04 §1, §2 tables and §4.5", 9.5, C["dim"], anchor="end"))
    body += band(W, H, f"Drawn to WP-S-04 v0.2 planning values (t_r {t_r:g} s, lift brake {t_b:g} s assumed, keep-clear radius {kc:g} m assumed). A loop diagram shows the arithmetic of a stop; it does not show that a measure works.")
    return svg(W, H, uid, f"Figure 2-{lp['n']}: {lp['title']}",
               f"Six boxes from stepping onto the zone through the keep-clear device, the logic, the lift power, the brake's assumed engagement and the standstill; a time axis to 0.4 s with the {ms_target:g} ms target marked; "
               f"a distance bar of the {walk_r:.2f} m walked during the reaction and {walk_b:.2f} m during the brake inside the {kc:g} m radius, leaving {margin:.2f} m; a top view of the base, the column, the hatched keep-clear ring and the person at its edge and at standstill.", body)
  raise ValueError(lp["ledger"])


# ------------------------------------------------------------------------------------------------- the side elevation (§4.2)
# The vertical hazards the top views cannot show. Heights: WP-C-01 §4 (deck, scan planes, the 1.7 m envelope), WP-S-02
# SR-02.03 (the detection height), WP-S-04 §4.5 (reach, walk, lift); the upper body's documented dimensions as the
# Blender scene builds them (assurance/sim/blender/cfg002.py; the test checks the copies agree).
CFG002 = {"plate_top": 0.304, "column_retracted": 0.530, "column_foreaft": 0.240, "column_axis_x": 0.060, "profile": (0.120, 0.060, 0.340), "arm_mount_x": 0.240,
          "shoulder_z": 1.000, "lift_drawn": 0.35, "head_cam": (0.022, 0.223)}
ROBOT_H = 0.305   # the base's height from the CAD extent (blender README §4); the deck is 0.294 m (WP-C-01 §4)


def fig_elevation(src: dict) -> str:
  W, H = 1120, 700
  uid = "s04-4-2"
  M = 150.0
  K, t_r = src["K"], src["t_r"]
  planes, det_h, env, deck = src["planes"], src["detect_height"], src["envelope"], src["deck"]
  reach = src["reach"]
  walk = dict((t, d) for t, d in src["walk_terms"])[0.3]
  kc = src["keep_clear"]
  cf = CFG002
  body = [hatch_defs(uid), text(28, 34, "Figure 4-2  Side elevation: the vertical hazards the top views cannot show", 15, C["ink"], 700),
          text(28, 54, f"A: the scan plane against what is on the floor (SR-02.03, GAP-14, the C = 0 reading). B: the 2.0 manipulator's envelope, the arm workspace and the lift keep-clear (SR-11.02, SR-12.03). 1 m = {M:.0f} px in both.", 11, C["muted"])]
  # ---- panel A
  ax, ay, aw, ah = 28, 72, 520, 500
  floor = ay + 408
  body += [rect(ax, ay, aw, ah, C["panel"], C["stroke"], 6), text(ax + 16, ay + 22, "A  Scan plane height against what is on the floor", 12, C["ink"], 700)]
  Yz = lambda z: floor - z * M  # noqa: E731
  body.append(line(ax + 16, floor, ax + aw - 16, floor, C["ink"], 1.6))
  for z in (det_h, 1.0, 1.5, 2.0):
    body += [line(ax + 16, Yz(z), ax + aw - 16, Yz(z), C["stroke"], 1), text(ax + 18, Yz(z) - 3, f"{z:g} m", 9, C["dim"])]
  body.append(text(ax + 16, floor + 14, "floor", 9.5, C["muted"]))
  # the base in side view: ROBOT_L long, ROBOT_H high, front at bx1
  bx0 = ax + 62
  bx1 = bx0 + ROBOT_L * M
  body.append(rect(bx0, Yz(ROBOT_H), ROBOT_L * M, ROBOT_H * M, C["white"], C["ink"], 6, 1.4))
  body += [circle(bx0 + 0.25 * M, floor, 0.1 * M, C["ink"]), circle(bx1 - 0.12 * M, floor, 0.045 * M, C["dim"]),
           text((bx0 + bx1) / 2, Yz(ROBOT_H) - 8, f"MMP base, deck {deck:g} m", 9.5, C["muted"], anchor="middle"),
           text((bx0 + bx1) / 2, Yz(ROBOT_H) - 20, f"{ROBOT_H:g} m over all", 9.5, C["muted"], anchor="middle")]
  body.append(rect(bx1, Yz(det_h), ax + aw - 16 - bx1, det_h * M, C["red"], "none", 0, 1, "", ' opacity="0.06"'))
  body += [text(bx1 + 4, Yz(det_h) - 66, f"SR-02.03: detect from the floor to {det_h:g} m (TBC)", 9.5, C["red"], 700),
           text(bx1 + 4, Yz(det_h) - 54, "a plane alone cannot: a bumper or a second plane (§4.2)", 9.5, C["red"]),
           line(bx1 + 4, Yz(det_h) - 48, bx1 + 4, Yz(det_h) - 2, C["red"], 1), text(bx1 + 8, Yz(det_h) - 4, f"{det_h:g} m", 9, C["red"], 700)]
  body.append(line(bx1 - 0.08 * M, Yz(planes["S3"]), ax + aw - 16, Yz(planes["S3"]), C["teal"], 1.6, "6,3"))
  body.append(line(bx1 - 0.08 * M, Yz(planes["A1"]), ax + aw - 16, Yz(planes["A1"]), "#2FA69C", 1, "3,3"))
  lx = ax + aw - 20
  body += [text(lx, Yz(det_h) - 30, f"S3 plane {planes['S3']:g} m (2.0 base)", 9.5, C["teal"], 600, "end"), line(lx + 2, Yz(det_h) - 26, lx + 2, Yz(planes["S3"]), C["teal"], 1),
           text(lx, Yz(det_h) - 42, f"A1 plane {planes['A1']:g} m (Gate A unit)", 9.5, "#2FA69C", 600, "end"), line(lx + 7, Yz(det_h) - 38, lx + 7, Yz(planes["A1"]), "#2FA69C", 1)]
  objs = [(0.16, 0.40, 0.15, "0.15 m carton", "unseen", C["red"], 0), (0.70, 0.40, 0.30, f"{det_h:g} m carton", "seen", C["green"], 0), (1.20, 0.26, 0.12, "foot on the floor", "unseen", C["red"], 1)]
  for dx, w, h, name, verdict, col, row in objs:
    x = bx1 + dx * M
    body.append(rect(x, Yz(h), w * M, h * M, "#F0E4D2", col, 1 if h > 0.13 else 6, 1.2))
    body += [text(x + w * M / 2, floor + 24 + 26 * row, name, 9.5, col, anchor="middle"), text(x + w * M / 2, floor + 36 + 26 * row, verdict, 9.5, col, 700, "middle")]
  cx = bx1 + 1.72 * M
  body += [f'<ellipse cx="{cx:.1f}" cy="{Yz(0.14):.1f}" rx="{0.19 * M:.1f}" ry="{0.12 * M:.1f}" fill="#E9D5C3" stroke="{C["amber"]}" stroke-width="1.2"/>',
           circle(cx + 0.2 * M, Yz(0.22), 0.07 * M, "#E9D5C3", C["amber"], 1.2),
           text(cx + 0.08 * M, floor + 24, "crawling child", 9.5, C["amber"], anchor="middle"), text(cx + 0.08 * M, floor + 36, "marginal: head at the plane", 9.5, C["amber"], 700, "middle")]
  body += [text(ax + 16, ay + ah - 22, f"Heights: S3 174 + 17.5 + 30.55 mm (mechanical BOM); A1 {planes['A1']:g} m (WP-C-01 §4.2). The objects are the cases behind the C = 0 reading of §4.2;", 9, C["muted"]),
           text(ax + 16, ay + ah - 10, "the standing or walking person a mobile platform's field is sized for is detected at the legs. Nothing here is a measurement.", 9, C["muted"])]
  # ---- panel B
  bx, by, bw, bh = 568, 72, 524, 500
  body += [rect(bx, by, bw, bh, C["panel"], C["stroke"], 6), text(bx + 16, by + 22, f"B  CFG-002 envelope, arm workspace and lift keep-clear (lift extended {cf['lift_drawn']:g} m)", 12, C["ink"], 700)]
  body.append(line(bx + 16, floor, bx + bw - 16, floor, C["ink"], 1.6))
  for z in (0.5, 1.0, 1.5):
    body += [line(bx + 16, Yz(z), bx + bw - 16, Yz(z), C["stroke"], 1), text(bx + 18, Yz(z) - 3, f"{z:g} m", 9, C["dim"])]
  body.append(line(bx + 16, Yz(env), bx + bw - 16, Yz(env), C["red"], 1, "6,3"))
  body.append(text(bx + bw - 18, Yz(env) - 4, f"{env:g} m envelope (WP-C-01 §4)", 9, C["red"], 600, "end"))
  ox = bx + 60 + ROBOT_L / 2 * M       # base_link x on the sheet
  Xx = lambda x: ox + x * M  # noqa: E731
  body.append(rect(Xx(-ROBOT_L / 2), Yz(ROBOT_H), ROBOT_L * M, ROBOT_H * M, C["white"], C["ink"], 6, 1.4))
  body.append(circle(Xx(-0.14), floor, 0.1 * M, C["ink"]))
  col_top = cf["plate_top"] + cf["column_retracted"]
  body.append(rect(Xx(cf["column_axis_x"] - cf["column_foreaft"] / 2), Yz(col_top), cf["column_foreaft"] * M, cf["column_retracted"] * M, C["white"], C["ink"], 1, 1.2))
  body.append(rect(Xx(cf["column_axis_x"] - cf["column_foreaft"] / 2 + 0.02), Yz(col_top + cf["lift_drawn"]), (cf["column_foreaft"] - 0.04) * M, cf["lift_drawn"] * M, C["grey_bg"], C["ink"], 1, 1.2))
  ztop = col_top + cf["lift_drawn"]
  pw, pd, ph = cf["profile"]
  body.append(rect(Xx(cf["arm_mount_x"] - pw / 2), Yz(ztop + 0.010 + ph), pw * M, ph * M, C["white"], C["ink"], 1, 1.2))
  sz = cf["shoulder_z"] + cf["lift_drawn"]
  sX, sY = Xx(cf["arm_mount_x"]), Yz(sz)
  body.append(rect(sX - 0.015 * M + cf["head_cam"][0] * M, Yz(sz + cf["head_cam"][1] + 0.015), 0.03 * M, 0.03 * M, C["ink"], "none", 1))
  body.append(f'<path d="M {sX:.1f} {sY - reach * M:.1f} A {reach * M:.1f} {reach * M:.1f} 0 0 1 {sX + reach * M:.1f} {sY:.1f} A {reach * M:.1f} {reach * M:.1f} 0 0 1 {sX:.1f} {sY + reach * M:.1f}" fill="{C["teal_bg"]}" fill-opacity="0.6" stroke="{C["teal"]}" stroke-width="1.2" stroke-dasharray="4,3"/>')
  body += [line(sX, sY, sX + 0.36 * M, sY + 0.22 * M, C["ink"], 5, extra=' stroke-linecap="round"'), line(sX + 0.36 * M, sY + 0.22 * M, sX + 0.56 * M, sY + 0.02 * M, C["ink"], 4, extra=' stroke-linecap="round"'),
           circle(sX, sY, 4, C["teal"]), text(Xx(cf["arm_mount_x"] - pw / 2) - 6, sY - 6, f"shoulder {sz:.2f} m", 9.5, C["teal"], 600, "end"), text(Xx(cf["arm_mount_x"] - pw / 2) - 6, sY + 6, f"({cf['shoulder_z']:.2f} retracted)", 9.5, C["teal"], anchor="end"),
           text(sX + reach * M * 0.5, sY - reach * M - 6, f"reach {reach:g} m (planning value)", 9.5, C["teal"], 600)]
  wx = Xx(cf["arm_mount_x"] + reach + walk)
  body += [line(wx, floor, wx, Yz(1.45), C["amber"], 1.6, "6,3"), text(wx - 6, Yz(0.44), f"boundary {reach + walk:.2f} m", 9.5, C["amber"], 700, "end"),
           text(wx - 6, Yz(0.44) + 13, f"{reach:g} reach + {walk:.2f} walk (0.3 s; §4.5)", 9.5, C["amber"], anchor="end")]
  px = wx + 0.22 * M
  body += [circle(px, Yz(1.66), 0.08 * M, "#E9D5C3", C["ink"], 1), rect(px - 0.1 * M, Yz(1.56), 0.2 * M, 0.72 * M, "#5B8BD6", "none", 8),
           rect(px - 0.09 * M, Yz(0.86), 0.08 * M, 0.86 * M, "#4E4E52", "none", 1), rect(px + 0.01 * M, Yz(0.86), 0.08 * M, 0.86 * M, "#4E4E52", "none", 1),
           text(px, floor + 16, "person, 1.78 m", 9.5, C["muted"], anchor="middle")]
  body.append(rect(Xx(cf["column_axis_x"] - kc), floor, 2 * kc * M, 6, C["amber"], "none", 0, 1, "", ' opacity="0.6"'))
  body.append(text(Xx(cf["column_axis_x"]), floor + 28, f"lift keep-clear {kc:g} m each side of the column axis (SR-12.03; radius assumed)", 9.5, C["amber"], 600, "middle"))
  lx = Xx(cf["column_axis_x"] - cf["column_foreaft"] / 2 - 0.05)
  body += [line(lx, Yz(col_top), lx, Yz(ztop), C["green"], 1.2), text(lx - 4, Yz(0.66), f"lift {cf['lift_drawn']:g} m drawn", 9, C["green"], anchor="end"),
           text(lx - 4, Yz(0.66) + 12, f"{src['lift_mm_s']:g} mm/s", 9, C["green"], anchor="end")]
  body += [text(bx + 16, by + bh - 22, "Heights from upstream's general-arrangement page; the column section, carriage and brackets are drawn (supplier CAD not public).", 9, C["muted"]),
           text(bx + 16, by + bh - 10, "Reach from the OpenArm description's joint offsets; the arm's stopping time is TBC (WP-C-01 OI-6); the keep-clear radius is assumed.", 9, C["muted"])]
  body.append(text(W - 32, H - 52, "Generated by assurance/03-system/figures/fig_s04.py from WP-S-04 §1 and §4.5, WP-C-01 §4 and WP-S-02 SR-02.03", 9.5, C["dim"], anchor="end"))
  body += band(W, H, f"Drawn to WP-S-04 v0.2 planning values and documented dimensions; nothing measured (K = {K:g} m/s, t_r = {t_r:g} s). An elevation shows what a plane can and cannot see; it does not show that a measure works.")
  return svg(W, H, uid, "Figure 4-2: side elevation, the scan plane against low objects and the CFG-002 envelope, workspace and keep-clear",
             f"Two panels. A: the base in side view with the {planes['S3']:g} m and {planes['A1']:g} m scan planes drawn as dashed lines ahead of it over a translucent band up to the {det_h:g} m detection height; a 0.15 m carton, "
             f"a {det_h:g} m carton, a foot and a crawling child on the floor, each labelled seen, unseen or marginal. B: the 2.0 manipulator with the lift extended, the arm profile and head camera, a reaching arm, the {reach:g} m reach arc, "
             f"the {reach + walk:.2f} m workspace boundary as a vertical dashed line with a person standing at it, the {env:g} m envelope line and the {kc:g} m keep-clear bar on the floor.", body)


OUTPUTS = {"fig-s04-4-1-field-length-vs-speed.svg": fig_field, "fig-s04-4-2-side-elevation.svg": fig_elevation}
for _lp in LOOPS:
  OUTPUTS[f"fig-s04-2-{_lp['n']}-loop-{_lp['key']}.svg"] = (lambda src, lp=_lp: fig_loop(src, lp))


def check_source(src: dict) -> list[str]:
  errs = []
  if src["K"] is None or src["Z"] is None or src["t_r"] is None:
    return ["§1 K or Z, or the SF-02 scanner row of §2, could not be read"]
  K, Z, t_r = src["K"], src["Z"], src["t_r"]
  for b in src["budget"]:
    if None in (b["det"], b["logic"], b["power"], b["tr"]):
      errs.append(f"§2 {b['sf']} ({b['path'][:30]}): a stage or t_r has no number")
      continue
    if abs(b["det"] + b["logic"] + b["power"] - b["tr"]) > 0.5:
      errs.append(f"§2 {b['sf']} ({b['path'][:30]}): stages add to {b['det'] + b['logic'] + b['power']:g} ms, the row says {b['tr']:g}")
    if b["target"] is not None and b["tr"] > b["target"] + 2.5:
      errs.append(f"§2 {b['sf']} ({b['path'][:30]}): t_r {b['tr']:g} ms exceeds the target {b['target']:g} ms")
  if not src["fields"]:
    errs.append("§4.1 has no FS- or CK- rows")
  for f in src["fields"]:
    if None in (f["v"], f["a"], f["t_b"], f["d_s"], f["L"]):
      errs.append(f"§4.1 {f['id']}: a number is missing")
      continue
    t_b, d_s, L = model(f["v"], f["a"], t_r, K, Z)
    if abs(t_b - f["t_b"]) > 0.006:
      errs.append(f"§4.1 {f['id']}: t_b {f['t_b']:g} s, the formula gives {t_b:.2f}")
    if abs(d_s - f["d_s"]) > 0.0006:
      errs.append(f"§4.1 {f['id']}: d_s {f['d_s']:g} m, the formula gives {d_s:.3f}")
    if abs(L - f["L"]) > 0.006:
      errs.append(f"§4.1 {f['id']}: L {f['L']:g} m, the formula gives {L:.2f}")
  for r in src["stop_rows"]:
    if r["v"] is None:
      continue
    if r["d_r"] is not None and abs(r["v"] * t_r - r["d_r"]) > 0.0006:
      errs.append(f"§3.2 v = {r['v']:g}: d_r {r['d_r']:g}, the formula gives {r['v'] * t_r:.3f}")
    for case in r["cases"]:
      if case is None:
        continue
      a, t_b_doc, d_s_doc = case
      t_b, d_s, _ = model(r["v"], a, t_r, K, Z)
      if abs(t_b - t_b_doc) > 0.006 or abs(d_s - d_s_doc) > 0.0006:
        errs.append(f"§3.2 v = {r['v']:g}, a = {a:g}: table says t_b {t_b_doc:g}, d_s {d_s_doc:g}; the formula gives {t_b:.2f}, {d_s:.3f}")
  # the loop diagrams: every path row they draw exists, and the numbers the text states follow from the rows
  for lp in LOOPS:
    if budget_row(src, lp["sf"], lp["match"]) is None:
      errs.append(f"§2 has no {lp['sf']} row matching '{lp['match']}' (Figure 2-{lp['n']})")
    for fid in (lp.get("field"), lp.get("ceiling_row"), *lp.get("alts", ())):
      if fid and not any(f["id"] == fid for f in src["fields"]):
        errs.append(f"§4.1 has no row {fid} (Figure 2-{lp['n']})")
  if set(src["cases"]) != {"coast slow", "coast fast", "braked"}:
    errs.append("§3.1 does not name the three planning cases coast slow, coast fast and braked")
  b = budget_row(src, "SF-02", "bumper")
  if b and src["bumper_mm"] and src["cases"]:
    v = 0.05
    for a, mm in ((src["cases"]["coast slow"], src["bumper_mm"][0]), (src["cases"]["coast fast"], src["bumper_mm"][1])):
      d_s = v * b["tr"] / 1000.0 + v * v / (2 * a)
      if abs(round(d_s * 1000) - mm) > 0.5:
        errs.append(f"§4.3: {mm:g} mm at a = {a:g}, the bumper path (t_r {b['tr']:g} ms) at {v} m/s gives {d_s * 1000:.0f} mm")
  elif not src["bumper_mm"] or not src["overtravel_mm"]:
    errs.append("§4.3: the two stopping distances in mm or the overtravel range could not be read")
  a11 = budget_row(src, "SF-11", "station")
  if a11 and src["walk_terms"]:
    for t_total, d in src["walk_terms"]:
      if abs(K * t_total - d) > 0.006:
        errs.append(f"§4.5: the walk term {d:g} m at {t_total:g} s, K·t gives {K * t_total:.2f}")
    if not any(abs(t - 0.3) < 1e-9 for t, _ in src["walk_terms"]):
      errs.append("§4.5 states no walk term at 0.3 s (the case the figures draw)")
  else:
    errs.append("§4.5: the walk terms could not be read, or §2 has no SF-11 row")
  if src["lift_mm_s"] and src["lift_stop"]:
    ms, mm = src["lift_stop"]
    if abs(src["lift_mm_s"] * ms / 1000.0 - mm) > 0.05:
      errs.append(f"§4.5: the lift travels {mm:g} mm in {ms:g} ms, {src['lift_mm_s']:g} mm/s gives {src['lift_mm_s'] * ms / 1000.0:.1f}")
  else:
    errs.append("§4.5: the lift speed or its travel in the SR-12.04 time could not be read")
  for key in ("reach", "keep_clear", "ceiling", "trip_margin", "envelope", "deck", "detect_height"):
    if src.get(key) is None:
      errs.append(f"the source for '{key}' could not be read (see load_source)")
  if set(src["planes"]) != {"A1", "S3"}:
    errs.append("WP-C-01 §4: the two scan-plane heights could not be read")
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
    print(f"fig_s04: {len(OUTPUTS)} figures current; {len(src['budget'])} budget rows, {len(src['fields'])} field rows, §4.3 and §4.5 recomputed")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
