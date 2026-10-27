#!/usr/bin/env python3
"""Judge the Gazebo scenario traces against scenarios.yaml and write the results.

Every check of scenarios.yaml is evaluated, on every target of pins.yaml, from the trace's true pose (Gazebo's model
pose, not odometry) and the nav2 footprint: clearance between the footprint and each obstacle, how far the robot
advanced, the distance travelled after a fault before the robot stands still, the highest reverse speed. A check
passes when its outcome (holds, violated or not exercised) is the one the record predicts for that target
(`expected`, one value for every target or one per target).

    python3 evaluate.py --write                 # results/traces/<target>/ -> results/summary.json, README.md, figure
    python3 evaluate.py --check                 # fast CI: recompute from the committed traces; fail if stale or any check fails
    python3 evaluate.py --traces DIR --verify   # after a fresh simulation run: fail if any check fails (nothing written)

Standard library plus PyYAML. Output is deterministic.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

HERE = Path(__file__).resolve().parent
SCENARIOS = HERE / "scenarios.yaml"
PINS = HERE / "pins.yaml"
RESULTS = HERE / "results"
TRACES = RESULTS / "traces"
CONTACT_M = 0.03       # clearance at or below this is contact (footprint polygon against collision geometry)
STILL_MPS = 0.01       # true speed below this is standing still
STILL_S = 0.5          # for at least this long
SMOOTH = 5             # samples in the speed window
STEP_S = 0.05          # the driver samples at 20 Hz


# ------------------------------------------------------------------ geometry

def footprint_world(fp, x, y, yaw):
  c, s = math.cos(yaw), math.sin(yaw)
  return [(x + c * px - s * py, y + s * px + c * py) for px, py in fp]


def _seg_point(p, a, b):
  ax, ay = a
  bx, by = b
  dx, dy = bx - ax, by - ay
  L = dx * dx + dy * dy
  t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L))
  return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def _inside(p, poly):
  x, y = p
  inside = False
  for i in range(len(poly)):
    (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
    if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
      inside = not inside
  return inside


def poly_poly(a, b):
  if any(_inside(p, b) for p in a) or any(_inside(p, a) for p in b):
    return 0.0
  edges = lambda P: [(P[i], P[(i + 1) % len(P)]) for i in range(len(P))]
  return min(min(_seg_point(p, *e) for e in edges(b) for p in a), min(_seg_point(p, *e) for e in edges(a) for p in b))


def clearance(fp_world, ob):
  x, y, _ = ob["pose"]
  if ob["shape"] == "box":
    sx, sy, _ = ob["size"]
    rect = [(x - sx / 2, y - sy / 2), (x + sx / 2, y - sy / 2), (x + sx / 2, y + sy / 2), (x - sx / 2, y + sy / 2)]
    return poly_poly(fp_world, rect)
  r = ob["size"][0]
  if _inside((x, y), fp_world):
    return 0.0
  d = min(_seg_point((x, y), fp_world[i], fp_world[(i + 1) % len(fp_world)]) for i in range(len(fp_world)))
  return max(0.0, d - r)


# ------------------------------------------------------------------ metrics

def true_speed(rows):
  """Signed speed along the heading from consecutive true poses, smoothed over SMOOTH samples."""
  raw = [0.0]
  for a, b in zip(rows, rows[1:]):
    dt = b["t"] - a["t"]
    if dt <= 0:
      raw.append(raw[-1])
      continue
    raw.append(((b["x"] - a["x"]) * math.cos(b["yaw"]) + (b["y"] - a["y"]) * math.sin(b["yaw"])) / dt)
  out = []
  for i in range(len(raw)):
    w = raw[max(0, i - SMOOTH + 1):i + 1]
    out.append(sum(w) / len(w))
  return out


def metrics(spec, trace):
  rows, fp = trace["rows"], trace["footprint"]
  v = true_speed(rows)
  obs = spec.get("obstacles", [])
  clear = [min((clearance(footprint_world(fp, r["x"], r["y"], r["yaw"]), o) for o in obs), default=None) for r in rows]
  m = {"samples": len(rows), "duration_s": rows[-1]["t"] if rows else 0.0,
       "travel_m": round(math.hypot(rows[-1]["x"] - rows[0]["x"], rows[-1]["y"] - rows[0]["y"]), 3) if rows else 0.0,
       "max_forward_mps": round(max(v), 3) if v else 0.0, "max_reverse_mps": round(max(0.0, -min(v)), 3) if v else 0.0,
       "monitor_actions": sorted({r["action"] for r in rows}), "monitor_state": trace.get("monitor", {}).get("state")}
  if obs:
    m["min_clearance_m"] = round(min(clear), 3)
    first = next((r["t"] for r, c in zip(rows, clear) if c <= CONTACT_M), None)
    m["contact_at_s"] = first
  for f in spec.get("faults", []):
    i0 = next((i for i, r in enumerate(rows) if r["t"] >= float(f["at"])), None)
    if i0 is None:
      continue
    stop = None   # first sample after which the robot stays still to the end of the trace, for at least STILL_S
    for i in range(i0, len(rows)):
      if all(abs(x) < STILL_MPS for x in v[i:]) and rows[-1]["t"] - rows[i]["t"] >= STILL_S:
        stop = i
        break
    a = rows[i0]
    m["fault_at_s"] = a["t"]
    before = v[max(0, i0 - int(1.0 / STEP_S)):i0 + 1]
    m["speed_at_fault_mps"] = round(sum(before) / len(before), 3)
    if stop is not None:
      b = rows[stop]
      m["stopped_at_s"] = b["t"]
      m["travel_after_fault_m"] = round(math.hypot(b["x"] - a["x"], b["y"] - a["y"]), 3)
    else:
      m["stopped_at_s"] = None
      m["travel_after_fault_m"] = round(math.hypot(rows[-1]["x"] - a["x"], rows[-1]["y"] - a["y"]), 3)
  return m


def outcome(check, m):
  p = check["property"]
  if p == "no_contact":
    return "holds" if m.get("contact_at_s") is None else "violated"
  if p == "advances":
    return "holds" if m["travel_m"] >= float(check["min_m"]) else "violated"
  if p == "monitor_engaged":
    return "holds" if any(a in (1, 2, 3) for a in m["monitor_actions"]) else "violated"
  if p == "stops_after_fault":
    if abs(m["speed_at_fault_mps"]) < STILL_MPS:
      return "not exercised"   # the robot was already standing when the fault came
    return "holds" if m.get("stopped_at_s") is not None and m["travel_after_fault_m"] <= float(check["limit_m"]) else "violated"
  if p == "reverse_speed_le":
    return "holds" if m["max_reverse_mps"] <= float(check["limit_mps"]) + 0.005 else "violated"
  raise ValueError(f"unknown property {p}")


def per_target(value, target):
  """A check's `expected` or `why`: one value for every target, or a mapping target -> value."""
  return value[target] if isinstance(value, dict) else value


