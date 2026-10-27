#!/usr/bin/env python3
"""Self-tests for evaluate.py on synthetic traces (no simulator): footprint geometry and clearance, contact, how far
the robot advanced, the stop after a fault, reverse speed, per-target predictions, the plant calibration, and that
the committed results are current and show what the record predicts."""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "harness"))

import calibrate  # noqa: E402
import evaluate  # noqa: E402
import world  # noqa: E402

FP = [[0.415, 0.19], [0.415, -0.19], [0.315, -0.29], [-0.290, -0.29], [-0.390, -0.19], [-0.390, 0.19], [-0.290, 0.29], [0.315, 0.29]]


def trace(xs, dt=0.05, yaw=0.0):
  return {"footprint": FP, "rows": [{"t": round(i * dt, 3), "x": x, "y": 0.0, "yaw": yaw, "action": 0} for i, x in enumerate(xs)]}


class TestGeometry(unittest.TestCase):
  def test_clearance_box_ahead(self):
    fp = evaluate.footprint_world(FP, 0.0, 0.0, 0.0)
    box = {"shape": "box", "size": [0.30, 0.40, 0.15], "pose": [1.40, 0.0, 0.075]}
    self.assertAlmostEqual(evaluate.clearance(fp, box), 1.40 - 0.15 - 0.415, places=6)

  def test_overlap_is_zero(self):
    fp = evaluate.footprint_world(FP, 1.0, 0.0, 0.0)
    box = {"shape": "box", "size": [0.30, 0.40, 0.15], "pose": [1.40, 0.0, 0.075]}
    self.assertEqual(evaluate.clearance(fp, box), 0.0)

  def test_cylinder_behind(self):
    fp = evaluate.footprint_world(FP, 0.0, 0.0, 0.0)
    person = {"shape": "cylinder", "size": [0.15, 1.7], "pose": [-1.04, 0.0, 0.85]}
    self.assertAlmostEqual(evaluate.clearance(fp, person), 1.04 - 0.15 - 0.390, places=6)

  def test_rotation(self):
    fp = evaluate.footprint_world(FP, 0.0, 0.0, math.pi / 2)
    self.assertAlmostEqual(max(p[1] for p in fp), 0.415, places=6)


class TestMetrics(unittest.TestCase):
  spec_box = {"id": "T", "obstacles": [{"shape": "box", "size": [0.30, 0.40, 0.15], "pose": [1.40, 0.0, 0.075]}]}

  def test_contact_detected(self):
    xs = [min(0.01 * i, 0.84) for i in range(200)]   # footprint front reaches 1.255 = box face at x 0.84
    m = evaluate.metrics(self.spec_box, trace(xs))
    self.assertIsNotNone(m["contact_at_s"])
    self.assertEqual(evaluate.outcome({"property": "no_contact"}, m), "violated")

  def test_stop_short_of_box(self):
    xs = [min(0.01 * i, 0.60) for i in range(200)]
    m = evaluate.metrics(self.spec_box, trace(xs))
    self.assertIsNone(m["contact_at_s"])
    self.assertEqual(evaluate.outcome({"property": "no_contact"}, m), "holds")

  def test_stop_after_fault(self):
    xs = [0.01 * i if i < 100 else 0.99 + 0.005 * min(i - 99, 20) for i in range(200)]   # 0.2 m/s, slows, stops at 1.09
    spec = {"id": "T", "faults": [{"kind": "scan_dropout", "at": 4.0}]}
    m = evaluate.metrics(spec, trace(xs))
    self.assertIsNotNone(m["stopped_at_s"])
    self.assertAlmostEqual(m["travel_after_fault_m"], 1.09 - 0.80, delta=0.02)
    self.assertEqual(evaluate.outcome({"property": "stops_after_fault", "limit_m": 0.25}, m), "violated")
    self.assertEqual(evaluate.outcome({"property": "stops_after_fault", "limit_m": 0.35}, m), "holds")

  def test_never_stops(self):
    spec = {"id": "T", "faults": [{"kind": "scan_dropout", "at": 4.0}]}
    m = evaluate.metrics(spec, trace([0.01 * i for i in range(200)]))
    self.assertIsNone(m["stopped_at_s"])
    self.assertEqual(evaluate.outcome({"property": "stops_after_fault", "limit_m": 10}, m), "violated")

  def test_fault_while_standing_is_not_exercised(self):
    spec = {"id": "T", "faults": [{"kind": "scan_dropout", "at": 4.0}]}
    m = evaluate.metrics(spec, trace([0.0] * 200))
    self.assertEqual(evaluate.outcome({"property": "stops_after_fault", "limit_m": 0.25}, m), "not exercised")
    self.assertEqual(evaluate.outcome({"property": "advances", "min_m": 0.30}, m), "violated")

  def test_advances(self):
    m = evaluate.metrics({"id": "T"}, trace([-0.005 * i for i in range(100)]))
    self.assertEqual(evaluate.outcome({"property": "advances", "min_m": 0.30}, m), "holds")

  def test_prediction_per_target(self):
    self.assertEqual(evaluate.per_target("holds", "bl-001"), "holds")
    self.assertEqual(evaluate.per_target({"bl-001": "violated", "upstream-main": "holds"}, "upstream-main"), "holds")

  def test_scenarios_predict_every_target(self):
    targets = set(evaluate.load_pins()["targets"])
    for s in evaluate.yaml.safe_load(evaluate.SCENARIOS.read_text(encoding="utf-8"))["scenarios"]:
      for c in s["checks"]:
        for key in ("expected", "why"):
          if isinstance(c[key], dict):
            self.assertEqual(set(c[key]), targets, f"{s['id']} {c['property']} {key}")
        for t in targets:
          self.assertIn(evaluate.per_target(c["expected"], t), ("holds", "violated", "not exercised"))

  def test_reverse_speed(self):
    m = evaluate.metrics({"id": "T"}, trace([-0.005 * i for i in range(100)]))   # 0.10 m/s backwards
    self.assertAlmostEqual(m["max_reverse_mps"], 0.10, places=2)
    self.assertEqual(evaluate.outcome({"property": "reverse_speed_le", "limit_mps": 0.05}, m), "violated")


