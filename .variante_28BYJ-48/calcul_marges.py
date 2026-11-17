#!/usr/bin/env python3
"""Variante terrestre avec deux moteurs 28BYJ-48 : marges de couple, avec et sans contrepoids.

Reprend le modèle de couples de scripts/generate_tete_vis_sans_fin.py (mêmes vis sans fin, mêmes
frottements, mêmes couples de vent) en remplaçant les NEMA par des 28BYJ-48.

Le 28BYJ-48 a son réducteur (63,68:1) dans le moteur : son couple de 34,3 mN·m (fiche technique,
« in-traction torque » à 120 Hz) est déjà celui de l'arbre de sortie, en marche. On n'applique donc
pas le facteur K_RUN utilisé pour les NEMA (couple de maintien -> couple en marche).

Utilisation : python .variante_28BYJ-48/calcul_marges.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import generate_tracker as G
import generate_tete_vis_sans_fin as T

G.set_ajustements("petg")
T.build_parts()

C_NOM = 0.0343          # N·m, fiche technique (34,3 mN·m à 120 Hz, 5 V)
C_PRUD = 0.025          # N·m, valeur prudente (dispersion d'un moteur à l'autre, usure, 4,5 V)
M_CP, R_CP = 2.46, 0.0  # avec contrepoids (commit 3cdd766) : masse de la partie basculante, CdG sur l'axe
DESEQ = 0.02            # N·m : déséquilibre résiduel du contrepoids (bloc pesé à ± 2 %)

rows, M, cg = G.mass_properties(G.flatten(G.build_panel(True)))
R = math.hypot(cg.y, cg.z) / 1000
print(f"Partie basculante SANS contrepoids : {M:.2f} kg, CdG à {1000 * R:.1f} mm de l'axe")
print(f"Partie basculante AVEC contrepoids : {M_CP:.2f} kg, CdG sur l'axe, déséquilibre résiduel {DESEQ} N·m\n")

pesanteur_sans = M * T.G_TERRE * R
cas = {"el": dict(fr=T.FROT_EL, vent=T.VENT_EL, poids={"sans": pesanteur_sans, "avec": DESEQ}),
       "az": dict(fr=T.FROT_AZ, vent=T.VENT_AZ, poids={"sans": 0.0, "avec": 0.0})}

for key, (v, mot) in T.VIS.items():
    lam = math.atan(v["m"] / v["dp"])
    nom = "élévation" if key == "el" else "azimut"
    c = cas[key]
    print(f"=== {nom} : vis sans fin {v['z']}:1, angle d'hélice {math.degrees(lam):.1f}° ===")
    print(f"  pas de la roue par demi-pas du moteur : {360 / 4076 / v['z']:.4f}°")
    for mu, lib in ((0.15, "graissé"), (0.30, "à sec")):
        eta = math.tan(lam) / math.tan(lam + math.atan(mu))
        for cm, lm in ((C_NOM, "nominal"), (C_PRUD, "prudent")):
            dispo = cm * v["z"] * eta
            ligne = f"  {lib:8s} {lm:8s} : couple à la roue {dispo:.3f} N·m ; "
            for poids in ("sans", "avec"):
                p = c["poids"][poids] if key == "el" else 0.0
                base = p + c["fr"] + (0.01 if key == "az" else 0.0)
                v_max = 10 * math.sqrt(max(dispo - base, 0) / c["vent"])
                marge_int = dispo / base
                marge_10 = dispo / (base + c["vent"])
                ligne += f"{poids} CP : intérieur ×{marge_int:.1f}, 10 m/s ×{marge_10:.2f}, vent max {v_max:.1f} m/s ; "
            print(ligne)
    eta = math.tan(lam) / math.tan(lam + math.atan(0.15))
    dispo = C_NOM * v["z"] * eta
    print("  graissé, nominal, avec contrepoids, marge selon le vent :",
          ", ".join(f"{vv} m/s ×{dispo / (c['poids']['avec'] + c['fr'] + (0.01 if key == 'az' else 0.0) + c['vent'] * (vv / 10) ** 2):.1f}"
                    for vv in (3, 5, 8, 10)))
    print(f"  contrainte en pied de dent à {dispo:.2f} N·m : {37 * dispo / 3.0:.0f} MPa "
          f"(37 MPa pour 3,0 N·m, README du cas terrestre § 9)")
    print(f"  temps pour 90° de roue à 120 demi-pas/s : {0.25 * 4076 * v['z'] / 120 / 60:.1f} min\n")
