#!/usr/bin/env python3
"""
Optimisation de l'angle φ des jambes du trépied (jambes en Y à 120°).

φ est l'angle entre une jambe et la colonne. L'articulation haute est fixée par la
tête et le panneau (le trépied doit rester sous le volume balayé par le panneau) ;
φ fixe donc le rayon des pieds, la longueur des jambes et leur course télescopique.

Contraintes (paramètres dans P de generate_tracker.py) :
  C1 stabilité : angle de basculement sans ancrage (centre de gravité réel de la CAO,
     pire orientation du panneau) ≥ pente_stabilite + inclinaison due à un obstacle
     sous un pied + marge_basculement
  C2 nivelage  : course télescopique nécessaire pour remettre la tête de niveau sur
     pente_nivelage ≤ course possible avec une jambe à deux tubes
  C3 géométrie : garde au sol du bas de la colonne ≥ 150 mm
Critère : masse et encombrement minimaux. Longueur, masse, poussée dans les
entretoises, course de nivelage et emprise au sol augmentent toutes avec φ :
l'optimum est donc le plus petit φ qui respecte C1, C2 et C3.

Usage : python scripts/optimisation_angle.py   -> docs/optimisation_angle_jambes.md
"""

import math
import os

import cadquery as cq

import generate_tracker as G

OUT = os.path.join(G.RACINE, "docs", "optimisation_angle_jambes.md")
PHIS = [25.0 + 0.5 * i for i in range(71)]          # 25° à 60°


def group_mass_cg(flat, keep, yup=True):
    """Masse et centre de gravité (repère Z-up) des sous-assemblages 'keep'."""
    rows, _M, _cg = G.mass_properties([x for x in flat if x[0].split("/")[1] in keep])
    m = sum(r[4] for r in rows)
    c = cq.Vector(0, 0, 0)
    for r in rows:
        c = c + r[5] * r[4]
    c = c * (1 / m)
    return m, (G.to_zup(c) if yup else c)


def rot_z(v, deg):
    a = math.radians(deg)
    return cq.Vector(v.x * math.cos(a) - v.y * math.sin(a), v.x * math.sin(a) + v.y * math.cos(a), v.z)


