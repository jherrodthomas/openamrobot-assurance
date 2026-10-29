# Review scenes in Blender

| Field | Value |
|---|---|
| Scope | Photorealistic review pictures of the robot in its operating environment: CFG-001, the MMP base from upstream's CAD; CFG-002, the 2.0 mobile manipulator with the OpenArm 2.0 arms; thirteen hazard scenes with a person, one for every high-risk row of WP-C-03; the companions of the WP-S-04 loop diagrams and side elevation; the top-down sprites of the 2D views |
| Version | 0.3 (2026-10-29): eight more hazard scenes (`fire`, `m-corner`, `m-public`, `m-uncommanded`, `m-restart`, `m-resume`, `m-mode`, `m-drop`), so that every high-risk row of WP-C-03 has a picture in its [Annex A](../../02-concept/WP-C-03-annex-a-high-risk-hazard-sheets.md) sheet (the lead's pick of 2026-10-27); a child figure scaled from the library. 0.2 (2026-10-27): eight companion renders for WP-S-04 (the standstill moment of each loop diagram, Figures 2-1 to 2-6; the two elevation panels of Figure 4-2 as orthographic side views with the heights drawn on by `overlay.py`); the three top-down sprites of `sprites/`, cropped to 250 px/m by `sprites.py` and pinned by hash in `../figures/fig_sim_is.py`; the §4.3 caption corrected to 7 to 17 mm. 0.1 (2026-10-21): first set of eight renders, reviewed by the project lead as pictures |
| Status | Draft. AI-drafted (Claude, AI assistant; I0 under WP-M-02 §3.3). **Synthetic: pictures only, no evidence credit** |
| Inputs | `openamr-platform-hw/mechanical/cad/Full_assembly_STEP` (the base), `enactic/openarm_description` (the arms), the general-arrangement page of `openamrobot-docs` (the upper body), the CC0 figures of [`library/people/`](library/people/README.md) |

Every render carries a band that says what it is. The band is not decoration: a picture in this folder never
stands in for a measurement, an inspection or a test.

## 1. The renders

| Picture | What it shows | Record it serves |
|---|---|---|
| ![CFG-001 base, three-quarter view on a warehouse floor](renders/openamrobot-hero.jpg) | **CFG-001**, the MMP base as modelled in the full-assembly STEP: chassis, cover, panels, wheels and castors | WP-C-01 §1.1 |
| ![The 2.0 manipulator: base, lift column, arm profile, two OpenArm arms hanging stowed, head camera](renders/openamrobot-m-hero.jpg) | **CFG-002**, the 2.0 mobile manipulator: base from CAD, lift and profile from documented dimensions, arms from the OpenArm 2.0 description | WP-C-01 §1.2 |
| ![The LiDAR scan plane drawn as cyan beams at 0.222 m over a low carton and a taller one](renders/openamrobot-scanplane.jpg) | **GAP-14**: a 0.15 m carton below the scan plane is invisible to every software layer; the 0.30 m one is seen | WP-C-03 H-01, SR-02.03 |
| ![The base reversing toward a dock with the blind 0.7 m path marked in red on the floor](renders/openamrobot-undock.jpg) | **GAP-35, DQ-018 A**: the undock reverse, now at 0.05 m/s under the rear bumper | WP-C-03 H-01 dock lane, SR-02.04, WP-S-04 §4.3 |
| ![The manipulator driving along an aisle with the protective field marked in cyan ahead and a person crossing it](renders/openamrobot-m-aisle.jpg) | **H-01, IS-01**: a person crossing ahead at navigation speed; the field is set FS-1b of WP-S-04 (1.09 m, fast coast) | WP-C-06 IS-01, WP-S-04 §4.1 |
| ![The manipulator at a rack with the lift extended and an arm reaching to a shelf, a person in the aisle inside an amber ring](renders/openamrobot-m-station.jpg) | **H-13, IS-13**: a person at the station while an arm reaches; the amber ring is the SR-11.02 workspace boundary, reach plus walk term | WP-C-06 IS-13 and CA-02, SR-11.02, WP-S-04 §4.5 |
| ![The manipulator carrying a blue crate in both arms with the carry field ahead and a person crossing](renders/openamrobot-m-carry.jpg) | **H-13, IS-15**: carrying at 0.3 m/s; the arms and the load widen the footprint the carry field must cover | WP-C-06 IS-15 and CA-07, SR-02.10, SR-03.06 |
| ![The manipulator with the lift raised and a person standing beside the column inside an amber keep-clear ring](renders/openamrobot-m-lift.jpg) | **H-15, IS-14**: the lift moving with a person beside the column; the ring is the keep-clear zone of SR-12.03 | WP-C-06 IS-14 and CA-04, SR-12.03 |
| ![The manipulator in an aisle beside racking that ends at a cross-aisle, a person walking out from behind the rack end into its path, the protective field in cyan ahead](renders/openamrobot-m-corner.jpg) | **H-01, IS-02**: a person steps out of a blind corner; nothing is visible until 0.5 m ahead, so the zone speed and the site measures carry the row | WP-C-03 H-01 blind corner, Annex A; WP-C-06 IS-02 |
| ![The manipulator on a shop floor by white shelving, a small child standing in its path beside an adult](renders/openamrobot-m-public.jpg) | **H-01, IS-09**: the public floor, rated e and excluded; the child is the library figure scaled to 1.04 m | WP-C-03 H-01 public floor, OL-01, DQ-019 |
| ![The manipulator standing still with a person just ahead of it, their back to the robot, and a red strip on the floor where it moves](renders/openamrobot-m-uncommanded.jpg) | **H-02**: the robot looks stopped and moves anyway | WP-C-03 H-02, SF-01, SF-04, SF-05 |
| ![A technician in a green shirt facing the stopped manipulator at its front, a red strip on the floor under him](renders/openamrobot-m-restart.jpg) | **H-05, OS-09**: a restart after a stop with nobody having reset it | WP-C-03 H-05 restart, SF-05 |
| ![The manipulator with the protective field ahead clear and a person beside it turning back across its path](renders/openamrobot-m-resume.jpg) | **H-05, IS-10**: resuming after waiting on a person who stepped aside | WP-C-03 H-05 resume, SF-02, SF-08 |
| ![An operator in the foreground holding a tablet with a red on-screen stop while the manipulator drives along a red path toward a second person](renders/openamrobot-m-mode.jpg) | **H-10, IS-06**: the on-screen stop taken for an emergency stop, eyes on the screen | WP-C-03 H-10, SF-01, HR-05 |
| ![The manipulator with both arms raised at shoulder height and a blue tote falling beside a person, an amber landing zone on the floor](renders/openamrobot-m-drop.jpg) | **H-14, IS-14**: the gripper lets go of its load on a stop or a power loss | WP-C-03 H-14, SF-12, DM-07 |
| ![The base on the warehouse floor with grey smoke rising from it and an orange glow on the floor beside it](renders/openamrobot-fire.jpg) | **H-07**: an electrical fire in the battery bay of the inherited base | WP-C-03 H-07, DM-04, GAP-19 |

### 1.1 The companions of the WP-S-04 figures

Each loop diagram of WP-S-04 §2.1 is an arithmetic diagram; its companion is the standstill moment rendered, with
the person placed by bounding box at the clearance the ledger prints (`place_person()`), so the picture shows the
same planning-case gap. The two elevation renders are orthographic, so `overlay.py` can draw the heights of
Figure 4-2 at the camera's scale.

| Picture | What it shows | Figure |
|---|---|---|
| ![The base stopped in an aisle with the red field FS-1b on the floor and a walking person 0.10 m from its front](renders/openamrobot-loop-sf02-scanner.jpg) | SF-02 by the scanner at standstill: the person has walked 0.91 m into the 1.09 m field, the gap is Z | WP-S-04 Figure 2-1 |
| ![The base stopped with its rear bumper at a standing person's shin, the dock and the red reverse path behind](renders/openamrobot-loop-sf02-bumper.jpg) | SF-02 by the bumper at standstill: 7 to 17 mm of stop after contact, inside the edge's overtravel | WP-S-04 Figure 2-2 |
| ![The base stopped with the red field, an amber strip of the shortfall beyond it and a person at the front bumper](renders/openamrobot-loop-sf03.jpg) | SF-03 at the channel 1 cap: the field is 0.19 m short of the stop from 0.25 m/s; contact in the planning case | WP-S-04 Figure 2-3 |
| ![The base stopped with a red and amber ruler on the floor beside it; the operator stands well behind](renders/openamrobot-loop-sf04.jpg) | the SF-04 fault path: 0.21 m with no command, then the coast | WP-S-04 Figure 2-4 |
| ![The manipulator at a rack with an arm reaching and a person standing at the reach radius inside the workspace ring](renders/openamrobot-m-loop-sf11.jpg) | SF-11 at standstill: the person crossed the 1.08 m ring and walked 0.48 m; the arm is stopped | WP-S-04 Figure 2-5 |
| ![The manipulator with the lift raised and a person at the column's side inside the keep-clear ring](renders/openamrobot-m-loop-sf12.jpg) | SF-12 at standstill: the person stepped onto the 0.55 m ring and walked 0.27 m during t_r | WP-S-04 Figure 2-6 |
| ![Orthographic side view of the base with the scan plane, a 0.15 m carton below it, a 0.30 m carton and a standing adult, the heights drawn on](renders/openamrobot-elev-a.jpg) | panel A: the scan plane against what is on the floor (SR-02.03, GAP-14) | WP-S-04 Figure 4-2 |
| ![Orthographic side view of the manipulator with the lift extended, the reach arc, the workspace boundary with a person at it, the envelope and the keep-clear bar drawn on](renders/openamrobot-m-elev-b.jpg) | panel B: the CFG-002 envelope, workspace and keep-clear | WP-S-04 Figure 4-2 |

### 1.2 The sprites

The robot on the 2D views of `../figures/fig_sim_is.py` is its own CAD seen from above: the `sprite`, `m-sprite` and
`m-carry-sprite` views render orthographic and transparent at 500 px/m, and `sprites.py` crops each to its alpha
bounding box, halves it to 250 px/m and writes a sidecar with the base's centre in image pixels. The three files
in [`sprites/`](sprites/) (CFG-001; CFG-002 stowed; CFG-002 carry) are pinned by SHA-256 in `fig_sim_is.py`, so a
re-render that changes a pixel fails CI until the pin is updated on purpose.

## 2. How to regenerate

The pipeline runs on a CPU-only machine with Python 3.11 and no GPU. The render environment is not committed.

```sh
# 1. environment (bpy is Blender 5.0 as a Python module; cadquery-ocp gives the OpenCascade bindings)
uv venv --python 3.11 assurance/sim/blender/render-venv
VIRTUAL_ENV=$PWD/assurance/sim/blender/render-venv uv pip install bpy cadquery-ocp numpy pillow
PY=assurance/sim/blender/render-venv/bin/python

# 2. the inputs: upstream clones beside this repository (read-only; never edited here)
#    ../openamrobot/openamr-platform-hw        the base STEP (Git LFS; the zip is a real file)
#    ../enactic/openarm_description            the OpenArm 2.0 description (or set OPENARM_DESCRIPTION)
mkdir -p /tmp/amr-cad && unzip -o "../openamrobot/openamr-platform-hw/mechanical/cad/Full_assembly_STEP/MMP.00.00.00.000_full_assembly.STEP.zip" -d /tmp/amr-cad

# 3. tessellate the STEP once (about 8 minutes; 1,983 OBJ files, 126 MB, not committed)
$PY -I assurance/sim/blender/step_to_obj.py /tmp/amr-cad/MMP.00.00.00.000_full_assembly.STEP assurance/sim/blender/mesh 0.2

# 4. render the set (the first render caches the imported base as mesh/model_cache.blend; about 4 minutes per picture after that;
#    the sprites go to sprites/, the sixteen banded pictures to renders/)
$PY -I assurance/sim/blender/make_set.py assurance/sim/blender/mesh /tmp/renders 64 1400 788 sprite m-sprite m-carry-sprite
$PY -I assurance/sim/blender/make_set.py assurance/sim/blender/mesh assurance/sim/blender/renders 64 1400 788

# one view, fast preview
$PY -I assurance/sim/blender/render_amr.py assurance/sim/blender/mesh /tmp/preview.png 24 900 506 m-station
```

Views: `hero`, `scanplane`, `undock`, `fire` (the base) and `m-hero`, `m-station`, `m-carry`, `m-lift`, `m-aisle`,
`m-corner`, `m-public`, `m-uncommanded`, `m-restart`, `m-resume`, `m-mode`, `m-drop` (the manipulator); the WP-S-04 companions `elev-a`, `m-elev-b`, `loop-sf02-scanner`, `loop-sf02-bumper`, `loop-sf03`,
`loop-sf04`, `m-loop-sf11`, `m-loop-sf12`; the sprites `sprite`, `m-sprite`, `m-carry-sprite`. `render_amr.py ... --probe` prints the model's extent, up axis and named-part positions without
rendering. Every scene with a person or a prop runs an axis-aligned overlap check of the actors against every robot
and rack part before the render and prints each intersection; a scene is published only with zero.

## 3. The scripts

| File | What it does |
|---|---|
| [`step_to_obj.py`](step_to_obj.py) | Tessellates a STEP assembly with OpenCascade into one OBJ per leaf part, keeping the assembly path, the part name and the colour where the file has one; writes `index.json` |
| [`dae.py`](dae.py) | Reads the OpenArm Collada meshes with numpy (Blender 5.0 has no Collada importer): triangles, node matrices, diffuse colours. The node matrices alone place each link as the URDF expects; the file's `Y_UP` is not converted |
| [`cfg002.py`](cfg002.py) | The upper body: base plate, lift column, adapter plate, vertical arm profile, J1_A plates, head camera, chest E-stop from the documented dimensions; the two arms from the URDF joint tree by forward kinematics at the documented mount points; poses `stowed`, `reach_right`, `carry`; a person from the library; floor rings and a tote |
| [`render_amr.py`](render_amr.py) | The scene: imports the OBJ set (auto-detecting the SolidWorks Y-up frame and the mm unit), assigns materials by part-name rules, builds the warehouse set, the props of each view, the lights, the camera; Cycles on CPU with denoising. `place_person()` slides a figure so that its bounding box sits at a stated clearance; the elevation views switch the camera to orthographic |
| [`overlay.py`](overlay.py) | Draws the heights and distances of WP-S-04 Figure 4-2 onto the two orthographic elevation renders at the camera's pixels-per-metre: the scan planes, the SR-02.03 band, the reach arc, the workspace boundary, the envelope, the keep-clear bar |
| [`sprites.py`](sprites.py) | Crops a top-down sprite render to its alpha bounding box, halves it to 250 px/m and writes the sidecar `fig_sim_is.py` reads |
| [`band.py`](band.py), [`make_set.py`](make_set.py) | The review band (title, caption, the rule) and the driver that renders the set |
| [`library/people/`](library/people/README.md) | Two CC0 walking figures |
| [`sprites/`](sprites/) | The three top-down sprites with their sidecars, pinned by hash in `../figures/fig_sim_is.py` |

## 4. What is real and what is approximated

| Element | Source | Status |
|---|---|---|
| Base chassis, cover, panels, wheels, castors, brackets, fasteners | upstream full-assembly STEP, 1,983 parts, 139 MB | **as modelled**. The STEP carries no colours; materials follow part-name rules (the fastener and bracket names are Russian, read as cp1251 bytes). The electronics inside are upstream's 2.0 set (Jetson carrier, STM32, ZLAC8015D, RPLIDAR S3, Gemini 336L, TF-Luna), not the Gate A unit's Pi 5, Teensy and ZBLD drivers; the chassis is the same |
| OpenArm 2.0 arms and pinch grippers | `enactic/openarm_description`, `assets/robot/openarm_v2.0` and `assets/end_effector/pinch_gripper`: the URDF joint tree and the visual meshes | **as published**. Mount points per the general-arrangement page (x +0.240 m, y ±0.031 m, shoulder 1.000 m retracted); shells rendered white and metal parts aluminium (the meshes' palette says matte black and silver) |
| Lift column, base plate, adapter plate, arm profile, J1_A plates, head camera bracket, chest E-stop | the general-arrangement and upper-body pages of `openamrobot-docs` (DOLD Hexalift V4 530/880 mm, 240 mm fore-aft; 10 mm plate at 294 mm; HFS6-60120 profile 340 mm; ZED Mini 22 mm ahead and 223 mm above the mount) | **approximation**: the column's lateral section (160 mm), the extending section, the guide rods, the carriage and the brackets are drawn, not modelled; upstream's supplier CAD is not public (`openamr-upperbody-hw` holds text only) |
| Warehouse floor, racking, cartons, dock, tote | drawn | set dressing for the operating environment of WP-C-02 |
| Person | CC0 figures, 1.78 m and 1.66 m | a standing frame of the walk cycle; no reaching pose |
| Zones and fields on the floor | WP-S-04 §4.1 (FS-1b 1.09 m, FS-4 0.95 m; CK-1b 1.28 m for the shortfall strip), §4.5 (reach plus 0.48 m walk; keep-clear 0.55 m radius, assumed, now stated there), the SF-04 fault path of §2 (0.21 m plus the coast) | markings, drawn to the budget's planning values |
| The person's clearance in the loop companions | the ledger of the matching WP-S-04 figure: Z = 0.10 m (Figure 2-1), contact (2-2, 2-3), the reach radius (2-5), the base's side (2-6) | set by bounding box in the rest pose; the walking frame's leading foot can sit a few centimetres closer |

**One derived value.** The OpenArm joint offsets of the description package (shoulder to wrist 0.436 m along the
arm, plus the gripper to the fingertip about 0.15 m) give a shoulder-to-fingertip reach of about **0.6 m**. WP-S-02
SR-11.02 and WP-S-04 §4.5 carry it as a planning value until upstream publishes the official reach and the
stopping distance (WP-S-02 OI-8, WP-C-01 OI-6). It is a number read off a description file, not a measurement.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | A reaching or crouching pose for the person (the packs ship the walk cycle only), so the hand-in-gripper case of IS-13 and the hand-under-carriage case of IS-14 can be drawn | Assurance team | next set |
| OI-2 | The Gate A unit as built (Pi 5, Teensy, ZBLD, RPLIDAR A1 at 0.18 m) as its own configuration of the base scene, when a CAD of its electronics bracket exists; today the base is the 2.0-electronics MMP | Assurance team | — |
| OI-3 | Replace the drawn upper body with upstream's supplier CAD when `openamr-upperbody-hw` publishes it | Assurance team | when public |
| OI-4 | A physics layer: run the WP-S-04 stopping model as a plant and draw the stop where the model puts it (the Gazebo scenario tests of `../gazebo/` are a first physics layer; they do not yet carry the WP-S-04 model) | Assurance team | after WP-V-02 |
