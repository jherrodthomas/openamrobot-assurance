#!/usr/bin/env python3
"""Self-tests for fig_c01.py: the source tables are read, the structural facts resolve, and the SVGs are well-formed."""
from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

import fig_c01


class TestFigC01(unittest.TestCase):
  def setUp(self):
    self.src = fig_c01.load_source()

  def test_source_tables(self):
    self.assertEqual(len(self.src["elements"]), 10)
    self.assertEqual(len(self.src["elements2"]), 10)
    self.assertEqual(len(self.src["interfaces"]), 8)
    self.assertEqual(len(self.src["modes"]), 7)

  def test_structural_facts_resolve(self):
    self.assertEqual(fig_c01.check_source(self.src), [])

  def test_svgs_are_well_formed_and_labelled(self):
    for name, fn in fig_c01.OUTPUTS.items():
      root = ET.fromstring(fn(self.src))
      self.assertTrue(root.tag.endswith("svg"), name)
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)

  def test_every_interface_is_drawn(self):
    out = fig_c01.fig_ibd(self.src) + fig_c01.fig_context(self.src)
    for iid in self.src["interfaces"]:
      self.assertIn(iid, out)

  def test_deterministic(self):
    for name, fn in fig_c01.OUTPUTS.items():
      self.assertEqual(fn(self.src), fn(self.src), name)


if __name__ == "__main__":
  unittest.main()
