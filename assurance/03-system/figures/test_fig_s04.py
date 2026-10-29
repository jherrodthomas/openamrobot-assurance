#!/usr/bin/env python3
"""Self-tests for fig_s04.py: the conventions and the scanner-path reaction time are read, every budget row adds up
and sits inside its target, every field-set row and stopping-distance row agrees with the formula, the person's
walk dominates the field length, the §4.3 bumper distances and the §4.5 walk terms follow from the rows, every
loop diagram's rows exist, the elevation's copies of the Blender scene's dimensions agree with cfg002.py, and
every SVG is well-formed and deterministic."""
from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import fig_s04


class TestFigS04(unittest.TestCase):
  def setUp(self):
    self.src = fig_s04.load_source()

  def test_source_is_consistent(self):
    self.assertEqual(fig_s04.check_source(self.src), [])

  def test_conventions(self):
    self.assertEqual(self.src["K"], 1.6)
    self.assertEqual(self.src["Z"], 0.10)
    self.assertAlmostEqual(self.src["t_r"], 0.17)
    self.assertEqual(self.src["cases"], {"coast slow": 0.1, "coast fast": 0.5, "braked": 1.0})

  def test_budget_rows(self):
    sfs = {b["sf"] for b in self.src["budget"]}
    for sf in ("SF-01", "SF-02", "SF-03", "SF-04", "SF-06", "SF-09", "SF-10", "SF-11", "SF-12"):
      self.assertIn(sf, sfs)
    sf04 = [b for b in self.src["budget"] if b["sf"] == "SF-04"]
    self.assertEqual(len(sf04), 3, "SF-04 has the drive, contactor and fault paths")
    self.assertEqual(sorted(b["target"] for b in sf04), [200.0, 300.0, 1100.0])

  def test_field_rows_cover_every_set(self):
    ids = [f["id"] for f in self.src["fields"]]
    for prefix in ("FS-1", "FS-2", "FS-3", "FS-4", "CK-1", "CK-2"):
      self.assertTrue(any(i.startswith(prefix) for i in ids), prefix)
    for f in self.src["fields"]:
      self.assertIn(f["config"], ("CFG-001", "CFG-002"), f["id"])

  def test_the_walk_dominates(self):
    K, Z, t_r = self.src["K"], self.src["Z"], self.src["t_r"]
    for f in self.src["fields"]:
      t_b, d_s, L = fig_s04.model(f["v"], f["a"], t_r, K, Z)
      self.assertGreater(K * (t_r + t_b), d_s, f["id"])

  def test_loops_resolve_to_rows(self):
    keys = [lp["key"] for lp in fig_s04.LOOPS]
    self.assertEqual(len(keys), 6)
    self.assertEqual(len(set(keys)), 6)
    for lp in fig_s04.LOOPS:
      b = fig_s04.budget_row(self.src, lp["sf"], lp["match"])
      self.assertIsNotNone(b, lp["key"])
      self.assertLessEqual(b["tr"], b["target"], lp["key"])
      for fid in (lp.get("field"), lp.get("ceiling_row"), *lp.get("alts", ())):
        if fid:
          fig_s04.field_row(self.src, fid)

  def test_bumper_and_walk_terms_follow_from_the_rows(self):
    b = fig_s04.budget_row(self.src, "SF-02", "bumper")
    slow, fast = self.src["bumper_mm"]
    self.assertEqual(round((0.05 * b["tr"] / 1000 + 0.05 ** 2 / (2 * 0.1)) * 1000), slow)
    self.assertEqual(round((0.05 * b["tr"] / 1000 + 0.05 ** 2 / (2 * 0.5)) * 1000), fast)
    self.assertLess(slow, self.src["overtravel_mm"][0], "the slow-coast stop must sit inside the smallest overtravel")
    for t, d in self.src["walk_terms"]:
      self.assertAlmostEqual(self.src["K"] * t, d, delta=0.006)
    self.assertAlmostEqual(self.src["lift_mm_s"] * self.src["lift_stop"][0] / 1000, self.src["lift_stop"][1], delta=0.05)

  def test_ceiling_shortfall_is_what_figure_2_3_says(self):
    f = fig_s04.field_row(self.src, "FS-1b")
    ck = fig_s04.field_row(self.src, "CK-1b")
    self.assertEqual(f["v"], 0.20)
    self.assertEqual(ck["v"], self.src["ceiling"])
    self.assertGreater(ck["L"], f["L"], "a stop from the cap needs more field than FS-1b carries (OI-8)")

  def test_elevation_dimensions_match_the_blender_scene(self):
    cfg = (Path(__file__).resolve().parents[2] / "sim" / "blender" / "cfg002.py").read_text(encoding="utf-8")
    def const(name):
      return float(re.search(rf"^{name} = ([0-9.]+)", cfg, re.M).group(1))
    self.assertEqual(fig_s04.CFG002["plate_top"], const("PLATE_TOP"))
    self.assertEqual(fig_s04.CFG002["column_retracted"], const("COLUMN_RETRACTED"))
    self.assertEqual(fig_s04.CFG002["column_axis_x"], const("COLUMN_AXIS_X"))
    self.assertEqual(fig_s04.CFG002["arm_mount_x"], const("ARM_MOUNT_X"))
    self.assertEqual(fig_s04.CFG002["shoulder_z"], const("SHOULDER_Z"))
    self.assertEqual(fig_s04.CFG002["column_foreaft"], float(re.search(r"COLUMN_FOREAFT, COLUMN_LAT = ([0-9.]+)", cfg).group(1)))
    self.assertEqual(fig_s04.CFG002["profile"], tuple(float(v) for v in re.search(r"PROFILE = \(([^)]+)\)", cfg).group(1).split(",")))
    self.assertEqual(self.src["planes"], {"A1": 0.18, "S3": 0.222})
    self.assertEqual(self.src["envelope"], 1.7)

  def test_svg_well_formed(self):
    self.assertEqual(len(fig_s04.OUTPUTS), 8)
    for name, fn in fig_s04.OUTPUTS.items():
      out = fn(self.src)
      root = ET.fromstring(out)
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(out, fn(self.src), name)
      if name.startswith("fig-s04-2-") or name.endswith("elevation.svg"):
        self.assertIn(fig_s04.BAND, out, name)


if __name__ == "__main__":
  unittest.main()
