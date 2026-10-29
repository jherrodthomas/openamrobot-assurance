#!/usr/bin/env python3
"""Draw the 2D views of the hazard situations: the warehouse plan and one looping view per interaction scenario.

  fig-sim-plan.svg            the warehouse from above: the zones of WP-C-02 §2 mapped onto a typical floor, the robot
                              with every field set of WP-S-04 §4.1 at its planning length, the station rings of
                              WP-S-04 §4.5, the people of the interaction scenarios where they happen, hazard chips
                              with the PLr adopted in WP-C-03 §5
  fig-sim-is-NN-anim.svg      one loop per interaction scenario (SMIL, no script): a fixed crop of the same plan; the
                              robot at the zone speed with the field set that applies drawn as the sum of its terms, or
                              turning, reversing, or at rest with the arm or the lift; the person at K; the field or
                              ring outline changing at the demand and at power removal; events, time strip and the
                              person-to-robot distance with a cursor. A still viewer shows the first frame
  fig-sim-is-NN-still.svg     the three scenarios with no motion (IS-07, IS-08, IS-11) as stills of the same crop
  fig-sim-tour-anim.svg       the tour (SMIL): CFG-002 on a closed route through the whole plan, the field set switching
                              at each zone boundary, the crossing of IS-01 and the resume of IS-10 played on the way,
                              the other situations of the route lit as they are reached; a readout panel and a timeline

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

The robot on the views is the top-down CAD render of assurance/sim/blender/sprites (pinned by hash in SPRITES); the
drawn footprint stands in when the files are absent. Standard library only. Output is deterministic.
"""
from __future__ import annotations

import base64
import hashlib
import json
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

# The robot on the views is its own CAD, rendered top-down by the Blender pipeline (assurance/sim/blender/README.md §2:
# orthographic, transparent, cropped to 250 px/m) and pinned here by hash like a sprite sheet (ideas-2d-views.md §4).
# A re-render that changes a file fails --check until its pin is updated on purpose. Without the files the drawn
# footprint of Plan.sprite() stands in.
SPRITE_DIR = ROOT / "assurance" / "sim" / "blender" / "sprites"
SPRITES = {
  "cfg001": ("cfg001-top.png", "41e4878c8835083d336de1060cfb85e59c840a5a5edaf3574838f9b33f5499f9"),
  "cfg002": ("cfg002-stowed-top.png", "24ced09a24f7b1b211f6bc3a6df25228f9a82351e7318e88a153a55c0cb59575"),
  "cfg002-carry": ("cfg002-carry-top.png", "4bb417c6ac9d1ce52942021d4d915333299bd8fa4aea8da59d6dd2234515875f"),
}


def load_sprites() -> dict:
  out = {}
  for kind, (name, pin) in SPRITES.items():
    png = SPRITE_DIR / name
    meta = png.with_name(name + ".json")
    if not png.exists() or not meta.exists():
      continue
    data = png.read_bytes()
    m = json.loads(meta.read_text(encoding="utf-8"))
    out[kind] = {"name": name, "sha": hashlib.sha256(data).hexdigest(), "pin": pin, "b64": base64.b64encode(data).decode("ascii"),
                 "w": m["size_px"][0], "h": m["size_px"][1], "ox": m["origin_px"][0], "oy": m["origin_px"][1], "ppm": m["px_per_m"]}
  return out


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
          "Z_s04": _num(conv["Z"][1]) if "Z" in conv else None, "budget": budget, "fields": fields, "zones": zones, "ratings": ratings,
          "sprites": load_sprites()}


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
  for fid in PLAN_FIELDS + [sc["field"] for sc in SCENES.values() if sc["field"]]:
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
    if rating_for(src, sid) is None and sid not in UNRATED:
      errs.append(f"WP-C-03 §5 has no rated row naming {sid}")
  for kind, sp in src["sprites"].items():
    if sp["sha"] != sp["pin"]:
      errs.append(f"sprite {sp['name']} changed (sha256 {sp['sha'][:12]}…): re-pin it in SPRITES if the new render is the one to use")
    if sp["ppm"] != 250:
      errs.append(f"sprite {sp['name']} is {sp['ppm']} px/m, not 250")
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
  "station": {"mark": (11.4, 9.0, 2.4, 0.5), "centre": (12.6, 8.34), "robot": (12.6, 8.1)},   # the ring on the arm mount, 0.24 m ahead of the base centre (heading +y)
  "aisle_robot": (7.6, 8.35),                  # the live robot, aisle 2, heading +x
  "aisle1_robot": (14.0, 11.1),               # the carry-pose ghost, aisle 1
  "dock_robot": (20.8, 13.2),                 # the docking ghost, heading −x, reverse path behind it
}
UNRATED = ("IS-07", "IS-08")   # scenarios WP-C-03 §5 folds into H-02/H-08 and H-03/H-06 without naming them; their chips say so
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


def svg(w, h, uid, title, desc, body, sprites=()):
  """sprites: the (kind, spec) pairs a Plan used; each becomes one <image> in <defs> that the <use> elements reference."""
  images = "".join(f'<image id="{uid}-sp-{kind}" width="{sp["w"]}" height="{sp["h"]}" href="data:image/png;base64,{sp["b64"]}"/>' for kind, sp in sprites)
  return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
          f'<title id="{uid}-t">{escape(title)}</title>\n<desc id="{uid}-d">{escape(desc)}</desc>\n' + defs(uid) + (f"<defs>{images}</defs>" if images else "") + "\n"
          f'<rect x="0" y="0" width="{w}" height="{h}" fill="{C["bg"]}"/>\n' + "\n".join(body) + "\n</svg>\n")


def band(w, h, note):
  return [rect(0, h - 44, w, 44, C["amber_bg"]), text(16, h - 26, BAND, 11, C["amber"], 700, family=MONO), text(16, h - 11, note, 10, C["amber"])]


class Plan:
  """The site in a pixel frame: P maps metres to pixels, M is pixels per metre, uid prefixes the pattern ids."""

  def __init__(self, px, py, M, uid, origin=(0.0, 0.0), height=None, sprites=None):
    self.px, self.py, self.M, self.uid = px, py, M, uid
    self.ox, self.oy = origin
    self.h = height if height is not None else SITE["size"][1]
    self.sprites = sprites or {}
    self.used = {}

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

  def worker(self, x, y, vest=None, label="", color=None, scale=1.0):
    M = self.M * scale
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

  def sprite(self, x, y, heading=1, opacity=1.0, kind="cfg001", at_origin=False):
    """The robot from above: the CAD render of SPRITES when the file is present and pinned (the image's +x is to the
    right and its +y up, as on the plan; origin_px is the base's centre), else a drawn footprint of the base
    (WP-C-01 §4: 780 × 582 mm): deck, bumper ends, drive wheels, castors, the scanner at the front, the rear bumper red."""
    M = self.M
    cx, cy = (0.0, 0.0) if at_origin else self.P(x, y)
    sp = self.sprites.get(kind)
    if sp:
      self.used[kind] = sp
      s = M / sp["ppm"]
      return [f'<use href="#{self.uid}-sp-{kind}" opacity="{opacity}" transform="translate({cx:.1f},{cy:.1f}) scale({heading * s:.4f},{s:.4f}) translate({-sp["ox"]:.1f},{-sp["oy"]:.1f})"/>']
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
  pl = Plan(40, 92, M, uid, sprites=src["sprites"])
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
  body += pl.sprite(bx, by, 1, 0.35, "cfg002-carry")
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
           text(40, ly + 28, ("The robot is its CAD rendered from above (assurance/sim/blender/sprites); the carry ghost is CFG-002 in the carry pose." if src["sprites"] else "Robot footprint 0.78 × 0.58 m (WP-C-01 §4), drawn.")
                + " Field lengths: WP-S-04 §4.1 planning values, C = 0; the coast is unmeasured (WP-V-02).", 10.5, C["muted"]),
           text(W - 32, ly + 28, "Generated by assurance/sim/figures/fig_sim_is.py", 9.5, C["dim"], anchor="end")]
  body += band(W, H, "Drawn to WP-S-04 v0.1 planning values; the coast is unmeasured (WP-V-02). A plan shows where the situations are; it does not show that a measure works.")
  return svg(W, H, uid, "The warehouse from above with the zones, the field sets and the situations",
             "A typical warehouse floor seen from above: the office and visitor route as Z5 excluded, a taped test area Z1, three rack rows with dashed aisle lanes as Z2, a dock lane Z3 with the robot's dock, a charging bay Z4, a truck loading dock as Z0 excluded; the robot in an aisle with the three FS-1 field lengths nested ahead of it, a carry ghost with FS-3 and FS-4, a docking ghost with the FS-2 lengths and the blind reverse path; a station bay with the workspace ring and lift keep-clear; the people of IS-01, IS-02, IS-04 and IS-13 where they happen, with hazard chips.", body, sprites=list(pl.used.items()))


# ------------------------------------------------------------------------------------------------------ the loops
# One looping view per interaction scenario, a fixed crop of the plan. Every loop is built the same way: each actor
# gets a trajectory sampled at DT from the planning values (the robot's stop profile from WP-S-04, the person at K),
# the demand is found where the person's body meets the field the row names, and the SVG animates the samples with
# SMIL. The three scenarios with no motion (IS-07, IS-08, IS-11) are stills from the same crop machinery.
DT = 0.05
ARM_MOUNT, COLUMN_X, SWEEP = 0.24, 0.06, 0.85   # CFG-002: arm mount and column axis ahead of the base centre (blender/cfg002.py); the load's sweep radius at head height in the carry pose
TURN_RATE = 0.5                                  # rad/s, the Z1/Z2 angular limit (WP-C-02 §2)


def kinematics(src: dict, fid: str, path: str = "scanner"):
  """The stop from a field row: t_r of the named §2 path (scanner or bumper), the coast t_b, d_r, d_b, the walk term, L."""
  f = src["fields"][fid]
  sp = scanner_path(src) if path == "scanner" else next(b for b in src["budget"] if b["sf"] == "SF-02" and "bumper" in b["path"])
  t_r = sp["t_r"] / 1000.0
  t_b, d_s, L = model(f["v"], f["a"], t_r, src["K"], src["Z"])
  return {"v": f["v"], "a": f["a"], "t_r": t_r, "t_b": t_b, "t_s": t_r + t_b, "d_r": f["v"] * t_r, "d_b": f["v"] ** 2 / (2 * f["a"]),
          "walk": src["K"] * (t_r + t_b), "Z": src["Z"], "L": L, "K": src["K"], "t_det": sp["det"] / 1000.0, "t_logic": (sp["det"] + sp["logic"]) / 1000.0}


def robot_travel(k: dict, t: float, t0: float) -> float:
  """Distance travelled since t0: constant speed until t_r, then the coast, then standstill (the demand at t = 0)."""
  if t <= k["t_r"]:
    return k["v"] * (t - t0)
  if t <= k["t_s"]:
    return k["v"] * (k["t_r"] - t0) + k["v"] * (t - k["t_r"]) - 0.5 * k["a"] * (t - k["t_r"]) ** 2
  return k["v"] * (k["t_r"] - t0) + k["d_b"]


def speed_after_demand(k: dict, t_d: float):
  """The robot's speed as a function of time for a demand at t_d: v until t_d + t_r, the coast, then 0."""
  def v(t):
    if t <= t_d + k["t_r"]:
      return k["v"]
    if t <= t_d + k["t_s"]:
      return k["v"] - k["a"] * (t - t_d - k["t_r"])
    return 0.0
  return v


def samples(T0, T1):
  n = int(round((T1 - T0) / DT))
  return [T0 + i * DT for i in range(n + 1)]


def integrate_pose(x0, y0, yaw0, vel, T0, T1):
  """Robot samples (t, x, y, yaw_deg) from a velocity function vel(t) -> (speed along the heading, yaw rate deg/s)."""
  out = [(T0, x0, y0, yaw0)]
  x, y, yaw = x0, y0, yaw0
  for t in samples(T0, T1)[1:]:
    v, w = vel(t - DT / 2)
    yaw += w * DT
    x += v * math.cos(math.radians(yaw)) * DT
    y += v * math.sin(math.radians(yaw)) * DT
    out.append((t, x, y, yaw))
  return out


def integrate_xy(x0, y0, vel, T0, T1):
  """Person samples (t, x, y) from vel(t) -> (vx, vy)."""
  out = [(T0, x0, y0)]
  x, y = x0, y0
  for t in samples(T0, T1)[1:]:
    vx, vy = vel(t - DT / 2)
    x += vx * DT
    y += vy * DT
    out.append((t, x, y))
  return out


