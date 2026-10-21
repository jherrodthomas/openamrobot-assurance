# Review scenes in Blender

| Field | Value |
|---|---|
| Scope | Photorealistic review pictures of the robot in its operating environment: CFG-001, the MMP base from upstream's CAD; CFG-002, the 2.0 mobile manipulator with the OpenArm 2.0 arms; five hazard scenes with a person |
| Version | 0.1 (2026-10-21): first set of eight renders, reviewed by the project lead as pictures |
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

# 4. render the set (the first render caches the imported base as mesh/model_cache.blend; about 4 minutes per picture after that)
$PY -I assurance/sim/blender/make_set.py assurance/sim/blender/mesh assurance/sim/blender/renders 64 1400 788

# one view, fast preview
$PY -I assurance/sim/blender/render_amr.py assurance/sim/blender/mesh /tmp/preview.png 24 900 506 m-station
```

Views: `hero`, `scanplane`, `undock` (the base) and `m-hero`, `m-station`, `m-carry`, `m-lift`, `m-aisle` (the
manipulator). `render_amr.py ... --probe` prints the model's extent, up axis and named-part positions without
rendering. Every scene with a person or a prop runs an axis-aligned overlap check of the actors against every robot
and rack part before the render and prints each intersection; a scene is published only with zero.

## 3. The scripts

| File | What it does |
|---|---|
| [`step_to_obj.py`](step_to_obj.py) | Tessellates a STEP assembly with OpenCascade into one OBJ per leaf part, keeping the assembly path, the part name and the colour where the file has one; writes `index.json` |
| [`dae.py`](dae.py) | Reads the OpenArm Collada meshes with numpy (Blender 5.0 has no Collada importer): triangles, node matrices, diffuse colours. The node matrices alone place each link as the URDF expects; the file's `Y_UP` is not converted |
| [`cfg002.py`](cfg002.py) | The upper body: base plate, lift column, adapter plate, vertical arm profile, J1_A plates, head camera, chest E-stop from the documented dimensions; the two arms from the URDF joint tree by forward kinematics at the documented mount points; poses `stowed`, `reach_right`, `carry`; a person from the library; floor rings and a tote |
| [`render_amr.py`](render_amr.py) | The scene: imports the OBJ set (auto-detecting the SolidWorks Y-up frame and the mm unit), assigns materials by part-name rules, builds the warehouse set, the props of each view, the lights, the camera; Cycles on CPU with denoising |
| [`band.py`](band.py), [`make_set.py`](make_set.py) | The review band (title, caption, the rule) and the driver that renders the set |
| [`library/people/`](library/people/README.md) | Two CC0 walking figures |

## 4. What is real and what is approximated

| Element | Source | Status |
|---|---|---|
| Base chassis, cover, panels, wheels, castors, brackets, fasteners | upstream full-assembly STEP, 1,983 parts, 139 MB | **as modelled**. The STEP carries no colours; materials follow part-name rules (the fastener and bracket names are Russian, read as cp1251 bytes). The electronics inside are upstream's 2.0 set (Jetson carrier, STM32, ZLAC8015D, RPLIDAR S3, Gemini 336L, TF-Luna), not the Gate A unit's Pi 5, Teensy and ZBLD drivers; the chassis is the same |
| OpenArm 2.0 arms and pinch grippers | `enactic/openarm_description`, `assets/robot/openarm_v2.0` and `assets/end_effector/pinch_gripper`: the URDF joint tree and the visual meshes | **as published**. Mount points per the general-arrangement page (x +0.240 m, y ±0.031 m, shoulder 1.000 m retracted); shells rendered white and metal parts aluminium (the meshes' palette says matte black and silver) |
| Lift column, base plate, adapter plate, arm profile, J1_A plates, head camera bracket, chest E-stop | the general-arrangement and upper-body pages of `openamrobot-docs` (DOLD Hexalift V4 530/880 mm, 240 mm fore-aft; 10 mm plate at 294 mm; HFS6-60120 profile 340 mm; ZED Mini 22 mm ahead and 223 mm above the mount) | **approximation**: the column's lateral section (160 mm), the extending section, the guide rods, the carriage and the brackets are drawn, not modelled; upstream's supplier CAD is not public (`openamr-upperbody-hw` holds text only) |
| Warehouse floor, racking, cartons, dock, tote | drawn | set dressing for the operating environment of WP-C-02 |
| Person | CC0 figures, 1.78 m and 1.66 m | a standing frame of the walk cycle; no reaching pose |
| Zones and fields on the floor | WP-S-04 §4.1 (FS-1b 1.09 m, FS-4 0.95 m), §4.5 (reach plus 0.48 m walk), SR-12.03 (keep-clear 0.55 m radius, assumed) | markings, drawn to the budget's planning values |

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
| OI-4 | A physics layer: run the WP-S-04 stopping model as a plant and draw the stop where the model puts it | Assurance team | after WP-V-02 |
