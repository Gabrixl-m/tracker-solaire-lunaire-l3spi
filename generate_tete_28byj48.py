#!/usr/bin/env python3
"""
Tête rotative (pan-tilt) à deux moteurs pas à pas 28BYJ-48 (5 V, unipolaires),
posée sur la colonne Ø50 du trépied. Fichier à part du tracker complet.

Architecture (inspirée d'une tourelle « socle cylindrique + chape en U + tambour ») :
  - AZIMUT (axe vertical) : 28BYJ-48 fixé DANS le socle, arbre vers le HAUT, arbre sur
    l'axe d'azimut (son corps est décalé de 8 mm). Deux roulements 6806 portent la chape ;
    l'arbre du moteur n'entraîne que la rotation, par un méplat (accouplement flottant).
  - ÉLÉVATION (axe horizontal) : 28BYJ-48 logé DANS la chape, sous l'axe, arbre
    horizontal. Il entraîne l'axe d'élévation par une vis sans fin (module 1, rapport 50:1),
    irréversible : le panneau reste en place moteur coupé.
  - Le panneau 356 x 253 x 30 est vissé sur deux rails, sur une platine portée par
    deux demi-tambours calés sur l'axe d'élévation.

Repère de construction : Z vertical, origine sur l'axe, au dessus de la colonne du trépied.
Repère exporté : Y vertical (convention SolidWorks), comme le tracker complet.

Usage : python generate_tete_28byj48.py
"""

import math
import os
import re

import cadquery as cq
from cadquery import Location, Vector

import generate_tracker as G
from generate_tracker import box, box_span, cyl_x, cyl_z, ring_z, rot, trans

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CAD = os.path.join(HERE, "CAO")
OUT_PARTS = os.path.join(OUT_CAD, "pieces_tete_28BYJ48")

# ---------------------------------------------------------------------------
# PARAMÈTRES (mm)
# ---------------------------------------------------------------------------
Z_T = 136.0                 # axe d'élévation au-dessus du haut de la colonne
COL_OD, COL_ID = 50.0, 46.0  # colonne du trépied
SOCLE_OD, SOCLE_ID = 62.0, 56.0
Z_SOCLE_TOP = 65.0
Z_ROUL1, Z_ROUL2 = 58.0, 45.0      # roulements 6806 (Ø30/Ø42 x 7)
Z_FACE_AZ = 34.5                   # face (côté arbre) du moteur d'azimut
Z_CHAPE = 67.0                     # dessous de la semelle de la chape
ARM_X = (46.0, 55.0)               # bras de la chape (faces intérieure / extérieure)
D_PAN = 41.5                       # axe d'élévation -> dos du cadre du panneau
# engrenage roue / vis sans fin
M_VSF, Z_ROUE, DP_VIS = 1.0, 50, 16.0
ENTRAXE = M_VSF * Z_ROUE / 2 + DP_VIS / 2          # 33 mm
Z_VIS = Z_T - ENTRAXE                              # axe de la vis (et de l'arbre moteur)
Y_FACE_EL = -6.5                                   # face du moteur d'élévation
VIS_PHASE = 95.0       # calage de la vis pour él = 40° ; elle tourne de -50° par degré d'élévation

# 28BYJ-48 (cotes du constructeur)
BYJ = dict(d=28.0, h=19.0, offset=8.0, ear_pitch=35.0, ear_w=7.0, ear_t=0.8, ear_hole=4.2,
           boss_d=9.0, boss_h=1.5, shaft_d=5.0, shaft_l=10.0, flat=3.0,
           box_w=14.6, box_r=17.0, box_h=16.0,
           torque=0.034, ratio=64, steps=4096)   # couple d'entraînement ≥ 34 mN·m à 5 V

COLORS = {
    "socle":  cq.Color(0.45, 0.33, 0.25),
    "chape":  cq.Color(0.52, 0.39, 0.30),
    "tambour": cq.Color(0.12, 0.12, 0.13),
    "steel":  cq.Color(0.72, 0.72, 0.74),
    "motor":  cq.Color(0.78, 0.79, 0.80),
    "bluebox": cq.Color(0.20, 0.42, 0.85),
    "brass":  cq.Color(0.80, 0.65, 0.30),
    "peek":   cq.Color(0.82, 0.74, 0.56),
    "alu":    cq.Color(0.80, 0.81, 0.83),
    "ghost":  cq.Color(0.70, 0.70, 0.72),
}