def walk(K, segments):
  """vel(t) for a walker: segments are (t_until, (dx, dy)) unit directions in order; standing still is (0, 0)."""
  def vel(t):
    for t_until, (dx, dy) in segments:
      if t < t_until:
        return (dx * K, dy * K)
    return (0.0, 0.0)
  return vel


def at(samples_, t):
  """Linear interpolation of a sample list at time t."""
  if t <= samples_[0][0]:
    return samples_[0][1:]
  for a, b in zip(samples_, samples_[1:]):
    if t <= b[0]:
      f = (t - a[0]) / (b[0] - a[0]) if b[0] > a[0] else 0.0
      return tuple(p + (q - p) * f for p, q in zip(a[1:], b[1:]))
  return samples_[-1][1:]


def in_field(robot_pose, px, py, L, half_w, r=0.14):
  """Whether a person circle meets the field rectangle ahead of the robot, in the robot's frame."""
  x, y, yaw = robot_pose
  c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
  dx, dy = px - x, py - y
  u, v = dx * c + dy * s, -dx * s + dy * c
  return (ROBOT_L / 2 - r) <= u <= (ROBOT_L / 2 + L + r) and abs(v) <= half_w + r


def hull_distance(robot_pose, px, py):
  """Distance from a point to the robot's hull rectangle (0 inside)."""
  x, y, yaw = robot_pose
  c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
  dx, dy = px - x, py - y
  u, v = dx * c + dy * s, -dx * s + dy * c
  du, dv = max(abs(u) - ROBOT_L / 2, 0.0), max(abs(v) - ROBOT_W / 2, 0.0)
  return math.hypot(du, dv)


def front_distance(robot_pose, px, py):
  """Distance from the robot's front face (centre) to a point, along the heading, floored at zero."""
  x, y, yaw = robot_pose
  c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
  u = (px - x) * c + (py - y) * s
  return max(u - ROBOT_L / 2, 0.0)


# The scenes. Each entry names the crop, the configuration drawn and a builder; the builder returns the actors, the
# events and the plot from the tables. Titles are the scenario in a line; the row of WP-C-06 §2 supplies the rest.
SCENES = {
  "IS-01": dict(crop=(6.4, 6.3, 6.0, 3.6), field="FS-1b", kind="cfg001", title="a person crosses the aisle ahead at walking pace"),
  "IS-02": dict(crop=(13.0, 6.5, 6.0, 3.6), field="FS-1b", kind="cfg001", title="a person steps out from behind the rack end, unseen until 0.5 m ahead"),
  "IS-03": dict(crop=(7.0, 9.4, 6.0, 3.6), field="FS-1b", kind="cfg001", title="a person walks alongside inside 0.5 m; the robot turns toward the rack"),
  "IS-04": dict(crop=(17.4, 11.2, 6.0, 3.6), field="FS-2b", kind="cfg001", title="a person behind the robot as it reverses out of the dock at the crawl limit"),
  "IS-05": dict(crop=(17.4, 11.2, 6.0, 3.6), field="FS-2b", kind="cfg001", title="a person steps into the dock lane during the final blind approach"),
  "IS-06": dict(crop=(0.6, 0.4, 6.0, 3.6), field="FS-1b", kind="cfg001", title="teleoperation: the operator watches the screen, the robot is not where the map says"),
  "IS-07": dict(crop=(17.4, 9.6, 6.0, 3.6), field=None, kind="cfg001", still=True, title="the charger is connected with the robot powered; a command arrives from the network"),
  "IS-08": dict(crop=(7.0, 9.4, 6.0, 3.6), field=None, kind="cfg001", still=True, title="a person sits on the robot while another pushes it"),
  "IS-09": dict(crop=(9.0, 9.4, 6.0, 3.6), field="FS-1b", kind="cfg001", title="a crawling child below the scan plane: the field passes over them"),
  "IS-10": dict(crop=(5.0, 6.3, 6.0, 3.6), field="FS-1b", kind="cfg001", title="a person stands in the path; the robot waits, the person steps aside, the robot resumes"),
  "IS-11": dict(crop=(7.0, 9.4, 6.0, 3.6), field="FS-1b", kind="cfg001", still=True, title="the on-screen E-STOP is pressed; the robot does not stop"),
  "IS-12": dict(crop=(5.0, 6.3, 6.0, 3.6), field="FS-1b", kind="cfg001", title="a bystander stands in front with a hand out, then holds the robot"),
  "IS-13": dict(crop=(9.6, 6.6, 6.0, 3.6), field=None, kind="cfg002", title="a person reaches into the arm's workspace at the station while the arm moves"),
  "IS-14": dict(crop=(9.6, 6.6, 6.0, 3.6), field=None, kind="cfg002", title="a person steps under the lowering lift carriage"),
  "IS-15": dict(crop=(9.0, 9.4, 6.0, 3.6), field="FS-4", kind="cfg002-carry", title="carrying at 0.3 m/s past a bystander, then a turn in place: the load sweeps at head height"),
}


def _stop_states(k, t_d, T0, T1, resume=None):
  """Field outline colour over time and the robot's status label: live, violated, power removed, (resumed)."""
  states = [(T0, C["teal"]), (t_d, C["red"]), (t_d + k["t_r"], C["line"])]
  labels = [(T0, f"{k['v']:.2f} m/s", C["ink"]), (t_d + k["t_r"], "coasting", C["amber"]), (t_d + k["t_s"], "STANDSTILL", C["green"])]
  if resume is not None:
    states.append((resume, C["teal"]))
    labels.append((resume, f"{k['v']:.2f} m/s", C["ink"]))
  return states, labels


def _stop_events(k, t_d, what="field violated", device="OSSDs open"):
  return [(t_d, what, C["red"]), (t_d + k["t_det"], device, C["teal"]), (t_d + k["t_r"], "contactors open", C["red"]), (t_d + k["t_s"], "standstill", C["green"])]


def _approach(src, sid, robot0, person0, walk_segments, standing=False, T0=-0.5, t_after=0.33, hold=1.5, who=None):
  """The common case: the robot drives +x at the field's speed, a person on foot; the demand where the body meets the field."""
  sc = SCENES[sid]
  k = kinematics(src, sc["field"])
  half_w = ROBOT_W / 2 + k["Z"]
  pre = integrate_pose(robot0[0], robot0[1], 0.0, lambda t: (k["v"], 0.0), T0, T0 + 12.0)
  person = integrate_xy(person0[0], person0[1], walk(k["K"], walk_segments), T0, T0 + 12.0)
  t_d = next((t for (t, *_) in pre if in_field(at(pre, t), *at(person, t), k["L"], half_w)), None)
  assert t_d is not None, sid
  T1 = t_d + k["t_s"] + t_after
  robot = integrate_pose(robot0[0], robot0[1], 0.0, (lambda v: lambda t: (v(t), 0.0))(speed_after_demand(k, t_d)), T0, T1)
  person = integrate_xy(person0[0], person0[1], walk(k["K"], walk_segments), T0, T1)
  states, labels = _stop_states(k, t_d, T0, T1)
  dist = lambda t: math.hypot(*(a - b for a, b in zip(at(person, t), at(robot, t)[:2]))) if False else _person_front(robot, person, t)  # noqa: E731
  return dict(k=k, T0=T0, T1=T1, HOLD=hold, t_d=t_d, robot=robot, person=person, states=states, labels=labels, dist=dist,
              events=_stop_events(k, t_d) + [(None, "contact: none", C["green"])], who=who)


def _person_front(robot, person, t):
  return front_distance(at(robot, t), *at(person, t)) if abs(at(person, t)[1] - at(robot, t)[1]) < ROBOT_W / 2 + 0.14 else hull_distance(at(robot, t), *at(person, t))


