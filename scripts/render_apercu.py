#!/usr/bin/env python3
"""
Rendus d'aperçu (PNG) du tracker lunaire, éclairé depuis la direction du Soleil.
Nécessite un affichage OpenGL ; sur serveur : xvfb-run -a python scripts/render_apercu.py
"""

import math
import os

import cadquery as cq
from cadquery.occ_impl.assembly import _loc2vtk
from PIL import Image, ImageDraw, ImageFont
from cadquery.occ_impl.exporters.vtk import extractEdgesFaces
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import (vtkActor, vtkLight, vtkPolyDataMapper,
                                         vtkRenderer, vtkRenderWindow,
                                         vtkWindowToImageFilter)
from vtkmodules.vtkRenderingOpenGL2 import vtkOpenGLRenderer  # noqa: F401 (charge le backend)

import generate_tracker as G

OUT = os.path.join(G.RACINE, "docs")
# code couleur de la visserie (comme dans les STEP) : vis en orange, rondelles et écrous en vert clair
VISSERIE = (("Vis", G.COL["vis"]), ("Rondelles et écrous", G.COL["rondelle"]))
RGB_VISSERIE = {tuple(round(v, 2) for v in c.toTuple()[:3]) for _t, c in VISSERIE}


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
        vis = tuple(round(v, 2) for v in c[:3]) in RGB_VISSERIE
        p = a.GetProperty()
        p.SetColor(*c[:3])
        p.SetAmbient(0.45 if vis else 0.12)          # visserie : couleur franche, même à l'ombre
        p.SetDiffuse(0.70 if vis else 0.85)
        p.SetSpecular(0.10 if vis else 0.35 if c[2] > c[0] else 0.15)
        p.SetSpecularPower(40)
        ren.AddActor(a)
        if edges or vis:
            me = vtkPolyDataMapper()
            me.SetInputData(d_edges)
            ae = vtkActor()
            ae.SetMapper(me)
            ae.SetPosition(*trans)
            ae.SetOrientation(*rot)
            ae.GetProperty().SetColor(0.05, 0.05, 0.05)
            ae.GetProperty().SetLineWidth(1.2 if vis else 0.6)      # contour net autour de la visserie
            ae.GetProperty().SetOpacity(0.9 if vis else 0.35)
            ren.AddActor(ae)
    if ground:
        g = vtkCylinderSource()
        g.SetRadius(1800)
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


def legende(path, fond=None, texte=None):
    """Ajoute sous l'image un bandeau avec le code couleur de la visserie. Par défaut, le bandeau
    prend la couleur du fond de l'image (coin bas gauche) et le texte contraste avec lui."""
    im = Image.open(path).convert("RGB")
    fond = fond or im.getpixel((2, im.height - 2))
    texte = texte or ((20, 20, 20) if sum(fond) > 3 * 128 else (235, 235, 235))
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except OSError:
        f = ImageFont.load_default()
    out = Image.new("RGB", (im.width, im.height + 64), fond)
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    x, y = 30, im.height + 14
    for txt, col in VISSERIE:
        d.rectangle([x, y, x + 34, y + 34], fill=tuple(round(255 * v) for v in col.toTuple()[:3]),
                    outline=texte, width=2)
        d.text((x + 48, y + 2), txt, fill=texte, font=f)
        x += 48 + d.textlength(txt, font=f) + 60
    out.save(path)


def shoot(ren, fname, pos, focal=(0, 900, 0), up=(0, 1, 0), size=(1600, 1200), angle=30, avec_legende=False):
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
    if avec_legende:
        legende(os.path.join(OUT, fname))
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
        f0 = (0, 420, 0)
        shoot(ren, f"apercu_{tag}_iso.png", (1900, 1250, 2150), focal=f0)
        shoot(ren, f"apercu_{tag}_face.png", (0, 700, 3000), focal=f0)
        shoot(ren, f"apercu_{tag}_profil.png", (3000, 700, 0), focal=f0)
        shoot(ren, f"apercu_{tag}_arriere.png", (-1800, 1300, -2150), focal=f0)
        shoot(ren, f"apercu_{tag}_detail_tete.png", (-640, 870, -600), focal=(0, 650, 0), angle=32,
              avec_legende=True)
        shoot(ren, f"apercu_{tag}_detail_tete_avant.png", (-700, 830, 720), focal=(0, 660, 0), angle=32,
              avec_legende=True)
        shoot(ren, f"apercu_{tag}_detail_pied.png", (1000, 430, 900), focal=(390, 70, 225), angle=30)

if __name__ == "__main__":
    main()
