#!/usr/bin/env python3
"""
Tête rotative motorisée, deux versions, SANS contrepoids, structure conservée :
socle cylindrique Ø62 sur la colonne du trépied, chape en U, chapeau en U renversé
portant le panneau 356 x 253 x 30 (pivots Ø8 sur roulements 608).

  VERSION "VSF" (vis sans fin, irréversible sur les deux axes) :
    - élévation : NEMA 17 court (34 mm) + vis sans fin m1 Ø16 + roue Z50 (50:1)
    - azimut    : NEMA 11 (28 mm) + vis sans fin m0,8 Ø12 + roue fixe Z60 (60:1)
    Chaque vis tourne sur son propre arbre (2 roulements 685) et un accouplement
    la relie au moteur : le moteur ne subit pas la poussée de la vis.
  VERSION "ENG" (engrenages droits) :
    - élévation : NEMA 17 (40 mm) + pignon Z15 / secteur denté Z120 m0,8 (8:1)
    - azimut    : NEMA 17 court (34 mm) + pignon Z18 / couronne fixe Z92 m0,8 (5,1:1)

En azimut, la roue (ou la couronne) est FIXÉE sur le socle et le moteur est porté par
la chape : son pignon (ou sa vis) roule autour, comme sur une tourelle à couronne.
Les deux moteurs tournent donc avec le panneau : aucun ne gêne le panneau.

Usage : python generate_tete_motorisee.py            (les deux versions)
"""

import math
import os
import re
import sys

import cadquery as cq
from cadquery import Location, Vector

import generate_tracker as G
from generate_tracker import box_span, cyl_x, cyl_z, ring_z, rot, trans

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CAD = os.path.join(HERE, "CAO")

# ---------------------------------------------------------------------------
# PARAMÈTRES COMMUNS (mm)
# ---------------------------------------------------------------------------
COL_OD, COL_ID = 50.0, 46.0
SOCLE_OD, SOCLE_ID = 62.0, 56.0
Z_ROUL1, Z_ROUL2 = 58.0, 45.0        # roulements 6806 d'azimut
ARM_X = (40.0, 48.0)                 # bras de la chape
ARM_R = 24.0
U_X = (50.0, 56.0)                   # flancs du chapeau en U
U_TOP = (28.0, 33.0)                 # plaque du chapeau (rayons)
U_Y = 22.0
U_BAS = -25.0                        # bas des flancs (sous l'axe), sans contrepoids
D_PAN = 46.0                         # axe d'élévation -> dos du panneau
RAIL_X = 44.0
X_SORTIE = (-34.0, -26.0)            # roue / grande roue d'élévation sur le pivot gauche
EL_REF = 40.0                        # élévation des fichiers exportés

# Cas de charge
G_LUNE, G_TERRE = 1.62, 9.81
VENT_EL, VENT_AZ = 0.35, 0.50        # couple de vent à 10 m/s (N·m), voir README
FROT_EL, FROT_AZ = 0.01, 0.02        # roulements, câbles
K_RUN = 0.70                         # couple en marche lente / couple de maintien (TMC2209, micro-pas)

# Moteurs pas à pas (valeurs typiques de catalogue)
MOTEURS = {
    "NEMA11_45": dict(c=28.2, L=45.0, pilot=22.0, holes=23.0, hole_d=2.5, shaft=20.0,
                      hold=0.095, amp=0.67, masse=0.14, nom="NEMA 11, 28 x 28 x 45 mm"),
    "NEMA17_34": dict(c=42.3, L=34.0, pilot=22.0, holes=31.0, hole_d=3.0, shaft=24.0,
                      hold=0.28, amp=1.3, masse=0.22, nom="NEMA 17, 42 x 42 x 34 mm"),
    "NEMA17_40": dict(c=42.3, L=40.0, pilot=22.0, holes=31.0, hole_d=3.0, shaft=24.0,
                      hold=0.42, amp=1.5, masse=0.28, nom="NEMA 17, 42 x 42 x 40 mm"),
}

VERSIONS = {
    "VSF": dict(
        nom="Tete_Rotative_VisSansFin", Z_CHAPE=92.0, Z_T=156.0,
        moteur_el="NEMA17_34", moteur_az="NEMA11_45",
        el=dict(type="vis", m=1.0, z=50, dp=16.0, L=10.0),
        az=dict(type="vis", m=0.8, z=60, dp=12.0, L=9.0),
    ),
    "ENG": dict(
        nom="Tete_Rotative_Engrenages", Z_CHAPE=79.0, Z_T=164.0,
        moteur_el="NEMA17_40", moteur_az="NEMA17_34",
        el=dict(type="eng", m=0.8, zp=15, zr=120),
        az=dict(type="eng", m=0.8, zp=18, zr=92),
    ),
}
V = None              # version courante (dict)