def build(src: dict, sid: str) -> dict:
  """The actors, events and plot of one scenario, from the tables and the scene geometry below."""
  sc = SCENES[sid]
  row = src["scenes"][sid]
  K, Z = src["K"], src["Z"]
  cx0, cy0, cw, ch = sc["crop"]
  if sid == "IS-01":
    k = kinematics(src, "FS-1b")
    rx, ry = 7.3, 8.35
    x_edge0 = rx + ROBOT_L / 2 + k["v"] * 0.5 + k["L"]
    s = _approach(src, sid, (rx, ry), (x_edge0 - 0.30, ry + ROBOT_W / 2 + Z + 0.14 + 0.8), [(99, (0, -1))], T0=-0.5)
    s["note"] = f"closest approach in the planning case: {s['dmin']:.2f} m; a person who keeps walking passes in front of the stopped robot" if "dmin" in s else ""
    return s
  if sid == "IS-02":
    k = kinematics(src, "FS-1b")
    # the person walks down the cross-aisle at x = 16.95 from behind rack 2 (y ≥ 9.5); the robot's front is 0.5 m short of that line when they appear
    appear_y = 9.5 + 0.14
    person0 = (16.95, appear_y + K * 0.5)
    s = _approach(src, sid, (16.45 - ROBOT_L / 2 - k["v"] * 0.5, 8.35), person0, [(99, (0, -1))], T0=-0.5)
    s["events"].insert(0, (0.0, "appears 0.5 m ahead", C["amber"]))
    s["statics"] = ["occluded"]
    return s
  if sid == "IS-03":
    k = kinematics(src, "FS-1b")
    T0 = -1.0
    rx, ry = 8.2, 11.15
    py = ry + ROBOT_W / 2 + 0.14 + 0.25       # 0.25 m between the body and the hull, inside the 0.5 m of the row
    turn = 15.0                               # deg/s, below the 0.5 rad/s limit
    pre = integrate_pose(rx, ry, 0.0, lambda t: (k["v"], turn if t >= 0 else 0.0), T0, 6.0)
    person_pre = integrate_xy(rx - 0.1, py, lambda t: (k["v"], 0.0), T0, 6.0)
    t_c = next(t for (t, *_) in pre if hull_distance(at(pre, t), *at(person_pre, t)) <= 0.14 + 0.005)
    stall = next(b for b in src["budget"] if b["sf"] == "SF-06" and "stall" in b["path"])
    t_stall = t_c + stall["t_r"] / 1000.0
    T1 = t_stall + k["t_b"] + 0.3
    vel = lambda t: ((k["v"] if t < t_stall else max(k["v"] - k["a"] * (t - t_stall), 0.0)), (turn if 0 <= t < 2.0 else 0.0))  # noqa: E731
    robot = integrate_pose(rx, ry, 0.0, vel, T0, T1)
    person = integrate_xy(rx - 0.1, py, lambda t: ((k["v"], 0.0) if t < t_c else (0.0, 0.0)), T0, T1)
    person = [(t, x, min(y, 12.0 - 0.14)) for t, x, y in person]
    return dict(k=k, T0=T0, T1=T1, HOLD=1.5, t_d=None, robot=robot, person=person, masked=True,
                states=[(T0, C["teal"])], labels=[(T0, f"{k['v']:.2f} m/s", C["ink"]), (0.0, "turning 15°/s", C["ink"]), (t_stall, "stall: power off", C["amber"]), (t_stall + k["t_b"], "STANDSTILL", C["green"])],
                dist=lambda t: hull_distance(at(robot, t), *at(person, t)) - 0.14 + 0.14 if True else 0,
                events=[(0.0, "turn toward the rack begins", C["amber"]), (t_c, "corner meets the person: no demand (side masked, GAP-35)", C["red"]),
                        (t_stall, f"SF-06 stall detector, {stall['t_r'] / 1000:.2f} s", C["teal"]), (t_stall + k["t_b"], "standstill", C["green"]), (None, "pinned against the rack", C["red"])],
                dist_label="distance from the person to the hull, m: the side sectors are masked, so the field never sees them", dist_line=None)
  if sid in ("IS-04", "IS-05"):
    kb = kinematics(src, "FS-2b", "bumper")
    kf = kinematics(src, "FS-2b")
    if sid == "IS-04":
      T0 = -1.0
      px, py = 21.5, 13.2
      cx_contact = px - 0.14 - 0.045 - ROBOT_L / 2        # the rear bumper edge meets the shin at t = 0 (yaw 180: the rear is at +x)
      rx = cx_contact + 0.05 * T0 * 1.0
      vel = lambda t: ((-0.05 if t < kb["t_r"] else -max(0.05 - kb["a"] * (t - kb["t_r"]), 0.0)), 0.0)  # noqa: E731
      T1 = kb["t_s"] + 0.6
      robot = integrate_pose(rx, py, 180.0, vel, T0, T1)
      person = [(t, px, py) for t in samples(T0, T1)]
      rear = lambda t: max(px - 0.14 - (at(robot, t)[0] + ROBOT_L / 2 + 0.045), 0.0)  # noqa: E731
      return dict(k=kb, T0=T0, T1=T1, HOLD=1.5, t_d=0.0, robot=robot, person=person, no_field=True, rear_red=True, reverse_strip=rx,
                  states=[(T0, C["line"])], labels=[(T0, "reversing 0.05 m/s", C["ink"]), (kb["t_r"], "coasting", C["amber"]), (kb["t_s"], "STANDSTILL", C["green"])],
                  dist=rear, events=[(0.0, "bumper edge meets the shin", C["red"]), (kb["t_det"], "edge detected", C["teal"]), (kb["t_r"], "contactors open", C["red"]), (kb["t_s"], f"standstill, {kb['d_r'] * 1000 + kb['d_b'] * 1000:.0f} mm after contact", C["green"]), (None, "rear sector masked: no field", C["amber"])],
                  dist_label="distance from the rear bumper to the person's shin, m; the stop after contact is millimetres", dist_line=None)
    # IS-05: the final approach, nose first at the crawl limit; the field is muted inside the last metre (GAP-15)
    T0 = -2.0
    dock_x = 22.9
    rx0 = dock_x - 1.0 - ROBOT_L / 2 + 0.05 * T0      # the front is 1.0 m from the dock at t = 0
    px0, py0 = 22.3, 12.35
    person = integrate_xy(px0, py0, walk(K, [(0.2, (0, 0)), (0.2 + (13.2 - py0) / K, (0, 1))]), T0, 12.0)
    pre = integrate_pose(rx0, 13.2, 0.0, lambda t: (0.05, 0.0), T0, 12.0)
    t_c = next(t for (t, *_) in pre if at(pre, t)[0] + ROBOT_L / 2 + 0.045 >= px0 - 0.14)
    T1 = t_c + kb["t_s"] + 0.6
    vel = lambda t: ((0.05 if t < t_c + kb["t_r"] else max(0.05 - kb["a"] * (t - t_c - kb["t_r"]), 0.0)), 0.0)  # noqa: E731
    robot = integrate_pose(rx0, 13.2, 0.0, vel, T0, T1)
    person = integrate_xy(px0, py0, walk(K, [(0.2, (0, 0)), (0.2 + (13.2 - py0) / K, (0, 1))]), T0, T1)
    return dict(k=kf, kb=kb, T0=T0, T1=T1, HOLD=1.5, t_d=t_c, robot=robot, person=person, muted_at=0.0,
                states=[(T0, C["teal"]), (0.0, C["dim"]), (t_c, C["red"]), (t_c + kb["t_r"], C["line"])],
                labels=[(T0, "0.05 m/s", C["ink"]), (t_c + kb["t_r"], "coasting", C["amber"]), (t_c + kb["t_s"], "STANDSTILL", C["green"])],
                dist=lambda t: front_distance(at(robot, t), *at(person, t)) if at(person, t)[1] > 13.2 - ROBOT_W / 2 - 0.14 else 9.0,
                events=[(0.0, "field muted inside the last metre (GAP-15)", C["amber"]), (0.2, "steps into the lane", C["amber"]), (t_c, "bumper meets the person", C["red"]),
                        (t_c + kb["t_r"], "contactors open", C["red"]), (t_c + kb["t_s"], f"standstill, {(kb['d_r'] + kb['d_b']) * 1000:.0f} mm after contact", C["green"])],
                dist_label="distance from the front bumper to the person, m, once they are in the lane; nothing but the bumper detects them")
  if sid == "IS-06":
    s = _approach(src, sid, (3.0, 2.4), (4.8, 2.4), [(99, (0, 0))], T0=-0.5, who="bystander")
    s["map_ghost"] = 0.6
    s["events"] = [(None, "operator watches the screen: no SF-01, no deadman release", C["red"])] + s["events"][:-1] + [(None, "SF-02 is live in every mode", C["green"])]
    return s
  if sid == "IS-09":
    k = kinematics(src, "FS-1b")
    T0 = -0.5
    rx, ry, cx_child = 9.8, 11.15, 11.6
    stall = next(b for b in src["budget"] if b["sf"] == "SF-06" and "stall" in b["path"])
    t_field = next(t for t in samples(T0, 10) if rx + k["v"] * (t - T0) + ROBOT_L / 2 + k["L"] >= cx_child - 0.2)
    t_c = next(t for t in samples(T0, 10) if rx + k["v"] * (t - T0) + ROBOT_L / 2 >= cx_child - 0.2)
    t_stall = t_c + stall["t_r"] / 1000.0
    T1 = t_stall + k["t_b"] + 0.3
    vel = lambda t: ((k["v"] if t < t_stall else max(k["v"] - k["a"] * (t - t_stall), 0.0)), 0.0)  # noqa: E731
    robot = integrate_pose(rx, ry, 0.0, vel, T0, T1)
    child = [(t, cx_child, ry) for t in samples(T0, T1)]
    return dict(k=k, T0=T0, T1=T1, HOLD=1.5, t_d=None, robot=robot, person=child, child=True,
                states=[(T0, C["teal"])], labels=[(T0, f"{k['v']:.2f} m/s", C["ink"]), (t_c, "pushing", C["red"]), (t_stall, "stall: power off", C["amber"]), (t_stall + k["t_b"], "STANDSTILL", C["green"])],
                dist=lambda t: max(at(robot, t)[0] + ROBOT_L / 2 - (cx_child - 0.2), 0.0) * 0 + max(cx_child - 0.2 - at(robot, t)[0] - ROBOT_L / 2, 0.0),
                events=[(t_field, "field over the child: no demand (below the 0.18 m plane)", C["amber"]), (t_c, "front meets the child at 0.20 m/s", C["red"]),
                        (t_stall, f"SF-06 stall detector, {stall['t_r'] / 1000:.2f} s, if the wheels block", C["teal"]), (t_stall + k["t_b"], "standstill", C["green"])],
                dist_label="distance from the robot's front to the child, m; the field never sees them (SR-02.03: detection to 0.3 m, TBC)")
  if sid in ("IS-10", "IS-12"):
    k = kinematics(src, "FS-1b")
    T0 = -0.5
    rx, ry, px = 8.2, 8.35, 10.3
    t_d = next(t for t in samples(T0, 10) if rx + k["v"] * (t - T0) + ROBOT_L / 2 + k["L"] >= px - 0.14)
    if sid == "IS-10":
      t_aside = t_d + k["t_s"] + 1.5
      t_reset = t_aside + 0.9 / K + 0.4
      warn = 2.0                                     # HR-07, SR-08.01: warning time before motion, TBC
      t_go = t_reset + warn
      T1 = t_go + 1.5
      vel = lambda t: ((speed_after_demand(k, t_d)(t) if t < t_go else k["v"]), 0.0)  # noqa: E731
      robot = integrate_pose(rx, ry, 0.0, vel, T0, T1)
      person = integrate_xy(px, ry, walk(K, [(t_aside, (0, 0)), (t_aside + 0.9 / K, (0, 1))]), T0, T1)
      states, labels = _stop_states(k, t_d, T0, T1, resume=t_go)
      labels.insert(-1, (t_reset, "warning 2 s", C["amber"]))
      events = _stop_events(k, t_d) + [(t_aside, "steps aside", C["amber"]), (t_reset, "SF-05 reset, warning 2 s (HR-07, TBC)", C["amber"]), (t_go, "motion resumes", C["teal"])]
      return dict(k=k, T0=T0, T1=T1, HOLD=1.0, t_d=t_d, robot=robot, person=person, states=states, labels=labels, warn=(t_reset, t_go),
                  dist=lambda t: _person_front(robot, person, t), events=events, dist_label="distance from the person to the robot's front, m; the warning is drawn as a flashing beacon")
    t_hold = t_d + k["t_s"] + 0.8
    T1 = t_hold + 1.5
    vel = lambda t: (speed_after_demand(k, t_d)(t), 0.0)  # noqa: E731
    robot = integrate_pose(rx, ry, 0.0, vel, T0, T1)
    person = integrate_xy(px, ry, lambda t: ((-K, 0.0) if t_hold <= t and at(robot, t)[0] + ROBOT_L / 2 + 0.14 < px - K * (t - t_hold) - 0.0 else (0.0, 0.0)), T0, T1)
    person = [(t, max(x, at(robot, t)[0] + ROBOT_L / 2 + 0.14), y) for t, x, y in person]
    states, labels = _stop_states(k, t_d, T0, T1)
    return dict(k=k, T0=T0, T1=T1, HOLD=1.5, t_d=t_d, robot=robot, person=person, states=states, labels=labels, hand_out=True,
                dist=lambda t: _person_front(robot, person, t),
                events=_stop_events(k, t_d, "hand out: field violated") + [(t_hold, "walks up and holds the robot: no motion, latched (SF-05)", C["teal"])],
                dist_label="distance from the bystander to the robot's front, m; a hold on a powered drive would trip SF-06 within 1 s")
  if sid == "IS-13":
    b11 = next(b for b in src["budget"] if b["sf"] == "SF-11")
    t_r, t_b = b11["t_r"] / 1000.0, 0.30 - b11["t_r"] / 1000.0   # the arm's stopping time is TBC; 0.3 s total is the middle case of WP-S-04 §4.5
    T0 = -0.6
    rx, ry = SITE["station"]["robot"]
    mx, my = rx, ry + ARM_MOUNT
    ring = REACH + WALK_ARM
    px0 = mx - ring - 0.14 - K * 0.6
    person = integrate_xy(px0, my, walk(K, [(0.30, (1, 0))]), T0, 2.6)
    T1 = 2.6
    period = 4.0
    arm = [(t, 135.0 + 45.0 * math.cos(2 * math.pi * (min(t, t_r + t_b) - (t_r + t_b)) / period)) for t in samples(T0, T1)]
    robot = [(t, rx, ry, 90.0) for t in samples(T0, T1)]
    def tip(t):
      a = math.radians(at(arm, t)[0])
      return mx + REACH * math.cos(a), my + REACH * math.sin(a)
    return dict(k=None, T0=T0, T1=T1, HOLD=1.5, t_d=0.0, robot=robot, person=person, arm=arm, station=True, ring=(mx, my, ring),
                states=[(T0, C["amber"]), (0.0, C["red"]), (t_r, C["line"])], labels=[(T0, "arm moving", C["ink"]), (t_r, "torque off", C["amber"]), (t_r + t_b, "ARM AT REST", C["green"])],
                dist=lambda t: max(math.hypot(*(a - b for a, b in zip(at(person, t), tip(t)))) - 0.14, 0.0),
                events=[(0.0, "crosses the workspace ring", C["red"]), (b11["det"] / 1000.0, "station device", C["teal"]), (t_r, "arm safe torque off", C["red"]), (t_r + t_b, "arm at rest (0.13 s assumed)", C["green"]), (0.30, "person at the reach radius", C["amber"])],
                dist_label="distance from the person to the gripper, m; the ring is reach plus the walk during the stop (WP-S-04 §4.5)")
  if sid == "IS-14":
    b12 = next(b for b in src["budget"] if b["sf"] == "SF-12")
    t_r, t_b = b12["t_r"] / 1000.0, 0.05
    T0 = -0.6
    rx, ry = SITE["station"]["robot"]
    cx_col, cy_col = rx, ry + COLUMN_X
    px0 = cx_col - KEEP_CLEAR - 0.14 - K * 0.6
    stop_x = cx_col - ROBOT_W / 2 - 0.14
    person = integrate_xy(px0, cy_col, lambda t: ((K, 0.0) if px0 + K * (t - T0) < stop_x else (0.0, 0.0)), T0, 2.2)
    T1 = 2.2
    robot = [(t, rx, ry, 90.0) for t in samples(T0, T1)]
    lift_mm = 18.0
    return dict(k=None, T0=T0, T1=T1, HOLD=1.5, t_d=0.0, robot=robot, person=person, station=True, lift=(t_r + t_b, lift_mm), ring=(cx_col, cy_col, KEEP_CLEAR),
                states=[(T0, C["amber"]), (0.0, C["red"]), (t_r, C["line"])], labels=[(T0, "lift lowering 18 mm/s", C["ink"]), (t_r, "power off", C["amber"]), (t_r + t_b, "LIFT AT REST", C["green"])],
                dist=lambda t: max(stop_x - at(person, t)[0], 0.0),
                events=[(0.0, "steps onto the keep-clear zone", C["red"]), (b12["det"] / 1000.0, "keep-clear device", C["teal"]), (t_r, "lift power removed", C["red"]), (t_r + t_b, f"lift at rest, {lift_mm * (t_r + t_b):.0f} mm lower (brake 0.05 s assumed)", C["green"]), ((stop_x - px0) / K + T0, "person at the column", C["amber"])],
                dist_label="distance from the person to the base's side, m; the carriage is the hazard above them")
  if sid == "IS-15":
    k = kinematics(src, "FS-4")
    T0 = -0.5
    rx, ry = 11.3, 11.15
    bx, by = 12.2, ry + ROBOT_W / 2 + 0.14 + 0.15
    a_cmd = 1.0
    t_dec = (bx - rx - k["v"] ** 2 / (2 * a_cmd)) / k["v"] + T0
    t_stop = t_dec + k["v"] / a_cmd
    t_turn_end = t_stop + math.pi / 2 / TURN_RATE
    T1 = t_turn_end + 0.5
    def vel(t):
      if t < t_dec:
        return (k["v"], 0.0)
      if t < t_stop:
        return (max(k["v"] - a_cmd * (t - t_dec), 0.0), 0.0)
      if t < t_turn_end:
        return (0.0, math.degrees(TURN_RATE))
      return (0.0, 0.0)
    robot = integrate_pose(rx, ry, 0.0, vel, T0, T1)
    person = [(t, bx, by) for t in samples(T0, T1)]
    def load(t):
      x, y, yaw = at(robot, t)
      a = math.radians(yaw)
      return x + 0.64 * math.cos(a), y + 0.64 * math.sin(a)
    dist = lambda t: max(math.hypot(*(a - b for a, b in zip(load(t), (bx, by)))) - 0.2 - 0.14, 0.0)  # noqa: E731
    t_c = next((t for t in samples(T0, T1) if t > t_stop and dist(t) <= 0.0), T1)
    return dict(k=k, T0=T0, T1=T1, HOLD=1.5, t_d=None, robot=robot, person=person, sweep=True,
                states=[(T0, C["teal"])], labels=[(T0, f"{k['v']:.2f} m/s, carry pose", C["ink"]), (t_dec, "planned stop", C["ink"]), (t_stop, "turn in place 0.5 rad/s", C["amber"]), (t_turn_end, "STANDSTILL", C["green"])],
                dist=dist, events=[(None, "bystander beside the path: outside FS-4", C["amber"]), (t_dec, "planned stop at the bay", C["teal"]), (t_stop, "turn in place: the load sweeps 0.85 m at head height", C["amber"]),
                                   (t_c, "load reaches the bystander: no demand (above the plane)", C["red"]), (t_turn_end, "turn complete", C["green"])],
                dist_label="distance from the load's edge to the bystander, m; the field is ahead and the sweep is above the scan plane (CA-07, SR-02.10)")
  raise KeyError(sid)


