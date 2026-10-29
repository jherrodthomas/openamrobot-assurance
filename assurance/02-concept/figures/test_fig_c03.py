#!/usr/bin/env python3
"""Self-tests for fig_c03.py: the source tables are read, every rated row agrees with the risk graph, every
measure reduces a listed hazard, the hazards rated d have a safety function, the SVGs are well-formed; the risk
sheets: every measure has a state, every high-risk row has a sheet, the spreadsheet is a valid workbook and is
byte-for-byte reproducible."""
from __future__ import annotations

import io
import unittest
import xml.etree.ElementTree as ET
import zipfile

import fig_c03
import fig_c03_sheets as sheets


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


class TestSheets(unittest.TestCase):
  def setUp(self):
    self.text = fig_c03.SOURCE.read_text(encoding="utf-8")
    self.d = sheets.load(self.text, fig_c03._table, fig_c03._clean)
    self.out = fig_c03.all_outputs(fig_c03.load_source())

  def test_sources_agree(self):
    self.assertEqual(sheets.check(self.d), [])

  def test_every_measure_has_a_state(self):
    self.assertEqual(len(self.d["measures"]), 28)
    for m in self.d["measures"].values():
      self.assertIn(m["state"], sheets.STATES, m["id"])

  def test_high_risk_rows(self):
    high = sheets.high_rows(self.d)
    self.assertEqual(len(high), 12)
    self.assertTrue(all(r["pl"] in ("d", "e") or r["graph"] == "d" for r in high))
    self.assertTrue(any(r["pl"] == "e" for r in high), "the excluded public-floor row has a sheet")
    cards = [p for p in self.out if p.name.endswith("-card.svg")]
    self.assertEqual(len(cards), len(high))
    annex = self.out[sheets.ANNEX]
    for p in cards:
      self.assertIn(f"figures/{p.name}", annex)

  def test_every_rated_row_is_on_the_worksheet(self):
    ws = self.out[fig_c03.HERE / "fig-c03-5-2-worksheet.svg"]
    for r in self.d["rows"]:
      self.assertIn(r["hazard"], ws)

  def test_new_svgs_well_formed(self):
    for p, out in self.out.items():
      if p.suffix == ".svg":
        root = ET.fromstring(out)
        self.assertIn("title", [c.tag.split("}")[-1] for c in root], p.name)

  def test_workbook(self):
    data = self.out[sheets.XLSX]
    self.assertEqual(data, fig_c03.all_outputs(fig_c03.load_source())[sheets.XLSX], "reproducible")
    z = zipfile.ZipFile(io.BytesIO(data))
    self.assertIn("xl/workbook.xml", z.namelist())
    for name in z.namelist():
      if name.endswith(".xml") or name.endswith(".rels"):
        ET.fromstring(z.read(name))
    reg = z.read("xl/worksheets/sheet1.xml").decode()
    self.assertEqual(reg.count("<row "), 2 + len(self.d["rows"]))
    self.assertIn('state="frozen"', reg)
    self.assertIn("<autoFilter", reg)


if __name__ == "__main__":
  unittest.main()
