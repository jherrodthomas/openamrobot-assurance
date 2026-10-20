#!/usr/bin/env python3
"""Draw the WP-C-06 human-robot-interaction figures.

  fig-c06-2-1-interaction-scenes.svg   Figure 2-1  scene cards IS-01…IS-12 (top-down pictograms, 1 m grid)
  fig-c06-3-1-detection-distance.svg   Figure 3-1  minimum detection distance L against the coasting time to standstill
  fig-c06-5-1-misuse-matrix.svg        Figure 5-1  misuse matrix, likelihood × consequence, MU IDs in the cells

The source of record is ../WP-C-06-human-robot-interaction-and-misuse.md: scenario IDs, zone, closest distance and
measure from the §2 table; K, v, t_r, Z from the §3 parameter table; misuse IDs, likelihood and consequence from
the §5 table. The pictogram of each scene is listed here and checked against the IDs. `--check` fails when a
source row is gone, a parameter is missing, or an SVG is stale.

    python3 fig_c06.py            # regenerate
    python3 fig_c06.py --check    # fail if the source changed or an SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "WP-C-06-human-robot-interaction-and-misuse.md"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "stroke": "#D3DDE2", "line": "#7E949B", "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#B86F0C", "amber_bg": "#FFF6E8", "teal": "#00938B", "teal_bg": "#E9F7F5", "red": "#D64535", "red_bg": "#FDEDEB",
  "green": "#2C9A58", "green_bg": "#E8F6EC", "grey_bg": "#EDF2F4", "white": "#FFFFFF",
}


def _table(text: str, heading: str) -> list[list[str]]:
  i = text.index(heading)
  rows = []
  for line in text[i:].splitlines()[1:]:
    if line.startswith("|"):
      rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    elif rows:
      break
  return rows[2:]


def _num(s: str) -> float | None:
  m = re.search(r"-?[0-9]+(?:\.[0-9]+)?", s.replace("**", ""))
  return float(m.group(0)) if m else None


def load_source() -> dict:
  text = SOURCE.read_text(encoding="utf-8")
  scenes = {r[0]: {"who": r[1], "zone": r[2], "doing": r[4], "closest": r[5], "measure": r[8]} for r in _table(text, "## 2. Interaction scenarios")}
  params = {r[0]: r[2] for r in _table(text, "## 3. Approach speeds and safety distances")}
  misuse = {r[0]: {"text": r[1], "likelihood": r[2], "consequence": r[3]} for r in _table(text, "## 5. Reasonably foreseeable misuse")}
  return {"scenes": scenes, "params": params, "misuse": misuse}


# Pictogram per scene: robot at (x, y) metres on a 5 x 4 m card, heading (dx, dy); persons as (x, y, dx, dy, low);
# props: racks as (x, y, w, h); dock as (x, y); screen flag; field drawn unless field=False.
SCENES = {
  "IS-01": dict(robot=(1.0, 2.0, 1, 0), persons=[(3.4, 0.6, 0, 1, False)], caption="crosses ahead at walking pace"),
  "IS-02": dict(robot=(1.0, 2.0, 1, 0), persons=[(3.0, 1.45, 0, 1, False)], racks=[(2.6, 0.2, 1.2, 0.9)], caption="steps out from behind a rack, 0.5 m ahead"),
  "IS-03": dict(robot=(1.5, 2.2, 1, 0), persons=[(1.6, 1.4, 1, 0, False)], racks=[(0.2, 0.1, 4.6, 0.6)], caption="walks alongside; a turn pins against the rack"),
  "IS-04": dict(robot=(3.0, 2.0, -1, 0), persons=[(4.6, 2.0, -1, 0, False)], dock=(1.0, 2.0), field=False, caption="behind the robot while it reverses from the dock"),
  "IS-05": dict(robot=(3.0, 2.0, -1, 0), persons=[(1.6, 1.1, 0, 1, False)], dock=(1.0, 2.0), caption="steps into the dock lane during the blind approach"),
  "IS-06": dict(robot=(1.2, 2.2, 1, 0), persons=[(3.6, 2.2, 0, 0, False), (4.3, 0.7, 0, 0, False)], screen=True, caption="operator watches the screen; bystander in the path"),
  "IS-07": dict(robot=(2.0, 2.0, 1, 0), persons=[(0.9, 2.0, 0, 0, False)], charger=True, field=False, caption="technician connects the charger; a command arrives"),
  "IS-08": dict(robot=(2.0, 2.0, 0, 0), persons=[(2.4, 2.0, 0, 0, False)], field=False, caption="sits on or pushes the robot"),
  "IS-09": dict(robot=(1.0, 2.0, 1, 0), persons=[(3.2, 2.1, -1, 0, True)], caption="child or crouching person below the scan plane"),
  "IS-10": dict(robot=(1.0, 2.0, 1, 0), persons=[(2.8, 2.0, 0, 0, False)], caption="stands in the path; robot waits, then resumes silently"),
  "IS-11": dict(robot=(1.2, 2.0, 1, 0), persons=[(4.0, 0.8, 0, 0, False)], screen=True, field=False, caption="presses the on-screen E-STOP; nothing stops"),
  "IS-12": dict(robot=(1.0, 2.0, 1, 0), persons=[(3.0, 2.0, -1, 0, False)], caption="tries to stop the robot with a hand"),
}

MISUSE_CELLS = {("L", "S1"), ("M", "S1"), ("H", "S1"), ("L", "S2"), ("M", "S2"), ("H", "S2")}


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
  <marker id="{uid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{C['ink']}"/></marker>
  <pattern id="{uid}-grid" patternUnits="userSpaceOnUse" width="36" height="36">
    <path d="M36,0 L0,0 L0,36" fill="none" stroke="{C['stroke']}" stroke-width="0.7"/></pattern>
  <pattern id="{uid}-hatch" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="8" stroke="{C['amber']}" stroke-width="1"/></pattern>
</defs>"""
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
          f'<title id="{uid}-t">{escape(title)}</title>\n<desc id="{uid}-d">{escape(desc)}</desc>\n{defs}\n'
          f'<rect x="0" y="0" width="{w}" height="{h}" fill="{C["bg"]}"/>\n' + "\n".join(body) + "\n</svg>\n")


