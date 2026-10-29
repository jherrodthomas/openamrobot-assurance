"""The WP-C-03 risk sheets, drawn by fig_c03.py:

  fig-c03-5-1-ladder.svg              Figure 5-1  one line per hazard: where its rated rows land on the PL scale a…e
  fig-c03-5-2-worksheet.svg           Figure 5-2  the risk worksheet: every rated row identified, estimated, reduced in
                                                  the three steps of ISO 12100, its residual class, and what exists today
  fig-c03-a-1-barrier-board.svg       Figure A-1  the high-risk rows against the measures they rely on, by state
  fig-c03-a-NN-card.svg               Figure A-NN one hazard sheet per high-risk row
  ../WP-C-03-annex-a-high-risk-hazard-sheets.md   Annex A, the sheets with their review pictures
  ../WP-C-03-risk-register.xlsx       the worksheet as a spreadsheet, with the measures and the risk graph

Sources: WP-C-03 §4 (hazards), §5 (ratings), §6 (measures and their state), §9 (cross-references); WP-C-05 §5 (the
measures per ISO 12100 step, the residual-risk class and the verification of each rated row); the review renders of
../../sim/blender/renders/. A row is high risk when its adopted PLr is d or it is excluded at e, or, for a row with
no control function (n/a), when the risk graph gives d or e. Standard library only; output is deterministic.
"""
from __future__ import annotations

import re
import zipfile
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
C05 = HERE.parent / "WP-C-05-risk-reduction-concept.md"
ANNEX = HERE.parent / "WP-C-03-annex-a-high-risk-hazard-sheets.md"
XLSX = HERE.parent / "WP-C-03-risk-register.xlsx"
RENDERS = HERE.parent.parent / "sim" / "blender" / "renders"

STATES = ("none", "partial", "in place")
CLASS_NAME = {"S": "safeguarded at the PLr", "D": "reduced by design", "I": "carried by information for use", "E": "excluded",
              "O": "open: no adequate measure yet"}
S_WORD = {"S1": "slight, normally reversible", "S2": "serious, normally irreversible"}
F_WORD = {"F1": "seldom or short exposure", "F2": "frequent or long exposure"}
P_WORD = {"P1": "possible to avoid", "P2": "scarcely possible to avoid"}
# The review pictures of the Blender track that show a high-risk row: (hazard, start of the §5 situation) -> render
PICTURES = {("H-01", "aisle, staff crossing"): "openamrobot-m-aisle.jpg", ("H-01", "aisle, blind corner"): "openamrobot-m-corner.jpg",
            ("H-01", "dock lane"): "openamrobot-undock.jpg", ("H-01", "public floor"): "openamrobot-m-public.jpg",
            ("H-02", "uncommanded"): "openamrobot-m-uncommanded.jpg", ("H-05", "restart"): "openamrobot-m-restart.jpg",
            ("H-05", "resume"): "openamrobot-m-resume.jpg", ("H-07", "electrical fire"): "openamrobot-fire.jpg",
            ("H-10", "mode confusion"): "openamrobot-m-mode.jpg", ("H-13", "arm contact"): "openamrobot-m-station.jpg",
            ("H-13", "base moves"): "openamrobot-m-carry.jpg", ("H-14", "load drops"): "openamrobot-m-drop.jpg"}
CONDITION = r"\b(?:AOU|CA|HR)-\d\d\b"
MEASURE = r"\b(?:DM|OL|SF|IFU)-\d\d\b"


# ---------------------------------------------------------------- data

def load(text03: str, tbl, clean) -> dict:
  """Join WP-C-03 §5 with WP-C-05 §5 and the §6 states. `tbl` and `clean` are fig_c03's table reader and cleaner."""
  measures = {}
  for r in tbl(text03, "## 6. Risk evaluation and reduction"):
    name = clean(r[0])
    mid = name.split()[0]
    measures[mid] = {"id": mid, "name": name[len(mid):].strip(), "type": r[1], "reduces": re.findall(r"H-\d\d", r[2]),
                     "status": clean(r[3]), "state": clean(r[4]) if len(r) > 4 else ""}
  hazards = {r[0]: {"origin": clean(r[1]), "event": clean(r[2]), "zone": clean(r[3])} for r in tbl(text03, "## 4. Hazard identification")}
  xref = {r[0]: {"gaps": clean(r[1]), "scenarios": clean(r[2]), "requirements": clean(r[3]), "decisions": clean(r[4])}
          for r in tbl(text03, "## 9. Hazard log cross-references")}
  alloc = {}
  for r in tbl(C05.read_text(encoding="utf-8"), "## 5. Allocation table"):
    if len(r) < 7:
      continue
    alloc[clean(r[0])] = {"steps": [re.findall(MEASURE + "|" + CONDITION, r[k]) for k in (2, 3, 4)],
                          "classes": re.findall(r"\b([SDIEO])\b", re.sub(r"\*\*", "", r[5]).split(".")[0]),
                          "residual": clean(re.sub(r"^\*\*[^*]*\*\*\s*", "", r[5])), "verification": clean(r[6])}
  rows = []
  for r in tbl(text03, "## 5. Risk estimation"):
    label = clean(r[0])
    hid, _, sit = label.partition(" · ")
    adopted = clean(r[7])
    m = re.match(r"([a-e])\b", adopted.lower())
    pl = "e" if "excluded" in adopted.lower() else (m.group(1) if m else "n/a")
    a = alloc.get(label, {})
    rows.append({"label": label, "hazard": hid, "situation": sit, "zone": r[1], "S": r[2], "F": r[3], "P": r[4], "why": clean(r[5]),
                 "graph": clean(r[6]), "adopted": adopted, "pl": pl, "cfg2": "CFG-002" in sit, "steps": a.get("steps", [[], [], []]),
                 "classes": a.get("classes", []), "residual": a.get("residual", ""), "verification": a.get("verification", ""),
                 "in_c05": label in alloc})
  for r in rows:
    r["high"] = r["pl"] in ("d", "e") or (r["pl"] == "n/a" and r["graph"] in ("d", "e"))
  return {"rows": rows, "measures": measures, "hazards": hazards, "xref": xref}


