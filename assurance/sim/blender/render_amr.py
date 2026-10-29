#!/usr/bin/env python3
"""Render the OpenAMRobot MMP base (tessellated from upstream's STEP) with Blender (bpy) and Cycles.

Usage: python render_amr.py <mesh_dir> <out.png> [samples] [width] [height] [view]
       python render_amr.py <mesh_dir> --probe          # print the bounding box and named-part centroids, no render

Views: hero (three-quarter front), scanplane (low side view with a 0.15 m obstacle under the LiDAR plane, GAP-14),
undock (rear three-quarter with the dock and the 0.7 m blind reverse path, GAP-35), fire (H-07), front, top; m-hero,
m-station, m-carry, m-lift, m-aisle and the hazard scenes m-corner, m-public, m-uncommanded, m-restart, m-resume, m-mode,
m-drop (CFG-002, the pictures of WP-C-03 Annex A); the companions of the WP-S-04 figures: elev-a and elev-b (orthographic side views
with the heights of Figure 4-2 drawn on them by overlay.py) and loop-sf02-scanner, loop-sf02-bumper, loop-sf03,
loop-sf04, loop-sf11, loop-sf12 (the standstill moment of each loop diagram of Figures 2-1 to 2-6); the sprites
sprite, m-sprite, m-carry-sprite (orthographic top-down, transparent, cropped to 250 px/m for fig_sim_is.py).
Synthetic picture for review: it earns no evidence credit.
"""
import collections
import json
import math
import sys
from pathlib import Path

import bpy
import mathutils
from mathutils import Vector
import numpy as np

mesh_dir = Path(sys.argv[1])
probe = "--probe" in sys.argv
out_png = Path(sys.argv[2]) if not probe else None
samples = int(sys.argv[3]) if len(sys.argv) > 3 and not probe else 96
W = int(sys.argv[4]) if len(sys.argv) > 4 and not probe else 1600
H = int(sys.argv[5]) if len(sys.argv) > 5 and not probe else 900
view = sys.argv[6] if len(sys.argv) > 6 and not probe else "hero"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = samples
scene.cycles.use_adaptive_sampling = True; scene.cycles.use_denoising = True; scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.max_bounces = 6
scene.render.resolution_x, scene.render.resolution_y = W, H; scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.image_settings.file_format = "PNG"


def principled(name, base, metallic=0.0, rough=0.5, specular=0.5, coat=0.0, aniso=0.0, alpha=1.0, emission=None):
  m = bpy.data.materials.new(name); m.use_nodes = True
  bsdf = m.node_tree.nodes["Principled BSDF"]
  bsdf.inputs["Base Color"].default_value = (*base, 1.0); bsdf.inputs["Metallic"].default_value = metallic
  bsdf.inputs["Roughness"].default_value = rough
  for k, v in (("Specular IOR Level", specular), ("Coat Weight", coat), ("Anisotropic", aniso), ("Alpha", alpha)):
    if k in bsdf.inputs:
      bsdf.inputs[k].default_value = v
  if emission is not None:
    bsdf.inputs["Emission Color"].default_value = (*emission, 1.0); bsdf.inputs["Emission Strength"].default_value = 4.0
  if alpha < 1.0:
    m.surface_render_method = "BLENDED" if hasattr(m, "surface_render_method") else m.surface_render_method
  return m


def build_mats():
  return {
    "white": principled("powder-coated steel, white RAL 9016", (0.86, 0.86, 0.85), rough=0.38, coat=0.25),
    "orange": principled("powder-coated steel, orange RAL 2004", (0.92, 0.33, 0.05), rough=0.4, coat=0.2),
    "galv": principled("galvanised steel bracket", (0.62, 0.63, 0.64), metallic=0.85, rough=0.5),
    "zinc": principled("zinc-plated fastener", (0.72, 0.72, 0.70), metallic=1.0, rough=0.35),
    "alu": principled("aluminium", (0.80, 0.81, 0.82), metallic=1.0, rough=0.3, aniso=0.3),
    "black": principled("black plastic", (0.012, 0.012, 0.013), rough=0.5, specular=0.35),
    "petg": principled("printed PETG, black", (0.02, 0.02, 0.022), rough=0.6, specular=0.3),
    "tyre": principled("drive tyre, polyurethane black", (0.02, 0.02, 0.02), rough=0.75),
    "castor": principled("castor tread, polyurethane orange", (0.85, 0.42, 0.08), rough=0.55),
    "pcb": principled("PCB solder mask", (0.02, 0.16, 0.08), rough=0.45, coat=0.3),
    "red": principled("E-stop button, red", (0.75, 0.03, 0.02), rough=0.35, coat=0.3),
    "yellow": principled("E-stop collar, yellow", (0.95, 0.75, 0.05), rough=0.4),
    "glass": principled("sensor window", (0.02, 0.02, 0.03), rough=0.1, coat=0.8),
    "green_led": principled("LED lens, green", (0.1, 0.8, 0.2), rough=0.3, emission=(0.1, 0.9, 0.2)),
    "steel": principled("bare steel", (0.45, 0.45, 0.46), metallic=0.9, rough=0.45),
    "copper": principled("copper", (0.85, 0.5, 0.3), metallic=1.0, rough=0.35),
  }


MATS = {}