# ------------------------------------------------------------------------------------------------------ rendering a loop
def _discrete(attr, states, kt, dur, T0):
  vals, keys = [], []
  for i, (t, v) in enumerate(states):
    if i == 0:
      vals.append(v); keys.append("0")
    else:
      vals.append(v); keys.append(f"{kt(t):.4f}")
  vals.append(vals[-1]); keys.append("1")
  return f'<animate attributeName="{attr}" values="{";".join(vals)}" keyTimes="{";".join(keys)}" dur="{dur:.2f}s" calcMode="discrete" repeatCount="indefinite"/>'


def _anim_translate(samples_, pl, kt, dur, ref):
  """animateTransform translate from (t, x, y[, yaw]) samples, relative to the reference point ref (metres)."""
  X0, Y0 = pl.P(*ref)
  vals, keys = [], []
  for s_ in samples_:
    X, Y = pl.P(s_[1], s_[2])
    vals.append(f"{X - X0:.2f},{Y - Y0:.2f}"); keys.append(f"{kt(s_[0]):.4f}")
  vals.append(vals[-1]); keys.append("1")
  return f'<animateTransform attributeName="transform" type="translate" values="{";".join(vals)}" keyTimes="{";".join(keys)}" dur="{dur:.2f}s" repeatCount="indefinite" calcMode="linear"/>'


def _anim_rotate(samples_, kt, dur, yaw0, idx=3):
  vals = [f"{-(s_[idx] - yaw0):.2f}" for s_ in samples_] + [f"{-(samples_[-1][idx] - yaw0):.2f}"]
  keys = [f"{kt(s_[0]):.4f}" for s_ in samples_] + ["1"]
  return f'<animateTransform attributeName="transform" type="rotate" values="{";".join(vals)}" keyTimes="{";".join(keys)}" dur="{dur:.2f}s" repeatCount="indefinite" calcMode="linear"/>'


def _show(kt, dur, t_on, t_off=None):
  """An opacity animation: hidden before t_on, shown after (and hidden again after t_off)."""
  if t_off is None:
    return f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{kt(t_on):.4f};{kt(t_on) + 0.0005:.4f};1" dur="{dur:.2f}s" repeatCount="indefinite"/>'
  return f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{kt(t_on):.4f};{kt(t_on) + 0.0005:.4f};{kt(t_off):.4f};{kt(t_off) + 0.0005:.4f};1" dur="{dur:.2f}s" repeatCount="indefinite"/>'