DENS = {  # kg/m3
    "Al 6061-T6": 2700.0, "Acier inox 17-4PH": 7800.0, "Acier 440C": 7700.0,
    "PEEK + PTFE": 1440.0, "Ti-6Al-4V": 4430.0, "Al 7075-T73": 2810.0,
}
MOTOR_MASS = 0.033            # kg, 28BYJ-48


# ---------------------------------------------------------------------------
# PIÈCES STANDARD
# ---------------------------------------------------------------------------
def p_28byj48():
    """28BYJ-48. Repère : arbre selon +Z sur l'origine, face côté arbre en z = 0.
    Corps décalé de 8 mm vers -Y ; pattes selon X ; bloc de câbles bleu vers -Y."""
    b = BYJ
    oy = -b["offset"]
    body = cyl_z(b["d"], b["h"], 0, oy, -b["h"])
    ear = (box_span(-b["ear_pitch"] / 2, b["ear_pitch"] / 2, oy - b["ear_w"] / 2, oy + b["ear_w"] / 2,
                    -b["ear_t"], 0)
           .union(cyl_z(b["ear_w"], b["ear_t"], -b["ear_pitch"] / 2, oy, -b["ear_t"]))
           .union(cyl_z(b["ear_w"], b["ear_t"], b["ear_pitch"] / 2, oy, -b["ear_t"])))
    for sx in (-1, 1):
        ear = ear.cut(cyl_z(b["ear_hole"], 3, sx * b["ear_pitch"] / 2, oy, -2))
    boss = cyl_z(b["boss_d"], b["boss_h"])
    shaft = cyl_z(b["shaft_d"], b["shaft_l"], z=b["boss_h"])
    flats = (box_span(b["flat"] / 2, 4, -4, 4, b["boss_h"] + 4, b["boss_h"] + b["shaft_l"] + 1)
             .union(box_span(-4, -b["flat"] / 2, -4, 4, b["boss_h"] + 4, b["boss_h"] + b["shaft_l"] + 1)))
    shaft = shaft.cut(flats)
    can = body.union(ear).union(boss).union(shaft)
    blue = box_span(-b["box_w"] / 2, b["box_w"] / 2, oy - b["box_r"], oy - b["d"] / 2 + 3,
                    -b["h"] + 1.5, -b["h"] + 1.5 + b["box_h"])
    blue = blue.cut(cyl_z(b["d"], b["h"] + 2, 0, oy, -b["h"] - 1))   # plaqué contre le corps
    return can, blue


def p_roulement(od, idia, w):
    r = ring_z(od, idia, w)
    m = (od + idia) / 2
    return r.cut(ring_z(m + 1.5, m - 1.5, 0.6, w - 0.6))


def p_roulement_x(od, idia, w, x0):
    return (cq.Workplane("YZ").circle(od / 2).circle(idia / 2).extrude(w).translate((x0, 0, 0)))


# ---------------------------------------------------------------------------
# PIÈCES — SOCLE FIXE
# ---------------------------------------------------------------------------
def p_fond_socle():
    f = cyl_z(SOCLE_OD, 5)
    f = f.union(ring_z(COL_ID - 0.5, 36, 15, -15))          # centrage dans la colonne
    zt = Z_FACE_AZ - BYJ["ear_t"]
    for sx in (-1, 1):                                      # piliers du moteur d'azimut
        x, y = sx * BYJ["ear_pitch"] / 2, -BYJ["offset"]
        f = f.union(cyl_z(6, zt - 5, x, y, 5)).cut(cyl_z(2.5, zt, x, y, 6))   # taraudage M3
    for k in range(3):                                      # vis de fixation au socle
        a = math.radians(120 * k)
        f = f.cut(cyl_z(3.4, 8, 25 * math.cos(a), 25 * math.sin(a), -1))
    return f