def check(d: dict) -> list[str]:
  errs = []
  for m in d["measures"].values():
    if m["state"] not in STATES:
      errs.append(f"WP-C-03 §6 {m['id']}: state {m['state']!r} is not one of {', '.join(STATES)}")
  for r in d["rows"]:
    if not r["in_c05"]:
      errs.append(f"WP-C-03 §5 row {r['label']!r} has no row in WP-C-05 §5")
    for step in r["steps"]:
      for i in step:
        if re.match(MEASURE, i) and i not in d["measures"]:
          errs.append(f"{r['label']}: WP-C-05 names {i}, which WP-C-03 §6 does not register")
  for (h, start), f in PICTURES.items():
    if not any(r["hazard"] == h and r["situation"].startswith(start) and r["high"] for r in d["rows"]):
      errs.append(f"picture {f}: no high-risk row {h} · {start}…")
    if not (RENDERS / f).exists():
      errs.append(f"picture {f} is missing from sim/blender/renders/")
  return errs


def high_rows(d: dict) -> list[dict]:
  return [r for r in d["rows"] if r["high"]]


def picture(r: dict) -> str | None:
  for (h, start), f in PICTURES.items():
    if r["hazard"] == h and r["situation"].startswith(start):
      return f
  return None


def situation_short(r: dict) -> str:
  return re.sub(r"\s*\(.*$", "", r["situation"])


def card_name(i: int) -> str:
  return f"fig-c03-a-{i + 2:02d}-card.svg"


# ---------------------------------------------------------------- drawing helpers

class Pen:
  def __init__(self, f):
    self.f = f   # fig_c03 module: text, rect, wrap, svg, C, PL_FILL, PL_INK, FONT, MONO, _w

  def state_style(self, d: dict, mid: str):
    C = self.f.C
    if re.match(CONDITION, mid) or mid not in d["measures"]:
      return C["white"], C["dim"], C["muted"], "3,2"
    st = d["measures"][mid]["state"]
    return {"none": (C["red_bg"], C["red"], C["red"], ""), "partial": (C["amber_bg"], C["amber"], C["amber"], ""),
            "in place": (C["green_bg"], C["green"], C["green"], "")}[st]

  def chip(self, d, mid, x, y, label=None):
    f = self.f
    label = label or mid
    w = f._w(label, 9.5) + 12
    fill, stroke, ink, dash = self.state_style(d, mid)
    group = re.match(r"[A-Z]+", mid).group(0)
    bar = {"DM": "#5B6B9A", "OL": "#6E7F86", "SF": f.C["teal"], "IFU": "#8A6FB0"}.get(group)
    out = [f.rect(x, y, w, 18, fill, stroke, 3, 1, dash)]
    if bar:
      out.append(f'<rect x="{x + 0.5:.1f}" y="{y + 0.5:.1f}" width="3.5" height="17" rx="1.5" fill="{bar}"/>')
    out.append(f.text(x + w / 2 + (1.5 if bar else 0), y + 13, label, 9.5, ink, 600, "middle", family=f.MONO))
    return out, w

  def chips(self, d, ids, x, y, width):
    out, cx, cy = [], x, y
    for i in ids:
      w = self.f._w(i, 9.5) + 12
      if cx + w > x + width and cx > x:
        cx, cy = x, cy + 22
      o, w = self.chip(d, i, cx, cy)
      out += o
      cx += w + 4
    return out, (cy - y + 22) if ids else 22

  def pl_badge(self, pl, x, y, size=12, w=24, h=18):
    f = self.f
    key = pl if pl in f.PL_FILL else None
    fill = f.PL_FILL[key] if key else f.C["grey_bg"]
    ink = f.PL_INK[key] if key else f.C["muted"]
    label = "e" if pl == "e" else pl
    return [f.rect(x, y, w, h, fill, fill if key and key != "a" else f.C["stroke"], 4), f.text(x + w / 2, y + h / 2 + size * 0.36, label, size, ink, 700, "middle", family=f.MONO)]

  def legend(self, x, y, d):
    f = self.f
    out = [f.text(x, y + 13, "Measures:", 10, f.C["muted"], 600)]
    cx = x + 66
    for mid, label in (("DM-00", "DM design"), ("OL-00", "OL limit"), ("SF-00", "SF safety function"), ("IFU-00", "IFU information")):
      o, w = self.chip({"measures": {mid: {"state": "in place"}}}, mid, cx, y, label)
      o[0] = f.rect(cx, y, w, 18, f.C["white"], f.C["line"], 3)
      o[-1] = f.text(cx + w / 2 + 1.5, y + 13, label, 9.5, f.C["ink"], 600, "middle", family=f.MONO)
      out += o
      cx += w + 6
    out.append(f.text(cx + 8, y + 13, "State today:", 10, f.C["muted"], 600))
    cx += 88
    for st, label in (("none", "none"), ("partial", "partial"), ("in place", "in place")):
      o, w = self.chip({"measures": {"SF-00": {"state": st}}}, "SF-00", cx, y, label)
      out += o
      cx += w + 6
    o, w = self.chip(d, "AOU-00", cx + 8, y, "AOU condition")
    out += o
    return out


# ---------------------------------------------------------------- Figure 5-1 ladder

