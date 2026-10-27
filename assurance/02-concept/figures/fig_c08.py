#!/usr/bin/env python3
"""Draw the WP-C-08 trace figure and check the cybersecurity requirements.

  fig-c08-4-1-trace.svg   Figure 4-1  the requirements CSR-nn against the threat scenarios TS-nn of WP-C-07, with the safety
                                      functions each requirement supports

The source of record is ../WP-C-08-cybersecurity-requirements-and-sl-target.md (§2 target, §3 component requirements, §4
allocated requirements, §5 safety-function interface, §7 the security requirements of WP-S-02). The check also reads the
scenarios and treatments of ../WP-C-07-cybersecurity-threat-and-risk-assessment.md §5 and §6, the safety functions of
../WP-C-03-risk-assessment.md §7 and the requirement IDs of ../../03-system/WP-S-02-safety-requirements.md. `--check`
fails when the SVG is stale, or when:

  - §2 is not FR 1…FR 7 with a level from 1 to 4;
  - a §3 row says "yes" with a level above its FR's target or no requirement meeting it, "no" with a level within the
    target (unless it is not used), or "pending" with a level within the target;
  - §3 and §4 disagree on which requirement meets which component requirement (checked both ways);
  - a requirement treats a scenario WP-C-07 does not have, or §4 and WP-C-07 §6 disagree on which requirement treats
    which scenario (checked both ways);
  - a requirement names a safety function not in WP-C-03 §7 or a safety requirement not in WP-S-02;
  - §5 does not list every safety function of WP-C-03 §7, or names a requirement §4 does not have;
  - §7 does not list every SR-90 requirement of WP-S-02, or disagrees with the "Supports" column of §4 (both ways).

    python3 fig_c08.py            # regenerate
    python3 fig_c08.py --check    # fail if the source changed or the SVG is stale

Standard library only. Output is deterministic.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "WP-C-08-cybersecurity-requirements-and-sl-target.md"
WP_C07 = HERE.parent / "WP-C-07-cybersecurity-threat-and-risk-assessment.md"
WP_C03 = HERE.parent / "WP-C-03-risk-assessment.md"
WP_S02 = HERE.parent.parent / "03-system" / "WP-S-02-safety-requirements.md"

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg": "#FFFFFF", "panel": "#F7FAFB", "stroke": "#D3DDE2", "line": "#7E949B", "ink": "#122026", "muted": "#4E6A73", "dim": "#7E949B",
  "amber": "#B86F0C", "amber_bg": "#FFF1DC", "teal": "#00938B", "teal_bg": "#E9F7F5", "red": "#D64535", "red_bg": "#FBE3E0",
  "green": "#2C9A58", "green_bg": "#E3F4E8", "grey_bg": "#EDF2F4", "white": "#FFFFFF", "blue": "#2F6FD6",
}
CR_RE = r"CR \d\.\d+(?: RE\(\d\))?"
BAND_FILL = {"low": C["green_bg"], "medium": C["amber_bg"], "high": C["red_bg"]}
BAND_INK = {"low": C["green"], "medium": C["amber"], "high": C["red"]}


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
  return re.findall(rf"\b{prefix}-\d\d\b", cell)


def _int(cell: str) -> int | None:
  c = _clean(cell)
  return int(c) if c.isdigit() else None


def load_source() -> dict:
  text = SOURCE.read_text(encoding="utf-8")
  slt = {r[0]: _int(r[2]) for r in _table(text, "## 2. Security level target") if r[0].startswith("FR ")}
  crs = []
  for r in _table(text, "## 3. Component requirements at the target"):
    if not r[0].startswith("CR "):
      continue
    crs.append({"id": r[0], "title": _clean(r[1]), "sl": _int(r[2]), "applies": _clean(r[3]), "met_by": _ids(r[4], "CSR"),
                "fr": f"FR {r[0][3]}", "ncells": len(r)})
  csrs = []
  for r in _table(text, "## 4. Allocated requirements"):
    if not r[0].startswith("CSR-"):
      continue
    m = re.match(r"\*\*(.+?)\.\*\*", r[1])
    csrs.append({"id": r[0], "name": m.group(1) if m else "", "text": _clean(r[1]), "crs": re.findall(CR_RE, r[2]) if len(r) > 2 else [],
                 "element": _clean(r[3]) if len(r) > 3 else "", "config": _clean(r[4]) if len(r) > 4 else "",
                 "treats": _ids(r[5], "TS") if len(r) > 5 else [], "sfs": _ids(r[6], "SF") if len(r) > 6 else [],
                 "srs": re.findall(r"SR-\d\d\.\d\d", r[6]) if len(r) > 6 else [], "supports": _clean(r[6]) if len(r) > 6 else "",
                 "verif": [v.strip() for v in _clean(r[7]).split(",")] if len(r) > 7 else [], "ncells": len(r)})
  sf_rows = {r[0]: {"protected_by": _ids(r[2], "CSR")} for r in _table(text, "## 5. Interface to the safety functions") if r[0].startswith("SF-")}
  sr_rows = {r[0]: _ids(r[1], "CSR") for r in _table(text, "## 7. The security requirements of WP-S-02") if r[0].startswith("SR-")}
  c07 = WP_C07.read_text(encoding="utf-8")
  scenarios = [r[0] for r in _table(c07, "## 5. Threat scenarios") if r[0].startswith("TS-")]
  treatments, residual = {}, {}
  for r in _table(c07, "## 6. Risk assessment"):
    if r[0].startswith("TS-") and len(r) >= 10:
      treatments[r[0]] = _ids(r[7], "CSR")
      m = re.search(r"(low|medium|high)", r[9])
      residual[r[0]] = m.group(1) if m else ""
  c03 = WP_C03.read_text(encoding="utf-8")
  sfs = [r[0] for r in _table(c03, "## 7. Safety functions") if re.match(r"SF-\d\d$", r[0])]
  s02 = WP_S02.read_text(encoding="utf-8")
  srs = sorted(set(re.findall(r"^\| (SR-\d\d\.\d\d) \|", s02, re.M)))
  return {"slt": slt, "crs": crs, "csrs": csrs, "sf_rows": sf_rows, "sr_rows": sr_rows, "scenarios": scenarios,
          "treatments": treatments, "residual": residual, "sfs": sfs, "srs": srs}


def check_source(src: dict) -> list[str]:
  errs = []
  slt = src["slt"]
  if sorted(slt) != [f"FR {n}" for n in range(1, 8)] or any(v not in (1, 2, 3, 4) for v in slt.values()):
    errs.append(f"§2 is not FR 1…FR 7 with levels 1 to 4: {slt}")
  csr_ids = [c["id"] for c in src["csrs"]]
  if csr_ids != [f"CSR-{n:02d}" for n in range(1, len(csr_ids) + 1)]:
    errs.append(f"§4 requirement IDs are not CSR-01…CSR-{len(csr_ids):02d} in order")
  csr_by = {c["id"]: c for c in src["csrs"]}
  cr_by = {}
  for cr in src["crs"]:
    if cr["id"] in cr_by:
      errs.append(f"§3 lists {cr['id']} twice")
    cr_by[cr["id"]] = cr
    t, target = cr["id"], slt.get(cr["fr"])
    if cr["ncells"] != 5 or cr["sl"] not in (1, 2, 3, 4) or target is None:
      errs.append(f"{t}: malformed §3 row")
      continue
    a = cr["applies"]
    if a == "yes":
      if cr["sl"] > target:
        errs.append(f"{t}: applies 'yes' at SL {cr['sl']}, above the {cr['fr']} target {target}")
      if not cr["met_by"]:
        errs.append(f"{t}: applies, but no requirement meets it")
    elif a.startswith("no"):
      if cr["sl"] <= target and "not used" not in a:
        errs.append(f"{t}: 'no' at SL {cr['sl']}, within the {cr['fr']} target {target}, without 'not used'")
    elif a.startswith("pending DQ-"):
      if cr["sl"] <= target:
        errs.append(f"{t}: pending, but SL {cr['sl']} is within the {cr['fr']} target {target}")
      if not cr["met_by"]:
        errs.append(f"{t}: pending with no requirement written for it")
    else:
      errs.append(f"{t}: applies must be yes, no: … or pending DQ-…, got {a!r}")
    for csr in cr["met_by"]:
      if csr not in csr_by:
        errs.append(f"{t}: met by {csr}, not in §4")
      elif t not in csr_by[csr]["crs"]:
        errs.append(f"{t}: §3 says {csr} meets it, but {csr} does not cite it")
  for c in src["csrs"]:
    t = c["id"]
    if c["ncells"] != 8:
      errs.append(f"{t}: §4 row has {c['ncells']} cells, expected 8")
      continue
    if not c["name"]:
      errs.append(f"{t}: the requirement does not open with a bold name ('**Name.** …')")
    if not c["crs"]:
      errs.append(f"{t}: cites no component requirement")
    for cr in c["crs"]:
      if cr not in cr_by:
        errs.append(f"{t}: cites {cr}, not in §3")
      elif t not in cr_by[cr]["met_by"]:
        errs.append(f"{t}: cites {cr}, but §3 does not list {t} as meeting it")
    if c["config"] not in ("both", "CFG-001", "CFG-002"):
      errs.append(f"{t}: config {c['config']!r}")
    if not c["treats"]:
      errs.append(f"{t}: treats no threat scenario")
    for ts in c["treats"]:
      if ts not in src["scenarios"]:
        errs.append(f"{t}: treats {ts}, not in WP-C-07 §5")
      elif t not in src["treatments"].get(ts, []):
        errs.append(f"{t}: treats {ts}, but WP-C-07 §6 does not list {t} for it")
    for sf in c["sfs"]:
      if sf not in src["sfs"]:
        errs.append(f"{t}: supports {sf}, not in WP-C-03 §7")
    for sr in c["srs"]:
      if sr not in src["srs"]:
        errs.append(f"{t}: supports {sr}, not in WP-S-02")
    if not (c["sfs"] or c["srs"]) and c["supports"] != "none":
      errs.append(f"{t}: 'Supports' must name SF-nn or SR-nn.nn, or read 'none'")
    if not c["verif"] or any(v not in ("I", "T", "P") for v in c["verif"]):
      errs.append(f"{t}: verification {c['verif']} must be I, T or P")
  for ts, lst in src["treatments"].items():
    for csr in lst:
      if csr in csr_by and ts not in csr_by[csr]["treats"]:
        errs.append(f"WP-C-07 §6 treats {ts} with {csr}, but {csr} does not list {ts}")
  for sf in src["sfs"]:
    if sf not in src["sf_rows"]:
      errs.append(f"§5 has no row for {sf}")
  for sf, v in src["sf_rows"].items():
    if sf not in src["sfs"]:
      errs.append(f"§5 lists {sf}, not in WP-C-03 §7")
    for csr in v["protected_by"]:
      if csr not in csr_by:
        errs.append(f"§5 {sf}: {csr} not in §4")
  sr90 = [s for s in src["srs"] if s.startswith("SR-90.")]
  if sorted(src["sr_rows"]) != sr90:
    errs.append(f"§7 lists {sorted(src['sr_rows'])}, WP-S-02 has {sr90}")
  for sr, lst in src["sr_rows"].items():
    for csr in lst:
      if csr not in csr_by:
        errs.append(f"§7 {sr}: {csr} not in §4")
      elif sr not in csr_by[csr]["srs"]:
        errs.append(f"§7 {sr}: met by {csr}, but {csr} does not support it")
  for c in src["csrs"]:
    for sr in c["srs"]:
      if sr.startswith("SR-90.") and c["id"] not in src["sr_rows"].get(sr, []):
        errs.append(f"{c['id']}: supports {sr}, but §7 does not list it")
  return errs


# ------------------------------------------------------------------ drawing

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


def fig_trace(src: dict) -> str:
  csrs, scen = src["csrs"], src["scenarios"]
  W = 1200
  labx, labw = 24, 300
  gx, cw = labx + labw + 10, 27
  chipx = gx + len(scen) * cw + 14
  rowh = 22
  top = 118
  H = top + len(csrs) * rowh + 78
  uid = "c08-4-1"
  untreated = [ts for ts in scen if not src["treatments"].get(ts)]
  body = [text(24, 30, "Figure 4-1  Cybersecurity requirements against the threat scenarios of WP-C-07", 15, C["ink"], 700),
          text(24, 50, f"{len(csrs)} requirements, {len(scen)} scenarios. A dot marks a treatment; chips name the safety functions a requirement supports; "
                       "column heads are shaded by the residual risk after treatment", 11, C["muted"])]
  # column heads
  for k, ts in enumerate(scen):
    x = gx + k * cw
    res = src["residual"].get(ts, "low")
    body.append(rect(x + 1, top - 46, cw - 2, 40, BAND_FILL.get(res, C["grey_bg"]), stroke="none", r=4))
    body.append(text(x + cw / 2, top - 30, "TS", 8, BAND_INK.get(res, C["dim"]), 600, "middle", MONO))
    body.append(text(x + cw / 2, top - 16, ts[3:], 10, BAND_INK.get(res, C["dim"]), 700, "middle", MONO))
  body.append(text(chipx, top - 16, "Supports", 10.5, C["muted"], 700))
  for i, c in enumerate(csrs):
    y = top + i * rowh
    if i % 2 == 0:
      body.append(rect(16, y, chipx - 22, rowh, C["panel"], stroke="none", r=0))
    body.append(text(labx, y + 15, c["id"], 10, C["ink"], 700, family=MONO))
    name = c["name"] + (" (CFG-002)" if c["config"] == "CFG-002" else "")
    body.append(text(labx + 58, y + 15, name, 10.5, C["ink"]))
    for k, ts in enumerate(scen):
      x = gx + k * cw + cw / 2
      if ts in c["treats"]:
        body.append(f'<circle cx="{x:.1f}" cy="{y + rowh / 2:.1f}" r="5.5" fill="{C["teal"]}"/>')
      else:
        body.append(f'<circle cx="{x:.1f}" cy="{y + rowh / 2:.1f}" r="1.4" fill="{C["stroke"]}"/>')
    x = chipx
    shown = c["sfs"] if len(c["sfs"]) <= 6 else c["sfs"][:5]
    for sf in shown:
      w = _w(sf, 8.5) + 10
      body.append(rect(x, y + 3, w, 16, C["teal_bg"], stroke=C["teal"], r=4, sw=1))
      body.append(text(x + w / 2, y + 14.5, sf, 8.5, C["teal"], 600, "middle", MONO))
      x += w + 4
    if len(shown) < len(c["sfs"]):
      body.append(text(x + 2, y + 15, f"+{len(c['sfs']) - len(shown)} more", 9.5, C["teal"], 600))
    if not c["sfs"]:
      srs = [s for s in c["srs"]]
      label = ", ".join(srs) if srs else "no safety function"
      body.append(text(chipx, y + 15, label, 9.5, C["muted"] if srs else C["dim"], 500, family=MONO if srs else FONT))
  for k, ts in enumerate(scen):
    if ts in untreated:
      x = gx + k * cw
      body.append(rect(x + 2, top, cw - 4, len(csrs) * rowh, C["grey_bg"], stroke=C["dim"], r=3, dash="3,3", extra=' fill-opacity="0.85"'))
      body.append(text(x + cw / 2, top + len(csrs) * rowh / 2, "outside the target", 9.5, C["muted"], 600, "middle",
                       extra=f' transform="rotate(-90 {x + cw / 2:.1f} {top + len(csrs) * rowh / 2:.1f})"'))
  ly = top + len(csrs) * rowh + 28
  body.append(f'<circle cx="30" cy="{ly - 4}" r="5.5" fill="{C["teal"]}"/>')
  body.append(text(42, ly, "treats the scenario (WP-C-07 §6)", 10.5, C["ink"]))
  x = 260
  for res in ("low", "medium"):
    body.append(rect(x, ly - 12, 22, 16, BAND_FILL[res], stroke="none", r=4))
    lab = f"residual {res}"
    body.append(text(x + 28, ly, lab, 10.5, C["ink"]))
    x += 28 + _w(lab, 10.5) + 18
  body.append(rect(x, ly - 12, 22, 16, C["grey_bg"], stroke=C["dim"], r=3, dash="3,3"))
  body.append(text(x + 28, ly, "outside the security level target: carried by the safety architecture (WP-C-07 §7)", 10.5, C["ink"]))
  body.append(text(24, ly + 24, "Where no safety function relies on a requirement, the column names the safety requirement of WP-S-02 it meets, if any.", 10.5, C["muted"]))
  return svg(W, H, uid, "Cybersecurity requirements traced to threat scenarios",
             "A matrix of the cybersecurity requirements against the threat scenarios they treat, with chips naming the safety functions "
             "each requirement supports. One scenario, a sensing attack outside the security level target, has no requirement.", body)


OUTPUTS = {"fig-c08-4-1-trace.svg": fig_trace}


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
    print(f"fig_c08: {len(OUTPUTS)} figure current; {len(src['csrs'])} requirements, {len(src['crs'])} component requirements, "
          f"{len(src['scenarios'])} scenarios and {len(src['sf_rows'])} safety functions traced")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
