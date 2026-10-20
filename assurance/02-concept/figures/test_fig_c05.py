#!/usr/bin/env python3
"""Self-tests for fig_c05.py: the §5 allocation rows are the rated rows of WP-C-03 §5, every measure cited is in the
WP-C-03 §6 register and the two agree on which hazard each measure reduces, no row rated c or higher rests on
information for use alone, the residual classes are the five of §1.1, the CFG-002 rows are open, the SVG is
well-formed."""
from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

import fig_c05


class TestFigC05(unittest.TestCase):
  def setUp(self):
    self.src = fig_c05.load_source()

  def test_source_is_consistent(self):
    self.assertEqual(fig_c05.check_source(self.src), [])

  def test_rows_are_the_rated_rows(self):
    self.assertEqual([r["label"] for r in self.src["rows"]], [r["label"] for r in self.src["rated"]])
    self.assertEqual(len(self.src["rows"]), 25)
    self.assertEqual(sorted({r["hazard"] for r in self.src["rows"]}), self.src["hazards"])

  def test_register_has_the_three_new_design_measures(self):
    for mid in ("DM-08", "DM-09", "DM-10"):
      self.assertIn(mid, self.src["register"], mid)
      self.assertEqual(self.src["register"][mid]["kind"], "DM")

  def test_no_s2_row_on_information_for_use_alone(self):
    for r in self.src["rows"]:
      if r["plr"] in ("c", "d", "e"):
        self.assertTrue(r["steps"][0]["measures"] or r["steps"][1]["measures"], r["label"])

  def test_residual_classes(self):
    for r in self.src["rows"]:
      self.assertTrue(r["classes"], r["label"])
      for c in r["classes"]:
        self.assertIn(c, fig_c05.CLASSES, r["label"])
    excluded = [r for r in self.src["rows"] if r["plr"] == "excluded"]
    self.assertEqual(len(excluded), 1)
    self.assertEqual(excluded[0]["classes"], ["E"])

  def test_cfg_002_rows_are_open(self):
    cfg2 = [r for r in self.src["rows"] if r["cfg2"]]
    self.assertEqual(len(cfg2), 5)
    for r in cfg2:
      self.assertEqual(r["classes"][0], "O", r["label"])
    for r in self.src["rows"]:
      if not r["cfg2"]:
        self.assertNotEqual(r["classes"][0], "O", r["label"])

  def test_step_three_is_information_only(self):
    for r in self.src["rows"]:
      for mid in r["steps"][2]["measures"]:
        self.assertTrue(mid.startswith("IFU-"), r["label"])

  def test_svg_well_formed(self):
    for name, fn in fig_c05.OUTPUTS.items():
      root = ET.fromstring(fn(self.src))
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(fn(self.src), fn(self.src), name)


if __name__ == "__main__":
  unittest.main()
