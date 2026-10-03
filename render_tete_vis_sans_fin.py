#!/usr/bin/env python3
"""
Rendus de la tête rotative à vis sans fin seule, dont deux vues en coupe.
Sur serveur : xvfb-run -a python render_tete_vis_sans_fin.py
"""

import math

import cadquery as cq

import generate_tete_vis_sans_fin as T
import generate_tracker as G
from render_apercu import build_renderer, shoot

SUN = tuple(v / math.sqrt(0.5 ** 2 + 0.8 ** 2 + 0.6 ** 2) for v in (0.5, 0.8, 0.6))


def coupe(assy, x=(-1e3, 1e3), y=(-1e3, 1e3), z=(-1e3, 1e3)):
    """Assemblage limité à une boîte (repère Y-up exporté) : vue en coupe."""
    cut = cq.Assembly(name="coupe")
    keep = cq.Solid.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], cq.Vector(x[0], y[0], z[0]))
    for i, (n, s) in enumerate(G.flatten(assy)):
        k = G.part_key(n)
        if k == "Haut_Colonne_Trepied":
            continue
        part = s.intersect(keep)
        if part.Volume() < 1e-3:
            continue
        cut.add(part, name=f"p{i}", color=G.PARTS[k][2])
    return cut


def main():
    T.build_parts()
    fy = (G.Z_CHAPE + G.Z_T) / 2                      # hauteur du centre de la tête (Y-up)
    with_pan = T.build_head(0.0, G.EL_REF, "avec_panneau", True)
    r = build_renderer(with_pan, SUN, ground=False)
    shoot(r, "tete_vis_sans_fin_avec_panneau.png", (620, 430, 760), focal=(0, 130, 0), angle=30)
    r = build_renderer(with_pan, (-SUN[0], SUN[1], -SUN[2]), ground=False)   # éclairé côté cellules
    shoot(r, "tete_vis_sans_fin_avec_panneau_face.png", (-560, 380, -680), focal=(0, 130, 0), angle=30)

    head = T.build_head(0.0, G.EL_REF, "tete", False)
    r = build_renderer(head, SUN, ground=False)
    shoot(r, "tete_vis_sans_fin_iso.png", (330, 280, 400), focal=(-5, fy, 15), angle=36)
    shoot(r, "tete_vis_sans_fin_cote_moteurs.png", (-380, 260, 330), focal=(-5, fy, 15), angle=36)
    # coupe dans le plan de la roue d'élévation (x = -30 : axe de la vis)
    r = build_renderer(coupe(head, x=(-1e3, -30.0)), SUN, ground=False)
    shoot(r, "tete_vis_sans_fin_coupe_elevation.png", (420, 190, 160), focal=(-30, G.Z_T - 25, 0), angle=34)
    # coupe horizontale dans le plan de la vis d'azimut, vue de dessus
    z_az = G.AZ_VIS["z"]
    r = build_renderer(coupe(head, y=(-1e3, z_az)), SUN, ground=False)
    shoot(r, "tete_vis_sans_fin_coupe_azimut.png", (110, 260, 210), focal=(-25, z_az - 10, 25), angle=30)


if __name__ == "__main__":
    main()
