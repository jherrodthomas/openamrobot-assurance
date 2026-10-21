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
views = sys.argv[6:] or ["hero", "scanplane", "undock", "m-hero", "m-station", "m-carry", "m-lift", "m-aisle"]

CAPTIONS = {
  "hero": ("CFG-001 base: the MMP platform from upstream's full-assembly STEP (1,983 parts)",
           "Chassis, cover, panels, wheels and castors as modelled; materials from part names (the STEP carries no colours). The electronics inside are upstream's 2.0 set, not the Gate A unit's."),
  "scanplane": ("GAP-14: a 0.15 m carton below the LiDAR scan plane (0.222 m, RPLIDAR S3 per the BOM)",
                "The cyan beams and rim are the scan plane. The low carton is invisible to every software layer; the tall one is seen. SR-02.03 asks for detection down to 0.3 m, which only a bumper or a second plane gives."),
  "undock": ("GAP-35 / DQ-018 A: the undock reverse, 0.7 m on odometry, rear sector masked",
             "The red strip is the blind reverse path toward the dock. Since DQ-018 A reverse is at 0.05 m/s under the rear bumper; the bumper overtravel covers the 6 to 16 mm stopping distance (WP-S-04 §4.3)."),
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
}

out.mkdir(parents=True, exist_ok=True)
for v in views:
  png = out / f"{v}.png"
  r = subprocess.run([str(PY), "-I", str(HERE / "render_amr.py"), str(mesh), str(png), samples, W, H, v], capture_output=True, text=True)
  tail = [l for l in r.stdout.splitlines() if l.startswith(("rendered", "arm fingertips"))]
  print(v, "->", tail[-1] if tail else r.stderr[-400:])
  title, caption = CAPTIONS.get(v, (v, ""))
  subprocess.run([str(PY), "-I", str(HERE / "band.py"), str(png), str(out / f"openamrobot-{v}.jpg"), title, caption], check=True)
print("done")