# Keywords are matched on the lower-cased leaf name first, then on the whole assembly path; first match wins.
# The STEP's Russian part names arrive as cp1251 bytes read as latin-1, so the keywords are written the same way:
# âèíò = screw, ãàéêà = nut, øàéáà = washer, çàêë = rivet, ñòîéêà = standoff, øïîíêà = key, ïëàòà = board,
# ìîòîð = motor, ñåðäå÷íèê = core, êíîïêà = button, ãðèáîê = mushroom.
RULES = [
  (("ãðèáîê", "mushroom", "estop", "e-stop", "emergency"), "red"),
  (("êíîïêà", "button", "switch", "cas-120"), "black"),
  (("âèíò", "ãàéêà", "øàéáà", "çàêë", "ñòîéêà", "øïîíêà", "screw", "washer", "nut", "rivet", "din 9", "din 7", "din 6", "iso 4", "iso 7", "standoff", "sleeve", "insert"), "zinc"),
  (("ïëàòà", "pcb", "pcba", "shield", "nucleo", "mb1364", "recomputer", "click", "imu", "board"), "pcb"),
  (("gevn",), "tyre"),
  (("gh-lpa", "lpa035"), "castor"),
  (("vsth", "am_lpa"), "zinc"),
  (("ìîòîð", "z4bld", "bldc", "motor-", "ñåðäå÷íèê", "ucfl", "rexnord", "shaft", "bearing", "adapter"), "steel"),
  (("front panel", "back panel", "side panel", "plastic cover", "cover flange", "mmp.01.00.00.001", "mmp.02.00.00.001", "mmp.00.00.00.00"), "white"),
  (("s3_continue", "rplidar", "lidar", "s3m1", "gemini", "336l", "tf-luna", "tf_luna", "luna", "camera", "zlac", "8015d", "usb", "type-c", "connector", "header", "terminal", "xt30", "socket", "plug"), "black"),
  (("ultrasonic", "mount", "spacer"), "petg"),
  (("led",), "green_led"),
  (("center bracket", "centre bracket", "bracket", "support", "plate", "frame", "base", "mmp.03", "mmp.04", "mmp.05", "mmp.07"), "galv"),
  (("battery", "cell", "pack"), "black"),
]


def material_for(path: str, color):
  parts = path.strip("/").split("/")
  leaf = parts[-1].lower()
  whole = path.lower()
  for keys, mat in RULES:
    if any(k in leaf for k in keys):
      return MATS[mat]
  for keys, mat in RULES:
    if any(k in whole for k in keys):
      return MATS[mat]
  if color:
    r, g, b = color
    key = f"step colour {r:.2f} {g:.2f} {b:.2f}"
    if key not in MATS:
      lum = 0.3 * r + 0.59 * g + 0.11 * b
      MATS[key] = principled(key, (r, g, b), metallic=0.6 if lum > 0.5 and abs(r - b) < 0.1 else 0.0, rough=0.45)
    return MATS[key]
  return MATS["galv"]


def load_obj(path):
  verts, faces = [], []
  for line in open(path):
    if line.startswith("v "):
      x, y, z = line.split()[1:4]; verts.append((float(x), float(y), float(z)))
    elif line.startswith("f "):
      faces.append(tuple(int(i) - 1 for i in line.split()[1:4]))
  return np.array(verts, dtype=float), faces


index = json.loads((mesh_dir / "index.json").read_text())
raw = []
for part in index:
  v, f = load_obj(mesh_dir / part["file"])
  if len(v):
    raw.append((part, v, f))
allv = np.vstack([v for _, v, _ in raw])
ext = allv.max(axis=0) - allv.min(axis=0)
# units: the STEP is in mm if the extent is hundreds; orientation: the smallest extent is the height (a 0.8 × 0.58 × 0.3 m box)
scale = 0.001 if ext.max() > 50 else 1.0
up = int(np.argmin(ext))
if up == 1:    # Y up (SolidWorks): (x, y, z) -> (x, -z, y)
  R = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=float)
elif up == 0:  # X up: (x, y, z) -> (y, z, x)
  R = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=float)
else:
  R = np.eye(3)
allv_b = (allv * scale) @ R.T
floor_z = allv_b[:, 2].min()
centre_xy = (allv_b[:, :2].min(axis=0) + allv_b[:, :2].max(axis=0)) / 2
print(f"extent (model units) {ext.round(1)}, scale {scale}, up axis {'xyz'[up]}, floor z {floor_z:.3f}, centre {centre_xy.round(3)}")

if probe:
  MATS.update(build_mats())
  print("named parts (centroid in blender metres, after centring and floor at z=0):")
  seen = collections.Counter()
  for part, v, f in raw:
    vb = (v * scale) @ R.T
    c = vb.mean(axis=0) - np.array([centre_xy[0], centre_xy[1], floor_z])
    leaf = part["path"].strip("/").split("/")[-1]
    key = leaf[:40]
    seen[key] += 1
    if seen[key] <= 2 and not leaf[:1].isdigit():
      print(f"  {leaf[:48]:48s} n={len(f):6d} centroid {c.round(3)} colour {part['color']}")
  print("per-material counts:", collections.Counter(material_for(p["path"], p["color"]).name for p, _, _ in raw).most_common(20))
  sys.exit(0)

cache = mesh_dir / "model_cache.blend"
if cache.exists():
  bpy.ops.wm.open_mainfile(filepath=str(cache))
  scene = bpy.context.scene
  scene.cycles.samples = samples; scene.render.resolution_x, scene.render.resolution_y = W, H
  coll = bpy.data.collections["model"]
  raw = []
  print("loaded cached scene", cache)
else:
  coll = bpy.data.collections.new("model"); scene.collection.children.link(coll)
MATS.update(build_mats())   # materials must be made after a cache load: loading a file drops every datablock made before it
for part, v, f in raw:
  vb = (v * scale) @ R.T - np.array([centre_xy[0], centre_xy[1], floor_z])
  me = bpy.data.meshes.new(part["file"][:60]); me.from_pydata([tuple(p) for p in vb], [], f); me.validate(clean_customdata=False); me.update()
  ob = bpy.data.objects.new(part["file"][:60], me); ob.data.materials.append(material_for(part["path"], part["color"])); coll.objects.link(ob)
  for p in me.polygons:
    p.use_smooth = True
  try:
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30)); ob.select_set(False)
  except Exception:
    pass
if raw:
  print(f"imported {len(raw)} parts", collections.Counter(o.data.materials[0].name for o in coll.objects).most_common(12))
  bpy.ops.wm.save_as_mainfile(filepath=str(cache)); print("cached", cache)



