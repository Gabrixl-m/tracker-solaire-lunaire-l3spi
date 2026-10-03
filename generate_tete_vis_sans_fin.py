#!/usr/bin/env python3
"""
Tête rotative à vis sans fin, seule (sans le trépied) : cas réel et démonstration PETG.

La géométrie est celle de generate_tracker.py (une seule source), avec ses deux jeux
de cotes (generate_tracker.AJUSTEMENTS). Ce script :
  - cas réel : exporte la tête seule, panneau monté à 40°,
    CAO/Cas_Reel/Tete_Rotative_VisSansFin.step ;
  - démonstration sur Terre (impression 3D PETG) : exporte l'assemblage imprimé
    CAO/Demo_Terre_PETG/Tete_Rotative_PETG.step, les pièces à imprimer orientées pour
    l'impression (STL + STEP) dans CAO/Demo_Terre_PETG/a_imprimer/, et une éprouvette
    de réglage des ajustements ;
  - cale les vis par rapport aux roues pour chaque jeu de cotes ;
  - calcule les couples nécessaires et disponibles (Lune, Terre intérieur, Terre avec
    vent) et la tenue moteurs coupés ;
  - vérifie interférences, engrènement et garde sur toute la course d'élévation.

Usage : python generate_tete_vis_sans_fin.py
"""

import math
import os

import cadquery as cq

import generate_tracker as G
from generate_tracker import box_span, cyl_z, ring_z, rot

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_REEL = os.path.join(HERE, "CAO", "Cas_Reel", "Tete_Rotative_VisSansFin.step")
OUT_PETG = os.path.join(HERE, "CAO", "Demo_Terre_PETG")
OUT_IMPR = os.path.join(OUT_PETG, "a_imprimer")

# Cas de charge
G_LUNE, G_TERRE = 1.62, 9.81
VENT_EL, VENT_AZ = 0.35, 0.50        # couple de vent à 10 m/s (N·m), voir README
FROT_EL, FROT_AZ = 0.01, 0.02        # roulements, câbles
K_RUN = 0.70                         # couple en marche lente / couple de maintien (TMC2209, micro-pas)
# frottement vis / roue en marche (rendement) et au repos (tenue moteurs coupés)
MU_MARCHE = {"reel": {"acier / bronze graissé": 0.15},
             "petg": {"PETG graissé": 0.15, "PETG à sec": 0.30}}
MU_REPOS = {"reel": {"Terre, graissé": 0.10, "Terre, vibrations": 0.05, "Lune, MoS2 sous vide": 0.02},
            "petg": {"Terre, PETG graissé": 0.15, "Terre, vibrations": 0.08}}

PAIRES = {"el": ("/Vis_Elevation", "/Roue_Elevation"), "az": ("/Vis_Azimut", "/Roue_Azimut_Fixe")}
VIS = {"el": (G.VIS_EL, G.MOT_EL), "az": (G.VIS_AZ, G.MOT_AZ)}
# orientation d'impression : rotations (axe, angle) appliquées à la pièce, puis posée sur le plateau
ORIENTATION = {
    "Fond_Socle": [((1, 0, 0), 180)], "Socle": [], "Roue_Azimut_Fixe": [], "Chape": [],
    "Moyeu_Chape": [((1, 0, 0), 180)], "Bague_Arret_Moyeu": [], "Palier_Vis_Azimut": [((1, 0, 0), 180)],
    "Support_Moteur_Azimut": [((1, 0, 0), 180)], "Vis_Azimut": [], "Palier_Vis_Elevation": [],
    "Support_Moteur_Elevation": [], "Vis_Elevation": [], "Chapeau_U": [((1, 0, 0), 180)],
    "Roue_Elevation": [((0, 1, 0), -90)],
    "Pivot_Entraine": [((1, 0, 0), 180)],        # couché sur son méplat
    "Pivot_Libre": [((0, 1, 0), 90)],            # debout, tête en bas
}


