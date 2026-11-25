#!/usr/bin/env python3
"""
Aperçus de la tête à fourche du cas terrestre (Fichiers 3D (CAO)/Cas Terrestre (démonstration)/), écrits dans docs (extra)/.
Sur serveur : xvfb-run -a python scripts/render_fourche.py
"""
import math
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_fourche as F
import generate_tracker as G
import generate_tete_vis_sans_fin as T
import render_apercu as RA
from render_apercu import build_renderer, shoot

SUN = tuple(v / math.sqrt(0.5 ** 2 + 0.8 ** 2 + 0.6 ** 2) for v in (0.5, 0.8, 0.6))
os.makedirs(RA.OUT, exist_ok=True)


def cam(f, off, k):
    return tuple(f[i] + k * off[i] for i in range(3))


def plateau():
    """Pièces PETG à imprimer, dans leur orientation d'impression, rangées sur un plateau."""
    orient = dict(T.ORIENTATION)
    orient.update(F.ORIENT)
    assy = cq.Assembly(name="plateau")
    x = y = rang = 0.0
    larg = 0.0
    for n in F.IMPRIMEES:
        wp = T.a_plat(G.PARTS[n][0], orient[n])
        bb = wp.val().BoundingBox()
        if x + bb.xlen > 520:
            larg, x, y, rang = max(larg, x), 0.0, y + rang + 25, 0.0
        assy.add(wp, name=n, loc=G.TO_YUP * G.trans(x + bb.xlen / 2, -(y + bb.ylen / 2), 0), color=cq.Color(0.95, 0.45, 0.10))
        x += bb.xlen + 25
        rang = max(rang, bb.ylen)
    larg = max(larg, x)
    prof = y + rang
    r = build_renderer(assy, SUN, ground=False)
    shoot(r, "fourche_pieces_a_imprimer.png", (larg / 2, 0.95 * larg, prof / 2 + 0.55 * larg), focal=(larg / 2, 0, prof / 2), angle=40)


def tete(zv, zb, ph, el, panneau=True):
    root = cq.Assembly(name="tete")
    root.add(F.assembler(zv, zb, el, 0.0, panneau, True, ph), name="Tete", loc=G.TO_YUP)
    return root


def main():
    zb, zv, _xr = F.construire()
    ph, _a, _b = F.calage(zv)
    zt = F.ZT
    plateau()
    F0 = (0, zt - 20, 0)
    r = build_renderer(tete(zv, zb, ph, 40.0), SUN, ground=False)
    shoot(r, "fourche_iso.png", cam(F0, (900, 280, 1000), 0.55), focal=F0, angle=34)
    shoot(r, "fourche_arriere.png", cam(F0, (-850, 240, -950), 0.55), focal=F0, angle=34)
    shoot(r, "fourche_cote.png", cam(F0, (1300, 20, 80), 0.5), focal=F0, angle=34)
    F1 = (225, zt - 30, -10)
    shoot(r, "fourche_detail_elevation.png", cam(F1, (330, 60, 360), 0.8), focal=F1, angle=34, avec_legende=True)
    F2 = (-45, 80, 45)
    shoot(r, "fourche_detail_azimut.png", cam(F2, (-300, 70, 280), 0.8), focal=F2, angle=34, avec_legende=True)
    r = build_renderer(tete(zv, zb, ph, 40.0, False), SUN, ground=False)
    shoot(r, "fourche_structure.png", cam((0, zt - 70, 0), (780, 190, 900), 0.55), focal=(0, zt - 70, 0), angle=34, avec_legende=True)
    for el, nom in ((-2.0, "vertical"), (92.0, "a_plat")):
        r = build_renderer(tete(zv, zb, ph, el), SUN, ground=False)
        shoot(r, f"fourche_{nom}.png", cam(F0, (900, 280, 1000), 0.55), focal=F0, angle=34)
    trepied(zv, zb, ph)


def trepied(zv, zb, ph):
    import generate_demo_trepied as D
    noms = D.enregistrer_trepied()
    D.enregistrer_lest()

    def assemblage(az, el, noms_, name="Demo_Trepied", lest=True):
        root = cq.Assembly(name=name)
        tr = cq.Assembly(name="SA_Trepied")
        for n in noms_:
            G.add(tr, n)
        root.add(tr, name="SA_Trepied", loc=G.TO_YUP)
        if lest and D.NOMS_LEST[0] in G.PARTS:
            ls = cq.Assembly(name="SA_Lest")
            for n in D.NOMS_LEST:
                G.add(ls, n)
            root.add(ls, name="SA_Lest", loc=G.TO_YUP)
        root.add(F.assembler(zv, zb, el, az, True, True, ph), name="Tete", loc=G.TO_YUP * G.trans(0, 0, D.z_tete()))
        return root

    D.assemblage = assemblage
    bp0, pb0 = G.build_panel, G.P["pan_back"]
    G.build_panel = lambda with_panel=True: F.panneau_assy(True, False)
    G.P["pan_back"] = -G.P["pan_T"] / 2
    try:
        pre = "demo_trepied_"
        sun = tuple(v / math.sqrt(0.45 ** 2 + 0.75 ** 2 + 0.6 ** 2) for v in (0.45, 0.75, -0.6))
        assy = assemblage(0.0, 40.0, noms)
        r = build_renderer(assy, sun)
        r.SetBackground(0.80, 0.86, 0.93)
        f0 = (0, 520, 0)
        shoot(r, pre + "iso.png", (1350, 1050, -1500), focal=f0, angle=34)
        shoot(r, pre + "profil.png", (2300, 560, 0), focal=f0, angle=30)
        shoot(r, pre + "arriere.png", (-1200, 1000, 1500), focal=f0, angle=34)
        r = build_renderer(assy, sun, ground=False)
        r.SetBackground(0.80, 0.86, 0.93)
        shoot(r, pre + "detail.png", (-560, 900, 520), focal=(0, 720, 0), angle=30, avec_legende=True)
        shoot(r, pre + "lest.png", (620, 420, -640), focal=(0, 90, 0), angle=30)
    finally:
        G.build_panel, G.P["pan_back"] = bp0, pb0


if __name__ == "__main__":
    main()
