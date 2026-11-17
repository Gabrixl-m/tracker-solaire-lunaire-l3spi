#!/usr/bin/env python3
"""
Vérification indépendante de la stabilité du modèle terrestre sur son trépied.

Les masses et les centres de gravité viennent de la CAO, assemblée pour de bon dans 48 poses
(12 azimuts x 4 élévations). La mécanique est refaite sans reprendre le calcul de
generate_demo_trepied.py : moments autour de chaque arête du triangle d'appui, vent de toutes les
directions (tous les 5°) et incliné de ±10°, traînée de la tête et des jambes, portance du panneau
incliné. Il chiffre ensuite chaque levier possible sans toucher au trépied : lest, géométrie de
la tête, orientation des jambes par rapport au vent, élévation minimale, panneau à plat.

Usage : python scripts/verification_stabilite.py
"""
import math
import random
import sys


def poses_cao():
    import generate_demo_trepied as D
    import generate_tete_vis_sans_fin as T
    import generate_tracker as G
    G.set_ajustements("petg")
    if D.VARIANTE:                      # VARIANTE_28BYJ=1 : variante 28BYJ-48 avec contrepoids
        G.set_variante("28byj")
    T.build_parts()
    noms = D.enregistrer_trepied()
    out = []
    for el in (0.0, 30.0, 60.0, 90.0):
        for az in range(0, 360, 30):
            fl = G.flatten(D.assemblage(float(az), el, noms, "p"))

            def grp(f):
                m, c = D.masse_cdg([x for x in fl if f(x[0])])
                return [m, c.x, c.y, c.z]
            out.append(dict(az=az, el=el,
                            trepied=grp(lambda n: "/SA_Trepied/" in n),
                            tete=grp(lambda n: "/SA_Trepied/" not in n and "/SA_Panneau/" not in n),
                            bascule=grp(lambda n: "/SA_Panneau/" in n),
                            tout=grp(lambda n: True)))
    G.set_variante(None)
    G.set_ajustements("reel")
    return out


P = poses_cao()
RHO, G0, A = 1.2, 9.81, 0.356 * 0.253
ANN = [(0.012 * 1.1, 0.70), (0.036 * 1.0, 0.27)]
def cn(sa):            # plaque plane : force normale ~ constante au-delà de 35° d'incidence
    return 1.2 * min(1.0, abs(sa) / math.sin(math.radians(35)))
def limite(p, lest=0.0, r=0.230, rot_pieds=0.0, vents=range(0, 360, 5), e_zero=False, dh=0.0, incl=(-10, 0, 10), box=0.0):
    corps = [(p["trepied"][0], p["trepied"][1:]), (p["tete"][0], p["tete"][1:]), (p["bascule"][0], p["bascule"][1:])]
    M = sum(m for m, _ in corps) + lest
    cx = 0 if e_zero else sum(m * c[0] for m, c in corps) / M / 1000
    cy = 0 if e_zero else sum(m * c[1] for m, c in corps) / M / 1000
    az, el = math.radians(p["az"]), math.radians(p["el"])
    n = (-math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))
    pc = [v / 1000 for v in p["bascule"][1:]]; pc[2] += dh
    ft = [(r * math.cos(math.radians(f + rot_pieds)), r * math.sin(math.radians(f + rot_pieds))) for f in (90, 210, 330)]
    ann = ANN + ([(box, 0.06)] if box else [])
    best = 1e9
    for psd in vents:
        ps = math.radians(psd)
        for inc in incl:
            ci, si = math.cos(math.radians(inc)), math.sin(math.radians(inc))
            w = (math.cos(ps) * ci, math.sin(ps) * ci, si)
            sa = sum(a * b for a, b in zip(w, n))
            fN = cn(sa) * A * (1 if sa > 0 else -1)
            F = [fN * c for c in n]
            for i in range(3):
                (x1, y1), (x2, y2) = ft[i], ft[(i + 1) % 3]
                ex, ey = x2 - x1, y2 - y1; L = math.hypot(ex, ey); ox, oy = ey / L, -ex / L
                if ox * x1 + oy * y1 < 0: ox, oy = -ox, -oy
                d = ox * x1 + oy * y1
                ms = M * G0 * (d - ox * cx - oy * cy)
                mr = (F[0] * ox + F[1] * oy) * pc[2] + F[2] * (d - ox * pc[0] - oy * pc[1]) + sum(a * (w[0] * ox + w[1] * oy) * z for a, z in ann)
                if mr > 1e-9: best = min(best, math.sqrt(2 * ms / mr / RHO))
    return best
def pire(sel=lambda p: True, **kw): return min(limite(p, **kw) for p in P if sel(p)) * 3.6
print("modèle aéro prudent (force normale constante au-delà de 35°, rafales inclinées de ±10°)")
for l in (0, 3, 5, 8, 11, 15): print(f"lest {l:2d} kg : pire cas {pire(lest=l):.0f} km/h ; à plat {pire(lambda p: p['el']==90, lest=l):.0f} km/h")
print("\nlest 11 kg, leviers côté tête :")
print("  excentration du centre de gravité annulée :", round(pire(lest=11, e_zero=True)), "km/h")
print("  tête abaissée de 30 mm :", round(pire(lest=11, dh=-0.03)), "km/h ; de 70 mm (sans rotule) :", round(pire(lest=11, dh=-0.07)), "km/h")
print("  sans lest : excentration annulée", round(pire(lest=0, e_zero=True)), "km/h")
print("\norientation des jambes, vent dominant venant de l'est-sud-est (souffle vers 300°, repère 0° = +x), secteur ±30° :")
# vent soufflant VERS la direction psi ; le script utilise w = direction où va le vent
for l in (3, 11):
    for rotp in range(0, 120, 15):
        v = pire(lest=l, rot_pieds=rotp, vents=range(-30, 31, 5))   # vent soufflant vers 0° ± 30° ; pieds à 90+rot, ...
        print(f"  lest {l} kg, une jambe à {90 + rotp:3d}° du sens du vent : {v:.0f} km/h")
print("\nminimum d'élévation du panneau (lest 11 kg) :")
for emin in (0, 30, 60): print(f"  él >= {emin}° : {pire(lambda p: p['el'] >= emin, lest=11):.0f} km/h")