COLORS = {
    "socle": cq.Color(0.45, 0.33, 0.25), "chape": cq.Color(0.86, 0.72, 0.30),
    "u": cq.Color(0.33, 0.45, 0.80), "steel": cq.Color(0.72, 0.72, 0.74),
    "motor": cq.Color(0.14, 0.14, 0.15), "brass": cq.Color(0.80, 0.65, 0.30),
    "peek": cq.Color(0.82, 0.74, 0.56), "orange": cq.Color(0.93, 0.45, 0.12),
    "alu": cq.Color(0.80, 0.81, 0.83), "ghost": cq.Color(0.70, 0.70, 0.72),
    "coupler": cq.Color(0.55, 0.60, 0.85),
}
DENS = {"Al 6061-T6": 2700.0, "Acier inox 17-4PH": 7800.0, "Acier 440C": 7700.0,
        "Bronze CuSn12": 8800.0, "Al 7075-T73": 2810.0}


# ---------------------------------------------------------------------------
# OUTILS
# ---------------------------------------------------------------------------
def cyl_y(d, L, x, y0, z):
    return cq.Workplane("XZ").circle(d / 2).extrude(-L).translate((x, y0, z))


def roulement_x(od, idia, w):
    return cq.Workplane("YZ").circle(od / 2).circle(idia / 2).extrude(w)


def roulement_z(od, idia, w):
    r = ring_z(od, idia, w)
    m = (od + idia) / 2
    return r.cut(ring_z(m + 1.5, m - 1.5, 0.6, w - 0.6))


def p_nema(key):
    """Moteur pas à pas : face avant en z = 0, arbre selon +Z, corps vers -Z."""
    m = MOTEURS[key]
    c, L = m["c"], m["L"]
    body = box_span(-c / 2, c / 2, -c / 2, c / 2, -L, 0).edges("|Z").chamfer(c * 0.09)
    body = body.cut(box_span(-c, c, -c, c, -L + 6, -L + 7).cut(cyl_z(c * 0.95, 3, z=-L + 5)))  # rainure d'aspect
    body = body.union(cyl_z(m["pilot"], 2)).union(cyl_z(5, m["shaft"]))
    for sx in (-1, 1):
        for sy in (-1, 1):
            body = body.cut(cyl_z(m["hole_d"], 4.5, sx * m["holes"] / 2, sy * m["holes"] / 2, -4.5))
    return body.union(box_span(-6, 6, c / 2 - 1, c / 2 + 5, -L + 2, -L + 12))     # connecteur


def p_vis(m, dp, L):
    """Vis sans fin un filet, axe Z centré, alésage Ø5 (sur son arbre)."""
    rr, h = dp / 2 - 1.25 * m, 2.25 * m
    lead = math.pi * m
    t = lead / 2 - 0.15 * m
    ta = math.tan(math.radians(20))
    w_root, w_tip = t + 2 * ta * 1.25 * m, t - 2 * ta * m
    z0 = -L / 2 - lead
    helix = cq.Wire.makeHelix(pitch=lead, height=L + 2 * lead, radius=rr, center=Vector(0, 0, z0))
    prof = cq.Workplane("XZ").polyline([(rr - 0.3, z0 - w_root / 2), (rr + h, z0 - w_tip / 2),
                                        (rr + h, z0 + w_tip / 2), (rr - 0.3, z0 + w_root / 2)]).close()
    thread = prof.sweep(cq.Workplane().add(helix), isFrenet=True)
    w = cyl_z(2 * rr, L, z=-L / 2).union(thread).intersect(cyl_z(dp + 2 * m + 1, L, z=-L / 2))
    return w.cut(cyl_z(5, L + 2, z=-L / 2 - 1))


def p_accouplement():
    a = cyl_z(19, 25).cut(cyl_z(5, 27, z=-1))
    for z0 in (8.0, 15.0):
        a = a.cut(ring_z(20, 15, 1.2, z0))                  # fentes d'aspect (accouplement flexible)
    return a


# ---------------------------------------------------------------------------
# PIÈCES COMMUNES
# ---------------------------------------------------------------------------
def p_haut_colonne():
    return ring_z(COL_OD, COL_ID, 80, -80)


def p_fond_socle():
    f = cyl_z(SOCLE_OD, 5).union(ring_z(COL_ID - 0.5, 36, 15, -15))
    for k in range(3):
        a = math.radians(120 * k)
        f = f.cut(cyl_z(3.4, 8, 25 * math.cos(a), 25 * math.sin(a), -1))
    return f


def p_socle():
    s = ring_z(SOCLE_OD, SOCLE_ID, 54, 5).union(cyl_z(SOCLE_OD, 6, z=59))
    s = s.union(ring_z(50, 42, 14, 45)).union(ring_z(42, 36, 6, 52))
    s = s.cut(cyl_z(42, 8, z=58)).cut(cyl_z(36, 20, z=50))
    s = s.cut(cyl_y(9, 10, 0, -SOCLE_OD / 2 + 5, 14))       # passe-câble
    for k in range(3):
        a = math.radians(120 * k)
        x, y = 25 * math.cos(a), 25 * math.sin(a)
        s = s.union(cyl_z(7, 8, x, y, 5)).cut(cyl_z(2.6, 9, x, y, 4))
    for k in range(6):                                      # fixation de la roue / couronne fixe
        a = math.radians(30 + 60 * k)
        s = s.cut(cyl_z(2.6, 8, 23.5 * math.cos(a), 23.5 * math.sin(a), 59))
    return s


