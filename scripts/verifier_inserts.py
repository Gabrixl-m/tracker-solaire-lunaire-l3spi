"""Contrôle des inserts à chaud (cas terrestre) : pour chacun des 25 inserts, vérifie qu'il y a
au moins 1,6 mm de matière autour du trou (4 périmètres) et derrière son fond (au moins 1,2 mm pour les inserts longs, 1,6 mm pour les courts).

Utilisation : python scripts/verifier_inserts.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadquery as cq
from cadquery import Vector
import generate_tracker as G, generate_tete_vis_sans_fin as T
G.set_ajustements("petg"); T.build_parts()
res = []
for rep, piece, genre, pt, d in G.table_inserts():
    i = G.INSERT[genre]
    s = G.PARTS[piece][0].val()
    dec = Vector(G.X_CAPTEUR, 0, G.CAPTEUR["z"]) if piece == "Capteur_Solaire_Boitier" else Vector(0,0,0)
    base = Vector(*pt) - dec; v = Vector(*d)
    trou = cq.Solid.makeCylinder(i["d_trou"]/2, i["prof"], base, v)
    plein = s.fuse(trou)                                    # perçage rebouché : la matière autour doit exister
    mur = cq.Solid.makeCylinder(i["d_trou"]/2 + 1.6, i["prof"], base, v)
    manque = mur.cut(plein).Volume() / mur.Volume()
    # fond : épaisseur de matière pleine derrière le perçage (cylindre Ø1,6 mm, par dichotomie)
    def plein_sur(e):
        c = cq.Solid.makeCylinder(0.8, e, base + v * i["prof"], v)
        return c.cut(plein).Volume() / c.Volume() < 0.01
    lo_, hi_ = 0.0, 3.0
    for _ in range(8):
        mid = (lo_ + hi_) / 2
        lo_, hi_ = (mid, hi_) if plein_sur(mid) else (lo_, mid)
    manque_fond = lo_
    res.append((piece, genre, tuple(round(c,1) for c in pt), manque, manque_fond))
FOND_MINI = {"L": 1.2, "C": 1.6}      # insert long : 1,2 mm (piliers) ; insert court : 1,6 mm
mal = [r for r in res if r[3] > 0.01 or r[4] < FOND_MINI[r[1]] - 0.05]
for r in res:
    flag = "  <-- A SURVEILLER" if (r[3] > 0.01 or r[4] < FOND_MINI[r[1]] - 0.05) else ""
    print(f"{r[0]:26s} {r[1]} {str(r[2]):28s} manque autour {100*r[3]:4.1f} % ; fond plein sur {r[4]:.2f} mm{flag}")
print(len(res), "inserts,", len(mal), "à surveiller")
