"""The CFG-002 upper body as a second GLB over the base: the base plate, DOLD lift column, adapter plate, HFS6-60120 arm
profile, J1_A plates, head camera and chest E-stop from upstream's documented dimensions, and the two OpenArm 2.0 arms
placed by forward kinematics from the official description package. The dimensions, mount points and poses are the
ones of assurance/sim/blender/cfg002.py (the review-scene track), carried here so the README hero and the review
scenes draw the same robot; the Collada reader is that track's dae.py. The supplier CAD of the upper body is not public,
so column, plates and profile are labelled approximations. Nothing here is evidence.

usage: python3 build_manipulator.py <openarm_description dir> <base.glb> <out.glb> [pose]
The output is in the base GLB's frame (millimetres, Y up, +X forward, floor at the base's lowest point)."""
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4] / "assurance" / "sim" / "blender"))
import dae  # noqa: E402  (assurance/sim/blender/dae.py)

# upstream general-arrangement values (option B, bp000), metres from base_link at floor level; see cfg002.py
DECK_TOP = 0.300
PLATE_TOP = 0.304
COLUMN_AXIS_X = 0.060
COLUMN_RETRACTED = 0.530
COLUMN_FOREAFT, COLUMN_LAT = 0.240, 0.160
PROFILE = (0.120, 0.060, 0.340)
ARM_MOUNT_X = 0.240
ARM_MOUNT_Y = 0.031
SHOULDER_Z = 1.000
HEAD_CAM = (0.022, 0.0, 0.223)
POSES = {
  "stowed": ({"joint1": 0.0, "joint4": 0.35}, {"joint1": 0.0, "joint4": 0.35}),
  "reach_right": ({"joint1": 0.0, "joint4": 0.35}, {"joint1": 1.35, "joint2": 0.35, "joint4": 0.55, "joint6": 0.3}),
  "carry": ({"joint1": -1.25, "joint2": -0.25, "joint4": 1.05, "joint6": 0.2}, {"joint1": 1.25, "joint2": 0.25, "joint4": 1.05, "joint6": 0.2}),
  "ready": ({"joint1": -0.25, "joint2": -0.15, "joint4": 0.9, "joint6": 0.2}, {"joint1": 0.25, "joint2": 0.15, "joint4": 0.9, "joint6": 0.2}),
}
COLOUR = {"white": (0xf6, 0xf8, 0xf9), "alu": (0xb9, 0xc4, 0xc9), "silver": (0xb9, 0xc4, 0xc9), "black": (0x2f, 0x3d, 0x44),
          "red": (0xd6, 0x45, 0x35), "yellow": (0xf2, 0xa3, 0x3a)}


def rot(axis, a):
  x, y, z = np.asarray(axis, dtype=float) / np.linalg.norm(axis); c, s = math.cos(a), math.sin(a); C = 1 - c
  M = np.eye(4)
  M[:3, :3] = [[c + x * x * C, x * y * C - z * s, x * z * C + y * s], [y * x * C + z * s, c + y * y * C, y * z * C - x * s], [z * x * C - y * s, z * y * C + x * s, c + z * z * C]]
  return M


def rpy(r, p, y):
  return rot((0, 0, 1), y) @ rot((0, 1, 0), p) @ rot((1, 0, 0), r)


def tr(x, y, z):
  M = np.eye(4); M[:3, 3] = (x, y, z); return M


def parse_urdf(openarm: Path):
  root = ET.parse(openarm / "assets/robot/openarm_v2.0/urdf/example/v2.urdf").getroot()
  joints = []
  for j in root.findall("joint"):
    o = j.find("origin"); ax = j.find("axis")
    xyz = [float(v) for v in (o.get("xyz", "0 0 0") if o is not None else "0 0 0").split()]
    r = [float(v) for v in (o.get("rpy", "0 0 0") if o is not None else "0 0 0").split()]
    axis = [float(v) for v in (ax.get("xyz") if ax is not None else "0 0 1").split()]
    joints.append({"name": j.get("name"), "type": j.get("type"), "parent": j.find("parent").get("link"), "child": j.find("child").get("link"),
                   "origin": tr(*xyz) @ rpy(*r), "axis": axis})
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
      r = [float(s) for s in (o.get("rpy", "0 0 0") if o is not None else "0 0 0").split()]
      vs.append({"file": openarm / fn, "scale": scale, "origin": tr(*xyz) @ rpy(*r)})
    visuals[l.get("name")] = vs
  return joints, visuals


def fk(joints, q, roots):
  world = dict(roots); by_parent = {}
  for j in joints:
    by_parent.setdefault(j["parent"], []).append(j)
  stack = list(roots)
  while stack:
    link = stack.pop()
    for j in by_parent.get(link, []):
      m = world[link] @ j["origin"]
      if j["type"] in ("revolute", "continuous"):
        m = m @ rot(j["axis"], q.get(j["name"], 0.0))
      world[j["child"]] = m; stack.append(j["child"])
  return world


class Builder:
  def __init__(self):
    self.parts = []   # (name, material key, Trimesh) in Z-up metres

  def add(self, name, key, mesh):
    self.parts.append((name, key, mesh))

  def cube(self, name, dims, loc, key, rot_y=0.0):
    T = tr(*loc) @ rot((0, 1, 0), rot_y)
    self.add(name, key, trimesh.creation.box(extents=dims, transform=T))

  def cylinder(self, name, r, depth, loc, key, rot_y=0.0):
    T = tr(*loc) @ rot((0, 1, 0), rot_y)
    self.add(name, key, trimesh.creation.cylinder(radius=r, height=depth, sections=48, transform=T))


