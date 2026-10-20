#!/usr/bin/env python3
"""Self-tests for fig_c02.py: the source tables are read, the matrix covers every task and zone, the SVGs are well-formed."""
from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

import fig_c02


class TestFigC02(unittest.TestCase):
  def setUp(self):
    self.src = fig_c02.load_source()

  def test_source_tables(self):
    self.assertEqual(sorted(self.src["zones"]), ["Z0", "Z1", "Z2", "Z3", "Z4", "Z5"])
    self.assertEqual(len(self.src["tasks"]), 8)

  def test_matrix_covers_tasks_and_zones(self):
    self.assertEqual(fig_c02.check_source(self.src), [])
    for tid, row in fig_c02.MATRIX.items():
      self.assertEqual(sorted(row), fig_c02.ZONE_ORDER, tid)
      for kind, _ in row.values():
        self.assertIn(kind, ("now", "sf", "no"))

  def test_only_the_test_area_is_permitted_now(self):
    for tid, row in fig_c02.MATRIX.items():
      for zid, (kind, _) in row.items():
        if kind == "now":
          self.assertEqual(zid, "Z1", f"{tid} permitted now outside Z1")

  def test_svgs_well_formed(self):
    for name, fn in fig_c02.OUTPUTS.items():
      root = ET.fromstring(fn(self.src))
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(fn(self.src), fn(self.src), name)


if __name__ == "__main__":
  unittest.main()
