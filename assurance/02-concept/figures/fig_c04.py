#!/usr/bin/env python3
"""Draw the WP-C-04 safety-function figures.

  fig-c04-2-1-safety-functions.svg   Figure 2-1  one card per safety function: demand → safe state, PLr, category, stop category, response
  fig-c04-7-1-response-budget.svg    Figure 7-1  demand-to-power-removal budget per stop function on one time axis, target markers
  fig-c04-8-1-task-matrix.svg        Figure 8-1  safety function × task applicability

The source of record is ../WP-C-04-safety-functions-and-plr.md: the §2 overview table (ID, name, demand, safe
state, PLr, category, stop category, response target); the §7 budget table (milliseconds per stage and the
target); the §8 applicability table (one cell per task). `--check` fails when an SVG is stale, when a §7 row's
stages do not add up to its total, when a §2 PLr is not a…e, or when an §8 cell uses a word the legend does not.

    python3 fig_c04.py            # regenerate
    python3 fig_c04.py --check    # fail if the source changed or an SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "WP-C-04-safety-functions-and-plr.md"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "stroke": "#D3DDE2", "line": "#7E949B", "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#B86F0C", "amber_bg": "#FFF6E8", "teal": "#00938B", "teal_bg": "#E9F7F5", "red": "#D64535", "red_bg": "#FDEDEB",
  "green": "#2C9A58", "green_bg": "#E8F6EC", "grey_bg": "#EDF2F4", "white": "#FFFFFF",
}
PL_FILL = {"a": "#EAF6F5", "b": "#C9ECE8", "c": "#8FD3CC", "d": "#2FA69C", "e": "#D64535"}
PL_INK = {"a": C["ink"], "b": C["ink"], "c": C["ink"], "d": C["white"], "e": C["white"]}

GROUPS = [("Stops demanded by a person or a detection device", ["SF-01", "SF-02", "SF-09"]),
          ("Monitoring that demands a stop", ["SF-03", "SF-04", "SF-06"]),
          ("Restart, inhibit and warning", ["SF-05", "SF-07", "SF-08"])]
TASKS = ["T-01", "T-02", "T-03", "T-04", "T-05", "T-06", "T-07", "T-08"]
CELL_KINDS = ("active", "active, not claimed", "inhibits", "arming", "—")


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
  m = re.search(r"-?[0-9]+(?:\.[0-9]+)?", s.replace("**", ""))
  return float(m.group(0)) if m else None


def load_source() -> dict:
  text = SOURCE.read_text(encoding="utf-8")
  functions = {}
  for r in _table(text, "## 2. Safety functions"):
    functions[r[0]] = {"name": r[1], "demand": _clean(r[2]), "safe": _clean(r[3]), "plr": _clean(r[4]), "cat": _clean(r[5]),
                       "stop": _clean(r[6]), "response": _clean(r[7]), "hazards": re.findall(r"H-\d\d", r[8])}
  budget = {}
  for r in _table(text, "## 7. Response time and stop category per function"):
    budget[r[0]] = {"stop": _clean(r[1]), "input": _num(r[2]), "logic": _num(r[3]), "power": _num(r[4]), "total": _num(r[5]), "target": _num(r[6]), "standstill": _clean(r[7])}
  tasks_header = None
  i = text.index("## 8. Applicability per task and mode")
  for line in text[i:].splitlines():
    if line.startswith("| SF |"):
      tasks_header = [c.strip() for c in line.strip().strip("|").split("|")][1:]
      break
  matrix = {}
  for r in _table(text, "## 8. Applicability per task and mode"):
    matrix[r[0]] = {tasks_header[k][:4]: _clean(r[k + 1]) for k in range(len(tasks_header))}
  return {"functions": functions, "budget": budget, "matrix": matrix, "task_headers": tasks_header or []}


def _cell_kind(cell: str) -> str:
  c = cell.strip()
  if c == "—":
    return "—"
  if c.startswith("active, not claimed"):
    return "active, not claimed"
  for k in ("active", "inhibits", "arming"):
    if c.startswith(k):
      return k
  return ""


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


def clip(lines: list[str], n: int) -> list[str]:
  if len(lines) <= n:
    return lines
  out = lines[:n]
  out[-1] = out[-1].rstrip(" ,;:")[:-1] + "…"
  return out


def svg(w, h, uid, title, desc, body):
  defs = f"""<defs>
  <marker id="{uid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{C['ink']}"/></marker>
  <pattern id="{uid}-hatch" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="8" stroke="{C['dim']}" stroke-width="1"/></pattern>
