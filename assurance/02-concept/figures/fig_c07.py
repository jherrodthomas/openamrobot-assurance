#!/usr/bin/env python3
"""Draw the WP-C-07 cybersecurity figures and check the threat and risk assessment.

  fig-c07-4-1-zones-conduits.svg   Figure 4-1  the security zones SZ-n and the conduits CD-n between them
  fig-c07-6-1-risk-matrix.svg      Figure 6-1  every threat scenario on a likelihood x impact matrix, before and after treatment

The source of record is ../WP-C-07-cybersecurity-threat-and-risk-assessment.md (§1.2 actors, §3 assets, §4 zones and
conduits, §5 scenarios, §6 risk, §7 security level check, §8 residual risk, §9 hazards). The check also reads the hazard
list of ../WP-C-03-risk-assessment.md §4 and, from ../WP-C-08-cybersecurity-requirements-and-sl-target.md, the security
level target of §2 and the requirement IDs of §4. `--check` fails when an SVG is stale, or when:

  - a scenario names an actor, conduit, asset or hazard that does not exist;
  - §6 is not one row per §5 scenario in the same order, a risk is not likelihood x impact with the right band, the impact
    with the safety architecture exceeds the impact before treatment, or "SL needed" is not the actor's level;
  - a treatment names a requirement WP-C-08 §4 does not have, or a scenario has no treatment without being in §7;
  - §7 does not list exactly the (scenario, FR) pairs whose target in WP-C-08 §2 is below the level the scenario needs;
  - §8 does not list exactly the scenarios whose residual is medium or high;
  - §9 is not the inverse of the hazard column of §5;
  - a conduit enters the safety chain SZ-4 other than for commissioning, or leaves it other than one way;
  - the interface anchor of IX-01 is missing.

    python3 fig_c07.py            # regenerate
    python3 fig_c07.py --check    # fail if the source changed or an SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "WP-C-07-cybersecurity-threat-and-risk-assessment.md"
WP_C03 = HERE.parent / "WP-C-03-risk-assessment.md"
WP_C08 = HERE.parent / "WP-C-08-cybersecurity-requirements-and-sl-target.md"
ANCHOR = "Safety impact is anchored to the hazard list of WP-C-03"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "stroke": "#D3DDE2", "line": "#7E949B", "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#B86F0C", "amber_bg": "#FFF1DC", "teal": "#00938B", "teal_bg": "#E9F7F5", "red": "#D64535", "red_bg": "#FBE3E0",
  "green": "#2C9A58", "green_bg": "#E3F4E8", "grey_bg": "#EDF2F4", "white": "#FFFFFF", "blue": "#2F6FD6", "blue_bg": "#EAF1FC",
}
BANDS = {"low": (1, 3), "medium": (4, 8), "high": (9, 16)}
BAND_FILL = {"low": C["green_bg"], "medium": C["amber_bg"], "high": C["red_bg"]}
BAND_INK = {"low": C["green"], "medium": C["amber"], "high": C["red"]}
L_NAMES = {4: "almost certain", 3: "likely", 2: "possible", 1: "unlikely"}
I_NAMES = {1: "minor", 2: "moderate", 3: "major", 4: "severe"}
ZONE_STYLE = {
  "SZ-1": (C["dim"], C["grey_bg"]), "SZ-2": (C["blue"], C["blue_bg"]), "SZ-3": (C["amber"], C["amber_bg"]),
  "SZ-4": (C["red"], C["red_bg"]), "SZ-5": (C["muted"], C["panel"]),
}


def band(r: int) -> str:
  for name, (lo, hi) in BANDS.items():
    if lo <= r <= hi:
      return name
  return "?"


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
  return re.sub(r"\*\*|`", "", cell).strip()


def _ids(cell: str, prefix: str) -> list[str]:
  return re.findall(rf"\b{prefix}-\d\d?\b", cell)


def _frs(cell: str) -> list[str]:
  return [f"FR {n}" for n in re.findall(r"FR (\d)", cell)]


def _score(cell: str) -> tuple[int | None, str]:
  m = re.match(r"(\d+) (low|medium|high)$", _clean(cell))
  return (int(m.group(1)), m.group(2)) if m else (None, _clean(cell))


def _int(cell: str) -> int | None:
  c = _clean(cell)
  return int(c) if c.isdigit() else None


def load_source() -> dict:
  text = SOURCE.read_text(encoding="utf-8")
  actors = {r[0]: {"who": _clean(r[1]), "sl": _int(r[3])} for r in _table(text, "### 1.2 Threat actors") if r[0].startswith("TA-")}
  assets = {r[0]: {"name": _clean(r[1]), "config": r[2]} for r in _table(text, "## 3. Assets") if r[0].startswith("A-")}
  zones = {r[0]: {"name": _clean(r[1]), "contains": _clean(r[2]), "assets": _ids(r[3], "A"), "trust": _clean(r[4])}
           for r in _table(text, "### 4.1 Zones") if r[0].startswith("SZ-")}
  conduits = {r[0]: {"from": r[1], "to": r[2], "carries": _clean(r[3]), "interfaces": _ids(r[4], "IF"), "today": _clean(r[5])}
              for r in _table(text, "### 4.2 Conduits") if r[0].startswith("CD-")}
  scenarios = []
  for r in _table(text, "## 5. Threat scenarios"):
    if not r[0].startswith("TS-"):
      continue
    scenarios.append({"id": r[0], "ncells": len(r), "text": _clean(r[1]), "actors": _ids(r[2], "TA"), "conduits": _ids(r[3], "CD") if len(r) > 3 else [],
                      "conduit_cell": _clean(r[3]) if len(r) > 3 else "", "assets": _ids(r[4], "A") if len(r) > 4 else [],
                      "hazards": _ids(r[6], "H") if len(r) > 6 else [], "hazard_cell": _clean(r[6]) if len(r) > 6 else "",
                      "config": _clean(r[7]) if len(r) > 7 else ""})
  risk = []
  for r in _table(text, "## 6. Risk assessment"):
    if not r[0].startswith("TS-"):
      continue
    before = _score(r[3]) if len(r) > 3 else (None, "")
    after = _score(r[9]) if len(r) > 9 else (None, "")
    risk.append({"id": r[0], "ncells": len(r), "l": _int(r[1]), "i": _int(r[2]), "before": before, "i_arch": _int(r[4]) if len(r) > 4 else None,
                 "frs": _frs(r[5]) if len(r) > 5 else [], "sl_needed": _int(r[6]) if len(r) > 6 else None,
                 "treatment": _ids(r[7], "CSR") if len(r) > 7 else [], "treatment_cell": _clean(r[7]) if len(r) > 7 else "",
                 "l_after": _int(r[8]) if len(r) > 8 else None, "after": after})
  slcheck = [{"id": r[0], "fr": _frs(r[1])[0] if _frs(r[1]) else "", "slt": _int(r[2]), "need": _int(r[3]), "disposition": _clean(r[4])}
             for r in _table(text, "## 7. Security level check") if r[0].startswith("TS-")]
  residual = [{"id": r[0], "score": _score(r[1])} for r in _table(text, "## 8. Treatment and residual risk") if r[0].startswith("TS-")]
  hazmap = {r[0]: _ids(r[1], "TS") for r in _table(text, "## 9. Interface to the risk assessment") if r[0].startswith("H-")}
  c03 = WP_C03.read_text(encoding="utf-8")
  hazards = {r[0]: _clean(r[1]) for r in _table(c03, "## 4. Hazard identification") if re.match(r"H-\d\d$", r[0])}
  c08 = WP_C08.read_text(encoding="utf-8")
  slt = {}
  for r in _table(c08, "## 2. Security level target"):
    if r[0].startswith("FR "):
      slt[r[0]] = _int(r[2])
  csrs = [r[0] for r in _table(c08, "## 4. Allocated requirements") if r[0].startswith("CSR-")]
  return {"text": text, "actors": actors, "assets": assets, "zones": zones, "conduits": conduits, "scenarios": scenarios, "risk": risk,
          "slcheck": slcheck, "residual": residual, "hazmap": hazmap, "hazards": hazards, "slt": slt, "csrs": csrs}


def check_source(src: dict) -> list[str]:
  errs = []
  if ANCHOR not in src["text"]:
    errs.append(f"the IX-01 anchor {ANCHOR!r} is missing (process model interfaces.yaml)")
  actors, assets, zones, conduits = src["actors"], src["assets"], src["zones"], src["conduits"]
  for a, v in actors.items():
    if v["sl"] not in (1, 2, 3, 4):
      errs.append(f"{a}: SL {v['sl']!r} is not 1 to 4")
  for cd, v in conduits.items():
    for end in ("from", "to"):
      if v[end] not in zones:
        errs.append(f"{cd}: {end} zone {v[end]!r} is not in §4.1")
    if v["to"] == "SZ-4" and "commissioning" not in v["carries"]:
      errs.append(f"{cd}: enters the safety chain SZ-4 for something other than commissioning")
    if v["from"] == "SZ-4" and "one way" not in v["carries"]:
      errs.append(f"{cd}: leaves the safety chain SZ-4 without being one way")
  for z, v in zones.items():
    for a in v["assets"]:
      if a not in assets:
        errs.append(f"{z}: asset {a} is not in §3")
  ids = [s["id"] for s in src["scenarios"]]
  if ids != [f"TS-{n:02d}" for n in range(1, len(ids) + 1)]:
    errs.append(f"§5 scenario IDs are not TS-01…TS-{len(ids):02d} in order: {ids}")
  for s in src["scenarios"]:
    if s["ncells"] != 8:
      errs.append(f"{s['id']}: §5 row has {s['ncells']} cells, expected 8")
      continue
    if not s["actors"] or any(a not in actors for a in s["actors"]):
      errs.append(f"{s['id']}: actor {s['actors']} not in §1.2")
    if not s["conduits"] and not s["conduit_cell"].startswith("none"):
      errs.append(f"{s['id']}: no conduit and not marked 'none (…)'")
    for cd in s["conduits"]:
      if cd not in conduits:
        errs.append(f"{s['id']}: conduit {cd} not in §4.2")
    if not s["assets"] or any(a not in assets for a in s["assets"]):
      errs.append(f"{s['id']}: asset {s['assets']} not in §3")
    if not s["hazards"] and s["hazard_cell"] != "none":
      errs.append(f"{s['id']}: hazard cell must name hazards or read 'none'")
    for h in s["hazards"]:
      if h not in src["hazards"]:
        errs.append(f"{s['id']}: {h} is not in the hazard list of WP-C-03 §4")
    if s["config"] not in ("both", "CFG-001", "CFG-002"):
      errs.append(f"{s['id']}: config {s['config']!r}")
  by_id = {s["id"]: s for s in src["scenarios"]}
  if [r["id"] for r in src["risk"]] != ids:
    errs.append("§6 rows are not the §5 scenarios in the same order")
  slt = src["slt"]
  if sorted(slt) != [f"FR {n}" for n in range(1, 8)] or any(v not in (1, 2, 3, 4) for v in slt.values()):
    errs.append(f"WP-C-08 §2 security level target is not FR 1…FR 7 with levels 1 to 4: {slt}")
  expected_gap = set()
  for r in src["risk"]:
    if r["ncells"] != 10:
      errs.append(f"{r['id']}: §6 row has {r['ncells']} cells, expected 10")
      continue
    t = f"{r['id']}"
    if r["l"] not in L_NAMES or r["i"] not in I_NAMES or r["i_arch"] not in I_NAMES or r["l_after"] not in L_NAMES:
      errs.append(f"{t}: likelihood and impact must be 1 to 4")
      continue
    want = r["l"] * r["i"]
    if r["before"] != (want, band(want)):
      errs.append(f"{t}: before is {r['before']}, {r['l']} x {r['i']} gives {want} {band(want)}")
    want2 = r["l_after"] * r["i_arch"]
    if r["after"] != (want2, band(want2)):
      errs.append(f"{t}: residual is {r['after']}, {r['l_after']} x {r['i_arch']} gives {want2} {band(want2)}")
    if r["i_arch"] > r["i"]:
      errs.append(f"{t}: impact with WP-S-03 ({r['i_arch']}) exceeds the impact before treatment ({r['i']})")
    if r["l_after"] > r["l"]:
      errs.append(f"{t}: likelihood after ({r['l_after']}) exceeds the likelihood before ({r['l']})")
    s = by_id.get(r["id"])
    if s and s["actors"] and all(a in actors for a in s["actors"]):
      need = max(actors[a]["sl"] for a in s["actors"])
      if r["sl_needed"] != need:
        errs.append(f"{t}: SL needed {r['sl_needed']}, the actor {s['actors']} implies {need}")
    if not r["frs"]:
      errs.append(f"{t}: no FR named")
    for fr in r["frs"]:
      if fr in slt and r["sl_needed"] is not None and slt[fr] is not None and slt[fr] < r["sl_needed"]:
        expected_gap.add((r["id"], fr))
    for csr in r["treatment"]:
      if csr not in src["csrs"]:
        errs.append(f"{t}: {csr} is not a requirement of WP-C-08 §4")
    if not r["treatment"] and not r["treatment_cell"].startswith("none: outside the SL-T"):
      errs.append(f"{t}: no treatment and not marked 'none: outside the SL-T'")
  listed = {(x["id"], x["fr"]) for x in src["slcheck"]}
  for pair in sorted(expected_gap - listed):
    errs.append(f"§7 misses {pair[0]} {pair[1]}: its target in WP-C-08 §2 is below the level the scenario needs")
  for pair in sorted(listed - expected_gap):
    errs.append(f"§7 lists {pair[0]} {pair[1]}, but the target covers it")
  risk_by_id = {r["id"]: r for r in src["risk"]}
  for x in src["slcheck"]:
    r = risk_by_id.get(x["id"])
    if r and (x["slt"] != slt.get(x["fr"]) or x["need"] != r["sl_needed"]):
      errs.append(f"§7 {x['id']} {x['fr']}: SL-T {x['slt']} and need {x['need']} disagree with WP-C-08 §2 and §6")
  for r in src["risk"]:
    if not r["treatment"] and not any(x["id"] == r["id"] and x["disposition"].startswith("Outside") for x in src["slcheck"]):
      errs.append(f"{r['id']}: untreated, but §7 does not record it as outside the target")
  want_res = {r["id"]: r["after"] for r in src["risk"] if r["after"][1] in ("medium", "high")}
  got_res = {x["id"]: x["score"] for x in src["residual"]}
  if want_res != got_res:
    errs.append(f"§8 lists {got_res}, §6 has medium or high residuals {want_res}")
  inverse: dict[str, list[str]] = {}
  for s in src["scenarios"]:
    for h in s["hazards"]:
      inverse.setdefault(h, []).append(s["id"])
  if inverse != src["hazmap"]:
    for h in sorted(set(inverse) | set(src["hazmap"])):
      if inverse.get(h) != src["hazmap"].get(h):
        errs.append(f"§9 {h}: lists {src['hazmap'].get(h)}, §5 gives {inverse.get(h)}")
  return errs


# ------------------------------------------------------------------ drawing

def _w(s: str, size: float) -> float:
  return len(s) * size * 0.56


def _wrap(s: str, width: float, size: float) -> list[str]:
  words, lines, cur = s.split(), [], ""
  for w in words:
    t = (cur + " " + w).strip()
    if _w(t, size) > width and cur:
      lines.append(cur)
      cur = w
    else:
      cur = t
  if cur:
    lines.append(cur)
  return lines


def text(x, y, s, size=12, fill=C["ink"], weight=400, anchor="start", family=FONT, extra=""):
  return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
          f'fill="{fill}" text-anchor="{anchor}"{extra}>{escape(s)}</text>')


def rect(x, y, w, h, fill, stroke=C["stroke"], r=6, sw=1, dash="", extra=""):
  d = f' stroke-dasharray="{dash}"' if dash else ""
  return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>'


def svg(w, h, uid, title, desc, body, defs=""):
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
          f'<title id="{uid}-t">{escape(title)}</title>\n<desc id="{uid}-d">{escape(desc)}</desc>\n'
          + (f"<defs>{defs}</defs>\n" if defs else "")
          + f'<rect x="0" y="0" width="{w}" height="{h}" fill="{C["bg"]}"/>\n' + "\n".join(body) + "\n</svg>\n")


def _arrow_defs(uid: str) -> str:
  out = []
  for key, hue in (("ink", C["line"]), ("red", C["red"]), ("amber", C["amber"])):
    out.append(f'<marker id="{uid}-{key}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
               f'<path d="M0,0 L10,5 L0,10 z" fill="{hue}"/></marker>')
  return "".join(out)


# zone boxes: x, y, w, h (the layout knows the five zones of §4.1)
ZONE_BOX = {"SZ-1": (24, 92, 214, 244), "SZ-2": (300, 92, 296, 244), "SZ-3": (664, 92, 214, 244),
            "SZ-4": (944, 92, 232, 244), "SZ-5": (300, 418, 876, 96)}


def _short(carries: str) -> str:
  return re.split(r"[;(]", carries)[0].strip().rstrip(",")


def fig_zones(src: dict) -> str:
  W, H = 1200, 590
  uid = "c07-4-1"
  zones, conduits = src["zones"], src["conduits"]
  body = [text(24, 30, "Figure 4-1  Security zones and conduits of the robot (IEC 62443-3-2 ZCR 3)", 15, C["ink"], 700),
          text(24, 50, f"{len(zones)} zones, {len(conduits)} conduits. No conduit from the network reaches the safety chain: it reports one way and is configured only at commissioning", 11, C["muted"])]
  for z, (x, y, w, h) in ZONE_BOX.items():
    if z not in zones:
      continue
    v = zones[z]
    hue, tint = ZONE_STYLE[z]
    sw = 2.6 if z == "SZ-4" else 1.4
    dash = "6,4" if z in ("SZ-1", "SZ-5") else ""
    body.append(rect(x, y, w, h, tint, stroke=hue, r=10, sw=sw, dash=dash))
    body.append(text(x + 14, y + 24, z, 12, hue, 700, family=MONO))
    body.append(text(x + 14 + _w(z, 12) + 10, y + 24, v["name"], 12.5, C["ink"], 700))
    trust = _wrap(f"trust: {v['trust']}", w - 28, 10)
    for k, ln in enumerate(trust[:2]):
      body.append(text(x + 14, y + 42 + k * 13, ln, 10, C["muted"], 500))
    y0 = y + 50 + 13 * len(trust[:2])
    lines = _wrap(v["contains"], w - 28, 10)
    maxl = 2 if z == "SZ-5" else 7
    for k, ln in enumerate(lines[:maxl]):
      body.append(text(x + 14, y0 + k * 14, ln + ("…" if k == maxl - 1 and len(lines) > maxl else ""), 10, C["ink"]))
    cx, cy = x + 14, (y + h - 30) if z != "SZ-5" else (y + h - 26)
    for a in v["assets"]:
      cw = _w(a, 8.5) + 10
      if cx + cw > x + w - 10:
        cx = x + 14
        cy -= 20
      body.append(rect(cx, cy, cw, 16, C["white"], stroke=hue, r=4, sw=1))
      body.append(text(cx + cw / 2, cy + 11.5, a, 8.5, hue, 600, "middle", MONO))
      cx += cw + 4
  # conduits
  pair_count: dict[tuple[str, str], int] = {}
  for cd, v in conduits.items():
    a, b = v["from"], v["to"]
    if a not in ZONE_BOX or b not in ZONE_BOX:
      continue
    key = tuple(sorted((a, b)))
    k = pair_count.get(key, 0)
    pair_count[key] = k + 1
    ax, ay, aw, ah = ZONE_BOX[a]
    bx, by, bw, bh = ZONE_BOX[b]
    into_chain = b == "SZ-4"
    hue = C["red"] if into_chain else (C["amber"] if a == "SZ-4" else C["line"])
    mk = "red" if into_chain else ("amber" if a == "SZ-4" else "ink")
    dash = ' stroke-dasharray="6,4"' if into_chain else ""
    label = f"{cd}  {_short(v['carries'])}"
    if a == "SZ-5" or b == "SZ-5":
      top = b if a == "SZ-5" else a
      tx, ty, tw, th = ZONE_BOX[top]
      px = tx + tw * (0.72 if top == "SZ-4" else 0.5)
      y1, y2 = ay if a == "SZ-5" else by, ty + th
      if a != "SZ-5":
        y1, y2 = ty + th, by
      body.append(f'<line x1="{px:.1f}" y1="{y1:.1f}" x2="{px:.1f}" y2="{y2:.1f}" stroke="{hue}" stroke-width="2"{dash} marker-end="url(#{uid}-{mk})"/>')
      ly = (y1 + y2) / 2
      right_edge = px > W - 260
      for n, ln in enumerate(_wrap(label, 190 if right_edge else 150, 9.5)[:4]):
        body.append(text(px - 8 if right_edge else px + 8, ly - 10 + n * 12, ln, 9.5, hue if into_chain else C["muted"], 600 if n == 0 else 400,
                         "end" if right_edge else "start"))
    else:
      left, right = (a, b) if ZONE_BOX[a][0] < ZONE_BOX[b][0] else (b, a)
      lx, ly0, lw, lh = ZONE_BOX[left]
      rx, ry0, rw, rh = ZONE_BOX[right]
      py = ly0 + 112 + k * 80
      x1, x2 = lx + lw, rx
      start, end = (x1, x2) if left == a else (x2, x1)
      body.append(f'<line x1="{start:.1f}" y1="{py:.1f}" x2="{end:.1f}" y2="{py:.1f}" stroke="{hue}" stroke-width="2"{dash} marker-end="url(#{uid}-{mk})"/>')
      mid = (x1 + x2) / 2
      lines = _wrap(label, max(60, x2 - x1 - 8), 9.5)
      for n, ln in enumerate(lines[:4]):
        body.append(text(mid, py - 8 - (len(lines[:4]) - 1 - n) * 12, ln, 9.5, C["amber"] if a == "SZ-4" else C["muted"], 600 if n == 0 else 400, "middle"))
  x, y, w, h = ZONE_BOX["SZ-4"]
  body.append(text(x + 14, y + h - 40, "no conduit from the network", 10.5, C["red"], 700))
  # legend
  ly = H - 22
  body.append(f'<line x1="24" y1="{ly - 4}" x2="60" y2="{ly - 4}" stroke="{C["line"]}" stroke-width="2" marker-end="url(#{uid}-ink)"/>')
  body.append(text(66, ly, "conduit, from the zone that opens it", 10.5, C["ink"]))
  body.append(f'<line x1="300" y1="{ly - 4}" x2="336" y2="{ly - 4}" stroke="{C["amber"]}" stroke-width="2" marker-end="url(#{uid}-amber)"/>')
  body.append(text(342, ly, "one-way status out of the safety chain", 10.5, C["ink"]))
  body.append(f'<line x1="600" y1="{ly - 4}" x2="636" y2="{ly - 4}" stroke="{C["red"]}" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#{uid}-red)"/>')
  body.append(text(642, ly, "into the safety chain: commissioning only, disconnected in operation", 10.5, C["ink"]))
  body.append(text(24, ly - 26, "Dashed zones are outside the item. Chips are the assets of §3 each zone holds.", 10.5, C["muted"]))
  return svg(W, H, uid, "Security zones and conduits of WP-C-07",
             "Five security zones: the site network, the robot compute, motion control, the safety chain and the development, supply and "
             "maintenance zone, with the conduits between them. The safety chain has no data conduit in; it reports one way to motion control "
             "and is configured only at commissioning.", body, _arrow_defs(uid))


def fig_matrix(src: dict) -> str:
  W = 1200
  cw, ch = 118, 72
  top = 112
  grids = [(112, "Before treatment", "the robot as inherited at BL-001", "before"), (700, "After WP-C-08", "the requirements, with the safety architecture of WP-S-03", "after")]
  H = top + 4 * ch + 112
  uid = "c07-6-1"
  risk = src["risk"]
  med = {r["id"] for r in risk if r["after"][1] in ("medium", "high")}
  haz = {s["id"]: bool(s["hazards"]) for s in src["scenarios"]}
  nb = {b: sum(1 for r in risk if r["before"][1] == b) for b in BANDS}
  na = {b: sum(1 for r in risk if r["after"][1] == b) for b in BANDS}
  body = [text(24, 30, "Figure 6-1  Threat scenarios on the likelihood x impact matrix, before and after treatment", 15, C["ink"], 700),
          text(24, 50, f"{len(risk)} scenarios. Before: {nb['high']} high, {nb['medium']} medium, {nb['low']} low. After: {na['high']} high, {na['medium']} medium, {na['low']} low. "
                       "The safety architecture moves a scenario left, the requirements move it down", 11, C["muted"])]
  for gx, title, sub, key in grids:
    body.append(text(gx, top - 34, title, 13, C["ink"], 700))
    body.append(text(gx + _w(title, 13) + 10, top - 34, sub, 10.5, C["muted"]))
    for li, l in enumerate((4, 3, 2, 1)):
      y = top + li * ch
      body.append(text(gx - 10, y + ch / 2 - 2, str(l), 12, C["ink"], 700, "end"))
      body.append(text(gx - 10, y + ch / 2 + 12, L_NAMES[l], 8.5, C["muted"], 400, "end"))
      for ii, i in enumerate((1, 2, 3, 4)):
        x = gx + ii * cw
        b = band(l * i)
        body.append(rect(x, y, cw - 4, ch - 4, BAND_FILL[b], stroke=C["white"], r=6, sw=1))
        body.append(text(x + cw - 10, y + 13, str(l * i), 9, BAND_INK[b], 700, "end"))
        cell = [r for r in risk if (r["l"], r["i"]) == (l, i)] if key == "before" else [r for r in risk if (r["l_after"], r["i_arch"]) == (l, i)]
        for n, r in enumerate(cell):
          px = x + 6 + (n % 5) * 22
          py = y + 18 + (n // 5) * 17
          ring = C["red"] if (key == "after" and r["id"] in med) else (C["teal"] if haz.get(r["id"]) else C["dim"])
          body.append(rect(px, py, 20, 15, C["white"], stroke=ring, r=4, sw=1.8 if r["id"] in med and key == "after" else 1.1))
          body.append(text(px + 10, py + 11, r["id"][3:], 8.5, C["ink"], 600, "middle", MONO))
    for ii, i in enumerate((1, 2, 3, 4)):
      x = gx + ii * cw + (cw - 4) / 2
      body.append(text(x, top + 4 * ch + 14, f"{i} {I_NAMES[i]}", 10, C["ink"], 600, "middle"))
    body.append(text(gx + 2 * cw - 2, top + 4 * ch + 32, "impact", 10.5, C["muted"], 700, "middle"))
    body.append(text(gx - 74, top + 2 * ch, "likelihood", 10.5, C["muted"], 700, "middle", extra=f' transform="rotate(-90 {gx - 74} {top + 2 * ch})"'))
  ly = top + 4 * ch + 70
  x = 24
  for b in BANDS:
    lo, hi = BANDS[b]
    body.append(rect(x, ly - 11, 26, 15, BAND_FILL[b], stroke=C["white"], r=4))
    lab = f"{b} ({lo}–{hi})"
    body.append(text(x + 32, ly, lab, 10.5, C["ink"]))
    x += 32 + _w(lab, 10.5) + 18
  for ring, lab in ((C["teal"], "can cause a hazard of WP-C-03"), (C["dim"], "no path to a person"), (C["red"], "residual for the lead to accept (§8)")):
    body.append(rect(x, ly - 11, 20, 15, C["white"], stroke=ring, r=4, sw=1.6))
    body.append(text(x + 26, ly, lab, 10.5, C["ink"]))
    x += 26 + _w(lab, 10.5) + 18
  body.append(text(24, ly + 24, "Chips are scenario numbers: 01 is TS-01. Risk = likelihood x impact; low is tolerable, medium only as an accepted residual, high never (§1.3).", 10.5, C["muted"]))
  return svg(W, H, uid, "Risk matrix of WP-C-07",
             "Two four-by-four matrices of likelihood against impact. Left, every threat scenario before treatment; right, after the "
             "cybersecurity requirements with the designed safety architecture. Cells are shaded low, medium or high.", body)


OUTPUTS = {"fig-c07-4-1-zones-conduits.svg": fig_zones, "fig-c07-6-1-risk-matrix.svg": fig_matrix}


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
    print(f"fig_c07: {len(OUTPUTS)} figures current; {len(src['scenarios'])} scenarios, {len(src['conduits'])} conduits, "
          f"{len(src['slcheck'])} security-level gaps checked against WP-C-03 and WP-C-08")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