# ---------------------------------------------------------------- Figure 2-1 scene cards

M = 36.0  # px per metre on a card


def _person(cx, cy, low=False, color=C["ink"]):
  r = 0.17 * M if not low else 0.12 * M
  out = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{C["white"]}" stroke="{color}" stroke-width="1.6"/>']
  if not low:
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{0.26 * M:.1f}" ry="{0.1 * M:.1f}" fill="none" stroke="{color}" stroke-width="1.2"/>')
  else:
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{0.3 * M:.1f}" ry="{0.16 * M:.1f}" fill="none" stroke="{color}" stroke-width="1.2" stroke-dasharray="2,2"/>')
  return out


def _card(x0, y0, cw, chh, sid, sc, spec, uid):
  out = [rect(x0, y0, cw, chh, C["white"], C["stroke"], 8)]
  px, py, pw, ph = x0 + 10, y0 + 30, 5 * M, 4 * M
  out.append(rect(px, py, pw, ph, f"url(#{uid}-grid)", C["stroke"], 3))
  out.append(text(x0 + 10, y0 + 20, sid, 11, C["ink"], 700, family=MONO))
  closest = sc['closest'].replace('**', '').split('(')[0].split(' if')[0].split(',')[0].strip()
  out.append(text(x0 + 60, y0 + 20, f"{sc['zone']} · closest {closest}", 10, C["muted"]))

  def P(xm, ym):
    return px + xm * M, py + ym * M

  for (rx, ry, rw, rh) in spec.get("racks", []):
    x, y = P(rx, ry)
    out.append(rect(x, y, rw * M, rh * M, C["grey_bg"], C["line"], 2))
  if "dock" in spec:
    x, y = P(*spec["dock"])
    out.append(rect(x - 0.15 * M, y - 0.5 * M, 0.3 * M, 1.0 * M, C["teal_bg"], C["teal"], 2))
    out.append(text(x, y + 0.9 * M, "dock", 9, C["teal"], anchor="middle"))
  rx, ry, dx, dy = spec["robot"]
  cx, cy = P(rx, ry)
  rl, rw = 0.805 * M, 0.58 * M
  if spec.get("field", True) and (dx or dy):
    fx = cx + (rl / 2 if dx > 0 else -rl / 2)
    fl = 1.0 * M * (1 if dx > 0 else -1)
    pts = [(fx, cy - rw / 2 - 0.1 * M), (fx + fl, cy - rw / 2 - 0.25 * M), (fx + fl, cy + rw / 2 + 0.25 * M), (fx, cy + rw / 2 + 0.1 * M)]
    out.append('<path d="M' + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f' z" fill="{C["teal"]}" fill-opacity="0.15" stroke="{C["teal"]}" stroke-width="1" stroke-dasharray="3,2"/>')
  out.append(rect(cx - rl / 2, cy - rw / 2, rl, rw, C["white"], C["ink"], 3, 1.4))
  bx = cx - rl / 2 - 0.06 * M if dx >= 0 else cx + rl / 2
  out.append(rect(bx, cy - rw / 2 + 2, 0.06 * M, rw - 4, C["red"], C["red"], 1))
  if dx or dy:
    ax = cx + dx * (rl / 2 + 0.05 * M)
    out.append(f'<line x1="{ax:.1f}" y1="{cy:.1f}" x2="{ax + dx * 0.35 * M:.1f}" y2="{cy:.1f}" stroke="{C["ink"]}" stroke-width="1.4" marker-end="url(#{uid}-arrow)"/>')
  for (hx, hy, hdx, hdy, low) in spec["persons"]:
    x, y = P(hx, hy)
    out += _person(x, y, low)
    if hdx or hdy:
      out.append(f'<line x1="{x + hdx * 0.3 * M:.1f}" y1="{y + hdy * 0.3 * M:.1f}" x2="{x + hdx * 0.75 * M:.1f}" y2="{y + hdy * 0.75 * M:.1f}" stroke="{C["ink"]}" stroke-width="1.4" marker-end="url(#{uid}-arrow)"/>')
  if spec.get("screen"):
    x, y = P(4.2, 0.4)
    out.append(rect(x, y, 0.6 * M, 0.4 * M, C["amber_bg"], C["amber"], 2))
    out.append(text(x + 0.3 * M, y + 0.27 * M, "UI", 8, C["amber"], 700, "middle"))
  if spec.get("charger"):
    x, y = P(0.3, 2.0)
    out.append(rect(x - 0.15 * M, y - 0.3 * M, 0.3 * M, 0.6 * M, C["amber_bg"], C["amber"], 2))
    out.append(text(x, y + 0.75 * M, "charger", 9, C["amber"], anchor="middle"))
  cy0 = py + ph + 14
  for i, ln in enumerate(wrap(spec["caption"], cw - 20, 10)[:2]):
    out.append(text(x0 + 10, cy0 + i * 12, ln, 10, C["ink"], 600))
  meas = sc["measure"].replace("**", "").split(";")[0]
  for i, ln in enumerate(wrap("needs: " + meas, cw - 20, 9.5)[:2]):
    out.append(text(x0 + 10, cy0 + 26 + i * 12, ln, 9.5, C["muted"]))
  return out


