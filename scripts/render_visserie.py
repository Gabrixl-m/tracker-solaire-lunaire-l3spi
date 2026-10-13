#!/usr/bin/env python3
"""
Images de la visserie (docs/visserie/, expliquées dans docs/visserie/README.md), avec le code
couleur des assemblages STEP : vis en orange, rondelles et écrous en vert clair. Dans les vues
éclatées, chaque vis est sortie de son trou le long de son axe (trait gris), chaque rondelle et
chaque écrou est écarté de son appui.
  - nomenclature.png : chaque modèle de vis, de rondelle et d'écrou, à la même échelle, avec sa
    quantité dans le cas réel et dans la démonstration PETG ;
  - tete_eclatee.png : la tête du cas réel, vue d'ensemble ;
  - chape_dessus_eclatee.png : paliers et supports sur la chape, rondelles sur les lumières ;
  - tete_dessous_eclatee.png : fond, roue d'azimut, vis posées par-dessous la chape ;
  - vis_sans_fin_blocage.png : la vis sans tête qui bloque une vis sans fin sur son arbre ;
  - panneau_eclate.png, panneau_rail_eclate.png : rails sur le chapeau, cadre du panneau sur les
    rails (laminé, cellules et boîte de jonction masqués pour voir les écrous) ;
  - capteur_eclate.png : capteur solaire sur le petit côté du cadre, coupé par l'axe d'une vis ;
  - demo_fond_eclate.png : fond de la démonstration PETG sur le trépied photo, en demi-coupe.
Sur serveur : xvfb-run -a python scripts/render_visserie.py
"""

import math
import os
import re
from collections import Counter

import cadquery as cq
from PIL import Image, ImageDraw, ImageFont
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import vtkCoordinate, vtkRenderWindow, vtkWindowToImageFilter

import generate_tete_vis_sans_fin as T
import generate_tracker as G
import render_explications as E
from render_apercu import build_renderer, legende

OUT = os.path.join(G.RACINE, "docs", "visserie")
GRIS = cq.Color(0.35, 0.35, 0.38)
ECART = {"Rondelle_M3": 5.0, "Ecrou_M3": 9.0, "Ecrou_1_4_UNC": 14.0}
MASQUE_TETE = ("Haut_Colonne_Trepied", "Rail_Panneau", "Vis_CHC_M3x14")   # rails : voir le panneau


def est_visserie(k):
    return k.startswith(("Vis_CHC_", "Vis_FHC_", "Vis_STHC_", "Rondelle_", "Ecrou_")) or k == "Vis_1_4_Trepied_Photo"


def longueur(k):
    return float(re.search(r"x(\d+(?:\.\d+)?)$", k).group(1))


def decalage(k):
    """Écart de la vue éclatée, dans le repère de la pièce : vis sorties de leur trou vers leur tête
    (+Z local ; +Y pour les vis sans tête, dans le repère de la vis sans fin), rondelles et écrous
    écartés de leur appui le long du même axe."""
    if k.startswith(("Vis_CHC_", "Vis_FHC_")):
        return (0, 0, longueur(k) + 10)
    if k.startswith("Vis_STHC_"):
        return (0, 10, 0)
    if k == "Vis_1_4_Trepied_Photo":
        return (0, 0, -18)
    return (0, 0, ECART[k]) if k in ECART else None