def main():
    P = G.P
    phi_file = P["leg_angle"]
    G.build_parts()
    G.build_tripod()

    # tête et panneau : masse et centre de gravité, pour plusieurs élévations (az = 0)
    head = []
    for el in (P["el_min"], 0.0, 30.0, 60.0, P["el_max"]):
        flat = G.flatten(G.build_assembly(0.0, el, "opt"))
        head.append((group_mass_cg(flat, ("SA_Tete_Fixe",)), group_mass_cg(flat, ("SA_Tete_Orientable",))))

    h = P["z_hinge"] - P["z_ball"]
    kmax = 2 / 3 * math.sqrt(1 / 3)                     # max de sin²φ·cosφ (φ = 54,7°)
    res = []
    for phi in PHIS:
        G.set_leg_geometry(phi)
        G.build_tripod_parts()
        m_t, cg_t = group_mass_cg([("x/" + n, s) for n, s in G.flatten(G.build_tripod())],
                                  ("SA_Trepied",), yup=False)
        # basculement : pire cas sur toutes les orientations du panneau
        tip = 90.0
        for (m_f, cg_f), (m_r, cg_r) in head:
            for az in range(0, 360, 15):
                M = m_t + m_f + m_r
                cg = (cg_t * m_t + cg_f * m_f + rot_z(cg_r, az) * m_r) * (1 / M)
                tip = min(tip, G.tipping(cg))
        R = P["r_foot"]
        req = P["pente_stabilite"] + math.degrees(math.atan2(P["obstacle"], 1.5 * R)) + P["marge_basculement"]
        t, t_max = P["course_telescopique"], G.course_telescopique_max(phi)
        clamp_ok = P["z_col_bot"] - 25.0 >= 150.0          # pointe de la colonne
        b = math.radians(phi)
        res.append(dict(
            phi=phi, R=R, L=G.LEG_L, m_t=m_t, M=m_t + head[0][0][0] + head[0][1][0], tip=tip, req=req,
            t=t, t_max=t_max, c1=tip >= req, c2=t <= t_max, c3=clamp_ok,
            thrust=math.tan(b), k=math.sin(b) ** 2 * math.cos(b) / kmax * 100))

    ok = [r for r in res if r["c1"] and r["c2"] and r["c3"]]
    best = ok[0] if ok else None

    # sensibilité de l'optimum aux exigences (la géométrie ne change pas, seuls les seuils)
    def optimum(pente, obst, marge, niv):
        for r in res:
            req = pente + math.degrees(math.atan2(obst, 1.5 * r["R"])) + marge
            t = r["R"] * math.tan(math.radians(niv)) / math.cos(math.radians(r["phi"]))
            if r["tip"] >= req and t <= r["t_max"] and r["c3"]:
                return r["phi"]
        return None

    L = []
    w = L.append
    w("# Optimisation de l'angle φ des jambes du trépied\n")
    w("Générée par `scripts/optimisation_angle.py` à partir des masses et centres de gravité de la CAO.\n")
    w("## Données fixées par la tête et le panneau\n")
    w(f"- Jambes en Y, à 120°. Articulation haute à r = {P['r_hinge']:.0f} mm, "
      f"z = {P['z_hinge']:.0f} mm : juste sous le socle de la tête. Le panneau vertical descend "
      f"jusqu'à {P['z_el'] - 129:.0f} mm et tout le trépied doit rester en dessous.")
    w(f"- Centre de la rotule de pied à z = {P['z_ball']:.0f} mm, soit une hauteur de jambe h = {h:.0f} mm.")
    w(f"- Tête + panneau : {head[0][0][0] + head[0][1][0]:.2f} kg. Le centre de gravité est pris dans la "
      "pire orientation du panneau (élévation de −2° à +92°, azimut sur 360°).\n")
    w("## Exigences\n")
    w("| Exigence | Valeur |\n|---|---|")
    w(f"| Pente maxi sans ancrage (C1) | {P['pente_stabilite']:.0f}° |")
    w(f"| Obstacle ou enfoncement sous un pied (C1) | {P['obstacle']:.0f} mm |")
    w(f"| Marge de sécurité au basculement (C1) | {P['marge_basculement']:.0f}° |")
    w(f"| Pente rattrapée par les jambes télescopiques (C2) | {P['pente_nivelage']:.0f}° |")
    w(f"| Recouvrement mini des tubes (C2) | {P['recouvrement_min']:.0f} mm |\n")
    w("## Résultats selon φ\n")
    w("| φ | Ø des pieds | Jambe | Masse trépied | Basculement | Exigé (C1) | Course ± nécessaire / possible (C2) "
      "| Poussée entretoise | Rigidité latérale | Admissible |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for r in res:
        if r["phi"] % 2.5 and r is not best:
            continue
        mark = "**" if r is best else ""
        adm = "oui" if (r["c1"] and r["c2"] and r["c3"]) else \
            "non (" + ", ".join(n for n, c in (("C1", r["c1"]), ("C2", r["c2"]), ("C3", r["c3"])) if not c) + ")"
        w(f"| {mark}{r['phi']:.1f}°{mark} | {2 * r['R']:.0f} mm | {r['L']:.0f} mm | {r['m_t']:.2f} kg | "
          f"{r['tip']:.1f}° | {r['req']:.1f}° | {r['t']:.0f} / {r['t_max']:.0f} mm | "
          f"{r['thrust']:.2f} × charge | {r['k']:.0f} % | {adm} |")
    w("")
    if best:
        lo = best["phi"]
        hi = max(r["phi"] for r in ok)
        w(f"**Plage admissible : φ de {lo:.1f}° à {hi:.1f}°. Optimum : φ = {lo:.1f}°**, le plus petit angle "
          "admissible, donc les jambes les plus courtes et les plus légères, la poussée la plus faible "
          "dans les entretoises, la plus petite course de nivelage et la plus petite emprise au sol.\n")
    else:
        w("**Aucun angle ne respecte toutes les exigences** : il faut les assouplir ou changer la géométrie.\n")
    w("La rigidité latérale est maximale à 54,7°, mais elle ne dimensionne pas sur la Lune : "
      "sans vent, seuls les pas des moteurs et les manipulations l'excitent.\n")
    w("## Sensibilité de l'optimum aux exigences\n")
    w("| Variante | φ optimal |\n|---|---|")
    base = (P["pente_stabilite"], P["obstacle"], P["marge_basculement"], P["pente_nivelage"])
    variants = [("Exigences de référence", base),
                ("Pente sans ancrage 10°", (10.0,) + base[1:]),
                ("Pente sans ancrage 20°", (20.0,) + base[1:]),
                ("Sans obstacle sous un pied", (base[0], 0.0) + base[2:]),
                ("Obstacle de 100 mm", (base[0], 100.0) + base[2:]),
                ("Marge de 10°", base[:2] + (10.0, base[3])),
                ("Nivelage sur 15°", base[:3] + (15.0,))]
    for name, v in variants:
        o = optimum(*v)
        w(f"| {name} | {'aucun' if o is None else f'{o:.1f}°'} |")
    w("")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    if best and abs(best["phi"] - phi_file) > 1e-6:
        print(f"\n>>> Reporter leg_angle={best['phi']:.1f} dans generate_tracker.py (actuellement {phi_file}).")


if __name__ == "__main__":
    main()
