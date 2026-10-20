#!/usr/bin/env python3
"""Self-tests for fig_s04.py: the conventions and the scanner-path reaction time are read, every budget row adds up
and sits inside its target, every field-set row and stopping-distance row agrees with the formula, the person's
walk dominates the field length, the SVG is well-formed."""
from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

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

  def test_svg_well_formed(self):
    for name, fn in fig_s04.OUTPUTS.items():
      root = ET.fromstring(fn(self.src))
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(fn(self.src), fn(self.src), name)


if __name__ == "__main__":
  unittest.main()