def _bbox(o):
  pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
  return (min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)), (max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))


def _union(objs):
  boxes = [_bbox(o) for o in objs if o.type == "MESH"]
  lo = tuple(min(b[0][i] for b in boxes) for i in range(3)); hi = tuple(max(b[1][i] for b in boxes) for i in range(3))
  return lo, hi


ROBOT_LO, ROBOT_HI = _union(list(coll.objects))     # the base's extent in metres: ROBOT_HI[0] is the front bumper face, ROBOT_LO[0] the rear
print(f"base extent x {ROBOT_LO[0]:.3f}..{ROBOT_HI[0]:.3f}, y {ROBOT_LO[1]:.3f}..{ROBOT_HI[1]:.3f}, z to {ROBOT_HI[2]:.3f}")


def place_person(rig, axis, face, target):
  """Slide a placed person along one axis so that the near face of their bounding box (the rest pose, as the overlap
  check sees it) sits at the target coordinate: axis 0 or 1, face 'lo' or 'hi'. The planning-case gaps of the loop
  diagrams are set this way, so a still shows the same clearance the ledger prints."""
  bpy.context.view_layer.update()
  lo, hi = _union([o for o in rig.children_recursive if o.type == "MESH"])
  cur = lo[axis] if face == "lo" else hi[axis]
  rig.location[axis] += target - cur
  bpy.context.view_layer.update()


# ---------------------------------------------------------------- set dressing: a warehouse floor and racking


def plane(name, size, loc, mat, rot=(0, 0, 0)):
  bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot); ob = bpy.context.active_object; ob.name = name; ob.data.materials.append(mat); return ob


def cube(name, dims, loc, mat):
  bpy.ops.mesh.primitive_cube_add(size=1, location=loc); ob = bpy.context.active_object; ob.name = name; ob.scale = dims; ob.data.materials.append(mat); return ob


floor_mat = bpy.data.materials.new("floor, dark tiles"); floor_mat.use_nodes = True
nt = floor_mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
brick = nt.nodes.new("ShaderNodeTexBrick"); brick.inputs["Scale"].default_value = 1.0; brick.inputs["Mortar Size"].default_value = 0.006
brick.inputs["Color1"].default_value = (0.045, 0.047, 0.05, 1); brick.inputs["Color2"].default_value = (0.06, 0.062, 0.066, 1); brick.inputs["Mortar"].default_value = (0.02, 0.02, 0.02, 1)
brick.offset = 0.0; brick.squash = 1.0
coord = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / 0.6, 1 / 0.6, 1.0)
noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 40; noise.inputs["Detail"].default_value = 8
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs["Factor"].default_value = 0.08
nt.links.new(coord.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], brick.inputs["Vector"]); nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
nt.links.new(brick.outputs["Color"], mix.inputs[6]); nt.links.new(noise.outputs["Color"], mix.inputs[7]); nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.45
bsdf.inputs["Coat Weight"].default_value = 0.35; bsdf.inputs["Coat Roughness"].default_value = 0.25
plane("floor", 30, (0, 0, 0), floor_mat)

tape_y = principled("hazard tape, yellow", (0.95, 0.75, 0.05), rough=0.5); tape_k = principled("hazard tape, black", (0.02, 0.02, 0.02), rough=0.5)
wall_mat = principled("wall, painted block", (0.80, 0.80, 0.78), rough=0.9)
beam_mat = principled("rack beam, orange", (0.90, 0.35, 0.05), rough=0.45); upright_mat = principled("rack upright, blue", (0.07, 0.18, 0.45), rough=0.5)
cardboard = principled("cardboard", (0.62, 0.47, 0.30), rough=0.85); pallet = principled("pallet wood", (0.55, 0.42, 0.26), rough=0.8)
plane("wall", 30, (0, 5.0, 3.0), wall_mat, rot=(math.radians(90), 0, 0))
for ix, x in enumerate((-3.0, -0.6, 1.8, 4.2)):     # a run of racking along the wall
  for y in (3.3, 4.4):
    cube("upright", (0.09, 0.09, 3.0), (x, y, 1.5), upright_mat)
  for z in (0.45, 1.5, 2.55):
    cube("beam", (2.3, 0.08, 0.12), (x + 1.2, 3.3, z), beam_mat); cube("beam", (2.3, 0.08, 0.12), (x + 1.2, 4.4, z), beam_mat)
    cube("pallet", (1.2, 0.8, 0.144), (x + 1.2, 3.85, z + 0.13), pallet); cube("box", (1.0, 0.7, 0.55), (x + 1.2, 3.85, z + 0.48), cardboard)
for i in range(-8, 9):   # a lane marking: yellow-black tape along y = 1.6 m
  cube("tape", (0.5, 0.06, 0.002), (i * 0.5, 1.6, 0.001), tape_y if i % 2 == 0 else tape_k)

# the robot's frame: +x is forward (set from the probe: the camera and LiDAR sit toward +x)
SCAN_PLANE_Z = 0.222     # RPLIDAR S3 on the 2.0 base: 174 + 17.5 + 30.55 mm (mechanical BOM); the Gate A unit's A1 sits at 0.18 m
rim_mat = principled("LiDAR scan plane rim", (0.1, 0.9, 1.0), rough=0.3, emission=(0.1, 0.9, 1.0))
zone_mat = principled("workspace boundary", (0.95, 0.6, 0.05), rough=0.6, alpha=0.55, emission=(0.9, 0.5, 0.05))
field_mat = principled("protective field", (0.1, 0.9, 1.0), rough=0.3, alpha=0.22, emission=(0.1, 0.9, 1.0))
field_red = principled("protective field, violated", (0.95, 0.15, 0.1), rough=0.3, alpha=0.30, emission=(0.9, 0.1, 0.1))
strip_amber = principled("coast strip", (0.95, 0.6, 0.05), rough=0.6, alpha=0.5, emission=(0.9, 0.5, 0.05))
shirt = principled("shirt, work blue", (0.08, 0.22, 0.5), rough=0.85)
people = Path(__file__).resolve().parent / "library" / "people"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cfg002  # noqa: E402  (the upper body, the arms, the people and the floor rings)


