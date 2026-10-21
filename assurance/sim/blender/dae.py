"""Minimal Collada (.dae) reader for the OpenArm meshes: triangles with per-node matrices and diffuse colours.
Blender 5.0 has no Collada importer, so geometry is read here with numpy. Returns a list of
(name, vertices [n,3] float, faces [m,3] int, rgb or None) in metres, Z-up (the file's Y_UP is converted when
convert_up is True, as ROS mesh loaders do)."""
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

Y_TO_Z = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=float)   # (x, y, z) -> (x, -z, y)


def _ns(root):
  return {"c": root.tag.split("}")[0].strip("{")}


def read(path: Path, convert_up: bool = True):
  root = ET.parse(path).getroot(); ns = _ns(root)
  unit = root.find("c:asset/c:unit", ns); meter = float(unit.get("meter", "1")) if unit is not None else 1.0
  up = root.find("c:asset/c:up_axis", ns); y_up = (up is not None and up.text.strip() == "Y_UP")
  sources = {}
  geoms = {}
  for g in root.findall(".//c:library_geometries/c:geometry", ns):
    mesh = g.find("c:mesh", ns)
    if mesh is None:
      continue
    for s in mesh.findall("c:source", ns):
      fa = s.find("c:float_array", ns)
      acc = s.find(".//c:accessor", ns)
      stride = int(acc.get("stride", "3")) if acc is not None else 3
      arr = np.fromstring(fa.text, sep=" ", dtype=float).reshape(-1, stride)
      sources["#" + s.get("id")] = arr
    vert = mesh.find("c:vertices", ns)
    pos_src = next(i.get("source") for i in vert.findall("c:input", ns) if i.get("semantic") == "POSITION")
    sources["#" + vert.get("id")] = sources[pos_src]
    tris = []
    for prim in mesh:
      tag = prim.tag.split("}")[-1]
      if tag not in ("triangles", "polylist"):
        continue
      inputs = prim.findall("c:input", ns)
      stride = max(int(i.get("offset")) for i in inputs) + 1
      voff = next(int(i.get("offset")) for i in inputs if i.get("semantic") == "VERTEX")
      vsrc = next(i.get("source") for i in inputs if i.get("semantic") == "VERTEX")
      p = np.fromstring(prim.find("c:p", ns).text, sep=" ", dtype=int)
      idx = p.reshape(-1, stride)[:, voff]
      if tag == "polylist":
        vcount = np.fromstring(prim.find("c:vcount", ns).text, sep=" ", dtype=int)
        faces, k = [], 0
        for n in vcount:
          for t in range(1, n - 1):
            faces.append((idx[k], idx[k + t], idx[k + t + 1]))
          k += n
        faces = np.array(faces, dtype=int)
      else:
        faces = idx.reshape(-1, 3)
      tris.append((faces, prim.get("material"), sources[vsrc]))
    geoms["#" + g.get("id")] = tris
  # materials -> diffuse colour
  effects = {}
  for e in root.findall(".//c:library_effects/c:effect", ns):
    d = e.find(".//c:diffuse/c:color", ns)
    effects["#" + e.get("id")] = tuple(float(v) for v in d.text.split()[:3]) if d is not None else None
  materials = {}
  for m in root.findall(".//c:library_materials/c:material", ns):
    ie = m.find("c:instance_effect", ns)
    materials[m.get("id")] = effects.get(ie.get("url")) if ie is not None else None
  out = []
  for node in root.findall(".//c:library_visual_scenes//c:node", ns):
    mat = node.find("c:matrix", ns)
    M = np.fromstring(mat.text, sep=" ", dtype=float).reshape(4, 4) if mat is not None else np.eye(4)
    for ig in node.findall("c:instance_geometry", ns):
      binds = {im.get("symbol"): im.get("target").lstrip("#") for im in ig.findall(".//c:instance_material", ns)}
      for faces, symbol, verts in geoms.get(ig.get("url"), []):
        v = np.c_[verts[:, :3], np.ones(len(verts))] @ M.T
        v = v[:, :3] * meter
        if y_up and convert_up:
          v = v @ Y_TO_Z.T
        rgb = materials.get(binds.get(symbol, symbol or ""), None)
        out.append((node.get("id") or ig.get("url").lstrip("#"), v, faces, rgb))
  return out


if __name__ == "__main__":
  import sys
  for f in sys.argv[1:]:
    for conv in (False, True):
      parts = read(Path(f), convert_up=conv)
      allv = np.vstack([v for _, v, _, _ in parts])
      print(f"{Path(f).name} convert_up={conv}: {len(parts)} parts, {sum(len(fc) for _, _, fc, _ in parts)} tris, bbox min {allv.min(axis=0).round(3)} max {allv.max(axis=0).round(3)}, colours {sorted({c for *_, c in parts if c})}")