class TestHarness(unittest.TestCase):
  def test_calibration_replaces_and_guards(self):
    urdf = ('<robot><gazebo><plugin filename="gz-sim-diff-drive-system" name="gz::sim::systems::DiffDrive">'
            '<wheel_separation>0.400</wheel_separation><max_linear_velocity>1.0</max_linear_velocity></plugin></gazebo></robot>')
    out, notes = calibrate.calibrate(urdf, {"wheel_separation": (0.46, 0.400), "max_linear_velocity": (0.71, 1.0)})
    self.assertIn("<wheel_separation>0.46</wheel_separation>", out)
    self.assertEqual(len(notes), 2)
    with self.assertRaises(ValueError):
      calibrate.calibrate(urdf, {"wheel_separation": (0.46, 0.4075)})

  def test_sensor_override_replaces_and_guards(self):
    urdf = ('<robot><sensor name="lidar_sensor" type="gpu_lidar"><lidar><scan><horizontal><min_angle>-3.14</min_angle></horizontal>'
            '</scan><range><min>0.40</min><max>10.0</max></range></lidar></sensor></robot>')
    o = {"sensor": "lidar_sensor", "element": "range/min", "value": 0.05, "upstream": 0.40}
    out, note = calibrate.override_sensor(urdf, o)
    self.assertIn("<min>0.05</min><max>10.0</max>", out)
    self.assertIn("<min_angle>-3.14</min_angle>", out)
    self.assertEqual(note, "lidar_sensor range/min: 0.4 -> 0.05")
    with self.assertRaises(ValueError):
      calibrate.override_sensor(urdf, {**o, "upstream": 0.15})

  def test_plant_file_parses(self):
    plant = calibrate.load_plant(str(HERE / "plant.yaml"))
    self.assertEqual(plant["wheel_separation"], (0.46, 0.400))
    self.assertEqual(len(plant), 8)

  def test_world_keeps_upstream_systems(self):
    up = '<sdf><world name="w"><plugin filename="a" name="A"></plugin><plugin filename="s" name="S"><render_engine>ogre2</render_engine></plugin><model name="wall"/></world></sdf>'
    w = world.world(up, [{"name": "b", "shape": "box", "size": [1, 1, 1], "pose": [1, 0, 0.5]}], "t")
    self.assertIn("ogre2", w)
    self.assertNotIn('name="wall"', w)
    self.assertIn('<model name="b">', w)


class TestCommittedResults(unittest.TestCase):
  def test_results_current_and_predictions_shown(self):
    if not any(evaluate.TRACES.glob("*/*.trace.json")):
      self.skipTest("no committed traces")
    res = evaluate.evaluate(evaluate.TRACES)
    for p, text in evaluate.outputs(res, evaluate.TRACES).items():
      self.assertEqual(p.read_text(encoding="utf-8"), text, f"{p.name} is stale")
    for sid, t, c in evaluate.all_checks(res):
      self.assertTrue(c["pass"], f"{sid} on {t} {c['property']}: predicted {c['expected']}, observed {c['outcome']}")


if __name__ == "__main__":
  unittest.main()
