#!/usr/bin/env python3
"""Self-tests for fig_s02.py: every requirement row is read with its eight attributes, the blocks are the twelve
functions plus common and security, the per-function PLr agrees with WP-C-04 §2, the CFG-002 functions carry only
CFG-002 rows, every traced hazard exists in WP-C-03 §4, the §18 table matches the rows, the SVGs are well-formed."""
from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

import fig_s02


class TestFigS02(unittest.TestCase):
  def setUp(self):
    self.src = fig_s02.load_source()

  def test_source_is_consistent(self):
    self.assertEqual(fig_s02.check_source(self.src), [])

  def test_blocks_and_counts(self):
    blocks = sorted({r["block"] for r in self.src["rows"].values()})
    self.assertEqual(blocks, sorted(fig_s02.BLOCKS))
    self.assertEqual(len(self.src["functions"]), 12)
    self.assertGreaterEqual(len(self.src["order"]), 80)
    self.assertEqual(len(self.src["order"]), len(set(self.src["order"])))

  def test_every_row_has_eight_attributes(self):
    for sid, r in self.src["rows"].items():
      self.assertEqual(r["ncells"], 8, sid)
      self.assertTrue(r["types"], sid)
      self.assertTrue(r["verif"], sid)
      self.assertIn(r["config"], fig_s02.CONFIGS, sid)
      self.assertTrue(r["trace"], sid)

  def test_function_plr_matches_wp_c04(self):
    for sf, f in self.src["functions"].items():
      self.assertEqual(fig_s02._block_plr(self.src, sf[3:]), f["plr"], sf)
    self.assertEqual(fig_s02._block_plr(self.src, "05"), "d", "SF-05 was raised to d (WP-C-04 v0.2)")
    self.assertEqual(fig_s02._block_plr(self.src, "90"), "—", "security rows carry no PL")

  def test_cfg_002_functions_only_have_cfg_002_rows(self):
    for b in ("10", "11", "12"):
      self.assertEqual({r["config"] for r in fig_s02._block_rows(self.src, b)}, {"CFG-002"}, b)
    for b in ("01", "02", "03", "04", "05", "06", "07", "08", "09"):
      self.assertIn("both", {r["config"] for r in fig_s02._block_rows(self.src, b)}, b)

  def test_traced_hazards_exist(self):
    self.assertEqual(len(self.src["hazards"]), 15)
    for sid, r in self.src["rows"].items():
      for h in r["trace"]:
        self.assertIn(h, self.src["hazards"], sid)

  def test_security_block_is_sr_90(self):
    self.assertIn("SR-90.01", self.src["rows"])
    self.assertEqual(self.src["rows"]["SR-10.01"]["section"], "10", "SR-10 is SF-10 since v0.3, not security")

  def test_cited_requirements_exist(self):
    for sid in self.src["cited"]:
      self.assertIn(sid, self.src["rows"], sid)

  def test_svgs_well_formed(self):
    for name, fn in fig_s02.OUTPUTS.items():
      root = ET.fromstring(fn(self.src))
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(fn(self.src), fn(self.src), name)
      self.assertEqual(root.attrib["width"], "1040", name)


if __name__ == "__main__":
  unittest.main()