def p_socle():
    s = ring_z(SOCLE_OD, SOCLE_ID, 54, 5)
    s = s.union(cyl_z(SOCLE_OD, 6, z=59))
    s = s.union(ring_z(50, 42, 14, 45))                     # logement des roulements
    s = s.union(ring_z(42, 36, 6, 52))                      # épaulement entre roulements
    s = s.cut(cyl_z(42, 8, z=58))                           # alésage roulement haut
    s = s.cut(cyl_z(36, 20, z=50))
    s = s.cut(cyl_x(9, 10, -5, 0, 0).rotate((0, 0, 0), (0, 0, 1), 90).translate((0, -SOCLE_OD / 2 + 2, 14)))
    for k in range(3):                                      # bossages des vis du fond
        a = math.radians(120 * k)
        x, y = 25 * math.cos(a), 25 * math.sin(a)
        s = s.union(cyl_z(7, 8, x, y, 5)).cut(cyl_z(2.6, 9, x, y, 4))
    return s


# ---------------------------------------------------------------------------
# PIÈCES — CHAPE (tourne en azimut)
# ---------------------------------------------------------------------------
def p_chape():
    xi, xo = ARM_X
    c = box_span(-xo, xo, -24, 24, Z_CHAPE, Z_CHAPE + 8).edges("|Z").fillet(6)
    arm = (cq.Workplane("YZ").moveTo(-24, Z_CHAPE).lineTo(24, Z_CHAPE).lineTo(32, Z_T)
           .threePointArc((0, Z_T + 32), (-32, Z_T)).close().extrude(xo - xi))
    c = c.union(arm.translate((xi, 0, 0))).union(arm.translate((-xo, 0, 0)))
    # moyeu d'azimut dans les roulements
    c = c.union(cyl_z(30, Z_CHAPE - 42, z=42)).union(cyl_z(34, 2, z=Z_CHAPE - 2))
    c = c.cut(cyl_z(20, Z_CHAPE + 8 - 46, z=47))            # passage des câbles
    # barrette d'accouplement à méplats (arbre du moteur d'azimut)
    win = cyl_z(20, 6.5, z=41)
    c = c.cut(win.intersect(box_span(-11, 11, -11, -4, 40, 48))).cut(win.intersect(box_span(-11, 11, 4, 11, 40, 48)))
    dhole = cyl_z(BYJ["shaft_d"] + 0.1, 8, z=40).intersect(box_span(-1.55, 1.55, -3, 3, 40, 48))
    c = c.cut(dhole)
    # logements des roulements 608 et passage de l'axe d'élévation
    c = c.cut(cyl_x(10, 2 * xo + 2, -xo - 1, 0, Z_T))
    c = c.cut(cyl_x(22, 7, xo - 7, 0, Z_T)).cut(cyl_x(22, 7, -xo, 0, Z_T))
    # trous de fixation : support moteur, butée
    for x in (-17, 17):
        c = c.cut(cyl_z(3.4, 10, x, -9.3, Z_CHAPE - 1))
    c = c.cut(cyl_z(3.4, 10, 0, 7.5, Z_CHAPE - 1))
    return c


def p_bague_arret():
    return ring_z(34, 30, 3, 42)


def p_support_moteur_el():
    zb = Z_CHAPE + 8
    zc = Z_VIS - BYJ["offset"]                              # centre du corps du moteur
    s = box_span(-22, 22, Y_FACE_EL - BYJ["ear_t"] - 4, Y_FACE_EL - BYJ["ear_t"], zb, Z_VIS)
    s = s.union(box_span(-22, 22, -16, Y_FACE_EL - BYJ["ear_t"], zb, zb + 5))    # semelle
    s = s.cut(cyl_y(29.5, 20, 0, -20, zc))
    s = s.cut(box_span(-8, 8, -20, 0, zb - 1, zc))          # passage du bloc de câbles
    for sx in (-1, 1):
        s = s.cut(cyl_y(3.4, 20, sx * BYJ["ear_pitch"] / 2, -20, zc))
        s = s.cut(cyl_z(3.4, 10, sx * 17, -9.3, zb - 1))
    return s


def p_butee_vis():
    zb = Z_CHAPE + 8
    yb = Y_FACE_EL + BYJ["boss_h"] + BYJ["shaft_l"]         # bout de l'arbre moteur
    b = box_span(-6, 6, yb + 0.5, yb + 4.5, zb, Z_T - 28)
    b = b.union(box_span(-6, 6, yb + 0.5, yb + 10, zb, zb + 5))
    b = b.union(cyl_y(6, 0.5, 0, yb, Z_VIS))                # grain de butée (reprend la poussée axiale)
    return b.cut(cyl_z(3.4, 10, 0, 7.5, zb - 1))


