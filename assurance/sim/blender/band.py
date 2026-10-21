#!/usr/bin/env python3
"""Stamp a review band under a render: title, a wrapped caption and the no-evidence-credit rule.
Usage: band.py in.png out.jpg "title" "caption" """
import sys

from PIL import Image, ImageDraw, ImageFont

src, dst, title, caption = sys.argv[1:5]
im = Image.open(src).convert("RGB")
W, H = im.size
try:
  f_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
  f_cap = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
  f_rule = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
except OSError:
  f_title = f_cap = f_rule = ImageFont.load_default()
d0 = ImageDraw.Draw(im)


def wrap_px(text, font, width):
  lines, cur = [], ""
  for word in text.split():
    cand = (cur + " " + word).strip()
    if d0.textlength(cand, font=font) > width and cur:
      lines.append(cur); cur = word
    else:
      cur = cand
  return lines + ([cur] if cur else [])


title_lines = wrap_px(title, f_title, W - 32) or [""]
cap_lines = wrap_px(caption, f_cap, W - 32) or [""]
band_h = 14 + 26 * len(title_lines) + 20 * len(cap_lines) + 34
out = Image.new("RGB", (W, H + band_h), (18, 20, 23))
out.paste(im, (0, 0))
d = ImageDraw.Draw(out)
y = H + 10
for l in title_lines:
  d.text((16, y), l, fill=(245, 245, 240), font=f_title); y += 26
for l in cap_lines:
  d.text((16, y), l, fill=(190, 196, 200), font=f_cap); y += 20
rule = "SYNTHETIC RENDER FROM UPSTREAM CAD AND DOCUMENTED DIMENSIONS  ·  REVIEW ONLY  ·  NO EVIDENCE CREDIT"
tw = d.textlength(rule, font=f_rule)
d.rectangle((16, y + 6, 16 + tw + 20, y + 28), fill=(214, 69, 53))
d.text((26, y + 11), rule, fill=(255, 255, 255), font=f_rule)
out.save(dst, quality=92)
print("wrote", dst)