def eclater(assy, garde=None, masque=()):
    """Assemblage à plat, visserie écartée, axes en gris. Avec une garde (boîte), les pièces sont
    coupées par la boîte, sauf la visserie, gardée entière si elle la touche. Renvoie aussi, pour
    chaque pièce de visserie gardée, sa clé et un point où la viser une fois écartée : le dessous de
    la tête pour une vis CHC ou fraisée, le centre de la pièce sinon."""
    out = cq.Assembly(name="eclate")
    pos = []

    def forme(obj):
        return cq.Compound.makeCompound([s for s in obj.vals() if isinstance(s, cq.Shape)])

    def poser(obj, loc, col, entiere=False):
        sh = forme(obj).moved(loc)
        if garde is not None:
            coupe = sh.intersect(garde)
            if coupe.Volume() < 1e-3:
                return None
            sh = sh if entiere else coupe
        out.add(sh, name=f"m{len(out.children)}", color=col)
        return sh

    def walk(a, loc):
        cur = loc * a.loc
        if a.obj is not None:
            try:
                k = G.part_key(a.name)
            except KeyError:
                k = a.name
            d = decalage(k) if est_visserie(k) else None
            if k in masque:
                pass
            elif d is None:
                poser(a.obj, cur, a.color)
            else:
                loin = cur * G.trans(*d)
                sh = poser(a.obj, loin, a.color, entiere=True)
                if sh is not None:                 # axe : du centre de la pièce en place à sa position écartée
                    c0 = forme(a.obj).moved(cur).BoundingBox().center
                    u = loin.toTuple()[0]
                    o = cur.toTuple()[0]
                    n = math.sqrt(sum((x - y) ** 2 for x, y in zip(u, o)))
                    out.add(G.cyl_dir(0.5, n, c0.toTuple(), tuple((x - y) / n for x, y in zip(u, o))).val(),
                            name=f"m{len(out.children)}", color=GRIS)
                    tete = k.startswith(("Vis_CHC_", "Vis_FHC_"))
                    pos.append((k, loin.toTuple()[0] if tete else sh.BoundingBox().center.toTuple()))
        for ch in a.children:
            walk(ch, cur)
    walk(assy, cq.Location())
    return out, pos


def yup(p):
    return (p[0], p[2], -p[1])


def en_yup(assy, pos):
    """Assemblage et positions d'un repère Z-up passés dans le repère Y-up des rendus."""
    a = cq.Assembly(name="yup")
    a.add(assy, name="z_up", loc=G.TO_YUP)
    return a, [(k, yup(p)) for k, p in pos]


def plus_proche(pos, prefixe, cam):
    """Position de la pièce de visserie de ce type la plus proche du point cam."""
    pts = [p for k, p in pos if k.startswith(prefixe)]
    return min(pts, key=lambda p: sum((a - b) ** 2 for a, b in zip(p, cam)))


FORMES = {}                          # modèle de visserie -> (forme, couleur), du premier mode qui l'emploie


def quantites(mode):
    """Nombre de pièces de chaque modèle de visserie dans la tête (avec panneau) de ce mode."""
    G.set_ajustements(mode)
    T.build_parts()
    c = Counter()
    for n, _s in G.flatten(T.build_head(0.0, G.EL_REF, "q", True)):
        k = G.part_key(n)
        if est_visserie(k):
            m = "Vis_STHC_M3x4" if k.startswith("Vis_STHC_") else k
            c[m] += 1
            FORMES.setdefault(m, (G.PARTS[k][0].val(), G.PARTS[k][2]))
    return c


def nom(k):
    """Désignation sur deux lignes, pour la planche."""
    if k.startswith(("Vis_CHC_", "Vis_FHC_")):
        t = "Vis CHC" if k.startswith("Vis_CHC_") else "Vis fraisée"
        return t + "\n" + k[8:].replace("x", "×").replace(".", ",")
    return {"Vis_STHC_M3x4": "Vis sans\ntête M3×4", "Vis_1_4_Trepied_Photo": "Vis 1/4\"\ndu trépied",
            "Rondelle_M3": "Rondelle\nM3", "Ecrou_M3": "Écrou\nM3", "Ecrou_1_4_UNC": "Écrou\n1/4\"-20"}[k]


def rang(k):
    for i, p in enumerate(("Vis_CHC_M2", "Vis_CHC_", "Vis_FHC_", "Vis_STHC_", "Vis_1_4", "Rondelle_",
                           "Ecrou_M3", "Ecrou_1_4")):
        if k.startswith(p):
            return i, longueur(k) if p in ("Vis_CHC_", "Vis_FHC_") else 0
    raise KeyError(k)


def photo(assy, path, pos, focal, angle, points, size):
    """Rendu sur fond blanc ; renvoie la position à l'écran des points 3D demandés."""
    ren = build_renderer(assy, E.SUN, ground=False)
    ren.SetBackground(1, 1, 1)
    rw = vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetMultiSamples(8)
    rw.AddRenderer(ren)
    rw.SetSize(*size)
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
    pw = vtkPNGWriter()
    pw.SetFileName(path)
    pw.SetInputConnection(w2i.GetOutputPort())
    pw.Write()
    out = []
    for p3 in points:
        c = vtkCoordinate()
        c.SetCoordinateSystemToWorld()
        c.SetValue(*p3)
        x, y = c.GetComputedDisplayValue(ren)
        out.append((x, size[1] - y))
    rw.Finalize()
    return out


