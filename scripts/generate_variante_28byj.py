#!/usr/bin/env python3
"""
Variante terrestre à moteurs 28BYJ-48 avec contrepoids (document caché .variante_28BYJ-48/README.md).

Reprend la démonstration PETG (generate_tracker.py, jeu de cotes "petg", inserts à chaud) en
remplaçant les deux NEMA par des 28BYJ-48 et en ajoutant le contrepoids d'élévation :
  - supports de moteur redessinés (oreilles à 35 mm, lamage pour l'accouplement court) ;
  - accouplement flexible Ø14 x 19 ;
  - platine du contrepoids (inserts dans le flanc du chapeau) et bloc d'acier de 905 g.

Écrit dans .variante_28BYJ-48/ : l'assemblage Tete_Rotative_PETG_28BYJ.step et, dans a_imprimer/, les
seules pièces qui diffèrent de la version principale (STL + STEP, orientées pour l'impression).
Contrôles : interférences, prise des vis, appuis des roulements, engrènement, garde de la partie basculante.

Utilisation : python scripts/generate_variante_28byj.py
"""
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_tracker as G
import generate_tete_vis_sans_fin as T

OUT = os.path.join(G.RACINE, ".variante_28BYJ-48")
OUT_IMPR = os.path.join(OUT, "a_imprimer")
PIECES_VARIANTE = ("Support_Moteur_Elevation", "Support_Moteur_Azimut", "Chape", "Chapeau_U", "Support_Contrepoids")
T.ORIENTATION["Support_Contrepoids"] = [((0, 1, 0), 90)]      # à plat, face extérieure sur le plateau


def construire():
    G.set_ajustements("petg")
    G.set_variante("28byj")
    T.build_parts()
    G.PIECES_IMPRIMEES = tuple(G.PIECES_IMPRIMEES) + ("Support_Contrepoids",)


def exporter(assy):
    os.makedirs(OUT_IMPR, exist_ok=True)
    chemin = os.path.join(OUT, "Tete_Rotative_PETG_28BYJ.step")
    assy.export(chemin)
    G.clean_step_names(chemin)
    print(f"  {chemin} ({os.path.getsize(chemin) / 1e6:.1f} Mo)")
    for nom in PIECES_VARIANTE:
        wp = T.a_plat(G.PARTS[nom][0], T.ORIENTATION[nom])
        cq.exporters.export(wp, os.path.join(OUT_IMPR, f"{nom}.stl"), tolerance=0.01, angularTolerance=0.1)
        cq.exporters.export(wp, os.path.join(OUT_IMPR, f"{nom}.step"))
    print(f"  {len(PIECES_VARIANTE)} pièces propres à la variante -> {OUT_IMPR}")


def masses():
    rows, M, cg = G.mass_properties(G.flatten(G.build_panel(True)))
    print(f"  partie basculante (avec contrepoids) : {M:.2f} kg, CdG ({cg.x:.1f} ; {cg.y:.1f} ; {cg.z:.1f}) mm "
          f"(repère : origine sur l'axe d'élévation)")


def main():
    print("\n=== Variante terrestre 28BYJ-48 avec contrepoids ===")
    construire()
    assy = T.build_head(0.0, G.EL_REF, "Tete_Rotative_PETG_28BYJ", True)
    exporter(assy)
    T.verifier(assy)
    masses()
    G.set_variante(None)
    G.set_ajustements("reel")


if __name__ == "__main__":
    main()
