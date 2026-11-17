#!/usr/bin/env python3
"""
Aperçus de la variante terrestre à moteurs 28BYJ-48 (document caché .variante_28BYJ-48/README.md),
écrits dans .variante_28BYJ-48/apercus/.
Sur serveur : xvfb-run -a python scripts/render_variante_28byj.py
"""
import math
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_tete_vis_sans_fin as T
import generate_tracker as G
import generate_variante_28byj as V
import render_apercu as RA
from render_apercu import build_renderer, shoot
from render_tete_vis_sans_fin import coupe

SUN = tuple(v / math.sqrt(0.5 ** 2 + 0.8 ** 2 + 0.6 ** 2) for v in (0.5, 0.8, 0.6))
RA.OUT = os.path.join(V.OUT, "apercus")
os.makedirs(RA.OUT, exist_ok=True)


def plateau():
    """Les cinq pièces propres à la variante, orientées pour l'impression, sur deux rangs."""
    assy = cq.Assembly(name="plateau")
    x = y = rang = 0.0
    larg = 0.0
    for name in V.PIECES_VARIANTE:
        wp = T.a_plat(G.PARTS[name][0], T.ORIENTATION[name])
        bb = wp.val().BoundingBox()
        if x + bb.xlen > 330:
            larg, x, y, rang = max(larg, x), 0.0, y + rang + 25, 0.0
        assy.add(wp, name=name, loc=G.TO_YUP * G.trans(x + bb.xlen / 2, -(y + bb.ylen / 2), 0),
                 color=cq.Color(0.95, 0.45, 0.10))
        x += bb.xlen + 25
        rang = max(rang, bb.ylen)
    larg = max(larg, x)
    prof = y + rang
    r = build_renderer(assy, SUN, ground=False)
    shoot(r, "variante_pieces_a_imprimer.png", (larg / 2, 0.9 * larg, prof / 2 + 0.6 * larg),
          focal=(larg / 2, 0, prof / 2), angle=40)


def main():
    V.construire()
    zv, yf = G.z_vis_el(), G.EL_VIS["y_face"]
    xf, ya, za = G.AZ_VIS["x_face"], G.y_vis_az(), G.AZ_VIS["z"]
    fy = (G.Z_CHAPE + G.Z_T) / 2
    avec = T.build_head(0.0, G.EL_REF, "avec_panneau", True)
    r = build_renderer(avec, SUN, ground=False)
    shoot(r, "variante_avec_panneau.png", (620, 430, 760), focal=(0, 130, 0), angle=30)
    head = T.build_head(0.0, G.EL_REF, "tete", False)
    r = build_renderer(head, SUN, ground=False)
    shoot(r, "variante_iso.png", (330, 280, 400), focal=(-5, fy, 15), angle=36, avec_legende=True)
    shoot(r, "variante_cote_moteurs.png", (-380, 260, 330), focal=(-5, fy, 15), angle=36, avec_legende=True)
    shoot(r, "variante_contrepoids.png", (330, 100, 260), focal=(70, 60, 0), angle=40, avec_legende=True)
    # détails des deux moteurs (repère Y-up exporté : x -> x, z -> y, y -> -z)
    shoot(r, "variante_detail_moteur_elevation.png", (-130, 215, 150), focal=(-30, zv, -yf), angle=34,
          avec_legende=True)
    shoot(r, "variante_detail_moteur_azimut.png", (-150, 130, 130), focal=(xf, za, -ya), angle=34,
          avec_legende=True)
    # coupes dans l'axe de chaque moteur (vues du côté de la face coupée) : bossage, lamage, accouplement
    r = build_renderer(coupe(head, x=(-1e3, -30.0)), SUN, ground=False)
    shoot(r, "variante_coupe_elevation.png", (150, zv + 30, -yf + 20), focal=(-30, zv, -yf + 5), angle=30,
          avec_legende=True)
    r = build_renderer(coupe(head, z=(-ya, 1e3)), SUN, ground=False)
    shoot(r, "variante_coupe_azimut.png", (xf + 20, za + 30, -ya - 190), focal=(xf + 8, za, -ya), angle=30,
          avec_legende=True)
    plateau()
    G.set_variante(None)
    G.set_ajustements("reel")


if __name__ == "__main__":
    main()