def nomenclature(q_reel, q_petg):
    """Planche : chaque modèle debout (tête en haut), rondelles et écrous inclinés vers l'objectif."""
    ordre = sorted({*q_reel, *q_petg}, key=rang)
    a = cq.Assembly(name="nomenclature")
    pas = 23.0
    for i, k in enumerate(ordre):
        s, col = FORMES[k]
        bb = s.BoundingBox()
        if k == "Vis_STHC_M3x4":         # dans le repère de la vis sans fin : axe selon Y, bout plat en bas
            loc = G.rot((1, 0, 0), 90) * G.trans(-bb.center.x, -bb.ymin, -bb.center.z)
        elif k == "Vis_1_4_Trepied_Photo":
            loc = G.trans(0, 0, -bb.zmax)
        elif k.startswith(("Rondelle_", "Ecrou_")):
            loc = G.trans(0, 0, -4) * G.rot((1, 0, 0), 65) * G.trans(0, 0, -bb.center.z)
        else:
            loc = cq.Location()
        a.add(s.moved(G.TO_YUP * G.trans(i * pas, 0, 0) * loc), name=k, color=col)
    xm = (len(ordre) - 1) * pas / 2
    path = os.path.join(OUT, "nomenclature.png")
    W, H = 1800, 660
    ecran = photo(a, path, (xm, 22, 310), (xm, -17, 0), 21.2, [(i * pas, -29.0, 0.0) for i in range(len(ordre))],
                  (W, H))
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    f2 = ImageFont.truetype("DejaVuSans.ttf", 19)
    ft = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
    d.text((40, 30), f"Visserie de la tête, à la même échelle ({pas:g} mm d'une pièce à l'autre)",
           fill=(20, 20, 20), font=ft)
    for k, (x0, y0) in zip(ordre, ecran):
        txt = nom(k)
        bb = d.multiline_textbbox((0, 0), txt, font=f, align="center")
        d.multiline_text((x0 - (bb[2] - bb[0]) / 2, y0), txt, fill=(20, 20, 20), font=f, align="center",
                         spacing=6)
        y1 = y0 + bb[3] + 16
        for t in (f"réel : {q_reel.get(k, 0)}", f"PETG : {q_petg.get(k, 0)}"):
            d.text((x0 - d.textlength(t, font=f2) / 2, y1), t, fill=(70, 70, 70), font=f2)
            y1 += 27
    im.save(path)
    legende(path)
    print("->", path)


def rendu(assy, fname, cam, focal, angle, etiquettes):
    E.rendu(assy, fname, cam, focal, angle, etiquettes, dossier=OUT, avec_legende=True)


def vis_sans_fin():
    """Vis sans fin d'élévation sur son arbre, entre ses roulements, vis de blocage vers le haut."""
    a = cq.Assembly(name="vis_sans_fin")
    zv = G.z_vis_el()
    loc = G.trans(-30, 0, zv) * G.rot((1, 0, 0), -90) * G.rot((0, 0, 1), 180)    # trou de la vis vers +Z
    for i, y0 in enumerate(G.x_685(G.EL_VIS["palier"])):
        G.add(a, "Roulement_685", G.trans(-30, y0, zv) * G.rot((0, 0, 1), 90), f"Roulement_685_{i}")
    G.add(a, "Arbre_Vis_Elevation")
    G.add(a, "Vis_Elevation", loc)
    G.add(a, "Vis_STHC_M3x4_El", loc)
    return a


