#!/usr/bin/env python3
"""
Vérification indépendante de la stabilité du modèle terrestre sur son trépied.

Les masses et les centres de gravité viennent de la CAO, assemblée pour de bon dans 48 poses
(12 azimuts x 4 élévations). La mécanique est refaite sans reprendre le calcul de
generate_demo_trepied.py : moments autour de chaque arête du triangle d'appui, vent de toutes les
directions (tous les 5°), traînée de la tête et des jambes, portance du panneau incliné,
glissement, base élargie (planche lestée) et incertitudes (masse du trépied, écartement des
pieds, coefficient de force, hauteur du centre de poussée).

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
    G.set_ajustements("reel")
    return out


P = poses_cao()
RHO, G0 = 1.2, 9.81
A_PAN = 0.356 * 0.253
R_PIED = 0.230
PHIS = (90, 210, 330)
# traînées annexes (surface x Cx, hauteur) : tête + moteurs, 3 jambes du trépied
ANNEXES = [(0.012 * 1.1, 0.70), (0.036 * 1.0, 0.27)]

def pieds(r):
    return [(r * math.cos(math.radians(p)), r * math.sin(math.radians(p))) for p in PHIS]

def vent_limite(p, lest=0.0, z_lest=0.05, cn=1.2, r=R_PIED, m_trep=None, mu=None, dz=0.0, annexes=True, boite=None):
    """Plus petit vent (m/s) qui fait basculer (ou glisser si mu) cette pose, toutes directions de vent."""
    mt = p["trepied"][0] if m_trep is None else m_trep
    corps = [(mt, p["trepied"][1:]), (p["tete"][0], p["tete"][1:]), (p["bascule"][0], p["bascule"][1:])]
    M = sum(m for m, _ in corps) + lest
    cx = sum(m * c[0] for m, c in corps) / M / 1000
    cy = sum(m * c[1] for m, c in corps) / M / 1000
    az, el = math.radians(p["az"]), math.radians(p["el"])
    n = (-math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))   # normale du panneau
    pc = [v / 1000 for v in p["bascule"][1:]]; pc[2] += dz                        # centre de poussée ~ CdG de la partie basculante
    ft = pieds(r)
    best = (1e9, None)
    for k in range(72):
        ps = math.radians(5 * k); w = (math.cos(ps), math.sin(ps))
        cosi = w[0] * n[0] + w[1] * n[1]                    # vent . normale
        fN = cn * A_PAN * cosi                              # force normale / q, le long de n (signe compris)
        F = [fN * n[0], fN * n[1], fN * n[2]]               # par unité de pression dynamique
        ann = list(ANNEXES) if annexes else []
        if boite: ann.append(boite)
        Fh = [F[0] + sum(a for a, _ in ann) * w[0], F[1] + sum(a for a, _ in ann) * w[1]]
        if mu is not None:                                  # glissement : |Fh| q = mu (Mg - Fz q)
            fh = math.hypot(*Fh); den = fh + mu * F[2]
            if den > 0:
                q = mu * M * G0 / den; v = math.sqrt(2 * q / RHO)
                if v < best[0]: best = (v, ("glisse", 5 * k))
            continue
        for i in range(3):
            (x1, y1), (x2, y2) = ft[i], ft[(i + 1) % 3]
            ex, ey = x2 - x1, y2 - y1; L = math.hypot(ex, ey); ex, ey = ex / L, ey / L
            ox, oy = ey, -ex                                # normale sortante de l'arête
            if ox * x1 + oy * y1 < 0: ox, oy = -ox, -oy
            d_e = ox * x1 + oy * y1                         # distance axe -> arête
            bras = d_e - (ox * cx + oy * cy)                # CdG -> arête
            m_stab = M * G0 * bras
            # moment renversant / q : forces horizontales x hauteur + force verticale x bras
            m_r = (F[0] * ox + F[1] * oy) * pc[2] + F[2] * (d_e - (ox * pc[0] + oy * pc[1]))
            m_r += sum(a * (w[0] * ox + w[1] * oy) * z for a, z in ann)
            if m_r > 0:
                v = math.sqrt(2 * m_stab / m_r / RHO)
                if v < best[0]: best = (v, ("bascule", 5 * k, i))
    return best

def pire(**kw):
    b = (1e9,)
    for p in P:
        v, info = vent_limite(p, **kw)
        if v < b[0]: b = (v, p["az"], p["el"], info)
    return b

def ligne(nom, **kw):
    v, az, el, info = pire(**kw)
    print(f"{nom:58s} {v:5.1f} m/s = {v*3.6:4.0f} km/h   (az {az}°, él {el:.0f}°, {info})")

if __name__ == "__main__":
    print("masse totale", round(P[0]["tout"][0], 2), "kg ; CdG à", round(P[0]["tout"][3]), "mm du sol")
    # 1. recoupement avec le script du projet (mêmes hypothèses : panneau seul, Cx 1,2)
    for l in (0, 2, 3): ligne(f"panneau seul, Cx 1,2, lest {l} kg", lest=l, annexes=False)
    print()
    for l in (0, 2, 3, 5, 10): ligne(f"+ traînée tête et trépied, lest {l} kg", lest=l)
    for l in (0, 3): ligne(f"Cn 1,8 (panneau de signalisation, Eurocode), lest {l} kg", lest=l, cn=1.8)
    print()
    for mu in (0.3, 0.5, 0.7):
        for l in (0, 3): ligne(f"glissement, mu = {mu}, lest {l} kg", lest=l, mu=mu)
    print()
    # panneau à plat (él 90) seulement
    for l in (0, 3):
        b = min((vent_limite(p, lest=l) + (p["az"],) for p in P if p["el"] == 90.0), key=lambda t: t[0])
        print(f"panneau à plat, lest {l} kg : {b[0]:.1f} m/s = {b[0]*3.6:.0f} km/h")
    # base élargie : trépied sanglé sur une planche lestée (arête à r/2)
    print()
    for cote, lest in ((0.6, 10), (0.6, 20), (0.8, 10), (0.8, 20), (1.0, 10), (1.0, 20)):
        # planche carrée : arête à cote/2 ; équivalent triangle r = cote
        M = P[0]["tout"][0] + lest
        worst = 1e9
        for p in P:
            az, el = math.radians(p["az"]), math.radians(p["el"])
            n = (-math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))
            pc = [v / 1000 for v in p["bascule"][1:]]
            cgx, cgy = p["tout"][1] / 1000 * P[0]["tout"][0] / M, p["tout"][2] / 1000 * P[0]["tout"][0] / M
            for k in range(72):
                ps = math.radians(5 * k); w = (math.cos(ps), math.sin(ps))
                fN = 1.2 * A_PAN * (w[0] * n[0] + w[1] * n[1]); F = [fN * c for c in n]
                for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    d = cote / 2
                    m_r = (F[0] * ox + F[1] * oy) * (pc[2] + 0.03) + F[2] * (d - (ox * pc[0] + oy * pc[1]))
                    m_r += sum(a * (w[0] * ox + w[1] * oy) * (z + 0.03) for a, z in ANNEXES)
                    if m_r > 0:
                        worst = min(worst, math.sqrt(2 * M * G0 * (d - ox * cgx - oy * cgy) / m_r / RHO))
        print(f"planche {cote*100:.0f} x {cote*100:.0f} cm, {lest} kg de lest dessus : bascule à {worst:.1f} m/s = {worst*3.6:.0f} km/h")
    # incertitudes (lest 3 kg) : masse du trépied, rayon des pieds, Cn, hauteur du centre de poussée
    random.seed(1); vs = []
    for _ in range(400):
        kw = dict(lest=3.0, m_trep=random.uniform(0.7, 1.5), r=random.uniform(0.21, 0.25), cn=random.uniform(1.1, 1.8), dz=random.uniform(-0.02, 0.05))
        vs.append(pire(**kw)[0])
    vs.sort(); print(f"\nincertitudes, lest 3 kg : 5 % {vs[20]*3.6:.0f} km/h, médiane {vs[200]*3.6:.0f} km/h, 95 % {vs[380]*3.6:.0f} km/h")
    vs = []
    random.seed(1)
    for _ in range(400):
        kw = dict(lest=0.0, m_trep=random.uniform(0.7, 1.5), r=random.uniform(0.21, 0.25), cn=random.uniform(1.1, 1.8), dz=random.uniform(-0.02, 0.05))
        vs.append(pire(**kw)[0])
    vs.sort(); print(f"incertitudes, sans lest : 5 % {vs[20]*3.6:.0f} km/h, médiane {vs[200]*3.6:.0f} km/h, 95 % {vs[380]*3.6:.0f} km/h")