def p_chape():
    xi, xo = ARM_X
    zc = V["Z_CHAPE"]
    plate = box_span(-xo, xo, -ARM_R, ARM_R, zc, zc + 8)
    if V is VERSIONS["VSF"]:
        plate = plate.union(box_span(-60, -2, -60, -ARM_R + 1, zc, zc + 8))      # queue : les deux moteurs
    else:
        plate = plate.union(box_span(-25, 25, -68, -ARM_R + 1, zc, zc + 8))      # queue : moteur d'azimut
    c = plate.edges("|Z").fillet(5)
    arm = (cq.Workplane("YZ").moveTo(-ARM_R, zc).lineTo(ARM_R, zc).lineTo(ARM_R, V["Z_T"])
           .threePointArc((0, V["Z_T"] + ARM_R), (-ARM_R, V["Z_T"])).close().extrude(xo - xi))
    c = c.union(arm.translate((xi, 0, 0))).union(arm.translate((-xo, 0, 0)))
    c = c.union(cyl_z(30, zc - 42, z=42)).union(cyl_z(34, 2, z=65))              # moyeu d'azimut
    c = c.cut(cyl_z(20, zc + 10 - 40, z=40))                                     # passage des câbles
    c = c.cut(cyl_x(10, 2 * xo + 2, -xo - 1, 0, V["Z_T"]))
    c = c.cut(cyl_x(22, 7, xo - 7, 0, V["Z_T"])).cut(cyl_x(22, 7, -xo, 0, V["Z_T"]))
    if V is VERSIONS["ENG"]:                                # passage de l'arbre du moteur d'azimut
        c = c.cut(cyl_z(23, 12, 0, -AZ_ENG_C, zc - 2))
    return c


def p_bague_arret():
    return ring_z(34, 30, 3, 42)


def p_chapeau_u():
    xi, xo = U_X
    u = box_span(-xo, xo, -ARM_R, ARM_R, U_TOP[0], U_TOP[1])
    for x0, x1 in ((xi, xo), (-xo, -xi)):
        u = u.union(box_span(x0, x1, -U_Y, U_Y, U_BAS, U_TOP[1]).edges("|X and <Z").fillet(8))
    u = u.cut(cyl_x(8, 2 * xo + 2, -xo - 1))
    for x in (-RAIL_X, RAIL_X):
        for y in (-14, 14):
            u = u.cut(cyl_z(3.4, 10, x, y, U_TOP[0] - 1))
    return u


def p_pivot_entraine():
    """Pivot gauche : serré dans le chapeau, roulement 608, porte la roue d'élévation."""
    return cyl_x(8, U_X[1] + X_SORTIE[1] + 2, -U_X[1]).union(cyl_x(12, 2, -U_X[1] - 2))


def p_pivot_libre():
    return cyl_x(8, U_X[1] - ARM_X[0] + 1, ARM_X[0] - 1).union(cyl_x(12, 2, U_X[1]))


def p_rail():
    r = box_span(-6, 6, -G.P["pan_H"] / 2, G.P["pan_H"] / 2, U_TOP[1], D_PAN)
    for y in (-14, 14, -G.P["pan_H"] / 2 + 6, G.P["pan_H"] / 2 - 6):
        r = r.cut(cyl_z(3.4, 20, 0, y, U_TOP[1] - 1))
    return r


# ---------------------------------------------------------------------------
# VERSION VIS SANS FIN
# ---------------------------------------------------------------------------
# azimut : roue fixe Z60 m0,8 (z 72..80), vis le long de X en (y = -30, z = 76)
AZ_VSF = dict(zr=(72.0, 80.0), y=-30.0, z=76.0, palier=(14.0, 19.0), x_joint=-32.5, x_face=-52.5)
# élévation : vis le long de Y en (x = -30, z = Z_T - 33)
EL_VSF = dict(palier=(14.0, 19.0), y_joint=-32.5, y_face=-56.5)
B685 = (11.0, 5.0, 5.0)               # roulement 685 : Ø11 / Ø5 x 5


def p_roue_az_vsf():
    a = V["az"]
    r = G.gear_z(a["z"], a["m"], 8, AZ_VSF["zr"][0], backlash=0.15)
    r = r.union(ring_z(50, 36, AZ_VSF["zr"][0] - 65, 65))
    r = r.cut(cyl_z(36, 30, z=60))
    for k in range(6):
        ang = math.radians(30 + 60 * k)
        r = r.cut(cyl_z(2.9, 20, 23.5 * math.cos(ang), 23.5 * math.sin(ang), 60))
    return r


def p_arbre_vis_az():
    x1 = AZ_VSF["palier"][1] + 1
    return cq.Workplane("YZ").circle(2.5).extrude(x1 - AZ_VSF["x_joint"]).translate((AZ_VSF["x_joint"], AZ_VSF["y"], AZ_VSF["z"]))


def p_palier_vis_az():
    p0, p1 = AZ_VSF["palier"]
    y, z, zc = AZ_VSF["y"], AZ_VSF["z"], V["Z_CHAPE"]
    b = None
    for x0, x1 in ((p0, p1), (-p1, -p0)):
        pl = box_span(x0, x1, y - 8, y + 7, z - 7, zc).cut(cyl_x(B685[0], x1 - x0 + 2, x0 - 1, y, z))
        b = pl if b is None else b.union(pl)
    b = b.union(box_span(-p1, p1, y - 8, y + 7, zc - 5, zc))
    for x in (-16.5, 16.5):
        b = b.cut(cyl_z(3.4, 8, x, y, zc - 6))
    return b


