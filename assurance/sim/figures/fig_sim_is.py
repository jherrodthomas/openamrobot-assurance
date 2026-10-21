#!/usr/bin/env python3
"""Draw the 2D views of the hazard situations: the warehouse plan and one looping view per interaction scenario.

  fig-sim-plan.svg            the warehouse from above: the zones of WP-C-02 §2 mapped onto a typical floor, the robot
                              with every field set of WP-S-04 §4.1 at its planning length, the station rings of
                              WP-S-04 §4.5, the people of the interaction scenarios where they happen, hazard chips
                              with the PLr adopted in WP-C-03 §5
  fig-sim-is-01-anim.svg      IS-01 as a loop (SMIL, no script): a fixed crop of the same plan; the robot at the zone
                              speed with the field set that applies drawn as the sum of its terms; the person at K;
                              the field outline changing at the demand and at power removal; events, time strip and
                              the person-to-robot distance with a cursor. A still viewer shows the first frame

The sources of record are the tables: WP-C-06 §2 (scenarios) and §3 (K, Z); WP-S-04 §2 (the stage times of the
scanner path), §3.1 (the planning decelerations) and §4.1 (the field sets, recomputed here from
L = v·t_r + v²/(2a) + K·(t_r + v/a) + Z + C with C = 0); WP-C-02 §2 (zones, people class, speed); WP-C-03 §5
(the PLr adopted per rated row). The plan geometry and the scene of each loop are listed here (SITE, SCENES) and
checked against the scenario IDs. `--check` fails when a source row is gone, a §4.1 row disagrees with the
formula, or a committed SVG is stale.

Pictures only, synthetic, no evidence credit: every view carries the band. The motion is kinematic from the
planning values; the coast is unmeasured until WP-V-02 (assurance/sim/ideas-2d-views.md §7).

    python3 fig_sim_is.py            # regenerate
    python3 fig_sim_is.py --check    # fail if the sources changed or an SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WP_C06 = ROOT / "assurance" / "02-concept" / "WP-C-06-human-robot-interaction-and-misuse.md"
WP_C02 = ROOT / "assurance" / "02-concept" / "WP-C-02-operating-environment-and-tasks.md"
WP_C03 = ROOT / "assurance" / "02-concept" / "WP-C-03-risk-assessment.md"
WP_S04 = ROOT / "assurance" / "03-system" / "WP-S-04-response-time-and-stopping-budget.md"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "stroke": "#D3DDE2", "line": "#7E949B", "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#B86F0C", "amber_bg": "#FFF6E8", "teal": "#00938B", "teal_bg": "#E9F7F5", "red": "#D64535", "red_bg": "#FDEDEB",
  "green": "#2C9A58", "green_bg": "#E8F6EC", "grey_bg": "#EDF2F4", "blue": "#2F6DB5", "blue_bg": "#EAF1FA",
  # the floor vocabulary
  "floor": "#D7DADD", "rack": "#5F666C", "rack2": "#7A8187", "wall": "#3B4045", "lane": "#FFFFFF", "vest": "#F28C28", "skin": "#5B3A1E",
  "tape": "#F2C01E", "pallet": "#C9A06A", "pallet2": "#A77E4A", "carton": "#E2C79B", "carton2": "#8C6B3F",
}
BAND = "SYNTHETIC: pictures only, no evidence credit"


# ------------------------------------------------------------------------------------------------------ sources
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
  c06 = WP_C06.read_text(encoding="utf-8")
  scenes = {r[0]: {"who": _clean(r[1]), "zone": _clean(r[2]), "task": _clean(r[3]), "doing": _clean(r[4]), "closest": _clean(r[5]),
                   "hazard": _clean(r[7]), "measure": _clean(r[8])} for r in _table(c06, "## 2. Interaction scenarios")}
  params = {r[0]: _num(r[2]) for r in _table(c06, "## 3. Approach speeds and safety distances")}
  s04 = WP_S04.read_text(encoding="utf-8")
  conv = {r[0]: r for r in _table(s04, "## 1. Purpose, inputs and conventions")}
  budget = []
  for r in _table(s04, "## 2. Response time budget per safety function"):
    budget.append({"sf": r[0], "path": _clean(r[1]), "det": _num(r[2]), "logic": _num(r[3]), "power": _num(r[4]), "t_r": _num(r[6])})
  fields = {}
  for r in _table(s04, "### 4.1 Field length per field set"):
    if re.match(r"(FS|CK)-\d", r[0]):
      fields[r[0]] = {"set": _clean(r[1]), "v": _num(r[2]), "case": _clean(r[3]), "a": _num(r[4]), "t_b": _num(r[5]), "d_s": _num(r[6]),
                      "L": _num(r[7]), "config": _clean(r[8])}
  c02 = WP_C02.read_text(encoding="utf-8")
  zones = {r[0]: {"name": _clean(r[1]), "people": _clean(r[5]), "speed": _clean(r[6])} for r in _table(c02, "## 2. Zones")}
  c03 = WP_C03.read_text(encoding="utf-8")
  ratings = []
  for r in _table(c03, "## 5. Risk estimation"):
    head = _clean(r[0])
    ratings.append({"row": head, "hazard": head.split(" ")[0], "scenes": re.findall(r"IS-\d\d", head), "plr": _clean(r[7]).split(" ")[0]})
  return {"scenes": scenes, "K": params.get("K"), "Z": params.get("Z"), "K_s04": _num(conv["K"][1]) if "K" in conv else None,
          "Z_s04": _num(conv["Z"][1]) if "Z" in conv else None, "budget": budget, "fields": fields, "zones": zones, "ratings": ratings}


def model(v: float, a: float, t_r: float, K: float, Z: float) -> tuple[float, float, float]:
  t_b = v / a
  d_s = v * t_r + v * v / (2 * a)
  return t_b, d_s, d_s + K * (t_r + t_b) + Z


def scanner_path(src: dict) -> dict:
  return next(b for b in src["budget"] if b["sf"] == "SF-02" and "scanner" in b["path"])


def rating_for(src: dict, sid: str) -> dict | None:
  return next((r for r in src["ratings"] if sid in r["scenes"]), None)


def check_source(src: dict) -> list[str]:
  errs = []
  for sid in SCENES:
    if sid not in src["scenes"]:
      errs.append(f"WP-C-06 §2 has no row {sid}")
  if src["K"] is None or src["Z"] is None:
    errs.append("WP-C-06 §3: K or Z missing")
  if src["K_s04"] != src["K"] or src["Z_s04"] != src["Z"]:
    errs.append("K or Z differ between WP-C-06 §3 and WP-S-04 §1")
  try:
    sp = scanner_path(src)
    if sp["t_r"] is None or sp["det"] is None:
      errs.append("WP-S-04 §2: the SF-02 scanner row has no t_r or detection time")
  except StopIteration:
    errs.append("WP-S-04 §2: no SF-02 scanner row")
    return errs
  t_r = sp["t_r"] / 1000.0
  for fid in PLAN_FIELDS + [sc["field"] for sc in SCENES.values()]:
    f = src["fields"].get(fid)
    if not f:
      errs.append(f"WP-S-04 §4.1 has no row {fid}")
      continue
    t_b, d_s, L = model(f["v"], f["a"], t_r, src["K"], src["Z"])
    if abs(L - f["L"]) > 0.011:
      errs.append(f"WP-S-04 §4.1 {fid}: L {f['L']:g} m, the formula gives {L:.2f}")
  for zid in ("Z1", "Z2", "Z3", "Z4", "Z5"):
    if zid not in src["zones"]:
      errs.append(f"WP-C-02 §2 has no row {zid}")
  for sid in SCENES:
    if rating_for(src, sid) is None:
      errs.append(f"WP-C-03 §5 has no rated row naming {sid}")
  return errs


# ------------------------------------------------------------------------------------------------------ the site
# A fictional but typical floor, in metres, origin bottom-left, 24 × 15 m. Sizes WP-C-02 §2 states are kept (the
# dock lane is the 2 m pre-dock approach plus the robot's length; aisles are wider than footprint + 2 × 0.5 m);
# the rest is ordinary. Replaced by the surveyed site when WP-O-01 records one (ideas-2d-views.md OI-3).
SITE = {
  "size": (24.0, 15.0),
  "office": (0.6, 11.8, 4.2, 2.6),            # Z5, excluded
  "visitor": (0.6, 10.8, 4.2, 0.9),           # Z5, excluded
  "test_area": (0.6, 0.4, 5.4, 5.0),          # Z1
  "racks": [(7.0, 12.0, 9.6, 0.8), (7.0, 9.5, 9.6, 0.8), (7.0, 6.4, 9.6, 0.8)],
  "lanes": [((6.2, 13.9), (6.2, 1.0)), ((17.2, 13.9), (17.2, 9.0)), ((6.2, 13.9), (17.2, 13.9)), ((6.2, 1.0), (17.2, 1.0)),
            ((6.2, 11.15), (17.2, 11.15)), ((6.2, 8.35), (17.2, 8.35)), ((6.2, 5.9), (17.2, 5.9))],
  "pallets": [(7.2, 1.3, 2), (8.6, 1.3, 3), (15.0, 1.3, 2), (10.4, 14.0, 3), (12.0, 14.0, 2)],
  "drums": [(14.6, 14.5), (15.3, 14.5), (14.6, 13.8)],
  "cart": (13.4, 1.6, 1.0, 0.6),
  "dock_lane": (17.6, 12.6, 5.8, 1.2),        # Z3
  "dock": (22.9, 12.9, 0.4, 0.6),
  "charge_bay": (17.6, 10.7, 5.8, 1.4),       # Z4
  "charger": (22.7, 10.95, 0.5, 0.7),
  "loading_dock": (17.5, 0.0, 6.0, 4.4),      # Z0
  "trucks": [(18.2, 0.4, 1.6, 3.6, "#C8382E"), (20.6, 0.4, 1.6, 3.6, "#8E9AA2")],
  "station": {"mark": (11.4, 9.0, 2.4, 0.5), "centre": (12.6, 8.5), "robot": (12.6, 8.0)},
  "aisle_robot": (7.6, 8.35),                  # the live robot, aisle 2, heading +x
  "aisle1_robot": (14.0, 11.1),               # the carry-pose ghost, aisle 1
  "dock_robot": (20.8, 13.2),                 # the docking ghost, heading −x, reverse path behind it
}
PLAN_FIELDS = ["FS-1a", "FS-1b", "FS-1c", "FS-2a", "FS-2b", "FS-2c", "FS-3b", "FS-4"]
ROBOT_L, ROBOT_W = 0.78, 0.58                # WP-C-01 §4: 780 × 582 mm chassis
REACH, WALK_ARM, KEEP_CLEAR = 0.6, 0.48, 0.55  # WP-S-04 §4.5 planning values; SR-12.03 keep-clear as the Blender scenes assume it

# The scene of each loop: the crop of the plan (x, y, w, h in metres), the robot's start and heading, the field set
# that applies, the person's path (start relative to the field's far edge and its lateral edge at t = 0, direction),
# the time window. The numbers that move come from the tables.
SCENES = {
  "IS-01": dict(crop=(6.4, 6.3, 6.0, 3.6), robot=(7.3, 8.35, 1), field="FS-1b",
                person=dict(x_from_edge=-0.30, side=+1, dir=(0, -1)), t0=-0.4, t_after=0.33, hold=1.5,
                title="a person crosses the aisle ahead at walking pace"),
}


# ------------------------------------------------------------------------------------------------------ drawing
def text(x, y, s, size=12, fill=C["ink"], weight=400, anchor="start", family=FONT, extra=""):
  return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
          f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def rect(x, y, w, h, fill, stroke="none", r=0, sw=1, dash="", extra=""):
  d = f' stroke-dasharray="{dash}"' if dash else ""
  return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} {extra}/>'


def line(x1, y1, x2, y2, stroke, sw=1.2, dash="", arrow=False, extra=""):
  d = f' stroke-dasharray="{dash}"' if dash else ""
  a = ' marker-end="url(#arrow)"' if arrow else ""
  return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{d}{a} {extra}/>'


def circle(cx, cy, r, fill, stroke="none", sw=1, dash="", extra=""):
  d = f' stroke-dasharray="{dash}"' if dash else ""
  return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} {extra}/>'


def defs(uid: str) -> str:
  return (f'<defs><marker id="{uid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{C["ink"]}"/></marker>'
          f'<pattern id="{uid}-hz" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          f'<rect width="10" height="10" fill="{C["tape"]}"/><rect width="5" height="10" fill="#222222"/></pattern>'
          f'<pattern id="{uid}-hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          f'<line x1="0" y1="0" x2="0" y2="8" stroke="{C["amber"]}" stroke-width="1.2" opacity="0.6"/></pattern>'
          f'<pattern id="{uid}-hatchred" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          f'<line x1="0" y1="0" x2="0" y2="8" stroke="{C["red"]}" stroke-width="1.2" opacity="0.5"/></pattern>'
          f'<pattern id="{uid}-pallet" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="{C["pallet"]}"/>'
          f'<rect x="0" y="4" width="14" height="2" fill="{C["pallet2"]}"/><rect x="0" y="10" width="14" height="2" fill="{C["pallet2"]}"/></pattern></defs>')


def svg(w, h, uid, title, desc, body):
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
          f'<title id="{uid}-t">{escape(title)}</title>\n<desc id="{uid}-d">{escape(desc)}</desc>\n' + defs(uid) + "\n"
          f'<rect x="0" y="0" width="{w}" height="{h}" fill="{C["bg"]}"/>\n' + "\n".join(body) + "\n</svg>\n")


def band(w, h, note):
  return [rect(0, h - 44, w, 44, C["amber_bg"]), text(16, h - 26, BAND, 11, C["amber"], 700, family=MONO), text(16, h - 11, note, 10, C["amber"])]


class Plan:
  """The site in a pixel frame: P maps metres to pixels, M is pixels per metre, uid prefixes the pattern ids."""

  def __init__(self, px, py, M, uid, origin=(0.0, 0.0), height=None):
    self.px, self.py, self.M, self.uid = px, py, M, uid
    self.ox, self.oy = origin
    self.h = height if height is not None else SITE["size"][1]

  def P(self, xm, ym):
    return self.px + (xm - self.ox) * self.M, self.py + (self.h - (ym - self.oy)) * self.M

  def R(self, x, y, w, h, fill, stroke="none", r=0, sw=1, dash="", extra=""):
    X, Y = self.P(x, y + h)
    return rect(X, Y, w * self.M, h * self.M, fill, stroke, r, sw, dash, extra)

  def rack(self, x, y, w, h, label=""):
    M = self.M
    X, Y = self.P(x, y + h)
    out = [rect(X - 3, Y - 3, w * M + 6, h * M + 6, f"url(#{self.uid}-hz)"), rect(X, Y, w * M, h * M, C["rack"])]
    bay = 1.2
    for i in range(int(w / bay)):
      out.append(rect(X + i * bay * M + 3, Y + 3, bay * M - 6, h * M - 6, C["rack2"]))
    if label:
      out.append(text(X + 8, Y + h * M / 2 + 4, label, max(9, M / 5.2), "#E8EBED", 700))
    return out

  def pallet(self, x, y, boxes):
    M = self.M
    X, Y = self.P(x, y + 1.0)
    out = [rect(X, Y, 1.2 * M, 1.0 * M, f"url(#{self.uid}-pallet)", C["carton2"], 2)]
    for i in range(boxes):
      out.append(rect(X + 6 + i * 0.5 * M, Y + 6, 0.45 * M, 0.85 * M, C["carton"], C["carton2"], 2))
    return out

  def drum(self, x, y):
    X, Y = self.P(x, y)
    return [circle(X, Y, 0.3 * self.M, C["tape"], "#9A7A05", 1.5), circle(X, Y, 0.12 * self.M, "#9A7A05")]

  def worker(self, x, y, vest=None, label="", color=None):
    M = self.M
    X, Y = self.P(x, y)
    out = [f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="{0.28 * M:.1f}" ry="{0.14 * M:.1f}" fill="{vest or C["vest"]}" stroke="#2B2B2B" stroke-width="1.2"/>',
           circle(X, Y, 0.1 * M, C["skin"], "#2B2B2B", 1)]
    if label:
      out.append(text(X + 0.35 * M, Y + 4, label, min(11, max(9.5, M / 5.2)), color or C["ink"], 700))
    return out

  def lane(self, a, b):
    X1, Y1 = self.P(*a)
    X2, Y2 = self.P(*b)
    return [line(X1, Y1, X2, Y2, C["lane"], 2.5, "10,7")]

  def sprite(self, x, y, heading=1, opacity=1.0):
    """A drawn footprint of the base (WP-C-01 §4: 780 × 582 mm): deck, bumper ends, drive wheels, castors, the
    scanner at the front, the rear bumper edge red. Replaced by the top-down CAD render when it exists (OI-4)."""
    M = self.M
    cx, cy = self.P(x, y)
    rl, rw = ROBOT_L * M, ROBOT_W * M
    g = [f'<g opacity="{opacity}" transform="translate({cx:.1f},{cy:.1f}) scale({heading},1)">',
         rect(-rl / 2, -rw / 2, rl, rw, "#F4F6F7", "#1B1F22", 0.07 * M, 2)]
    for sx in (-rl / 2, rl / 2 - 0.05 * M):
      g.append(rect(sx, -rw / 2, 0.05 * M, rw, "#1B1F22", "none", 0.03 * M))
    for sy in (-rw / 2 - 0.03 * M, rw / 2 - 0.03 * M):
      g.append(rect(-0.2 * M, sy, 0.2 * M, 0.06 * M, "#15181A", "#2F3A44", 2))
    for (qx, qy) in ((-0.25 * M, 0.0), (0.27 * M, -0.19 * M), (0.27 * M, 0.19 * M)):
      g.append(circle(qx, qy, 0.05 * M, "#9AA3AB", C["blue"], 1))
    g.append(circle(rl / 2 - 0.1 * M, 0, 0.035 * M, C["teal"]))
    g.append(rect(-rl / 2 - 0.045 * M, -rw / 2 + 0.02 * M, 0.04 * M, rw - 0.04 * M, C["red"], "none", 2))
    g.append("</g>")
    return g

  def chip(self, x, y, hz, rating, col):
    X, Y = self.P(x, y)
    return [rect(X, Y - 12, 126, 20, C["bg"], col, 10, 1.4), text(X + 8, Y + 2, hz, 9.5, col, 700, family=MONO),
            text(X + 120, Y + 2, rating, 9.5, col, 700, "end", family=MONO)]

  def floor(self, src: dict, with_labels=True):
    """Everything static: walls, blocks, racks, lanes, props, the zone labels."""
    S, M, uid = SITE, self.M, self.uid
    z = src["zones"]
    out = []
    # office and visitor route: Z5, excluded
    x, y, w, h = S["office"]
    out += [self.R(x, y, w, h, C["tape"], C["wall"], 0, 3), self.R(x, y, w, h, f"url(#{uid}-hatchred)")]
    X, Y = self.P(x, y + h)
    if with_labels:
      out += [text(X + 10, Y + 22, "OFFICE", 13, C["wall"], 800), text(X + 10, Y + 40, f"Z5 {z['Z5']['name'].split(' (')[0].lower()}: excluded (DQ-019)", 10, C["red"], 700)]
    x, y, w, h = S["visitor"]
    out.append(self.R(x, y, w, h, f"url(#{uid}-hatchred)", C["red"], 0, 1, "4,3"))
    X, Y = self.P(x, y + h)
    if with_labels:
      out.append(text(X + 10, Y + 0.6 * M, "visitor route (Z5)", 9.5, C["red"], 700))
    # loading dock: Z0, excluded
    x, y, w, h = S["loading_dock"]
    out += [self.R(x, y, w, h, C["wall"])]
    X, Y = self.P(x, y + h)
    out.append(rect(X - 3, Y - 3, w * M + 6, 3, f"url(#{uid}-hz)"))
    for (tx, ty, tw, th, col) in S["trucks"]:
      out += [self.R(tx, ty, tw, th, col, "#4A5B6C", 6, 2), self.R(tx + 0.2, ty - 0.1, tw - 0.4, 0.9, "#9FB3C8", "#4A5B6C", 6, 2)]
    if with_labels:
      out.append(text(X + 10, Y - 8, "LOADING DOCK: Z0 excluded (dock edge, WP-C-02 §5)", 9.5, C["tape"], 700))
    # Z1 test area, taped
    x, y, w, h = S["test_area"]
    out.append(self.R(x, y, w, h, "#E6EFE8", C["green"], 0, 2.5, "8,5"))
    X, Y = self.P(x, y + h)
    out.append(rect(X - 3, Y - 3, w * M + 6, 3, f"url(#{uid}-hz)"))
    if with_labels:
      out += [text(X + 8, Y + 18, "Z1 TEST AREA", 11, C["green"], 800),
              text(X + 8, Y + 32, f"{_short(z['Z1']['people'])} · {_speed(z['Z1']['speed'])} · FS-1 · the operator holds the pendant outside the path", 9.5, C["muted"])]
    out += [self.R(1.5, 1.6, 0.6, 0.6, C["carton"], C["carton2"], 2), self.R(3.6, 0.9, 0.6, 0.3, C["carton"], C["carton2"], 2)]
    out += self.worker(4.9, 3.6, C["blue"], "operator" if with_labels else "")
    # racks and lanes: Z2
    for i, (x, y, w, h) in enumerate(S["racks"]):
      out += self.rack(x, y, w, h, f"RACK {i + 1}" if with_labels else "")
    for a, b in S["lanes"]:
      out += self.lane(a, b)
    if with_labels:
      X, Y = self.P(6.4, 13.4)
      out.append(text(X, Y, f"Z2 TRANSPORT AISLES · {_short(z['Z2']['people'])} · {_speed(z['Z2']['speed'])}, 0.30 ceiling with a person and detection · FS-1 / FS-3", 10.5, C["teal"], 800))
    for (x, y, n) in S["pallets"]:
      out += self.pallet(x, y, n)
    for (x, y) in S["drums"]:
      out += self.drum(x, y)
    x, y, w, h = S["cart"]
    out.append(self.R(x, y, w, h, "#C9CDD1", C["rack2"], 2))
    # Z3 dock lane and the robot's dock; Z4 charging bay and the charger
    x, y, w, h = S["dock_lane"]
    out.append(self.R(x, y, w, h, "#DCE8F5", C["blue"], 0, 2, "6,4"))
    X, Y = self.P(x, y + h)
    if with_labels:
      out.append(text(X + 8, Y - 6, f"Z3 DOCK LANE · {_short(z['Z3']['people'])} · {_speed(z['Z3']['speed'])} · FS-2 · reverse only", 9.5, C["blue"], 800))
    out.append(self.R(*S["dock"], C["blue"], "#1E4A80", 2, 1.5))
    if with_labels:
      X, Y = self.P(22.0, 12.3)
      out.append(text(X, Y, "robot dock, tags", 9, C["blue"], 700))
    x, y, w, h = S["charge_bay"]
    out.append(self.R(x, y, w, h, "#FFF1D6", C["amber"], 0, 2))
    X, Y = self.P(x, y + h)
    out.append(rect(X - 3, Y - 3, w * M + 6, 3, f"url(#{uid}-hz)"))
    if with_labels:
      out.append(text(X + 8, Y + 16, f"Z4 CHARGING BAY · {_short(z['Z4']['people'])} · 0 m/s · chain open", 9.5, C["amber"], 800))
    out.append(self.R(*S["charger"], C["tape"], "#9A7A05", 2, 1.5))
    # the station bay on rack 2 with the workspace ring and the lift keep-clear
    out.append(self.R(*S["station"]["mark"], C["tape"], "none", 0, 1, "", 'opacity="0.6"'))
    X, Y = self.P(*S["station"]["centre"])
    out.append(circle(X, Y, (REACH + WALK_ARM) * M, C["amber"], C["amber"], 1.2, "4,3", 'fill-opacity="0.12"'))
    rx, ry = self.P(*S["station"]["robot"])
    out.append(circle(rx, ry, KEEP_CLEAR * M, f"url(#{uid}-hatch)", C["amber"], 1))
    if with_labels:
      out.append(text(X + (REACH + WALK_ARM) * M + 6, Y - 0.6 * M, f"station: workspace {REACH + WALK_ARM:.1f} m (reach {REACH:g} + walk {WALK_ARM:g}, planning), keep-clear {KEEP_CLEAR:g} m", 9, C["amber"], 700))
    return out


def _short(people: str) -> str:
  s = re.split(r"[;:(,]", people)[0].strip()
  words = s.split()
  return "none" if words and words[0] == "none" else " ".join(words[:2])


def _speed(cell: str) -> str:
  m = re.search(r"\d+\.\d+ m/s", cell)
  return m.group(0) if m else "0 m/s"


# ------------------------------------------------------------------------------------------------------ the plan
def fig_plan(src: dict) -> str:
  W, H = 1400, 1000
  M = 52.0
  uid = "sim-plan"
  pl = Plan(40, 92, M, uid)
  F = src["fields"]
  sw, sh = SITE["size"]
  body = [text(40, 36, "The warehouse from above: the zones of WP-C-02 §2 on a typical floor, the robot with every field set of WP-S-04 §4.1, the situations where they happen", 18, C["ink"], 700),
          text(40, 60, "A fictional but typical site drawn by the generator; the zones, people classes, speeds, field lengths, rings and ratings are read from the tables. Field sets are nested at their planning lengths on the robot where each applies.", 11.5, C["muted"]),
          rect(40, 92, sw * M, sh * M, C["floor"], C["wall"], 0, 4)]
  body += pl.floor(src)
  # the live robot in aisle 2 with the FS-1 trio, the carry ghost in aisle 1 with FS-3b and FS-4, the docking ghost with the FS-2 trio
  def nested(x, y, heading, ids, cols):
    out = []
    for fid, col in zip(ids, cols):
      L = F[fid]["L"]
      if heading > 0:
        out.append(pl.R(x + ROBOT_L / 2, y - ROBOT_W / 2 - 0.10, L, ROBOT_W + 0.20, col, col, 0, 1.2, "5,3", 'fill-opacity="0.16"'))
      else:
        out.append(pl.R(x - ROBOT_L / 2 - L, y - ROBOT_W / 2 - 0.10, L, ROBOT_W + 0.20, col, col, 0, 1.2, "5,3", 'fill-opacity="0.16"'))
    return out
  ax, ay = SITE["aisle_robot"]
  body += nested(ax, ay, 1, ["FS-1a", "FS-1b", "FS-1c"], [C["amber"], C["teal"], C["green"]])
  body += pl.sprite(ax, ay, 1)
  X, Y = pl.P(ax + ROBOT_L / 2 + 0.05, ay - ROBOT_W / 2 - 0.1 - 0.17)
  for i, (fid, col) in enumerate((("FS-1a", C["amber"]), ("FS-1b", C["teal"]), ("FS-1c", C["green"]))):
    body.append(text(X, Y + i * 12, f"{fid} {F[fid]['L']:.2f} m ({F[fid]['case']}, {F[fid]['config']})", 9.5, col, 700))
  bx, by = SITE["aisle1_robot"]
  body += nested(bx, by, 1, ["FS-3b", "FS-4"], [C["amber"], C["blue"]])
  body += pl.sprite(bx, by, 1, 0.35)
  X, Y = pl.P(bx - ROBOT_L / 2, by + ROBOT_W / 2 + 0.42)
  body += [text(X, Y, f"FS-4 {F['FS-4']['L']:.2f} m (carry, {F['FS-4']['config']})", 9.5, C["blue"], 700),
           text(X, Y + 13, f"FS-3b {F['FS-3b']['L']:.2f} m (0.30 m/s with a person, {F['FS-3b']['case']})", 9.5, C["amber"], 700)]
  dx, dy = SITE["dock_robot"]
  body += nested(dx, dy, -1, ["FS-2a", "FS-2b", "FS-2c"], [C["amber"], C["blue"], C["green"]])
  body.append(pl.R(dx + ROBOT_L / 2, dy - ROBOT_W / 2, 0.7, ROBOT_W, f"url(#{uid}-hatchred)", C["red"], 0, 1))
  body += pl.sprite(dx, dy, -1, 0.35)
  X, Y = pl.P(SITE["dock_lane"][0] + 0.1, SITE["dock_lane"][1] + 0.12)
  body.append(text(X, Y, f"FS-2 crawl {F['FS-2a']['L']:.2f} / {F['FS-2b']['L']:.2f} / {F['FS-2c']['L']:.2f} m", 9, C["blue"], 700))
  X, Y = pl.P(SITE["dock_lane"][0] + SITE["dock_lane"][2] - 0.1, SITE["dock_lane"][1] + 0.12)
  body.append(text(X, Y, "reverse 0.7 m: bumper only, 0.05 m/s", 9, C["red"], 700, "end"))
  # the people of the situations and the hazard chips
  def chip_for(sid, x, y, col):
    r = rating_for(src, sid)
    return pl.chip(x, y, f"{r['hazard']} {sid}", f"PLr {r['plr']}", col)
  body += pl.worker(9.1, 9.1, None, "IS-01 crosses")
  X1, Y1 = pl.P(9.1, 8.85)
  body.append(line(X1, Y1, X1, Y1 + 1.0 * M, C["ink"], 1.4, "4,3", True).replace("url(#arrow)", f"url(#{uid}-arrow)"))
  body += chip_for("IS-01", 6.3, 9.3, C["teal"])
  body += pl.worker(6.4, 6.1, None, "IS-02 steps out at the rack end")
  body += chip_for("IS-02", 6.4, 5.4, C["red"])
  body += pl.worker(13.6, 8.1, None, "IS-13 reaches in")
  body += chip_for("IS-13", 15.3, 8.05, C["amber"])
  body += pl.worker(19.6, 13.2, None, "IS-04 behind")
  body += chip_for("IS-04", 21.3, 14.45, C["blue"])
  body += pl.worker(9.0, 3.2) + pl.worker(15.8, 11.0, C["blue"]) + pl.worker(4.0, 11.25, "#9AA3AB")
  ly = 92 + sh * M + 16
  body += [text(40, ly + 12, "Zones are WP-C-02 §2's; the loading dock, office and visitor route show what Z0 and Z5 look like on a real floor. Workers in vests are briefed staff, blue is the technician, grey a visitor. Chips: hazard, scenario, PLr adopted (WP-C-03 §5).", 10.5, C["muted"]),
           text(40, ly + 28, "Robot footprint 0.78 × 0.58 m (WP-C-01 §4), drawn; replaced by the top-down CAD render when it exists. Field lengths: WP-S-04 §4.1 planning values, C = 0; the coast is unmeasured (WP-V-02).", 10.5, C["muted"]),
           text(W - 32, ly + 28, "Generated by assurance/sim/figures/fig_sim_is.py", 9.5, C["dim"], anchor="end")]
  body += band(W, H, "Drawn to WP-S-04 v0.1 planning values; the coast is unmeasured (WP-V-02). A plan shows where the situations are; it does not show that a measure works.")
  return svg(W, H, uid, "The warehouse from above with the zones, the field sets and the situations",
             "A typical warehouse floor seen from above: the office and visitor route as Z5 excluded, a taped test area Z1, three rack rows with dashed aisle lanes as Z2, a dock lane Z3 with the robot's dock, a charging bay Z4, a truck loading dock as Z0 excluded; the robot in an aisle with the three FS-1 field lengths nested ahead of it, a carry ghost with FS-3 and FS-4, a docking ghost with the FS-2 lengths and the blind reverse path; a station bay with the workspace ring and lift keep-clear; the people of IS-01, IS-02, IS-04 and IS-13 where they happen, with hazard chips.", body)


# ------------------------------------------------------------------------------------------------------ the loops
def kinematics(src: dict, fid: str):
  f = src["fields"][fid]
  sp = scanner_path(src)
  t_r = sp["t_r"] / 1000.0
  t_b, d_s, L = model(f["v"], f["a"], t_r, src["K"], src["Z"])
  return {"v": f["v"], "a": f["a"], "t_r": t_r, "t_b": t_b, "t_s": t_r + t_b, "d_r": f["v"] * t_r, "d_b": f["v"] ** 2 / (2 * f["a"]),
          "walk": src["K"] * (t_r + t_b), "Z": src["Z"], "L": L, "K": src["K"], "t_det": sp["det"] / 1000.0, "t_logic": (sp["det"] + sp["logic"]) / 1000.0}


def robot_travel(k: dict, t: float, t0: float) -> float:
  """Distance travelled since t0: constant speed until t_r, then the coast, then standstill."""
  if t <= k["t_r"]:
    return k["v"] * (t - t0)
  if t <= k["t_s"]:
    return k["v"] * (k["t_r"] - t0) + k["v"] * (t - k["t_r"]) - 0.5 * k["a"] * (t - k["t_r"]) ** 2
  return k["v"] * (k["t_r"] - t0) + k["d_b"]


def fig_loop(src: dict, sid: str) -> str:
  sc = SCENES[sid]
  row = src["scenes"][sid]
  k = kinematics(src, sc["field"])
  T0, T1, HOLD = sc["t0"], k["t_s"] + sc["t_after"], sc["hold"]
  DUR = (T1 - T0) + HOLD
  kt = lambda t: (t - T0) / DUR  # noqa: E731
  W, H = 1200, 980
  M = 150.0
  uid = f"sim-{sid.lower()}"
  cx0, cy0, cw, ch = sc["crop"]
  px, py = 40, 96
  pw, ph = cw * M, ch * M
  pl = Plan(px, py, M, uid, origin=(cx0, cy0), height=ch)
  rating = rating_for(src, sid)
  body = [text(40, 36, f"{sid} · {row['hazard']} · {row['zone']} · {row['task']}: {sc['title']}", 20, C["ink"], 700),
          text(40, 60, f"Looping view: a fixed {cw:g} × {ch:g} m crop of the warehouse plan; {sc['field']} ({src['fields'][sc['field']]['config']}, {src['fields'][sc['field']]['case']}: a = {k['a']:g} m/s², unmeasured); "
               f"t = {T0:g} s to {T1:.2f} s, then a {HOLD:g} s hold", 12, C["muted"]),
          text(40, 78, f"The person is {row['who']}, closest {row['closest'].split(' if')[0]} if the robot does not stop (WP-C-06 §2). A viewer that shows the SVG as a still shows t = {T0:g} s.", 12, C["muted"]),
          rect(px, py, pw, ph, C["floor"], C["wall"], 0, 3),
          f'<clipPath id="{uid}-crop"><rect x="{px}" y="{py}" width="{pw:.1f}" height="{ph:.1f}"/></clipPath>',
          f'<g clip-path="url(#{uid}-crop)">']
  body += pl.floor(src, with_labels=False)
  for i, (x, y, w, h) in enumerate(SITE["racks"]):
    if not (cy0 + 0.15 <= y + h / 2 <= cy0 + ch - 0.15):
      continue
    X, Y = pl.P(x, y + h)
    body.append(text(X + 8 + (cx0 - x) * M if x < cx0 else X + 8, Y + h * M / 2 + 4, f"RACK {i + 1}", 10, "#E8EBED", 700))
  # the robot group: sprite and field, translated by the travel
  rx, ry, heading = sc["robot"]
  RX, RY = pl.P(rx, ry)
  times = [T0, 0.0, k["t_r"], k["t_s"], T1, T1 + HOLD]
  xs = [robot_travel(k, t, T0) * M for t in times]
  body.append('<g>' + _translate(xs, [0.0] * len(xs), [kt(t) for t in times], DUR))
  fx0 = RX + ROBOT_L / 2 * M
  hw = (ROBOT_W / 2 + k["Z"]) * M
  x = fx0
  for length, col in ((k["d_r"], C["red"]), (k["d_b"], C["amber"]), (k["walk"], C["teal"]), (k["Z"], C["blue"])):
    fill = f"url(#{uid}-hatch)" if col == C["amber"] else col
    body.append(rect(x, RY - hw, length * M, 2 * hw, fill, "none", 0, 1, "", 'fill-opacity="0.22"' if col != C["amber"] else ""))
    x += length * M
  body.append(f'<rect x="{fx0:.1f}" y="{RY - hw:.1f}" width="{k["L"] * M:.1f}" height="{2 * hw:.1f}" fill="none" stroke="{C["teal"]}" stroke-width="2" stroke-dasharray="6,3">'
              f'<animate attributeName="stroke" values="{C["teal"]};{C["teal"]};{C["red"]};{C["red"]};{C["line"]};{C["line"]}" '
              f'keyTimes="0;{kt(0):.4f};{kt(0) + 0.001:.4f};{kt(k["t_r"]):.4f};{kt(k["t_r"]) + 0.001:.4f};1" dur="{DUR:.2f}s" repeatCount="indefinite"/></rect>')
  body.append(text(fx0 + 4, RY + hw + 14, f"{sc['field']} {k['L']:.2f} m = {k['d_r']:.3f} + {k['d_b']:.3f} coast + {k['walk']:.2f} walk + {k['Z']:.2f}", 10, C["teal"], 700))
  body += pl.sprite(rx, ry, heading)
  for lab, col, t_on, t_off in (("%.2f m/s" % k["v"], C["ink"], None, k["t_r"]), ("coasting", C["amber"], k["t_r"], k["t_s"]), ("STANDSTILL", C["green"], k["t_s"], None)):
    keys = "0;1" if t_on is None and t_off is None else ""
    if t_on is None:
      vals, keys = "1;1;0;0", f"0;{kt(t_off):.4f};{kt(t_off) + 0.001:.4f};1"
    elif t_off is None:
      vals, keys = "0;0;1;1", f"0;{kt(t_on):.4f};{kt(t_on) + 0.001:.4f};1"
    else:
      vals, keys = "0;0;1;1;0;0", f"0;{kt(t_on):.4f};{kt(t_on) + 0.001:.4f};{kt(t_off):.4f};{kt(t_off) + 0.001:.4f};1"
    body.append(f'<text x="{RX:.1f}" y="{RY - 0.42 * M:.1f}" font-family="{MONO}" font-size="11" font-weight="700" fill="{col}" text-anchor="middle" opacity="{1 if t_on is None else 0}">{lab}'
                f'<animate attributeName="opacity" values="{vals}" keyTimes="{keys}" dur="{DUR:.2f}s" repeatCount="indefinite"/></text>')
  body.append('</g>')
  # the person: body touches the field's lateral edge at t = 0, x set back from the field's far edge
  pe = sc["person"]
  x_edge0 = rx + ROBOT_L / 2 + robot_travel(k, 0.0, T0) + k["L"]
  pxm = x_edge0 + pe["x_from_edge"]
  y_enter = ry + pe["side"] * (ROBOT_W / 2 + k["Z"] + 0.14)
  dxm, dym = pe["dir"]
  PX, PY = pl.P(pxm, y_enter)
  def off(t):  # pixel offset of the person at scene time t
    return (dxm * k["K"] * t * M, -dym * k["K"] * t * M)
  body.append('<g>' + _translate([off(T0)[0], off(T1)[0], off(T1)[0]], [off(T0)[1], off(T1)[1], off(T1)[1]], [0.0, kt(T1), 1.0], DUR))
  body += pl.worker(pxm, y_enter, None, f"{row['who']}, K = {k['K']:g} m/s")
  body.append('</g>')
  body.append('</g>')
  body += pl.chip(cx0 + cw - 1.0, cy0 + ch - 0.25, f"{rating['hazard']} {sid}", f"PLr {rating['plr']}", C["teal"])
  # events, time strip, distance plot
  ey = py + ph + 24
  events = [(0.0, "field violated", C["red"]), (k["t_det"], "OSSDs open", C["teal"]), (k["t_r"], "contactors open", C["red"]), (k["t_s"], "standstill", C["green"]), (None, "contact: none", C["green"])]
  for i, (t, lab, col) in enumerate(events):
    X = 40 + i * 232
    anim = "" if t is None else f'<animate attributeName="opacity" values="0.25;0.25;1;1" keyTimes="0;{kt(t):.4f};{kt(t) + 0.001:.4f};1" dur="{DUR:.2f}s" repeatCount="indefinite"/>'
    label = lab if t is None else f"{t:.2f} s  {lab}"
    body.append(f'<g opacity="0.25">{anim}' + rect(X, ey, 216, 30, C["panel"], col, 6, 1.4) + text(X + 10, ey + 20, label, 10.5, col, 700, family=MONO) + '</g>')
  sy = ey + 70
  x0, x1 = 60, W - 60
  Xt = lambda t: x0 + (x1 - x0) * (t - T0) / (T1 - T0)  # noqa: E731
  body += [text(40, sy - 16, "time, scene seconds", 10, C["muted"], 600), line(x0, sy, x1, sy, C["line"], 2)]
  for t, lab in ((T0, f"{T0:g}"), (0.0, "0 demand"), (k["t_r"], f"{k['t_r']:.2f} power off"), (k["t_s"], f"{k['t_s']:.2f} standstill"), (T1, f"{T1:.2f} hold")):
    body += [line(Xt(t), sy - 7, Xt(t), sy + 7, C["ink"], 1.5), text(Xt(t), sy + 22, lab, 9.5, C["muted"], 600, "middle", MONO)]
  cursor = (f'<animateTransform attributeName="transform" type="translate" values="0,0;{x1 - x0:.1f},0;{x1 - x0:.1f},0" keyTimes="0;{kt(T1):.4f};1" '
            f'dur="{DUR:.2f}s" repeatCount="indefinite" calcMode="linear"/>')
  body.append(f'<line x1="{x0}" y1="{sy - 16}" x2="{x0}" y2="{sy + 10}" stroke="{C["red"]}" stroke-width="2.5">{cursor}</line>')
  gy0, gy1 = sy + 50, sy + 150
  body += [rect(40, gy0 - 12, W - 80, 130, C["panel"], C["stroke"], 6),
           text(52, gy0 + 2, "distance from the person to the robot's front, m (planning case); the red line is the field edge, the cursor the time shown", 10, C["muted"], 600)]
  def dist(t):
    rfx = rx + ROBOT_L / 2 + robot_travel(k, t, T0)
    return math.hypot(pxm + dxm * k["K"] * t - rfx, y_enter + dym * k["K"] * t - ry)
  dmax = 2.6
  pts = []
  n = int(round((T1 - T0) / 0.05))
  for i in range(n + 1):
    t = T0 + i * 0.05
    pts.append((Xt(t), gy1 - min(dist(t), dmax) / dmax * (gy1 - gy0 - 20)))
  body.append('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="none" stroke="{C["teal"]}" stroke-width="2"/>')
  yL = gy1 - k["L"] / dmax * (gy1 - gy0 - 20)
  body += [line(x0, yL, x1, yL, C["red"], 1, "4,3"), text(x0 - 6, yL + 4, f"{k['L']:.2f}", 9, C["red"], 600, "end", MONO), text(x0 - 6, gy1 + 4, "0", 9, C["muted"], 600, "end", MONO),
           f'<line x1="{x0}" y1="{gy0 + 8}" x2="{x0}" y2="{gy1}" stroke="{C["ink"]}" stroke-width="1.5">{cursor}</line>']
  dmin = min(dist(T0 + i * 0.01) for i in range(int(round((T1 - T0) / 0.01)) + 1))
  body.append(text(x1, gy1 + 16, f"closest approach in the planning case: {dmin:.2f} m; a person who keeps walking passes in front of the stopped robot", 10, C["teal"], 600, "end"))
  body.append(text(W - 32, H - 52, "Generated by assurance/sim/figures/fig_sim_is.py", 9.5, C["dim"], anchor="end"))
  body += band(W, H, f"Kinematic motion from WP-S-04 v0.1 planning values (t_r {k['t_r']:g} s, a = {k['a']:g} m/s² unmeasured, C = 0, K = {k['K']:g} m/s). A loop shows a situation; it does not show that a measure works.")
  return svg(W, H, uid, f"{sid}: {sc['title']}, looping",
             f"Looping top view of {sid}: in a warehouse aisle between two rack rows the robot drives at {k['v']:g} m/s with its protective field {sc['field']} drawn ahead of it as four bands, the robot's travel during the reaction time, the coast, the person's walk and the tolerance; "
             f"a person walks into the field at {k['K']:g} m/s; the field outline turns red at the demand, the contactors open at {k['t_r']:.2f} s, the robot coasts to a standstill at {k['t_s']:.2f} s; "
             f"the events light up below, a cursor runs along a time strip, and a plot shows the distance from the person to the robot's front falling to {dmin:.2f} m in the planning case.", body)


def _translate(xs, ys, keys, dur):
  vals = ";".join(f"{x:.2f},{y:.2f}" for x, y in zip(xs, ys))
  kts = ";".join(f"{k:.4f}" for k in keys)
  return f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{kts}" dur="{dur:.2f}s" repeatCount="indefinite" calcMode="linear"/>'


OUTPUTS = {"fig-sim-plan.svg": fig_plan}
for _sid in SCENES:
  OUTPUTS[f"fig-sim-{_sid.lower()}-anim.svg"] = (lambda s, sid=_sid: fig_loop(s, sid))


def main(argv: list[str]) -> int:
  check = "--check" in argv
  src = load_source()
  errs = check_source(src)
  for name, fn in OUTPUTS.items():
    out = fn(src)
    path = HERE / name
    if check:
      if not path.exists() or path.read_text(encoding="utf-8") != out:
        errs.append(f"{name} is stale: run python3 {Path(__file__).relative_to(ROOT)}")
    else:
      path.write_text(out, encoding="utf-8")
      print("wrote", path.relative_to(ROOT))
  for e in errs:
    print("ERROR:", e, file=sys.stderr)
  if not errs and check:
    print(f"fig_sim_is: sources consistent, {len(OUTPUTS)} SVGs current")
  return 1 if errs else 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
