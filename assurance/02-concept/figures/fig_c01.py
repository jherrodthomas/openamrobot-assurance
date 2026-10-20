#!/usr/bin/env python3
"""Draw the WP-C-01 item-definition figures.

  fig-c01-3-1-context-boundary.svg   Figure 3-1  context and item boundary: elements E-01…E-10 inside the dashed
                                                  boundary, the external actors of §3.2 outside, interfaces IF-01…IF-08
  fig-c01-3-2-bdd.svg                Figure 3-2  SysML block definition diagram: the Gate A unit and its parts
  fig-c01-3-3-ibd.svg                Figure 3-3  SysML internal block diagram: parts, ports and item flows, with the
                                                  unwired and undocumented connections drawn as such
  fig-c01-5-1-modes.svg              Figure 5-1  operating modes M0…M6 as a state machine

The source of record is ../WP-C-01-item-definition.md. The element IDs and names are read from the §3.1 table, the
interface IDs from the §3.3 table and the modes from the §5 table; the figure structure (which element connects to
which, over what) is listed here and every structural fact names the §3.3 row it comes from. `--check` fails when a
table row the figures rely on is gone, or when a committed SVG differs from what the generator draws.

    python3 fig_c01.py            # regenerate the SVGs
    python3 fig_c01.py --check    # fail if the source tables changed or an SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "WP-C-01-item-definition.md"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "panel2": "#EDF2F4", "stroke": "#D3DDE2", "line": "#7E949B",
  "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#D4821A", "amber_bg": "#FFF6E8", "cyan": "#0E8C83", "cyan_bg": "#E9F7F5",
  "red": "#D64535", "red_bg": "#FDEDEB", "green": "#2C9A58", "grey_bg": "#F1F5F9", "white": "#FFFFFF",
}

# ---------------------------------------------------------------- source tables


def _table(text: str, heading: str) -> list[list[str]]:
  """Rows of the first Markdown table after `heading` (cells stripped, header and rule skipped)."""
  i = text.index(heading)
  rows = []
  for line in text[i:].splitlines()[1:]:
    if line.startswith("|"):
      rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    elif rows:
      break
  return rows[2:]


def load_source() -> dict:
  text = SOURCE.read_text(encoding="utf-8")
  elements = {r[0]: r[1] for r in _table(text, "### 3.1 Inside the item")}
  interfaces = {r[0]: (r[1], r[2]) for r in _table(text, "### 3.3 Interfaces")}
  modes = [(r[0], r[1], r[2]) for r in _table(text, "## 5. Operating modes and states")]
  return {"elements": elements, "interfaces": interfaces, "modes": modes}


# Structural facts: which element talks to which, over which interface of §3.3. Checked against the source IDs.
FLOWS = [
  # (from, to, interface id, label on the connector, kind)  kind: data | power | unwired | undocumented
  ("EXT-OP", "E-04", "IF-05", "goals, dock, lifecycle", "data"),
  ("EXT-OP", "E-04", "IF-01", "/cmd_vel (teleop, UI)", "data"),
  ("E-04", "E-03", "IF-01", "/cmd_vel over USB serial", "data"),
  ("EXT-NET", "E-03", "IF-02", "/debug/* (any participant)", "data"),
  ("E-03", "E-04", "IF-03", "/odom, /imu, /debug", "data"),
  ("E-05", "E-04", "IF-04", "/scan (USB)", "data"),
  ("E-06", "E-04", "IF-04", "image (CSI)", "data"),
  ("E-07", "E-03", "IF-03", "I2C", "data"),
  ("E-08", "E-03", "IF-03", "A/B quadrature", "data"),
  ("E-03", "E-02", "IF-06", "PWM, FWD, REV", "data"),
  ("E-02", "E-01", "IF-06", "U/V/W, Hall", "data"),
  ("E-09", "E-02", "IF-07", "24 V (no fuse, no disconnect)", "power"),
  ("EXT-MAINS", "E-09", "IF-07", "mains converter in parallel", "power"),
  ("E-09", "E-04", "IF-08", "24→5 V buck", "power"),
  ("E-04", "E-03", "IF-08", "USB 5 V", "power"),
  ("E-02", "E-03", "IF-06", "ERR/DO1, SPD/DO2 (unwired)", "unwired"),
  ("E-03", "E-02", "IF-06", "BRK/DI5 (unwired)", "unwired"),
  ("E-10", "E-09", "IF-07", "switches nothing documented", "undocumented"),
]

MODE_TRANSITIONS = [
  ("M0", "M1", "flash bench image, 24 V on"), ("M1", "M0", "24 V off"),
  ("M0", "M2", "agent up, teleop"), ("M2", "M3", "Nav2 goal"), ("M3", "M2", "teleop publishes (last wins)"),
  ("M3", "M4", "dock trigger"), ("M4", "M3", "docked / failed"), ("M2", "M5", "SLAM running"), ("M5", "M2", "map saved"),
  ("M2", "M6", "no /cmd_vel 200 ms"), ("M3", "M6", "no /cmd_vel 200 ms, agent lost"), ("M4", "M6", "agent lost"),
  ("M6", "M3", "commands resume (no reset)"),
]

# ---------------------------------------------------------------- svg helpers


def _w(s: str, size: float) -> float:
  return len(s) * size * 0.56


def text(x, y, s, size=12, fill=C["ink"], weight=400, anchor="start", family=FONT, extra=""):
  return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
          f'fill="{fill}" text-anchor="{anchor}"{extra}>{escape(s)}</text>')


def rect(x, y, w, h, fill, stroke=C["stroke"], r=6, sw=1, dash=""):
  d = f' stroke-dasharray="{dash}"' if dash else ""
  return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def line(x1, y1, x2, y2, stroke=C["line"], sw=1.2, dash="", marker=""):
  d = f' stroke-dasharray="{dash}"' if dash else ""
  m = f' marker-end="url(#{marker})"' if marker else ""
  return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{d}{m}/>'


def path(d, stroke=C["line"], sw=1.2, dash="", marker="", fill="none"):
  dd = f' stroke-dasharray="{dash}"' if dash else ""
  m = f' marker-end="url(#{marker})"' if marker else ""
  return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dd}{m}/>'


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
  <marker id="{uid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{C['line']}"/></marker>
  <marker id="{uid}-arrow-amber" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{C['amber']}"/></marker>
  <marker id="{uid}-arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{C['red']}"/></marker>
  <marker id="{uid}-diamond" viewBox="0 0 12 8" refX="0" refY="4" markerWidth="12" markerHeight="8" orient="auto">
    <path d="M0,4 L6,0 L12,4 L6,8 z" fill="{C['ink']}"/></marker>
</defs>"""
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
          f'aria-labelledby="{uid}-t {uid}-d">\n<title id="{uid}-t">{escape(title)}</title>\n<desc id="{uid}-d">{escape(desc)}</desc>\n'
          f'{defs}\n<rect x="0" y="0" width="{w}" height="{h}" fill="{C["bg"]}"/>\n' + "\n".join(body) + "\n</svg>\n")