def p_support_moteur_az_vsf():
    m = MOTEURS[V["moteur_az"]]
    y, z, zc = AZ_VSF["y"], AZ_VSF["z"], V["Z_CHAPE"]
    x1 = AZ_VSF["x_face"] + 4
    s = box_span(AZ_VSF["x_face"], x1, y - 16, y + 16, z - 16, zc)
    s = s.union(box_span(AZ_VSF["x_face"], x1 + 11, y - 16, y + 7, zc - 5, zc))
    s = s.cut(cyl_x(m["pilot"] + 0.5, 10, AZ_VSF["x_face"] - 1, y, z))
    for sy in (-1, 1):
        for sz in (-1, 1):
            s = s.cut(cyl_x(m["hole_d"] + 0.4, 10, AZ_VSF["x_face"] - 1, y + sy * m["holes"] / 2, z + sz * m["holes"] / 2))
    return s


def p_roue_el_vsf():
    e = V["el"]
    g = G.gear_x(e["z"], e["m"], X_SORTIE[1] - X_SORTIE[0], X_SORTIE[0], backlash=0.1)
    g = g.union(cyl_x(16, 4, X_SORTIE[1])).cut(cyl_x(8, 20, X_SORTIE[0] - 2))
    for k in range(5):
        a = math.radians(72 * k)
        g = g.cut(cyl_x(7, 12, X_SORTIE[0] - 2, 15 * math.cos(a), 15 * math.sin(a)))
    return g


def p_arbre_vis_el():
    y1 = EL_VSF["palier"][1] + 1
    return cyl_y(5, y1 - EL_VSF["y_joint"], -30, EL_VSF["y_joint"], V["Z_T"] - EL_ENTRAXE())


def EL_ENTRAXE():
    e = V["el"]
    return e["m"] * e["z"] / 2 + e["dp"] / 2


def p_palier_vis_el():
    p0, p1 = EL_VSF["palier"]
    zv = V["Z_T"] - EL_ENTRAXE()
    zb = V["Z_CHAPE"] + 8
    b = None
    for y0, y1 in ((p0, p1), (-p1, -p0)):
        pl = box_span(-37, -23, y0, y1, zb, V["Z_T"] - 26).cut(cyl_y(B685[0], y1 - y0 + 2, -30, y0 - 1, zv))
        b = pl if b is None else b.union(pl)
    b = b.union(box_span(-37, -23, -p1, p1, zb, zb + 5))
    return b.cut(cyl_z(3.4, 8, -30, 0, zb - 1))


def p_support_moteur_el_vsf():
    m = MOTEURS[V["moteur_el"]]
    zv = V["Z_T"] - EL_ENTRAXE()
    zb = V["Z_CHAPE"] + 8
    y0 = EL_VSF["y_face"] + 4
    s = box_span(-30 - 24, -30 + 24, EL_VSF["y_face"], y0, zb, zv + 24)
    s = s.union(box_span(-30 - 24, -30 + 24, EL_VSF["y_face"], y0 + 18, zb, zb + 5))
    s = s.cut(cyl_y(m["pilot"] + 0.5, 6, -30, EL_VSF["y_face"] - 1, zv))
    for sx in (-1, 1):
        for sz in (-1, 1):
            s = s.cut(cyl_y(m["hole_d"] + 0.4, 6, -30 + sx * m["holes"] / 2, EL_VSF["y_face"] - 1, zv + sz * m["holes"] / 2))
    return s


# ---------------------------------------------------------------------------
# VERSION ENGRENAGES DROITS
# ---------------------------------------------------------------------------
AZ_ENG_C = 0.8 * (18 + 92) / 2        # entraxe pignon / couronne d'azimut : 44 mm
EL_ENG_C = 0.8 * (15 + 120) / 2       # entraxe pignon / secteur d'élévation : 54 mm
X_FACE_EL_ENG = -10.0                 # face du moteur d'élévation


def p_couronne_az_eng():
    a = V["az"]
    g = G.gear_z(a["zr"], a["m"], 10, 67.0, backlash=0.1)
    g = g.union(ring_z(40, 36, 2, 65)).cut(cyl_z(36, 30, z=60))
    g = g.cut(ring_z(62, 44, 5, 72))                        # allègement
    for k in range(6):
        ang = math.radians(30 + 60 * k)
        g = g.cut(cyl_z(2.9, 20, 23.5 * math.cos(ang), 23.5 * math.sin(ang), 60))
    return g


def p_pignon_az_eng():
    a = V["az"]
    return G.gear_z(a["zp"], a["m"], 10, 67.0).cut(cyl_z(5, 20, z=60))


def p_roue_el_eng():
    e = V["el"]
    g = G.gear_x(e["zr"], e["m"], X_SORTIE[1] - X_SORTIE[0], X_SORTIE[0], backlash=0.1, tip_relief=0.1)
    g = g.union(cyl_x(16, 4, X_SORTIE[1])).cut(cyl_x(8, 20, X_SORTIE[0] - 2))
    g = g.cut(ring_x(84, 24, 4, X_SORTIE[0] + 4))
    # secteur denté : le pignon n'engrène que sur le quart avant-bas (él. -2° à 92°) ;
    # la partie haute est supprimée pour passer sous la plaque du chapeau
    return g.intersect(box_span(-60, 0, -12, 60, -60, U_TOP[0] - 6))