def scan_beams(depth=1.25, rim=True):
  """The scan plane drawn as beams from the LiDAR over the forward sector, with the rim torus at the plane height."""
  if rim:
    bpy.ops.mesh.primitive_torus_add(major_radius=1.6, minor_radius=0.004, major_segments=128, minor_segments=6, location=(0.3, 0.0, SCAN_PLANE_Z)); r = bpy.context.active_object; r.name = "scan plane rim"; r.data.materials.append(rim_mat)
  for k in range(-60, 61, 6):
    ang = math.radians(k)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.0025, depth=depth, location=(0.35 + depth / 2 * math.cos(ang), depth / 2 * math.sin(ang), SCAN_PLANE_Z), rotation=(0, math.radians(90), ang))
    b = bpy.context.active_object; b.name = "scan beam"; b.data.materials.append(rim_mat)


def dock_props():
  dock = principled("dock, grey", (0.35, 0.36, 0.38), rough=0.5, metallic=0.3)
  cube("dock", (0.35, 0.5, 0.30), (-1.35, 0.0, 0.15), dock); cube("dock contact", (0.06, 0.2, 0.08), (-1.15, 0.0, 0.1), MATS["copper"])
  path_mat = principled("reverse path", (0.95, 0.15, 0.1), rough=0.6, alpha=0.45, emission=(0.9, 0.1, 0.1))
  cube("reverse path", (0.7, 0.60, 0.003), (-0.78, 0.0, 0.0015), path_mat)


def field_strip(name, length, start_x, mat, width=0.78, y=0.0):
  """A translucent strip on the floor from start_x forward by length (a field set, or one term of the ledger)."""
  return cube(name, (length, width, 0.003), (start_x + length / 2, y, 0.0015), mat)


FRONT, REAR = ROBOT_HI[0], ROBOT_LO[0]
if view == "scanplane":
  # GAP-14: a 0.15 m carton in the path, below the scan plane; a 0.30 m one beside it is seen
  cube("low obstacle", (0.4, 0.3, 0.15), (1.05, 0.0, 0.075), cardboard)
  scan_beams()
  cube("tall obstacle", (0.4, 0.3, 0.30), (1.05, 0.55, 0.15), cardboard)
if view == "fire":
  # H-07: smoke from the battery bay after a short on the unfused 24 V bus, lit orange from inside the chassis
  for k, (x, y, z, r) in enumerate(((-0.18, -0.05, 0.42, 0.16), (-0.08, 0.06, 0.62, 0.22), (-0.2, 0.15, 0.86, 0.27), (0.02, 0.02, 1.08, 0.31),
                                    (-0.12, 0.22, 1.32, 0.36), (0.1, 0.18, 1.6, 0.4))):
    puff = principled(f"smoke {k}", (0.16 + 0.04 * k, 0.16 + 0.04 * k, 0.17 + 0.04 * k), rough=1.0, specular=0.0, alpha=0.42 - 0.05 * k)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=r, location=(x, y, z)); ob = bpy.context.active_object; ob.name = f"smoke {k}"
    ob.scale = (1.0, 0.9, 0.8); ob.data.materials.append(puff)
    tex = bpy.data.textures.new(f"smoke billow {k}", type="CLOUDS"); tex.noise_scale = 0.12
    dm = ob.modifiers.new("billow", "DISPLACE"); dm.texture = tex; dm.strength = 0.35 * r
  bpy.ops.object.light_add(type="POINT", location=(-0.1, -0.36, 0.18)); gl = bpy.context.active_object; gl.name = "fire glow"
  gl.data.energy = 60; gl.data.color = (1.0, 0.42, 0.08); gl.data.shadow_soft_size = 0.05
if view == "undock":
  dock_props()   # GAP-35: the dock behind the robot and the 0.7 m blind reverse path on the floor
if view == "elev-a":
  # Figure 4-2 panel A: the scan plane against a 0.15 m carton (below it), a 0.30 m carton (at the SR-02.03 height) and a standing adult's legs
  scan_beams(depth=0.98, rim=False)
  kraft = principled("carton, kraft", (0.30, 0.19, 0.09), rough=0.85)
  cube("low obstacle", (0.4, 0.3, 0.15), (1.05, 0.0, 0.075), kraft)
  cube("tall obstacle", (0.4, 0.3, 0.30), (1.55, 0.0, 0.15), kraft)
  rig = cfg002.add_person(scene.collection, people / "pedestrian_male.glb", (2.4, 0.0, 0.0), 180.0, frame=0, shirt=shirt)
  place_person(rig, 0, "lo", 2.05)
if view == "loop-sf02-scanner":
  # Figure 2-1 at standstill: the robot has coasted to rest, the person who entered field FS-1b has walked K·(t_r + t_b) and stands Z = 0.10 m from the front
  field_strip("protective field FS-1b (1.09 m), violated", 1.09, FRONT, field_red)
  rig = cfg002.add_person(scene.collection, people / "pedestrian_female.glb", (1.2, 0.0, 0.0), 180.0, frame=12, shirt=shirt)
  place_person(rig, 0, "lo", FRONT + 0.10)
if view == "loop-sf03":
  # Figure 2-3 at standstill: at the 0.25 m/s ceiling the fast coast needs 1.28 m (CK-1b) and the field is 0.19 m short: contact in the planning case
  field_strip("protective field FS-1b (1.09 m), violated", 1.09, FRONT, field_red)
  field_strip("CK-1b shortfall (0.19 m)", 0.19, FRONT + 1.09, strip_amber)
  rig = cfg002.add_person(scene.collection, people / "pedestrian_female.glb", (1.2, 0.0, 0.0), 180.0, frame=12, shirt=shirt)
  place_person(rig, 0, "lo", FRONT + 0.002)
