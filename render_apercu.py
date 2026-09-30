#!/usr/bin/env python3
"""
Rendus d'aperçu (PNG) du tracker lunaire, éclairé depuis la direction du Soleil.
Nécessite un affichage OpenGL ; sur serveur : xvfb-run -a python render_apercu.py
"""

import math
import os

import cadquery as cq
from cadquery.occ_impl.assembly import _loc2vtk
from cadquery.occ_impl.exporters.vtk import extractEdgesFaces
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import (vtkActor, vtkLight, vtkPolyDataMapper,
                                         vtkRenderer, vtkRenderWindow,
                                         vtkWindowToImageFilter)
from vtkmodules.vtkRenderingOpenGL2 import vtkOpenGLRenderer  # noqa: F401 (charge le backend)

import generate_tracker as G

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")


def sun_vector_yup(az, el):
    """Direction du Soleil (repère Y-up exporté) pour une pose (az tête, élévation)."""
    a, e = math.radians(az), math.radians(el)
    # normale du panneau en Z-up : Rz(az) * (0, cos e, sin e)
    x, y, z = -math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)
    return (x, z, -y)


def build_renderer(assy, sun, ground=True, edges=True):
    ren = vtkRenderer()
    ren.SetBackground(0.02, 0.02, 0.04)
    for shape, _name, loc, col in assy:
        data = shape.toVtkPolyData(0.25, 0.25)
        d_edges, d_faces = extractEdgesFaces(data)
        trans, rot = _loc2vtk(loc)
        m = vtkPolyDataMapper()
        m.SetInputData(d_faces)
        a = vtkActor()
        a.SetMapper(m)
        a.SetPosition(*trans)
        a.SetOrientation(*rot)
        c = col.toTuple() if col else (0.8, 0.8, 0.8, 1)
        p = a.GetProperty()
        p.SetColor(*c[:3])
        p.SetAmbient(0.12)
        p.SetDiffuse(0.85)
        p.SetSpecular(0.35 if c[2] > c[0] else 0.15)
        p.SetSpecularPower(40)
        ren.AddActor(a)
        if edges:
            me = vtkPolyDataMapper()
            me.SetInputData(d_edges)
            ae = vtkActor()
            ae.SetMapper(me)
            ae.SetPosition(*trans)
            ae.SetOrientation(*rot)
            ae.GetProperty().SetColor(0.05, 0.05, 0.05)
            ae.GetProperty().SetLineWidth(0.6)
            ae.GetProperty().SetOpacity(0.35)
            ren.AddActor(ae)
    if ground:
        g = vtkCylinderSource()
        g.SetRadius(2600)
        g.SetHeight(4)
        g.SetResolution(120)
        g.SetCenter(0, -2.1, 0)
        mg = vtkPolyDataMapper()
        mg.SetInputConnection(g.GetOutputPort())
        ag = vtkActor()
        ag.SetMapper(mg)
        ag.GetProperty().SetColor(0.42, 0.41, 0.40)
        ag.GetProperty().SetAmbient(0.25)
        ag.GetProperty().SetDiffuse(0.8)
        ren.AddActor(ag)
    ren.RemoveAllLights()
    sunl = vtkLight()
    sunl.SetLightTypeToSceneLight()
    sunl.SetPositional(False)
    sunl.SetPosition(*(10000 * v for v in sun))
    sunl.SetFocalPoint(0, 0, 0)
    sunl.SetIntensity(1.0)
    ren.AddLight(sunl)
    fill = vtkLight()
    fill.SetLightTypeToHeadlight()
    fill.SetIntensity(0.35)
    ren.AddLight(fill)
    return ren


def shoot(ren, fname, pos, focal=(0, 900, 0), up=(0, 1, 0), size=(1600, 1200), angle=30):
    rw = vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetMultiSamples(8)
    rw.AddRenderer(ren)
    rw.SetSize(*size)
    cam = ren.GetActiveCamera()
    cam.SetPosition(*pos)
    cam.SetFocalPoint(*focal)
    cam.SetViewUp(*up)
    cam.SetViewAngle(angle)
    ren.ResetCameraClippingRange()
    rw.Render()
    w = vtkWindowToImageFilter()
    w.SetInput(rw)
    w.Update()
    p = vtkPNGWriter()
    p.SetFileName(os.path.join(OUT, fname))
    p.SetInputConnection(w.GetOutputPort())
    p.Write()
    rw.Finalize()
    print("->", fname)


def main():
    os.makedirs(OUT, exist_ok=True)
    G.build_parts()
    G.build_tripod()
    for fname, (az, el, _desc) in G.POSES.items():
        assy = G.build_assembly(az, el, fname)
        sun = sun_vector_yup(az, el)
        # la lumière rasante du pôle rend le sol noir : on relève un peu la lumière pour l'aperçu
        sun_draw = (sun[0], max(sun[1], 0.35), sun[2])
        n = math.sqrt(sum(v * v for v in sun_draw))
        sun_draw = tuple(v / n for v in sun_draw)
        ren = build_renderer(assy, sun_draw)
        tag = fname.replace("Tracker_Lunaire_", "").lower()
        f0 = (0, 650, 0)
        shoot(ren, f"apercu_{tag}_iso.png", (2700, 1800, 3000), focal=f0)
        shoot(ren, f"apercu_{tag}_face.png", (0, 1000, 4300), focal=f0)
        shoot(ren, f"apercu_{tag}_profil.png", (4300, 1000, 0), focal=f0)
        shoot(ren, f"apercu_{tag}_arriere.png", (-2600, 1900, -3100), focal=f0)
        shoot(ren, f"apercu_{tag}_detail_tete.png", (-640, 1170, -600), focal=(0, 950, 0), angle=32)
        shoot(ren, f"apercu_{tag}_detail_tete_avant.png", (-700, 1130, 720), focal=(0, 960, 0), angle=32)
        shoot(ren, f"apercu_{tag}_detail_pied.png", (1250, 750, 1750),
              focal=(0.866 * 800 * 0.8, 150, 0.5 * 800 * 0.8), angle=30)


if __name__ == "__main__":
    main()
