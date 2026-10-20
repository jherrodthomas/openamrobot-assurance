#!/usr/bin/env python3
"""Draw the WP-S-04 stopping-budget figure.

  fig-s04-4-1-field-length-vs-speed.svg   Figure 4-1  minimum detection distance L against speed for the planning decelerations

The source of record is ../WP-S-04-response-time-and-stopping-budget.md: the §1 conventions table (K, Z), the §2
response budget (t_r of the scanner path), the §3.2 stopping-distance table and the §4.1 field-set table. The
check recomputes every t_b, d_s and L of §4.1 and every d_s of §3.2 from L = v·t_r + v²/(2a) + K·(t_r + v/a) + Z
and fails when a table value differs from the formula by more than the rounding, when a §2 row's stages do not
add up to its t_r, when a row's t_r exceeds its target, or when the SVG is stale.

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
  return {"K": K, "Z": Z, "t_r": t_r, "budget": budget, "stop_rows": stop_rows, "fields": fields}


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


OUTPUTS = {"fig-s04-4-1-field-length-vs-speed.svg": fig_field}


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
    print(f"fig_s04: {len(OUTPUTS)} figure current; {len(src['budget'])} budget rows, {len(src['fields'])} field rows recomputed")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