if view == "loop-sf02-bumper":
  # Figure 2-2 at standstill: reversing at 0.05 m/s into a person's shin; the bumper's overtravel absorbs the 7 to 17 mm stop
  dock_props()
  rig = cfg002.add_person(scene.collection, people / "pedestrian_male.glb", (-0.9, 0.0, 0.0), 0.0, frame=0, shirt=shirt)
  place_person(rig, 0, "hi", REAR - 0.002)
if view == "loop-sf04":
  # Figure 2-4 at standstill: channel 1 died with PWM applied; 1.07 s at 0.20 m/s with no command (red), then the coast (amber), drawn as a ruler beside the robot
  field_strip("no command: 1.07 s at 0.20 m/s (0.21 m)", 0.214, FRONT - 0.254, principled("no-command strip", (0.95, 0.15, 0.1), rough=0.6, alpha=0.6, emission=(0.9, 0.1, 0.1)), width=0.25, y=-0.55)
  field_strip("coast 0.04 m (fast case)", 0.040, FRONT - 0.040, strip_amber, width=0.25, y=-0.55)
  rig = cfg002.add_person(scene.collection, people / "pedestrian_male.glb", (-2.4, 2.6, 0.0), -45.0, frame=0, shirt=shirt)   # the operator, pendant in hand, well outside the path

