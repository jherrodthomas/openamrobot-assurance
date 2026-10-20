#!/usr/bin/env python3
"""Tests for make_assets.py: well-formed SVG, the data lands in the figures, --check detects staleness."""
from __future__ import annotations

import sys
import tempfile
import unittest
import xml.dom.minidom
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_assets as ma


class RenderTests(unittest.TestCase):
  def test_every_figure_is_well_formed_svg(self):
    for name, s in ma.render_all().items():
      xml.dom.minidom.parseString(s)
      self.assertTrue(s.startswith("<svg"), name)
      self.assertIn("<title", s, name)
      self.assertIn("<desc", s, name)

  def test_data_lands_in_the_figures(self):
    figs = ma.render_all()
    for chip in ma.CHIPS:
      self.assertIn(chip, figs["hero.svg"])
    for name, _, question, _ in ma.STANDARDS:
      self.assertIn(question, figs["standards.svg"])
      self.assertIn(name.split(" ")[0], figs["standards.svg"])
    for _, title, _, _ in ma.LAYERS:
      self.assertIn(title, figs["architecture.svg"])
    for _, name, status, _ in ma.ROADMAP:
      self.assertIn(name, figs["roadmap.svg"])
      self.assertIn(status, figs["roadmap.svg"])
    for g, _, _ in ma.GATES:
      self.assertIn(f">{g}<", figs["lifecycle.svg"])
    self.assertIn("TODAY · " + ma.TODAY_PHASE, figs["lifecycle.svg"])

  def test_check_detects_staleness(self):
    with tempfile.TemporaryDirectory() as d:
      out = Path(d)
      self.assertEqual(ma.main(["--out", str(out)]), 0)
      figs = ma.render_all()
      for n in ma.NAMES:
        self.assertEqual((out / n).read_text(encoding="utf-8"), figs[n])
      (out / "hero.svg").write_text("stale", encoding="utf-8")
      stale = [n for n in ma.NAMES if (out / n).read_text(encoding="utf-8") != figs[n]]
      self.assertEqual(stale, ["hero.svg"])

  def test_committed_figures_are_current(self):
    self.assertEqual(ma.main(["--check"]), 0)


if __name__ == "__main__":
  unittest.main()