def cyl_y(d, L, x, y0, z):
    """Cylindre d'axe Y, de y0 à y0+L."""
    return cq.Workplane("XZ").circle(d / 2).extrude(-L).translate((x, y0, z))


def p_vis_sans_fin():
    """Vis sans fin module 1, un filet, Ø primitif 16, longueur 9 (axe Z, centrée)."""
    m, dp, L = M_VSF, DP_VIS, 9.0
    rr, h = dp / 2 - 1.25 * m, 2.25 * m
    lead = math.pi * m
    t_pitch = lead / 2 - 0.15                    # épaisseur du filet au primitif (jeu)
    tan_a = math.tan(math.radians(20))
    w_root = t_pitch + 2 * tan_a * 1.25 * m
    w_tip = t_pitch - 2 * tan_a * 1.0 * m
    z0 = -L / 2 - lead
    helix = cq.Wire.makeHelix(pitch=lead, height=L + 2 * lead, radius=rr, center=Vector(0, 0, z0))
    prof = (cq.Workplane("XZ").polyline([(rr - 0.3, z0 - w_root / 2), (rr + h, z0 - w_tip / 2),
                                         (rr + h, z0 + w_tip / 2), (rr - 0.3, z0 + w_root / 2)]).close())
    thread = prof.sweep(cq.Workplane().add(helix), isFrenet=True)
    worm = cyl_z(2 * rr, L, z=-L / 2).union(thread).intersect(cyl_z(dp + 2 * m + 1, L, z=-L / 2))
    bore = cyl_z(BYJ["shaft_d"] + 0.1, L + 2, z=-L / 2 - 1).intersect(box_span(-1.55, 1.55, -3, 3, -L, L))
    return worm.cut(bore)


# ---------------------------------------------------------------------------
# PIÈCES — PARTIE BASCULANTE (repère : origine sur l'axe d'élévation, X = axe,
#           Z = normale au panneau, panneau côté +Z)
# ---------------------------------------------------------------------------
def p_axe_elevation():
    return cyl_x(8, 124, -62)


def p_bague_axe():
    b = cyl_x(14, 4.5, 55.5).cut(cyl_x(8, 6, 55))
    return b.union(cyl_z(4, 3, 57.75, 0, 6))                 # vis de pression


def p_roue_vsf():
    g = G.gear_x(Z_ROUE, M_VSF, 8, -4, backlash=0.1)
    g = g.union(cyl_x(16, 14, -7))
    g = g.cut(cyl_x(8, 16, -8))
    for k in range(5):
        a = math.radians(72 * k)
        g = g.cut(cyl_x(7, 10, -5, 15 * math.cos(a), 15 * math.sin(a)))
    return g


def p_demi_tambour():
    t = cyl_x(56, 26, 16)
    t = t.cut(cyl_x(48, 23, 20))                             # creux, voile côté centre
    t = t.cut(box_span(10, 50, -30, 30, 26.5, 40))           # méplat d'appui de la platine
    t = t.union(cyl_x(16, 26, 16)).cut(cyl_x(8, 30, 14))     # moyeu sur l'axe Ø8
    t = t.cut(cyl_z(3, 27, 18, 0, -30))                      # vis de pression
    return t


def p_platine():
    p = box_span(-42, 42, -20, 20, 26.5, 31.5)
    p = p.cut(box_span(-6, 6, -11, 11, 25, 33))              # dégagement de la roue
    for x in (-36, 36):
        for y in (-14, 14):
            p = p.cut(cyl_z(3.4, 8, x, y, 25))
    for x in (-29, 29):
        p = p.cut(cyl_z(3.4, 8, x, 0, 25))
    return p


def p_rail_panneau():
    r = box_span(-6, 6, -G.P["pan_H"] / 2, G.P["pan_H"] / 2, 31.5, D_PAN)
    for y in (-14, 14, -G.P["pan_H"] / 2 + 6, G.P["pan_H"] / 2 - 6):
        r = r.cut(cyl_z(3.4, 14, 0, y, 30))
    return r


def p_haut_colonne():
    return ring_z(COL_OD, COL_ID, 80, -80)


