#!/usr/bin/env python3
"""Draw the WP-S-02 safety-requirements figures.

  fig-s02-17-1-verification-methods.svg   Figure 17-1  per block, how many requirements each verification method covers
  fig-s02-18-1-requirement-map.svg        Figure 18-1  one row per function, one chip per requirement coloured by type

The source of record is ../WP-S-02-safety-requirements.md: every `| SR-nn.mm |` row of its requirement tables
(ID, requirement, type, PLr, verification, implemented by, configuration, trace) and the §18 traceability table. The
check also reads ../../02-concept/WP-C-04-safety-functions-and-plr.md §2 (function names and PLr) and
../../02-concept/WP-C-03-risk-assessment.md §4 (the hazard IDs). `--check` fails when an SVG is stale, when a
requirement sits under the wrong function heading or repeats an ID, when its type, verification method, PLr or
configuration uses a letter the conventions of §1 do not, when a traced hazard is not in WP-C-03 §4, when a
function's highest PLr disagrees with WP-C-04 §2 or with the §18 table, when the §18 ranges or hazard lists do not
match the rows, or when the text cites an SR that does not exist.

    python3 fig_s02.py            # regenerate
    python3 fig_s02.py --check    # fail if the source changed or an SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "WP-S-02-safety-requirements.md"
WP_C04 = HERE.parent.parent / "02-concept" / "WP-C-04-safety-functions-and-plr.md"
WP_C03 = HERE.parent.parent / "02-concept" / "WP-C-03-risk-assessment.md"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "stroke": "#D3DDE2", "line": "#7E949B", "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#B86F0C", "amber_bg": "#FFF6E8", "teal": "#00938B", "teal_bg": "#E9F7F5", "red": "#D64535", "red_bg": "#FDEDEB",
  "green": "#2C9A58", "green_bg": "#E8F6EC", "grey_bg": "#EDF2F4", "white": "#FFFFFF",
}
PL_FILL = {"a": "#EAF6F5", "b": "#C9ECE8", "c": "#8FD3CC", "d": "#2FA69C", "e": "#D64535"}
PL_INK = {"a": C["ink"], "b": C["ink"], "c": C["ink"], "d": C["white"], "e": C["white"]}
PL_RANK = {"—": 0, "a": 1, "b": 2, "c": 3, "d": 4, "e": 5}

TYPES = {"F": ("functional", C["teal"], C["teal_bg"]), "I": ("integrity", C["muted"], C["grey_bg"]),
         "T": ("timing", C["amber"], C["amber_bg"]), "D": ("diagnostic", C["green"], C["green_bg"]),
         "S": ("security", C["red"], C["red_bg"])}
METHODS = {"A": ("analysis", C["muted"]), "I": ("inspection", C["amber"]), "T": ("test", C["teal"]), "D": ("demonstration", C["green"])}
CONFIGS = ("CFG-001", "CFG-002", "both")
BLOCKS = ["00"] + [f"{i:02d}" for i in range(1, 13)] + ["90"]
BLOCK_LABEL = {"00": "common", "90": "security"}


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


def _letters(cell: str) -> list[str]:
  return [p.strip() for p in _clean(cell).split(",") if p.strip()]


def load_source() -> dict:
  text = SOURCE.read_text(encoding="utf-8")
  rows: dict[str, dict] = {}
  order: list[str] = []
  section = None
  for line in text.splitlines():
    m = re.match(r"## \d+\. (.*)", line)
    if m:
      h = m.group(1)
      sf = re.match(r"SF-(\d\d)\b", h)
      section = sf.group(1) if sf else ("00" if h.startswith("Requirements common") else "90" if h.startswith("Security") else None)
      continue
    m = re.match(r"\| (SR-(\d\d)\.(\d\d)) \|", line)
    if not m:
      continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    sid = m.group(1)
    rows[sid] = {"id": sid, "block": m.group(2), "n": int(m.group(3)), "section": section, "ncells": len(cells),
                 "text": _clean(cells[1]) if len(cells) > 1 else "", "types": _letters(cells[2]) if len(cells) > 2 else [],
                 "plr": _clean(cells[3]) if len(cells) > 3 else "", "verif": _letters(cells[4]) if len(cells) > 4 else [],
                 "by": _clean(cells[5]) if len(cells) > 5 else "", "config": _clean(cells[6]) if len(cells) > 6 else "",
                 "trace": re.findall(r"H-\d\d", cells[7]) if len(cells) > 7 else [], "tbc": "(TBC" in cells[1]}
    order.append(sid)
  trace = {}
  for r in _table(text, "## 18. Traceability"):
    key = r[0] if r[0] in ("common", "security") else r[0]
    trace[key] = {"range": _clean(r[1]), "plr": _clean(r[2]), "hazards": re.findall(r"H-\d\d", r[3]) if r[3].strip() != "all" else "all", "claim": _clean(r[4])}
  cited = sorted(set(re.findall(r"SR-\d\d\.\d\d", text)))
  functions = {}
  for r in _table(WP_C04.read_text(encoding="utf-8"), "## 2. Safety functions"):
    functions[r[0]] = {"name": re.sub(r"\s*\(CFG-002\)\s*$", "", _clean(r[1])), "plr": _clean(r[4])[:1].lower(), "cfg2": "(CFG-002)" in r[1]}
  hazards = [r[0] for r in _table(WP_C03.read_text(encoding="utf-8"), "## 4. Hazard identification") if re.match(r"H-\d\d$", r[0])]
  return {"rows": rows, "order": order, "trace": trace, "cited": cited, "functions": functions, "hazards": hazards}


def _block_rows(src: dict, block: str) -> list[dict]:
  return [src["rows"][s] for s in src["order"] if src["rows"][s]["block"] == block]


def _block_plr(src: dict, block: str) -> str:
  best = "—"
  for r in _block_rows(src, block):
    p = r["plr"][:1].lower() if r["plr"] else "—"
    if PL_RANK.get(p, 0) > PL_RANK[best]:
      best = p
  return best


def _block_name(src: dict, block: str) -> str:
  if block in BLOCK_LABEL:
    return {"00": "Common to every function", "90": "Security supporting the functions"}[block]
  return src["functions"].get(f"SF-{block}", {}).get("name", "")


def _w(s: str, size: float) -> float:
  return len(s) * size * 0.56


def _ell(s: str, width: float, size: float) -> str:
  if _w(s, size) <= width:
    return s
  while s and _w(s + "…", size) > width:
    s = s[:-1]
  return s.rstrip(" ,;:") + "…"


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


def _pl_badge(x, y, plr, size=24):
  p = plr[:1].lower() if plr else "—"
  if p in PL_FILL:
    return [rect(x, y, size, size, PL_FILL[p], stroke=PL_FILL[p], r=5), text(x + size / 2, y + size * 0.7, p, 12, PL_INK[p], 700, "middle")]
  return [rect(x, y, size, size, C["grey_bg"], r=5), text(x + size / 2, y + size * 0.7, "—", 12, C["dim"], 600, "middle")]


def _row_label(x, y, block, name, cfg2, labelw):
  head = f"SF-{block}" if block not in BLOCK_LABEL else BLOCK_LABEL[block]
  out = [text(x, y + 14, head, 12, C["ink"], 700)]
  if cfg2:
    out.append(text(x + _w(head, 12) + 8, y + 14, "CFG-002 only", 10, C["amber"], 600))
  out.append(text(x, y + 29, _ell(name, labelw, 10.5), 10.5, C["muted"]))
  return out


# ---------------------------------------------------------------- Figure 18-1 requirement map


def fig_map(src: dict) -> str:
  W = 1040
  labelx, labelw = 24, 270
  badgex = labelx + labelw + 8
  chipx, chipw, chiph, gap = badgex + 40, 58, 24, 5
  rowh = 40
  top = 66
  rows_n = len(BLOCKS)
  legend_y = top + rows_n * rowh + 18
  H = legend_y + 58
  uid = "s02-18-1"
  n_total = len(src["order"])
  n_cfg2 = sum(1 for r in src["rows"].values() if r["config"] == "CFG-002")
  n_tbc = sum(1 for r in src["rows"].values() if r["tbc"])
  body = [text(24, 28, f"Figure 18-1  Requirement map: {n_total} requirements, SR-00 to SR-90", 15, C["ink"], 700),
          text(24, 46, f"One chip per requirement, coloured by type; a dashed border marks the {n_cfg2} CFG-002-only requirements, a dot the {n_tbc} with a value to be confirmed",
               11, C["muted"])]
  for i, block in enumerate(BLOCKS):
    y = top + i * rowh
    if i % 2 == 0:
      body.append(rect(16, y - 2, W - 32, rowh, C["panel"], stroke="none", r=4))
    f = src["functions"].get(f"SF-{block}", {})
    body += _row_label(labelx, y + 2, block, _block_name(src, block), f.get("cfg2", False), labelw)
    body += _pl_badge(badgex, y + 6, _block_plr(src, block))
    for k, r in enumerate(_block_rows(src, block)):
      x = chipx + k * (chipw + gap)
      t = r["types"][0] if r["types"] else "F"
      _, hue, tint = TYPES.get(t, TYPES["F"])
      dash = "4,3" if r["config"] == "CFG-002" else ""
      body.append(rect(x, y + 6, chipw, chiph, tint, stroke=hue, r=5, sw=1.4, dash=dash))
      body.append(text(x + chipw / 2, y + 6 + chiph * 0.68, r["id"], 10, hue, 600, "middle", MONO))
      if r["tbc"]:
        body.append(f'<circle cx="{x + chipw - 4:.1f}" cy="{y + 10:.1f}" r="4" fill="{C["amber"]}" stroke="{C["white"]}" stroke-width="1.5"/>')
  # legend
  x = 24
  body.append(text(x, legend_y + 12, "Type", 10.5, C["muted"], 700))
  x += 36
  for t, (name, hue, tint) in TYPES.items():
    body.append(rect(x, legend_y + 2, 22, 14, tint, stroke=hue, r=4, sw=1.4))
    body.append(text(x + 11, legend_y + 12.5, t, 9, hue, 700, "middle", MONO))
    body.append(text(x + 28, legend_y + 12.5, name, 10.5, C["ink"]))
    x += 36 + _w(name, 10.5) + 18
  x += 10
  body.append(rect(x, legend_y + 2, 22, 14, C["white"], stroke=C["ink"], r=4, sw=1.4, dash="4,3"))
  body.append(text(x + 28, legend_y + 12.5, "CFG-002 only (2.0 manipulator, unverified)", 10.5, C["ink"]))
  x += 28 + _w("CFG-002 only (2.0 manipulator, unverified)", 10.5) + 18
  body.append(f'<circle cx="{x + 6:.1f}" cy="{legend_y + 9:.1f}" r="4" fill="{C["amber"]}" stroke="{C["white"]}" stroke-width="1.5"/>')
  body.append(text(x + 18, legend_y + 12.5, "value (TBC)", 10.5, C["ink"]))
  y2 = legend_y + 32
  body.append(text(24, y2 + 12, "PLr", 10.5, C["muted"], 700))
  x = 60
  for p in "abcde":
    body += _pl_badge(x, y2 + 1, p, 16)
    x += 22
  body.append(text(x + 6, y2 + 12.5, "required Performance Level of the function (WP-C-04 §2); the common block carries the highest of its rows", 10.5, C["ink"]))
  return svg(W, H, uid, "Requirement map of WP-S-02",
             "One row per safety function plus the common and security blocks; each requirement is a chip coloured by its type; "
             "dashed chips apply only to the 2.0 configuration; dotted chips carry a value to be confirmed.", body)


# ---------------------------------------------------------------- Figure 17-1 verification methods


def fig_methods(src: dict) -> str:
  W = 1040
  labelx, labelw = 24, 270
  barx, barw = labelx + labelw + 16, 640
  rowh, barh = 36, 20
  top = 72
  rows_n = len(BLOCKS)
  axis_y = top + rows_n * rowh + 6
  H = axis_y + 44
  uid = "s02-17-1"
  counts = {b: {m: sum(1 for r in _block_rows(src, b) if m in r["verif"]) for m in METHODS} for b in BLOCKS}
  maxtot = max(sum(c.values()) for c in counts.values()) or 1
  scale = barw / maxtot
  n_total = len(src["order"])
  body = [text(24, 28, f"Figure 17-1  Verification methods per block, counted from the Verif. column of {n_total} requirements", 15, C["ink"], 700),
          text(24, 46, "A requirement with two methods counts once under each; the number at the end of a bar is its block's requirement count", 11, C["muted"])]
  x = barx
  for m, (name, hue) in METHODS.items():
    body.append(rect(x, top - 20, 14, 12, hue, stroke=hue, r=3))
    body.append(text(x + 20, top - 10, f"{m} {name}", 10.5, C["ink"]))
    x += 20 + _w(f"{m} {name}", 10.5) + 22
  for i, block in enumerate(BLOCKS):
    y = top + i * rowh
    if i % 2 == 0:
      body.append(rect(16, y - 2, W - 32, rowh, C["panel"], stroke="none", r=4))
    f = src["functions"].get(f"SF-{block}", {})
    body += _row_label(labelx, y, block, _block_name(src, block), f.get("cfg2", False), labelw)
    x = barx
    for m, (name, hue) in METHODS.items():
      n = counts[block][m]
      if not n:
        continue
      w = n * scale - 2
      body.append(rect(x, y + 6, w, barh, hue, stroke="none", r=3))
      if w > 14:
        body.append(text(x + w / 2, y + 6 + barh * 0.7, str(n), 10, C["white"], 700, "middle"))
      x += n * scale
    body.append(text(x + 6, y + 6 + barh * 0.7, f"{len(_block_rows(src, block))} req.", 10.5, C["muted"]))
  body.append(f'<line x1="{barx}" y1="{axis_y}" x2="{barx + barw}" y2="{axis_y}" stroke="{C["stroke"]}" stroke-width="1"/>')
  step = 2 if maxtot <= 12 else 4
  for n in range(0, maxtot + 1, step):
    x = barx + n * scale
    body.append(f'<line x1="{x:.1f}" y1="{axis_y}" x2="{x:.1f}" y2="{axis_y + 4}" stroke="{C["line"]}" stroke-width="1"/>')
    body.append(text(x, axis_y + 16, str(n), 9.5, C["dim"], 400, "middle"))
  body.append(text(barx + barw / 2, axis_y + 32, "method coverages (requirement × method)", 10, C["dim"], 400, "middle"))
  return svg(W, H, uid, "Verification methods per block of WP-S-02",
             "Stacked horizontal bars, one per safety function and one each for the common and security blocks, showing how many "
             "requirements each verification method covers: analysis, inspection, test and demonstration.", body)


OUTPUTS = {"fig-s02-17-1-verification-methods.svg": fig_methods, "fig-s02-18-1-requirement-map.svg": fig_map}


def check_source(src: dict) -> list[str]:
  errs = []
  rows, order = src["rows"], src["order"]
  if len(order) != len(set(order)):
    errs.append("duplicate SR IDs: " + ", ".join(sorted({s for s in order if order.count(s) > 1})))
  seen_blocks = sorted({r["block"] for r in rows.values()})
  for b in seen_blocks:
    if b not in BLOCKS:
      errs.append(f"block SR-{b} is not SF-01…SF-12, common (00) or security (90)")
  for b in BLOCKS:
    br = _block_rows(src, b)
    if not br:
      errs.append(f"no requirement rows for block SR-{b}")
      continue
    if [r["n"] for r in br] != list(range(1, len(br) + 1)):
      errs.append(f"block SR-{b}: numbering is {[r['n'] for r in br]}, expected 1…{len(br)} in order")
  for sid in order:
    r = rows[sid]
    if r["ncells"] != 8:
      errs.append(f"{sid}: {r['ncells']} cells, the convention is 8")
    if r["section"] != r["block"]:
      errs.append(f"{sid} sits under the heading of SF-{r['section']}" if r["section"] else f"{sid} sits under no function heading")
    for t in r["types"]:
      if t not in TYPES:
        errs.append(f"{sid}: type {t!r} is not one of {''.join(TYPES)}")
    for v in r["verif"]:
      if v not in METHODS:
        errs.append(f"{sid}: verification {v!r} is not one of {''.join(METHODS)}")
    if not r["verif"]:
      errs.append(f"{sid}: no verification method")
    p = r["plr"][:1].lower() if r["plr"] else ""
    if p not in PL_RANK:
      errs.append(f"{sid}: PLr {r['plr']!r} is not a…e or —")
    if r["config"] not in CONFIGS:
      errs.append(f"{sid}: config {r['config']!r} is not one of {CONFIGS}")
    for h in r["trace"]:
      if h not in src["hazards"]:
        errs.append(f"{sid}: traces {h}, which is not in WP-C-03 §4")
    if not r["trace"]:
      errs.append(f"{sid}: traces no hazard")
  for sf, f in src["functions"].items():
    b = sf[3:]
    if b not in seen_blocks:
      errs.append(f"{sf} of WP-C-04 §2 has no requirements")
      continue
    got = _block_plr(src, b)
    if got != f["plr"]:
      errs.append(f"{sf}: highest row PLr is {got}, WP-C-04 §2 says {f['plr']}")
    cfgs = {r["config"] for r in _block_rows(src, b)}
    if f["cfg2"] and cfgs != {"CFG-002"}:
      errs.append(f"{sf} is CFG-002 in WP-C-04 §2 but its rows are marked {sorted(cfgs)}")
  for b in BLOCKS:
    key = BLOCK_LABEL.get(b, f"SF-{b}")
    t = src["trace"].get(key)
    if not t:
      errs.append(f"§18 has no row for {key}")
      continue
    br = _block_rows(src, b)
    want = f"SR-{b}.01…SR-{b}.{len(br):02d}"
    if t["range"] != want:
      errs.append(f"§18 {key}: requirements {t['range']!r}, the rows say {want!r}")
    if t["plr"] != _block_plr(src, b):
      errs.append(f"§18 {key}: PLr {t['plr']!r}, the rows say {_block_plr(src, b)!r}")
    if t["hazards"] != "all":
      union = sorted({h for r in br for h in r["trace"]})
      if sorted(t["hazards"]) != union:
        errs.append(f"§18 {key}: hazards {t['hazards']}, the rows trace {union}")
  for sid in src["cited"]:
    if sid not in rows:
      errs.append(f"{sid} is cited in the text but is not a requirement")
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
    print(f"fig_s02: {len(OUTPUTS)} figures current; {len(src['order'])} requirements in {len(BLOCKS)} blocks, {len(src['hazards'])} hazards checked")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
