#!/usr/bin/env python3
"""Self-tests for fig_c03.py: the source tables are read, every rated row agrees with the risk graph, every
measure reduces a listed hazard, the hazards rated d have a safety function, the SVGs are well-formed."""
from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

import fig_c03


class TestFigC03(unittest.TestCase):
  def setUp(self):
    self.src = fig_c03.load_source()

  def test_source_tables(self):
    self.assertEqual(len(self.src["graph"]), 8)
    self.assertEqual(len(self.src["situations"]), 18)
    self.assertEqual(len(self.src["hazards"]), 15)
    self.assertEqual(len(self.src["rated"]), 25)
    self.assertEqual(fig_c03.check_source(self.src), [])

  def test_risk_graph_is_the_published_mapping(self):
    g = self.src["graph"]
    self.assertEqual(g[("S1", "F1", "P1")], "a")
    self.assertEqual(g[("S2", "F1", "P2")], "d")
    self.assertEqual(g[("S2", "F2", "P1")], "d")
    self.assertEqual(g[("S2", "F2", "P2")], "e")

  def test_every_rated_row_matches_the_graph(self):
    for r in self.src["rated"]:
      self.assertEqual(self.src["graph"][(r["S"], r["F"], r["P"])], r["graph"], r["label"])

  def test_the_e_row_is_excluded_not_argued_down(self):
    e_rows = [r for r in self.src["rated"] if r["graph"] == "e"]
    self.assertEqual(len(e_rows), 1)
    self.assertIn("excluded", e_rows[0]["adopted"].lower())

  def test_hazards_rated_d_have_a_safety_function(self):
    sf = {h for m in self.src["measures"] if m["group"] == "SF" for h in m["reduces"]}
    for hid in self.src["hazards"]:
      if fig_c03._adopted_pl(self.src["rated"], hid) == "d":
        self.assertIn(hid, sf, hid)

  def test_every_hazard_has_a_measure_beyond_information(self):
    covered = {h for m in self.src["measures"] if m["group"] != "IFU" for h in m["reduces"]}
    for hid in self.src["hazards"]:
      self.assertIn(hid, covered, hid)

  def test_every_situation_names_a_zone(self):
    for sid, s in self.src["situations"].items():
      self.assertTrue(fig_c03._zones_of(s["zone"]), sid)

  def test_svgs_well_formed(self):
    for name, fn in fig_c03.OUTPUTS.items():
      root = ET.fromstring(fn(self.src))
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(fn(self.src), fn(self.src), name)


if __name__ == "__main__":
  unittest.main()