def load_pins() -> dict:
  return yaml.safe_load(PINS.read_text(encoding="utf-8"))


def evaluate(traces_dir: Path) -> dict:
  specs = yaml.safe_load(SCENARIOS.read_text(encoding="utf-8"))["scenarios"]
  pins = load_pins()
  targets = list(pins["targets"])
  out = {"pins": {"targets": {t: str(pins["targets"][t]["commit"]) for t in targets}, "navigation2": pins["navigation2"]["commit"][:7],
                  "laser_filters": pins["laser_filters"]["commit"][:7], "image": pins["image"]["base"].split("@")[-1][:19]},
         "scenarios": []}
  for s in specs:
    entry = {"id": s["id"], "title": s["title"], "record": s.get("record", []), "runs": {}}
    for t in targets:
      p = traces_dir / t / f"{s['id']}.trace.json"
      if not p.exists():
        entry["runs"][t] = {"status": "not run", "checks": [
          {"property": c["property"], "expected": per_target(c["expected"], t), "outcome": "not run", "pass": False} for c in s["checks"]]}
        continue
      trace = json.loads(p.read_text(encoding="utf-8"))
      m = metrics(s, trace)
      checks = []
      for c in s["checks"]:
        o, e = outcome(c, m), per_target(c["expected"], t)
        checks.append({"property": c["property"], "expected": e, "outcome": o, "pass": o == e})
      entry["runs"][t] = {"status": "run", "software_commit": trace.get("software_commit", "")[:7], "scan_filter": trace.get("scan_filter", ""),
                          "metrics": m, "checks": checks}
    out["scenarios"].append(entry)
  return out