def box(x, y, w, h, title, lines, fill=C["panel"], stroke=C["stroke"], title_fill=C["ink"], stereo="", mono_id=""):
  out = [rect(x, y, w, h, fill, stroke)]
  ty = y + 16
  if stereo:
    out.append(text(x + w / 2, ty, stereo, 10, C["dim"], anchor="middle"))
    ty += 13
  if mono_id:
    out.append(text(x + 8, ty, mono_id, 10, C["muted"], 600, family=MONO))
    out.append(text(x + 8 + _w(mono_id, 10) + 6, ty, title, 12, title_fill, 600))
  else:
    out.append(text(x + w / 2, ty, title, 12, title_fill, 600, anchor="middle"))
  ty += 15
  for ln in lines:
    out.append(text(x + 8, ty, ln, 10.5, C["muted"]))
    ty += 13
  return out


def legend(x, y, items):
  out = []
  for label, color, dash in items:
    out.append(line(x, y, x + 28, y, color, 2, dash))
    out.append(text(x + 34, y + 4, label, 10.5, C["muted"]))
    x += 34 + _w(label, 10.5) + 22
  return out


def pill(x, y, label, color, anchor="middle", size=9.5):
  w = _w(label, size) + 10
  x0 = x - w / 2 if anchor == "middle" else x if anchor == "start" else x - w
  return (f'<rect x="{x0:.1f}" y="{y - size:.1f}" width="{w:.1f}" height="{size + 6}" rx="4" fill="{C["white"]}" fill-opacity="0.92"/>'
          + text(x, y + 1, label, size, color, 600, anchor))


