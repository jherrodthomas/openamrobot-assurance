"""CFG-002, the 2.0 mobile manipulator, on top of the MMP base: the lift column, base plate and arm profile built from
upstream's documented dimensions (general-arrangement page; supplier CAD not public, so these are labelled
approximations), the two OpenArm 2.0 arms from the official description package (URDF joint tree and Collada
meshes, enactic/openarm_description), a head camera and a chest E-stop; plus a CC0 pedestrian figure
(library/people). Everything here is a picture for review and earns no evidence credit."""
import math
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

# the OpenArm description package (enactic/openarm_description), cloned beside the upstream clones: ../../../../enactic/
OPENARM = Path(os.environ.get("OPENARM_DESCRIPTION", Path(__file__).resolve().parents[4] / "enactic" / "openarm_description"))
URDF = OPENARM / "assets/robot/openarm_v2.0/urdf/example/v2.urdf"

# upstream general-arrangement values (option B, bp000), metres from base_link at floor level
DECK_TOP = 0.300   # documented 294; raised 6 mm so the plate sits on the CAD cover top
PLATE_TOP = 0.304
COLUMN_AXIS_X = 0.060
COLUMN_RETRACTED = 0.530        # 304 + 530 = 834 column top
COLUMN_FOREAFT, COLUMN_LAT = 0.240, 0.160   # 240 mm side fore-aft (documented); lateral width assumed
PROFILE = (0.120, 0.060, 0.340)            # HFS6-60120, 340 mm, standing on a 10 mm adapter plate
ARM_MOUNT_X = 0.240
ARM_MOUNT_Y = 0.031
SHOULDER_Z = 1.000                          # at the retracted lift
HEAD_CAM = (0.022, 0.0, 0.223)              # lens relative to the arm mount point


def rpy_matrix(r, p, y):
  return Matrix.Rotation(y, 4, "Z") @ Matrix.Rotation(p, 4, "Y") @ Matrix.Rotation(r, 4, "X")


def parse_urdf(path=URDF):
  root = ET.parse(path).getroot()
  joints = []
  for j in root.findall("joint"):
    o = j.find("origin"); ax = j.find("axis")
    xyz = [float(v) for v in (o.get("xyz", "0 0 0") if o is not None else "0 0 0").split()]
    rpy = [float(v) for v in (o.get("rpy", "0 0 0") if o is not None else "0 0 0").split()]
    axis = [float(v) for v in (ax.get("xyz") if ax is not None else "0 0 1").split()]
    joints.append({"name": j.get("name"), "type": j.get("type"), "parent": j.find("parent").get("link"), "child": j.find("child").get("link"),
                   "origin": Matrix.Translation(xyz) @ rpy_matrix(*rpy), "axis": Vector(axis)})
  visuals = {}
  for l in root.findall("link"):
    vs = []
    for v in l.findall("visual"):
      m = v.find("geometry/mesh"); o = v.find("origin")
      if m is None:
        continue
      fn = m.get("filename").replace("package://openarm_description/", "")
      scale = [float(s) for s in (m.get("scale") or "1 1 1").split()]
      xyz = [float(s) for s in (o.get("xyz", "0 0 0") if o is not None else "0 0 0").split()]
      rpy = [float(s) for s in (o.get("rpy", "0 0 0") if o is not None else "0 0 0").split()]
      vs.append({"file": OPENARM / fn, "scale": scale, "origin": Matrix.Translation(xyz) @ rpy_matrix(*rpy)})
    visuals[l.get("name")] = vs
  return joints, visuals


def fk(joints, q, roots):
  """World matrices of every link below the given roots {link: Matrix}; q maps joint name to angle (rad)."""
  world = dict(roots)
  by_parent = {}
  for j in joints:
    by_parent.setdefault(j["parent"], []).append(j)
  stack = list(roots)
  while stack:
    link = stack.pop()
    for j in by_parent.get(link, []):
      m = world[link] @ j["origin"]
      if j["type"] in ("revolute", "continuous"):
        m = m @ Matrix.Rotation(q.get(j["name"], 0.0), 4, j["axis"])
      world[j["child"]] = m
      stack.append(j["child"])
  return world


_dae_cache = {}