def fig_ladder(f, d: dict) -> str:
  C = f.C
  pen = Pen(f)
  by_h = {}
  for r in d["rows"]:
    by_h.setdefault(r["hazard"], []).append(r)
  x0, y0, rowh, cw = 380, 112, 30, 70
  W = x0 + 5 * (cw + 6) + 250
  H = y0 + rowh * len(by_h) + 64
  body = [f.text(32, 34, "Figure 5-1  Where each hazard's rated rows land on the Performance Level scale", 15, C["ink"], 700),
          f.text(32, 52, "One line per hazard of §4; one dot per rated row of §5 at its adopted PLr (rows with no control function at their risk-graph value, hollow).", 11, C["muted"]),
          f.text(32, 68, "The two right-hand columns say how many of the hazard's rows are high risk and how many of the measures they rely on exist today.", 11, C["muted"])]
  for k, p in enumerate("abcde"):
    x = x0 + k * (cw + 6)
    body += pen.pl_badge(p, x + cw / 2 - 14, y0 - 26, 12, 28, 20)
  body.append(f.text(x0 + 5 * (cw + 6) + 14, y0 - 12, "high-risk rows", 10, C["muted"], 600))
  body.append(f.text(x0 + 5 * (cw + 6) + 110, y0 - 12, "measures today", 10, C["muted"], 600))
  for i, (hid, rs) in enumerate(by_h.items()):
    y = y0 + i * rowh
    if i % 2 == 0:
      body.append(f.rect(28, y, W - 56, rowh, C["panel"], "none", 0, 0))
    body.append(f.text(32, y + 19, hid, 11, C["ink"], 700, family=f.MONO))
    origin = d["hazards"][hid]["origin"]
    title = origin.split(":", 1)[1].strip() if ":" in origin else origin
    title = re.sub(r"\s*\(CFG-002\)", "", title)
    lines = f.wrap(title, 300, 10.5)
    body.append(f.text(80, y + 19, lines[0] + ("…" if len(lines) > 1 else ""), 10.5, C["muted"]))
    for k, p in enumerate("abcde"):
      x = x0 + k * (cw + 6)
      here = [r for r in rs if r["pl"] == p or (r["pl"] == "n/a" and r["graph"] == p)]
      fill = f.PL_FILL[p] if here else C["white"]
      body.append(f.rect(x, y + 4, cw, rowh - 8, fill, C["stroke"] if not here or p == "a" else fill, 4))
      for j, r in enumerate(here):
        cx = x + cw / 2 + (j - (len(here) - 1) / 2) * 13
        ink = f.PL_INK[p]
        if r["pl"] == "n/a":
          body.append(f'<circle cx="{cx:.1f}" cy="{y + rowh / 2:.1f}" r="4.5" fill="none" stroke="{ink}" stroke-width="1.6"/>')
        else:
          body.append(f'<circle cx="{cx:.1f}" cy="{y + rowh / 2:.1f}" r="5" fill="{ink}"/>')
    hi = sum(r["high"] for r in rs)
    body.append(f.text(x0 + 5 * (cw + 6) + 40, y + 19, str(hi) if hi else "—", 11, C["red"] if hi else C["dim"], 700, "middle", family=f.MONO))
    ids = sorted({i for r in rs for s in r["steps"] for i in s if i in d["measures"]})
    n_none = sum(d["measures"][i]["state"] == "none" for i in ids)
    n_part = sum(d["measures"][i]["state"] == "partial" for i in ids)
    n_ok = len(ids) - n_none - n_part
    bx = x0 + 5 * (cw + 6) + 110
    seg = 84 / max(1, len(ids))
    for j, i in enumerate(sorted(ids, key=lambda i: ("none", "partial", "in place").index(d["measures"][i]["state"]))):
      _, stroke, _, _ = pen.state_style(d, i)
      body.append(f'<rect x="{bx + j * seg:.1f}" y="{y + 10}" width="{max(1.0, seg - 1.5):.1f}" height="10" rx="1.5" fill="{stroke}"/>')
    body.append(f.text(bx + 90, y + 19, f"{n_ok}/{len(ids)}", 10, C["muted"], 600, family=f.MONO))
  ly = y0 + rowh * len(by_h) + 20
  body.append(f.text(32, ly + 10, "Bar: one segment per distinct measure of WP-C-05 §5 across the hazard's rows; red none, amber partial, green in place (WP-C-03 §6 State). n/m: in place of all.", 10.5, C["muted"]))
  body.append(f.text(W - 32, H - 12, "Generated by figures/fig_c03.py from WP-C-03 §4, §5 and §6 and WP-C-05 §5", 9.5, C["dim"], anchor="end"))
  return f.svg(W, H, "lad", "Figure 5-1: where each hazard's rated rows land on the PL scale",
               "One line per hazard with five cells for the Performance Levels a to e; a dot in a cell for each rated row at that level, the cell coloured by level; at the right the number of high-risk rows and a bar of the measures the rows rely on, coloured by whether each exists today.", body)


# ---------------------------------------------------------------- Figure 5-2 worksheet