def ring_x(od, idia, w, x0):
    return cq.Workplane("YZ").circle(od / 2).circle(idia / 2).extrude(w).translate((x0, 0, 0))


def p_pignon_el_eng():
    e = V["el"]
    return G.gear_x(e["zp"], e["m"], X_SORTIE[1] - X_SORTIE[0], X_SORTIE[0]).cut(cyl_x(5, 20, X_SORTIE[0] - 2))


def p_support_moteur_el_eng():
    m = MOTEURS[V["moteur_el"]]
    zm = V["Z_T"] - EL_ENG_C
    zb = V["Z_CHAPE"] + 8
    x0 = X_FACE_EL_ENG - 4
    s = box_span(x0, X_FACE_EL_ENG, -21, 21, zb, zm + 24)              # y ±21 : laisse passer le moteur d'azimut
    s = s.union(box_span(X_SORTIE[1], X_FACE_EL_ENG, -21, 21, zb, zb + 5))
    s = s.cut(cyl_x(m["pilot"] + 0.5, 10, x0 - 1, 0, zm))
    for sy in (-1, 1):
        for sz in (-1, 1):
            s = s.cut(cyl_x(m["hole_d"] + 0.4, 10, x0 - 1, sy * m["holes"] / 2, zm + sz * m["holes"] / 2))
    return s


# ---------------------------------------------------------------------------
# REGISTRE ET ASSEMBLAGE
# ---------------------------------------------------------------------------
PARTS = {}
PANEL = ("Cadre_Panneau", "Lamine_PV", "Cellules_PV", "Boite_Jonction")
MASSES = {}           # masses forfaitaires (moteurs)


def reg(name, wp, mat, col, desc, masse=None):
    PARTS[name] = (wp, mat, col, desc)
    if masse is not None:
        MASSES[name] = masse


def build_parts():
    PARTS.clear()
    MASSES.clear()
    me, ma = MOTEURS[V["moteur_el"]], MOTEURS[V["moteur_az"]]
    reg("Haut_Colonne_Trepied", p_haut_colonne(), "Al 7075-T73", COLORS["ghost"], "Référence : haut de la colonne")
    reg("Fond_Socle", p_fond_socle(), "Al 6061-T6", COLORS["socle"], "Fond du socle, centrage dans la colonne")
    reg("Socle", p_socle(), "Al 6061-T6", COLORS["socle"], "Socle Ø62, roulements d'azimut")
    reg("Roulement_6806", roulement_z(42, 30, 7), "Acier 440C", COLORS["steel"], "Roulement 6806-ZZ")
    reg("Chape", p_chape(), "Al 6061-T6", COLORS["chape"], "Chape en U")
    reg("Bague_Arret_Moyeu", p_bague_arret(), "Acier inox 17-4PH", COLORS["steel"], "Bague d'arrêt du moyeu")
    reg("Roulement_608", roulement_x(22, 8, 7), "Acier 440C", COLORS["steel"], "Roulement 608-ZZ")
    reg("Chapeau_U", p_chapeau_u(), "Al 6061-T6", COLORS["u"], "Chapeau en U renversé porte-panneau")
    reg("Pivot_Entraine", p_pivot_entraine(), "Acier inox 17-4PH", COLORS["steel"], "Pivot Ø8 entraîné")
    reg("Pivot_Libre", p_pivot_libre(), "Acier inox 17-4PH", COLORS["steel"], "Pivot Ø8 libre")
    reg("Rail_Panneau", p_rail(), "Al 6061-T6", COLORS["alu"], "Rail 12 x 13 du panneau")
    reg("Moteur_Elevation", p_nema(V["moteur_el"]), "moteur", COLORS["motor"], me["nom"], me["masse"])
    reg("Moteur_Azimut", p_nema(V["moteur_az"]), "moteur", COLORS["motor"], ma["nom"], ma["masse"])
    if V is VERSIONS["VSF"]:
        reg("Roue_Azimut_Fixe", p_roue_az_vsf(), "Bronze CuSn12", COLORS["brass"], "Roue fixe m0,8 Z60")
        reg("Vis_Azimut", p_vis(V["az"]["m"], V["az"]["dp"], V["az"]["L"]), "Acier inox 17-4PH", COLORS["steel"],
            "Vis sans fin m0,8 Ø12")
        reg("Arbre_Vis_Azimut", p_arbre_vis_az(), "Acier inox 17-4PH", COLORS["steel"], "Arbre de vis Ø5")
        reg("Palier_Vis_Azimut", p_palier_vis_az(), "Al 6061-T6", COLORS["chape"], "Palier de la vis d'azimut")
        reg("Support_Moteur_Azimut", p_support_moteur_az_vsf(), "Al 6061-T6", COLORS["chape"], "Support du moteur d'azimut")
        reg("Roue_Elevation", p_roue_el_vsf(), "Bronze CuSn12", COLORS["brass"], "Roue m1 Z50")
        reg("Vis_Elevation", p_vis(V["el"]["m"], V["el"]["dp"], V["el"]["L"]), "Acier inox 17-4PH", COLORS["steel"],
            "Vis sans fin m1 Ø16")
        reg("Arbre_Vis_Elevation", p_arbre_vis_el(), "Acier inox 17-4PH", COLORS["steel"], "Arbre de vis Ø5")
        reg("Palier_Vis_Elevation", p_palier_vis_el(), "Al 6061-T6", COLORS["chape"], "Palier de la vis d'élévation")
        reg("Support_Moteur_Elevation", p_support_moteur_el_vsf(), "Al 6061-T6", COLORS["chape"], "Support du moteur d'élévation")
        reg("Roulement_685", roulement_x(B685[0], 5, B685[2]), "Acier 440C", COLORS["steel"], "Roulement 685-ZZ")
        reg("Accouplement", p_accouplement(), "Al 7075-T73", COLORS["coupler"], "Accouplement flexible 5/5")
    else:
        reg("Couronne_Azimut_Fixe", p_couronne_az_eng(), "Al 7075-T73", COLORS["orange"], f"Couronne fixe m{V['az']['m']:g} Z{V['az']['zr']}")
        reg("Pignon_Azimut", p_pignon_az_eng(), "Acier inox 17-4PH", COLORS["steel"], f"Pignon m{V['az']['m']:g} Z{V['az']['zp']}")
        reg("Roue_Elevation", p_roue_el_eng(), "Al 7075-T73", COLORS["orange"], f"Secteur denté m{V['el']['m']:g} Z{V['el']['zr']}")
        reg("Pignon_Elevation", p_pignon_el_eng(), "Acier inox 17-4PH", COLORS["steel"], f"Pignon m{V['el']['m']:g} Z{V['el']['zp']}")
        reg("Support_Moteur_Elevation", p_support_moteur_el_eng(), "Al 6061-T6", COLORS["chape"], "Support du moteur d'élévation")
    G.P["pan_back"] = D_PAN
    reg("Cadre_Panneau", G.p_cadre_pv(), "Al 6063-T5", G.COL["alu"], "Cadre du panneau 356 x 253 x 30")
    reg("Lamine_PV", G.p_lamine(), "Verre 3,2 mm + EVA + backsheet (eq)", G.COL["pv_bg"], "Verre + EVA")
    reg("Cellules_PV", G.p_cellules()[0], "Silicium polycristallin", G.COL["pv"], "72 cellules")
    reg("Boite_Jonction", G.p_boite_jonction(), "PPO (boîte de jonction)", G.COL["black"], "Boîte de jonction")