def route(points, kind, uid, label="", at=None, anchor="middle"):
  """Orthogonal polyline through `points`; the arrowhead at the last point; the label as a pill at `at`.
  Returns (line elements, label elements) so callers can draw lines behind the boxes and labels on top."""
  color = {"data": C["line"], "power": C["amber"], "unwired": C["dim"], "undocumented": C["red"], "contact": C["dim"], "red": C["red"], "ink": C["ink"]}[kind]
  marker = {"data": f"{uid}-arrow", "power": f"{uid}-arrow-amber", "unwired": "", "undocumented": f"{uid}-arrow-red", "contact": "", "red": f"{uid}-arrow-red", "ink": f"{uid}-arrow"}[kind]
  dash = {"data": "", "power": "", "unwired": "3,4", "undocumented": "6,4", "contact": "2,3", "red": "", "ink": ""}[kind]
  d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
  lines = [path(d, color, 1.4, dash, marker)]
  labels = []
  if label:
    if at is None:
      (x1, y1), (x2, y2) = points[0], points[-1]
      at = ((x1 + x2) / 2, (y1 + y2) / 2 - 6)
    labels.append(pill(at[0], at[1], label, color, anchor))
  return lines, labels


def port_sq(x, y):
  return f'<rect x="{x - 4:.1f}" y="{y - 4:.1f}" width="8" height="8" fill="{C["white"]}" stroke="{C["ink"]}" stroke-width="1"/>'


# ---------------------------------------------------------------- Figure 3-1 context and boundary

EXTERNALS = {
  "EXT-OP": ("Operator", "browser UI, keyboard teleop, phone"),
  "EXT-BY": ("Bystanders", "share the floor; cannot stop it"),
  "EXT-SITE": ("Site", "floor, slopes, doors, lighting, other vehicles"),
  "EXT-NET": ("Wi-Fi network", "DDS domain 0, multicast; any participant"),
  "EXT-MAINS": ("Mains and charger", "230 V converter, unknown model"),
  "EXT-PAY": ("Payload", "on the top plate; no limit set"),
  "EXT-20": ("2.0 upper body", "OpenArm 2.0 arms and the lift"),
  "EXT-FLEET": ("Fleet server", "cloud fleet management"),
}