# world: soft gradient sky (no HDRI available in this container)
world = bpy.data.worlds.new("studio"); scene.world = world; world.use_nodes = True
wn = world.node_tree; bg = wn.nodes["Background"]
grad = wn.nodes.new("ShaderNodeTexGradient"); wc = wn.nodes.new("ShaderNodeTexCoord"); wmp = wn.nodes.new("ShaderNodeMapping")
wmp.inputs["Rotation"].default_value = (0, math.radians(-90), 0); ramp = wn.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = (0.16, 0.17, 0.19, 1)
ramp.color_ramp.elements[1].position = 0.75; ramp.color_ramp.elements[1].color = (0.70, 0.73, 0.78, 1)
wn.links.new(wc.outputs["Generated"], wmp.inputs["Vector"]); wn.links.new(wmp.outputs["Vector"], grad.inputs["Vector"])
wn.links.new(grad.outputs["Fac"], ramp.inputs["Fac"]); wn.links.new(ramp.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 0.6; scene.view_settings.exposure = -0.05


def area(name, loc, target, size, energy, color=(1, 1, 1)):
  bpy.ops.object.light_add(type="AREA", location=loc); l = bpy.context.active_object; l.name = name
  l.data.energy = energy; l.data.size = size; l.data.color = color
  l.rotation_euler = mathutils.Vector(np.array(target) - np.array(loc)).to_track_quat("-Z", "Y").to_euler(); return l


area("key", (1.8, -2.2, 3.2), (0.0, 0.0, 0.2), 2.5, 900, (1.0, 0.97, 0.92))
area("fill", (-2.6, -1.4, 2.0), (0.0, 0.0, 0.2), 4.0, 350, (0.92, 0.95, 1.0))
area("rim", (-1.0, 2.8, 2.6), (0.0, 0.0, 0.2), 2.0, 600)
for x in (-4, 0, 4):  # warehouse ceiling lights
  area(f"ceiling {x}", (x, 2.0, 5.0), (x, 2.0, 0.0), 1.2, 150, (1.0, 0.98, 0.95))

bpy.ops.object.camera_add(); cam = bpy.context.active_object; scene.camera = cam
cam.data.lens = 40; cam.data.sensor_width = 36
views = {
  "hero": ((1.42, -1.30, 0.72), (0.03, 0.0, 0.16), 50),
  "front": ((2.4, -0.25, 0.55), (0.0, 0.0, 0.17), 60),
  "top": ((0.0, -0.01, 3.2), (0.0, 0.0, 0.0), 40),
  "scanplane": ((2.4, -1.7, 0.55), (0.8, 0.15, 0.16), 45),
  "undock": ((-2.3, -1.7, 1.05), (-0.55, 0.0, 0.15), 42),
  "fire": ((2.2, -2.5, 1.2), (-0.05, 0.0, 0.6), 36),
  "sprite": ((0, 0, 4), (0, 0, 0), 50),
  "elev-a": ((1.2, -6.0, 0.82), (1.2, 0.0, 0.82), 50),
  "loop-sf02-scanner": ((1.6, -3.2, 1.4), (0.8, 0.0, 0.55), 30),
  "loop-sf03": ((1.6, -3.2, 1.4), (0.8, 0.0, 0.55), 30),
  "loop-sf02-bumper": ((-2.4, -1.9, 1.1), (-0.6, 0.0, 0.3), 42),
  "loop-sf04": ((1.3, -1.6, 0.8), (0.0, -0.35, 0.15), 38),
}
# ---------------------------------------------------------------- CFG-002 scenes (m-*): upper body, arms, a person, props
if view.startswith("m-"):
  sys.path.insert(0, str(Path(__file__).resolve().parent))
  import cfg002
  mats2 = {"white": MATS["white"], "alu": MATS["alu"], "silver": MATS["alu"], "black": MATS["black"], "red": MATS["red"], "yellow": MATS["yellow"]}
  lift, pose = {"m-hero": (0.0, "stowed"), "m-station": (0.35, "reach_right"), "m-carry": (0.0, "carry"), "m-lift": (0.20, "stowed"), "m-aisle": (0.0, "stowed"),
                "m-sprite": (0.0, "stowed"), "m-carry-sprite": (0.0, "carry"), "m-elev-b": (0.35, "reach_right"), "m-loop-sf11": (0.35, "reach_right"), "m-loop-sf12": (0.20, "stowed"),
                "m-corner": (0.0, "stowed"), "m-public": (0.0, "stowed"), "m-uncommanded": (0.0, "stowed"), "m-restart": (0.0, "stowed"),
                "m-resume": (0.0, "stowed"), "m-mode": (0.0, "stowed"), "m-drop": (0.35, "carry")}[view]
  ub = bpy.data.collections.new("cfg002"); scene.collection.children.link(ub)
  cfg002.build_upper_body(ub, lift, mats2)
  world_m, tips = cfg002.build_arms(ub, *cfg002.POSES[pose], lift, mats2)
  print("arm fingertips", {k: tuple(round(c, 3) for c in v) for k, v in tips.items()})
  if view == "m-elev-b":
    # Figure 4-2 panel B: lift extended, the right arm reaching, a person standing at the workspace boundary (reach 0.6 + walk 0.48 m from the shoulder axis)
    cfg002.floor_ring(ub, "workspace boundary (reach 0.6 m + 0.48 m walk)", (cfg002.ARM_MOUNT_X, 0.0), 1.08, 0.06, zone_mat)
    rig = cfg002.add_person(ub, people / "pedestrian_male.glb", (1.6, 0.0, 0.0), 180.0, frame=0, shirt=shirt)
    place_person(rig, 0, "lo", cfg002.ARM_MOUNT_X + 1.08)
  if view == "m-loop-sf11":
    # Figure 2-5 at standstill: the person who crossed the ring at 1.08 m has walked 0.48 m and stands at the reach radius, 0.6 m from the shoulder axis; the arm is stopped
    for y in (-0.9, 0.9):
      cube("station upright", (0.09, 0.09, 2.2), (1.05, y, 1.1), upright_mat)
    for z in (0.45, 0.95, 1.45):
      cube("station beam", (0.08, 1.9, 0.10), (1.0, 0.0, z), beam_mat); cube("station shelf", (0.5, 1.8, 0.03), (1.25, 0.0, z + 0.06), pallet)
      for y in (-0.6, -0.15, 0.3):
        cube("item", (0.3, 0.25, 0.22), (1.25, y, z + 0.19), cardboard)
    cfg002.floor_ring(ub, "workspace boundary (reach 0.6 m + 0.48 m walk)", (cfg002.ARM_MOUNT_X, 0.0), 1.08, 0.06, zone_mat)
    rig = cfg002.add_person(ub, people / "pedestrian_male.glb", (cfg002.ARM_MOUNT_X, -1.0, 0.0), 90.0, frame=0, shirt=shirt)
    place_person(rig, 1, "hi", -cfg002.ARM_MOUNT_Y - 0.60)
  if view == "m-loop-sf12":
    # Figure 2-6 at standstill: the person who stepped onto the 0.55 m keep-clear ring has walked K·t_r = 0.27 m and stands at the column's side; the lift has moved 3 mm
    cfg002.floor_ring(ub, "lift keep-clear zone", (cfg002.COLUMN_AXIS_X, 0.0), 0.55, 0.05, zone_mat)
    rig = cfg002.add_person(ub, people / "pedestrian_male.glb", (cfg002.COLUMN_AXIS_X, -0.95, 0.0), 90.0, frame=0, shirt=shirt)
    place_person(rig, 1, "hi", ROBOT_LO[1] - 0.002)
  if view == "m-station":
    # a station rack ahead of the robot; the person works at the same shelf (IS-13); the workspace ring = reach + walk term (WP-S-04 §4.5)
    for y in (-0.9, 0.9):
      cube("station upright", (0.09, 0.09, 2.2), (1.05, y, 1.1), upright_mat)
    for z in (0.45, 0.95, 1.45):
      cube("station beam", (0.08, 1.9, 0.10), (1.0, 0.0, z), beam_mat); cube("station shelf", (0.5, 1.8, 0.03), (1.25, 0.0, z + 0.06), pallet)
      for y in (-0.6, -0.15, 0.3):
        cube("item", (0.3, 0.25, 0.22), (1.25, y, z + 0.19), cardboard)
    cfg002.add_person(ub, people / "pedestrian_male.glb", (0.30, -0.98, 0.0), 0.0, frame=0, shirt=shirt)
    cfg002.floor_ring(ub, "workspace boundary (reach 0.6 m + 0.48 m walk)", (cfg002.ARM_MOUNT_X, 0.0), 1.08, 0.06, zone_mat)
  if view == "m-carry":
    mid = sum((Vector(t) for t in tips.values()), Vector()) / max(len(tips), 1)
    crate = principled("tote, blue plastic crate", (0.08, 0.25, 0.6), rough=0.5, coat=0.2)
    cfg002.tote(ub, (mid.x + 0.04, 0.0, mid.z - 0.07), crate)
    cube("carry field FS-4 (0.95 m)", (0.95, 0.80, 0.003), (0.41 + 0.475, 0.0, 0.0015), field_mat)
    cfg002.add_person(ub, people / "pedestrian_female.glb", (2.1, 0.7, 0.0), -90.0, frame=12, shirt=shirt)
  if view == "m-lift":
    cfg002.floor_ring(ub, "lift keep-clear zone", (cfg002.COLUMN_AXIS_X, 0.0), 0.55, 0.05, zone_mat)
    cfg002.add_person(ub, people / "pedestrian_male.glb", (0.0, -0.95, 0.0), 90.0, frame=0, shirt=shirt)
  if view == "m-aisle":
    cube("protective field FS-1b (1.09 m)", (1.09, 0.78, 0.003), (0.41 + 0.545, 0.0, 0.0015), field_mat)
    cfg002.add_person(ub, people / "pedestrian_female.glb", (1.75, 0.65, 0.0), -90.0, frame=12, shirt=shirt)
  path_mat = principled("motion path, red", (0.95, 0.15, 0.1), rough=0.6, alpha=0.45, emission=(0.9, 0.1, 0.1))
  shirt2 = principled("shirt, work green", (0.08, 0.30, 0.14), rough=0.85)
  if view == "m-corner":
    # H-01 / IS-02: racking on the robot's left ends at a cross-aisle; a person walks out from behind its end
    for x in (-2.0, -0.85, 0.3, 1.0):
      for y in (0.62, 1.55):
        cube("rack end upright", (0.08, 0.08, 2.4), (x, y, 1.2), upright_mat)
    for z in (0.12, 0.95, 1.8):
      for y in (0.62, 1.55):
        cube("rack end beam", (3.1, 0.07, 0.10), (-0.5, y, z), beam_mat)
      for xc in (-1.45, -0.3, 0.65):
        cube("rack end box", (0.95, 0.8, 0.62 if z > 0.2 else 0.7), (xc, 1.085, z + (0.38 if z > 0.2 else 0.42)), cardboard)
    cube("protective field FS-1b (1.09 m)", (1.09, 0.78, 0.003), (0.41 + 0.545, 0.0, 0.0015), field_mat)
    cfg002.add_person(ub, people / "pedestrian_female.glb", (1.42, 0.78, 0.0), -90.0, frame=12, shirt=shirt)
  if view == "m-public":
    # H-01 / IS-09, excluded: a shop floor with low gondola shelving; a small child stands in the robot's path
    gondola = principled("gondola shelving, white", (0.85, 0.86, 0.86), rough=0.4)
    for y in (1.05,):
      cube("gondola", (2.6, 0.5, 1.4), (1.3, y, 0.7), gondola)
      for z in (0.35, 0.75, 1.15):
        for xc in (0.4, 0.95, 1.5, 2.05):
          cube("goods", (0.4, 0.3, 0.22), (xc, y - (0.12 if y > 0 else -0.12), z + 0.11), principled(f"goods {xc} {z}", (0.2 + 0.3 * ((xc * 7) % 1), 0.25 + 0.4 * ((z * 3) % 1), 0.5), rough=0.6))
    child = cfg002.add_person(ub, people / "pedestrian_male.glb", (1.05, 0.12, 0.0), 180.0, frame=0, shirt=shirt2)
    child.scale = (0.58, 0.58, 0.58)
    cfg002.add_person(ub, people / "pedestrian_female.glb", (1.5, 0.52, 0.0), 200.0, frame=0, shirt=shirt)
  if view == "m-uncommanded":
    # H-02: the robot looks stopped; a person stands just ahead of it; a stale or stuck command moves it (red: the path it takes)
    cube("uncommanded path", (1.0, 0.62, 0.003), (0.42 + 0.5, 0.0, 0.0015), path_mat)
    cfg002.add_person(ub, people / "pedestrian_male.glb", (1.08, 0.02, 0.0), 0.0, frame=0, shirt=shirt)
  if view == "m-restart":
    # H-05 / OS-09: after a stop a technician works at the robot's front; it restarts when commands resume, with no reset
    cube("restart path", (1.0, 0.62, 0.003), (0.42 + 0.5, 0.0, 0.0015), path_mat)
    cfg002.add_person(ub, people / "pedestrian_male.glb", (0.9, 0.04, 0.0), 180.0, frame=0, shirt=shirt2)
  if view == "m-resume":
    # H-05 / IS-10: the robot waited for a person who stepped aside; it resumes while the person turns back across its path
    cube("protective field FS-1b (1.09 m)", (1.09, 0.78, 0.003), (0.41 + 0.545, 0.0, 0.0015), field_mat)
    cfg002.add_person(ub, people / "pedestrian_female.glb", (0.72, -0.88, 0.0), 75.0, frame=4, shirt=shirt)
  if view == "m-mode":
    # H-10 / IS-06: the operator watches the tablet with its on-screen stop while the robot drives toward a second person
    op = (-1.05, -1.25)
    cfg002.add_person(ub, people / "pedestrian_male.glb", (op[0], op[1], 0.0), 35.0, frame=0, shirt=shirt2)
    th = math.radians(35.0)
    screen = principled("tablet screen", (0.05, 0.08, 0.12), rough=0.2, emission=(0.25, 0.45, 0.7))
    tab = cube("tablet", (0.32, 0.22, 0.014), (op[0] + 0.40 * math.cos(th), op[1] + 0.40 * math.sin(th), 1.2), screen)
    tab.rotation_euler = (0.0, math.radians(-62), th)
    stop_btn = principled("on-screen stop", (0.85, 0.05, 0.03), rough=0.3, emission=(0.9, 0.05, 0.03))
    b = cube("on-screen stop", (0.07, 0.07, 0.004), tab.location, stop_btn); b.rotation_euler = tab.rotation_euler
    b.location = tab.location + mathutils.Euler(tab.rotation_euler).to_matrix() @ Vector((0.05, 0.0, 0.008))
    cube("motion path", (1.6, 0.62, 0.003), (0.42 + 0.8, 0.0, 0.0015), path_mat)
    cfg002.add_person(ub, people / "pedestrian_female.glb", (1.95, 0.55, 0.0), -90.0, frame=12, shirt=shirt)
  if view == "m-drop":
    # H-14 / IS-14: at the station the gripper releases its tote on a stop or power loss; it falls beside a person's feet
    mid = sum((Vector(t) for t in tips.values()), Vector()) / max(len(tips), 1)
    crate = principled("tote, blue plastic crate", (0.08, 0.25, 0.6), rough=0.5, coat=0.2)
    t = cube("tote falling", (0.40, 0.30, 0.22), (mid.x + 0.08, -0.05, 0.55), crate); t.rotation_euler = (math.radians(18), math.radians(-24), math.radians(10))
    fall_mat = principled("fall path", (0.95, 0.6, 0.05), rough=0.6, alpha=0.5, emission=(0.9, 0.5, 0.05))
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.26, depth=0.003, location=(mid.x + 0.08, -0.05, 0.0015)); fp = bpy.context.active_object; fp.name = "landing zone"; fp.data.materials.append(fall_mat)
    cfg002.add_person(ub, people / "pedestrian_female.glb", (mid.x + 0.30, -0.92, 0.0), 90.0, frame=0, shirt=shirt)
  views.update({
    "m-corner": ((2.9, -2.9, 2.7), (0.55, 0.45, 0.45), 36),
    "m-public": ((3.9, -3.0, 1.9), (0.95, 0.2, 0.6), 34),
    "m-uncommanded": ((0.9, -4.3, 1.8), (0.6, 0.0, 0.75), 34),
    "m-restart": ((0.6, -4.3, 1.8), (0.45, 0.0, 0.75), 34),
    "m-resume": ((0.9, 2.9, 1.7), (0.6, -0.35, 0.55), 36),
    "m-mode": ((0.1, -4.6, 2.7), (0.35, -0.35, 0.55), 30),
    "m-drop": ((1.0, 2.9, 1.9), (0.65, -0.35, 0.75), 36),
    "m-hero": ((2.15, -1.95, 1.35), (0.12, 0.0, 0.72), 45),
    "m-station": ((-1.3, -3.9, 2.2), (0.7, -0.25, 1.0), 40),
    "m-carry": ((3.5, -3.1, 1.6), (1.1, 0.3, 0.7), 40),
    "m-lift": ((3.0, -3.6, 1.55), (0.1, -0.45, 0.8), 42),
    "m-aisle": ((3.4, -2.7, 1.5), (0.95, 0.15, 0.55), 40),
    "m-sprite": ((0, 0, 4), (0, 0, 0), 50), "m-carry-sprite": ((0, 0, 4), (0, 0, 0), 50),
    "m-elev-b": ((0.80, -6.0, 0.95), (0.80, 0.0, 0.95), 50),
    "m-loop-sf11": ((-2.2, -3.2, 2.4), (0.45, -0.3, 0.9), 40),
    "m-loop-sf12": ((3.0, -3.6, 1.55), (0.1, -0.45, 0.8), 42),
  })