PHASE = {"el": 0.0, "az": 0.0}        # calages de denture (calculés par caler_dentures)


def add(assy, part, loc=None, inst=None):
    wp, _m, col, _d = PARTS[part]
    assy.add(wp, name=inst or part, loc=loc or Location(), color=col)


def build_basculant(with_panel=True):
    b = cq.Assembly(name="SA_Basculant")
    add(b, "Chapeau_U")
    add(b, "Pivot_Entraine")
    add(b, "Pivot_Libre")
    add(b, "Roue_Elevation")
    add(b, "Rail_Panneau", trans(RAIL_X, 0, 0), "Rail_Panneau_1")
    add(b, "Rail_Panneau", trans(-RAIL_X, 0, 0), "Rail_Panneau_2")
    if with_panel:
        for n in PANEL:
            add(b, n)
    return b


def build_chape(az, el, with_panel=True):
    c = cq.Assembly(name="SA_Chape")
    zt, zc = V["Z_T"], V["Z_CHAPE"]
    add(c, "Chape")
    add(c, "Bague_Arret_Moyeu")
    add(c, "Roulement_608", trans(ARM_X[1] - 7, 0, zt), "Roulement_608_1")
    add(c, "Roulement_608", trans(-ARM_X[1], 0, zt), "Roulement_608_2")
    if V is VERSIONS["VSF"]:
        # azimut : vis le long de X, moteur NEMA 11 en bout, côté -X
        a = AZ_VSF
        add(c, "Palier_Vis_Azimut")
        add(c, "Arbre_Vis_Azimut")
        for i, x0 in enumerate((a["palier"][0], -a["palier"][1]), 1):
            add(c, "Roulement_685", trans(x0, a["y"], a["z"]), f"Roulement_685_Az_{i}")
        add(c, "Vis_Azimut", trans(0, a["y"], a["z"]) * rot((0, 1, 0), 90) * rot((0, 0, 1), PHASE["az"] + V["az"]["z"] * az))
        add(c, "Accouplement", trans(a["x_joint"] - 12.5, a["y"], a["z"]) * rot((0, 1, 0), 90), "Accouplement_Az")
        add(c, "Support_Moteur_Azimut")
        add(c, "Moteur_Azimut", trans(a["x_face"], a["y"], a["z"]) * rot((0, 1, 0), 90))
        # élévation : vis le long de Y sous la roue, moteur NEMA 17 court à l'arrière
        zv = zt - EL_ENTRAXE()
        add(c, "Palier_Vis_Elevation")
        add(c, "Arbre_Vis_Elevation")
        for i, y0 in enumerate((EL_VSF["palier"][0], -EL_VSF["palier"][1]), 1):
            add(c, "Roulement_685", trans(-30, y0, zv) * rot((0, 0, 1), 90), f"Roulement_685_El_{i}")
        add(c, "Vis_Elevation", trans(-30, 0, zv) * rot((1, 0, 0), -90)
            * rot((0, 0, 1), PHASE["el"] - V["el"]["z"] * (el - EL_REF)))
        add(c, "Accouplement", trans(-30, EL_VSF["y_joint"] - 12.5, zv) * rot((1, 0, 0), -90), "Accouplement_El")
        add(c, "Support_Moteur_Elevation")
        add(c, "Moteur_Elevation", trans(-30, EL_VSF["y_face"], zv) * rot((1, 0, 0), -90))
    else:
        # azimut : moteur vertical sur la queue de la chape, arbre vers le bas, pignon sous la chape
        add(c, "Moteur_Azimut", trans(0, -AZ_ENG_C, zc + 8) * rot((1, 0, 0), 180))
        add(c, "Pignon_Azimut", trans(0, -AZ_ENG_C, 0) * rot((0, 0, 1), PHASE["az"] + V["az"]["zr"] / V["az"]["zp"] * az))
        # élévation : moteur couché sous l'axe, pignon sur la roue du pivot
        zm = zt - EL_ENG_C
        add(c, "Support_Moteur_Elevation")
        add(c, "Moteur_Elevation", trans(X_FACE_EL_ENG, 0, zm) * rot((0, 1, 0), -90))
        e = V["el"]
        add(c, "Pignon_Elevation", trans(0, 0, zm) * rot((1, 0, 0), PHASE["el"] - e["zr"] / e["zp"] * (el - 90.0)))
    c.add(build_basculant(with_panel), name="SA_Basculant", loc=trans(0, 0, zt) * rot((1, 0, 0), el - 90))
    return c


