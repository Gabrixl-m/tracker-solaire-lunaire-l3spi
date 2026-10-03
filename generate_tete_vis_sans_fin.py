#!/usr/bin/env python3
"""
Tête rotative à vis sans fin, seule (sans le trépied), et son dimensionnement.

La géométrie est celle de generate_tracker.py (une seule source). Ce script :
  - exporte la tête seule, panneau monté à 40° : CAO/Tete_Rotative_VisSansFin.step,
    et ses pièces dans CAO/pieces_tete_vissansfin/ ;
  - cale les vis par rapport aux roues et vérifie generate_tracker.PHASE ;
  - calcule les couples nécessaires et disponibles (Lune, Terre intérieur, Terre avec
    vent) et la tenue moteurs coupés ;
  - vérifie interférences, engrènement et garde sur toute la course d'élévation.

Usage : python generate_tete_vis_sans_fin.py
"""

import math
import os

import cadquery as cq

import generate_tracker as G
from generate_tracker import ring_z, rot, trans

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_STEP = os.path.join(HERE, "CAO", "Tete_Rotative_VisSansFin.step")
OUT_PARTS = os.path.join(HERE, "CAO", "pieces_tete_vissansfin")

# Cas de charge
G_LUNE, G_TERRE = 1.62, 9.81
VENT_EL, VENT_AZ = 0.35, 0.50        # couple de vent à 10 m/s (N·m), voir README
FROT_EL, FROT_AZ = 0.01, 0.02        # roulements, câbles
K_RUN = 0.70                         # couple en marche lente / couple de maintien (TMC2209, micro-pas)
MU_MARCHE = 0.15                     # frottement vis / roue pour le rendement en marche (prudent)
# frottement au repos pour la tenue moteurs coupés
MU_REPOS = {"Terre, graissé": 0.10, "Terre, vibrations": 0.05, "Lune, MoS2 sous vide": 0.02}

HEAD_PARTS = ("Fond_Socle", "Socle", "Roulement_6806", "Roue_Azimut_Fixe", "Chape", "Bague_Arret_Moyeu",
              "Roulement_608", "Roulement_685", "Vis_Azimut", "Arbre_Vis_Azimut", "Palier_Vis_Azimut",
              "Support_Moteur_Azimut", "Moteur_Azimut_NEMA11", "Vis_Elevation", "Arbre_Vis_Elevation",
              "Palier_Vis_Elevation", "Support_Moteur_Elevation", "Moteur_Elevation_NEMA17", "Accouplement",
              "Chapeau_U", "Pivot_Entraine", "Pivot_Libre", "Roue_Elevation", "Rail_Panneau") + G.PANEL_PARTS
PAIRES = {"el": ("/Vis_Elevation", "/Roue_Elevation"), "az": ("/Vis_Azimut", "/Roue_Azimut_Fixe")}
VIS = {"el": (G.VIS_EL, G.MOT_EL), "az": (G.VIS_AZ, G.MOT_AZ)}


def build_parts():
    G.PARTS.clear()
    G.build_head_parts()
    G.reg("Haut_Colonne_Trepied", ring_z(G.P["col_od"], G.COL_ID, 80, -80), "Al 7075-T73",
          cq.Color(0.70, 0.70, 0.72), "Référence : haut de la colonne du trépied")


def build_head(az, el, name, with_panel=True):
    """Tête seule, repère exporté Y-up, origine au sommet de la colonne."""
    root = cq.Assembly(name=name)
    ref = cq.Assembly(name="SA_Reference_Trepied")
    G.add(ref, "Haut_Colonne_Trepied")
    root.add(ref, name="SA_Reference_Trepied", loc=G.TO_YUP)
    root.add(G.build_head_fixed(), name="SA_Tete_Fixe", loc=G.TO_YUP)
    root.add(G.build_head(az, el, with_panel), name="SA_Tete_Orientable", loc=G.TO_YUP * rot((0, 0, 1), az))
    return root


def overlap(flat, a_end, b_end):
    a = [s for n, s in flat if n.endswith(a_end)][0]
    b = [s for n, s in flat if n.endswith(b_end)][0]
    return a.intersect(b).Volume()


def caler_dentures():
    """Calage angulaire des vis : dents en prise, sans chevauchement, à l'élévation de référence."""
    for key, (a, b) in PAIRES.items():
        ref = G.PHASE[key]

        def essai(k):
            G.PHASE[key] = k
            return overlap(G.flatten(build_head(0.0, G.EL_REF, "c", False)), a, b)
        best = (ref, essai(ref))
        step = 10.0
        k = 0.0
        while best[1] > 1e-6 and k < 360.0:
            v = essai(k)
            if v < best[1] - 0.01:          # on ne change de calage que pour un vrai gain
                best = (k, v)
            k += step
        for _ in range(2):                  # affinage autour du meilleur calage
            if best[1] < 1e-6:
                break
            step /= 4
            for k in (best[0] + i * step for i in range(-3, 4) if i):
                v = essai(k)
                if v < best[1] - 0.01:
                    best = (k, v)
        G.PHASE[key] = best[0]
        note = "" if abs(best[0] - ref) < 1e-6 else f"  -> reporter PHASE['{key}'] = {best[0]:.1f} dans generate_tracker.py"
        print(f"  calage vis {key} : {best[0]:.1f}° (recouvrement {best[1]:.3f} mm3){note}")