def main():
    os.makedirs(OUT, exist_ok=True)
    q_reel, q_petg = quantites("reel"), quantites("petg")
    nomenclature(q_reel, q_petg)

    # tête du cas réel, sans panneau ni rails, en vue éclatée
    G.set_ajustements("reel")
    T.build_parts()
    tete, pos = eclater(T.build_head(0.0, G.EL_REF, "tete", False), masque=MASQUE_TETE)
    cam = (300, 270, 330)
    rendu(tete, "tete_eclatee.png", cam, (-12, 86, 12), 32, [
        ("Vis CHC M3×12 et rondelle M3 :\npaliers d'azimut sur la chape", plus_proche(pos, "Rondelle_M3", cam),
         (1000, 40)),
        ("Vis CHC M3×8 :\nmoteur d'élévation", plus_proche(pos, "Vis_CHC_M3x8", (0, 140, 40)), (40, 40)),
        ("Vis CHC M3×12 par-dessous :\nsupports et palier\nd'élévation", plus_proche(pos, "Vis_CHC_M3x12", (-80, 0, 80)),
         (40, 620)),
        ("Vis CHC M3×6 : arrêt\nen rotation sur la colonne", plus_proche(pos, "Vis_CHC_M3x6", cam), (40, 900)),
        ("Vis CHC M3×25 :\nfond sous le socle", plus_proche(pos, "Vis_CHC_M3x25", cam), (1150, 900)),
    ])
    cam = (95, 225, 150)
    rendu(tete, "chape_dessus_eclatee.png", cam, (-15, 108, 26), 30, [
        ("Vis CHC M3×12 (orange)", plus_proche(pos, "Vis_CHC_M3x12", (20, 125, 30)), (1050, 300)),
        ("Rondelle M3 (vert clair) : sous\nla tête, sur la lumière du palier", plus_proche(pos, "Rondelle_M3", cam),
         (900, 920)),
        ("Vis CHC M3×8 :\nmoteur d'élévation", plus_proche(pos, "Vis_CHC_M3x8", cam), (40, 40)),
    ])
    cam = (240, -110, 240)
    rendu(tete, "tete_dessous_eclatee.png", cam, (-12, 38, 10), 34, [
        ("Vis fraisée M3×8 :\nroue d'azimut sur le socle", plus_proche(pos, "Vis_FHC_M3x8", cam), (1080, 300)),
        ("Vis CHC M3×25 :\nfond sous le socle", plus_proche(pos, "Vis_CHC_M3x25", cam), (1080, 900)),
        ("Vis CHC M2,5×6 :\nmoteur d'azimut (NEMA 11)", plus_proche(pos, "Vis_CHC_M2.5x6", cam), (40, 620)),
        ("Vis CHC M3×12 par-dessous :\nsupports et palier d'élévation", plus_proche(pos, "Vis_CHC_M3x12", cam),
         (40, 40)),
        ("Vis CHC M3×6 : arrêt\nen rotation sur la colonne", plus_proche(pos, "Vis_CHC_M3x6", cam), (40, 900)),
    ])
    vsf, pos = en_yup(*eclater(vis_sans_fin()))
    zv = G.z_vis_el()
    zh = (G.VIS_EL["moyeu"] + G.EL_VIS["palier"][0] - G.LEVRE_685 - 0.15 - 0.6) / 2    # trou (cf. p_vis_pression)
    rendu(vsf, "vis_sans_fin_blocage.png", (40, zv + 62, 70), (-30, zv + 6, 0), 27, [
        ("Vis sans tête M3×4 (orange) : vissée\ndans le moyeu, son bout plat serre\nle méplat de l'arbre",
         plus_proche(pos, "Vis_STHC", (0, 0, 0)), (40, 40)),
        ("Trou taraudé M3\ndu moyeu", yup((-30, zh, zv + 6)), (1150, 330)),
        ("Vis sans fin d'élévation", yup((-30, -3, zv + 8.5)), (1050, 120)),
        ("Arbre Ø5 : limer un méplat\nde 0,5 mm sous la vis", yup((-30, -24, zv + 2.5)), (40, 860)),
        ("Roulement 685 (rose)", yup((-30, G.x_685(G.EL_VIS["palier"])[1], zv + 5.5)), (1050, 860)),
    ])

    # panneau, laminé masqué : vue d'ensemble des rails, puis un bout de rail et le capteur solaire
    masque = ("Lamine_PV", "Cellules_PV", "Boite_Jonction")
    xf, yf, zb = G.P["pan_L"] / 2, G.Y_FIX_PANNEAU, G.P["pan_back"]
    garde = cq.Solid.makeBox(170, 280, 100, cq.Vector(-85, -140, 0))
    pan, pos = en_yup(*eclater(G.build_panel(True), garde=garde, masque=masque))
    cam = (230, 260, 300)
    rendu(pan, "panneau_eclate.png", cam, (0, 40, -10), 35, [
        ("Vis CHC M3×14 (orange) par-dessus :\nrail sur le chapeau, tête noyée\nsous le panneau",
         plus_proche(pos, "Vis_CHC_M3x14", (G.RAIL_X, 100, 14)), (40, 40)),
        ("Écrou M3 (vert clair) :\ndans le cadre", plus_proche(pos, "Ecrou_M3", (G.RAIL_X, 100, -yf)), (1100, 40)),
        ("Vis CHC M3×14 par-dessous :\ncadre sur le rail", plus_proche(pos, "Vis_CHC_M3x14", (G.RAIL_X, 0, yf)),
         (1050, 900)),
        ("Chapeau (bleu)", yup((0, 0, G.U_TOP[0])), (40, 900)),
    ])
    garde = cq.Solid.makeBox(60, 50, 100, cq.Vector(G.RAIL_X - 30, yf - 40, -10))
    pan, pos = en_yup(*eclater(G.build_panel(True), garde=garde, masque=masque))
    cam = (G.RAIL_X + 75, 75, -yf + 105)
    rendu(pan, "panneau_rail_eclate.png", cam, (G.RAIL_X, 40, -yf), 34, [
        ("Écrou M3 (vert clair) : posé sur\nl'aile arrière du cadre", plus_proche(pos, "Ecrou_M3", cam), (40, 40)),
        ("Vis CHC M3×14 (orange) par-dessous :\nsa tête se noie dans le rail", plus_proche(pos, "Vis_CHC_M3x14", cam),
         (40, 900)),
        ("Aile arrière du cadre", yup((G.RAIL_X + 22, yf - 4, zb + 1.5)), (1100, 330)),
        ("Rail", yup((G.RAIL_X + 6, yf - 25, 40)), (1250, 700)),
    ])
    garde = cq.Solid.makeBox(90, 50, 90, cq.Vector(xf - 40, -G.CAPTEUR["vis_y"], 25))   # coupe par l'axe d'une vis
    cap, pos = en_yup(*eclater(G.build_panel(True), garde=garde, masque=masque))
    c = G.CAPTEUR
    cam = (xf + 25, 140, 190)
    rendu(cap, "capteur_eclate.png", cam, (xf + 12, 64, 0), 25, [
        ("Écrou M3 (vert clair) :\nà l'intérieur du cadre", plus_proche(pos, "Ecrou_M3", cam), (40, 40)),
        ("Vis CHC M3×10 (orange) : équerre\nsur le petit côté du cadre",
         plus_proche(pos, "Vis_CHC_M3x10", (xf + 30, c["z_vis"], 0)), (1000, 40)),
        ("Vis CHC M3×10 par-dessous :\nboîtier sur l'équerre", plus_proche(pos, "Vis_CHC_M3x10", (xf + 20, 0, 0)),
         (1000, 900)),
        ("Petit côté du cadre\n(en coupe)", yup((xf - 0.75, -c["vis_y"], c["z_vis"] - 8)), (40, 900)),
    ])

    # démonstration PETG : fond sur le trépied photo, demi-coupe
    G.set_ajustements("petg")
    T.build_parts()
    garde = cq.Solid.makeBox(110, 90, 60, cq.Vector(-55, -50, -60))
    fond, pos = eclater(T.build_head(0.0, G.EL_REF, "demo", False), garde=garde)
    cam = (-70, 40, 170)
    rendu(fond, "demo_fond_eclate.png", cam, (0, -5, 0), 38, [
        ("Écrou 1/4\"-20 (vert clair) :\nposé dans son logement\nhexagonal du fond", plus_proche(pos, "Ecrou_1_4", cam),
         (1080, 40)),
        ("Vis 1/4\" du trépied photo (orange)", plus_proche(pos, "Vis_1_4", cam), (900, 940)),
        ("Vis CHC M3×10 (orange) :\nfond sous le socle", plus_proche(pos, "Vis_CHC_M3x10", cam), (40, 900)),
        ("Vis CHC M3×8 : rondelle\nd'arrêt sous le moyeu", plus_proche(pos, "Vis_CHC_M3x8", cam), (40, 300)),
        ("Plateau du trépied photo", (-20, G.z_fond_photo() - 5, -10), (40, 700)),
        ("Socle (imprimé)", (30, 20, -5), (1250, 420)),
        ("Fond (imprimé)", (-25, -1, -5), (40, 520)),
    ])
    G.set_ajustements("reel")


if __name__ == "__main__":
    main()
