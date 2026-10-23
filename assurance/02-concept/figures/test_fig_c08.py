#!/usr/bin/env python3
"""Self-tests for fig_c08.py: the security level target is the one DQ-013 A decided; every component requirement that
applies at it is met, and §3 and §4 agree both ways; every requirement treats a scenario of WP-C-07, and the two
documents agree both ways on which treats which; every safety function of WP-C-03 has a row in §5; the SR-90
requirements of WP-S-02 are each met; the checker catches the faults it is meant to catch; the SVG is well-formed and
deterministic."""
from __future__ import annotations

import copy
import unittest
import xml.etree.ElementTree as ET

import fig_c08


class TestFigC08(unittest.TestCase):
  def setUp(self):
    self.src = fig_c08.load_source()

  def test_source_is_consistent(self):
    self.assertEqual(fig_c08.check_source(self.src), [])

  def test_target_is_the_decided_one(self):
    self.assertEqual(self.src["slt"], {"FR 1": 2, "FR 2": 1, "FR 3": 2, "FR 4": 1, "FR 5": 2, "FR 6": 1, "FR 7": 2})

  def test_every_applying_cr_is_met(self):
    for cr in self.src["crs"]:
      if cr["applies"] == "yes":
        self.assertTrue(cr["met_by"], cr["id"])
        self.assertLessEqual(cr["sl"], self.src["slt"][cr["fr"]], cr["id"])

  def test_pending_rows_wait_on_the_fr2_question(self):
    pending = [cr["id"] for cr in self.src["crs"] if cr["applies"].startswith("pending")]
    self.assertEqual(pending, ["CR 2.1 RE(1)", "CR 2.1 RE(2)"])
    self.assertTrue(all("DQ-025" in cr["applies"] for cr in self.src["crs"] if cr["applies"].startswith("pending")))

  def test_every_scenario_but_the_sensing_attack_is_treated(self):
    untreated = [ts for ts in self.src["scenarios"] if not self.src["treatments"].get(ts)]
    self.assertEqual(untreated, ["TS-13"])

  def test_every_safety_function_has_an_interface_row(self):
    self.assertEqual(sorted(self.src["sf_rows"]), self.src["sfs"])
    self.assertEqual(len(self.src["sfs"]), 12)

  def test_sr90_met(self):
    self.assertEqual(sorted(self.src["sr_rows"]), ["SR-90.01", "SR-90.02", "SR-90.03", "SR-90.04"])
    for sr, lst in self.src["sr_rows"].items():
      self.assertTrue(lst, sr)

  def test_checker_catches_a_one_way_trace(self):
    bad = copy.deepcopy(self.src)
    bad["csrs"][0]["treats"] = bad["csrs"][0]["treats"] + ["TS-20"]
    self.assertTrue(any("CSR-01: treats TS-20" in e for e in fig_c08.check_source(bad)))

  def test_checker_catches_an_unmet_cr(self):
    bad = copy.deepcopy(self.src)
    for cr in bad["crs"]:
      if cr["id"] == "CR 5.1":
        cr["met_by"] = []
    self.assertTrue(any("CR 5.1: applies, but no requirement meets it" in e for e in fig_c08.check_source(bad)))

  def test_checker_catches_an_unknown_safety_function(self):
    bad = copy.deepcopy(self.src)
    bad["csrs"][0]["sfs"] = ["SF-99"]
    self.assertTrue(any("SF-99" in e for e in fig_c08.check_source(bad)))

  def test_svg_well_formed(self):
    for name, fn in fig_c08.OUTPUTS.items():
      out = fn(self.src)
      root = ET.fromstring(out)
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(out, fn(self.src), name)


if __name__ == "__main__":
  unittest.main()