def all_checks(res: dict):
  for s in res["scenarios"]:
    for t, run in s["runs"].items():
      for c in run["checks"]:
        yield s["id"], t, c


# ------------------------------------------------------------------ writing

def _measured(m: dict) -> str:
  meas = []
  if not m:
    return ""
  meas.append(f"travel {m['travel_m']} m")
  if "min_clearance_m" in m:
    meas.append(f"min clearance {m['min_clearance_m']} m" + (f", contact at {m['contact_at_s']} s" if m.get("contact_at_s") is not None else ""))
  if "travel_after_fault_m" in m:
    meas.append(f"{m['speed_at_fault_mps']} m/s at the fault, {m['travel_after_fault_m']} m after it"
                + (f", still at {m['stopped_at_s']} s" if m.get("stopped_at_s") is not None else ", never stopped"))
  meas.append(f"max {m['max_forward_mps']} m/s forward, {m['max_reverse_mps']} m/s reverse")
  meas.append("monitor actions " + ", ".join(str(a) for a in m["monitor_actions"]))
  return "; ".join(meas)


def report_md(res: dict) -> str:
  specs = {s["id"]: s for s in yaml.safe_load(SCENARIOS.read_text(encoding="utf-8"))["scenarios"]}
  targets = list(res["pins"]["targets"])
  n = sum(1 for _ in all_checks(res))
  ok = sum(c["pass"] for _, _, c in all_checks(res))
  lines = ["# Gazebo scenario results", "",
           "> Generated by [`../evaluate.py`](../evaluate.py) from the traces in [`traces/`](traces/); do not edit by hand.",
           "> Simulation: development evidence only, no evidence credit (see [`../README.md`](../README.md)).", "",
           f"**{ok} of {n} checks show what the record predicts.** Nav2 `{res['pins']['navigation2']}`, laser_filters "
           f"`{res['pins']['laser_filters']}`, base image `{res['pins']['image']}`.", "",
           "| Target | Software | Scan body filter |", "|---|---|---|"]
  for t in targets:
    runs = [s["runs"][t] for s in res["scenarios"] if s["runs"][t]["status"] == "run"]
    filt = runs[0]["scan_filter"] if runs else "not run"
    lines.append(f"| `{t}` | `{res['pins']['targets'][t]}` {'(BL-001)' if t == 'bl-001' else '(not a baseline)'} | {filt} |")
  lines += ["", "![Figure 1: one row per scenario and one panel per target, the robot's true speed over time and, where there is an "
            "obstacle, the clearance between its footprint and the obstacle, with each check's verdict](scenarios.svg)", "",
            "| Scenario | Check | " + " | ".join(f"`{t}` predicted / observed" for t in targets) + " |",
            "|---|---|" + "---|" * len(targets)]
  for s in res["scenarios"]:
    for k, c in enumerate(specs[s["id"]]["checks"]):
      cells = []
      for t in targets:
        r = s["runs"][t]["checks"][k]
        cells.append(f"{r['expected']} / {r['outcome']}" + ("" if r["pass"] else " **(fails)**"))
      lines.append(f"| {s['id'] if k == 0 else ''} | {c['property']} | " + " | ".join(cells) + " |")
  lines += ["", "Monitor actions are nav2_msgs/CollisionMonitorState codes: 0 nothing, 1 stop, 2 slow down, 3 approach, 4 limit.", "",
            "## Measured", "", "| Scenario | Target | Measured |", "|---|---|---|"]
  for s in res["scenarios"]:
    for j, t in enumerate(targets):
      lines.append(f"| {s['id'] if j == 0 else ''} | `{t}` | {_measured(s['runs'][t].get('metrics', {})) or 'not run'} |")
  lines += ["", "## Why each prediction", ""]
  for s in res["scenarios"]:
    parts = []
    for c in specs[s["id"]]["checks"]:
      w = c["why"]
      parts.append(f"{c['property']}: " + ("; ".join(f"`{t}` {w[t]}" for t in targets) if isinstance(w, dict) else w) + ".")
    lines.append(f"- **{s['id']}** {s['title']}. " + " ".join(parts))
  return "\n".join(lines) + "\n"


