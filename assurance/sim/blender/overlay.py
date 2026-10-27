"""Draw the heights and distances of WP-S-04 Figure 4-2 onto the orthographic side renders (elev-a, m-elev-b). The camera
is orthographic with a known number of pixels per metre, so every line lands where the metre value says; the
numbers are the planning values of WP-S-04 §4.2 and §4.5 and WP-C-01 §4, restated here beside their sources."""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TEAL, AMBER, RED, GREEN, INK, WHITE = (0, 200, 190), (240, 160, 30), (235, 80, 60), (70, 200, 110), (18, 20, 23), (245, 245, 240)


def _font(size, bold=False):
  try:
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf", size)
  except OSError:
    return ImageFont.load_default()


def dashed(d, p0, p1, fill, width=2, dash=(12, 7)):
  (x0, y0), (x1, y1) = p0, p1
  L = math.hypot(x1 - x0, y1 - y0)
  if L == 0:
    return
  ux, uy = (x1 - x0) / L, (y1 - y0) / L
  s = 0.0
  while s < L:
    e = min(s + dash[0], L)
    d.line([(x0 + ux * s, y0 + uy * s), (x0 + ux * e, y0 + uy * e)], fill=fill, width=width)
    s = e + dash[1]


def label(d, xy, text, color, font, anchor="la", pad=4):
  x, y = xy
  box = d.textbbox((x, y), text, font=font, anchor=anchor)
  d.rectangle((box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad), fill=(18, 20, 23, 200))
  d.text((x, y), text, fill=color, font=font, anchor=anchor)


def draw(png: Path, view: str, ppm: float, centre: tuple, front: float, top: float) -> None:
  im = Image.open(png).convert("RGBA")
  W, H = im.size
  cx, cz = centre
  X = lambda x: W / 2 + (x - cx) * ppm  # noqa: E731
  Y = lambda z: H / 2 - (z - cz) * ppm  # noqa: E731
  ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
  d = ImageDraw.Draw(ov)
  f, fb, fs = _font(max(12, int(W / 95))), _font(max(13, int(W / 85)), True), _font(max(11, int(W / 110)))
  # the floor and a height ruler at the left edge
  d.line([(0, Y(0)), (W, Y(0))], fill=WHITE, width=2)
  rx = 36
  d.line([(rx, Y(0)), (rx, Y(1.8 if view == "m-elev-b" else 1.2))], fill=WHITE, width=1)
  for z in ((0, 0.30, 0.5, 1.0, 1.5) if view == "elev-a" else (0, 0.5, 1.0, 1.5)):
    d.line([(rx - 5, Y(z)), (rx + 5, Y(z))], fill=WHITE, width=1)
    d.text((rx + 9, Y(z)), f"{z:g} m", fill=WHITE, font=fs, anchor="lm")
  if view == "elev-a":
    # SR-02.03's detection band from the floor to 0.30 m, ahead of the robot
    d.rectangle((X(front), Y(0.30), W, Y(0)), fill=(235, 80, 60, 28))
    lx = X(front - 0.78)   # the labels stack over the robot, left of the objects they name
    label(d, (lx, Y(0.30) - 92), "SR-02.03: detect from the floor to 0.30 m (TBC)", RED, fb, "lb")
    label(d, (lx, Y(0.30) - 66), "a plane alone cannot: a bumper or a second plane (§4.2)", RED, fs, "lb")
    label(d, (lx, Y(0.30) - 42), "scan plane 0.222 m: RPLIDAR S3, 2.0 base (mechanical BOM)", TEAL, f, "lb")
    label(d, (lx, Y(0.30) - 20), "A1 plane 0.18 m: Gate A unit (WP-C-01 §4.2)", TEAL, fs, "lb")
    dashed(d, (X(front), Y(0.222)), (W, Y(0.222)), TEAL, 3)
    dashed(d, (X(front), Y(0.18)), (W, Y(0.18)), TEAL, 1, (6, 6))
    d.text((W - 12, Y(0.222) - 6), "0.222 m", fill=TEAL, font=fs, anchor="rb")
    d.text((W - 12, Y(0.18) + 6), "0.18 m", fill=TEAL, font=fs, anchor="rt")
    d.text((X(front) + 6, Y(0.30) - 4), "0.30 m", fill=RED, font=fs, anchor="lb")
    label(d, (X(1.05), Y(0) + 12), "0.15 m carton: below the plane, unseen (GAP-14)", RED, f, "mt")
    label(d, (X(1.55), Y(0) + 40), "0.30 m carton: seen", GREEN, f, "mt")
    label(d, (X(2.3), Y(0) + 12), "standing adult: the legs cross the plane, seen", GREEN, f, "mt")
    label(d, (X(front - 0.4), Y(top) - 10), f"MMP base, {top:.2f} m high", WHITE, fs, "mb")
  else:
    sx, sz = 0.240, 1.35      # the shoulder: arm mount x, 1.00 m retracted plus the 0.35 m lift drawn
    dashed(d, (0, Y(1.7)), (W, Y(1.7)), RED, 2)
    label(d, (rx + 60, Y(1.7) - 8), "1.7 m: the complete robot at full lift extension (WP-C-01 §4)", RED, f, "lb")
    r = 0.6 * ppm
    d.arc((X(sx) - r, Y(sz) - r, X(sx) + r, Y(sz) + r), start=-90, end=90, fill=TEAL, width=3)
    d.ellipse((X(sx) - 6, Y(sz) - 6, X(sx) + 6, Y(sz) + 6), fill=TEAL)
    label(d, (X(sx) - 14, Y(sz)), "shoulder 1.35 m (1.00 + 0.35 lift)", TEAL, fs, "rm")
    label(d, (X(sx) + 10, Y(sz - 0.6) + 10), "reach 0.6 m: planning value, the description package's joint offsets", TEAL, fs, "lt")
    bx = sx + 1.08
    dashed(d, (X(bx), Y(0)), (X(bx), Y(1.55)), AMBER, 3)
    label(d, (X(bx) - 10, Y(0.50)), "workspace boundary: 1.08 m from the shoulder axis", AMBER, fb, "rb")
    label(d, (X(bx) - 10, Y(0.50) + 8), "reach 0.6 + walk 0.48 m at a 0.3 s stop (SR-11.02, §4.5; stopping time TBC)", AMBER, fs, "rt")
    kx = 0.060
    d.rectangle((X(kx - 0.55), Y(0) - 3, X(kx + 0.55), Y(0) + 4), fill=AMBER)
    label(d, (X(kx), Y(0) + 14), "lift keep-clear 0.55 m each side of the column axis (SR-12.03; the radius is assumed)", AMBER, f, "mt")
    label(d, (X(-0.08), Y(0.75)), "DOLD lift 530 to 880 mm at 18 mm/s", WHITE, fs, "rm")
    label(d, (X(-0.08), Y(0.75) + 22), "3.6 mm in the 200 ms of SR-12.04", WHITE, fs, "rm")
    label(d, (X(bx) + 12, Y(0) + 14), "person 1.78 m at the boundary", WHITE, fs, "lt")
  out = Image.alpha_composite(im, ov).convert("RGB")
  out.save(png)
  print("overlay drawn", view)