def fig_loop(src: dict, sid: str) -> str:
  sc = SCENES[sid]
  if sc.get("still"):
    return fig_still(src, sid)
  s = build(src, sid)
  row = src["scenes"][sid]
  T0, T1, HOLD = s["T0"], s["T1"], s["HOLD"]
  DUR = (T1 - T0) + HOLD
  kt = lambda t: min(max((t - T0) / DUR, 0.0), 1.0)  # noqa: E731
  W, H = 1200, 980 + (36 if len(s["events"]) > 5 else 0)
  M = 150.0
  uid = f"sim-{sid.lower()}"
  cx0, cy0, cw, ch = sc["crop"]
  px, py = 40, 96
  pw, ph = cw * M, ch * M
  pl = Plan(px, py, M, uid, origin=(cx0, cy0), height=ch, sprites=src["sprites"])
  rating = rating_for(src, sid)
  k = s.get("k")
  fid = sc["field"]
  f = src["fields"][fid] if fid else None
  case = (f"{fid} ({f['config']}, {f['case']}: a = {f['a']:g} m/s², unmeasured)" if f else "CFG-002, the base at rest")
  body = [text(40, 36, f"{sid} · {row['hazard']} · {row['zone']} · {row['task']}: {sc['title']}", 20, C["ink"], 700),
          text(40, 60, f"Looping view: a fixed {cw:g} × {ch:g} m crop of the warehouse plan; {case}; t = {T0:g} s to {T1:.2f} s, then a {HOLD:g} s hold", 12, C["muted"]),
          text(40, 78, f"The person is {row['who']}, closest {row['closest'].split(' if')[0]} if nothing stops the robot (WP-C-06 §2). A viewer that shows the SVG as a still shows t = {T0:g} s.", 12, C["muted"]),
          rect(px, py, pw, ph, C["floor"], C["wall"], 0, 3),
          f'<clipPath id="{uid}-crop"><rect x="{px}" y="{py}" width="{pw:.1f}" height="{ph:.1f}"/></clipPath>',
          f'<g clip-path="url(#{uid}-crop)">']
  body += pl.floor(src, with_labels=False)
  for i, (x, y, w, h) in enumerate(SITE["racks"]):
    if cy0 + 0.15 <= y + h / 2 <= cy0 + ch - 0.15 and x < cx0 + cw and x + w > cx0:
      X, Y = pl.P(max(x, cx0), y + h)
      body.append(text(X + 8, Y + h * M / 2 + 4, f"RACK {i + 1}", 10, "#E8EBED", 700))
  robot = s["robot"]
  r0 = robot[0]
  RX, RY = pl.P(r0[1], r0[2])
  # static props
  if s.get("reverse_strip") is not None:
    body.append(pl.R(r0[1] + ROBOT_L / 2, r0[2] - ROBOT_W / 2, 0.7, ROBOT_W, f"url(#{uid}-hatchred)", C["red"], 0, 1))
    X, Y = pl.P(r0[1] + ROBOT_L / 2 + 0.35, r0[2] - ROBOT_W / 2 - 0.12)
    body.append(text(X, Y, "blind reverse 0.7 m on odometry (GAP-35)", 9.5, C["red"], 700, "middle"))
  if s.get("map_ghost"):
    body.append(f'<g opacity="0.3">{_anim_translate(robot, pl, kt, DUR, (r0[1], r0[2]))}' + "".join(pl.sprite(r0[1] - s["map_ghost"], r0[2], 1, 1.0, sc["kind"])) + "</g>")
    X, Y = pl.P(r0[1] - s["map_ghost"], r0[2] - ROBOT_W / 2 - 0.12)
    body.append(f'<text x="{X:.1f}" y="{Y:.1f}" font-family="{FONT}" font-size="10" font-weight="700" fill="{C["blue"]}" text-anchor="middle">where the map says it is, {s["map_ghost"]:g} m behind'
                f'{_anim_translate(robot, pl, kt, DUR, (r0[1], r0[2]))}</text>')
    ox, oy = 4.9, 3.6
    body.append(pl.R(ox - 0.65, oy - 0.1, 0.3, 0.2, "#DCE8F5", C["blue"], 2, 1.2))
    X, Y = pl.P(ox - 0.5, oy + 0.3)
    body.append(text(X, Y, "pendant screen", 9, C["blue"], 700, "middle"))
  if s.get("station"):
    mx, my, rr = s["ring"]
    MX, MY = pl.P(mx, my)
    body.append(f'<circle cx="{MX:.1f}" cy="{MY:.1f}" r="{rr * M:.1f}" fill="{C["amber"]}" fill-opacity="0.10" stroke="{C["amber"]}" stroke-width="2" stroke-dasharray="6,3">{_discrete("stroke", s["states"], kt, DUR, T0)}</circle>')
    if sid == "IS-13":
      body.append(circle(MX, MY, REACH * M, "none", C["teal"], 1.2, "4,3"))
      body.append(text(MX + REACH * M + 4, MY - 6, f"reach {REACH:g} m", 9.5, C["teal"], 700))
      body.append(text(MX + rr * M + 6, MY - 0.25 * M, f"workspace ring {rr:.2f} m = reach + walk {WALK_ARM:g}", 10, C["amber"], 700))
    else:
      body.append(text(MX + rr * M + 6, MY - 0.25 * M, f"keep-clear {rr:g} m (SR-12.03; radius assumed)", 10, C["amber"], 700))
  # the robot group: translated and rotated by the samples; the field and the status label ride with it
  body.append(f'<g>{_anim_translate(robot, pl, kt, DUR, (r0[1], r0[2]))}<g transform="translate({RX:.1f},{RY:.1f})"><g>{_anim_rotate(robot, kt, DUR, 0.0)}')
  if f and not s.get("no_field"):
    hw = (ROBOT_W / 2 + src["Z"]) * M
    fx0 = ROBOT_L / 2 * M
    x = fx0
    terms = ((k["d_r"], C["red"]), (k["d_b"], C["amber"]), (k["walk"], C["teal"]), (k["Z"], C["blue"])) if k and k.get("walk") is not None else ()
    for length, col in terms:
      fill = f"url(#{uid}-hatch)" if col == C["amber"] else col
      body.append(rect(x, -hw, length * M, 2 * hw, fill, "none", 0, 1, "", 'fill-opacity="0.22"' if col != C["amber"] else ""))
      x += length * M
    body.append(f'<rect x="{fx0:.1f}" y="{-hw:.1f}" width="{f["L"] * M:.1f}" height="{2 * hw:.1f}" fill="none" stroke="{C["teal"]}" stroke-width="2" stroke-dasharray="6,3">{_discrete("stroke", s["states"], kt, DUR, T0)}</rect>')
    body.append(text(fx0 + 4, hw + 14, f"{fid} {f['L']:.2f} m" + (f" = {k['d_r']:.3f} + {k['d_b']:.3f} coast + {k['walk']:.2f} walk + {k['Z']:.2f}" if k else ""), 10, C["teal"], 700))
  if s.get("masked"):
    for sy in (-1, 1):
      body.append(f'<path d="M {-ROBOT_L / 2 * M:.1f},{sy * ROBOT_W / 2 * M:.1f} L {ROBOT_L / 2 * M:.1f},{sy * ROBOT_W / 2 * M:.1f} L {ROBOT_L / 2 * M:.1f},{sy * (ROBOT_W / 2 + 0.5) * M:.1f} L {-ROBOT_L / 2 * M:.1f},{sy * (ROBOT_W / 2 + 0.5) * M:.1f} Z" fill="{C["dim"]}" fill-opacity="0.25" stroke="{C["dim"]}" stroke-dasharray="3,3"/>')
    body.append(text(0, -(ROBOT_W / 2 + 0.5) * M - 6, "side sectors masked in the scan (GAP-35)", 9.5, C["dim"], 700, "middle"))
  if s.get("sweep"):
    body.append(circle(0, 0, SWEEP * M, C["amber"], C["amber"], 1.2, "4,3", 'fill-opacity="0.10"'))
    body.append(text(0, -SWEEP * M - 6, f"load sweep at head height, {SWEEP:g} m", 9.5, C["amber"], 700, "middle"))
  body += pl.sprite(r0[1], r0[2], 1, 1.0, sc["kind"], at_origin=True)
  if s.get("rear_red"):
    body.append(rect(-ROBOT_L / 2 * M - 0.045 * M, -ROBOT_W / 2 * M + 2, 0.045 * M, ROBOT_W * M - 4, C["red"], "none", 2))
  if s.get("arm"):
    AX = ARM_MOUNT * M
    body.append(f'<g transform="translate({AX:.1f},0)"><g>{_anim_rotate(s["arm"], kt, DUR, 0.0, idx=1)}'
                f'<line x1="0" y1="0" x2="{0.33 * M:.1f}" y2="{-0.06 * M:.1f}" stroke="{C["ink"]}" stroke-width="5" stroke-linecap="round"/>'
                f'<line x1="{0.33 * M:.1f}" y1="{-0.06 * M:.1f}" x2="{REACH * M:.1f}" y2="0" stroke="{C["ink"]}" stroke-width="4" stroke-linecap="round"/>'
                f'<rect x="{REACH * M - 6:.1f}" y="-5" width="10" height="10" fill="{C["teal"]}"/></g></g>')
  if s.get("warn"):
    t_on, t_off = s["warn"]
    body.append(f'<circle cx="0" cy="{-(ROBOT_W / 2 + 0.06) * M:.1f}" r="7" fill="{C["amber"]}" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;1;0;1;0;1;0;1;0;0" keyTimes="0;{kt(t_on):.4f};{kt(t_on) + 0.001:.4f};{kt(t_on + 0.5):.4f};{kt(t_on + 1.0):.4f};{kt(t_on + 1.25):.4f};{kt(t_on + 1.5):.4f};{kt(t_on + 1.75):.4f};{kt(t_off - 0.05):.4f};{kt(t_off):.4f};1" dur="{DUR:.2f}s" repeatCount="indefinite"/></circle>')
  body.append("</g>")   # rotation
  # the status label (not rotated)
  for i, (t_on, lab, col) in enumerate(s["labels"]):
    t_off = s["labels"][i + 1][0] if i + 1 < len(s["labels"]) else None
    anim = _show(kt, DUR, t_on, t_off) if t_on > T0 else (_show(kt, DUR, T0 - 1, t_off).replace('values="0;0;1;1;0;0"', 'values="1;1;1;1;0;0"') if t_off is not None else "")
    body.append(f'<text x="0" y="{-0.42 * M - (0.5 * M if s.get("masked") else 0):.1f}" font-family="{MONO}" font-size="11" font-weight="700" fill="{col}" text-anchor="middle" opacity="{1 if t_on <= T0 else 0}">{escape(lab)}{anim}</text>')
  body.append("</g></g>")   # translate
  # the person
  person = s["person"]
  p0 = person[0]
  who = s.get("who") or row["who"]
  body.append(f'<g>{_anim_translate(person, pl, kt, DUR, (p0[1], p0[2]))}')
  if s.get("child"):
    body += pl.worker(p0[1], p0[2], C["vest"], f"{who.split(',')[0]}, below the plane", scale=0.65)
  else:
    body += pl.worker(p0[1], p0[2], None, f"{who}, K = {src['K']:g} m/s" if any(abs(a[1] - b[1]) + abs(a[2] - b[2]) > 1e-6 for a, b in zip(person, person[1:])) else who)
  if s.get("hand_out"):
    PX, PY = pl.P(p0[1], p0[2])
    body.append(line(PX - 0.14 * M, PY, PX - 0.45 * M, PY, C["skin"], 4))
  body.append("</g>")
  if s.get("lift"):
    t_stop, mm = s["lift"]
    LX, LY = pl.P(cx0 + 0.15, cy0 + ch - 0.15)
    body += [rect(LX, LY, 1.1 * M, 0.26 * M, C["bg"], C["stroke"], 4), text(LX + 8, LY + 15, "lift carriage: lowering 18 mm/s", 9.5, C["ink"], 700)]
    body.append(f'<text x="{LX + 8:.1f}" y="{LY + 30:.1f}" font-family="{MONO}" font-size="10" font-weight="700" fill="{C["green"]}" opacity="0">stopped, {mm * t_stop:.0f} mm after the demand{_show(kt, DUR, t_stop)}</text>')
  body.append('</g>')
  if rating:
    body += pl.chip(cx0 + cw - 1.0, cy0 + ch - 0.25, f"{rating['hazard']} {sid}", f"PLr {rating['plr']}", C["teal"])
  else:
    body += pl.chip(cx0 + cw - 1.0, cy0 + ch - 0.25, f"{row['hazard'].split(',')[0]} {sid}", "not rated", C["muted"])
  # events, time strip, distance plot
  ey = py + ph + 24
  evs = s["events"]
  for i, (t, lab, col) in enumerate(evs[:5]):
    X = 40 + i * 232
    anim = "" if t is None else f'<animate attributeName="opacity" values="0.25;0.25;1;1" keyTimes="0;{kt(t):.4f};{kt(t) + 0.0005:.4f};1" dur="{DUR:.2f}s" repeatCount="indefinite"/>'
    label = lab if t is None else f"{t:.2f} s  {lab}"
    body.append(f'<g opacity="{1 if t is None else 0.25}">{anim}' + rect(X, ey, 216, 30, C["panel"], col, 6, 1.4) + text(X + 10, ey + 20, _fit(label, 216 - 20, 10.5), 10.5, col, 700, family=MONO) + '</g>')
  if len(evs) > 5:
    for i, (t, lab, col) in enumerate(evs[5:10]):
      X = 40 + i * 232
      anim = "" if t is None else f'<animate attributeName="opacity" values="0.25;0.25;1;1" keyTimes="0;{kt(t):.4f};{kt(t) + 0.0005:.4f};1" dur="{DUR:.2f}s" repeatCount="indefinite"/>'
      label = lab if t is None else f"{t:.2f} s  {lab}"
      body.append(f'<g opacity="{1 if t is None else 0.25}">{anim}' + rect(X, ey + 36, 216, 30, C["panel"], col, 6, 1.4) + text(X + 10, ey + 56, _fit(label, 216 - 20, 10.5), 10.5, col, 700, family=MONO) + '</g>')
  sy = ey + (70 if len(evs) <= 5 else 106)
  x0, x1 = 60, W - 60
  Xt = lambda t: x0 + (x1 - x0) * (t - T0) / (T1 - T0)  # noqa: E731
  body += [text(40, sy - 16, "time, scene seconds", 10, C["muted"], 600), line(x0, sy, x1, sy, C["line"], 2)]
  marks = [(T0, f"{T0:g}")] + [(t, f"{t:.2f} {lab.split(':')[0].split(',')[0][:18]}") for t, lab, _ in evs if t is not None and T0 < t < T1] + [(T1, f"{T1:.2f} hold")]
  placed = []
  for j, (t, lab) in enumerate(marks):
    X = Xt(t)
    body.append(line(X, sy - 7, X, sy + 7, C["ink"], 1.5))
    row_ = next(r for r in range(4) if all(abs(X - x_) > _w(lab, 9) / 2 + 40 for x_, r_ in placed if r_ == r))
    placed.append((X, row_))
    body.append(text(X, sy + 22 + 12 * row_, lab, 9, C["muted"], 600, "middle", MONO))
  cursor = (f'<animateTransform attributeName="transform" type="translate" values="0,0;{x1 - x0:.1f},0;{x1 - x0:.1f},0" keyTimes="0;{kt(T1):.4f};1" '
            f'dur="{DUR:.2f}s" repeatCount="indefinite" calcMode="linear"/>')
  body.append(f'<line x1="{x0}" y1="{sy - 16}" x2="{x0}" y2="{sy + 10}" stroke="{C["red"]}" stroke-width="2.5">{cursor}</line>')
  gy0, gy1 = sy + 70, sy + 170
  dist_label = s.get("dist_label", "distance from the person to the robot's front, m (planning case); the red line is the field edge, the cursor the time shown")
  body += [rect(40, gy0 - 12, W - 80, 130, C["panel"], C["stroke"], 6), text(52, gy0 + 2, dist_label, 10, C["muted"], 600)]
  dist = s["dist"]
  dmax = 2.6
  pts = []
  for t in samples(T0, T1):
    pts.append((Xt(t), gy1 - min(dist(t), dmax) / dmax * (gy1 - gy0 - 20)))
  body.append('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="none" stroke="{C["teal"]}" stroke-width="2"/>')
  if f and "dist_label" not in s:
    yL = gy1 - f["L"] / dmax * (gy1 - gy0 - 20)
    body += [line(x0, yL, x1, yL, C["red"], 1, "4,3"), text(x0 - 6, yL + 4, f"{f['L']:.2f}", 9, C["red"], 600, "end", MONO)]
  body += [text(x0 - 6, gy1 + 4, "0", 9, C["muted"], 600, "end", MONO), f'<line x1="{x0}" y1="{gy0 + 8}" x2="{x0}" y2="{gy1}" stroke="{C["ink"]}" stroke-width="1.5">{cursor}</line>']
  dmin = min(dist(t) for t in samples(T0, T1))
  note = s.get("note") or (f"closest approach in the planning case: {dmin:.2f} m" if dmin > 0.005 else "contact in the planning case: the distance reaches zero")
  body.append(text(x1, gy1 + 16, note, 10, C["teal"] if dmin > 0.005 else C["red"], 600, "end"))
  body.append(text(W - 32, H - 52, "Generated by assurance/sim/figures/fig_sim_is.py", 9.5, C["dim"], anchor="end"))
  band_note = (f"Kinematic motion from WP-S-04 v0.2 planning values (t_r {k['t_r']:g} s, a = {k['a']:g} m/s² unmeasured, C = 0, K = {src['K']:g} m/s). A loop shows a situation; it does not show that a measure works."
               if k else f"Kinematic motion from WP-S-04 v0.2 planning values (t_r 0.17 s, the arm's and the lift brake's stopping times assumed, K = {src['K']:g} m/s). A loop shows a situation; it does not show that a measure works.")
  body += band(W, H, band_note)
  desc = (f"Looping top view of {sid}: {sc['title']}. A fixed crop of the warehouse plan with the robot, its field where one applies, the person on their path at walking speed, "
          f"the events lighting up below, a cursor on a time strip and a plot of the distance between the person and the robot, which reaches {dmin:.2f} m in the planning case.")
  return svg(W, H, uid, f"{sid}: {sc['title']}, looping", desc, body, sprites=list(pl.used.items()))


def _fit(s: str, width: float, size: float) -> str:
  return s if len(s) * size * 0.6 <= width else s[: int(width / (size * 0.6)) - 1] + "…"


# ------------------------------------------------------------------------------------------------------ the stills
STILLS = {
  "IS-07": dict(robot=(22.2, 11.3, 0), people=[((21.3, 11.9), "technician", C["blue"])],
                notes=["charger connected: the interlock opens the safety chain (WP-H-02 §3.6)", "a command arrives from the network: no motion, the chain is open",
                       "mains never paralleled with the battery (H-08)"], cable=((21.45, 11.9), (22.75, 11.3))),
  "IS-08": dict(robot=(9.6, 11.15, 0), people=[((9.6, 11.15), "sits on the top plate", C["vest"]), ((8.95, 11.15), "pushes", C["vest"])],
                notes=["no field demand: the robot is a load, not an obstacle", "payload and stability limits (WP-H-08); information for use",
                       "SF-06 stall detector trips when the wheels are blocked (1 s)"], arrow=((8.6, 11.15), (9.1, 11.15))),
  "IS-11": dict(robot=(9.0, 11.15, 0), moving=True, people=[((11.4, 10.55), "operator, tablet in hand", C["blue"])],
                notes=["on-screen E-STOP pressed: no effect, the robot drives on at 0.20 m/s", "SR-01.09: the screen control is not labelled as an emergency stop",
                       "the physical E-stop (SF-01, E1) is within reach: 50 ms to power off"], screen=(11.75, 10.55)),
}