def import_dae(path: Path, coll, mats):
  """Read a Collada file once (dae.py, node matrices only: that is how the URDF places the OpenArm links) and return
  mesh objects linked to coll, one per node part, with the shell in white and the metal parts in aluminium."""
  import dae
  key = str(path)
  if key not in _dae_cache:
    parts = []
    for n, (name, v, f, rgb) in enumerate(dae.read(path, convert_up=False)):
      me = bpy.data.meshes.new(f"{path.stem}_{n}")
      me.from_pydata([tuple(p) for p in v], [], [tuple(int(i) for i in t) for t in f]); me.validate(clean_customdata=False); me.update()
      for poly in me.polygons:
        poly.use_smooth = True
      me.materials.append(mats["silver"] if rgb and rgb[0] > 0.5 else mats["white"])
      parts.append(me)
    _dae_cache[key] = parts
  out = []
  for me in _dae_cache[key]:
    o = bpy.data.objects.new(me.name, me)
    coll.objects.link(o)
    out.append(o)
  return out


def build_arms(coll, q_left, q_right, lift, mats, root_matrix=Matrix.Identity(4)):
  joints, visuals = parse_urdf()
  roots = {"openarm_left_base_link": root_matrix @ Matrix.Translation((ARM_MOUNT_X, ARM_MOUNT_Y, SHOULDER_Z + lift)),
           "openarm_right_base_link": root_matrix @ Matrix.Translation((ARM_MOUNT_X, -ARM_MOUNT_Y, SHOULDER_Z + lift))}
  q = {}
  q.update({f"openarm_left_{k}": v for k, v in q_left.items()})
  q.update({f"openarm_right_{k}": v for k, v in q_right.items()})
  world = fk(joints, q, roots)
  tips = {}
  for link, m in world.items():
    for v in visuals.get(link, []):
      for o in import_dae(v["file"], coll, mats):
        o.matrix_world = m @ v["origin"] @ Matrix.Diagonal((*v["scale"], 1.0))
        o.name = f"{link}:{o.name}"
    if link.endswith("ee_link1"):
      tips[link] = (m @ Vector((0, 0, -0.08))).copy()
  return world, tips


def cube(coll, name, dims, loc, mat):
  bpy.ops.mesh.primitive_cube_add(size=1, location=loc); ob = bpy.context.active_object; ob.name = name; ob.scale = dims
  ob.data.materials.append(mat)
  for c in list(ob.users_collection):
    c.objects.unlink(ob)
  coll.objects.link(ob); return ob


def cylinder(coll, name, r, depth, loc, mat, rot=(0, 0, 0), verts=48):
  bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot); ob = bpy.context.active_object; ob.name = name
  ob.data.materials.append(mat)
  for c in list(ob.users_collection):
    c.objects.unlink(ob)
  coll.objects.link(ob); return ob


