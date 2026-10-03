#!/usr/bin/env python3
"""
Images annotées pour le montage de la version PETG (docs/explications/) :
  - palier_joues_roulements.png : le palier d'une vis sans fin (semelle, joues, roulements,
    arbre, vis) ;
  - vis_sans_fin_moyeux.png : la vis sans fin imprimée seule (filet, moyeux, épaulements,
    trou de la vis sans tête, alésage).
Sur serveur : xvfb-run -a python render_explications.py
"""

import math
import os

import cadquery as cq
from PIL import Image, ImageDraw, ImageFont
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import vtkCoordinate, vtkRenderWindow, vtkWindowToImageFilter

import generate_tracker as G
from render_apercu import build_renderer

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "explications")
SUN = tuple(v / math.sqrt(0.5 ** 2 + 0.8 ** 2 + 0.6 ** 2) for v in (0.5, 0.8, 0.6))
W, H = 1600, 1100
ROUGE = (200, 0, 60)

_maillage = cq.Shape.toVtkPolyData
cq.Shape.toVtkPolyData = lambda self, *a, **k: _maillage(self, 0.02, 0.08)   # maillage fin : petits trous visibles


def rendu(assy, fname, pos, focal, angle, etiquettes):
    """Rendu sur fond blanc, puis étiquettes (texte, point 3D en repère Y-up, coin du texte)."""
    ren = build_renderer(assy, SUN, ground=False)
    ren.SetBackground(1, 1, 1)
    rw = vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetMultiSamples(8)
    rw.AddRenderer(ren)
    rw.SetSize(W, H)
    cam = ren.GetActiveCamera()
    cam.SetPosition(*pos)
    cam.SetFocalPoint(*focal)
    cam.SetViewUp(0, 1, 0)
    cam.SetViewAngle(angle)
    ren.ResetCameraClippingRange()
    rw.Render()
    w2i = vtkWindowToImageFilter()
    w2i.SetInput(rw)
    w2i.Update()
    path = os.path.join(OUT, fname)
    pw = vtkPNGWriter()
    pw.SetFileName(path)
    pw.SetInputConnection(w2i.GetOutputPort())
    pw.Write()
    pts = []
    for txt, p3, coin in etiquettes:
        c = vtkCoordinate()
        c.SetCoordinateSystemToWorld()
        c.SetValue(*p3)
        x, y = c.GetComputedDisplayValue(ren)
        pts.append((txt, (x, H - y), coin))
    rw.Finalize()
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
    except OSError:
        f = ImageFont.load_default()
    for txt, (x, y), (tx, ty) in pts:
        dx, dy = x - tx, y - ty
        n = max(1.0, math.hypot(dx, dy))
        d.line([(tx, ty), (x - 16 * dx / n, y - 16 * dy / n)], fill=ROUGE, width=4)
        d.ellipse([x - 16, y - 16, x + 16, y + 16], outline=ROUGE, width=4)
        bb = d.multiline_textbbox((tx, ty), txt, font=f)
        d.rectangle([bb[0] - 8, bb[1] - 6, bb[2] + 8, bb[3] + 6], fill=(255, 255, 255), outline=ROUGE, width=3)
        d.multiline_text((tx, ty), txt, fill=(20, 20, 20), font=f)
    im.save(path)
    print("->", path)


def yup(p):
    """Repère tête Z-up -> repère Y-up des rendus."""
    return (p[0], p[2], -p[1])


def main():
    os.makedirs(OUT, exist_ok=True)
    G.set_ajustements("petg")
    G.PARTS.clear()
    G.build_head_parts()

    # 1. palier d'élévation monté
    zv = G.z_vis_el()
    a = cq.Assembly(name="palier")

    def add(n, loc=None, inst=None):
        a.add(G.PARTS[n][0], name=inst or n, loc=G.TO_YUP * (loc or cq.Location()), color=G.PARTS[n][2])
    add("Palier_Vis_Elevation")
    for i, y0 in enumerate((G.EL_VIS["palier"][0], -G.EL_VIS["palier"][1])):
        add("Roulement_685", G.trans(-30, y0, zv) * G.rot((0, 0, 1), 90), f"Roulement_{i}")
    add("Arbre_Vis_Elevation")
    add("Vis_Elevation", G.trans(-30, 0, zv) * G.rot((1, 0, 0), -90))
    rendu(a, "palier_joues_roulements.png", (130, zv + 60, 90), (-30, zv - 5, 0), 32, [
        ("Joue (paroi) de gauche :\nelle tient un roulement", yup((-30, -16.5, zv + 9)), (40, 60)),
        ("Joue (paroi) de droite :\nelle tient l'autre roulement", yup((-30, 16.5, zv + 9)), (1010, 60)),
        ("Roulement 685 (rose)\nemmanché dans la joue", yup((-30, -19, zv + 4.5)), (40, 330)),
        ("Arbre acier Ø5\n(tige achetée)", yup((-30, -30, zv + 2.4)), (40, 640)),
        ("Vis sans fin (imprimée)", yup((-30, 0, zv + 8.5)), (560, 150)),
        ("Semelle : vissée\nsur la chape", yup((-23, 0, G.Z_CHAPE + 10.5)), (1050, 900)),
    ])

    # 2. vis sans fin imprimée seule, axe horizontal
    b = cq.Assembly(name="vis")
    b.add(G.PARTS["Vis_Elevation"][0], name="vis_sans_fin", loc=G.rot((0, 1, 0), 90),
          color=cq.Color(0.75, 0.75, 0.78))
    e = G.EL_VIS["palier"][0] - 0.15
    zh = (G.VIS_EL["moyeu"] + e - 0.6) / 2
    rendu(b, "vis_sans_fin_moyeux.png", (40, 72, 38), (1, 0, 0), 32, [
        ("Filet : la partie qui\nengrène avec la roue", (0, 9.2, 0), (560, 30)),
        ("Moyeu Ø12 (côté 1)", (-zh, 6, 0), (40, 230)),
        ("Moyeu Ø12 (côté 2)", (zh + 2.5, -1.0, 5.9), (1150, 420)),
        ("Trou de la vis sans tête M3\n(bloque la vis sur l'arbre)", (zh, 6.0, 0), (980, 40)),
        ("Épaulement Ø6,5 : appuie sur\nla bague intérieure du roulement", (e, -2.2, 2.2), (880, 900)),
        ("Alésage Ø5,1 :\nl'arbre passe dedans", (e, 0.0, 0.0), (1180, 640)),
    ])
    G.set_ajustements("reel")


if __name__ == "__main__":
    main()
