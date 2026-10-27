"""Tessellate a STEP assembly with its colours (XCAF) into one GLB, meshes grouped by top-level component and colour."""
import sys, time, collections
import numpy as np, trimesh
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen, XCAFDoc_ColorCurv
from OCP.TCollection import TCollection_ExtendedString
from OCP.IFSelect import IFSelect_RetDone
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.Quantity import Quantity_Color
from OCP.gp import gp_Trsf, gp_Pnt

src, out, defl = sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
t0 = time.time()
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
rd = STEPCAFControl_Reader(); rd.SetColorMode(True); rd.SetNameMode(True); rd.SetLayerMode(False)
assert rd.ReadFile(src) == IFSelect_RetDone, "read failed"
print(f"read {time.time()-t0:.0f}s", flush=True)
rd.Transfer(doc); print(f"transfer {time.time()-t0:.0f}s", flush=True)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

def name_of(label):
    n = TDataStd_Name(); 
    return n.Get().ToExtString() if label.FindAttribute(TDataStd_Name.GetID_s(), n) else ""
def color_of(label):
    c = Quantity_Color()
    for kind in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen):
        if XCAFDoc_ColorTool.GetColor_s(label, kind, c): return (round(c.Red(),3), round(c.Green(),3), round(c.Blue(),3))
    return None
def shape_color(shape):
    c = Quantity_Color()
    for kind in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen):
        if ct.GetColor(shape, kind, c): return (round(c.Red(),3), round(c.Green(),3), round(c.Blue(),3))
    return None

groups = collections.defaultdict(lambda: ([], []))   # (top, color) -> (verts, faces)
stats = collections.Counter()
def add_face(top, color, face, trsf):
    loc = TopLoc_Location(); tri = BRep_Tool.Triangulation_s(face, loc)
    if tri is None: stats["nomesh"] += 1; return
    t = trsf.Multiplied(loc.Transformation())
    n = tri.NbNodes(); verts = np.empty((n, 3))
    for i in range(1, n+1):
        p = tri.Node(i).Transformed(t); verts[i-1] = (p.X(), p.Y(), p.Z())
    rev = face.Orientation() == TopAbs_REVERSED
    fs = np.empty((tri.NbTriangles(), 3), dtype=np.int64)
    for i in range(1, tri.NbTriangles()+1):
        a, b, cc = tri.Triangle(i).Get(); fs[i-1] = (a-1, b-1, cc-1) if rev else (a-1, cc-1, b-1)
    V, F = groups[(top, color)]; off = sum(len(v) for v in V); V.append(verts); F.append(fs + off); stats["faces"] += 1

def walk(label, trsf, top, inherited):
    color = color_of(label) or inherited
    if st.IsAssembly_s(label):
        comps = TDF_LabelSequence(); st.GetComponents_s(label, comps)
        for i in range(1, comps.Length()+1):
            comp = comps.Value(i); ref = TDF_Label(); st.GetReferredShape_s(comp, ref)
            ccol = color_of(comp) or color
            t2 = trsf.Multiplied(st.GetLocation_s(comp).Transformation())
            walk(ref, t2, top or name_of(ref) or name_of(comp), ccol)
        return
    shape = st.GetShape_s(label)
    if shape.IsNull(): return
    BRepMesh_IncrementalMesh(shape, defl, False, 0.5, True)
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face_s(ex.Current()); fc = shape_color(f) or color or (0.72, 0.72, 0.72)
        add_face(top or name_of(label), fc, f, trsf); ex.Next()
    stats["parts"] += 1

free = TDF_LabelSequence(); st.GetFreeShapes(free)
for i in range(1, free.Length()+1):
    walk(free.Value(i), gp_Trsf(), "", None)
print(f"meshed {time.time()-t0:.0f}s {dict(stats)} groups={len(groups)}", flush=True)
scene = trimesh.Scene()
tri_total = 0
for (top, color), (V, F) in groups.items():
    m = trimesh.Trimesh(np.vstack(V), np.vstack(F), process=False)
    rgba = [int(255*c) for c in color] + [255]
    m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=rgba, metallicFactor=0.1, roughnessFactor=0.6))
    tri_total += len(m.faces)
    scene.add_geometry(m, node_name=f"{top}|{'%02x%02x%02x' % tuple(rgba[:3])}", geom_name=f"{top}|{'%02x%02x%02x' % tuple(rgba[:3])}")
scene.export(out)
print(f"wrote {out} triangles={tri_total} {time.time()-t0:.0f}s bounds={scene.bounds.tolist()}", flush=True)
