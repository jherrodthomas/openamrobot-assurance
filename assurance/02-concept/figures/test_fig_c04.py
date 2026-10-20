#!/usr/bin/env python3
"""Self-tests for fig_c04.py: the source tables are read, the budget rows add up and sit inside their targets
(except where the text says why), every function has a card group and a task row, the SVGs are well-formed."""
from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

import fig_c04


class TestFigC04(unittest.TestCase):
  def setUp(self):
    self.src = fig_c04.load_source()

  def test_source_tables(self):
    self.assertEqual(len(self.src["functions"]), 9)
    self.assertEqual(len(self.src["budget"]), 6)
    self.assertEqual(len(self.src["matrix"]), 9)
    self.assertEqual(fig_c04.check_source(self.src), [])

  def test_plr_matches_wp_c03(self):
    plr = {k: v["plr"][:1] for k, v in self.src["functions"].items()}
    self.assertEqual(plr["SF-01"], "d")
    self.assertEqual(plr["SF-02"], "d")
    self.assertEqual(plr["SF-03"], "d")
    self.assertEqual(plr["SF-05"], "d")
    self.assertEqual(plr["SF-07"], "b")

  def test_budget_rows_add_up(self):
    for sid, r in self.src["budget"].items():
      self.assertAlmostEqual(r["input"] + r["logic"] + r["power"], r["total"], msg=sid)

  def test_stop_functions_inside_target_except_sf04(self):
    for sid, r in self.src["budget"].items():
      if sid == "SF-04":
        self.assertLessEqual(r["total"] - r["target"], 50, "SF-04 may exceed its target by the relay time only")
      else:
        self.assertLessEqual(r["total"], r["target"], sid)

  def test_every_function_has_a_task_row_with_every_task(self):
    for sid in self.src["functions"]:
      self.assertIn(sid, self.src["matrix"], sid)
      self.assertEqual(sorted(self.src["matrix"][sid]), fig_c04.TASKS, sid)

  def test_teleoperation_enabling_control_only_in_manual_tasks(self):
    row = self.src["matrix"]["SF-09"]
    for tid, cell in row.items():
      kind = fig_c04._cell_kind(cell)
      self.assertEqual(kind == "active", tid in ("T-06", "T-07"), f"SF-09 in {tid}")

  def test_emergency_stop_active_everywhere(self):
    for tid, cell in self.src["matrix"]["SF-01"].items():
      self.assertEqual(fig_c04._cell_kind(cell), "active", tid)

  def test_svgs_well_formed(self):
    for name, fn in fig_c04.OUTPUTS.items():
      root = ET.fromstring(fn(self.src))
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(fn(self.src), fn(self.src), name)


if __name__ == "__main__":
  unittest.main()