TARGET_INK = ["#4E6A73", "#00938B", "#6B4FA8"]
OUTCOME_INK = {"holds": ("#E3F4E8", "#2C9A58"), "violated": ("#FBE3E0", "#D64535"), "not exercised": ("#EEF2F4", "#4E6A73")}


def figure_svg(res: dict, traces_dir: Path) -> str:
  specs = {s["id"]: s for s in yaml.safe_load(SCENARIOS.read_text(encoding="utf-8"))["scenarios"]}
  targets = list(res["pins"]["targets"])
  W, ph, top, chip = 1000, 120, 76, 30
  rowh = ph + 30 + chip * max(len(s["checks"]) for s in specs.values()) + 26
  H = top + len(res["scenarios"]) * rowh + 10
  font = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
  t_ = lambda x, y, s, size=11, fill="#122026", weight=400, anchor="start": (
    f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')
  body = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
          t_(24, 28, "Figure 1  Gazebo scenarios on each target: true speed and footprint clearance to the obstacle over sim time", 14, weight=700),
          t_(24, 46, "Synthetic, no evidence credit. Solid: true speed (0 at the centre line, ±0.3 m/s at the edges); amber: clearance; "
                     "dashed red: contact; dashed grey: fault", 10.5, "#4E6A73"),
          t_(24, 62, "Under each panel, one chip per check, coloured by what the simulation shows (green holds, red violated, grey not exercised); "
                     "a dark border marks an outcome the record does not predict", 10.5, "#4E6A73")]
  gap, x0 = 30, 70
  pw = (W - x0 - 24 - gap * (len(targets) - 1)) / len(targets)
  for k, s in enumerate(res["scenarios"]):
    spec = specs[s["id"]]
    y0 = top + k * rowh + 16
    body.append(t_(24, y0 - 4, f"{s['id']}  {s['title']}", 11, weight=600))
    obs = spec.get("obstacles", [])
    for j, tg in enumerate(targets):
      px = x0 + j * (pw + gap)
      ink = TARGET_INK[j % len(TARGET_INK)]
      py = y0 + 6
      body.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph}" fill="#F7FAFB" stroke="#D3DDE2"/>')
      body.append(t_(px + 6, py + 13, tg, 9.5, ink, 600))
      run = s["runs"][tg]
      if run["status"] == "run":
        trace = json.loads((traces_dir / tg / f"{s['id']}.trace.json").read_text(encoding="utf-8"))
        rows = trace["rows"]
        v = true_speed(rows)
        T = max(r["t"] for r in rows) or 1.0
        vmax = 0.3
        X = lambda tt: px + pw * tt / T
        Yv = lambda vv: py + ph / 2 - (ph / 2 - 6) * vv / vmax
        body.append(f'<line x1="{px:.1f}" y1="{Yv(0):.1f}" x2="{px + pw:.1f}" y2="{Yv(0):.1f}" stroke="#D3DDE2"/>')
        pts = " ".join(f"{X(r['t']):.1f},{Yv(max(-vmax, min(vmax, vv))):.1f}" for r, vv in zip(rows, v))
        body.append(f'<polyline points="{pts}" fill="none" stroke="{ink}" stroke-width="1.8"/>')
        if obs:
          clear = [min(clearance(footprint_world(trace["footprint"], r["x"], r["y"], r["yaw"]), o) for o in obs) for r in rows]
          cmax = max(clear) or 1.0
          Yc = lambda cc: py + ph - 6 - (ph - 26) * cc / cmax
          pts = " ".join(f"{X(r['t']):.1f},{Yc(c):.1f}" for r, c in zip(rows, clear))
          body.append(f'<polyline points="{pts}" fill="none" stroke="#B86F0C" stroke-width="1.6"/>')
          body.append(f'<line x1="{px:.1f}" y1="{Yc(CONTACT_M):.1f}" x2="{px + pw:.1f}" y2="{Yc(CONTACT_M):.1f}" stroke="#D64535" stroke-dasharray="4,3"/>')
          body.append(t_(px + pw - 4, py + 13, f"clearance from {cmax:.2f} m", 9, "#B86F0C", anchor="end"))
        for f in spec.get("faults", []):
          body.append(f'<line x1="{X(float(f["at"])):.1f}" y1="{py:.1f}" x2="{X(float(f["at"])):.1f}" y2="{py + ph:.1f}" stroke="#7E949B" stroke-dasharray="5,3"/>')
        body.append(t_(px + pw, py + ph + 12, f"{T:.0f} s", 9, "#7E949B", anchor="end"))
      else:
        body.append(t_(px + pw / 2, py + ph / 2, "not run", 11, "#7E949B", anchor="middle"))
      for i, c in enumerate(run["checks"]):
        fill, cink = OUTCOME_INK.get(c["outcome"], ("#EEF2F4", "#7E949B"))
        cy = py + ph + 18 + i * chip
        stroke = f'stroke="{cink}"' if c["pass"] else 'stroke="#122026" stroke-width="2.2"'
        body.append(f'<rect x="{px:.1f}" y="{cy:.1f}" width="{pw:.1f}" height="{chip - 4}" rx="5" fill="{fill}" {stroke}/>')
        body.append(t_(px + 8, cy + 16, f"{c['property']}: {c['outcome']}", 10, cink, 600))
        verdict = "as predicted" if c["pass"] else f"PREDICTED {c['expected'].upper()}"
        body.append(t_(px + pw - 8, cy + 16, verdict, 10, "#122026" if c["pass"] else "#D64535", 400 if c["pass"] else 700, anchor="end"))
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="gzs-t gzs-d">\n'
          f'<title id="gzs-t">Gazebo scenario results</title>\n<desc id="gzs-d">One row per scenario and one panel per target with the true speed and '
          f'the clearance to the obstacle over time, and the verdict of each check against the outcome the record predicts.</desc>\n' + "\n".join(body) + "\n</svg>\n")