def fig_still(src: dict, sid: str) -> str:
  sc, st = SCENES[sid], STILLS[sid]
  row = src["scenes"][sid]
  W, H = 1200, 760
  M = 150.0
  uid = f"sim-{sid.lower()}"
  cx0, cy0, cw, ch = sc["crop"]
  px, py = 40, 96
  pw, ph = cw * M, ch * M
  pl = Plan(px, py, M, uid, origin=(cx0, cy0), height=ch, sprites=src["sprites"])
  rating = rating_for(src, sid)
  body = [text(40, 36, f"{sid} · {row['hazard']} · {row['zone']} · {row['task']}: {sc['title']}", 20, C["ink"], 700),
          text(40, 60, f"Still: a fixed {cw:g} × {ch:g} m crop of the warehouse plan; nothing moves in this scenario that a kinematic loop could show", 12, C["muted"]),
          text(40, 78, f"The person is {row['who']}, closest {row['closest'].split(' if')[0]} (WP-C-06 §2); the measure needed: {row['measure'][:110]}", 12, C["muted"]),
          rect(px, py, pw, ph, C["floor"], C["wall"], 0, 3),
          f'<clipPath id="{uid}-crop"><rect x="{px}" y="{py}" width="{pw:.1f}" height="{ph:.1f}"/></clipPath>',
          f'<g clip-path="url(#{uid}-crop)">']
  body += pl.floor(src, with_labels=False)
  rx, ry, yaw = st["robot"]
  if st.get("moving"):
    f = src["fields"][sc["field"]]
    body.append(pl.R(rx + ROBOT_L / 2, ry - ROBOT_W / 2 - src["Z"], f["L"], ROBOT_W + 2 * src["Z"], C["teal"], C["teal"], 0, 1.5, "6,3", 'fill-opacity="0.16"'))
    X, Y = pl.P(rx + ROBOT_L / 2 + f["L"] + 0.1, ry)
    body.append(text(X, Y + 4, "→ 0.20 m/s, continues", 11, C["red"], 700, family=MONO))
  body += pl.sprite(rx, ry, 1, 1.0, sc["kind"])
  if st.get("cable"):
    (ax, ay), (bx, by) = st["cable"]
    AX, AY = pl.P(ax, ay); BX, BY = pl.P(bx, by)
    body.append(f'<path d="M {AX:.1f},{AY:.1f} Q {(AX + BX) / 2:.1f},{AY + 30:.1f} {BX:.1f},{BY:.1f}" fill="none" stroke="{C["ink"]}" stroke-width="3"/>')
  if st.get("arrow"):
    (ax, ay), (bx, by) = st["arrow"]
    AX, AY = pl.P(ax, ay); BX, BY = pl.P(bx, by)
    body.append(line(AX, AY, BX, BY, C["red"], 3, arrow=True).replace("url(#arrow)", f"url(#{uid}-arrow)"))
  if st.get("screen"):
    sx, sy_ = st["screen"]
    body.append(pl.R(sx, sy_ - 0.1, 0.28, 0.2, "#DCE8F5", C["blue"], 2, 1.2))
    X, Y = pl.P(sx + 0.14, sy_)
    body.append(rect(X - 10, Y - 6, 20, 12, C["red"], "none", 2))
  for (x, y), label, col in st["people"]:
    body += pl.worker(x, y, col, label)
  X, Y = pl.P(cx0 + 0.2, cy0 + 0.25)
  for i, n in enumerate(reversed(st["notes"])):
    body.append(rect(X - 6, Y - 16 - i * 22, _w(n, 11) + 16, 20, C["bg"], C["stroke"], 4, 1, "", 'fill-opacity="0.92"'))
    body.append(text(X + 2, Y - 2 - i * 22, n, 11, C["ink"], 600))
  body.append("</g>")
  if rating:
    body += pl.chip(cx0 + cw - 1.0, cy0 + ch - 0.25, f"{rating['hazard']} {sid}", f"PLr {rating['plr']}", C["teal"])
  else:
    body += pl.chip(cx0 + cw - 1.0, cy0 + ch - 0.25, f"{row['hazard'].split(',')[0]} {sid}", "not rated", C["muted"])
  body.append(text(W - 32, H - 52, "Generated by assurance/sim/figures/fig_sim_is.py", 9.5, C["dim"], anchor="end"))
  body += band(W, H, "Drawn to the WP-C-06 §2 row; nothing here is measured. A still shows a situation; it does not show that a measure works.")
  return svg(W, H, uid, f"{sid}: {sc['title']}", f"Top view of {sid}: {sc['title']}. A fixed crop of the warehouse plan with the robot, the people of the row and three notes naming the measures.", body, sprites=list(pl.used.items()))


def _w(s: str, size: float) -> float:
  return len(s) * size * 0.56


# ------------------------------------------------------------------------------------------------------ the tour
# One loop of the whole plan (ideas-2d-views.md §4): CFG-002 leaves the dock, crawls out of the dock lane, takes the
# cross-aisle and aisle 2 to the station, picks a tote, carries it round to a drop shelf on rack 1 and docks again.
# The speed limit of each step comes from the zone the robot is in (WP-C-02 §2), the field set from the speed and
# the pose (WP-S-04 §4.1, the CFG-002 braked rows and FS-4 in the carry pose), so the set switches where the zone
# boundaries are. One situation is played on the way, the crossing of IS-01 with the stop, the wait and the resume
# after the warning of IS-10; the others along the route light up as the robot reaches them. Transit runs faster
# than real time (the factor is printed), the played situation and the station work run at or near real time.
TOUR_DT = 0.05
A_PLAN = 0.5                     # m/s², the configured acceleration and the planned deceleration (WP-S-04 §5)
TOUR_DOCKED = (22.9 - 0.045 - ROBOT_L / 2 - 0.02, 13.2)   # nose in, the front bumper 20 mm off the dock face
TOUR_ROUTE = [
  ("hold", 1.0, "docked, charging contacts made"),
  ("reverse", 0.7, "undock: reverse 0.7 m on odometry"),
  ("turn", 180.0), ("drive", (17.2, 13.2)), ("turn", 270.0), ("drive", (17.2, 8.1)), ("turn", 180.0),
  ("drive", (12.6, 8.1)), ("turn", 90.0),
  ("work", 4.0, "carry", "station: the arm picks a tote"),
  ("turn", 180.0), ("drive", (6.2, 8.1)), ("turn", 90.0), ("drive", (6.2, 11.15)), ("turn", 0.0), ("drive", (15.4, 11.15)), ("turn", 90.0),
  ("work", 2.5, "stowed", "drop shelf: the arm places the tote"),
  ("turn", 0.0), ("drive", (17.2, 11.15)), ("turn", 90.0), ("drive", (17.2, 13.2)), ("turn", 0.0), ("drive", TOUR_DOCKED),
]
TOUR_CROSSER = dict(x=14.4, y0=9.33, y1=7.38, trigger=15.0)   # IS-01: picks at the rack 2 face, steps across aisle 2 to rack 3 when the robot's front passes x = 15.0
TOUR_BYSTANDER = (10.5, 11.83)                                 # IS-15: stands at the rack 1 face beside the carry route
TOUR_SPEEDUP = {"hold": 2.0, "reverse": 8.0, "turn": 4.0, "Z3": 16.0, "Z2": 10.0, "event": 1.0, "work": 1.5, "muted": 8.0}
TOUR_CHIPS = [("IS-04", "undock: reverse under the bumper only"), ("IS-02", "the turn at the rack end: a blind corner"), ("IS-01", "a person crosses ahead: protective stop"),
              ("IS-10", "the wait, the reset and the 2 s warning"), ("IS-13", "the arm works inside the station ring"), ("IS-15", "carrying past a bystander"),
              ("IS-05", "the last metre to the dock: field muted")]


def tour_zone(x: float, y: float) -> str:
  dx, dy, dw, dh = SITE["dock_lane"]
  if dx <= x <= dx + dw and dy <= y <= dy + dh:
    return "Z3"
  cx, cy, cw, ch = SITE["charge_bay"]
  if cx <= x <= cx + cw and cy <= y <= cy + ch:
    return "Z4"
  return "Z2"


def tour_sets(src: dict) -> dict:
  """The field set for each (zone speed, pose): the CFG-002 braked rows of §4.1 by speed, FS-4 for the carry pose."""
  rows = {fid: f for fid, f in src["fields"].items() if fid.startswith("FS-") and f["config"] == "CFG-002"}
  by_speed = {f["v"]: fid for fid, f in rows.items() if f["case"] == "braked" and fid != "FS-4"}
  return {"rows": rows, "by_speed": by_speed, "carry": "FS-4"}


