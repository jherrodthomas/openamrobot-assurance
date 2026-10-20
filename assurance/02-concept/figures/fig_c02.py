#!/usr/bin/env python3
"""Draw the WP-C-02 operating-environment figures.

  fig-c02-2-1-zones.svg              Figure 2-1  schematic site plan with zones Z0…Z5, people class and speed limit per
                                                  zone, the robot footprint, protective field and rear bumper to scale
  fig-c02-3-1-task-zone-matrix.svg   Figure 3-1  task-by-zone matrix: permitted now, permitted with safety functions,
                                                  excluded; speed limit in the cell

The source of record is ../WP-C-02-operating-environment-and-tasks.md: zone IDs, names, people class and speed
limit are read from the §2 table; task IDs and names from the §3 table. The plan geometry and the permission per
cell are listed here and checked against those IDs. `--check` fails when a source row is gone or an SVG is stale.

    python3 fig_c02.py            # regenerate
    python3 fig_c02.py --check    # fail if the source tables changed or an SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "WP-C-02-operating-environment-and-tasks.md"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "stroke": "#D3DDE2", "line": "#7E949B", "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#D4821A", "amber_bg": "#FFF6E8", "cyan": "#0E8C83", "cyan_bg": "#E9F7F5", "red": "#D64535", "red_bg": "#FDEDEB",
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


def load_source() -> dict:
  text = SOURCE.read_text(encoding="utf-8")
  zones = {r[0]: {"name": r[1], "people": r[5], "speed": r[6]} for r in _table(text, "## 2. Zones")}
  tasks = {r[0]: {"what": r[1], "zone": r[2], "speed": r[4]} for r in _table(text, "## 3. Tasks")}
  return {"zones": zones, "tasks": tasks}


# Permission per task and zone: "now" (inside the case at BL-001), "sf" (once the named safety functions exist), "no".
MATRIX = {
  "T-01": {"Z1": ("now", "0.20 m/s"), "Z2": ("sf", "0.20 m/s · SF-02, SF-03"), "Z3": ("no", ""), "Z4": ("no", ""), "Z5": ("no", "excluded")},
  "T-02": {"Z1": ("now", "0"), "Z2": ("sf", "0 · SF-05"), "Z3": ("no", ""), "Z4": ("no", ""), "Z5": ("no", "excluded")},
  "T-03": {"Z1": ("now", "crawl, lane empty"), "Z2": ("no", ""), "Z3": ("sf", "0.05 m/s · SF-02 lane field"), "Z4": ("no", ""), "Z5": ("no", "excluded")},
  "T-04": {"Z1": ("now", "crawl, observer behind"), "Z2": ("no", ""), "Z3": ("sf", "0.05 m/s · rear bumper"), "Z4": ("no", ""), "Z5": ("no", "excluded")},
  "T-05": {"Z1": ("no", ""), "Z2": ("no", ""), "Z3": ("no", ""), "Z4": ("sf", "0 · charge interlock"), "Z5": ("no", "excluded")},
  "T-06": {"Z1": ("now", "0.20 m/s"), "Z2": ("sf", "0.20 / 0.10 m/s · SF-01, deadman"), "Z3": ("sf", "crawl"), "Z4": ("sf", "crawl"), "Z5": ("no", "excluded")},
  "T-07": {"Z1": ("now", "as T-06"), "Z2": ("sf", "as T-06, floor empty"), "Z3": ("no", ""), "Z4": ("no", ""), "Z5": ("no", "excluded")},
  "T-08": {"Z1": ("now", "wheels off the ground"), "Z2": ("no", ""), "Z3": ("no", ""), "Z4": ("no", ""), "Z5": ("no", "")},
}
ZONE_ORDER = ["Z1", "Z2", "Z3", "Z4", "Z5"]


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
  <pattern id="{uid}-hatch" patternUnits="userSpaceOnUse" width="10" height="10" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="10" stroke="{C['dim']}" stroke-width="1.2"/></pattern>
  <pattern id="{uid}-grid" patternUnits="userSpaceOnUse" width="40" height="40">
    <path d="M40,0 L0,0 L0,40" fill="none" stroke="{C['stroke']}" stroke-width="0.8"/></pattern>
</defs>"""
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
          f'<title id="{uid}-t">{escape(title)}</title>\n<desc id="{uid}-d">{escape(desc)}</desc>\n{defs}\n'
          f'<rect x="0" y="0" width="{w}" height="{h}" fill="{C["bg"]}"/>\n' + "\n".join(body) + "\n</svg>\n")


