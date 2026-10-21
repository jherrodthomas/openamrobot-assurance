#!/usr/bin/env python3
"""Tessellate a STEP assembly with OpenCascade (OCP) and write one OBJ per solid, keeping names and colours.
Usage: python step_to_obj.py <assembly.step> <out_dir> [linear_deflection_mm]"""
import json
import sys
from pathlib import Path

from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen
from OCP.TDF import TDF_Label
from OCP.collections import Sequence_TDF_Label as TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.Quantity import Quantity_Color
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.IFSelect import IFSelect_RetDone

src, out = Path(sys.argv[1]), Path(sys.argv[2])
defl = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
out.mkdir(parents=True, exist_ok=True)

doc = TDocStd_Document(TCollection_ExtendedString("doc"))
reader = STEPCAFControl_Reader()
reader.SetColorMode(True); reader.SetNameMode(True); reader.SetLayerMode(True)
if reader.ReadFile(str(src)) != IFSelect_RetDone:
  raise SystemExit("read failed")
reader.Transfer(doc)
shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
color_tool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())


def name_of(label: TDF_Label) -> str:
  n = TDataStd_Name()
  if label.FindAttribute(TDataStd_Name.GetID_s(), n):
    return n.Get().ToExtString()
  return ""


def color_of(label: TDF_Label, shape):
  c = Quantity_Color()
  for kind in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen):
    for target in (label, shape):
      try:
        if color_tool.GetColor(target, kind, c):
          return (round(c.Red(), 3), round(c.Green(), 3), round(c.Blue(), 3))
      except TypeError:
        pass
  return None


parts = []
counter = [0]


def walk(label: TDF_Label, loc: TopLoc_Location, path: str):
  name = name_of(label) or f"part{counter[0]}"
  if shape_tool.IsAssembly_s(label):
    comps = TDF_LabelSequence()
    shape_tool.GetComponents_s(label, comps)
    for i in range(1, comps.Length() + 1):
      comp = comps.Value(i)
      cloc = shape_tool.GetLocation_s(comp)
      ref = TDF_Label()
      if shape_tool.GetReferredShape_s(comp, ref):
        walk(ref, loc.Multiplied(cloc), f"{path}/{name_of(comp) or name}")
      else:
        walk(comp, loc.Multiplied(cloc), f"{path}/{name}")
    return
  if shape_tool.IsReference_s(label):
    ref = TDF_Label()
    shape_tool.GetReferredShape_s(label, ref)
    walk(ref, loc.Multiplied(shape_tool.GetLocation_s(label)), path)
    return
  shape = shape_tool.GetShape_s(label)
  if shape.IsNull():
    return
  shape = shape.Moved(loc)
  col = color_of(label, shape_tool.GetShape_s(label))
  counter[0] += 1
  parts.append((f"{path}/{name}", shape, col, label))


roots = TDF_LabelSequence()
shape_tool.GetFreeShapes(roots)
for i in range(1, roots.Length() + 1):
  walk(roots.Value(i), TopLoc_Location(), "")

print(f"{len(parts)} leaf parts", flush=True)
index = []
for n, (path, shape, col, label) in enumerate(parts):
  BRepMesh_IncrementalMesh(shape, defl, False, 0.35, True)
  verts, faces, fcols = [], [], []
  exp = TopExp_Explorer(shape, TopAbs_FACE)
  while exp.More():
    face = TopoDS.Face(exp.Current())
    loc = TopLoc_Location()
    tri = BRep_Tool.Triangulation_s(face, loc)
    if tri is not None:
      trsf = loc.Transformation()
      base = len(verts)
      for k in range(1, tri.NbNodes() + 1):
        p = tri.Node(k).Transformed(trsf)
        verts.append((p.X(), p.Y(), p.Z()))
      rev = face.Orientation() == TopAbs_REVERSED
      fc = Quantity_Color()
      fcol = None
      try:
        if color_tool.GetColor(face, XCAFDoc_ColorSurf, fc):
          fcol = (round(fc.Red(), 3), round(fc.Green(), 3), round(fc.Blue(), 3))
      except TypeError:
        pass
      for k in range(1, tri.NbTriangles() + 1):
        a, b, c = tri.Triangle(k).Get()
        if rev:
          b, c = c, b
        faces.append((base + a, base + b, base + c))
        fcols.append(fcol)
    exp.Next()
  if not faces:
    continue
  safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in path.strip("/").replace("/", "__"))[:120]
  fname = f"{n:04d}_{safe}.obj"
  with open(out / fname, "w") as f:
    f.write(f"o {safe}\n")
    for v in verts:
      f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
    for a, b, c in faces:
      f.write(f"f {a} {b} {c}\n")
  facecols = sorted({c for c in fcols if c}, key=lambda c: -fcols.count(c))
  index.append({"file": fname, "path": path, "color": col or (facecols[0] if facecols else None), "faces": len(faces)})
  if n % 200 == 0:
    print(f"  {n}/{len(parts)}", flush=True)
(out / "index.json").write_text(json.dumps(index, indent=1))
print(f"wrote {len(index)} obj files to {out}")