def build_tour(src: dict) -> dict:
  """Integrate the route at TOUR_DT. Returns samples (t, x, y, yaw), the state changes, the crosser's samples and the warp."""
  K, Z = src["K"], src["Z"]
  zone_v = {z: float(re.search(r"(\d+\.\d+) m/s", src["zones"][z]["speed"]).group(1)) for z in ("Z2", "Z3")}
  sets = tour_sets(src)
  sp = scanner_path(src)
  t_r = sp["t_r"] / 1000.0
  a_brake = sets["rows"][sets["by_speed"][zone_v["Z2"]]]["a"]
  dock_face = SITE["dock"][0]
  x, y = TOUR_DOCKED
  yaw, v, pose = 0.0, 0.0, "stowed"
  t = 0.0
  robot = [(0.0, x, y, yaw)]
  st = {"set": [], "mode": [], "pose": [(0.0, "stowed")], "arm": [(0.0, None)], "speed": [], "zone": [], "factor": [], "colour": []}
  warp = [(0.0, 0.0)]
  a_t = 0.0
  person = None
  ev = {}

  def push(key, val):
    if not st[key] or st[key][-1][1] != val:
      st[key].append((t, val))

  def field_now(reverse=False):
    if reverse:
      return None, False
    fid = sets["carry"] if pose == "carry" else sets["by_speed"][zone_v[tour_zone(x, y)]]
    muted = tour_zone(x, y) == "Z3" and abs(((yaw + 180) % 360) - 180) < 1 and x + ROBOT_L / 2 >= dock_face - 1.0
    return fid, muted

  def step(vx, wz, factor, mode, reverse=False):
    nonlocal x, y, yaw, t, a_t
    yaw += wz * TOUR_DT
    s = -1.0 if reverse else 1.0
    x += s * vx * math.cos(math.radians(yaw)) * TOUR_DT
    y += s * vx * math.sin(math.radians(yaw)) * TOUR_DT
    t += TOUR_DT
    a_t += TOUR_DT / factor
    warp.append((t, a_t))
    robot.append((t, x, y, yaw))
    fid, muted = field_now(reverse)
    push("set", (fid, muted))
    push("mode", mode)
    push("speed", round(vx, 3))
    push("zone", tour_zone(x, y))
    push("factor", factor)
    if person is not None:
      person["samples"].append((t, person["x"], person["y"]))

  for act in TOUR_ROUTE:
    kind = act[0]
    if kind == "hold":
      n = int(round(act[1] / TOUR_DT))
      for _ in range(n):
        step(0.0, 0.0, TOUR_SPEEDUP["hold"], act[2])
    elif kind == "reverse":
      vr = min(zone_v["Z3"], 0.05)
      n = int(round(act[1] / vr / TOUR_DT))
      for _ in range(n):
        step(vr, 0.0, TOUR_SPEEDUP["reverse"], act[2], reverse=True)
    elif kind == "turn":
      target = act[1]
      d = ((target - yaw + 180) % 360) - 180
      w = math.degrees(TURN_RATE) * (1 if d > 0 else -1)
      n = int(round(abs(d) / abs(w) / TOUR_DT))
      for i in range(n):
        step(0.0, d / n / TOUR_DT, TOUR_SPEEDUP["turn"], "turn in place, 0.5 rad/s" + (", the load sweeps (IS-15)" if pose == "carry" else ""))
      yaw = target % 360 if target % 360 <= 180 else target % 360 - 360
      robot[-1] = (t, x, y, yaw)
    elif kind == "work":
      n = int(round(act[1] / TOUR_DT))
      for i in range(n):
        arm = 45.0 * math.sin(2 * math.pi * (i + 1) / n)
        push("arm", round(arm, 2))
        step(0.0, 0.0, TOUR_SPEEDUP["work"], act[3])
      push("arm", None)
      pose = act[2]
      push("pose", pose)
    elif kind == "drive":
      tx, ty = act[1]
      c, s_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
      stopped_for = None
      while True:
        rem = (tx - x) * c + (ty - y) * s_
        if rem <= 1e-4:
          break
        # the event: IS-01 is spawned on aisle 2, westbound, when the front passes the trigger
        if "spawn" not in ev and abs(yaw - 180) < 1 and abs(y - TOUR_CROSSER["y0"] + 1.23) < 0.3 and x - ROBOT_L / 2 <= TOUR_CROSSER["trigger"]:
          ev["spawn"] = t
          person = {"x": TOUR_CROSSER["x"], "y": TOUR_CROSSER["y0"], "samples": [(t, TOUR_CROSSER["x"], TOUR_CROSSER["y0"])]}
        if person is not None and person["y"] > TOUR_CROSSER["y1"]:
          person["y"] = max(person["y"] - K * TOUR_DT, TOUR_CROSSER["y1"])
        fid, muted = field_now()
        L = sets["rows"][fid]["L"]
        # the demand, the stop, the clear, the reset and the warning
        if person is not None and "demand" not in ev and not muted and in_field((x, y, yaw), person["x"], person["y"], L, ROBOT_W / 2 + Z):
          ev["demand"] = t
        if "demand" in ev and "go" not in ev:
          if t < ev["demand"] + t_r:
            vnew, mode = v, "field violated"
          elif v > 0:
            vnew, mode = max(v - a_brake * TOUR_DT, 0.0), "power removed: braking"
            if vnew == 0.0:
              ev["standstill"] = t + TOUR_DT
          else:
            vnew = 0.0
            clear = not in_field((x, y, yaw), person["x"], person["y"], L, ROBOT_W / 2 + Z)
            if clear and "clear" not in ev:
              ev["clear"] = t
            if "clear" in ev and t >= ev["clear"] + 0.5 and "reset" not in ev:
              ev["reset"] = t
            mode = "protective stop, latched" if "reset" not in ev else "SF-05 reset, 2 s warning (HR-07)"
            if "reset" in ev and t >= ev["reset"] + 2.0:
              ev["go"] = t
          push("colour", "red" if t < ev["demand"] + t_r else "grey")
          step(vnew, 0.0, TOUR_SPEEDUP["event"], mode)
          v = vnew
          continue
        # planned motion: the zone limit ahead, the end of the segment
        vmax = min(zone_v[tour_zone(x, y)], 0.30 if pose == "carry" else 9.9)
        d = 0.0
        while d <= min(rem, 0.4):
          px_, py_ = x + c * d, y + s_ * d
          vmax = min(vmax, math.sqrt(zone_v[tour_zone(px_, py_)] ** 2 + 2 * A_PLAN * d))
          d += 0.02
        vmax = min(vmax, math.sqrt(2 * A_PLAN * rem))
        vnew = min(vmax, v + A_PLAN * TOUR_DT) if v < vmax else max(vmax, v - A_PLAN * TOUR_DT)
        vnew = min(vnew, rem / TOUR_DT)
        vnew = min(vnew, zone_v[tour_zone(x + c * vnew * TOUR_DT, y + s_ * vnew * TOUR_DT)])   # never enter a slower zone above its limit
        in_event = "spawn" in ev and ("go" not in ev or t < ev["go"] + 1.5)
        zone = tour_zone(x, y)
        factor = TOUR_SPEEDUP["event"] if in_event else (TOUR_SPEEDUP["muted"] if muted else TOUR_SPEEDUP[zone])
        mode = ("driving, the carry pose" if pose == "carry" else "driving") if not muted else "docking: field muted in the last metre (GAP-15)"
        if "go" in ev and t < ev["go"] + 1.5:
          mode = "motion resumes"
        push("colour", "dim" if muted else "teal")
        step(vnew, 0.0, factor, mode)
        v = vnew
      x, y = tx, ty
      robot[-1] = (t, x, y, yaw)
      v = 0.0
  push("colour", "teal")
  T = t
  # the chips: when each situation along the route is reached
  def first(pred):
    return next((tt for (tt, xx, yy, ww) in robot if pred(tt, xx, yy, ww)), None)
  reach = {
    "IS-04": 0.9,
    "IS-02": first(lambda tt, xx, yy, ww: abs(xx - 17.2) < 0.01 and abs(yy - 8.1) < 0.01),
    "IS-01": ev["demand"],
    "IS-10": ev["reset"],
    "IS-13": first(lambda tt, xx, yy, ww: abs(xx - 12.6) < 0.01 and abs(yy - 8.1) < 0.01 and abs(ww - 90) < 0.5),
    "IS-15": first(lambda tt, xx, yy, ww: abs(yy - 11.15) < 0.01 and abs(ww) < 1 and xx >= TOUR_BYSTANDER[0] - 1.2),
    "IS-05": first(lambda tt, xx, yy, ww: yy > 13.0 and xx + ROBOT_L / 2 >= dock_face - 1.0 and abs(ww) < 1 and tt > 30),
  }
  return {"robot": robot, "states": st, "warp": warp, "T": T, "A": a_t, "events": ev, "person": person["samples"] if person else [], "reach": reach,
          "sets": sets, "zone_v": zone_v, "t_r": t_r, "a_brake": a_brake}


def _simplify(pts, tol):
  """Greedy simplification of (a, v1, v2, ...) samples: keep a point when linear interpolation in a from the last kept
  point would miss any skipped sample by more than tol (one tolerance per value)."""
  if len(pts) <= 2:
    return list(pts)
  out = [pts[0]]
  i = 0
  j = 2
  n = len(pts)
  while j < n:
    a0, a1 = pts[i], pts[j]
    ok = True
    for k in range(i + 1, j):
      f = (pts[k][0] - a0[0]) / (a1[0] - a0[0]) if a1[0] > a0[0] else 0.0
      for d in range(1, len(a0)):
        if abs(a0[d] + (a1[d] - a0[d]) * f - pts[k][d]) > tol[d - 1]:
          ok = False
          break
      if not ok:
        break
    if not ok:
      out.append(pts[j - 1])
      i = j - 1
    j += 1
  out.append(pts[-1])
  return out