def build_upper_body(b: Builder, lift=0.0):
  b.cube("base plate (10 mm aluminium)", (0.40, 0.36, 0.010), (COLUMN_AXIS_X, 0, DECK_TOP + 0.005), "alu")
  top = PLATE_TOP + COLUMN_RETRACTED
  b.cube("lift column, outer (assumed section)", (COLUMN_FOREAFT, COLUMN_LAT, COLUMN_RETRACTED), (COLUMN_AXIS_X, 0, PLATE_TOP + COLUMN_RETRACTED / 2), "white")
  if lift > 0.002:
    b.cube("lift column, extended section", (COLUMN_FOREAFT - 0.04, COLUMN_LAT - 0.04, lift + 0.02), (COLUMN_AXIS_X, 0, top + lift / 2 - 0.01), "alu")
  for sy in (-1, 1):
    b.cylinder("guide rod", 0.008, COLUMN_RETRACTED - 0.02, (COLUMN_AXIS_X + COLUMN_FOREAFT / 2 + 0.012, sy * 0.05, PLATE_TOP + COLUMN_RETRACTED / 2), "alu")
  ztop = top + lift
  b.cube("adapter plate (10 mm)", (0.36, 0.14, 0.010), (COLUMN_AXIS_X + 0.09, 0, ztop + 0.005), "alu")
  b.cube("arm profile HFS6-60120 (340 mm)", PROFILE, (ARM_MOUNT_X, 0, ztop + 0.010 + PROFILE[2] / 2), "alu")
  for sy in (-1, 1):
    b.cube("J1_A plate", (0.10, 0.008, 0.12), (ARM_MOUNT_X, sy * (PROFILE[1] / 2 + 0.004), SHOULDER_Z + lift), "black")
  cx, cy, cz = ARM_MOUNT_X + HEAD_CAM[0], 0.0, SHOULDER_Z + lift + HEAD_CAM[2]
  bh = HEAD_CAM[2] - PROFILE[2] + 0.11
  b.cube("head camera bracket", (0.03, 0.03, bh), (ARM_MOUNT_X, 0, ztop + 0.010 + PROFILE[2] + bh / 2 - 0.01), "alu")
  b.cube("head camera (ZED Mini)", (0.030, 0.125, 0.030), (cx, cy, cz), "black", rot_y=math.radians(25))
  b.cylinder("chest E-stop collar", 0.030, 0.010, (ARM_MOUNT_X + PROFILE[0] / 2 + 0.005, 0, SHOULDER_Z + lift - 0.06), "yellow", rot_y=math.radians(90))
  b.cylinder("chest E-stop button", 0.020, 0.022, (ARM_MOUNT_X + PROFILE[0] / 2 + 0.020, 0, SHOULDER_Z + lift - 0.06), "red", rot_y=math.radians(90))


def build_arms(b: Builder, openarm: Path, pose, lift=0.0):
  joints, visuals = parse_urdf(openarm)
  q_left, q_right = POSES[pose]
  roots = {"openarm_left_base_link": tr(ARM_MOUNT_X, ARM_MOUNT_Y, SHOULDER_Z + lift), "openarm_right_base_link": tr(ARM_MOUNT_X, -ARM_MOUNT_Y, SHOULDER_Z + lift)}
  q = {f"openarm_left_{k}": v for k, v in q_left.items()}
  q.update({f"openarm_right_{k}": v for k, v in q_right.items()})
  world = fk(joints, q, roots)
  cache = {}
  for link, m in world.items():
    for v in visuals.get(link, []):
      key = str(v["file"])
      if key not in cache:
        cache[key] = dae.read(v["file"], convert_up=False)
      M = m @ v["origin"] @ np.diag([*v["scale"], 1.0])
      for n, (name, verts, faces, rgb) in enumerate(cache[key]):
        vv = np.c_[verts, np.ones(len(verts))] @ M.T
        mat = "silver" if rgb and rgb[0] > 0.5 else "white"
        b.add(f"OpenArm {link} {v['file'].stem} {n}", mat, trimesh.Trimesh(vv[:, :3], faces, process=False))


def main():
  openarm, base, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
  pose = sys.argv[4] if len(sys.argv) > 4 else "stowed"
  lo, hi = trimesh.load(base, force="scene").bounds   # the base GLB: mm, Y up
  cx, cz, floor_y = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2, lo[1]
  print(f"base bounds {lo.round(1).tolist()} {hi.round(1).tolist()}: centre x {cx:.1f} z {cz:.1f}, floor y {floor_y:.1f}")
  b = Builder()
  build_upper_body(b)
  build_arms(b, openarm, pose)
  # Z-up metres (x forward, y left, z up) -> the base GLB frame (mm, Y up): (x, y, z) -> (x, z, -y)
  R = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], dtype=float)
  M = tr(cx, floor_y, cz) @ np.diag([1000.0, 1000.0, 1000.0, 1.0]) @ R
  scene = trimesh.Scene(); tris = 0
  for name, key, mesh in b.parts:
    mesh.apply_transform(M)
    rgba = [*COLOUR[key], 255]
    mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=rgba, metallicFactor=0.1, roughnessFactor=0.5))
    node = f"Upper body {name}|{'%02x%02x%02x' % tuple(rgba[:3])}"
    scene.add_geometry(mesh, node_name=node, geom_name=node); tris += len(mesh.faces)
  scene.export(out)
  print(f"wrote {out} pose={pose} parts={len(b.parts)} triangles={tris} bounds={scene.bounds.round(1).tolist()}")


if __name__ == "__main__":
  main()