# ---------------------------------------------------------------------------
# ASSEMBLAGE
# ---------------------------------------------------------------------------
PARTS = {}


def reg(name, wp, mat, col, desc):
    PARTS[name] = (wp, mat, col, desc)


def build_parts(with_panel):
    PARTS.clear()
    can, blue = p_28byj48()
    reg("Haut_Colonne_Trepied", p_haut_colonne(), "Al 7075-T73", COLORS["ghost"], "Référence : haut de la colonne Ø50")
    reg("Fond_Socle", p_fond_socle(), "Al 6061-T6", COLORS["socle"], "Fond du socle, centrage Ø45,5 dans la colonne")
    reg("Socle", p_socle(), "Al 6061-T6", COLORS["socle"], "Socle cylindrique Ø62, logement des roulements")
    reg("Roulement_6806", p_roulement(42, 30, 7), "Acier 440C", COLORS["steel"], "Roulement 6806-ZZ Ø30/Ø42 x 7")
    reg("Moteur_28BYJ48", can, "moteur", COLORS["motor"], "Moteur pas à pas 28BYJ-48 5 V")
    reg("Moteur_28BYJ48_Bloc_Cables", blue, "moteur", COLORS["bluebox"], "Capot des connexions du 28BYJ-48")
    reg("Chape", p_chape(), "Al 6061-T6", COLORS["chape"], "Chape en U (moyeu d'azimut + bras)")
    reg("Bague_Arret_Moyeu", p_bague_arret(), "Acier inox 17-4PH", COLORS["steel"], "Bague d'arrêt du moyeu")
    reg("Roulement_608", p_roulement_x(22, 8, 7, 0), "Acier 440C", COLORS["steel"], "Roulement 608-ZZ Ø8/Ø22 x 7")
    reg("Support_Moteur_Elevation", p_support_moteur_el(), "Al 6061-T6", COLORS["chape"], "Support du moteur d'élévation")
    reg("Butee_Vis_Sans_Fin", p_butee_vis(), "Al 6061-T6", COLORS["chape"], "Butée axiale de la vis sans fin")
    reg("Vis_Sans_Fin", p_vis_sans_fin(), "Acier inox 17-4PH", COLORS["steel"], "Vis sans fin m1, 1 filet, Ø16")
    reg("Axe_Elevation", p_axe_elevation(), "Acier inox 17-4PH", COLORS["steel"], "Axe d'élévation Ø8")
    reg("Bague_Axe", p_bague_axe(), "Acier inox 17-4PH", COLORS["steel"], "Bague d'arrêt de l'axe Ø8")
    reg("Roue_Vis_Sans_Fin", p_roue_vsf(), "PEEK + PTFE", COLORS["peek"], "Roue m1 Z50 (rapport 50:1)")
    reg("Demi_Tambour", p_demi_tambour(), "Al 6061-T6", COLORS["tambour"], "Demi-tambour Ø56, porte la platine")
    reg("Platine_Panneau", p_platine(), "Al 6061-T6", COLORS["alu"], "Platine de liaison au panneau")
    reg("Rail_Panneau", p_rail_panneau(), "Al 6061-T6", COLORS["alu"], "Rail 12 x 10 vissé sur le cadre du panneau")
    if with_panel:
        G.P["pan_back"] = D_PAN
        reg("Cadre_Panneau", G.p_cadre_pv(), "Al 6063-T5", G.COL["alu"], "Cadre du panneau 356 x 253 x 30")
        reg("Lamine_PV", G.p_lamine(), "Verre 3,2 mm + EVA + backsheet (eq)", G.COL["pv_bg"], "Verre + EVA")
        reg("Cellules_PV", G.p_cellules()[0], "Silicium polycristallin", G.COL["pv"], "72 cellules")
        reg("Boite_Jonction", G.p_boite_jonction(), "PPO (boîte de jonction)", G.COL["black"], "Boîte de jonction")


def add(assy, part, loc=None, inst=None):
    wp, _m, col, _d = PARTS[part]
    assy.add(wp, name=inst or part, loc=loc or Location(), color=col)


def add_motor(assy, inst, loc):
    m = cq.Assembly(name=inst)
    add(m, "Moteur_28BYJ48")
    add(m, "Moteur_28BYJ48_Bloc_Cables")
    assy.add(m, name=inst, loc=loc)


