#!/usr/bin/env python3
"""
Images annotées pour le montage de la version PETG (docs/explications/) :
  - palier_joues_roulements.png : le palier d'une vis sans fin (semelle, joues, roulements,
    arbre, vis) ;
  - vis_sans_fin_moyeux.png : la vis sans fin imprimée seule (filet, moyeux, épaulements,
    trou de la vis sans tête, alésage) ;
  - axe_elevation.png : coupe par l'axe d'élévation (pivots imprimés Ø12, roulements 6801,
    bossages du chapeau, roue d'élévation, chapeau, bras de la chape) ;
  - eprouvette_ajustements.png : l'éprouvette de réglage, avec ce qu'on essaie dans chaque trou ;
  - fond_trepied_photo.png : demi-coupe du fond vissé sur un trépied photo (écrou 1/4" captif).
  - capteur_solaire.png et capteur_solaire_coupe.png : le capteur solaire (4 BPW34, croix d'ombre)
    sur son équerre, vissée sur le petit côté du cadre du panneau ; vue d'ensemble et coupe.
Sur serveur : xvfb-run -a python scripts/render_explications.py
"""

import math
import os

import cadquery as cq
from PIL import Image, ImageDraw, ImageFont
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import vtkCoordinate, vtkRenderWindow, vtkWindowToImageFilter

import generate_tracker as G
from render_apercu import build_renderer