def build_upper_body(coll, lift, mats):
  """Base plate, DOLD lift column (outer and the extending inner section), adapter plate, vertical arm profile, head camera
  bracket and chest E-stop. Dimensions from the general-arrangement page; the column section and the carriage are assumed."""
  white, alu, black, red, yellow = mats["white"], mats["alu"], mats["black"], mats["red"], mats["yellow"]
  cube(coll, "base plate (10 mm aluminium)", (0.40, 0.36, 0.010), (COLUMN_AXIS_X, 0, DECK_TOP + 0.005), alu)
  top = PLATE_TOP + COLUMN_RETRACTED
  cube(coll, "lift column, outer (assumed section)", (COLUMN_FOREAFT, COLUMN_LAT, COLUMN_RETRACTED), (COLUMN_AXIS_X, 0, PLATE_TOP + COLUMN_RETRACTED / 2), white)
  if lift > 0.002:
    cube(coll, "lift column, extended section", (COLUMN_FOREAFT - 0.04, COLUMN_LAT - 0.04, lift + 0.02), (COLUMN_AXIS_X, 0, top + lift / 2 - 0.01), alu)
  for sy in (-1, 1):   # guide rods, as in upstream's product render
    cylinder(coll, "guide rod", 0.008, COLUMN_RETRACTED - 0.02, (COLUMN_AXIS_X + COLUMN_FOREAFT / 2 + 0.012, sy * 0.05, PLATE_TOP + COLUMN_RETRACTED / 2), alu)
  ztop = top + lift
  cube(coll, "adapter plate (10 mm)", (0.36, 0.14, 0.010), (COLUMN_AXIS_X + 0.09, 0, ztop + 0.005), alu)
  cube(coll, "arm profile HFS6-60120 (340 mm)", PROFILE, (ARM_MOUNT_X, 0, ztop + 0.010 + PROFILE[2] / 2), alu)
  for sy in (-1, 1):   # J1_A plates
    cube(coll, "J1_A plate", (0.10, 0.008, 0.12), (ARM_MOUNT_X, sy * (PROFILE[1] / 2 + 0.004), SHOULDER_Z + lift), black)
  cx, cy, cz = ARM_MOUNT_X + HEAD_CAM[0], 0.0, SHOULDER_Z + lift + HEAD_CAM[2]
  cube(coll, "head camera bracket", (0.03, 0.03, HEAD_CAM[2] - PROFILE[2] + 0.11), (ARM_MOUNT_X, 0, ztop + 0.010 + PROFILE[2] + (HEAD_CAM[2] - PROFILE[2] + 0.11) / 2 - 0.01), alu)
  cam = cube(coll, "head camera (ZED Mini)", (0.030, 0.125, 0.030), (cx, cy, cz), black)
  cam.rotation_euler = (0, math.radians(25), 0)
  # chest E-stop on the profile front
  cylinder(coll, "chest E-stop collar", 0.030, 0.010, (ARM_MOUNT_X + PROFILE[0] / 2 + 0.005, 0, SHOULDER_Z + lift - 0.06), yellow, rot=(0, math.radians(90), 0))
  cylinder(coll, "chest E-stop button", 0.020, 0.022, (ARM_MOUNT_X + PROFILE[0] / 2 + 0.020, 0, SHOULDER_Z + lift - 0.06), red, rot=(0, math.radians(90), 0))


def add_person(coll, glb: Path, loc, yaw_deg, frame=0, shirt=None):
  before = set(bpy.data.objects)
  bpy.ops.import_scene.gltf(filepath=str(glb))
  new = [o for o in bpy.data.objects if o not in before]
  for o in [o for o in new if o.type == "MESH" and o.name.startswith("Icosphere")]:   # a stray helper sphere in the pack
    bpy.data.objects.remove(o, do_unlink=True); new.remove(o)
  rig = next(o for o in new if o.type == "ARMATURE")
  meshes = [o for o in new if o.type == "MESH"]
  for o in new:
    for c in list(o.users_collection):
      c.objects.unlink(o)
    coll.objects.link(o)
  bpy.context.view_layer.update()
  eyes = next((o for o in meshes if o.name.startswith("Eyes")), None)
  fwd = (eyes.matrix_world.translation if eyes else Vector((1, 0, 0))) - rig.matrix_world.translation
  heading = math.atan2(fwd.y, fwd.x)
  rig.rotation_euler.z += math.radians(yaw_deg) - heading
  rig.location = Vector(loc)
  if rig.animation_data and rig.animation_data.action:
    bpy.context.scene.frame_set(frame)
  if shirt is not None:
    for o in meshes:
      for k, m in enumerate(o.data.materials):
        if m and m.name.split(".")[0] == "shirt":
          o.data.materials[k] = shirt
  return rig


def tote(coll, loc, mat, dims=(0.40, 0.30, 0.22)):
  return cube(coll, "tote", dims, loc, mat)


def floor_ring(coll, name, centre, radius, width, mat):
  """A flat translucent ring on the floor (the workspace boundary or a keep-clear zone)."""
  bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=width / 2, major_segments=96, minor_segments=6, location=(centre[0], centre[1], 0.002))
  ob = bpy.context.active_object; ob.name = name; ob.scale.z = 0.08
  ob.data.materials.append(mat)
  for c in list(ob.users_collection):
    c.objects.unlink(ob)
  coll.objects.link(ob); return ob


POSES = {
  "stowed": ({"joint1": 0.0, "joint4": 0.35}, {"joint1": 0.0, "joint4": 0.35}),
  "reach_right": ({"joint1": 0.0, "joint4": 0.35}, {"joint1": 1.35, "joint2": 0.35, "joint4": 0.55, "joint6": 0.3}),
  "carry": ({"joint1": -1.25, "joint2": -0.25, "joint4": 1.05, "joint6": 0.2}, {"joint1": 1.25, "joint2": 0.25, "joint4": 1.05, "joint6": 0.2}),
}