def build_basculant(with_panel):
    b = cq.Assembly(name="SA_Basculant")
    add(b, "Axe_Elevation")
    add(b, "Bague_Axe", inst="Bague_Axe_1")
    add(b, "Bague_Axe", rot((0, 0, 1), 180), "Bague_Axe_2")
    add(b, "Roue_Vis_Sans_Fin")
    add(b, "Demi_Tambour", inst="Demi_Tambour_1")
    add(b, "Demi_Tambour", rot((0, 0, 1), 180), "Demi_Tambour_2")
    add(b, "Platine_Panneau")
    add(b, "Rail_Panneau", trans(36, 0, 0), "Rail_Panneau_1")
    add(b, "Rail_Panneau", trans(-36, 0, 0), "Rail_Panneau_2")
    if with_panel:
        for n in ("Cadre_Panneau", "Lamine_PV", "Cellules_PV", "Boite_Jonction"):
            add(b, n)
    return b


def build_head(az, el, name, with_panel):
    root = cq.Assembly(name=name)
    Y = G.TO_YUP
    ref = cq.Assembly(name="SA_Reference_Trepied")
    add(ref, "Haut_Colonne_Trepied")
    root.add(ref, name="SA_Reference_Trepied", loc=Y)

    s = cq.Assembly(name="SA_Socle")
    add(s, "Fond_Socle")
    add(s, "Socle")
    add(s, "Roulement_6806", trans(0, 0, Z_ROUL1), "Roulement_6806_1")
    add(s, "Roulement_6806", trans(0, 0, Z_ROUL2), "Roulement_6806_2")
    add_motor(s, "Moteur_Azimut", trans(0, 0, Z_FACE_AZ))
    root.add(s, name="SA_Socle", loc=Y)

    c = cq.Assembly(name="SA_Chape")
    add(c, "Chape")
    add(c, "Bague_Arret_Moyeu")
    add(c, "Roulement_608", trans(ARM_X[1] - 7, 0, Z_T), "Roulement_608_1")
    add(c, "Roulement_608", trans(-ARM_X[1], 0, Z_T), "Roulement_608_2")
    add(c, "Support_Moteur_Elevation")
    add(c, "Butee_Vis_Sans_Fin")
    # moteur d'élévation : arbre selon +Y, corps sous l'arbre ; vis sans fin sur l'arbre
    add_motor(c, "Moteur_Elevation", trans(0, Y_FACE_EL, Z_VIS) * rot((0, 1, 1), 180))
    y_vis = Y_FACE_EL + BYJ["boss_h"] + BYJ["shaft_l"] - 0.5 - 4.5
    phase = (VIS_PHASE - Z_ROUE * (el - 40.0)) % 360.0     # filet engagé entre deux dents de la roue
    add(c, "Vis_Sans_Fin", trans(0, y_vis, Z_VIS) * rot((1, 0, 0), -90) * rot((0, 0, 1), phase))
    c.add(build_basculant(with_panel), name="SA_Basculant",
          loc=trans(0, 0, Z_T) * rot((1, 0, 0), el - 90))
    root.add(c, name="SA_Chape", loc=Y * rot((0, 0, 1), az))
    return root


def inst_part(inst):
    base = inst.split("/")[-1]
    if base in PARTS:
        return base
    b2 = re.sub(r"_\d+$", "", base)
    return b2 if b2 in PARTS else None


def clean_names(path):
    txt = open(path, encoding="utf-8", errors="replace").read()

    def sub(m):
        k = inst_part(m.group(1))
        return f"PRODUCT('{k}','{k}'" if k else m.group(0)
    open(path, "w", encoding="utf-8").write(re.sub(r"PRODUCT\('([^']*)','\1'", sub, txt))


def mass_of(inst, shp):
    k = inst_part(inst)
    mat = PARTS[k][1]
    if mat == "moteur":
        return k, MOTOR_MASS if k == "Moteur_28BYJ48" else 0.0
    dens = DENS.get(mat) or G.MAT[mat]
    return k, shp.Volume() * dens * 1e-9


# ---------------------------------------------------------------------------
# PRINCIPAL
# ---------------------------------------------------------------------------
POSES = {
    "Tete_Rotative_28BYJ48": (0.0, 40.0, False),
    "Tete_Rotative_28BYJ48_avec_panneau": (0.0, 40.0, True),
}