def fig_tour(src: dict) -> str:
  tr = build_tour(src)
  warp = tr["warp"]
  wt = [w[0] for w in warp]
  DUR = tr["A"]

  def anim(tsc):
    """Animation seconds at scene time tsc (the warp is sampled at TOUR_DT)."""
    if tsc <= 0:
      return 0.0
    if tsc >= tr["T"]:
      return DUR
    i = min(int(tsc / TOUR_DT), len(warp) - 2)
    (t0, a0), (t1, a1) = warp[i], warp[i + 1]
    return a0 + (a1 - a0) * (tsc - t0) / (t1 - t0)

  kt = lambda tsc: anim(tsc) / DUR  # noqa: E731
  W, H = 1440, 1120
  M = 46.0
  uid = "sim-tour"
  px, py = 32, 96
  sw_, sh_ = SITE["size"]
  pl = Plan(px, py, M, uid, sprites=src["sprites"])
  sets = tr["sets"]
  rows = sets["rows"]
  body = [text(32, 36, "The tour: CFG-002 drives a closed route through the warehouse plan; the field set switches at each zone boundary", 19, C["ink"], 700),
          text(32, 60, f"Dock lane Z3 at the crawl limit with {sets['by_speed'][tr['zone_v']['Z3']]}, aisles Z2 at the navigation limit with {sets['by_speed'][tr['zone_v']['Z2']]}, the carry leg with FS-4; the crossing of IS-01 and the resume of IS-10 played on the way.", 12, C["muted"]),
          text(32, 78, f"Scene time {tr['T']:.0f} s shown in {DUR:.0f} s: transit runs faster than real time (the factor is printed), the situation at 1×. A viewer that shows the SVG as a still shows the robot docked.", 12, C["muted"]),
          rect(px, py, sw_ * M, sh_ * M, C["floor"], C["wall"], 0, 4)]
  body += pl.floor(src)
  # the route, dashed under everything that moves
  pts = [TOUR_DOCKED] + [a[1] for a in TOUR_ROUTE if a[0] == "drive"]
  body.append('<polyline points="' + " ".join("%.1f,%.1f" % pl.P(*p) for p in pts) + f'" fill="none" stroke="{C["blue"]}" stroke-width="2" stroke-dasharray="2,5" opacity="0.7"/>')
  bx, by = TOUR_BYSTANDER
  body += pl.worker(bx, by, None, "IS-15 bystander")
  # the robot: translate + rotate from the simplified samples, the field rect, the sprites by pose, the arm
  rs = [(anim(t), x, y, yaw) for (t, x, y, yaw) in tr["robot"]]
  rs = _simplify(rs, (0.25 / M, 0.25 / M, 0.3))
  x0, y0 = TOUR_DOCKED
  X0, Y0 = pl.P(x0, y0)
  def keys(seq):
    ks = [f"{a / DUR:.5f}" for a in seq]
    if ks[-1] != "1.00000":
      ks.append("1")
      return ks, True
    ks[-1] = "1"
    return ks, False
  ks, extra = keys([p[0] for p in rs])
  tv = ["%.2f,%.2f" % tuple(q - r for q, r in zip(pl.P(p[1], p[2]), (X0, Y0))) for p in rs] + (["%.2f,%.2f" % tuple(q - r for q, r in zip(pl.P(rs[-1][1], rs[-1][2]), (X0, Y0)))] if extra else [])
  rv = [f"{-p[3]:.2f}" for p in rs] + ([f"{-rs[-1][3]:.2f}"] if extra else [])
  body.append(f'<g><animateTransform attributeName="transform" type="translate" values="{";".join(tv)}" keyTimes="{";".join(ks)}" dur="{DUR:.2f}s" repeatCount="indefinite" calcMode="linear"/>'
              f'<g transform="translate({X0:.1f},{Y0:.1f})"><g><animateTransform attributeName="transform" type="rotate" values="{";".join(rv)}" keyTimes="{";".join(ks)}" dur="{DUR:.2f}s" repeatCount="indefinite" calcMode="linear"/>')
  # the field: width by set, colour by state, hidden while reversing
  hw = (ROBOT_W / 2 + src["Z"]) * M
  set_states = tr["states"]["set"]
  wvals = [(t, f"{(rows[fid]['L'] if fid else 0.0) * M:.1f}") for t, (fid, muted) in set_states]
  colmap = {"teal": C["teal"], "red": C["red"], "grey": C["line"], "dim": C["dim"]}
  cvals = [(t, colmap[c]) for t, c in tr["states"]["colour"]]
  fvals = [(t, C["teal"] if c == "teal" else (C["red"] if c == "red" else ("#C9D2D6" if c in ("grey", "dim") else C["teal"]))) for t, c in tr["states"]["colour"]]
  body.append(f'<rect x="{ROBOT_L / 2 * M:.1f}" y="{-hw:.1f}" width="{wvals[0][1]}" height="{2 * hw:.1f}" fill="{C["teal"]}" fill-opacity="0.22" stroke="{C["teal"]}" stroke-width="1.6" stroke-dasharray="5,3">'
              + _disc("width", wvals, kt, DUR) + _disc("stroke", cvals, kt, DUR) + _disc("fill", fvals, kt, DUR) + '</rect>')
  for kind in ("cfg002", "cfg002-carry"):
    pose = "stowed" if kind == "cfg002" else "carry"
    vis = [(t, "1" if p == pose else "0") for t, p in tr["states"]["pose"]]
    body.append(f'<g opacity="{vis[0][1]}">{_disc("opacity", vis, kt, DUR)}' + "".join(pl.sprite(0, 0, 1, 1.0, kind, at_origin=True)) + '</g>')
  # the arm while working: a rotating line from the mount, hidden otherwise
  arm = tr["states"]["arm"]
  arm_on = [(t, "0" if a is None else "1") for t, a in arm]
  arm_on = [p for i, p in enumerate(arm_on) if i == 0 or p[1] != arm_on[i - 1][1]]
  arm_pts = _simplify([(anim(t), a) for t, a in arm if a is not None], (0.5,))
  if arm_pts:
    aks = [f"{p[0] / DUR:.5f}" for p in arm_pts]
    avs = [f"{-p[1]:.2f}" for p in arm_pts]
    aks = ["0"] + aks + ["1"]; avs = [avs[0]] + avs + [avs[-1]]
    body.append(f'<g transform="translate({0.24 * M:.1f},0)" opacity="0">{_disc("opacity", arm_on, kt, DUR)}<g><animateTransform attributeName="transform" type="rotate" values="{";".join(avs)}" keyTimes="{";".join(aks)}" dur="{DUR:.2f}s" repeatCount="indefinite" calcMode="linear"/>'
                f'<line x1="0" y1="0" x2="{REACH * M:.1f}" y2="0" stroke="{C["ink"]}" stroke-width="4" stroke-linecap="round"/><circle cx="{REACH * M:.1f}" cy="0" r="3.5" fill="{C["teal"]}"/></g></g>')
  # the warning beacon of IS-10
  ev = tr["events"]
  body.append(f'<circle cx="0" cy="0" r="6" fill="{C["amber"]}" opacity="0">' + _blink(ev["reset"], ev["go"], kt, DUR) + '</circle>')
  body.append("</g></g></g>")
  # the crosser of IS-01, shown from 2 s before the step to 3 s after the resume
  ps = _simplify([(anim(t), x, y) for t, x, y in tr["person"]], (0.25 / M, 0.25 / M))
  if ps:
    PX0, PY0 = pl.P(ps[0][1], ps[0][2])
    pks = ["0"] + [f"{p[0] / DUR:.5f}" for p in ps] + ["1"]
    pvs = ["0,0"] + ["%.2f,%.2f" % (pl.P(p[1], p[2])[0] - PX0, pl.P(p[1], p[2])[1] - PY0) for p in ps]
    pvs.append(pvs[-1])
    show = [(0.0, "0"), (max(ev["spawn"] - 2.0, 0.0), "1"), (ev["go"] + 3.0, "0")]
    body.append(f'<g opacity="0">{_disc("opacity", show, kt, DUR)}<g><animateTransform attributeName="transform" type="translate" values="{";".join(pvs)}" keyTimes="{";".join(pks)}" dur="{DUR:.2f}s" repeatCount="indefinite" calcMode="linear"/>'
                + "".join(pl.worker(ps[0][1], ps[0][2], None, "IS-01")) + '</g></g>')
  # ---- the readout panel
  qx = px + sw_ * M + 16
  qw = W - qx - 16
  body.append(rect(qx, py, qw, sh_ * M, C["panel"], C["stroke"], 6))
  body.append(text(qx + 12, py + 22, "NOW", 11, C["ink"], 800, extra='letter-spacing="1"'))
  rows_y = py + 44
  readouts = [
    ("zone", [(t, f"{z} · {src['zones'][z]['name'].split(' (')[0].lower()}") for t, z in tr["states"]["zone"]], C["ink"]),
    ("speed", [(t, f"{v:.2f} m/s") for t, v in tr["states"]["speed"]], C["ink"]),
    ("field set", [(t, ("rear: no field, the bumper only" if fid is None else (f"{fid} {rows[fid]['L']:.2f} m" + (", muted (GAP-15)" if m else f", {rows[fid]['case']} {rows[fid]['a']:g} m/s²")))) for t, (fid, m) in set_states], C["teal"]),
    ("pose", [(t, "CFG-002, arms stowed" if p == "stowed" else "CFG-002, carry pose, tote") for t, p in tr["states"]["pose"]], C["ink"]),
    ("state", tr["states"]["mode"], C["amber"]),
    ("shown at", [(t, f"{f:g}× real time" if f != 1 else "1× real time") for t, f in tr["states"]["factor"]], C["muted"]),
  ]
  for i, (label, states, col) in enumerate(readouts):
    yy = rows_y + i * 44
    body.append(text(qx + 12, yy, label.upper(), 9, C["dim"], 700, extra='letter-spacing="0.8"'))
    body += _readout(qx + 12, yy + 18, states, kt, DUR, col, qw - 24)
  cy0 = rows_y + len(readouts) * 44 + 8
  body.append(text(qx + 12, cy0, "SITUATIONS ON THE ROUTE", 9, C["dim"], 700, extra='letter-spacing="0.8"'))
  for i, (sid, what) in enumerate(TOUR_CHIPS):
    r = rating_for(src, sid)
    t_on = tr["reach"][sid]
    yy = cy0 + 14 + i * 40
    lit = f'<animate attributeName="opacity" values="0.35;0.35;1;1;0.6;0.6" keyTimes="0;{kt(t_on):.5f};{kt(t_on) + 0.0002:.5f};{min(kt(t_on) + 6.0 / DUR, 0.9998):.5f};{min(kt(t_on) + 6.0 / DUR, 0.9998) + 0.0001:.5f};1" dur="{DUR:.2f}s" repeatCount="indefinite"/>'
    body.append(f'<g opacity="0.35">{lit}' + rect(qx + 12, yy, qw - 24, 32, C["bg"], C["teal"], 6, 1.2)
                + text(qx + 20, yy + 14, f"{r['hazard']} {sid}  PLr {r['plr']}", 10, C["teal"], 700, family=MONO) + text(qx + 20, yy + 27, _fit(what, qw - 40, 9.5), 9.5, C["muted"]) + '</g>')
  # ---- the timeline: zones, the field length, the factor, the chips, a cursor
  ty = py + sh_ * M + 34
  x0t, x1t = 110, W - 32
  X = lambda tsc: x0t + (x1t - x0t) * kt(tsc)  # noqa: E731
  body.append(text(32, ty - 10, "The tour on one axis (animation time; the ticks are scene seconds)", 11.5, C["ink"], 700))
  zcol = {"Z2": C["teal_bg"], "Z3": "#DCE8F5", "Z4": "#FFF1D6"}
  zs = tr["states"]["zone"] + [(tr["T"], None)]
  body.append(text(32, ty + 13, "zone", 9.5, C["muted"], 600))
  for (t0, z), (t1, _) in zip(zs, zs[1:]):
    body.append(rect(X(t0), ty, max(X(t1) - X(t0), 0.5), 18, zcol.get(z, C["grey_bg"]), C["stroke"], 0, 0.5))
    if X(t1) - X(t0) > 24:
      body.append(text((X(t0) + X(t1)) / 2, ty + 13, z, 9.5, C["ink"], 700, "middle"))
  # the field length, a step plot 0..1 m
  gy0, gy1 = ty + 30, ty + 110
  body += [text(32, gy0 + 10, "field set", 9.5, C["muted"], 600), text(32, gy0 + 22, "length, m", 9.5, C["muted"], 600),
           line(x0t, gy1, x1t, gy1, C["line"], 1)]
  for L_ in (0.5, 1.0):
    yy = gy1 - L_ / 1.0 * (gy1 - gy0)
    body += [line(x0t, yy, x1t, yy, C["stroke"], 0.8, "3,3"), text(x0t - 6, yy + 3, f"{L_:g}", 9, C["muted"], 600, "end", MONO)]
  ss = set_states + [(tr["T"], set_states[-1][1])]
  path = []
  for (t0, (fid, m)), (t1, _) in zip(ss, ss[1:]):
    L_ = rows[fid]["L"] if fid else 0.0
    yy = gy1 - L_ / 1.0 * (gy1 - gy0)
    path.append(f"{X(t0):.1f},{yy:.1f} {X(t1):.1f},{yy:.1f}")
  body.append(f'<polyline points="{" ".join(path)}" fill="none" stroke="{C["teal"]}" stroke-width="2"/>')
  labelled = set()
  for (t0, (fid, m)), (t1, _) in zip(ss, ss[1:]):
    if fid and (fid, m) not in labelled and X(t1) - X(t0) > 40:
      L_ = rows[fid]["L"]
      body.append(text((X(t0) + X(t1)) / 2, gy1 - L_ * (gy1 - gy0) - 5, f"{fid}{' muted' if m else ''}", 9, C["teal"], 700, "middle"))
      labelled.add((fid, m))
  # the speed-up factor
  fy = gy1 + 12
  body.append(text(32, fy + 12, "shown at", 9.5, C["muted"], 600))
  fs = tr["states"]["factor"] + [(tr["T"], None)]
  for (t0, f), (t1, _) in zip(fs, fs[1:]):
    body.append(rect(X(t0), fy, max(X(t1) - X(t0), 0.5), 16, C["red_bg"] if f == 1 else C["grey_bg"], C["stroke"], 0, 0.5))
    if X(t1) - X(t0) > 22:
      body.append(text((X(t0) + X(t1)) / 2, fy + 12, f"{f:g}×", 9, C["red"] if f == 1 else C["muted"], 700, "middle"))
  # chips on the axis and scene-time ticks
  cyy = fy + 32
  for i, (sid, _) in enumerate(TOUR_CHIPS):
    t_on = tr["reach"][sid]
    body += [line(X(t_on), gy0 - 4, X(t_on), cyy + 2, C["amber"], 1, "2,2"), text(X(t_on), cyy + 12 + 11 * (i % 2), sid, 9, C["amber"], 700, "middle", MONO)]
  for tick in range(0, int(tr["T"]) + 1, 30):
    body += [line(X(tick), gy1, X(tick), gy1 + 4, C["ink"], 1), text(X(tick), cyy + 40, f"{tick} s", 9, C["muted"], 600, "middle", MONO)]
  cursor = f'<animateTransform attributeName="transform" type="translate" values="0,0;{x1t - x0t:.1f},0" keyTimes="0;1" dur="{DUR:.2f}s" repeatCount="indefinite" calcMode="linear"/>'
  body.append(f'<line x1="{x0t}" y1="{ty - 4}" x2="{x0t}" y2="{fy + 18}" stroke="{C["red"]}" stroke-width="2.5">{cursor}</line>')
  body.append(text(W - 32, H - 52, "Generated by assurance/sim/figures/fig_sim_is.py", 9.5, C["dim"], anchor="end"))
  body += band(W, H, f"Kinematic motion from WP-S-04 v0.2 planning values (CFG-002 braked at {tr['a_brake']:g} m/s², unmeasured; t_r {tr['t_r']:g} s; K = {src['K']:g} m/s; planned acceleration {A_PLAN:g} m/s²). A tour shows where the field sets apply; it does not show that a measure works.")
  return svg(W, H, uid, "The tour: CFG-002 on a closed route through the warehouse plan, looping",
             f"Looping view of the whole warehouse plan. The 2.0 mobile manipulator reverses out of its dock, crawls out of the dock lane with field set {sets['by_speed'][tr['zone_v']['Z3']]}, "
             f"takes the cross-aisle and aisle 2 at the navigation limit with {sets['by_speed'][tr['zone_v']['Z2']]}, stops for a person who crosses ahead, waits, warns for 2 s and resumes, "
             "picks a tote at the station with the arm, carries it round aisle 1 with field set FS-4 past a bystander, places it on a drop shelf and docks again with the field muted in the last metre. "
             "A panel beside the plan names the zone, speed, field set, pose, state and the speed-up factor at each moment and lights the situation chips as they are reached; "
             "a timeline below shows the zones, the field length as a step plot, the speed-up factor and a cursor.", body, sprites=list(pl.used.items()))


def _disc(attr, states, kt, dur):
  """A discrete animation of an attribute from (scene time, value) changes; the first value holds from 0."""
  vals, ks = [], []
  for i, (t, v) in enumerate(states):
    k = 0.0 if i == 0 else kt(t)
    if ks and k <= float(ks[-1]):
      vals[-1] = str(v)
      continue
    vals.append(str(v)); ks.append(f"{k:.5f}")
  ks[0] = "0"
  vals.append(vals[-1]); ks.append("1")
  return f'<animate attributeName="{attr}" values="{";".join(vals)}" keyTimes="{";".join(ks)}" dur="{dur:.2f}s" calcMode="discrete" repeatCount="indefinite"/>'


def _readout(x, y, states, kt, dur, col, width):
  """One <text> per distinct value, each shown while it is current."""
  out = []
  values = []
  for _, v in states:
    if v not in values:
      values.append(v)
  for v in values:
    vis = []
    for i, (t, w) in enumerate(states):
      on = "1" if w == v else "0"
      if not vis or vis[-1][1] != on:
        vis.append((t, on))
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="12" font-weight="700" fill="{col}" opacity="{vis[0][1]}">{escape(_fit(str(v), width, 12))}{_disc("opacity", vis, kt, dur)}</text>')
  return out


def _blink(t_on, t_off, kt, dur):
  ts = [t_on + 0.25 * i for i in range(int((t_off - t_on) / 0.25) + 1)]
  vals = ["0"] + ["1" if i % 2 == 0 else "0" for i in range(len(ts))] + ["0"]
  ks = ["0"] + [f"{kt(t):.5f}" for t in ts] + ["1"]
  return f'<animate attributeName="opacity" values="{";".join(vals)}" keyTimes="{";".join(ks)}" dur="{dur:.2f}s" calcMode="discrete" repeatCount="indefinite"/>'



OUTPUTS = {"fig-sim-plan.svg": fig_plan, "fig-sim-tour-anim.svg": fig_tour}
for _sid in SCENES:
  OUTPUTS[f"fig-sim-{_sid.lower()}-{'still' if SCENES[_sid].get('still') else 'anim'}.svg"] = (lambda s, sid=_sid: fig_loop(s, sid))


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