def fig_context(src: dict) -> str:
  W, H = 1180, 660
  el = src["elements"]
  head = [text(32, 34, "Figure 3-1  Context and item boundary of the Gate A unit", 15, C["ink"], 700),
          text(32, 52, "The ten elements inside the dashed boundary; the external actors of §3.2 outside, each naming the §3.3 interfaces that cross the boundary to it.", 11, C["muted"])]
  bx, by, bw, bh = 320, 84, 540, 470
  nodes = [rect(bx, by, bw, bh, C["panel2"], C["ink"], 10, 1.4, "8,5"),
           text(bx + 14, by + 22, "ITEM  OpenAMRobot Gate A unit (CFG-001)", 11, C["ink"], 700, extra=' letter-spacing="1"')]
  ew, eh = 246, 70
  order = ["E-04", "E-03", "E-02", "E-01", "E-09", "E-05", "E-06", "E-07", "E-08", "E-10"]
  for i, eid in enumerate(order):
    col, row = divmod(i, 5)
    x = bx + 18 + col * (ew + 12)
    y = by + 40 + row * (eh + 14)
    short, _, detail = el[eid].partition(":")
    nodes += box(x, y, ew, eh, short.strip(), wrap(detail.strip(), ew - 16, 10.5)[:3], C["white"], C["stroke"], mono_id=eid)
  ex_w, ex_h = 230, 76
  actors = {  # id: (x, y, third line)
    "EXT-OP": (40, 96, "crosses: IF-01, IF-05"), "EXT-NET": (40, 206, "crosses: IF-01, IF-02, IF-05"),
    "EXT-BY": (40, 316, "no interface, no detection"), "EXT-MAINS": (40, 426, "crosses: IF-07 (∥ battery)"),
    "EXT-SITE": (W - 40 - ex_w, 96, "contact: floor, obstacles"), "EXT-PAY": (W - 40 - ex_w, 206, "contact: mass on the plate"),
    "EXT-20": (W - 40 - ex_w, 316, "not this item (DQ-004)"), "EXT-FLEET": (W - 40 - ex_w, 426, "not this item"),
  }
  for k, (x, y, third) in actors.items():
    tt, d = EXTERNALS[k]
    nodes += box(x, y, ex_w, ex_h, tt, wrap(d, ex_w - 16, 10.5)[:2] + [third], C["grey_bg"], C["stroke"])
  lx, rx = 40 + ex_w, W - 40 - ex_w
  edges, labels = [], []
  for k, kind in (("EXT-OP", "data"), ("EXT-NET", "data"), ("EXT-BY", "contact"), ("EXT-MAINS", "power")):
    y = actors[k][1] + ex_h / 2
    ln, lb = route([(lx, y), (bx, y)], kind, "ctx")
    edges += ln
  for k in ("EXT-SITE", "EXT-PAY"):
    y = actors[k][1] + ex_h / 2
    ln, lb = route([(rx, y), (bx + bw, y)], "contact", "ctx")
    edges += ln
  note = [pill(bx + bw / 2, by + bh + 22, "E-10: the E-stop button's wiring is undocumented (GAP-01); nothing crosses the boundary from it", C["red"])]
  foot = legend(32, H - 24, [("data (ROS 2 / serial)", C["line"], ""), ("power", C["amber"], ""), ("physical contact, no interface", C["dim"], "2,3")])
  foot.append(text(W - 32, H - 20, "Generated by figures/fig_c01.py from WP-C-01 §3.1, §3.2, §3.3", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "ctx", "Figure 3-1: context and item boundary of the Gate A unit",
             "The ten elements of the item in a grid inside a dashed boundary; the operator, the Wi-Fi network, bystanders and the mains on the left, each naming the interface IDs that cross the boundary to it; the site, the payload, the 2.0 upper body and the fleet server on the right; a red note that the E-stop button's wiring is undocumented.",
             head + edges + nodes + labels + note + foot)


# ---------------------------------------------------------------- Figure 3-2 block definition diagram

BDD = [
  ("E-01", ["2 drive wheels Ø0.200 m", "swivel castors", "ZD Z4BLD60 BLDC ×2, 1:25 gearbox", "steel panel chassis, cover"]),
  ("E-02", ["ZBLD.C20-120L2R ×2", "open-loop power stage (SW1 off)", "BRK, ERR, SPD pins unused"]),
  ("E-03", ["Teensy 4.0 (i.MX RT1062)", "linorobot2 overlay firmware", "micro-ROS serial 115200"]),
  ("E-04", ["Raspberry Pi 5, 8 GB, no cooler", "ROS 2 Jazzy: bringup, drivers,", "perception, nav2, docking"]),
  ("E-05", ["RPLIDAR A1 (model unconfirmed)", "USB; S3 planned for 2.0"]),
  ("E-06", ["Pi Camera Module 3 NoIR", "CSI; AprilTag docking"]),
  ("E-07", ["MPU6500, no magnetometer", "I2C to the Teensy"]),
  ("E-08", ["AS5040 ×2, 1024 counts/rev", "3.3 V supply"]),
  ("E-09", ["2 × 12 V 7 Ah AGM in series", "24→5 V buck (generic)", "no fuse, no disconnect, no BMS"]),
  ("E-10", ["panel mushroom button", "wiring undocumented", "AprilTag dock bundle (3 tags)"]),
]


def fig_bdd(src: dict) -> str:
  W, H = 1180, 560
  el = src["elements"]
  body = [text(32, 34, "Figure 3-2  Block definition diagram (SysML bdd): the Gate A unit and its parts", 15, C["ink"], 700),
          text(32, 52, "Composition: the item «block» owns every part; multiplicities from §1.1. Part lists are the §1.1 reference configuration.", 11, C["muted"])]
  # root block
  rx, ry, rw, rh = 440, 80, 300, 78
  body += box(rx, ry, rw, rh, "OpenAMRobot Gate A unit", ["values: mass (unknown), max 0.71 m/s cmd, 24 V", "constraints: WP-C-01 §4 limits"], C["cyan_bg"], C["cyan"], C["ink"], "«block»")
  # children in two rows
  cw, ch = 210, 92
  gap = 20
  n = len(BDD)
  per_row = 5
  for i, (eid, parts) in enumerate(BDD):
    r, c = divmod(i, per_row)
    x = 32 + c * (cw + gap) + (0 if r == 0 else 0)
    y = 230 + r * (ch + 70)
    name = el[eid].partition(":")[0].strip()
    body += box(x, y, cw, ch, name, parts, C["white"], C["stroke"], C["ink"], "«block»", eid)
    # composition line from root bottom to child top (diamond at the root end)
    cx = x + cw / 2
    top = y
    midy = 200 if r == 0 else y - 30
    d = f"M{rx + rw / 2:.1f},{ry + rh:.1f} L{rx + rw / 2:.1f},{180:.1f} L{cx:.1f},{180:.1f} L{cx:.1f},{top:.1f}" if r == 0 else \
        f"M{rx + rw / 2:.1f},{ry + rh:.1f} L{rx + rw / 2:.1f},{180:.1f} L{W - 20:.1f},{180:.1f} L{W - 20:.1f},{midy:.1f} L{cx:.1f},{midy:.1f} L{cx:.1f},{top:.1f}"
    body.append(path(d, C["ink"], 1.1))
    mult = {"E-02": "2", "E-08": "2", "E-01": "1", "E-09": "1"}.get(eid, "1")
    body.append(text(cx + 6, top - 4, mult, 10, C["muted"]))
  # diamond at the root
  body.append(f'<path d="M{rx + rw / 2 - 6:.1f},{ry + rh + 8:.1f} L{rx + rw / 2:.1f},{ry + rh:.1f} L{rx + rw / 2 + 6:.1f},{ry + rh + 8:.1f} L{rx + rw / 2:.1f},{ry + rh + 16:.1f} z" fill="{C["white"]}" stroke="{C["ink"]}" stroke-width="1.1"/>')
  body.append(text(32, H - 20, "Composition (filled-diamond end at the owner) · «block» per SysML 1.6 · values and constraints are WP-C-01 §4 · Generated by figures/fig_c01.py", 9.5, C["dim"]))
  return svg(W, H, "bdd", "Figure 3-2: block definition diagram of the Gate A unit",
             "A SysML block definition diagram: the Gate A unit block at the top owns ten part blocks E-01 to E-10 by composition, each listing the parts of the reference configuration, with multiplicities two for the drivers and encoders.", body)


# ---------------------------------------------------------------- Figure 3-3 internal block diagram


def fig_ibd(src: dict) -> str:
  W, H = 1240, 640
  el = src["elements"]
  head = [text(32, 34, "Figure 3-3  Internal block diagram (SysML ibd): parts, ports and item flows", 15, C["ink"], 700),
          text(32, 52, "Connectors carry the §3.3 interface IDs (full content in the table). Grey dashed: driver pins that exist and are not wired. Red dashed: the E-stop button, which switches nothing documented.", 11, C["muted"])]
  fx, fy, fw, fh = 32, 72, W - 64, 500
  frame = [rect(fx, fy, fw, fh, C["panel2"], C["ink"], 8, 1.2), text(fx + 10, fy + 18, "ibd [block] Gate A unit", 11, C["ink"], 700, family=MONO)]
  B = {
    "EXT-OP": (40, 100, 190, 84), "E-04": (330, 100, 190, 84), "E-03": (660, 100, 190, 84), "E-02": (990, 100, 190, 84),
    "EXT-NET": (40, 250, 190, 64), "E-05": (300, 250, 130, 64), "E-06": (440, 250, 130, 64), "E-07": (630, 250, 130, 64), "E-08": (770, 250, 130, 64), "E-01": (990, 250, 190, 64),
    "EXT-MAINS": (40, 400, 190, 64), "E-09": (330, 400, 190, 64), "E-10": (630, 400, 190, 64),
  }
  nodes = []
  for k, (x, y, w, h) in B.items():
    if k.startswith("EXT"):
      tt, d = EXTERNALS[k]
      nodes += box(x, y, w, h, tt, wrap(d, w - 16, 10.5)[:3], C["grey_bg"], C["stroke"])
    else:
      nodes += box(x, y, w, h, el[k].partition(":")[0].strip(), [], C["white"], C["stroke"], C["ink"], mono_id=k)

  def P(k, side, f):
    x, y, w, h = B[k]
    return {"l": (x, y + h * f), "r": (x + w, y + h * f), "t": (x + w * f, y), "b": (x + w * f, y + h)}[side]

  edges, labels, ports = [], [], []

  def C2(a, sa, fa, b, sb, fb, kind, label, at=None, anchor="middle", via=None):
    p1, p2 = P(a, sa, fa), P(b, sb, fb)
    ln, lb = route([p1] + (via or []) + [p2], kind, "ibd", label, at, anchor)
    edges.extend(ln)
    labels.extend(lb)
    ports.extend([port_sq(*p1), port_sq(*p2)])

  C2("EXT-OP", "r", 0.25, "E-04", "l", 0.25, "data", "IF-05")
  C2("EXT-OP", "r", 0.55, "E-04", "l", 0.55, "data", "IF-01", (280, 162))
  C2("E-04", "r", 0.2, "E-03", "l", 0.2, "data", "IF-01 serial")
  C2("E-03", "l", 0.45, "E-04", "r", 0.45, "data", "IF-03", (590, 150))
  C2("E-04", "r", 0.7, "E-03", "l", 0.7, "power", "IF-08 USB 5 V", (590, 171))
  C2("E-03", "r", 0.3, "E-02", "l", 0.3, "data", "IF-06 PWM, FWD, REV")
  C2("E-02", "l", 0.7, "E-03", "r", 0.7, "unwired", "ERR, SPD, BRK unwired", (920, 172))
  C2("EXT-NET", "r", 0.5, "E-03", "l", 0.9, "data", "IF-02 /debug/*", (600, 216), "middle", [(270, 282), (270, 222), (640, 222), (640, 176)])
  C2("E-05", "t", 0.5, "E-04", "b", 0.2, "data", "IF-04", (354, 236), "start")
  C2("E-06", "t", 0.5, "E-04", "b", 0.9, "data", "CSI", (509, 236), "start")
  C2("E-07", "t", 0.5, "E-03", "b", 0.2, "data", "I2C", (700, 236), "start")
  C2("E-08", "t", 0.5, "E-03", "b", 0.9, "data", "A/B ×2", (840, 236), "start")
  C2("E-02", "b", 0.5, "E-01", "t", 0.5, "data", "U/V/W, Hall ×2", (1092, 224), "start")
  C2("EXT-MAINS", "r", 0.5, "E-09", "l", 0.5, "power", "IF-07 ∥")
  C2("E-09", "l", 0.2, "E-04", "l", 0.85, "power", "IF-08 5 V buck", (268, 380), "middle", [(285, 413), (285, 171)])
  C2("E-09", "r", 0.3, "E-02", "l", 0.9, "power", "IF-07 24 V, no fuse", (900, 355), "middle", [(960, 419), (960, 176)])
  C2("E-10", "l", 0.5, "E-09", "r", 0.7, "undocumented", "undocumented", (575, 426))
  foot = legend(32, H - 36, [("item flow (data)", C["line"], ""), ("power", C["amber"], ""), ("pin exists, not wired", C["dim"], "3,4"), ("undocumented", C["red"], "6,4")])
  foot.append(text(W - 32, H - 20, "Generated by figures/fig_c01.py from WP-C-01 §3.1, §3.3", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "ibd", "Figure 3-3: internal block diagram of the Gate A unit",
             "A SysML internal block diagram: the command chain operator, compute, low-level controller, motor drivers and chassis along the top; LiDAR, camera, IMU and encoders below their consumers; power at the bottom; port squares on every part and item flows labelled with the interface IDs; the driver fault, speed and brake pins drawn grey dashed as unwired and the E-stop button red dashed as undocumented.",
             head + frame + edges + nodes + ports + labels + foot)


# ---------------------------------------------------------------- Figure 5-1 operating modes


def fig_modes(src: dict) -> str:
  W, H = 1180, 580
  modes = {m[0].split()[0]: m for m in src["modes"]}
  head = [text(32, 34, "Figure 5-1  Operating modes M0…M6 as a state machine", 15, C["ink"], 700),
          text(32, 52, "Each state shows who commands motion and which protective layers are active (§5). No transition is arbitrated: the last publisher wins.", 11, C["muted"])]
  sw, sh = 220, 112
  P = {"M0": (50, 120), "M2": (330, 120), "M3": (610, 120), "M4": (890, 120), "M1": (50, 350), "M5": (330, 350), "M6": (610, 350)}
  nodes = []
  for mid, (x, y) in P.items():
    name, who, layers = modes[mid]
    fill = C["red_bg"] if mid in ("M1", "M6") else C["amber_bg"] if mid in ("M2", "M4", "M5") else C["cyan_bg"] if mid == "M3" else C["grey_bg"]
    stroke = C["red"] if mid in ("M1", "M6") else C["amber"] if mid in ("M2", "M4", "M5") else C["cyan"] if mid == "M3" else C["stroke"]
    wrapped = wrap("commands: " + who, sw - 16, 10.5) + wrap("layers: " + layers, sw - 16, 10.5)
    nodes += box(x, y, sw, sh, name, wrapped[:6], fill, stroke, C["ink"])

  def S(m, side, f):
    x, y = P[m]
    return {"l": (x, y + sh * f), "r": (x + sw, y + sh * f), "t": (x + sw * f, y), "b": (x + sw * f, y + sh)}[side]

  edges, labels = [], []

  def T(a, sa, fa, b, sb, fb, label, kind="ink", at=None, anchor="middle", via=None):
    ln, lb = route([S(a, sa, fa)] + (via or []) + [S(b, sb, fb)], kind, "mod", label, at, anchor)
    edges.extend(ln)
    labels.extend(lb)

  top, bot = 120, 120 + sh          # label rows: above the top edge and below the bottom edge of the upper row
  T("M0", "r", 0.35, "M2", "l", 0.35, "agent up, teleop", "ink", (300, top - 12))
  T("M2", "r", 0.35, "M3", "l", 0.35, "Nav2 goal", "ink", (580, top - 12))
  T("M3", "l", 0.65, "M2", "r", 0.65, "teleop publishes (last wins)", "ink", (580, bot + 18))
  T("M3", "r", 0.35, "M4", "l", 0.35, "dock trigger", "ink", (860, top - 12))
  T("M4", "l", 0.65, "M3", "r", 0.65, "docked / failed", "ink", (860, bot + 18))
  T("M0", "b", 0.35, "M1", "t", 0.35, "bench image, 24 V on", "ink", (118, 296), "end")
  T("M1", "t", 0.65, "M0", "b", 0.65, "24 V off", "ink", (200, 296), "start")
  T("M2", "b", 0.35, "M5", "t", 0.35, "SLAM running", "ink", (398, 296), "end")
  T("M5", "t", 0.65, "M2", "b", 0.65, "map saved", "ink", (480, 296), "start")
  T("M3", "b", 0.35, "M6", "t", 0.35, "silence 200 ms / agent lost", "red", (678, 318), "end")
  T("M6", "t", 0.65, "M3", "b", 0.65, "commands resume (no reset)", "red", (760, 318), "start")
  T("M2", "b", 0.85, "M6", "l", 0.3, "no /cmd_vel 200 ms", "red", (530, 262), "start", [(517, 272), (585, 272), (585, 384)])
  T("M4", "b", 0.5, "M6", "r", 0.5, "agent lost", "red", (1008, 300), "start", [(1000, 406)])
  start_mark = [f'<circle cx="30" cy="159" r="6" fill="{C["ink"]}"/>', line(36, 159, 50, 159, C["ink"], 1.3, "", "mod-arrow")]
  foot = [text(32, H - 36, "Red: the stop state M6 is reached by silence or loss, never by a demand, and leaves itself as soon as commands return (no reset; SF-05 absent).", 10.5, C["red"]),
          text(32, H - 20, "States from WP-C-01 §5; transitions from the upstream launch files and the docking sequencer as read in the gap assessment · Generated by figures/fig_c01.py", 9.5, C["dim"])]
  return svg(W, H, "mod", "Figure 5-1: operating modes of the Gate A unit as a state machine",
             "Seven states M0 off and bench, M1 powered debug, M2 teleoperation, M3 autonomous navigation, M4 docking, M5 mapping and M6 fault or stopped, each with who commands motion and which protective layers are active, joined by labelled transitions; M6 is reached by silence or loss and is left as soon as commands return.",
             head + edges + nodes + start_mark + labels + foot)


# ---------------------------------------------------------------- main

OUTPUTS = {
  "fig-c01-3-1-context-boundary.svg": fig_context,
  "fig-c01-3-2-bdd.svg": fig_bdd,
  "fig-c01-3-3-ibd.svg": fig_ibd,
  "fig-c01-5-1-modes.svg": fig_modes,
}


def check_source(src: dict) -> list[str]:
  errs = []
  for eid in [f"E-{i:02d}" for i in range(1, 11)]:
    if eid not in src["elements"]:
      errs.append(f"WP-C-01 §3.1 has no row for {eid}")
  for iid in [f"IF-{i:02d}" for i in range(1, 9)]:
    if iid not in src["interfaces"]:
      errs.append(f"WP-C-01 §3.3 has no row for {iid}")
  for a, b, iid, _, _ in FLOWS:
    for e in (a, b):
      if not e.startswith("EXT") and e not in src["elements"]:
        errs.append(f"flow {a}->{b} names unknown element {e}")
    if iid not in src["interfaces"]:
      errs.append(f"flow {a}->{b} names unknown interface {iid}")
  ids = {m[0].split()[0] for m in src["modes"]}
  for a, b, _ in MODE_TRANSITIONS:
    for m in (a, b):
      if m not in ids:
        errs.append(f"transition {a}->{b} names unknown mode {m}")
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
      print(f"wrote {p.relative_to(HERE.parents[2])}")
  if stale:
    print("FAIL: stale figures: " + ", ".join(stale) + "; run python3 assurance/02-concept/figures/fig_c01.py")
    return 1
  print("OK: WP-C-01 figures current" if check else "OK: WP-C-01 figures generated")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