def tilt_torque():
    """Couple de gravité maxi sur l'axe d'élévation (partie basculante + panneau)."""
    build_parts(True)
    flat = G.flatten(build_basculant(True))
    M, S = 0.0, Vector(0, 0, 0)
    for n, s in flat:
        _k, m = mass_of(n, s)
        M += m
        S = S + cq.Shape.centerOfMass(s) * m
    cg = S * (1 / M)
    r = math.hypot(cg.y, cg.z)                       # distance du CdG à l'axe (X)
    return M, r


def main():
    os.makedirs(OUT_PARTS, exist_ok=True)
    for f in os.listdir(OUT_PARTS):
        if f.endswith(".step"):
            os.remove(os.path.join(OUT_PARTS, f))
    results = {}
    for fname, (az, el, wp) in POSES.items():
        build_parts(wp)
        assy = build_head(az, el, fname, wp)
        path = os.path.join(OUT_CAD, f"{fname}.step")
        assy.export(path)
        clean_names(path)
        results[fname] = assy
        print(f"{fname}.step : {os.path.getsize(path) / 1e6:.1f} Mo")
    for name, (wp, _m, _c, _d) in PARTS.items():
        if name in ("Haut_Colonne_Trepied",):
            continue
        cq.exporters.export(wp, os.path.join(OUT_PARTS, f"{name}.step"))

    # masses
    flat = G.flatten(results["Tete_Rotative_28BYJ48_avec_panneau"])
    tot = {"tete": 0.0, "panneau": 0.0}
    for n, s in flat:
        k, m = mass_of(n, s)
        if k == "Haut_Colonne_Trepied":
            continue
        tot["panneau" if k in ("Cadre_Panneau", "Lamine_PV", "Cellules_PV", "Boite_Jonction") else "tete"] += m
    print(f"Masse de la tête : {tot['tete']:.2f} kg ; panneau : {tot['panneau']:.2f} kg")

    # dimensionnement des motorisations
    M, r = tilt_torque()
    lam = math.atan(M_VSF / DP_VIS)
    for mu in (0.10, 0.15):
        phi = math.atan(mu)
        eta = math.tan(lam) / math.tan(lam + phi)
        t_out = BYJ["torque"] * Z_ROUE * eta
        print(f"Élévation (μ = {mu}) : angle d'hélice {math.degrees(lam):.2f}° < frottement "
              f"{math.degrees(phi):.2f}° -> irréversible ; rendement {eta:.2f} ; couple dispo {t_out:.2f} N·m")
    print(f"Partie basculante : {M:.2f} kg, CdG à {r:.1f} mm de l'axe -> couple maxi "
          f"{M * 1.62 * r / 1000:.3f} N·m (Lune), {M * 9.81 * r / 1000:.3f} N·m (Terre)")
    print(f"Résolution : azimut {360 / BYJ['steps']:.3f}°/demi-pas, élévation "
          f"{360 / BYJ['steps'] / Z_ROUE:.4f}°/demi-pas")

    # interférences
    print("\nInterférences statiques :")
    for fname, assy in results.items():
        build_parts(POSES[fname][2])
        flat = G.flatten(assy)
        hits = G.interference(flat)
        print(f"  {fname}: {'aucune' if not hits else hits}")

    # garde sur toute la plage d'élévation
    build_parts(True)
    worst = (1e9,)
    for el in (-2.0, 0.0, 15.0, 45.0, 75.0, 92.0):
        flat = G.flatten(build_head(0.0, el, "chk", True))
        mov = [(n, s) for n, s in flat if "/SA_Basculant/" in n
               and not inst_part(n).startswith(("Axe_Elevation", "Roue_Vis", "Bague_Axe", "Cellules"))]
        fix = [(n, s) for n, s in flat if "/SA_Basculant/" not in n]
        d = G.min_clearance(mov, fix, cutoff=30.0)
        if d[0] < worst[0]:
            worst = d + (el,)
    print(f"\nGarde mini partie basculante (élévation -2° à 92°) : {worst[0]:.1f} mm "
          f"({str(worst[1]).split('/')[-1]} / {str(worst[2]).split('/')[-1]}, él={worst[3]}°)")


if __name__ == "__main__":
    main()
