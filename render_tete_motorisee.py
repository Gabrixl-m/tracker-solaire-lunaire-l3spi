#!/usr/bin/env python3
"""
Rendus des deux têtes motorisées (vis sans fin, engrenages droits), dont deux vues en coupe.
Sur serveur : xvfb-run -a python render_tete_motorisee.py [VSF] [ENG]
"""

import math
import sys

import cadquery as cq

import generate_tete_motorisee as T
import generate_tracker as G
from render_apercu import build_renderer, shoot

SUN = tuple(v / math.sqrt(0.5 ** 2 + 0.8 ** 2 + 0.6 ** 2) for v in (0.5, 0.8, 0.6))
PREFIX = {"VSF": "tete_vis_sans_fin", "ENG": "tete_engrenages"}


def coupe(assy, x=(-1e3, 1e3), y=(-1e3, 1e3), z=(-1e3, 1e3)):
    """Assemblage limité à une boîte (repère Y-up exporté) : vue en coupe."""
    cut = cq.Assembly(name="coupe")
    keep = cq.Solid.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], cq.Vector(x[0], y[0], z[0]))
    for i, (n, s) in enumerate(G.flatten(assy)):
        k = T.inst_part(n)
        if k is None or k == "Haut_Colonne_Trepied":
            continue
        part = s.intersect(keep)
        if part.Volume() < 1e-3:
            continue
        cut.add(part, name=f"p{i}", color=T.PARTS[k][2])
    return cut


def rendre(vk):
    V = T.preparer(vk)
    pre = PREFIX[vk]
    fy = (V["Z_CHAPE"] + V["Z_T"]) / 2                    # hauteur du centre de la tête (Y-up)
    with_pan = T.build_head(0.0, T.EL_REF, "avec_panneau", True)
    r = build_renderer(with_pan, SUN, ground=False)
    shoot(r, f"{pre}_avec_panneau.png", (620, 430, 760), focal=(0, 130, 0), angle=30)
    r = build_renderer(with_pan, (-SUN[0], SUN[1], -SUN[2]), ground=False)   # éclairé côté cellules
    shoot(r, f"{pre}_avec_panneau_face.png", (-560, 380, -680), focal=(0, 130, 0), angle=30)

    head = T.build_head(0.0, T.EL_REF, "tete", False)
    r = build_renderer(head, SUN, ground=False)
    shoot(r, f"{pre}_iso.png", (330, 280, 400), focal=(-5, fy, 15), angle=36)
    shoot(r, f"{pre}_cote_moteurs.png", (-380, 260, 330), focal=(-5, fy, 15), angle=36)
    # coupe dans le plan de la roue d'élévation (x = -30 : axe de la vis ou du pignon)
    r = build_renderer(coupe(head, x=(-1e3, -30.0)), SUN, ground=False)
    shoot(r, f"{pre}_coupe_elevation.png", (420, 190, 160), focal=(-30, V["Z_T"] - 25, 0), angle=34)
    # coupe horizontale dans le plan de la denture d'azimut, vue de dessus
    z_az = T.AZ_VSF["z"] if vk == "VSF" else 72.0
    r = build_renderer(coupe(head, y=(-1e3, z_az)), SUN, ground=False)
    shoot(r, f"{pre}_coupe_azimut.png", (120, 330, 260), focal=(-10, z_az - 10, 20), angle=34)


if __name__ == "__main__":
    for vk in [a for a in sys.argv[1:] if a in T.VERSIONS] or list(T.VERSIONS):
        rendre(vk)