OUT = os.path.join(G.RACINE, "docs", "explications")
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
    for i, y0 in enumerate(G.x_685(G.EL_VIS["palier"])):
        add("Roulement_685", G.trans(-30, y0, zv) * G.rot((0, 0, 1), 90), f"Roulement_{i}")
    add("Arbre_Vis_Elevation")
    add("Vis_Elevation", G.trans(-30, 0, zv) * G.rot((1, 0, 0), -90))
    rendu(a, "palier_joues_roulements.png", (130, zv + 60, 90), (-30, zv - 5, 0), 32, [
        ("Joue (paroi) de gauche :\nelle tient un roulement", yup((-30, -16.5, zv + 9)), (40, 60)),
        ("Joue (paroi) de droite :\nelle tient l'autre roulement", yup((-30, 16.5, zv + 9)), (1010, 60)),
        ("Roulement 685 (rose),\nprotégé : il dépasse\nde 1 mm côté vis", yup((-30, 13.0, zv + 5.2)), (1150, 540)),
        ("Lèvre de la joue : retient\nla bague extérieure seulement", yup((-30, -19, zv + 5.2)), (40, 880)),
        ("Arbre acier Ø5\n(tige achetée)", yup((-30, -30, zv + 2.4)), (40, 640)),
        ("Vis sans fin (imprimée)", yup((-30, 0, zv + 8.5)), (560, 150)),
        ("Semelle : vissée\nsur la chape", yup((-23, 0, G.Z_CHAPE + 10.5)), (1050, 900)),
    ])

    # 2. vis sans fin imprimée seule, axe horizontal
    b = cq.Assembly(name="vis")
    b.add(G.PARTS["Vis_Elevation"][0], name="vis_sans_fin", loc=G.rot((0, 1, 0), 90),
          color=cq.Color(0.75, 0.75, 0.78))
    e = G.EL_VIS["palier"][0] - G.LEVRE_685 - 0.15
    zh = (G.VIS_EL["moyeu"] + e - 0.6) / 2
    rendu(b, "vis_sans_fin_moyeux.png", (40, 72, 38), (1, 0, 0), 32, [
        ("Filet : la partie qui\nengrène avec la roue", (0, 9.2, 0), (560, 30)),
        ("Moyeu Ø12 (côté 1)", (-zh, 6, 0), (40, 230)),
        ("Moyeu Ø12 (côté 2)", (zh + 2.5, -1.0, 5.9), (1150, 420)),
        ("Trou de la vis sans tête M3\n(bloque la vis sur l'arbre)", (zh, 6.0, 0), (980, 40)),
        ("Épaulement Ø6,5 : appuie sur la\nbague intérieure du roulement,\npas sur sa flasque", (e, -2.2, 2.2), (880, 860)),
        ("Alésage Ø5,1 :\nl'arbre passe dedans", (e, 0.0, 0.0), (1180, 640)),
    ])
    # 3. coupe par l'axe d'élévation, panneau à plat (chapeau droit), moitié avant
    import generate_tete_vis_sans_fin as T
    import render_tete_vis_sans_fin as R
    T.build_parts()
    cut = R.coupe(T.build_head(0.0, 90.0, "tete", False), z=(-1e3, 0.0), y=(G.Z_CHAPE - 3, 1e3))
    zt, pv = G.Z_T, G.PV()
    rendu(cut, "axe_elevation.png", (25, zt + 45, 230), (0, zt - 12, 0), 42, [
        (f"Roulement {pv['ref']} (rose)\ndans le bras gauche", (-44.5, zt + 7.5, 0), (30, 40)),
        ("Roue d'élévation Z50\n(imprimée), calée sur\nle pivot par le méplat", (-30, zt + 20, 0), (560, 30)),
        (f"Pivot libre : PETG\nØ{pv['d']:g} (imprimé)", (49, zt + 2, 0), (1180, 40)),
        (f"Roulement {pv['ref']} (rose)\ndans le bras droit", (44.5, zt + 7.5, 0), (1180, 300)),
        (f"Pivot entraîné :\nPETG Ø{pv['d']:g} en D\n(imprimé, porte la roue)", (-37, zt + 2, 0), (30, 420)),
        ("Bossage du chapeau :\nappuie sur la bague\nintérieure seulement", (49.1, zt - 6.6, 0), (1180, 560)),
        ("Chapeau en U (bleu) :\nporte le panneau", (-53, zt - 12, 0), (30, 600)),
        ("Bras de la chape (jaune) :\nne tourne pas en élévation", (44, zt - 40, 0), (1090, 780)),
        ("Vis sans fin d'élévation :\nfait tourner la roue", (-30, G.z_vis_el() + 5, 0), (30, 900)),
    ])
    # 4. éprouvette de réglage des ajustements, paroi des trous horizontaux en goutte face à nous
    G.set_ajustements("petg")
    ep = T.eprouvette()
    c = cq.Assembly(name="eprouvette")
    c.add(ep, name="eprouvette_petg", loc=G.TO_YUP, color=cq.Color(0.93, 0.55, 0.20))
    aj, pv, rp = G.AJ, G.PV(), G.RP()
    def fr(v):
        return format(v, "g").replace(".", ",")
    rendu(c, "eprouvette_ajustements.png", (56, 150, 150), (56, 8, -36), 40, [
        (f"Trous horizontaux en goutte :\ncentrage moteur Ø{fr(aj['pilote'])}", (16, 25, -61.5), (30, 40)),
        (f"Logement de {pv['ref']}\n(horizontal)", (44, 24, -61.5), (480, 150)),
        ("Logement de 685\n(horizontal)", (68, 19, -61.5), (860, 40)),
        ("Pivot en D, méplat\nen bas (horizontal)", (92, 20, -61.5), (1180, 150)),
        (f"Téton de pivot Ø{fr(pv['d'] + aj['axe_imprime'])}\n(dans un {pv['ref']})", (104, 14, -46), (1180, 330)),
        ("3 logements de 685\n(jeu retenu, -0,1, +0,1)", (25, 6, -46), (30, 430)),
        (f"3 logements de {pv['ref']}\n(jeu retenu, -0,1, +0,1)", (42, 6, -16), (30, 860)),
        (f"Pivot en D Ø{fr(pv['d'] + aj['serrage'])}\n(trou vertical)", (57, 6, -46), (560, 960)),
        ("Téton du moyeu Ø29,95\n(dans un 6806)", (95, 14, -16), (1150, 880)),
    ])
    # 5. fond sur le trépied photo : demi-coupe par l'axe (écrou 1/4" captif, vis du trépied)
    G.set_ajustements("petg")
    T.build_parts()
    zb = G.z_fond_photo()
    garde = cq.Solid.makeBox(90, 45, 45, cq.Vector(-45, 0, -15))
    f = cq.Assembly(name="fond_photo")
    morceaux = [("Plateau_Trepied_Photo", cq.Location()), ("Fond_Socle", cq.Location()), ("Socle", cq.Location()),
                ("Ecrou_1_4_UNC", G.trans(0, 0, zb + G.TREPIED_PHOTO["plancher"]))]
    morceaux += [(G.nom_vis(t), G.loc_vis(pt, d)) for rp, t, pt, d in G.visserie() if rp == "fixe" and t == "M3x10"]
    for i, (n, loc) in enumerate(morceaux):
        sh = G.PARTS[n][0].val().moved(loc).intersect(garde)
        if sh.Volume() > 1e-3:
            f.add(sh, name=f"m{i}", loc=G.TO_YUP, color=G.PARTS[n][2])
    rendu(f, "fond_trepied_photo.png", (-60, 45, 150), (0, 2, 0), 34, [
        ("Écrou 1/4\"-20 pris dans son\nlogement hexagonal", (4.5, 3.5, 0), (900, 40)),
        ("Vis 1/4\" du trépied photo", (0, 1.5, 0), (560, 960)),
        ("Plateau du trépied", (-15, zb - 6, 0), (40, 760)),
        ("Fond imprimé : plancher de\n1,6 mm sous l'écrou", (-12, zb + 4, 0), (40, 500)),
        ("Vis M3×10, tête noyée,\nfond vissé sous le socle", (20, zb + 2, 0), (1050, 600)),
        ("Socle (imprimé)", (-29.5, 20, 0), (40, 60)),
    ])
    # 6. capteur solaire sur le petit côté du cadre : vue d'ensemble, puis coupe par 2 photodiodes
    G.set_ajustements("petg")
    G.PARTS.clear()
    G.build_head_parts()
    c, xc = G.CAPTEUR, G.X_CAPTEUR
    zd, xf = c["z"], G.P["pan_L"] / 2
    yd = G.xy_photodiodes()[0][1]

    def capteur(garde):
        a = cq.Assembly(name="capteur")
        for i, (n, s) in enumerate(G.flatten(G.build_panel(True))):
            sh = s.intersect(garde)
            k = G.part_key(n)
            col = cq.Color(0.30, 0.30, 0.32) if k == "Capteur_Solaire_Boitier" else G.PARTS[k][2]   # noir éclairci
            if sh.Volume() > 1e-3:
                a.add(sh, name=f"m{i}", loc=G.TO_YUP, color=col)
        return a
    w = c["mur"] / 2 + c["fenetre"]
    rendu(capteur(cq.Solid.makeBox(110, 120, 80, cq.Vector(xf - 53, -60, 30))), "capteur_solaire.png",
          (330, 200, 150), (192, 72, 0), 30, [
              (f"Croix d'ombre : {c['h']:g} mm de haut,\nparallèle à la normale du panneau",
               yup((xc, -8, zd + c["plancher"] + c["h"])), (960, 90)),
              (f"Fenêtre {fr(c['fenetre'])} × {fr(c['fenetre'])} mm au-dessus\nde chaque photodiode, contre la croix",
               yup((xc + w - 1.1, -w + 1.1, zd + c["plancher"])), (900, 950)),
              ("Boîtier imprimé\nen PETG noir", yup((xc + 16, 8, zd - 3)), (1180, 560)),
              ("Équerre imprimée", yup((xc - 4, -16, zd - c["corps"] - 2)), (560, 980)),
              ("Petit côté du cadre\n(côté du pivot libre)", yup((xf, -45, 62)), (40, 820)),
              ("Cellules : le capteur\nne leur fait pas d'ombre", yup((xf - 40, 30, 74.5)), (40, 300)),
          ])

    rendu(capteur(cq.Solid.makeBox(110, 60, 80, cq.Vector(xf - 38, yd, 30))), "capteur_solaire_coupe.png",
          (280, 120, 170), (192, 66, -yd), 30, [
              ("Photodiode BPW34 :\nentrée par en dessous,\npuce sous sa fenêtre",
               yup((xc + 3.6, yd, zd - 1.6)), (1170, 250)),
              ("Pattes et fils : par le\npassage de l'équerre",
               yup((xc - 2, yd, zd - c["corps"] - 3)), (1060, 800)),
              ("Vis M3×10 dans le cadre,\nécrou M3 à l'intérieur", yup((xf + c["ep"] + 1.5, c["vis_y"], c["z_vis"])),
               (40, 860)),
              ("Écrou M3 dans le cadre", yup((xf - 1.5, c["vis_y"] - 2.5, c["z_vis"])), (40, 640)),
              ("Croix d'ombre", yup((xc, yd, zd + 15)), (1100, 60)),
          ])
    G.set_ajustements("reel")


if __name__ == "__main__":
    main()
