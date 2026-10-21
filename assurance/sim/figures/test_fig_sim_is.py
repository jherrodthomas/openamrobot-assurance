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
    for sid, sc in f.SCENES.items():
      k = f.kinematics(self.src, sc["field"])
      self.assertGreater(k["t_s"], k["t_r"])
      travel_at_stop = f.robot_travel(k, k["t_s"], sc["t0"])
      self.assertAlmostEqual(f.robot_travel(k, k["t_s"] + 1.0, sc["t0"]), travel_at_stop, places=9, msg=sid)
      self.assertAlmostEqual(travel_at_stop - f.robot_travel(k, 0.0, sc["t0"]), k["d_r"] + k["d_b"], places=9, msg=sid)
      # the person's walk during the stop exceeds the robot's own travel: the term that sizes the field
      self.assertGreater(k["walk"], k["d_r"] + k["d_b"], sid)

  def test_scenes_resolve(self):
    for sid in f.SCENES:
      self.assertIn(sid, self.src["scenes"])
      self.assertIsNotNone(f.rating_for(self.src, sid), sid)
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


if __name__ == "__main__":
  unittest.main()