def build_parts():
    G.PARTS.clear()
    G.build_head_parts()
    col = ring_z(G.P["col_od"], G.COL_ID, 80, -80)
    col = col.cut(G.cyl_dir(3.4, 8, (0, -G.P["col_od"] / 2 + 4, -8), (0, -1, 0)))    # vis anti-rotation
    G.reg("Haut_Colonne_Trepied", col, "Al 7075-T73", cq.Color(0.70, 0.70, 0.72),
          "Référence : haut de la colonne du trépied")


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
    ph = G.PHASES[G.MODE]
    for key, (a, b) in PAIRES.items():
        ref = ph[key]

        def essai(k):
            ph[key] = k
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
        ph[key] = best[0]
        note = "" if abs(best[0] - ref) < 1e-6 else \
            f"  -> reporter PHASES['{G.MODE}']['{key}'] = {best[0]:.1f} dans generate_tracker.py"
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
    if G.MODE == "petg":                    # la démonstration ne va pas sur la Lune
        for key in besoin:
            del besoin[key]["Lune"]
    # couple extérieur que la vis doit retenir moteurs coupés (sans les frottements)
    charge = {"el": {"Terre": M * G_TERRE * r + VENT_EL, "Lune": M * G_LUNE * r},
              "az": {"Terre": VENT_AZ, "Lune": 0.0}}
    dispo = {}
    for key, (v, mot) in VIS.items():
        lam = math.atan(v["m"] / v["dp"])
        marche = {}
        for cas, mu in MU_MARCHE[G.MODE].items():
            eta = math.tan(lam) / math.tan(lam + math.atan(mu))
            marche[cas] = (eta, mot["hold"] * K_RUN * v["z"] * eta)
        tenue = {}
        for cas, mu in MU_REPOS[G.MODE].items():
            phi = math.atan(mu)
            t_ext = charge[key]["Lune" if cas.startswith("Lune") else "Terre"]
            if phi >= lam:
                tenue[cas] = ("irréversible", None)
            else:                           # réversible : le couple résiduel du moteur doit retenir
                t_vis = t_ext / v["z"] * math.tan(lam - phi) / math.tan(lam)
                tenue[cas] = ("réversible", mot["detent"] / t_vis if t_vis > 0 else math.inf)
        dispo[key] = dict(ratio=v["z"], lam=math.degrees(lam), marche=marche, tenue=tenue)
    return M, r, besoin, dispo


def verifier(assy):
    """Interférences, engrènement à plusieurs poses, garde de la partie basculante."""
    flat = G.flatten(assy)
    hits = G.interference(flat)
    print(f"  interférences : {'aucune' if not hits else hits}")
    for key, (a, b) in PAIRES.items():
        poses = ((0.0, -2.0), (0.0, 30.0), (0.0, 92.0)) if key == "el" else ((37.0, G.EL_REF), (113.0, G.EL_REF))
        for az, el in poses:
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
    return flat


def bilan(flat):
    rows, _M, _cg = G.mass_properties([x for x in flat if G.part_key(x[0]) not in G.PANEL_PARTS
                                       and G.part_key(x[0]) != "Haut_Colonne_Trepied"])
    print(f"  masse de la tête (hors panneau) : {sum(r[4] for r in rows):.2f} kg")
    M, r, besoin, dispo = couples()
    print(f"  partie basculante (chapeau, roue, rails, panneau) : {M:.2f} kg, CdG à {r * 1000:.1f} mm de l'axe")
    for key, mot in (("el", G.MOT_EL), ("az", G.MOT_AZ)):
        d = dispo[key]
        print(f"  {key} : {mot['nom']} ({mot['hold']} N·m, {mot['amp']} A), vis {d['ratio']}:1, hélice {d['lam']:.2f}°")
        for cas_mu, (eta, t) in d["marche"].items():
            marges = ", ".join(f"{cas} x{t / b:.1f}" for cas, b in besoin[key].items())
            print(f"      {cas_mu} : rendement {eta:.2f} -> {t:.2f} N·m ; marges : {marges}")
        for cas, (etat, marge) in d["tenue"].items():
            txt = "tient par la vis" if marge is None else (
                "aucune charge" if marge == math.inf else f"tient par le couple résiduel du moteur, marge x{marge:.1f}")
            print(f"      moteurs coupés, {cas:22s} {etat} : {txt}")