def overlap_report():
  """Axis-aligned overlap check between the placed actors and props (person, tote, cartons, rack) and the robot; floor
  markings are exempt. Prints every pair that intersects by more than 5 mm so a placement error is caught before a render."""
  robot = [o for o in bpy.data.objects if o.type == "MESH" and (o.users_collection and o.users_collection[0].name in ("model", "cfg002"))
           and not o.name.lower().startswith(("superhero", "eyes", "eyebrows", "hair", "tote", "workspace", "lift keep", "protective", "carry field"))]
  actors = [o for o in bpy.data.objects if o.type == "MESH" and (o.name.lower().startswith("superhero") or o.name.split(".")[0] in ("tote", "low obstacle", "tall obstacle", "dock", "station upright", "station beam", "station shelf", "item",
                                                                                                  "rack end upright", "rack end beam", "rack end box", "gondola", "goods", "tote on floor", "tote falling", "tablet"))]
  rb = [(_bbox(o), o.name) for o in robot]
  bad = 0
  for a in actors:
    (ax0, ay0, az0), (ax1, ay1, az1) = _bbox(a)
    for (b0, b1), name in rb:
      ox = min(ax1, b1[0]) - max(ax0, b0[0]); oy = min(ay1, b1[1]) - max(ay0, b0[1]); oz = min(az1, b1[2]) - max(az0, b0[2])
      if ox > 0.005 and oy > 0.005 and oz > 0.005:
        bad += 1
        if bad <= 12:
          print(f"OVERLAP {a.name} with {name}: {ox * 1000:.0f} x {oy * 1000:.0f} x {oz * 1000:.0f} mm")
  print(f"overlap check: {len(actors)} actors against {len(robot)} robot parts, {bad} overlaps")