# ---------------------------------------------------------------- Figure 2-1 zone plan (1 m = 40 px)

M = 40.0  # px per metre


def _clean(cell: str) -> str:
  """First clause of a table cell without Markdown emphasis; a leading (TBC) marker becomes a word."""
  s = cell.replace("**", "").split(";")[0].strip()
  if s.startswith("(TBC)"):
    s = "TBC" + s[5:]
  return s


def fig_zones(src: dict) -> str:
  W, H = 1180, 700
  z = src["zones"]
  body = [text(32, 34, "Figure 2-1  Zones of the operating environment (schematic site plan, 1 m grid)", 15, C["ink"], 700),
          text(32, 52, "Each zone with its people class and speed limit from §2. Only Z1 is inside the case at BL-001. The robot, its 1.0 m starting protective field and the rear bumper are to scale.", 11, C["muted"])]
  px, py, pw, ph = 32, 76, 900, 560   # plan area: 22.5 m x 14 m
  body.append(rect(px, py, pw, ph, f"url(#zon-grid)", C["ink"], 4, 1.2))
  body.append(rect(px, py, pw, ph, "none", C["ink"], 4, 1.2))
  # Z0 surroundings (hatched band at the bottom: loading dock edge) and a glass wall on the right
  body.append(rect(px, py + ph - 2.0 * M, pw, 2.0 * M, "url(#zon-hatch)", C["dim"], 0))
  body.append(text(px + 10, py + ph - 2.0 * M + 18, "Z0  excluded: loading-dock edge (drop), outdoor beyond", 11, C["ink"], 600))

  def zone(x_m, y_m, w_m, h_m, zid, fill, stroke, dash=""):
    x, y, w, h = px + x_m * M, py + y_m * M, w_m * M, h_m * M
    out = [rect(x, y, w, h, fill, stroke, 3, 1.4, dash)]
    name = z[zid]["name"]
    title_lines = wrap(f"{zid}  {name}", w - 16, 12)[:2]
    ty = y + 18
    for ln in title_lines:
      out.append(text(x + 8, ty, ln, 12, C["ink"], 700))
      ty += 15
    people = _clean(z[zid]["people"]).split(":")[0]
    speed = _clean(z[zid]["speed"])
    ty += 1
    for ln in wrap("people: " + people, w - 16, 10.5)[:2]:
      out.append(text(x + 8, ty, ln, 10.5, C["muted"]))
      ty += 13
    for ln in wrap("speed: " + speed, w - 16, 10.5)[:2]:
      out.append(text(x + 8, ty, ln, 10.5, C["muted"]))
      ty += 13
    return out

  # Z5 public corridor across the top (excluded), Z2 aisle in the middle, Z1 test area left, Z3 dock lane and Z4 bay right
  body += zone(0, 0, 22.5, 2.5, "Z5", "url(#zon-hatch)", C["dim"], "6,4")
  body += zone(0, 3.0, 8.0, 8.5, "Z1", C["green_bg"], C["green"])
  body += zone(8.5, 3.0, 14.0, 3.5, "Z2", C["amber_bg"], C["amber"])
  body += zone(14.0, 7.0, 5.0, 4.5, "Z3", C["amber_bg"], C["amber"], "6,4")
  body += zone(19.5, 7.0, 3.0, 4.5, "Z4", C["grey_bg"], C["line"])
  # racks along the aisle
  for i in range(3):
    rx = px + (9.0 + i * 1.6) * M
    body.append(rect(rx, py + 7.2 * M, 1.0 * M, 3.4 * M, C["grey_bg"], C["line"], 2))
  body.append(text(px + 9.0 * M, py + 11.2 * M + 14, "racks, pallets (fixed obstacles)", 10, C["dim"]))
  # dock at the end of the lane
  body.append(rect(px + 18.3 * M, py + 7.6 * M, 0.5 * M, 1.6 * M, C["cyan_bg"], C["cyan"], 2, 1.4))
  body.append(text(px + 16.5 * M, py + 9.6 * M, "dock, 3 AprilTags, well lit", 10, C["cyan"], anchor="middle"))
  for i, ln in enumerate(wrap("lane marked; 2 m approach; nobody inside during a dock or undock", 4.6 * M, 10)):
    body.append(text(px + 14.2 * M, py + 10.4 * M + i * 12, ln, 10, C["muted"]))
  # charger in the bay
  body.append(text(px + 19.7 * M, py + 11.2 * M, "charger, mains inlet", 10, C["muted"]))
  # the robot in Z1, to scale: 0.805 m x 0.58 m, facing right, with the 1.0 m field and the rear bumper
  rx, ry = px + 2.5 * M, py + 7.0 * M
  rl, rw = 0.805 * M, 0.58 * M
  field = [(rx + rl, ry - 0.1 * M), (rx + rl + 1.0 * M, ry - 0.25 * M), (rx + rl + 1.0 * M, ry + rw + 0.25 * M), (rx + rl, ry + rw + 0.1 * M)]
  body.append('<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in field) + f' z" fill="{C["cyan"]}" fill-opacity="0.18" stroke="{C["cyan"]}" stroke-width="1.2" stroke-dasharray="4,3"/>')
  body.append(rect(rx, ry, rl, rw, C["white"], C["ink"], 3, 1.4))
  body.append(rect(rx - 0.06 * M, ry + 0.04 * M, 0.06 * M, rw - 0.08 * M, C["red"], C["red"], 1))
  body.append(text(rx + rl / 2, ry + rw / 2 + 4, "robot", 10, C["ink"], 600, "middle"))
  body.append(text(rx + rl + 1.05 * M, ry - 0.3 * M, "front scanner field, 1.0 m start value (WP-H-02 §3.3)", 10, C["cyan"]))
  body.append(text(rx - 0.1 * M, ry + rw + 0.5 * M, "rear bumper", 10, C["red"]))
  body.append(text(px + 0.3 * M, py + 10.9 * M, "boundary marked; 2 m clear margin; operator + observer only", 10, C["muted"]))
  # right-hand key
  kx = px + pw + 24
  body.append(text(kx, py + 14, "KEY", 11, C["ink"], 700, extra=' letter-spacing="1"'))
  items = [(C["green_bg"], C["green"], "inside the case at BL-001 (Z1, under WP-V-07)"), (C["amber_bg"], C["amber"], "needs the named safety functions (Z2, Z3)"),
           (C["grey_bg"], C["line"], "robot stopped; electrical measures (Z4)"), ("url(#zon-hatch)", C["dim"], "excluded (Z0, Z5)")]
  y = py + 30
  for fill, stroke, label in items:
    body.append(rect(kx, y, 18, 14, fill, stroke, 2))
    for i, ln in enumerate(wrap(label, 200, 10.5)):
      body.append(text(kx + 26, y + 11 + i * 13, ln, 10.5, C["muted"]))
    y += 16 + 13 * max(0, len(wrap(label, 200, 10.5)) - 1) + 8
  y += 10
  for ln in wrap("Geometry is schematic: a 22.5 m by 14 m slice of an SME floor. Real sites are surveyed and marked per §6; the zone table, not this drawing, is the specification.", 210, 10):
    body.append(text(kx, y, ln, 10, C["dim"]))
    y += 12
  body.append(text(W - 32, H - 20, "Generated by figures/fig_c02.py from WP-C-02 §2 · 1 grid square = 1 m", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "zon", "Figure 2-1: zones of the operating environment as a schematic site plan",
             "A schematic plan on a one-metre grid: the development test area Z1 in green on the left, the transport aisle Z2 in amber across the middle with racks below it, the dock lane Z3 with the dock at its end and the charging bay Z4 on the right, the public corridor Z5 hatched along the top and the loading-dock edge Z0 hatched along the bottom; the robot to scale in Z1 with its one-metre front scanner field and rear bumper; a key explains the colours.", body)


# ---------------------------------------------------------------- Figure 3-1 task-by-zone matrix


def fig_matrix(src: dict) -> str:
  tasks = src["tasks"]
  zones = src["zones"]
  W = 1180
  rowh, colw, x0, y0 = 54, 176, 262, 110
  H = y0 + rowh * len(tasks) + 70
  body = [text(32, 34, "Figure 3-1  Task-by-zone matrix: where each task may run, now and once the safety functions exist", 15, C["ink"], 700),
          text(32, 52, "Green: inside the case at BL-001. Amber: permitted once the named safety function is validated. Grey: excluded. The cell gives the speed limit of §3.", 11, C["muted"])]
  for j, zid in enumerate(ZONE_ORDER):
    x = x0 + j * colw
    body.append(text(x + colw / 2, y0 - 26, zid, 12, C["ink"], 700, "middle"))
    body.append(text(x + colw / 2, y0 - 11, zones[zid]["name"][:30], 10, C["muted"], anchor="middle"))
  for i, (tid, t) in enumerate(tasks.items()):
    y = y0 + i * rowh
    body.append(text(32, y + 20, tid, 11, C["ink"], 700, family=MONO))
    lines = wrap(t["what"].split(":")[0], 190, 10.5)[:2]
    for k, ln in enumerate(lines):
      body.append(text(80, y + 20 + k * 13, ln, 10.5, C["muted"]))
    for j, zid in enumerate(ZONE_ORDER):
      kind, label = MATRIX[tid][zid]
      fill, stroke = {"now": (C["green_bg"], C["green"]), "sf": (C["amber_bg"], C["amber"]), "no": (C["grey_bg"], C["stroke"])}[kind]
      x = x0 + j * colw
      body.append(rect(x + 3, y + 3, colw - 6, rowh - 6, fill, stroke, 4))
      lab = label or "—"
      for k, ln in enumerate(wrap(lab, colw - 16, 10)[:2]):
        body.append(text(x + colw / 2, y + 23 + k * 13, ln, 10, C["ink"] if kind != "no" else C["dim"], 600 if kind == "now" else 400, "middle"))
  ly = y0 + rowh * len(tasks) + 24
  for fill, stroke, label, dx in [(C["green_bg"], C["green"], "inside the case at BL-001 (test area, WP-V-07)", 0), (C["amber_bg"], C["amber"], "permitted once the named safety function is validated", 330), (C["grey_bg"], C["stroke"], "excluded", 720)]:
    body.append(rect(32 + dx, ly, 18, 14, fill, stroke, 2))
    body.append(text(58 + dx, ly + 11, label, 10.5, C["muted"]))
  body.append(text(W - 32, H - 12, "Generated by figures/fig_c02.py from WP-C-02 §2 and §3", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "mtx", "Figure 3-1: task-by-zone matrix",
             "A grid with the eight tasks down the side and the five zones across: green cells where the task is inside the case at the current baseline, all of them in the test area; amber cells where it becomes permitted once a named safety function is validated, with the speed limit written in; grey cells excluded.", body)


OUTPUTS = {"fig-c02-2-1-zones.svg": fig_zones, "fig-c02-3-1-task-zone-matrix.svg": fig_matrix}


def check_source(src: dict) -> list[str]:
  errs = []
  for zid in ["Z0"] + ZONE_ORDER:
    if zid not in src["zones"]:
      errs.append(f"WP-C-02 §2 has no row for {zid}")
  for tid in MATRIX:
    if tid not in src["tasks"]:
      errs.append(f"WP-C-02 §3 has no row for {tid}")
  for tid in src["tasks"]:
    if tid not in MATRIX:
      errs.append(f"task {tid} in WP-C-02 §3 has no matrix row in fig_c02.py")
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
    print("FAIL: stale figures: " + ", ".join(stale) + "; run python3 assurance/02-concept/figures/fig_c02.py")
    return 1
  print("OK: WP-C-02 figures current" if check else "OK: WP-C-02 figures generated")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
