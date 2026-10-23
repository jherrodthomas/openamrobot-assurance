"""Deterministic screenshot of render.html: waits until the page reports 'rendered', then captures the canvas.
usage: python3 render.py out.png "view=tq&az=38&el=24&model=../robot.glb" [W] [H]
RENDER_PAGE overrides the page URL (default: render.html served from this folder by `python3 -m http.server 8765` run in ../)."""
import os
import sys
from playwright.sync_api import sync_playwright
out, query = sys.argv[1], sys.argv[2]
W, H = (int(sys.argv[3]) if len(sys.argv) > 3 else 1600), (int(sys.argv[4]) if len(sys.argv) > 4 else 1000)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--no-proxy-server", "--no-sandbox"])
    pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    page = os.environ.get("RENDER_PAGE", "http://127.0.0.1:8765/tools/render.html")
    pg.goto(f"{page}?w={W}&h={H}&quiet=1&{query}")
    pg.wait_for_function("document.title === 'rendered' || document.getElementById('log').textContent.includes('ERR') || document.getElementById('log').textContent.includes('LOAD')", timeout=600000)
    pg.wait_for_timeout(500)
    print(pg.evaluate("document.getElementById('log').textContent").strip())
    pg.locator("#c").screenshot(path=out, omit_background=True)
    b.close()
