#!/usr/bin/env python3
"""Self-tests for fig_c07.py: the threat and risk assessment is internally consistent and agrees with WP-C-03 and
WP-C-08; risks are likelihood x impact in the right band; the safety architecture never raises an impact; the
security level check lists exactly the gaps between the target of DQ-013 A and what the scenarios need; nothing
enters the safety chain from the network; the checker catches the faults it is meant to catch; the SVGs are
well-formed and deterministic."""
from __future__ import annotations

import copy
import unittest
import xml.etree.ElementTree as ET

import fig_c07


class TestFigC07(unittest.TestCase):
  def setUp(self):
    self.src = fig_c07.load_source()

  def test_source_is_consistent(self):
    self.assertEqual(fig_c07.check_source(self.src), [])

  def test_counts(self):
    self.assertEqual(len(self.src["actors"]), 5)
    self.assertEqual(len(self.src["zones"]), 5)
    self.assertEqual(len(self.src["conduits"]), 6)
    self.assertEqual(len(self.src["scenarios"]), 20)
    self.assertEqual([r["id"] for r in self.src["risk"]], [s["id"] for s in self.src["scenarios"]])

  def test_target_is_the_decided_one(self):
    # DQ-013 A: SL 2 for FR 1, 3, 5, 7; SL 1 for FR 2, 4, 6
    self.assertEqual(self.src["slt"], {"FR 1": 2, "FR 2": 1, "FR 3": 2, "FR 4": 1, "FR 5": 2, "FR 6": 1, "FR 7": 2})

  def test_bands(self):
    self.assertEqual(fig_c07.band(3), "low")
    self.assertEqual(fig_c07.band(4), "medium")
    self.assertEqual(fig_c07.band(8), "medium")
    self.assertEqual(fig_c07.band(9), "high")
    for r in self.src["risk"]:
      self.assertEqual(r["before"][0], r["l"] * r["i"], r["id"])
      self.assertEqual(r["after"][0], r["l_after"] * r["i_arch"], r["id"])
      self.assertLessEqual(r["i_arch"], r["i"], r["id"])

  def test_no_high_residual(self):
    self.assertFalse([r["id"] for r in self.src["risk"] if r["after"][1] == "high"])
    self.assertEqual({x["id"] for x in self.src["residual"]}, {"TS-07", "TS-12"})

  def test_fr2_finding(self):
    fr2 = sorted(x["id"] for x in self.src["slcheck"] if x["fr"] == "FR 2" and x["disposition"].startswith("Decision needed"))
    self.assertEqual(fr2, ["TS-01", "TS-04", "TS-05", "TS-11", "TS-14"])

  def test_safety_chain_has_no_inbound_data_conduit(self):
    for cd, v in self.src["conduits"].items():
      if v["to"] == "SZ-4":
        self.assertIn("commissioning", v["carries"], cd)
      if v["from"] == "SZ-4":
        self.assertIn("one way", v["carries"], cd)
    self.assertFalse([cd for cd, v in self.src["conduits"].items() if v["from"] == "SZ-1" and v["to"] in ("SZ-3", "SZ-4")])

  def test_checker_catches_a_wrong_product(self):
    bad = copy.deepcopy(self.src)
    bad["risk"][0]["before"] = (11, "high")
    self.assertTrue(any("before is" in e for e in fig_c07.check_source(bad)))

  def test_checker_catches_a_missing_gap(self):
    bad = copy.deepcopy(self.src)
    bad["slcheck"] = [x for x in bad["slcheck"] if x["id"] != "TS-14"]
    self.assertTrue(any("§7 misses TS-14" in e for e in fig_c07.check_source(bad)))

  def test_checker_catches_a_network_conduit_into_the_chain(self):
    bad = copy.deepcopy(self.src)
    bad["conduits"]["CD-9"] = {"from": "SZ-1", "to": "SZ-4", "carries": "a remote stop", "interfaces": [], "today": ""}
    self.assertTrue(any("CD-9" in e for e in fig_c07.check_source(bad)))

  def test_checker_catches_an_unknown_hazard(self):
    bad = copy.deepcopy(self.src)
    bad["scenarios"][0]["hazards"] = ["H-99"]
    self.assertTrue(any("H-99" in e for e in fig_c07.check_source(bad)))

  def test_svg_well_formed(self):
    for name, fn in fig_c07.OUTPUTS.items():
      out = fn(self.src)
      root = ET.fromstring(out)
      tags = [c.tag.split("}")[-1] for c in root]
      self.assertIn("title", tags, name)
      self.assertIn("desc", tags, name)
      self.assertEqual(out, fn(self.src), name)


if __name__ == "__main__":
  unittest.main()