def couples():
    """Couples nécessaires / disponibles par axe et par cas, tenue moteurs coupés."""
    rows, M, cg = G.mass_properties(G.flatten(G.build_panel(True)))
    r = math.hypot(cg.y, cg.z) / 1000                       # bras de levier maxi du CdG (m)
    besoin = {
        "el": {"Lune": M * G_LUNE * r + FROT_EL, "Terre, intérieur": M * G_TERRE * r + FROT_EL,
               "Terre, extérieur (vent 10 m/s)": M * G_TERRE * r + FROT_EL + VENT_EL},
        "az": {"Lune": FROT_AZ, "Terre, intérieur": FROT_AZ + 0.01,
               "Terre, extérieur (vent 10 m/s)": FROT_AZ + VENT_AZ},
    }
    # couple extérieur que la vis doit retenir moteurs coupés (sans les frottements)
    charge = {"el": {"Terre": M * G_TERRE * r + VENT_EL, "Lune": M * G_LUNE * r},
              "az": {"Terre": VENT_AZ, "Lune": 0.0}}
    dispo = {}
    for key, (v, mot) in VIS.items():
        lam = math.atan(v["m"] / v["dp"])
        eta = math.tan(lam) / math.tan(lam + math.atan(MU_MARCHE))
        tenue = {}
        for cas, mu in MU_REPOS.items():
            phi = math.atan(mu)
            t_ext = charge[key]["Lune" if cas.startswith("Lune") else "Terre"]
            if phi >= lam:
                tenue[cas] = ("irréversible", None)
            else:                           # réversible : le couple résiduel du moteur doit retenir
                t_vis = t_ext / v["z"] * math.tan(lam - phi) / math.tan(lam)
                tenue[cas] = ("réversible", mot["detent"] / t_vis if t_vis > 0 else math.inf)
        dispo[key] = dict(t=mot["hold"] * K_RUN * v["z"] * eta, ratio=v["z"], eta=eta,
                          lam=math.degrees(lam), tenue=tenue)
    return M, r, besoin, dispo


def main():
    print("=== Tête rotative à vis sans fin ===")
    build_parts()
    caler_dentures()
    assy = build_head(0.0, G.EL_REF, "Tete_Rotative_VisSansFin", True)
    assy.export(OUT_STEP)
    G.clean_step_names(OUT_STEP)
    print(f"  {OUT_STEP} ({os.path.getsize(OUT_STEP) / 1e6:.1f} Mo)")
    os.makedirs(OUT_PARTS, exist_ok=True)
    for f in os.listdir(OUT_PARTS):
        if f.endswith(".step"):
            os.remove(os.path.join(OUT_PARTS, f))
    for name in HEAD_PARTS:
        cq.exporters.export(G.PARTS[name][0], os.path.join(OUT_PARTS, f"{name}.step"))

    flat = G.flatten(assy)
    rows, _M, _cg = G.mass_properties([x for x in flat if G.part_key(x[0]) not in G.PANEL_PARTS
                                       and G.part_key(x[0]) != "Haut_Colonne_Trepied"])
    print(f"  masse de la tête (hors panneau) : {sum(r[4] for r in rows):.2f} kg")
    M, r, besoin, dispo = couples()
    print(f"  partie basculante (chapeau, roue, rails, panneau) : {M:.2f} kg, CdG à {r * 1000:.1f} mm de l'axe")
    for key, mot in (("el", G.MOT_EL), ("az", G.MOT_AZ)):
        d = dispo[key]
        print(f"  {key} : {mot['nom']} ({mot['hold']} N·m, {mot['amp']} A), vis {d['ratio']}:1, "
              f"hélice {d['lam']:.2f}°, rendement {d['eta']:.2f} -> {d['t']:.2f} N·m")
        for cas, b in besoin[key].items():
            print(f"      {cas:32s} besoin {b:.3f} N·m -> marge x{d['t'] / b:.1f}")
        for cas, (etat, marge) in d["tenue"].items():
            txt = "tient par la vis" if marge is None else (
                "aucune charge" if marge == math.inf else f"tient par le couple résiduel du moteur, marge x{marge:.1f}")
            print(f"      moteurs coupés, {cas:22s} {etat} : {txt}")

    hits = G.interference(flat)
    print(f"  interférences : {'aucune' if not hits else hits}")
    for key, (a, b) in PAIRES.items():
        for az, el in (((0.0, -2.0), (0.0, 92.0)) if key == "el" else ((37.0, G.EL_REF),)):
            v = overlap(G.flatten(build_head(az, el, "c", False)), a, b)
            print(f"  denture {key} à az={az:g}°, él={el:g}° : recouvrement {v:.3f} mm3")
    worst = (1e9,)
    for el in (-2.0, 0.0, 15.0, 45.0, 75.0, 92.0):
        fl = G.flatten(build_head(0.0, el, "chk", True))
        mov = [(n, s) for n, s in fl if "/SA_Panneau/" in n
               and not G.part_key(n).startswith(("Pivot", "Cellules"))]
        fix = [(n, s) for n, s in fl if "/SA_Panneau/" not in n and G.part_key(n) != "Vis_Elevation"]
        dd = G.min_clearance(mov, fix, cutoff=30.0)
        if dd[0] < worst[0]:
            worst = dd + (el,)
    print(f"  garde mini partie basculante (-2° à 92°) : {worst[0]:.1f} mm "
          f"({str(worst[1]).split('/')[-1]} / {str(worst[2]).split('/')[-1]}, él={worst[3]}°)")


if __name__ == "__main__":
    main()