def build_head(az, el, name, with_panel=True):
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
    add(s, "Roue_Azimut_Fixe" if V is VERSIONS["VSF"] else "Couronne_Azimut_Fixe")
    root.add(s, name="SA_Socle", loc=Y)
    root.add(build_chape(az, el, with_panel), name="SA_Chape", loc=Y * rot((0, 0, 1), az))
    return root


def inst_part(inst):
    base = inst.split("/")[-1]
    if base in PARTS:
        return base
    for pat in (r"_\d+$", r"_(Az|El)(_\d+)?$"):
        b2 = re.sub(pat, "", base)
        if b2 in PARTS:
            return b2
    return None


def clean_names(path):
    txt = open(path, encoding="utf-8", errors="replace").read()

    def sub(m):
        k = inst_part(m.group(1))
        return f"PRODUCT('{k}','{k}'" if k else m.group(0)
    open(path, "w", encoding="utf-8").write(re.sub(r"PRODUCT\('([^']*)','\1'", sub, txt))


def mass_of(inst, shp):
    k = inst_part(inst)
    if k in MASSES:
        return k, MASSES[k]
    mat = PARTS[k][1]
    return k, shp.Volume() * (DENS.get(mat) or G.MAT[mat]) * 1e-9


def overlap(flat, a_end, b_end):
    a = [s for n, s in flat if n.endswith(a_end)][0]
    b = [s for n, s in flat if n.endswith(b_end)][0]
    return a.intersect(b).Volume()


def PAIRES():
    if V is VERSIONS["VSF"]:
        return {"el": ("/Vis_Elevation", "/Roue_Elevation"), "az": ("/Vis_Azimut", "/Roue_Azimut_Fixe")}
    return {"el": ("/Pignon_Elevation", "/Roue_Elevation"), "az": ("/Pignon_Azimut", "/Couronne_Azimut_Fixe")}


def caler_dentures():
    """Calage angulaire des vis / pignons pour que les dentures soient en prise sans chevauchement."""
    for key, (a, b) in PAIRES().items():
        z = V[key]["z"] if V[key]["type"] == "vis" else V[key]["zp"]
        step = 10.0 if V[key]["type"] == "vis" else 360.0 / z / 12
        span = 360.0 if V[key]["type"] == "vis" else 360.0 / z
        def essai(k):
            PHASE[key] = k
            return overlap(G.flatten(build_head(0.0, EL_REF, "c", False)), a, b)
        best = None
        k = 0.0
        while k < span:
            v = essai(k)
            if best is None or v < best[1]:
                best = (k, v)
            if v < 1e-6:
                break
            k += step
        for _ in range(2):                  # affinage autour du meilleur calage
            if best[1] < 1e-6:
                break
            step /= 4
            for k in (best[0] + i * step for i in range(-3, 4) if i):
                v = essai(k)
                if v < best[1]:
                    best = (k, v)
        PHASE[key] = best[0]
        print(f"  calage {key} : {best[0]:.1f}° (recouvrement {best[1]:.3f} mm3)")