def fig_worksheet(f, d: dict) -> str:
  C = f.C
  pen = Pen(f)
  cols = [("Hazard", 96), ("Situation", 236), ("Zone", 54), ("S", 34), ("F", 34), ("P", 34), ("PLr", 52),
          ("Step 1 design", 168), ("Step 2 safeguarding", 232), ("Step 3 information", 168), ("Residual", 74), ("Today", 96)]
  xs = [28]
  for _, w in cols:
    xs.append(xs[-1] + w)
  W = xs[-1] + 28
  top = 150
  layout = []
  for r in d["rows"]:
    lines = f.wrap(r["situation"], cols[1][1] - 12, 10.5)
    hs = [pen.chips(d, s, 0, 0, cols[7 + k][1] - 12)[1] for k, s in enumerate(r["steps"])]
    layout.append((r, lines, max(len(lines) * 14 + 12, max(hs) + 10, 34)))
  H = top + sum(h for *_, h in layout) + 96
  band = [("Identify", 0, 3), ("Estimate", 3, 7), ("Reduce: the three steps of ISO 12100 §6 (WP-C-05 §5)", 7, 10), ("After", 10, 12)]
  body = [f.text(32, 34, "Figure 5-2  The risk worksheet: every rated row from hazard to residual, and what exists today", 15, C["ink"], 700),
          f.text(32, 52, "Identification and estimation from §4 and §5, the measures of each ISO 12100 step and the residual class from WP-C-05 §5; each measure coloured by its §6 state on any build today.", 11, C["muted"])]
  body += pen.legend(32, 66, d)
  for name, a, b in band:
    body.append(f.rect(xs[a] + 1, top - 52, xs[b] - xs[a] - 2, 22, C["ink"], C["ink"], 3))
    body.append(f.text(xs[a] + 8, top - 37, name, 10, C["white"], 700))
  for k, (name, w) in enumerate(cols):
    anchor = "middle" if name in ("S", "F", "P", "PLr", "Residual") else "start"
    x = xs[k] + w / 2 if anchor == "middle" else xs[k] + 6
    body.append(f.text(x, top - 12, name.upper(), 9.5, C["muted"], 700, anchor))
  body.append(f'<line x1="28" y1="{top - 4}" x2="{xs[-1]}" y2="{top - 4}" stroke="{C["ink"]}" stroke-width="1.5"/>')
  y = top
  prev = None
  for r, lines, h in layout:
    first = r["hazard"] != prev
    if first and prev is not None:
      body.append(f'<line x1="28" y1="{y:.1f}" x2="{xs[-1]}" y2="{y:.1f}" stroke="{C["line"]}" stroke-width="1"/>')
    elif prev is not None:
      body.append(f'<line x1="{xs[1]}" y1="{y:.1f}" x2="{xs[-1]}" y2="{y:.1f}" stroke="{C["stroke"]}" stroke-width="0.8"/>')
    if r["high"]:
      body.append(f'<rect x="{xs[1]}" y="{y:.1f}" width="3" height="{h:.1f}" fill="{C["red"]}"/>')
    if first:
      body.append(f.text(xs[0] + 6, y + 17, r["hazard"], 11, C["ink"], 700, family=f.MONO))
      origin = d["hazards"][r["hazard"]]["origin"].split(":")[0].replace("Cybersecurity-induced", "Cyber-induced")
      room = max(1, int((h - 22) // 12))
      lines_o = f.wrap(origin.replace(" / ", "/"), cols[0][1] - 12, 9)
      for j, ln in enumerate(lines_o[:room]):
        body.append(f.text(xs[0] + 6, y + 31 + j * 12, ln + ("…" if j == room - 1 and len(lines_o) > room else ""), 9, C["muted"]))
    prev = r["hazard"]
    for j, ln in enumerate(lines):
      body.append(f.text(xs[1] + 8, y + 17 + j * 14, ln, 10.5, C["ink"]))
    body.append(f.text(xs[2] + 6, y + 17, r["zone"], 10, C["ink"], 400, family=f.MONO))
    for k, key in ((3, "S"), (4, "F"), (5, "P")):
      hi = r[key].endswith("2")
      body.append(f.rect(xs[k] + 3, y + 4, cols[k][1] - 6, h - 8, C["red_bg"] if hi else C["grey_bg"], "none", 3, 0))
      body.append(f.text(xs[k] + cols[k][1] / 2, y + 17, r[key], 10.5, C["ink"], 700, "middle", family=f.MONO))
    body += pen.pl_badge(r["pl"], xs[6] + 8, y + 5, 11, 36, 18)
    for k in range(3):
      ids = r["steps"][k]
      if ids:
        o, _ = pen.chips(d, ids, xs[7 + k] + 6, y + 5, cols[7 + k][1] - 12)
        body += o
      else:
        body.append(f.text(xs[7 + k] + 8, y + 18, "—", 10.5, C["dim"]))
    cls = r["classes"] or ["?"]
    for j, c in enumerate(cls[:2]):
      fill = {"S": C["teal"], "D": C["green"], "I": C["amber"], "E": C["dim"], "O": C["red"]}.get(c, C["dim"])
      cx = xs[10] + cols[10][1] / 2 + (j - (len(cls[:2]) - 1) / 2) * 24
      body.append(f'<circle cx="{cx:.1f}" cy="{y + 14}" r="10" fill="{fill}"/>')
      body.append(f.text(cx, y + 18, c, 10.5, C["white"], 700, "middle", family=f.MONO))
    ids = [i for s in r["steps"] for i in s if i in d["measures"]]
    seg = (cols[11][1] - 16) / max(1, len(ids))
    order = sorted(ids, key=lambda i: STATES.index(d["measures"][i]["state"]))
    for j, i in enumerate(order):
      _, stroke, _, _ = pen.state_style(d, i)
      body.append(f'<rect x="{xs[11] + 8 + j * seg:.1f}" y="{y + 8}" width="{max(1.0, seg - 1.5):.1f}" height="8" rx="1.5" fill="{stroke}"/>')
    n_ok = sum(d["measures"][i]["state"] == "in place" for i in ids)
    body.append(f.text(xs[11] + 8, y + 30, f"{n_ok} of {len(ids)} in place" if ids else "no measure", 9.5, C["muted"]))
    y += h
  body.append(f'<line x1="28" y1="{y:.1f}" x2="{xs[-1]}" y2="{y:.1f}" stroke="{C["ink"]}" stroke-width="1.5"/>')
  ly = y + 20
  notes = ["Residual (WP-C-05 §1.1): S safeguarded at the PLr, D reduced by design, I carried by information for use, E excluded, O open.",
           "A red edge on the situation marks a high-risk row (PLr d or e, or d on the graph with no control function); Annex A has one sheet per such row.",
           "S, F, P: tinted at the higher class (S2, F2, P2). The rationale of each rating is the §5 table; the residual text and the verification are WP-C-05 §5 and WP-C-03-risk-register.xlsx."]
  for j, ln in enumerate(notes):
    body.append(f.text(32, ly + 10 + j * 16, ln, 10.5, C["muted"]))
  body.append(f.text(W - 32, H - 12, "Generated by figures/fig_c03.py from WP-C-03 §4, §5 and §6 and WP-C-05 §5", 9.5, C["dim"], anchor="end"))
  return f.svg(W, H, "ws", "Figure 5-2: the risk worksheet",
               "A worksheet with one line per rated row of the risk assessment, grouped by hazard: the situation and zone, the S, F and P ratings with the higher class tinted, the required Performance Level in a coloured chip, the measures of the three ISO 12100 steps as chips coloured by whether each exists today, the residual-risk class as a lettered dot, and a bar of how many of the row's measures are in place.", body)


# ---------------------------------------------------------------- Figure A-1 barrier board

def fig_board(f, d: dict) -> str:
  C = f.C
  pen = Pen(f)
  rows = high_rows(d)
  ids = sorted({i for r in rows for s in r["steps"] for i in s if i in d["measures"]},
               key=lambda i: (["DM", "OL", "SF", "IFU"].index(re.match(r"[A-Z]+", i).group(0)), i))
  x0, y0, rowh, cw = 360, 150, 28, 30
  W = x0 + cw * len(ids) + 120
  H = y0 + rowh * len(rows) + 110
  body = [f.text(32, 34, "Figure A-1  The high-risk rows against the measures they rely on, by what exists today", 15, C["ink"], 700),
          f.text(32, 52, "One line per high-risk row of WP-C-03 §5; one column per measure WP-C-05 §5 allocates to any of them. A filled cell is a measure the row relies on, coloured by its §6 state.", 11, C["muted"]),
          f.text(32, 68, "The count under each column is how many high-risk rows wait on that measure: the columns with the highest counts are the first to build.", 11, C["muted"])]
  gx = x0
  for g in ("DM", "OL", "SF", "IFU"):
    n = sum(1 for i in ids if i.startswith(g + "-"))
    if n:
      body.append(f.rect(gx + 1, y0 - 72, n * cw - 2, 18, {"SF": C["teal_bg"], "OL": C["amber_bg"]}.get(g, C["grey_bg"]), C["stroke"], 3))
      body.append(f.text(gx + n * cw / 2, y0 - 59, g, 9.5, C["ink"], 700, "middle", family=f.MONO))
      gx += n * cw
  for k, i in enumerate(ids):
    ax = x0 + k * cw + cw / 2 + 4
    body.append(f.text(ax, y0 - 8, i, 9.5, C["ink"], 600, "start", family=f.MONO, extra=f' transform="rotate(-60 {ax:.1f} {y0 - 8})"'))
  for j, r in enumerate(rows):
    y = y0 + j * rowh
    if j % 2 == 0:
      body.append(f.rect(28, y, W - 56, rowh, C["panel"], "none", 0, 0))
    body += pen.pl_badge(r["pl"], 32, y + 5, 11, 30, 18)
    body.append(f.text(70, y + 18, r["hazard"], 10.5, C["ink"], 700, family=f.MONO))
    s = situation_short(r)
    lines = f.wrap(s, x0 - 130, 10)
    body.append(f.text(116, y + 18, lines[0] + ("…" if len(lines) > 1 else ""), 10, C["muted"]))
    mine = {i for st in r["steps"] for i in st}
    for k, i in enumerate(ids):
      x = x0 + k * cw
      body.append(f.rect(x + 2, y + 3, cw - 4, rowh - 6, C["white"], C["stroke"], 2))
      if i in mine:
        _, stroke, _, _ = pen.state_style(d, i)
        body.append(f.rect(x + 2, y + 3, cw - 4, rowh - 6, stroke, stroke, 2))
  yb = y0 + rowh * len(rows) + 6
  for k, i in enumerate(ids):
    n = sum(i in {x for st in r["steps"] for x in st} for r in rows)
    body.append(f.text(x0 + k * cw + cw / 2, yb + 14, str(n), 10.5, C["ink"], 700, "middle", family=f.MONO))
  body.append(f.text(x0 - 10, yb + 14, "rows waiting", 10, C["muted"], 600, "end"))
  ly = yb + 36
  body.append(f.rect(32, ly, 14, 12, C["red"], C["red"], 2))
  body.append(f.text(52, ly + 10, "none", 10.5, C["muted"]))
  body.append(f.rect(100, ly, 14, 12, C["amber"], C["amber"], 2))
  body.append(f.text(120, ly + 10, "partial", 10.5, C["muted"]))
  body.append(f.rect(180, ly, 14, 12, C["green"], C["green"], 2))
  body.append(f.text(200, ly + 10, "in place (no measure yet)", 10.5, C["muted"]))
  body.append(f.text(W - 32, H - 12, "Generated by figures/fig_c03.py from WP-C-03 §5 and §6 and WP-C-05 §5", 9.5, C["dim"], anchor="end"))
  return f.svg(W, H, "bb", "Figure A-1: the high-risk rows against the measures they rely on",
               "A grid with the high-risk rows of the risk assessment down the side and the measures they rely on across, grouped as design, limits, safety functions and information for use; a cell is filled where the row relies on the measure, red where nothing exists today and amber where something partial exists; under each column the number of high-risk rows waiting on it.", body)


# ---------------------------------------------------------------- Figure A-n hazard sheet

def fig_card(f, d: dict, r: dict, n: int) -> str:
  C = f.C
  pen = Pen(f)
  W = 940
  hz = d["hazards"][r["hazard"]]
  title = f"{r['hazard']} · {situation_short(r)}"
  event = hz["event"]
  ev = f.wrap(event, W - 160, 11)
  why = f.wrap(r["why"], 300, 10.5)
  res = f.wrap(r["residual"], 520, 10.5)
  ver = f.wrap("Verification: " + r["verification"], 520, 10)
  # left column: ratings; right column: steps, residual
  step_h = []
  for k in range(3):
    step_h.append(pen.chips(d, r["steps"][k], 0, 0, 400)[1])
  right_h = 30 + sum(h + 30 for h in step_h) + 30 + 16 * len(res) + 14 * len(ver) + 20
  left_h = 36 + 3 * 44 + 40 + 15 * len(why) + 20
  top = 92 + 15 * len(ev)
  H = top + max(left_h, right_h) + 60
  body = [f.rect(0, 0, W, 6, f.PL_FILL.get(r["pl"], C["grey_bg"]), "none", 0, 0)]
  body.append(f.text(32, 36, f"Figure A-{n}", 11, C["muted"], 600, family=f.MONO))
  body.append(f.text(32, 60, title, 17, C["ink"], 700))
  body.append(f.text(32, 78, hz["origin"] + f"  ·  zone {r['zone']}" + ("  ·  CFG-002" if r["cfg2"] else ""), 10.5, C["muted"]))
  bx = W - 112
  body += pen.pl_badge(r["pl"], bx, 22, 24, 80, 46)
  body.append(f.text(bx + 40, 82, "excluded" if r["pl"] == "e" else ("no control fn" if r["pl"] == "n/a" else "required PL"), 10, C["muted"], 600, "middle"))
  for j, ln in enumerate(ev):
    body.append(f.text(32, 100 + j * 15, ln, 11, C["ink"]))
  y = top + 10
  body.append(f'<line x1="32" y1="{y - 4}" x2="{W - 32}" y2="{y - 4}" stroke="{C["stroke"]}"/>')
  # ratings
  body.append(f.text(32, y + 16, "WHY THIS RATING", 9.5, C["muted"], 700))
  for k, key in enumerate(("S", "F", "P")):
    yy = y + 28 + k * 44
    word = {"S": S_WORD, "F": F_WORD, "P": P_WORD}[key][r[key]]
    hi = r[key].endswith("2")
    body.append(f.rect(32, yy, 48, 36, C["red_bg"] if hi else C["grey_bg"], "none", 4, 0))
    body.append(f.text(56, yy + 23, r[key], 14, C["ink"], 700, "middle", family=f.MONO))
    body.append(f.text(90, yy + 22, word, 11.5, C["ink"]))
  yy = y + 28 + 3 * 44
  body.append(f.text(32, yy + 16, f"→ risk graph {r['graph']}  ·  adopted {r['adopted']}", 11, C["ink"], 700))
  for j, ln in enumerate(why):
    body.append(f.text(32, yy + 38 + j * 15, ln, 10.5, C["muted"]))
  # steps
  rx = 370
  body.append(f.text(rx, y + 16, "WHAT REDUCES IT, AND WHAT EXISTS TODAY", 9.5, C["muted"], 700))
  yy = y + 30
  for k, name in enumerate(("Step 1  inherently safe design", "Step 2  safeguarding", "Step 3  information for use")):
    body.append(f.text(rx, yy + 12, name, 10.5, C["ink"], 600))
    ids = r["steps"][k]
    if ids:
      o, hgt = pen.chips(d, ids, rx, yy + 18, W - rx - 32)
      body += o
    else:
      body.append(f.text(rx, yy + 32, "—", 10.5, C["dim"]))
      hgt = 22
    yy += 30 + hgt
  ids = [i for s in r["steps"] for i in s if i in d["measures"]]
  counts = {st: sum(d["measures"][i]["state"] == st for i in ids) for st in STATES}
  body.append(f.text(rx, yy + 12, f"Today: {counts['in place']} of {len(ids)} measures in place, {counts['partial']} partial, {counts['none']} with nothing on any build.", 10.5, C["red"] if counts["none"] else C["ink"], 600))
  yy += 30
  cls = r["classes"]
  label = ", then ".join(f"{c} {CLASS_NAME[c]}" for c in cls if c in CLASS_NAME) or "not classed"
  body.append(f.text(rx, yy, "AFTER THE MEASURES (WP-C-05): " + label.upper(), 9.5, C["muted"], 700))
  for j, ln in enumerate(res):
    body.append(f.text(rx, yy + 18 + j * 16, ln, 10.5, C["ink"]))
  yy += 18 + 16 * len(res)
  for j, ln in enumerate(ver):
    body.append(f.text(rx, yy + 4 + j * 14, ln, 10, C["muted"]))
  # footer: cross-references
  x = d["xref"].get(r["hazard"], {})
  fy = H - 36
  body.append(f'<line x1="32" y1="{fy - 14}" x2="{W - 32}" y2="{fy - 14}" stroke="{C["stroke"]}"/>')
  foot = f"Gaps {x.get('gaps', '—')}   ·   scenarios {x.get('scenarios', '—')}"
  fl = f.wrap(foot, W - 64, 9.5)
  for j, ln in enumerate(fl[:2]):
    body.append(f.text(32, fy + j * 13, ln, 9.5, C["muted"], 400, family=f.MONO))
  body.append(f.text(W - 32, H - 8, "Generated by figures/fig_c03.py from WP-C-03 §4, §5, §6, §9 and WP-C-05 §5", 9, C["dim"], anchor="end"))
  return f.svg(W, H, f"hc{n}", f"Figure A-{n}: hazard sheet {title}",
               f"The hazard sheet of {title}: the hazardous event, the S, F and P ratings in words with the required Performance Level {r['pl']}, the measures of the three ISO 12100 steps coloured by whether each exists today, the residual-risk class and its text, and the gap and scenario references.", body)


# ---------------------------------------------------------------- Annex A

def annex(f, d: dict, version: str) -> str:
  rows = high_rows(d)
  with_pic = sum(1 for r in rows if picture(r))
  L = ["# WP-C-03 Annex A High-Risk Hazard Sheets", "",
       "<!-- Generated by assurance/02-concept/figures/fig_c03.py from WP-C-03, WP-C-05 and the review renders; do not edit by hand. -->", "",
       "| Field | Value |", "|---|---|",
       "| Work product | Annex A of [WP-C-03](WP-C-03-risk-assessment.md) Risk assessment; not a separate work product |",
       f"| Version | Follows WP-C-03 {version}: generated from its tables at every change |",
       "| Status | Draft, as WP-C-03 |",
       "| Content | One sheet per high-risk row of WP-C-03 §5: adopted PLr d, or e and excluded, or d on the risk graph with no control function |", "",
       "> [!NOTE]",
       "> A view of the record, not a second record. Every value comes from WP-C-03 §4, §5, §6 and §9 and WP-C-05 §5;",
       "> change it there and run `figures/fig_c03.py`. The pictures are review renders of the simulation track: synthetic,",
       "> pictures only, no evidence credit. A picture shows the situation; the sheet under it says what would stop it and",
       "> what exists today.", "",
       f"{len(rows)} rows are high risk; {with_pic} of them have a review picture.", "",
       "## A.1 What to build first", "",
       "![Figure A-1: the high-risk rows against the measures they rely on, by what exists today: a grid with the rows down the side and the measures across, filled where a row relies on a measure, red where nothing exists, amber where something partial does, with the number of rows waiting on each measure under its column](figures/fig-c03-a-1-barrier-board.svg)", "",
       "*Figure A-1.* Every high-risk row waits on at least one measure with nothing on any build; the column counts rank the measures by how many of these rows they unblock.", "",
       "## A.2 The sheets", ""]
  for i, r in enumerate(rows):
    n = i + 2
    L += [f"### A.2.{i + 1} {r['hazard']} · {situation_short(r)}", ""]
    p = picture(r)
    if p:
      L += [f"![Review picture for {r['hazard']}, {situation_short(r)}: synthetic render, no evidence credit](../sim/blender/renders/{p})", "",
            f"*Review picture* `{p}`: synthetic, no evidence credit ([the render set](../sim/blender/README.md#1-the-renders)).", ""]
    else:
      L += ["*Review picture: not drawn yet.*", ""]
    L += [f"![Figure A-{n}: hazard sheet for {r['hazard']}, {situation_short(r)}: the event, the S, F and P ratings in words and the required PL {r['pl']}, the measures of the three steps coloured by whether each exists today, the residual class and the references](figures/{card_name(i)})", ""]
  L += ["## A.3 How the sheets are made", "",
        "`figures/fig_c03.py` selects the high-risk rows of WP-C-03 §5 and draws one sheet each from §4 (the event), §5 (the",
        "ratings and their rationale), §6 (the state of each measure), §9 (gaps and scenarios) and WP-C-05 §5 (the measures",
        "per step, the residual class, the verification). CI fails if a sheet is stale, if a §5 row has no WP-C-05 row, if",
        "WP-C-05 names a measure §6 does not register or if a measure has no state.", ""]
  return "\n".join(L)


# ---------------------------------------------------------------- the spreadsheet (SpreadsheetML written with the standard library)

def _col(n: int) -> str:
  s = ""
  n += 1
  while n:
    n, r = divmod(n - 1, 26)
    s = chr(65 + r) + s
  return s


FILLS = ["F4F7F8", "122026", "EAF6F5", "C9ECE8", "8FD3CC", "2FA69C", "D64535", "FDEDEB", "EDF2F4", "FFF6E8", "E8F6EC"]
# style ids: 0 normal wrap, 1 header, 2..6 PL a..e, 7 high tint, 8 low tint, 9 state none, 10 state partial, 11 state in place, 12 bold id, 13 title
_STYLE = {"normal": 0, "head": 1, "a": 2, "b": 3, "c": 4, "d": 5, "e": 6, "hi": 7, "lo": 8, "none": 9, "partial": 10, "in place": 11, "id": 12, "title": 13}


def _styles_xml() -> str:
  fills = '<fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>' + "".join(
    f'<fill><patternFill patternType="solid"><fgColor rgb="FF{c}"/><bgColor indexed="64"/></patternFill></fill>' for c in FILLS)
  fonts = ('<font><sz val="10"/><name val="Calibri"/></font><font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>'
           '<font><b/><sz val="10"/><name val="Calibri"/></font><font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>'
           '<font><b/><sz val="10"/><color rgb="FFD64535"/><name val="Calibri"/></font><font><b/><sz val="10"/><color rgb="FFB86F0C"/><name val="Calibri"/></font>'
           '<font><b/><sz val="10"/><color rgb="FF2C9A58"/><name val="Calibri"/></font><font><b/><sz val="14"/><name val="Calibri"/></font>')
  border = '<border><left style="thin"><color rgb="FFD3DDE2"/></left><right style="thin"><color rgb="FFD3DDE2"/></right><top style="thin"><color rgb="FFD3DDE2"/></top><bottom style="thin"><color rgb="FFD3DDE2"/></bottom><diagonal/></border>'
  def xf(font, fill, center=False):
    al = '<alignment wrapText="1" vertical="top"' + (' horizontal="center"' if center else "") + "/>"
    return f'<xf numFmtId="0" fontId="{font}" fillId="{fill}" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">{al}</xf>'
  title = '<xf numFmtId="0" fontId="7" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment vertical="center"/></xf>'
  xfs = [xf(0, 0), xf(1, 3), xf(2, 4, True), xf(2, 5, True), xf(2, 6, True), xf(3, 7, True), xf(3, 8, True), xf(2, 9, True), xf(0, 10, True),
         xf(4, 9, True), xf(5, 11, True), xf(6, 12, True), xf(2, 0), title]
  return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
          f'<fonts count="8">{fonts}</fonts><fills count="{len(FILLS) + 2}">{fills}</fills>'
          f'<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border>{border}</borders>'
          '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
          f'<cellXfs count="{len(xfs)}">{"".join(xfs)}</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')


def _sheet_xml(rows: list[list[tuple[str, str]]], widths: list[float], freeze: tuple[int, int] | None, filter_row: int | None, heights: dict[int, float]) -> str:
  cols = "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths))
  pane = ""
  if freeze:
    r, c = freeze
    pane = (f'<pane xSplit="{c}" ySplit="{r}" topLeftCell="{_col(c)}{r + 1}" activePane="bottomRight" state="frozen"/>'
            f'<selection pane="bottomRight" activeCell="{_col(c)}{r + 1}" sqref="{_col(c)}{r + 1}"/>')
  data = []
  for i, row in enumerate(rows):
    if i not in heights and len(row) > 1:
      lines = max(-(-len(v) // max(1, int(widths[j] * 1.15))) for j, (v, _) in enumerate(row))
      heights = {**heights, i: round(max(15, lines * 13.2 + 4), 1)}
    ht = f' ht="{heights[i]}" customHeight="1"' if i in heights else ""
    cells = "".join(f'<c r="{_col(j)}{i + 1}" s="{_STYLE[st]}" t="inlineStr"><is><t xml:space="preserve">{escape(v)}</t></is></c>' for j, (v, st) in enumerate(row))
    data.append(f'<row r="{i + 1}"{ht}>{cells}</row>')
  af = f'<autoFilter ref="A{filter_row}:{_col(max(len(r) for r in rows) - 1)}{len(rows)}"/>' if filter_row else ""
  return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
          '<sheetPr><pageSetUpPr fitToPage="1"/></sheetPr>'
          f'<sheetViews><sheetView workbookViewId="0">{pane}</sheetView></sheetViews><sheetFormatPr defaultRowHeight="15"/><cols>{cols}</cols>'
          f'<sheetData>{"".join(data)}</sheetData>{af}<pageMargins left="0.4" right="0.4" top="0.5" bottom="0.5" header="0.3" footer="0.3"/>'
          '<pageSetup paperSize="9" orientation="landscape" fitToWidth="1" fitToHeight="0"/></worksheet>')


def xlsx(f, d: dict, version: str) -> bytes:
  H = lambda s: (s, "head")
  reg = [[(f"WP-C-03 risk register, {version}: generated from WP-C-03 §4–§6 and WP-C-05 §5 by figures/fig_c03.py; do not edit (change the documents)", "title")],
         [H(h) for h in ("Hazard", "Hazard origin", "Hazardous event", "Situation", "Zone", "Config", "S", "F", "P", "Rationale", "Risk graph", "PLr adopted",
                         "High risk", "Step 1 design", "Step 2 safeguarding", "Step 3 information", "Measures in place", "Residual class", "Residual risk", "Verification")]]
  for r in d["rows"]:
    hz = d["hazards"][r["hazard"]]
    ids = [i for s in r["steps"] for i in s if i in d["measures"]]
    n_ok = sum(d["measures"][i]["state"] == "in place" for i in ids)
    plstyle = r["pl"] if r["pl"] in "abcde" else "lo"
    reg.append([(r["hazard"], "id"), (hz["origin"], "normal"), (hz["event"], "normal"), (r["situation"], "normal"), (r["zone"], "normal"),
                ("CFG-002" if r["cfg2"] else "CFG-001", "normal"), (r["S"], "hi" if r["S"] == "S2" else "lo"), (r["F"], "hi" if r["F"] == "F2" else "lo"),
                (r["P"], "hi" if r["P"] == "P2" else "lo"), (r["why"], "normal"), (r["graph"], r["graph"] if r["graph"] in "abcde" else "lo"),
                (r["adopted"], plstyle), ("yes" if r["high"] else "no", "hi" if r["high"] else "lo"),
                (", ".join(r["steps"][0]) or "—", "normal"), (", ".join(r["steps"][1]) or "—", "normal"), (", ".join(r["steps"][2]) or "—", "normal"),
                (f"{n_ok} of {len(ids)}", "none" if ids and n_ok == 0 else "lo"), (", then ".join(r["classes"]), "id"), (r["residual"], "normal"),
                (r["verification"], "normal")])
  mea = [[(f"WP-C-03 §6 measure register, {version}", "title")], [H(h) for h in ("Measure", "Name", "Type", "Reduces", "Status today", "State")]]
  for m in d["measures"].values():
    mea.append([(m["id"], "id"), (m["name"], "normal"), (m["type"], "normal"), (", ".join(m["reduces"]), "normal"), (m["status"], "normal"), (m["state"], m["state"])])
  grf = [[("ISO 13849-1 risk graph as used in WP-C-03 §2.2 (to be checked against a licensed copy)", "title")], [H("S"), H("F"), H("P"), H("PLr")]]
  for (s, fq, p), pl in sorted(f.load_source()["graph"].items()):
    grf.append([(s, "lo"), (fq, "lo"), (p, "lo"), (pl, pl)])
  sheets = [("Register", _sheet_xml(reg, [8, 22, 40, 34, 7, 9, 5, 5, 5, 46, 7, 16, 7, 18, 24, 18, 10, 9, 52, 30], (2, 1), 2, {0: 22})),
            ("Measures", _sheet_xml(mea, [8, 46, 26, 22, 46, 10], (2, 1), 2, {0: 22})),
            ("Risk graph", _sheet_xml(grf, [8, 8, 8, 8], (2, 0), None, {0: 22}))]
  files = {
    "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
      '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
      '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
      + "".join(f'<Override PartName="/xl/worksheets/sheet{i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(len(sheets)))
      + "</Types>",
    "_rels/.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
      '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
    "xl/workbook.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
      + "".join(f'<sheet name="{n}" sheetId="{i + 1}" r:id="rId{i + 1}"/>' for i, (n, _) in enumerate(sheets))
      + '</sheets><definedNames>' + "".join(f'<definedName name="_xlnm._FilterDatabase" localSheetId="{i}" hidden="1">\'{n}\'!$A$2:${_col(19 if i == 0 else 5)}${len(reg if i == 0 else mea)}</definedName>' for i, (n, _) in enumerate(sheets[:2]))
      + "</definedNames></workbook>",
    "xl/_rels/workbook.xml.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
      + "".join(f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i + 1}.xml"/>' for i in range(len(sheets)))
      + f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>',
    "xl/styles.xml": _styles_xml(),
  }
  for i, (_, x) in enumerate(sheets):
    files[f"xl/worksheets/sheet{i + 1}.xml"] = x
  buf = BytesIO()
  with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for name, content in files.items():
      info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
      info.compress_type = zipfile.ZIP_DEFLATED
      info.external_attr = 0o644 << 16
      z.writestr(info, content.encode("utf-8"))
  return buf.getvalue()
