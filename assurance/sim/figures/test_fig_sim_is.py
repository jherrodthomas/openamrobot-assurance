#!/usr/bin/env python3
"""Self-tests for fig_sim_is.py: the source tables read, the field formula holds, the kinematics end in a standstill,
every scene resolves to a WP-C-06 row and a WP-C-03 rating, the SVGs are well-formed and deterministic, and every
SMIL key-time list ends at 1 (a list that does not is silently ignored by browsers)."""
from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET

import fig_sim_is as f


class TestFigSimIs(unittest.TestCase):
  def setUp(self):
    self.src = f.load_source()

  def test_sources(self):
    self.assertEqual(f.check_source(self.src), [])
    self.assertEqual(len(self.src["scenes"]), 15)
    self.assertGreaterEqual(len(self.src["fields"]), 10)
    self.assertEqual(set(self.src["zones"]) >= {"Z1", "Z2", "Z3", "Z4", "Z5"}, True)

  def test_field_formula_matches_table(self):
    t_r = f.scanner_path(self.src)["t_r"] / 1000.0
    for fid in f.PLAN_FIELDS:
      row = self.src["fields"][fid]
      t_b, d_s, L = f.model(row["v"], row["a"], t_r, self.src["K"], self.src["Z"])
      self.assertAlmostEqual(L, row["L"], delta=0.011, msg=fid)
      self.assertAlmostEqual(t_b, row["t_b"], delta=0.006, msg=fid)

  def test_kinematics_end_in_standstill(self):
    for fid in ("FS-1b", "FS-2b", "FS-4"):
      k = f.kinematics(self.src, fid)
      self.assertGreater(k["t_s"], k["t_r"])
      travel_at_stop = f.robot_travel(k, k["t_s"], -0.5)
      self.assertAlmostEqual(f.robot_travel(k, k["t_s"] + 1.0, -0.5), travel_at_stop, places=9, msg=fid)
      self.assertAlmostEqual(travel_at_stop - f.robot_travel(k, 0.0, -0.5), k["d_r"] + k["d_b"], places=9, msg=fid)
      # the person's walk during the stop exceeds the robot's own travel: the term that sizes the field
      self.assertGreater(k["walk"], k["d_r"] + k["d_b"], fid)
    kb = f.kinematics(self.src, "FS-2b", "bumper")
    self.assertAlmostEqual(kb["t_r"], 0.09)

  def test_every_scene_builds_and_rests(self):
    self.assertEqual(len(f.SCENES), 15)
    for sid, sc in f.SCENES.items():
      if sc.get("still"):
        self.assertIn(sid, f.STILLS)
        continue
      s = f.build(self.src, sid)
      self.assertLess(s["T0"], 0.0, sid)
      self.assertGreater(s["T1"], 0.0, sid)
      last = s["robot"][-1]; before = s["robot"][-2]
      if sid != "IS-10":   # IS-10 ends with the robot driving on after the warning
        self.assertAlmostEqual(last[1], before[1], places=6, msg=f"{sid}: the robot still moves at the end of the loop")
        self.assertAlmostEqual(last[2], before[2], places=6, msg=sid)
      self.assertTrue(all(t0 < t1 for (t0, *_), (t1, *_) in zip(s["robot"], s["robot"][1:])), sid)
      self.assertGreaterEqual(min(s["dist"](t) for t in f.samples(s["T0"], s["T1"])), 0.0, sid)
      self.assertTrue(all(c in (f.C["teal"], f.C["red"], f.C["line"], f.C["dim"], f.C["amber"]) for _, c in s["states"]), sid)

  def test_demands_land_where_the_rows_say(self):
    s = f.build(self.src, "IS-01")
    self.assertAlmostEqual(s["t_d"], 0.0, delta=f.DT)
    s = f.build(self.src, "IS-04")
    self.assertAlmostEqual(min(s["dist"](t) for t in f.samples(s["T0"], s["T1"])), 0.0, places=6, msg="the bumper case is a contact")
    s = f.build(self.src, "IS-13")
    self.assertAlmostEqual(min(s["dist"](t) for t in f.samples(s["T0"], s["T1"])), 0.0, delta=0.02, msg="the ring is reach plus walk: no margin in the planning case")
    s = f.build(self.src, "IS-15")
    self.assertTrue(any(l.startswith("load reaches") and t is not None for t, l, _ in s["events"]))

  def test_scenes_resolve(self):
    for sid in f.SCENES:
      self.assertIn(sid, self.src["scenes"])
      if sid not in f.UNRATED:
        self.assertIsNotNone(f.rating_for(self.src, sid), sid)
      if f.SCENES[sid]["field"]:
        self.assertIn(f.SCENES[sid]["field"], self.src["fields"])

  def test_svgs_well_formed_and_deterministic(self):
    for name, fn in f.OUTPUTS.items():
      out = fn(self.src)
      root = ET.fromstring(out)
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(out, fn(self.src), name)
      self.assertIn(f.BAND, out, name)

  def test_smil_keytimes_end_at_one(self):
    for name, fn in f.OUTPUTS.items():
      if "anim" not in name:
        continue
      out = fn(self.src)
      lists = re.findall(r'keyTimes="([^"]+)"', out)
      self.assertGreater(len(lists), 5, name)
      for kt in lists:
        vals = [float(v) for v in kt.split(";")]
        self.assertEqual(vals[0], 0.0, kt)
        self.assertEqual(vals[-1], 1.0, kt)
        self.assertEqual(vals, sorted(vals), kt)
      for m in re.finditer(r'values="([^"]+)" keyTimes="([^"]+)"', out):
        self.assertEqual(len(m.group(1).split(";")), len(m.group(2).split(";")), m.group(0)[:80])


  def test_sprites_pinned_and_embedded(self):
    sp = self.src["sprites"]
    self.assertEqual(set(sp), set(f.SPRITES), "every pinned sprite file is present")
    for kind, v in sp.items():
      self.assertEqual(v["sha"], v["pin"], kind)
      self.assertEqual(v["ppm"], 250, kind)
      self.assertGreater(v["w"], 100, kind)
    plan = f.fig_plan(self.src)
    self.assertIn('id="sim-plan-sp-cfg001"', plan)
    self.assertIn('id="sim-plan-sp-cfg002-carry"', plan)
    self.assertGreaterEqual(plan.count('<use href="#sim-plan-sp-'), 3)
    self.assertIn('id="sim-is-01-sp-cfg001"', f.fig_loop(self.src, "IS-01"))
    self.assertIn('id="sim-is-15-sp-cfg002-carry"', f.fig_loop(self.src, "IS-15"))
    self.assertNotIn("<animate", f.fig_loop(self.src, "IS-07"))

  def test_fallback_footprint_without_sprites(self):
    src = dict(self.src, sprites={})
    self.assertNotIn("<image", f.fig_plan(src))
    self.assertIn("<circle", f.fig_plan(src))


if __name__ == "__main__":
  unittest.main()