def a_plat(wp, rots):
    """Pièce orientée pour l'impression, posée sur le plateau (z = 0) et centrée."""
    s = wp.val()
    for axis, ang in rots:
        s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(*axis), ang)
    bb = s.BoundingBox()
    return cq.Workplane().add(s.translate(cq.Vector(-bb.center.x, -bb.center.y, -bb.zmin)))


def eprouvette():
    """Éprouvette de réglage : logements des roulements de pivots (6801) et des 685 en trois jeux,
    alésages de pivot en D et Ø5, trous M3, téton Ø30 (bague intérieure d'un 6806) et téton de
    pivot (bague intérieure d'un 6801)."""
    aj = G.AJ
    e = box_span(0, 112, 0, 62, 0, 6).edges("|Z").fillet(3)
    pv = G.PV()
    for i, dj in enumerate((-0.10, 0.0, 0.10)):           # roulement de pivot + jeu du réglage ± 0,1
        e = e.cut(cyl_z(pv["roul"][0] + aj["roulement"] + dj, 8, 16 + 26 * i, 16, -1))
    for i, dj in enumerate((-0.10, 0.0, 0.10)):           # 685 : Ø11
        e = e.cut(cyl_z(11 + aj["roulement"] + dj, 8, 10 + 15 * i, 46, -1))
    dp = pv["d"] + aj["serrage"]
    e = e.cut(cyl_z(dp, 8, 57, 46, -1).cut(box_span(45, 70, 46 + pv["meplat"] + aj["serrage"] / 2, 60, -2, 8)))
    e = e.cut(cyl_z(5 + aj["serrage"], 8, 71, 46, -1))
    e = e.cut(cyl_z(aj["passage_m3"], 8, 83, 46, -1)).cut(cyl_z(aj["taraud_m3"], 8, 93, 46, -1))
    e = e.union(cyl_z(30 + aj["moyeu"], 8, 95, 16, 6))   # téton du moyeu dans le 6806
    e = e.union(cyl_z(pv["d"] + aj["axe_imprime"], 8, 104, 46, 6))   # téton de pivot dans le 6801
    return e


def exporter_impression():
    os.makedirs(OUT_IMPR, exist_ok=True)
    for f in os.listdir(OUT_IMPR):
        if f.endswith((".stl", ".step")):
            os.remove(os.path.join(OUT_IMPR, f))
    for name in G.PIECES_IMPRIMEES:
        wp = a_plat(G.PARTS[name][0], ORIENTATION[name])
        cq.exporters.export(wp, os.path.join(OUT_IMPR, f"{name}.stl"), tolerance=0.01, angularTolerance=0.1)
        cq.exporters.export(wp, os.path.join(OUT_IMPR, f"{name}.step"))
    e = eprouvette()
    cq.exporters.export(e, os.path.join(OUT_PETG, "Eprouvette_Ajustements.stl"), tolerance=0.01, angularTolerance=0.1)
    cq.exporters.export(e, os.path.join(OUT_PETG, "Eprouvette_Ajustements.step"))
    print(f"  {len(G.PIECES_IMPRIMEES)} pièces à imprimer -> {OUT_IMPR} (STL + STEP), éprouvette -> {OUT_PETG}")


def traiter(mode):
    print(f"\n=== Tête rotative à vis sans fin — {'cas réel' if mode == 'reel' else 'démonstration PETG'} ===")
    G.set_ajustements(mode)
    build_parts()
    caler_dentures()
    name = "Tete_Rotative_VisSansFin" if mode == "reel" else "Tete_Rotative_PETG"
    path = OUT_REEL if mode == "reel" else os.path.join(OUT_PETG, f"{name}.step")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    assy = build_head(0.0, G.EL_REF, name, True)
    assy.export(path)
    G.clean_step_names(path)
    print(f"  {path} ({os.path.getsize(path) / 1e6:.1f} Mo)")
    if mode == "petg":
        exporter_impression()
    flat = verifier(assy)
    bilan(flat)


def main():
    traiter("reel")
    traiter("petg")
    G.set_ajustements("reel")


if __name__ == "__main__":
    main()
