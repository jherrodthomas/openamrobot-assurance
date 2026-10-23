# Robot renders

Views of the robot rendered from upstream's own CAD and description packages, for the README header and for figures
that need to show the robot. They are presentation assets: nothing in them is evidence, and the CAD does not confirm
a dimension (the register already records a track width the CAD gets wrong, WP-C-01 §4). The review scenes with
people, fields and hazards are a separate track, [`assurance/sim/blender/`](../../../../assurance/sim/blender/README.md);
both draw the same robot from the same sources and the same documented dimensions.

| File | What | Used by |
|---|---|---|
| `manipulator-three-quarter.png` | CFG-002, the 2.0 mobile manipulator, three-quarter view from the emergency-stop side, arms stowed, transparent ground, 1000 × 1100 | [`make_assets.py`](../make_assets.py) embeds it in `hero.svg` |
| `base-three-quarter.png` | CFG-001, the base alone, same view, 1400 × 900 | figures of the Gate A unit |
| `base-side.png`, `base-top.png`, `base-front.png` | Orthographic views of the base on the light ground, 1200 × 750 | figures that need the outline (zones, fields, blind zones) |

## Sources and licences

- **The base** is tessellated from `mechanical/cad/Full_assembly_STEP/MMP.00.00.00.000_full_assembly.STEP.zip` in
  [openAMRobot/openamr-platform-hw](https://github.com/openAMRobot/openamr-platform-hw), CERN-OHL-P-2.0. The STEP is
  AP203 and carries few colours, so the hero style recolours parts by name (cover, panels, wheels, the emergency-stop
  and push buttons, the LED strip) in the palette of the README figures.
- **The arms** are the OpenArm 2.0 visual meshes placed by forward kinematics from the URDF of
  [enactic/openarm_description](https://github.com/enactic/openarm_description), Apache-2.0, at the mount points of
  upstream's general-arrangement page.
- **The lift column, base plate, adapter plate, arm profile, head camera and chest E-stop** are drawn from the
  documented dimensions of the general-arrangement page; the supplier CAD is not public, so they are labelled
  approximations ([`build_manipulator.py`](tools/build_manipulator.py) carries the values of the review-scene track's
  `cfg002.py`).

Botshare LTD and the OpenArm project are not affiliated with this fork and do not endorse it.

## How to regenerate

The GLBs (about 45 MB) and the three.js modules are not committed; the PNGs are. Rendering is a manual step; CI only
checks that `hero.svg` embeds the committed PNG.

```sh
pip install cadquery trimesh numpy playwright     # OCP for the STEP, trimesh for the GLBs, Playwright for the screenshot
tools/fetch_three.sh                               # three.js r160 (MIT) next to render.html
python3 tools/step_to_glb.py MMP.00.00.00.000_full_assembly.STEP robot.glb 1.0   # ~5 minutes, 1.7 M triangles
python3 tools/build_manipulator.py <openarm_description clone> robot.glb upper.glb stowed   # the upper body, seconds
(cd .. && python3 -m http.server 8765 --bind 127.0.0.1 &)                      # render.html loads the GLBs over HTTP
python3 tools/render.py manipulator-three-quarter.png "model=../robot.glb&extra=../upper.glb&view=tq&style=hero&az=38&el=16&dist=3.05&fov=24" 1000 1100
python3 tools/render.py base-three-quarter.png "model=../robot.glb&view=tq&style=hero&az=38&el=24&dist=2.25&fov=26" 1400 900
python3 tools/render.py base-side.png  "model=../robot.glb&view=side&style=hero&bg=f3f7f8" 1200 750
python3 tools/render.py base-top.png   "model=../robot.glb&view=top&style=hero&bg=f3f7f8" 1200 750
python3 tools/render.py base-front.png "model=../robot.glb&view=front&style=hero&bg=f3f7f8" 1200 750
python3 ../make_assets.py                          # re-embeds the manipulator view in hero.svg
```

`render.py` loads `http://127.0.0.1:8765/tools/render.html` (set `RENDER_PAGE` to serve it from elsewhere) and drives
Chromium with SwiftShader, so no GPU is needed. `render.html` takes `model` and `extra` (GLBs drawn in the same frame),
`view` (tq, side, top, front), `az`, `el`, `dist`, `fov`, `style=hero`, `ghost=` and `hide=` (node-name substrings,
to draw the cover translucent or leave it out) and `bg`. Parts are recoloured by node name; the loader turns the
spaces in STEP names into underscores, which `render.html` undoes before matching. `build_manipulator.py` takes a
pose: `stowed` (the hero), `ready`, `reach_right` or `carry`.