# ---------------------------------------------------------------------------
# DIMENSIONNEMENT
# ---------------------------------------------------------------------------
def couples():
    flat = G.flatten(build_basculant(True))
    M, S = 0.0, Vector(0, 0, 0)
    for n, s in flat:
        _k, m = mass_of(n, s)
        M += m
        S = S + cq.Shape.centerOfMass(s) * m
    r = math.hypot(S.y, S.z) / M / 1000                     # bras de levier du CdG (m)
    besoin = {
        "el": {"Lune": M * G_LUNE * r + FROT_EL, "Terre, intérieur": M * G_TERRE * r + FROT_EL,
               "Terre, extérieur (vent 10 m/s)": M * G_TERRE * r + FROT_EL + VENT_EL},
        "az": {"Lune": FROT_AZ, "Terre, intérieur": FROT_AZ + 0.01,
               "Terre, extérieur (vent 10 m/s)": FROT_AZ + VENT_AZ},
    }
    dispo = {}
    for key, mot in (("el", V["moteur_el"]), ("az", V["moteur_az"])):
        d = V[key]
        t_run = MOTEURS[mot]["hold"] * K_RUN
        if d["type"] == "vis":
            lam = math.atan(d["m"] / d["dp"])
            eta = math.tan(lam) / math.tan(lam + math.atan(0.15))
            ratio = d["z"]
            irrev = math.degrees(lam) < math.degrees(math.atan(0.10))
        else:
            eta, ratio, irrev = 0.97, d["zr"] / d["zp"], False
        dispo[key] = dict(t=t_run * ratio * eta, ratio=ratio, eta=eta, irrev=irrev,
                          tenue=MOTEURS[mot]["hold"] * 0.5 * ratio * eta)
    return M, r, besoin, dispo


def preparer(vk):
    """Sélectionne la version, construit les pièces et cale les dentures."""
    global V
    V = VERSIONS[vk]
    build_parts()
    caler_dentures()
    return V


def main(which):
    for vk in which:
        print(f"\n=== {VERSIONS[vk]['nom']} ===")
        preparer(vk)
        out_parts = os.path.join(OUT_CAD, "pieces_" + V["nom"].replace("Tete_Rotative_", "tete_").lower())
        assy = build_head(0.0, EL_REF, V["nom"], True)
        path = os.path.join(OUT_CAD, f"{V['nom']}.step")
        assy.export(path)
        clean_names(path)
        print(f"  {path} ({os.path.getsize(path) / 1e6:.1f} Mo)")
        os.makedirs(out_parts, exist_ok=True)
        for f in os.listdir(out_parts):
            if f.endswith(".step"):
                os.remove(os.path.join(out_parts, f))
        for name, (wp, *_r) in PARTS.items():
            if name != "Haut_Colonne_Trepied":
                cq.exporters.export(wp, os.path.join(out_parts, f"{name}.step"))

        flat = G.flatten(assy)
        tot = sum(mass_of(n, s)[1] for n, s in flat if inst_part(n) not in PANEL + ("Haut_Colonne_Trepied",))
        print(f"  masse de la tête (hors panneau) : {tot:.2f} kg")
        M, r, besoin, dispo = couples()
        print(f"  partie basculante : {M:.2f} kg, CdG à {r * 1000:.1f} mm de l'axe")
        for key, mot in (("el", V["moteur_el"]), ("az", V["moteur_az"])):
            d = dispo[key]
            print(f"  {key} : {MOTEURS[mot]['nom']} ({MOTEURS[mot]['hold']} N·m, {MOTEURS[mot]['amp']} A), "
                  f"rapport {d['ratio']:.2f}, rendement {d['eta']:.2f} -> {d['t']:.2f} N·m"
                  f"{' (irréversible)' if d['irrev'] else ''}")
            for cas, b in besoin[key].items():
                print(f"      {cas:32s} besoin {b:.3f} N·m -> marge x{d['t'] / b:.1f}")
            if not d["irrev"]:
                b = besoin[key]["Terre, extérieur (vent 10 m/s)"]
                print(f"      maintien à 50 % du courant : {d['tenue']:.2f} N·m -> marge x{d['tenue'] / b:.1f}")

        hits = G.interference(flat)
        print(f"  interférences : {'aucune' if not hits else hits}")
        worst = (1e9,)
        for el in (-2.0, 0.0, 15.0, 45.0, 75.0, 92.0):
            fl = G.flatten(build_head(0.0, el, "chk", True))
            mov = [(n, s) for n, s in fl if "/SA_Basculant/" in n
                   and not inst_part(n).startswith(("Pivot", "Cellules"))]
            fix = [(n, s) for n, s in fl if "/SA_Basculant/" not in n
                   and inst_part(n) not in ("Vis_Elevation", "Pignon_Elevation")]     # en prise avec la roue
            dd = G.min_clearance(mov, fix, cutoff=30.0)
            if dd[0] < worst[0]:
                worst = dd + (el,)
        # loi de rotation des vis / pignons : la denture doit rester en prise sans chevauchement
        poses = {"el": ((0.0, -2.0), (0.0, 92.0)), "az": ((37.0, EL_REF),)}
        for key, (a, b) in PAIRES().items():
            for az, el in poses[key]:
                v = overlap(G.flatten(build_head(az, el, "c", False)), a, b)
                print(f"  denture {key} à az={az:g}°, él={el:g}° : recouvrement {v:.3f} mm3")
        print(f"  garde mini partie basculante (-2° à 92°) : {worst[0]:.1f} mm "
              f"({str(worst[1]).split('/')[-1]} / {str(worst[2]).split('/')[-1]}, él={worst[3]}°)")


if __name__ == "__main__":
    main([a for a in sys.argv[1:] if a in VERSIONS] or list(VERSIONS))