def fig_scenes(src: dict) -> str:
  cw, chh, gap = 236, 258, 14
  cols = 4
  W = 32 * 2 + cols * cw + (cols - 1) * gap
  rows = 3
  H = 94 + rows * chh + (rows - 1) * gap + 50
  body = [text(32, 34, "Figure 2-1  Interaction scenarios IS-01…IS-12 as scene cards (top-down, 1 m grid)", 15, C["ink"], 700),
          text(32, 52, "Robot with its direction of travel, its 1.0 m starting field (teal) and the rear bumper (red); people as head-and-shoulders, dashed when below the scan plane.", 11, C["muted"]),
          text(32, 66, "Caption: what happens; below it, the measure the §2 table names.", 11, C["muted"])]
  for i, (sid, spec) in enumerate(SCENES.items()):
    r, c = divmod(i, cols)
    body += _card(32 + c * (cw + gap), 84 + r * (chh + gap), cw, chh, sid, src["scenes"][sid], spec, "scn")
  body.append(text(W - 32, H - 16, "Generated by figures/fig_c06.py from WP-C-06 §2", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "scn", "Figure 2-1: interaction scenarios as scene cards",
             "Twelve cards in a grid, one per interaction scenario: a top-down pictogram on a one-metre grid with the robot, its direction of travel, its one-metre protective field and rear bumper, the person or persons and their movement, racks, a dock, a screen or a charger where the scenario needs them, a caption and the measure needed.", body)


# ---------------------------------------------------------------- Figure 3-1 detection distance chart


def fig_distance(src: dict) -> str:
  p = src["params"]
  K = _num(p["K"]) or 1.6
  t_r = _num(p["t_r"]) or 0.17
  Z = _num(p["Z"]) or 0.10
  v_nav, v_crawl = 0.20, 0.05
  W, H = 1180, 560
  x0, y0, pw, ph = 90, 104, 760, 380          # plot area
  tmax, Lmax = 2.0, 4.5

  def X(t):
    return x0 + t / tmax * pw

  def Y(L):
    return y0 + ph - L / Lmax * ph

  def L_of(v, tb, C_=0.0):
    d_b = v * tb / 2.0          # coasting from v to 0 at constant deceleration: mean speed v/2
    return v * t_r + d_b + K * (t_r + tb) + Z + C_

  body = [text(32, 34, "Figure 3-1  Minimum detection distance L against the time to standstill after power removal", 15, C["ink"], 700),
          text(32, 52, f"L = v·t_r + d_b + K·(t_r + t_b) + Z + C, with K = {K:g} m/s, t_r = {t_r:g} s, Z = {Z:g} m, d_b = v·t_b/2 (constant deceleration). C drawn as 0 (lines) and as 0.85 m (band top).", 11, C["muted"])]
  body.append(rect(x0, y0, pw, ph, C["white"], C["stroke"], 0))
  for L in (0, 1, 2, 3, 4):
    body.append(f'<line x1="{x0}" y1="{Y(L):.1f}" x2="{x0 + pw}" y2="{Y(L):.1f}" stroke="{C["stroke"]}" stroke-width="1"/>')
    body.append(text(x0 - 10, Y(L) + 4, f"{L} m", 10.5, C["muted"], anchor="end"))
  for t in (0, 0.5, 1.0, 1.5, 2.0):
    body.append(text(X(t), y0 + ph + 18, f"{t:g} s", 10.5, C["muted"], anchor="middle"))
  body.append(text(x0 + pw / 2, y0 + ph + 40, "t_b: time from power removal to standstill (coasting on the Gate A unit; braked on 2.0)", 11, C["muted"], anchor="middle"))
  body.append(text(x0 - 60, y0 - 14, "L, minimum detection distance ahead of the robot", 11, C["muted"]))
  # C band for the navigation speed
  steps = [i * tmax / 40 for i in range(41)]
  upper = [(X(t), Y(min(Lmax, L_of(v_nav, t, 0.85)))) for t in steps]
  lower = [(X(t), Y(L_of(v_nav, t, 0.0))) for t in steps]
  band = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in upper) + " L" + " L".join(f"{a:.1f},{b:.1f}" for a, b in reversed(lower)) + " z"
  body.append(f'<path d="{band}" fill="url(#dst-hatch)" fill-opacity="0.35" stroke="none"/>')
  # robot's own travel at v_nav (thin)
  own = [(X(t), Y(v_nav * t_r + v_nav * t / 2.0)) for t in steps]
  body.append('<path d="M' + " L".join(f"{a:.1f},{b:.1f}" for a, b in own) + f'" fill="none" stroke="{C["dim"]}" stroke-width="1.2" stroke-dasharray="4,3"/>')
  # the two series
  for v, color, label in ((v_nav, C["teal"], "navigation speed 0.20 m/s"), (v_crawl, C["amber"], "crawl speed 0.05 m/s")):
    pts = [(X(t), Y(L_of(v, t))) for t in steps]
    body.append('<path d="M' + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/>')
    xe, ye = pts[-1]
    body.append(f'<circle cx="{xe:.1f}" cy="{ye:.1f}" r="4" fill="{color}" stroke="{C["white"]}" stroke-width="2"/>')
  # direct labels at the right end (text in ink tokens, colour chip beside)
  for v, color, label in ((v_nav, C["teal"], "0.20 m/s"), (v_crawl, C["amber"], "0.05 m/s")):
    ye = Y(L_of(v, tmax))
    body.append(f'<rect x="{x0 + pw + 10}" y="{ye - 6:.1f}" width="10" height="10" rx="2" fill="{color}"/>')
    body.append(text(x0 + pw + 26, ye + 4, label, 10.5, C["ink"], 600))
  # reference: the 1.0 m start value
  body.append(f'<line x1="{x0}" y1="{Y(1.0):.1f}" x2="{x0 + pw}" y2="{Y(1.0):.1f}" stroke="{C["red"]}" stroke-width="1.4" stroke-dasharray="6,4"/>')
  body.append(text(x0 + 8, Y(1.0) - 6, "1.0 m starting field (WP-H-02 §3.3)", 10.5, C["red"], 600))
  # where the 0.20 m/s line crosses 1.0 m with C = 0
  tcross = next((t for t in [i / 1000 for i in range(2001)] if L_of(v_nav, t) >= 1.0), None)
  if tcross is not None:
    body.append(f'<line x1="{X(tcross):.1f}" y1="{Y(1.0):.1f}" x2="{X(tcross):.1f}" y2="{y0 + ph}" stroke="{C["red"]}" stroke-width="1" stroke-dasharray="2,3"/>')
    body.append(text(X(tcross) + 6, y0 + ph - 8, f"t_b ≈ {tcross:.2f} s", 10.5, C["red"], 600))
  # legend
  lx, ly = x0 + pw + 10, y0 + 150
  body.append(text(lx, ly, "KEY", 10.5, C["ink"], 700, extra=' letter-spacing="1"'))
  items = [("L with C = 0", C["teal"], ""), ("L with C = 0.85 m (band)", C["amber"], "hatch"), ("robot's own travel at 0.20 m/s", C["dim"], "4,3"), ("1.0 m start value", C["red"], "6,4")]
  for i, (lab, color, dash) in enumerate(items):
    yy = ly + 20 + i * 36
    if dash == "hatch":
      body.append(f'<rect x="{lx}" y="{yy - 8}" width="24" height="12" fill="url(#dst-hatch)" fill-opacity="0.5"/>')
    else:
      d = f' stroke-dasharray="{dash}"' if dash else ""
      body.append(f'<line x1="{lx}" y1="{yy - 2}" x2="{lx + 24}" y2="{yy - 2}" stroke="{color}" stroke-width="2"{d}/>')
    for j, ln in enumerate(wrap(lab, 250, 10)):
      body.append(text(lx + 30, yy + 2 + j * 12, ln, 10, C["muted"]))
  body.append(text(W - 32, H - 16, "Generated by figures/fig_c06.py from the WP-C-06 §3 parameter table", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "dst", "Figure 3-1: minimum detection distance against the time to standstill",
             "A line chart with the time to standstill after power removal from zero to two seconds across and the minimum detection distance from zero to four and a half metres up: a teal line for the navigation speed and an amber line for the crawl speed, almost parallel because the walking person dominates; a hatched band above the teal line for the intrusion allowance; a thin dashed grey line for the robot's own travel; a red dashed line at one metre for the starting field, which the navigation line crosses at about four tenths of a second.", body)


# ---------------------------------------------------------------- Figure 5-1 misuse matrix


def fig_misuse(src: dict) -> str:
  mu = src["misuse"]
  W, H = 1180, 420
  x0, y0, cw, ch = 200, 90, 300, 130
  cols = [("L", "low"), ("M", "medium"), ("H", "high")]
  rows = [("S2", "serious (S2)"), ("S1", "slight (S1)")]
  body = [text(32, 34, "Figure 5-1  Reasonably foreseeable misuse by likelihood and consequence", 15, C["ink"], 700),
          text(32, 52, "Each cell lists the misuses of §5 that fall in it. The high-likelihood, serious cell is the one information for use alone cannot carry.", 11, C["muted"])]
  for j, (code, label) in enumerate(cols):
    body.append(text(x0 + j * cw + cw / 2, y0 - 12, f"likelihood {label}", 11, C["ink"], 700, "middle"))
  for i, (code, label) in enumerate(rows):
    body.append(text(x0 - 12, y0 + i * ch + ch / 2 + 4, label, 11, C["ink"], 700, "end"))
  for i, (rc, _) in enumerate(rows):
    for j, (cc, _) in enumerate(cols):
      ids = [k for k, m in mu.items() if m["likelihood"].strip() == cc and m["consequence"].strip() == rc]
      hot = (cc == "H" and rc == "S2")
      warm = (rc == "S2" and cc == "M") or (rc == "S1" and cc == "H")
      fill = C["red_bg"] if hot else C["amber_bg"] if warm else C["grey_bg"]
      stroke = C["red"] if hot else C["amber"] if warm else C["stroke"]
      x, y = x0 + j * cw, y0 + i * ch
      body.append(rect(x + 3, y + 3, cw - 6, ch - 6, fill, stroke, 6, 1.4 if hot else 1))
      ty = y + 24
      for k in ids:
        line = f"{k}  {mu[k]['text']}"
        lns = wrap(line, cw - 24, 10)[:1]
        body.append(text(x + 12, ty, lns[0] + ("…" if _w(line, 10) > cw - 24 else ""), 10, C["ink"], 600 if hot else 400))
        ty += 14
      if not ids:
        body.append(text(x + cw / 2, y + ch / 2 + 4, "—", 11, C["dim"], anchor="middle"))
  body.append(text(32, H - 36, "Likelihood: H expected in normal use by the intended users; M occasional or with untrained people; L needs effort or bad luck. Consequence classes of WP-C-03 §2.1.", 10, C["muted"]))
  body.append(text(W - 32, H - 16, "Generated by figures/fig_c06.py from WP-C-06 §5", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "mis", "Figure 5-1: misuse matrix",
             "A two-by-three grid with likelihood low, medium and high across and consequence serious or slight down; the high-likelihood serious cell is outlined red and lists the five misuses that fall in it; the medium-likelihood serious and high-likelihood slight cells are amber; the rest grey.", body)


OUTPUTS = {"fig-c06-2-1-interaction-scenes.svg": fig_scenes, "fig-c06-3-1-detection-distance.svg": fig_distance, "fig-c06-5-1-misuse-matrix.svg": fig_misuse}


def check_source(src: dict) -> list[str]:
  errs = []
  for sid in SCENES:
    if sid not in src["scenes"]:
      errs.append(f"WP-C-06 §2 has no row for {sid}")
  for sid in src["scenes"]:
    if sid not in SCENES:
      errs.append(f"scenario {sid} in WP-C-06 §2 has no scene in fig_c06.py")
  for k in ("K", "t_r", "Z"):
    if k not in src["params"] or _num(src["params"][k]) is None:
      errs.append(f"WP-C-06 §3 parameter {k} missing or without a number")
  for k, m in src["misuse"].items():
    if (m["likelihood"].strip(), m["consequence"].strip()) not in MISUSE_CELLS:
      errs.append(f"{k}: likelihood/consequence {m['likelihood']}/{m['consequence']} outside the matrix")
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
    print("FAIL: stale figures: " + ", ".join(stale) + "; run python3 assurance/02-concept/figures/fig_c06.py")
    return 1
  print("OK: WP-C-06 figures current" if check else "OK: WP-C-06 figures generated")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