def outputs(res: dict, traces_dir: Path) -> dict[Path, str]:
  return {RESULTS / "summary.json": json.dumps(res, indent=1, sort_keys=False) + "\n", RESULTS / "README.md": report_md(res),
          RESULTS / "scenarios.svg": figure_svg(res, traces_dir)}


def main(argv: list[str]) -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--traces", type=Path, default=TRACES)
  g = ap.add_mutually_exclusive_group()
  g.add_argument("--write", action="store_true")
  g.add_argument("--check", action="store_true")
  g.add_argument("--verify", action="store_true")
  a = ap.parse_args(argv)
  res = evaluate(a.traces)
  failed = [(sid, t, c["property"], c["expected"], c["outcome"]) for sid, t, c in all_checks(res) if not c["pass"]]
  if a.write:
    for p, text in outputs(res, a.traces).items():
      p.write_text(text, encoding="utf-8")
      print(f"wrote {p.relative_to(HERE)}")
  elif a.check:
    stale = [p.name for p, text in outputs(res, a.traces).items() if not p.exists() or p.read_text(encoding="utf-8") != text]
    for s in stale:
      print(f"STALE results/{s}: run python3 {Path(__file__).name} --write")
    if stale:
      return 1
  for sid, t, prop, exp, got in failed:
    print(f"FAIL {sid} on {t} {prop}: the record predicts {exp}, the simulation shows {got}")
  if not failed:
    print(f"gazebo scenarios: {sum(1 for _ in all_checks(res))} checks show what the record predicts")
  return 1 if failed and (a.check or a.verify) else 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
