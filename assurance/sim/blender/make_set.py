#!/usr/bin/env python3
"""Render the review set and stamp each picture with its title, caption and the no-evidence-credit band.
Usage: make_set.py <mesh_dir> <out_dir> [samples] [width] [height] [view ...]"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = Path(sys.executable)   # run this script with the render environment's python (README §2)
mesh, out = Path(sys.argv[1]), Path(sys.argv[2])
samples = sys.argv[3] if len(sys.argv) > 3 else "64"
W = sys.argv[4] if len(sys.argv) > 4 else "1400"
H = sys.argv[5] if len(sys.argv) > 5 else "788"
views = sys.argv[6:] or ["hero", "scanplane", "undock", "m-hero", "m-station", "m-carry", "m-lift", "m-aisle",
                         "elev-a", "m-elev-b", "loop-sf02-scanner", "loop-sf02-bumper", "loop-sf03", "loop-sf04", "m-loop-sf11", "m-loop-sf12"]
SPRITES = {"sprite": "cfg001-top.png", "m-sprite": "cfg002-stowed-top.png", "m-carry-sprite": "cfg002-carry-top.png"}   # written to <out_dir>/../sprites, no band

CAPTIONS = {
  "hero": ("CFG-001 base: the MMP platform from upstream's full-assembly STEP (1,983 parts)",
           "Chassis, cover, panels, wheels and castors as modelled; materials from part names (the STEP carries no colours). The electronics inside are upstream's 2.0 set, not the Gate A unit's."),
  "scanplane": ("GAP-14: a 0.15 m carton below the LiDAR scan plane (0.222 m, RPLIDAR S3 per the BOM)",
                "The cyan beams and rim are the scan plane. The low carton is invisible to every software layer; the tall one is seen. SR-02.03 asks for detection down to 0.3 m, which only a bumper or a second plane gives."),
  "undock": ("GAP-35 / DQ-018 A: the undock reverse, 0.7 m on odometry, rear sector masked",
             "The red strip is the blind reverse path toward the dock. Since DQ-018 A reverse is at 0.05 m/s under the rear bumper; the bumper overtravel covers the 7 to 17 mm stopping distance (WP-S-04 §4.3)."),
  "m-hero": ("CFG-002, the 2.0 mobile manipulator: base from CAD; lift, profile and head from documented dimensions; arms from the OpenArm 2.0 description",
             "Approximation: the DOLD column section, carriage and brackets are drawn from the general-arrangement page (supplier CAD not public). Arm meshes and joint tree are upstream's official package."),
  "m-station": ("H-13 / IS-13: a person at the station shelf while an arm reaches (SF-11 monitored stop, DQ-021 A)",
                "Lift extended to 1.35 m shoulder height. The amber ring is the workspace boundary of SR-11.02: arm reach about 0.6 m (from the description's joint offsets) plus 0.48 m of walk during a 0.3 s stop."),
  "m-carry": ("H-13 / IS-15: carrying in the carry pose at 0.3 m/s, a person crossing ahead (SF-10, SF-02 carry field)",
              "The cyan patch is field set FS-4 of WP-S-04 §4.1, 0.95 m braked at 1 m/s². The arms and tote widen the footprint the field must cover (CA-07, SR-02.10)."),
  "m-lift": ("H-15 / IS-14: lift moving with a person beside the column (SF-12 interlock, keep-clear zone)",
             "The amber ring is the keep-clear zone of SR-12.03 around the column; the lift moves at 18 mm/s and stops within 200 ms (3.6 mm) of a demand (WP-S-04 §4.5)."),
  "m-aisle": ("H-01 / IS-01: a person crossing the aisle ahead at navigation speed (SF-02 protective stop)",
              "The cyan patch is field set FS-1b of WP-S-04 §4.1: 1.09 m on the fast-coast planning case. On the slow coast it would be 3.8 m; the measurement of WP-V-02 decides."),
  "elev-a": ("WP-S-04 Figure 4-2, panel A as a render: the scan plane against what is on the floor",
             "Orthographic side view; the heights are drawn on at the camera's scale. The 0.15 m carton sits below the 0.222 m plane and is unseen by every software layer (GAP-14); the 0.30 m carton and a standing adult's legs are cut by it. SR-02.03's 0.30 m is the band."),
  "m-elev-b": ("WP-S-04 Figure 4-2, panel B as a render: CFG-002 envelope, arm workspace and lift keep-clear, lift extended 0.35 m",
               "Orthographic side view. Reach 0.6 m is a planning value from the description package's joint offsets; the 1.08 m boundary adds 0.48 m of walk at a 0.3 s stop (the arm's stopping time is TBC); the keep-clear radius is assumed. Column section, carriage and brackets are drawn, not modelled."),
  "loop-sf02-scanner": ("WP-S-04 Figure 2-1 at standstill: SF-02 by the scanner, field set FS-1b, fast-coast planning case",
                        "The person who entered the 1.09 m field has walked 0.91 m at 1.6 m/s while the robot travelled 0.034 m reacting and 0.040 m coasting; the gap at standstill is the tolerance Z = 0.10 m. On the slow coast the same picture needs a 3.81 m field."),
  "loop-sf02-bumper": ("WP-S-04 Figure 2-2 at standstill: SF-02 by the rear bumper, reversing at 0.05 m/s toward the dock",
                       "The bumper detects by contact: 0.0045 m of travel in the 90 ms reaction, then 2.5 to 12.5 mm of coast; the edge's 20 to 40 mm overtravel (TBC) absorbs the 7 to 17 mm. Above about 0.1 m/s on a slow coast it would not, which is why the reverse limit is a safety parameter."),
  "loop-sf03": ("WP-S-04 Figure 2-3 at standstill: SF-03 trips at the 0.25 m/s channel 1 ceiling, field set FS-1b sized for 0.20 m/s",
                "At the ceiling the fast coast needs 1.28 m of field (CK-1b) and FS-1b gives 1.09 m: the amber strip is the 0.19 m shortfall, and in the planning case the person reaches the robot as it stops. The ceiling and the trip threshold, not the field, bound this fault case (§5)."),
  "loop-sf04": ("WP-S-04 Figure 2-4 at standstill: SF-04 fault path, channel 1 dead with PWM applied, the hardware watchdog trips the chain at 1.07 s",
                "The ruler beside the robot: 0.21 m driven at 0.20 m/s with no command (red), then the 0.04 m fast coast (amber). The scanner path of SF-02 is still live through channel 2, so a person ahead is still protected; what this path bounds is how far a faulty drive carries the robot."),
  "m-loop-sf11": ("WP-S-04 Figure 2-5 at standstill: SF-11, the arm stopped as a person reaches the reach radius",
                  "The person crossed the 1.08 m workspace ring and walked 0.48 m during the 0.17 s reaction and the 0.13 s assumed arm stop; they stand 0.6 m from the shoulder axis as the arm reaches standstill. The arm's stopping time is TBC (WP-C-01 OI-6); a longer stop moves the ring out."),
  "m-loop-sf12": ("WP-S-04 Figure 2-6 at standstill: SF-12, the lift stopped as a person reaches the column",
                  "The person stepped onto the 0.55 m keep-clear ring (radius assumed) and walked 0.27 m in the 0.17 s reaction, plus the lift brake's time (TBC): they are at the column's side when the lift stops, 3 mm after the demand. The ring's radius, not the lift's speed, is the sizing question."),
}

out.mkdir(parents=True, exist_ok=True)
for v in views:
  if v in SPRITES:
    png = out.parent / "sprites" / SPRITES[v]
    png.parent.mkdir(parents=True, exist_ok=True)
  else:
    png = out / f"{v}.png"
  r = subprocess.run([str(PY), "-I", str(HERE / "render_amr.py"), str(mesh), str(png), samples, W, H, v], capture_output=True, text=True)
  tail = [l for l in r.stdout.splitlines() if l.startswith(("rendered", "arm fingertips", "overlap check", "sprite"))]
  print(v, "->", " | ".join(tail[-2:]) if tail else r.stderr[-400:], flush=True)
  if v in SPRITES:
    continue
  title, caption = CAPTIONS.get(v, (v, ""))
  subprocess.run([str(PY), "-I", str(HERE / "band.py"), str(png), str(out / f"openamrobot-{v}.jpg"), title, caption], check=True)
print("done")