overlap_report()
loc, target, lens = views[view]
cam.data.lens = lens
cam.location = loc; cam.rotation_euler = (mathutils.Vector(target) - mathutils.Vector(loc)).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = (mathutils.Vector(target) - mathutils.Vector(loc)).length; cam.data.dof.aperture_fstop = 8.0

# ---------------------------------------------------------------- top-down sprite: orthographic, transparent, fixed pixels per metre
if view.endswith("sprite"):
  for o in list(bpy.data.objects):
    if o.type == "MESH" and o.users_collection and o.users_collection[0].name not in ("model", "cfg002"):
      bpy.data.objects.remove(o, do_unlink=True)     # no floor, racking, props
    elif o.type == "LIGHT":
      bpy.data.objects.remove(o, do_unlink=True)
  scene.render.film_transparent = True
  bpy.ops.object.light_add(type="SUN", location=(0, 0, 5)); sun = bpy.context.active_object; sun.data.energy = 3.0; sun.rotation_euler = (math.radians(20), math.radians(10), 0)
  bg.inputs["Strength"].default_value = 1.0
  cam.data.type = "ORTHO"; cam.data.ortho_scale = 2.0        # 2.0 m across the frame
  scene.render.resolution_x = scene.render.resolution_y = 1000   # 500 px per metre; cropped and halved to 250 px/m below
  cam.location = (0.0, 0.0, 4.0); cam.rotation_euler = (0, 0, 0)
  cam.data.dof.use_dof = False
# ---------------------------------------------------------------- side elevations: orthographic, a known number of pixels per metre, heights drawn on by overlay.py
ELEV = {"elev-a": 3.6, "m-elev-b": 3.4}   # metres across the frame
if view in ELEV:
  cam.data.type = "ORTHO"; cam.data.ortho_scale = ELEV[view]; cam.data.dof.use_dof = False
  for o in list(bpy.data.objects):   # no racking behind an elevation: the silhouettes must read against the wall
    if o.type == "MESH" and o.name.split(".")[0] in ("upright", "beam", "pallet", "box"):
      bpy.data.objects.remove(o, do_unlink=True)
scene.render.filepath = str(out_png.resolve())
bpy.ops.render.render(write_still=True); print("rendered", out_png)

if view.endswith("sprite"):
  import sprites
  sprites.crop(out_png, 500, view)
if view in ELEV and "--no-overlay" not in sys.argv:
  import overlay
  overlay.draw(out_png, view, W / ELEV[view], (loc[0], loc[2]), FRONT, ROBOT_HI[2])