</defs>"""
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
          f'<title id="{uid}-t">{escape(title)}</title>\n<desc id="{uid}-d">{escape(desc)}</desc>\n{defs}\n'
          f'<rect x="0" y="0" width="{w}" height="{h}" fill="{C["bg"]}"/>\n' + "\n".join(body) + "\n</svg>\n")


# ---------------------------------------------------------------- Figure 2-1 safety-function cards


def _card(x, y, w, h, sid, f, uid):
  pl = f["plr"][:1].lower()
  out = [rect(x, y, w, h, C["white"], C["stroke"], 8)]
  out.append(f'<path d="M{x + 8},{y} h{w - 16} a8,8 0 0 1 8,8 v22 h-{w} v-22 a8,8 0 0 1 8,-8 z" fill="{PL_FILL[pl]}"/>')
  out.append(text(x + 12, y + 20, sid, 11.5, PL_INK[pl], 700, family=MONO))
  name = f["name"]
  avail = w - 66 - 58
  while name and _w(name, 11.5) > avail:
    name = name[:-1]
  if name != f["name"]:
    name = name.rstrip(" ,") + "…"
  out.append(text(x + 66, y + 20, name, 11.5, PL_INK[pl], 700))
  out.append(text(x + w - 12, y + 20, f"PLr {pl}", 11, PL_INK[pl], 700, "end"))
  # demand → safe state, two columns with an arrow between
  colw = (w - 24 - 34) / 2
  dx, sx = x + 12, x + 12 + colw + 34
  ty = y + 50
  out.append(text(dx, ty, "DEMAND", 9, C["muted"], 700, extra=' letter-spacing="1"'))
  out.append(text(sx, ty, "SAFE STATE", 9, C["muted"], 700, extra=' letter-spacing="1"'))
  dl = clip(wrap(f["demand"], colw, 9.5), 7)
  sl = clip(wrap(f["safe"], colw, 9.5), 7)
  for k, ln in enumerate(dl):
    out.append(text(dx, ty + 16 + k * 12.5, ln, 9.5, C["ink"]))
  for k, ln in enumerate(sl):
    out.append(text(sx, ty + 16 + k * 12.5, ln, 9.5, C["ink"]))
  ay = ty + 16 + 3 * 12.5 - 4
  out.append(f'<line x1="{dx + colw + 6:.1f}" y1="{ay:.1f}" x2="{sx - 8:.1f}" y2="{ay:.1f}" stroke="{C["ink"]}" stroke-width="1.4" marker-end="url(#{uid}-arrow)"/>')
  # badges
  by = y + h - 30
  badges = [("Cat.", f["cat"]), ("stop cat.", f["stop"].split("(")[0].strip() or "—"), ("response", f["response"])]
  bx = x + 12
  for label, val in badges:
    s = f"{label} {val}"
    avail = (x + w - 12) - bx - 14
    if avail < 60:
      break
    if _w(s, 9.5) > avail:
      while s and _w(s + "…", 9.5) > avail:
        s = s[:-1]
      s = s.rstrip(" ,;") + "…"
    bw = _w(s, 9.5) + 14
    out.append(rect(bx, by, bw, 20, C["panel"], C["stroke"], 10))
    out.append(text(bx + 7, by + 14, s, 9.5, C["muted"], 600))
    bx += bw + 6
  return out


def fig_cards(src: dict) -> str:
  fs = src["functions"]
  W = 1180
  cw, ch, gap, x0 = 368, 206, 10, 32
  y = 70
  body = [text(32, 34, "Figure 2-1  The safety functions: demand, safe state and the attributes a safety-requirements specification needs", 15, C["ink"], 700),
          text(32, 52, "One card per function of §2; the header colour is the required Performance Level. Text is the table's, cut with an ellipsis where it does not fit.", 11, C["muted"])]
  for title, ids in GROUPS:
    body.append(text(x0, y + 12, title.upper(), 10, C["muted"], 700, extra=' letter-spacing="1"'))
    y += 22
    for k, sid in enumerate(ids):
      if sid in fs:
        body += _card(x0 + k * (cw + gap), y, cw, ch, sid, fs[sid], "sfc")
    y += ch + 24
  H = y + 20
  # PL legend
  lx = x0
  body.append(text(lx, H - 20, "PLr", 10, C["muted"], 700))
  for i, pl in enumerate("abcde"):
    body.append(rect(lx + 34 + i * 40, H - 32, 32, 16, PL_FILL[pl], PL_FILL[pl] if pl != "a" else C["stroke"], 3))
    body.append(text(lx + 50 + i * 40, H - 20, pl, 10, PL_INK[pl], 700, "middle"))
  body.append(text(W - 32, H - 20, "Generated by figures/fig_c04.py from WP-C-04 §2", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "sfc", "Figure 2-1: safety-function cards",
             "Nine cards in three rows of three, grouped as stops demanded by a person or a device, monitoring that demands a stop, and restart, inhibit and warning; each card has a header coloured by Performance Level with the function's ID and name, a demand column with an arrow to a safe-state column, and badges for category, stop category and response target.", body)


# ---------------------------------------------------------------- Figure 7-1 response budget


def fig_budget(src: dict) -> str:
  b = src["budget"]
  fs = src["functions"]
  W = 1180
  x0, y0, rowh, pw = 250, 110, 56, 640
  tmax = 300.0
  H = y0 + rowh * len(b) + 110

  def X(ms):
    return x0 + ms / tmax * pw

  body = [text(32, 34, "Figure 7-1  Demand-to-power-removal budget per stop function, against its target", 15, C["ink"], 700),
          text(32, 52, "Three segments per function: the detecting device or input window, the logic (speed monitor and safety relay), the power removal (contactors). The red tick is the target of §7. The hatched bar is the standstill, unmeasured.", 11, C["muted"])]
  for ms in (0, 50, 100, 150, 200, 250, 300):
    body.append(f'<line x1="{X(ms):.1f}" y1="{y0 - 10}" x2="{X(ms):.1f}" y2="{y0 + rowh * len(b)}" stroke="{C["stroke"]}" stroke-width="1"/>')
    body.append(text(X(ms), y0 - 16, f"{ms} ms", 10, C["muted"], anchor="middle"))
  segs = [("input", C["dim"]), ("logic", C["teal"]), ("power", C["amber"])]
  for i, (sid, r) in enumerate(b.items()):
    y = y0 + i * rowh
    if i % 2 == 0:
      body.append(rect(28, y, W - 56, rowh, C["panel"], "none", 0, 0))
    body.append(text(32, y + 24, sid, 11, C["ink"], 700, family=MONO))
    name = fs.get(sid, {}).get("name", "")
    for k, ln in enumerate(clip(wrap(name, 180, 10), 2)):
      body.append(text(32, y + 40 + k * 12, ln, 10, C["muted"]))
    body.append(text(x0 - 8, y + 24, f"stop cat. {r['stop']}", 9.5, C["muted"], anchor="end"))
    x = x0
    by, bh = y + 14, 22
    for key, color in segs:
      v = r[key] or 0.0
      if v > 0:
        body.append(f'<rect x="{x:.1f}" y="{by}" width="{max(X(v) - X(0) - 2, 1):.1f}" height="{bh}" fill="{color}"/>')
        if X(v) - X(0) > 34:
          body.append(text(x + (X(v) - X(0)) / 2, by + 15, f"{v:g}", 9.5, C["white"] if key != "input" else C["ink"], 700, "middle"))
        x = X(v) - X(0) + x
    total = r["total"] or 0.0
    body.append(f'<rect x="{x + 2:.1f}" y="{by}" width="{min(X(total + 60), x0 + pw + 60) - x - 2:.1f}" height="{bh}" fill="url(#rb-hatch)" fill-opacity="0.6" stroke="none"/>')
    body.append(text(x + 8, by + bh + 14, f"total {total:g} ms", 9.5, C["ink"], 600))
    t = r["target"]
    if t is not None:
      over = total > t
      body.append(f'<line x1="{X(t):.1f}" y1="{by - 6}" x2="{X(t):.1f}" y2="{by + bh + 6}" stroke="{C["red"]}" stroke-width="2"/>')
      body.append(text(X(t) + 5, by - 6, f"target {t:g}" + (" · over by the relay time" if over else ""), 9.5, C["red"], 600))
  ly = y0 + rowh * len(b) + 26
  for k, (label, color) in enumerate([("device or input window", C["dim"]), ("logic", C["teal"]), ("power removal", C["amber"])]):
    body.append(rect(32 + k * 220, ly, 18, 12, color, color, 2))
    body.append(text(56 + k * 220, ly + 10, label, 10.5, C["muted"]))
  body.append(rect(32 + 660, ly, 18, 12, "url(#rb-hatch)", C["stroke"], 2))
  body.append(text(56 + 660, ly + 10, "standstill after power removal (TBC, WP-V-02)", 10.5, C["muted"]))
  body.append(text(32, ly + 34, "Budget from WP-H-02 §3.2 for the candidate parts; SF-05, SF-07 and SF-08 are not timed stops and are not drawn.", 10, C["muted"]))
  body.append(text(W - 32, H - 12, "Generated by figures/fig_c04.py from WP-C-04 §7", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "rb", "Figure 7-1: response budget per stop function",
             "Six horizontal bars on one time axis from zero to three hundred milliseconds, one per stop function, each made of a grey input segment, a teal logic segment and an amber power-removal segment with the milliseconds written in, a red target tick per bar, and a hatched tail for the unmeasured standstill; every bar ends before its tick except the loss-of-command function, which overshoots by the relay time.", body)


# ---------------------------------------------------------------- Figure 8-1 task matrix


def fig_matrix(src: dict) -> str:
  m = src["matrix"]
  fs = src["functions"]
  heads = src["task_headers"]
  W = 1180
  rowh, colw, x0, y0 = 50, 104, 300, 116
  H = y0 + rowh * len(m) + 80
  styles = {"active": (C["teal_bg"], C["teal"], ""), "active, not claimed": (C["teal_bg"], C["teal"], "4,3"), "inhibits": (C["grey_bg"], C["stroke"], ""),
            "arming": (C["amber_bg"], C["amber"], ""), "—": (C["white"], C["stroke"], "")}
  body = [text(32, 34, "Figure 8-1  Which safety function is active in which task", 15, C["ink"], 700),
          text(32, 52, "Cells from the §8 table. Teal: active and claimed; dashed teal: present but not the claimed measure; grey: the function inhibits; amber: the bench paths are admitted under arming; white: not applicable.", 11, C["muted"])]
  for j, h in enumerate(heads):
    x = x0 + j * colw
    tid = h[:4]
    rest = h[5:]
    body.append(text(x + colw / 2, y0 - 26, tid, 12, C["ink"], 700, "middle"))
    body.append(text(x + colw / 2, y0 - 11, rest, 9.5, C["muted"], anchor="middle"))
  for i, (sid, cells) in enumerate(m.items()):
    y = y0 + i * rowh
    body.append(text(32, y + 20, sid, 11, C["ink"], 700, family=MONO))
    name = fs.get(sid, {}).get("name", "")
    for k, ln in enumerate(clip(wrap(name, 200, 10), 2)):
      body.append(text(84, y + 20 + k * 12, ln, 10, C["muted"]))
    for j, h in enumerate(heads):
      cell = cells[h[:4]]
      kind = _cell_kind(cell)
      fill, stroke, dash = styles.get(kind, (C["red_bg"], C["red"], ""))
      x = x0 + j * colw
      body.append(rect(x + 3, y + 3, colw - 6, rowh - 6, fill, stroke, 4, 1, dash))
      qual = re.sub(r"^(active, not claimed|active|inhibits|arming|—)\s*", "", cell).strip("() ")
      label = kind if kind != "active, not claimed" else "not claimed"
      if kind == "—":
        body.append(text(x + colw / 2, y + rowh / 2 + 4, "—", 11, C["dim"], anchor="middle"))
        continue
      body.append(text(x + colw / 2, y + 19, label, 10, C["ink"], 600, "middle"))
      for k, ln in enumerate(clip(wrap(qual, colw - 14, 8.5), 2)):
        body.append(text(x + colw / 2, y + 31 + k * 10, ln, 8.5, C["muted"], anchor="middle"))
  ly = y0 + rowh * len(m) + 22
  for k, (kind, label) in enumerate([("active", "active, claimed"), ("active, not claimed", "present, not the claimed measure"), ("inhibits", "inhibits"), ("arming", "arming admits the bench paths"), ("—", "not applicable")]):
    fill, stroke, dash = styles[kind]
    dx = [0, 170, 420, 520, 760][k]
    body.append(rect(32 + dx, ly, 18, 14, fill, stroke, 2, 1, dash))
    body.append(text(58 + dx, ly + 11, label, 10.5, C["muted"]))
  body.append(text(W - 32, H - 12, "Generated by figures/fig_c04.py from WP-C-04 §8", 9.5, C["dim"], anchor="end"))
  return svg(W, H, "stm", "Figure 8-1: safety function by task",
             "A grid with the nine safety functions down the side and the eight tasks across; teal cells where the function is active and claimed, dashed teal where it is present but not the claimed measure, grey where it inhibits, amber for the armed bench image, white where it does not apply; each cell carries the qualifier of the table.", body)


OUTPUTS = {"fig-c04-2-1-safety-functions.svg": fig_cards, "fig-c04-7-1-response-budget.svg": fig_budget, "fig-c04-8-1-task-matrix.svg": fig_matrix}


def check_source(src: dict) -> list[str]:
  errs = []
  for sid, f in src["functions"].items():
    if f["plr"][:1].lower() not in PL_FILL:
      errs.append(f"{sid}: PLr {f['plr']!r} is not a…e")
  grouped = [s for _, ids in GROUPS for s in ids]
  for sid in src["functions"]:
    if sid not in grouped:
      errs.append(f"{sid} in WP-C-04 §2 has no card group in fig_c04.py")
  for sid in grouped:
    if sid not in src["functions"]:
      errs.append(f"WP-C-04 §2 has no row for {sid}")
  for sid, r in src["budget"].items():
    if sid not in src["functions"]:
      errs.append(f"§7 row {sid} is not a function of §2")
    if None in (r["input"], r["logic"], r["power"], r["total"], r["target"]):
      errs.append(f"§7 row {sid}: a stage, the total or the target has no number")
    elif abs(r["input"] + r["logic"] + r["power"] - r["total"]) > 0.5:
      errs.append(f"§7 row {sid}: stages add to {r['input'] + r['logic'] + r['power']:g}, the row says {r['total']:g}")
  if [h[:4] for h in src["task_headers"]] != TASKS:
    errs.append(f"§8 columns are {[h[:4] for h in src['task_headers']]}, expected {TASKS}")
  for sid, cells in src["matrix"].items():
    if sid not in src["functions"]:
      errs.append(f"§8 row {sid} is not a function of §2")
    for tid, cell in cells.items():
      if _cell_kind(cell) not in CELL_KINDS:
        errs.append(f"§8 {sid}/{tid}: cell {cell!r} does not start with one of {CELL_KINDS}")
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
    print(f"fig_c04: {len(OUTPUTS)} figures current; {len(src['functions'])} functions, {len(src['budget'])} budget rows")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
