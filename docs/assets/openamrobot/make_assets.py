#!/usr/bin/env python3
"""Render the README figures of OpenAMRobot assurance as SVG.

Five figures, one style: hero.svg (banner), standards.svg (one question per standard), architecture.svg
(three layers and the assurance column), roadmap.svg (four phases, status from repository evidence) and
lifecycle.svg (the seven gates and where the project stands). Everything is drawn from the data at the top
of this file; nothing is drawn by hand, so a change to the data is a change to the figure and CI checks that
the committed copies match (`--check`).

Usage: python3 docs/assets/openamrobot/make_assets.py [--out DIR | --check]
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
NAMES = ("hero.svg", "standards.svg", "architecture.svg", "roadmap.svg", "lifecycle.svg")

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
C = {
  "bg1": "#10262B", "bg2": "#07151A", "panel": "#12303A", "panel2": "#0E2630", "stroke": "#1F4752",
  "amber": "#F2A33A", "amber_hi": "#FFD38A", "amber_lo": "#B8731C", "cyan": "#3FD3C6", "cyan_lo": "#1E8F86",
  "text": "#F2F6F7", "muted": "#93AEB5", "dim": "#5F7B82", "red": "#FF6B5C", "green": "#5FD38F", "white": "#FFFFFF",
}

# ------------------------------------------------------------------ data

TAGLINE = "Open mobile manipulation. Engineered for safety."
CHIPS = ["ISO 12100", "ISO 3691-4", "ISO 13849-1", "EN 60204-1", "IEC 62443", "Machinery Reg. (EU) 2023/1230"]

STANDARDS = [
  ("ISO 12100", "Risk assessment and reduction", "What could hurt someone, and how much risk reduction does it need?", "Machine limits, hazard identification, risk estimation, the three-step method"),
  ("ISO 3691-4", "Driverless industrial trucks and AMRs", "Which safety functions must a driverless machine have?", "Emergency stop, personnel detection, speed, braking, stability, operating zones"),
  ("ISO 13849-1 / -2", "Safety-related parts of control systems", "How reliable must the control system be, and how is that shown?", "Required Performance Level, categories, MTTFD, DCavg, CCF, validation"),
  ("EN 60204-1 · ISO 13850", "Electrical equipment, emergency stop", "Is the electrical installation safe, and does the E-stop work?", "Supply disconnection, overcurrent, bonding, stop categories, E-stop devices"),
  ("ISO 13855 · IEC 61496", "Safeguards and protective equipment", "Where may a person be relative to the robot?", "Approach speeds, safety distances, protective fields, type 3 scanners"),
  ("IEC 62443-4-1 / -4-2", "Cybersecurity", "What if someone attacks it?", "Secure development lifecycle, zones and conduits, security level target"),
  ("ISO/IEC TR 5469", "AI in safety functions", "How far can a learned component be trusted?", "Technology classes, usage levels; here: no safety function on a learned component"),
  ("UL 4600 · Machinery Reg.", "Safety case and conformity", "Is the whole argument convincing, and what does the law require?", "Claims, evidence, defeaters; Annex III requirements, Annex IV technical file"),
]

LAYERS = [
  ("LAYER 1 · INHERITED FROM OPENAMROBOT, HARDENED AS DEFENCE IN DEPTH", "ROS 2 functional stack", "Raspberry Pi 5 · no Performance Level claim",
   [("Nav2 planning and control", "inherited"), ("Velocity smoother", "inherited"), ("Collision monitor", "inherited"),
    ("Command arbiter (twist_mux)", "hardened"), ("Docking inside the envelope", "hardened"), ("Operator UI with authentication", "hardened"),
    ("SROS2, pinned builds", "hardened"), ("Learned policy, outside every safety function", "proposed")]),
  ("LAYER 2 · THE LAST SOFTWARE BEFORE THE MOTORS", "Teensy 4.0 firmware", "Hardened checker · no Performance Level claim in the first safety case",
   [("Command validation: finite, bounded, fresh", "hardened"), ("Hardware watchdog", "hardened"), ("Driver fault read-back", "hardened"),
    ("Encoder and stall plausibility", "hardened"), ("Debug paths armed, parameters bounded", "hardened"), ("Version, reset cause, calibration flag", "hardened")]),
  ("LAYER 3 · HARDWIRED SAFETY CHAIN, THE CHECKER OF LAST RESORT", "Safety-related control system", "PL d target · ISO 13849-1 · nothing in software can hold a contactor closed",
   [("Two-channel E-stops", "chain"), ("Safety relay with monitored reset", "chain"), ("Two contactors, mirror contacts", "chain"),
    ("Brakes engaged on power loss", "chain"), ("Safety scanner OSSDs", "chain"), ("Fuse and lockable disconnect", "chain")]),
]
ASSURANCE_COLUMN = ["Machine limits and risk assessment", "Safety functions and required PL", "SRP/CS architecture and PL calculation",
                    "Stopping, detection and E-stop validation", "Cybersecurity threat assessment", "Safety case and technical file",
                    "Decision register and gates"]
LEGEND = [("inherited", "Inherited, functional only"), ("hardened", "Hardened by the fork (proposed)"), ("chain", "To be built, PL d target"), ("proposed", "Proposed, not yet in any repository")]

ROADMAP = [
  ("01", "Foundation", "ACTIVE", ["Governance and safety plan", "Baseline gap assessment", "Work product register", "Integrated process model", "Decision register"]),
  ("02", "Safety Engineering", "ACTIVE", ["Machine limits and risk assessment", "Safety functions and required PL", "Detection concept", "Cybersecurity threat assessment", "Test operations hold point"]),
  ("03", "Build and Verify", "PLANNED", ["Bench safety hardware", "Firmware hardening", "Chain design and PL calculation", "Stopping and detection tests", "Fault injection"]),
  ("04", "Validate and Release", "PLANNED", ["Validation on the robot", "Independent assessment", "Technical documentation", "Declaration of conformity draft", "Field monitoring"]),
]

GATES = [("G0", "Governance", "P0"), ("G1", "Concept", "P1"), ("G2", "System design", "P2"), ("G3", "HW/SW development", "P3"),
         ("G4", "Integration and verification", "P4"), ("G5", "Validation and release", "P5"), ("G6", "Operation", "P6")]
TODAY_PHASE = "P0"
HOLD_POINTS = {"G1": "no on-ground test before the bench safety hardware and WP-V-07", "G4": "no people in the area before WP-V-03 passes"}


# ------------------------------------------------------------------ helpers

def text(x, y, s, size, fill=C["text"], weight=400, anchor="start", family=FONT, extra=""):
  return (f'<text x="{x:g}" y="{y:g}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
          f'fill="{fill}" text-anchor="{anchor}"{extra}>{escape(s)}</text>')


def rect(x, y, w, h, fill, r=0, stroke="", sw=1, opacity=None, dash=""):
  st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
  op = f' fill-opacity="{opacity}"' if opacity is not None else ""
  da = f' stroke-dasharray="{dash}"' if dash else ""
  return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{r:g}" fill="{fill}"{st}{op}{da}/>'


def wrap(s, width, size):
  per = width / (size * 0.52)
  lines, cur = [], ""
  for w in s.split():
    cand = f"{cur} {w}".strip()
    if len(cand) > per and cur:
      lines.append(cur)
      cur = w
    else:
      cur = cand
  if cur:
    lines.append(cur)
  return lines


def card_bg(w, h, gid):
  return "\n".join([
    f'<linearGradient id="{gid}-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg1"]}"/><stop offset="1" stop-color="{C["bg2"]}"/></linearGradient>',
    f'<linearGradient id="{gid}-amber" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["amber_lo"]}"/><stop offset="0.5" stop-color="{C["amber_hi"]}"/><stop offset="1" stop-color="{C["amber_lo"]}"/></linearGradient>',
  ]), "\n".join([
    f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="22" fill="url(#{gid}-bg)" stroke="{C["stroke"]}"/>',
    f'<rect x="40" y="0" width="{w - 80}" height="3" fill="url(#{gid}-amber)"/>',
  ])


def svg(w, h, gid, title, desc, defs, body):
  return "\n".join([
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{gid}-t {gid}-d">',
    f'  <title id="{gid}-t">{escape(title)}</title>',
    f'  <desc id="{gid}-d">{escape(desc)}</desc>',
    "  <defs>", defs, "  </defs>", body, "</svg>", ""])


def heading(x, label, title, right=""):
  out = [text(x, 56, label, 15, C["amber"], 700, extra=' letter-spacing="3"'), text(x, 94, title, 28, C["text"], 700)]
  if right:
    out.append(text(960, 94, right, 15, C["muted"], anchor="end"))
  return "\n".join(out)


# ------------------------------------------------------------------ hero

def robot_emblem(cx, cy, s=1.0):
  """A geometric mobile manipulator: base with wheels, a LiDAR puck, a torso and two arms."""
  g = []
  # protective field on the floor
  g.append(f'<ellipse cx="{cx + 20 * s:g}" cy="{cy + 128 * s:g}" rx="{210 * s:g}" ry="{46 * s:g}" fill="{C["cyan"]}" fill-opacity="0.06" stroke="{C["cyan"]}" stroke-opacity="0.55" stroke-width="1.6" stroke-dasharray="8 6"/>')
  g.append(f'<ellipse cx="{cx + 20 * s:g}" cy="{cy + 128 * s:g}" rx="{130 * s:g}" ry="{28 * s:g}" fill="{C["cyan"]}" fill-opacity="0.08" stroke="{C["cyan"]}" stroke-opacity="0.8" stroke-width="1.6"/>')
  # wheels
  for dx in (-78, 78):
    g.append(f'<rect x="{cx + dx * s - 22 * s:g}" y="{cy + 86 * s:g}" width="{44 * s:g}" height="{30 * s:g}" rx="{10 * s:g}" fill="#243C44" stroke="{C["stroke"]}"/>')
    g.append(f'<rect x="{cx + dx * s - 12 * s:g}" y="{cy + 96 * s:g}" width="{24 * s:g}" height="{10 * s:g}" rx="{4 * s:g}" fill="{C["cyan"]}" fill-opacity="0.55"/>')
  # base
  g.append(f'<rect x="{cx - 120 * s:g}" y="{cy + 30 * s:g}" width="{240 * s:g}" height="{64 * s:g}" rx="{18 * s:g}" fill="url(#hero-body)" stroke="{C["amber_lo"]}" stroke-width="1.5"/>')
  g.append(f'<rect x="{cx - 100 * s:g}" y="{cy + 48 * s:g}" width="{200 * s:g}" height="{6 * s:g}" rx="3" fill="{C["bg2"]}" fill-opacity="0.45"/>')
  # e-stop on the base
  g.append(f'<circle cx="{cx + 92 * s:g}" cy="{cy + 62 * s:g}" r="{9 * s:g}" fill="{C["red"]}" stroke="#7A2A22" stroke-width="2"/>')
  g.append(f'<circle cx="{cx + 92 * s:g}" cy="{cy + 62 * s:g}" r="{14 * s:g}" fill="none" stroke="{C["amber_hi"]}" stroke-width="1.2"/>')
  # lidar window on the front face of the base, sweeping forward (to the left)
  g.append(f'<rect x="{cx - 112 * s:g}" y="{cy + 58 * s:g}" width="{44 * s:g}" height="{24 * s:g}" rx="{8 * s:g}" fill="#1C3942" stroke="{C["cyan_lo"]}"/>')
  g.append(f'<circle cx="{cx - 90 * s:g}" cy="{cy + 70 * s:g}" r="{6 * s:g}" fill="{C["cyan"]}"/>')
  for r, op in ((70, 0.5), (120, 0.3), (170, 0.16)):
    g.append(f'<path d="M{cx - 90 * s:g},{cy + 70 * s:g} m{-r * s * 0.94:g},{-r * s * 0.34:g} a{r * s:g},{r * s:g} 0 0 1 {0:g},{r * s * 0.68:g}" fill="none" stroke="{C["cyan"]}" stroke-opacity="{op}" stroke-width="1.5"/>')
  # torso
  g.append(f'<rect x="{cx - 34 * s:g}" y="{cy - 92 * s:g}" width="{68 * s:g}" height="{126 * s:g}" rx="{16 * s:g}" fill="url(#hero-body)" stroke="{C["amber_lo"]}" stroke-width="1.5"/>')
  g.append(f'<rect x="{cx - 20 * s:g}" y="{cy - 70 * s:g}" width="{40 * s:g}" height="{8 * s:g}" rx="4" fill="{C["bg2"]}" fill-opacity="0.4"/>')
  g.append(f'<rect x="{cx - 20 * s:g}" y="{cy - 54 * s:g}" width="{40 * s:g}" height="{8 * s:g}" rx="4" fill="{C["bg2"]}" fill-opacity="0.4"/>')
  # head / camera
  g.append(f'<rect x="{cx - 30 * s:g}" y="{cy - 134 * s:g}" width="{60 * s:g}" height="{36 * s:g}" rx="{12 * s:g}" fill="#1C3942" stroke="{C["cyan_lo"]}"/>')
  g.append(f'<rect x="{cx - 18 * s:g}" y="{cy - 124 * s:g}" width="{36 * s:g}" height="{14 * s:g}" rx="7" fill="{C["cyan"]}" fill-opacity="0.9"/>')
  # arms
  for side in (-1, 1):
    sx = cx + side * 34 * s
    g.append(f'<path d="M{sx:g},{cy - 72 * s:g} L{sx + side * 60 * s:g},{cy - 46 * s:g} L{sx + side * 72 * s:g},{cy - 2 * s:g}" fill="none" stroke="#A9C4CB" stroke-width="{12 * s:g}" stroke-linecap="round" stroke-linejoin="round"/>')
    g.append(f'<path d="M{sx:g},{cy - 72 * s:g} L{sx + side * 60 * s:g},{cy - 46 * s:g} L{sx + side * 72 * s:g},{cy - 2 * s:g}" fill="none" stroke="{C["panel"]}" stroke-width="{6 * s:g}" stroke-linecap="round" stroke-linejoin="round"/>')
    g.append(f'<circle cx="{sx + side * 60 * s:g}" cy="{cy - 46 * s:g}" r="{7 * s:g}" fill="{C["amber"]}"/>')
    g.append(f'<rect x="{sx + side * 72 * s - 9 * s:g}" y="{cy - 6 * s:g}" width="{18 * s:g}" height="{22 * s:g}" rx="4" fill="#A9C4CB"/>')
  return "\n".join(g)


def hero_svg():
  w, h = 1280, 520
  defs = "\n".join([
    f'<radialGradient id="hero-bg" cx="0.72" cy="0.45" r="0.95"><stop offset="0" stop-color="#153238"/><stop offset="0.55" stop-color="{C["bg1"]}"/><stop offset="1" stop-color="{C["bg2"]}"/></radialGradient>',
    f'<linearGradient id="hero-body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["amber_hi"]}"/><stop offset="1" stop-color="{C["amber_lo"]}"/></linearGradient>',
    f'<linearGradient id="hero-amber" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["amber_lo"]}"/><stop offset="0.5" stop-color="{C["amber_hi"]}"/><stop offset="1" stop-color="{C["amber_lo"]}"/></linearGradient>',
    f'<linearGradient id="hero-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["cyan"]}" stop-opacity="0"/><stop offset="1" stop-color="{C["cyan"]}" stop-opacity="0.3"/></linearGradient>',
    '<clipPath id="hero-frame"><rect width="1280" height="520" rx="24"/></clipPath>',
  ])
  body = ['<g clip-path="url(#hero-frame)">', f'<rect width="{w}" height="{h}" fill="url(#hero-bg)"/>']
  # floor grid in perspective, vanishing point right of centre
  vx, vy = 980, 300
  for i in range(-9, 13):
    body.append(f'<line x1="{vx}" y1="{vy}" x2="{vx + i * 170}" y2="{h}" stroke="url(#hero-fade)" stroke-width="1"/>')
  for k in range(1, 9):
    y = vy + (h - vy) * (k / 8) ** 1.9
    half = (y - vy) * 7.5
    body.append(f'<line x1="{vx - half:g}" y1="{y:g}" x2="{vx + half:g}" y2="{y:g}" stroke="{C["cyan"]}" stroke-opacity="{0.05 + 0.03 * k:.2f}" stroke-width="1"/>')
  body.append(f'<line x1="0" y1="{vy}" x2="{w}" y2="{vy}" stroke="{C["cyan"]}" stroke-opacity="0.25"/>')
  # emblem
  body.append(robot_emblem(990, 250, 1.0))
  # title block
  body.append(text(72, 150, "OPENAMROBOT ASSURANCE", 18, C["amber"], 700, extra=' letter-spacing="6"'))
  body.append(text(72, 218, "Open mobile manipulation.", 52, C["text"], 800, extra=' letter-spacing="-1"'))
  body.append(text(72, 278, "Engineered for safety.", 52, C["amber_hi"], 800, extra=' letter-spacing="-1"'))
  lines = wrap("The engineering assurance record for a safety-assured fork of the OpenAMRobot platform: machinery risk assessment, a hardwired safety chain with a Performance Level target, and a safety case published as it is built.", 560, 17)
  for i, ln in enumerate(lines):
    body.append(text(72, 320 + i * 25, ln, 17, C["muted"]))
  x = 72
  for chip in CHIPS:
    cw = 11 + len(chip) * 8.2
    body.append(rect(x, 404, cw, 30, C["panel"], r=15, stroke=C["stroke"]))
    body.append(text(x + cw / 2, 424, chip, 13, C["text"], 600, anchor="middle", family=MONO))
    x += cw + 10
  body.append(text(72, 474, "Standards-informed engineering · no compliance claimed · nothing approved for operation around people", 13, C["dim"]))
  body.append("</g>")
  desc = ("OpenAMRobot assurance banner: a geometric mobile manipulator in amber with a cyan LiDAR, a red emergency stop and a dashed protective field on a "
          "perspective floor grid, beside the project name and the tagline " + TAGLINE + " Chips name the standards: " + ", ".join(CHIPS) + ".")
  return svg(w, h, "hero", "OpenAMRobot assurance: " + TAGLINE, desc, defs, "\n".join(body))


# ------------------------------------------------------------------ standards

def standards_svg():
  w = 1000
  row_h, top = 70, 124
  h = top + len(STANDARDS) * (row_h + 10) + 36
  defs, frame = card_bg(w, h, "std")
  body = [frame, heading(40, "STANDARDS-INFORMED ENGINEERING", "One question per standard", "Aligned practices, not a compliance claim")]
  y = top
  for name, sub, question, scope in STANDARDS:
    body.append(rect(40, y, 920, row_h, C["panel"], r=14, stroke=C["stroke"]))
    body.append(rect(40, y + 18, 3, row_h - 36, C["amber"], r=1.5))
    body.append(text(64, y + 30, name, 18, C["amber"], 700))
    body.append(text(64, y + 52, sub, 13, C["muted"], 500))
    body.append(text(330, y + 30, question, 17, C["text"], 600))
    body.append(text(330, y + 52, scope, 13, C["muted"]))
    y += row_h + 10
  body.append(text(40, h - 14, "Every clause reference is marked to be checked against a licensed copy; how each standard is used is WP-M-01 §4.", 12, C["dim"]))
  desc = "Standards the engineering framework draws on. " + " ".join(f"{n} ({s}): {q}" for n, s, q, _ in STANDARDS) + " Aligned practices, not a claim of compliance."
  return svg(w, h, "std", "Standards-informed engineering framework", desc, defs, "\n".join(body))


# ------------------------------------------------------------------ architecture

STATE_STYLE = {
  "inherited": (C["cyan"], 0.12, C["cyan"], ""),
  "hardened": (C["amber"], 0.14, C["amber"], ""),
  "chain": (C["amber"], 0.28, C["amber_hi"], ""),
  "proposed": (C["muted"], 0.08, C["muted"], "5 4"),
}


def architecture_svg():
  w = 1000
  left_w, col_x, col_w = 640, 704, 256
  y = 124
  layer_boxes = []
  layer_tops = []
  for label, title, sub, items in LAYERS:
    cols = 3
    rows = math.ceil(len(items) / cols)
    lh = 96 + rows * 56
    layer_tops.append((y, lh))
    y += lh + 30
  h = y + 70
  defs, frame = card_bg(w, h, "arch")
  body = [frame, heading(40, "PLATFORM ARCHITECTURE", "Three layers, one checker of last resort")]
  for (label, title, sub, items), (ly, lh) in zip(LAYERS, layer_tops, strict=True):
    strong = title.startswith("Safety-related")
    body.append(rect(40, ly, left_w, lh, C["panel"], r=16, stroke=C["amber"] if strong else C["stroke"], sw=1.6 if strong else 1))
    body.append(text(60, ly + 26, label, 11, C["amber"], 700, extra=' letter-spacing="2"'))
    body.append(text(60, ly + 50, title, 19, C["text"], 700))
    body.append(text(60, ly + 70, sub, 12, C["muted"]))
    bw, bh, gap = 192, 46, 12
    for i, (name, state) in enumerate(items):
      bx = 60 + (i % 3) * (bw + gap)
      by = ly + 84 + (i // 3) * (bh + 10)
      fill, op, stroke, dash = STATE_STYLE[state]
      body.append(rect(bx, by, bw, bh, fill, r=9, stroke=stroke, opacity=op, dash=dash))
      lines = wrap(name, bw - 16, 12)
      for j, ln in enumerate(lines[:2]):
        body.append(text(bx + bw / 2, by + (29 if len(lines) == 1 else 21 + j * 15), ln, 12, C["text"], 500, anchor="middle"))
    layer_boxes.append((ly, lh))
  # arrows between layers
  for (ly, lh), (ny, _) in zip(layer_boxes, layer_boxes[1:], strict=False):
    mid = 40 + left_w / 2
    body.append(f'<line x1="{mid}" y1="{ly + lh}" x2="{mid}" y2="{ny - 2}" stroke="{C["muted"]}" stroke-width="1.6"/>')
    body.append(f'<polygon points="{mid - 6},{ny - 10} {mid + 6},{ny - 10} {mid},{ny - 2}" fill="{C["muted"]}"/>')
    body.append(text(mid + 14, ly + lh + 19, "requests, never authority", 11, C["dim"]))
  ly, lh = layer_boxes[-1]
  body.append(text(40 + left_w / 2, ly + lh + 26, "actuator power and brakes: removed by the chain, not by software", 12, C["amber_hi"], 600, anchor="middle"))
  # assurance column
  top, bottom = layer_boxes[0][0], layer_boxes[-1][0] + layer_boxes[-1][1]
  body.append(rect(col_x, top, col_w, bottom - top, C["panel2"], r=16, stroke=C["stroke"], dash="6 4"))
  body.append(text(col_x + 18, top + 26, "CROSS-CUTTING · ALL DRAFTS", 11, C["amber"], 700, extra=' letter-spacing="1.5"'))
  body.append(text(col_x + 18, top + 50, "Safety and assurance", 19, C["text"], 700))
  cy = top + 78
  for item in ASSURANCE_COLUMN:
    body.append(rect(col_x + 18, cy, col_w - 36, 40, C["amber"], r=8, stroke=C["amber"], opacity=0.08))
    lines = wrap(item, col_w - 52, 12)
    for j, ln in enumerate(lines[:2]):
      body.append(text(col_x + col_w / 2, cy + (25 if len(lines) == 1 else 18 + j * 14), ln, 12, C["text"], 500, anchor="middle"))
    cy += 50
  body.append(text(col_x + col_w / 2, bottom - 14, "applies to every layer", 11, C["dim"], anchor="middle"))
  # legend
  lx = 40
  for state, label in LEGEND:
    fill, op, stroke, dash = STATE_STYLE[state]
    body.append(rect(lx, h - 40, 16, 16, fill, r=4, stroke=stroke, opacity=op, dash=dash))
    body.append(text(lx + 24, h - 27, label, 12, C["muted"]))
    lx += 36 + len(label) * 6.6
  desc = ("Architecture diagram. " + " ".join(f"{t} ({s}): " + ", ".join(n for n, _ in it) + "." for _, t, s, it in LAYERS)
          + " A cross-cutting safety and assurance column of draft work products applies to every layer: " + ", ".join(ASSURANCE_COLUMN)
          + ". Legend: " + "; ".join(l for _, l in LEGEND) + ".")
  return svg(w, h, "arch", "OpenAMRobot platform architecture", desc, defs, "\n".join(body))


# ------------------------------------------------------------------ roadmap

def roadmap_svg():
  w = 1000
  cw, gap = 218, 16
  wrapped = [[wrap(it, cw - 56, 13) for it in items] for _, _, _, items in ROADMAP]
  card_h = max(160 + sum(len(ls) for ls in col) * 17 + len(col) * 12 for col in wrapped)
  h = 180 + card_h + 50
  defs, frame = card_bg(w, h, "road")
  body = [frame, heading(40, "ROADMAP", "Four phases, status from repository evidence")]
  n = len(ROADMAP)
  x0 = 40
  cx = [x0 + i * (cw + gap) + cw / 2 for i in range(n)]
  body.append(f'<line x1="{cx[0]}" y1="150" x2="{cx[-1]}" y2="150" stroke="{C["stroke"]}" stroke-width="2"/>')
  for i, (num, name, status, items) in enumerate(ROADMAP):
    active = status == "ACTIVE"
    col = C["cyan"] if active else C["dim"]
    body.append(f'<circle cx="{cx[i]}" cy="150" r="11" fill="{C["bg2"]}" stroke="{col}" stroke-width="2.5"/>')
    body.append(f'<circle cx="{cx[i]}" cy="150" r="5" fill="{col}"/>')
    x = x0 + i * (cw + gap)
    body.append(rect(x, 180, cw, card_h, C["panel"], r=14, stroke=col, opacity=None if active else 0.7, sw=1.2))
    body.append(text(x + 20, 214, f"PHASE {num}", 13, C["amber"], 700, extra=' letter-spacing="2"'))
    for j, ln in enumerate(wrap(name, cw - 40, 19)):
      body.append(text(x + 20, 242 + j * 22, ln, 19, C["text"], 700))
    by = 290
    body.append(rect(x + 20, by, 84, 24, col, r=12, stroke=col, opacity=0.12))
    body.append(text(x + 62, by + 16.5, status, 12, col, 600, anchor="middle", extra=' letter-spacing="1.2"'))
    iy = 340
    for lines in wrapped[i]:
      body.append(rect(x + 20, iy - 8, 6, 6, col, r=1))
      for ln in lines:
        body.append(text(x + 36, iy, ln, 13, C["muted"]))
        iy += 17
      iy += 12
  body.append(text(40, h - 16, "\"Active\" means work products exist as drafts or skeletons; nothing is marked complete before its review. The gates are in WP-M-00 §2.", 12, C["dim"]))
  desc = "Roadmap. " + " ".join(f"Phase {n_}, {name} ({s.title()}): " + ", ".join(it) + "." for n_, name, s, it in ROADMAP)
  return svg(w, h, "road", "OpenAMRobot assurance roadmap", desc, defs, "\n".join(body))


# ------------------------------------------------------------------ lifecycle

def lifecycle_svg():
  w, h = 1000, 300
  defs, frame = card_bg(w, h, "life")
  body = [frame, heading(40, "LIFECYCLE", "Seven phases, seven gates, none passed")]
  n = len(GATES)
  x0, x1 = 60, 940
  step = (x1 - x0) / (n - 1)
  body.append(f'<line x1="{x0}" y1="170" x2="{x1}" y2="170" stroke="{C["stroke"]}" stroke-width="3"/>')
  for i, (g, name, phase) in enumerate(GATES):
    x = x0 + i * step
    today = phase == TODAY_PHASE
    col = C["amber"] if today else C["dim"]
    body.append(f'<circle cx="{x:g}" cy="170" r="16" fill="{C["bg2"]}" stroke="{col}" stroke-width="2.5"/>')
    body.append(text(x, 175, g, 12, col, 700, anchor="middle", family=MONO))
    lines = wrap(name, 120, 12)
    for j, ln in enumerate(lines):
      body.append(text(x, 208 + j * 15, ln, 12, C["text"] if today else C["muted"], 600 if today else 400, anchor="middle"))
    if today:
      body.append(rect(x - 44, 118, 88, 22, C["amber"], r=11, stroke=C["amber"], opacity=0.15))
      body.append(text(x, 133, "TODAY · " + phase, 11, C["amber"], 700, anchor="middle", extra=' letter-spacing="1"'))
    if g in HOLD_POINTS:
      body.append(f'<path d="M{x - 9:g},150 L{x + 9:g},150 L{x:g},136 Z" fill="{C["red"]}"/>')
  body.append(text(40, h - 42, "Hold points: " + "; ".join(f"{g}: {t}" for g, t in HOLD_POINTS.items()) + ".", 12, C["red"]))
  body.append(text(40, h - 20, "A gate counts as passed only when its record in 10-safety-case/gates/ says Pass. Gate skeletons are generated by the process model.", 12, C["dim"]))
  desc = ("The seven phases P0 to P6, each closed by its gate: " + "; ".join(f"{g} {n_}" for g, n_, _ in GATES)
          + f". Today is {TODAY_PHASE}; no gate is passed. Hold points at " + " and ".join(HOLD_POINTS) + ".")
  return svg(w, h, "life", "OpenAMRobot assurance lifecycle", desc, defs, "\n".join(body))


# ------------------------------------------------------------------ entry points

def render_all() -> dict[str, str]:
  return {"hero.svg": hero_svg(), "standards.svg": standards_svg(), "architecture.svg": architecture_svg(),
          "roadmap.svg": roadmap_svg(), "lifecycle.svg": lifecycle_svg()}


def main(argv: list[str]) -> int:
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  g = ap.add_mutually_exclusive_group()
  g.add_argument("--out", type=Path, default=None)
  g.add_argument("--check", action="store_true")
  args = ap.parse_args(argv)
  out = args.out or HERE
  figs = render_all()
  if args.check:
    stale = [n for n, s in figs.items() if not (out / n).exists() or (out / n).read_text(encoding="utf-8") != s]
    for n in stale:
      print(f"{out / n}: stale or missing; run make_assets.py")
    print(f"README figures: {len(figs) - len(stale)} of {len(figs)} current")
    return 1 if stale else 0
  out.mkdir(parents=True, exist_ok=True)
  for n, s in figs.items():
    (out / n).write_text(s, encoding="utf-8")
    print(f"wrote {out / n}")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
