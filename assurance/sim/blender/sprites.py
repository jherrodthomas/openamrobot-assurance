"""Crop a rendered top-down sprite to its alpha bounding box, halve it to 250 px/m and write the sidecar that tells
fig_sim_is.py where the robot's centre sits in the image. Called by render_amr.py after a *sprite view renders."""
import json
from pathlib import Path

from PIL import Image

PAD = 6          # pixels of margin around the alpha bounding box, at the render scale
REDUCE = 2       # 500 px/m rendered, 250 px/m pinned


def crop(png: Path, ppm_render: int, view: str) -> dict:
  im = Image.open(png).convert("RGBA")
  W, H = im.size
  x0, y0, x1, y1 = im.getchannel("A").getbbox()
  x0, y0, x1, y1 = max(0, x0 - PAD), max(0, y0 - PAD), min(W, x1 + PAD), min(H, y1 + PAD)
  cut = im.crop((x0, y0, x1, y1))
  cut = cut.resize((cut.width // REDUCE, cut.height // REDUCE), Image.LANCZOS)
  cut.save(png, optimize=True)
  meta = {"file": png.name, "view": view, "px_per_m": ppm_render // REDUCE, "origin_px": [(W / 2 - x0) / REDUCE, (H / 2 - y0) / REDUCE],
          "size_px": [cut.width, cut.height], "frame": "the robot's +x (forward) is image right, +y is image up; origin_px is the base's centre"}
  Path(str(png) + ".json").write_text(json.dumps(meta, indent=1) + "\n")
  print("sprite", meta)
  return meta
