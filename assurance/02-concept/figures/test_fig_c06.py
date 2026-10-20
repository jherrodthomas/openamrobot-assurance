#!/usr/bin/env python3
"""Self-tests for fig_c06.py: source tables read, scenes and misuses resolve, the distance formula behaves, SVGs well-formed."""
from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

import fig_c06


class TestFigC06(unittest.TestCase):
  def setUp(self):
    self.src = fig_c06.load_source()

  def test_source_tables(self):
    self.assertEqual(len(self.src["scenes"]), 15)
    self.assertEqual(len(self.src["misuse"]), 16)
    self.assertEqual(fig_c06.check_source(self.src), [])

  def test_parameters_have_numbers(self):
    for k in ("K", "t_r", "Z"):
      self.assertIsNotNone(fig_c06._num(self.src["params"][k]), k)

  def test_walking_person_dominates(self):
    # at the navigation speed the person's walk during the stop exceeds the robot's own travel for any t_b > 0
    K, t_r = fig_c06._num(self.src["params"]["K"]), fig_c06._num(self.src["params"]["t_r"])
    for tb in (0.2, 0.5, 1.0, 2.0):
      self.assertGreater(K * (t_r + tb), 0.20 * t_r + 0.20 * tb / 2.0)

  def test_hot_cell_not_empty(self):
    hot = [k for k, m in self.src["misuse"].items() if m["likelihood"] == "H" and m["consequence"] == "S2"]
    self.assertGreaterEqual(len(hot), 3)

  def test_svgs_well_formed(self):
    for name, fn in fig_c06.OUTPUTS.items():
      root = ET.fromstring(fn(self.src))
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(fn(self.src), fn(self.src), name)


if __name__ == "__main__":
  unittest.main()
