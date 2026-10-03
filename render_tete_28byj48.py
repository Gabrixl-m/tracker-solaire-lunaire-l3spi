#!/usr/bin/env python3
"""
Rendus de la tête rotative 28BYJ-48 (dont une vue en coupe).
Sur serveur : xvfb-run -a python render_tete_28byj48.py
"""

import math

import cadquery as cq

import generate_tete_28byj48 as T
import generate_tracker as G
from render_apercu import build_renderer, shoot

SUN = tuple(v / math.sqrt(0.5 ** 2 + 0.8 ** 2 + 0.6 ** 2) for v in (0.5, 0.8, 0.6))


def coupe(assy, keep_x_below=0.0):
    """Assemblage coupé par le plan x = keep_x_below (on garde x < plan)."""
    cut = cq.Assembly(name="coupe")
    half = cq.Solid.makeBox(2000, 2000, 2000, cq.Vector(-2000 + keep_x_below, -1000, -1000))
    for i, (n, s) in enumerate(G.flatten(assy)):
        k = T.inst_part(n)
        if k is None:
            continue
        part = s.intersect(half)
        if part.Volume() < 1e-3:
            continue
        cut.add(part, name=f"p{i}", color=T.PARTS[k][2])
    return cut


def main():
    T.build_parts(True)
    with_pan = T.build_head(0.0, 40.0, "avec_panneau", True)
    r = build_renderer(with_pan, SUN, ground=False)
    shoot(r, "tete_28byj48_avec_panneau.png", (620, 430, 760), focal=(0, 105, 0), angle=30)
    r = build_renderer(with_pan, (-SUN[0], SUN[1], -SUN[2]), ground=False)   # éclairé côté cellules
    shoot(r, "tete_28byj48_avec_panneau_face.png", (-560, 380, -680), focal=(0, 105, 0), angle=30)

    T.build_parts(False)
    head = T.build_head(0.0, 40.0, "tete", False)
    r = build_renderer(head, SUN, ground=False)
    shoot(r, "tete_28byj48_iso.png", (300, 250, 360), focal=(0, 95, 0), angle=32)
    shoot(r, "tete_28byj48_cote_moteur.png", (260, 200, 380), focal=(0, 105, 0), angle=30)
    r = build_renderer(coupe(head), SUN, ground=False)
    shoot(r, "tete_28byj48_coupe.png", (430, 150, 160), focal=(0, 75, 0), angle=34)


if __name__ == "__main__":
    main()
