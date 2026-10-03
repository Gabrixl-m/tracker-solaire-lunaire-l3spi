#!/usr/bin/env python3
"""
Tête rotative (pan-tilt) à deux moteurs pas à pas 28BYJ-48 (5 V, unipolaires),
posée sur la colonne Ø50 du trépied. Fichier à part du tracker complet.

Architecture :
  - AZIMUT (axe vertical) : 28BYJ-48 fixé DANS le socle, arbre vers le HAUT, arbre sur
    l'axe d'azimut (son corps est décalé de 8 mm). Deux roulements 6806 portent la chape ;
    l'arbre du moteur n'entraîne que la rotation, par un méplat (accouplement flottant).
  - ÉLÉVATION (axe horizontal), EN PRISE DIRECTE : une pièce en U renversé coiffe la chape
    en U et pivote sur deux axes Ø8 montés sur roulements 608 dans les bras de la chape.
    Le 28BYJ-48 est vissé à l'intérieur de la chape contre le bras gauche ; son arbre
    traverse le bras dans le pivot du U renversé, qu'il entraîne par un méplat.
  - Le 28BYJ-48 n'a que ~0,034 N·m : la partie basculante est ÉQUILIBRÉE par deux
    contrepoids au bas des flancs du U renversé (calculés par le script) ; le moteur ne
    vainc plus que les frottements et le défaut d'équilibrage.
  - Le panneau 356 x 253 x 30 est vissé sur deux rails fixés sur le dessus du U renversé.

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
from generate_tracker import box_span, cyl_x, cyl_z, ring_z, rot, trans

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CAD = os.path.join(HERE, "CAO")
OUT_PARTS = os.path.join(OUT_CAD, "pieces_tete_28BYJ48")

# ---------------------------------------------------------------------------
# PARAMÈTRES (mm)
# ---------------------------------------------------------------------------
Z_T = 130.0                 # axe d'élévation au-dessus du haut de la colonne
COL_OD, COL_ID = 50.0, 46.0  # colonne du trépied
SOCLE_OD, SOCLE_ID = 62.0, 56.0
Z_ROUL1, Z_ROUL2 = 58.0, 45.0      # roulements 6806 (Ø30/Ø42 x 7)
Z_FACE_AZ = 34.5                   # face (côté arbre) du moteur d'azimut
Z_CHAPE = 67.0                     # dessous de la semelle de la chape
ARM_X = (40.0, 48.0)               # bras de la chape (faces intérieure / extérieure)
ARM_R = 24.0                       # demi-largeur des bras et rayon de leur sommet
X_FACE_EL = -34.0                  # face (côté arbre) du moteur d'élévation
# U renversé (repère basculant : Z = normale au panneau)
U_X = (50.0, 56.0)                 # flancs (faces intérieure / extérieure)
U_TOP = (28.0, 33.0)               # plaque du dessus (rayon intérieur / extérieur)
U_Y = 22.0                         # demi-largeur des flancs
D_PAN = 43.0                       # axe d'élévation -> dos du cadre du panneau
EL_REF = 40.0                      # élévation des fichiers exportés
RAIL_X = 44.0                      # position des rails
# contrepoids (alliage de tungstène), centre à CW_Z sous l'axe, section 16 x 40
CW_Z, CW_T, CW_W = -90.0, 16.0, 40.0
CW = dict(h=30.0, y=0.0)           # hauteur et décalage : recalculés par equilibrer()
EQUILIBRAGE = 1.0                  # tolérance d'équilibrage visée (mm)

# 28BYJ-48 (cotes du constructeur)
BYJ = dict(d=28.0, h=19.0, offset=8.0, ear_pitch=35.0, ear_w=7.0, ear_t=0.8, ear_hole=4.2,
           boss_d=9.0, boss_h=1.5, shaft_d=5.0, shaft_l=10.0, flat=3.0,
           box_w=14.6, box_r=17.0, box_h=16.0,
           torque=0.034,            # couple d'entraînement ≥ 34 mN·m à 5 V
           friction=0.059,          # couple de frottement du réducteur (600 à 1200 gf·cm)
           ratio=64, steps=4096)

COLORS = {
    "socle":  cq.Color(0.45, 0.33, 0.25),
    "chape":  cq.Color(0.86, 0.72, 0.30),
    "u":      cq.Color(0.33, 0.45, 0.80),
    "steel":  cq.Color(0.72, 0.72, 0.74),
    "motor":  cq.Color(0.78, 0.79, 0.80),
    "bluebox": cq.Color(0.20, 0.42, 0.85),
    "cw":     cq.Color(0.25, 0.25, 0.27),
    "alu":    cq.Color(0.80, 0.81, 0.83),
    "ghost":  cq.Color(0.70, 0.70, 0.72),
}

DENS = {  # kg/m3
    "Al 6061-T6": 2700.0, "Acier inox 17-4PH": 7800.0, "Acier 440C": 7700.0,
    "Ti-6Al-4V": 4430.0, "Al 7075-T73": 2810.0, "Alliage de tungstène W-Ni-Fe": 17600.0,
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
# PIÈCES — CHAPE EN U (tourne en azimut)
# ---------------------------------------------------------------------------
def p_chape():
    xi, xo = ARM_X
    c = box_span(-xo, xo, -ARM_R, ARM_R, Z_CHAPE, Z_CHAPE + 8).edges("|Z").fillet(6)
    arm = (cq.Workplane("YZ").moveTo(-ARM_R, Z_CHAPE).lineTo(ARM_R, Z_CHAPE).lineTo(ARM_R, Z_T)
           .threePointArc((0, Z_T + ARM_R), (-ARM_R, Z_T)).close().extrude(xo - xi))
    c = c.union(arm.translate((xi, 0, 0))).union(arm.translate((-xo, 0, 0)))
    # moyeu d'azimut dans les roulements
    c = c.union(cyl_z(30, Z_CHAPE - 42, z=42)).union(cyl_z(34, 2, z=Z_CHAPE - 2))
    c = c.cut(cyl_z(20, Z_CHAPE + 8 - 46, z=47))            # passage des câbles
    # barrette d'accouplement à méplats (arbre du moteur d'azimut)
    win = cyl_z(20, 6.5, z=41)
    c = c.cut(win.intersect(box_span(-11, 11, -11, -4, 40, 48))).cut(win.intersect(box_span(-11, 11, 4, 11, 40, 48)))
    c = c.cut(cyl_z(BYJ["shaft_d"] + 0.1, 8, z=40).intersect(box_span(-1.55, 1.55, -3, 3, 40, 48)))
    # entretoises du moteur d'élévation sur la face intérieure du bras gauche (taraudage M3)
    zc = Z_T - BYJ["offset"]
    for y in (-BYJ["ear_pitch"] / 2, BYJ["ear_pitch"] / 2):
        c = c.union(cyl_x(6, xi + X_FACE_EL, -xi, y, zc)).cut(cyl_x(2.5, 12, -xi - 2, y, zc))
    # roulements 608 des pivots du U renversé
    c = c.cut(cyl_x(10, 2 * xo + 2, -xo - 1, 0, Z_T))
    c = c.cut(cyl_x(22, 7, xo - 7, 0, Z_T)).cut(cyl_x(22, 7, -xo, 0, Z_T))
    return c


def p_bague_arret():
    return ring_z(34, 30, 3, 42)


# ---------------------------------------------------------------------------
# PIÈCES — PARTIE BASCULANTE (repère : origine sur l'axe d'élévation, X = axe,
#           Z = normale au panneau, panneau côté +Z)
# ---------------------------------------------------------------------------
def p_u_renverse():
    """U renversé : plaque du dessus et deux flancs qui descendent hors des bras."""
    xi, xo = U_X
    zb = CW_Z - CW["h"] / 2 - 6                             # bas des flancs, sous le contrepoids
    u = box_span(-xo, xo, -ARM_R, ARM_R, U_TOP[0], U_TOP[1])
    for x0, x1 in ((xi, xo), (-xo, -xi)):
        fl = box_span(x0, x1, -U_Y, U_Y, zb, U_TOP[1]).edges("|X and <Z").fillet(8)
        u = u.union(fl)
    u = u.cut(cyl_x(8, 2 * xo + 2, -xo - 1))                 # pivots Ø8 (montage serré)
    for x in (-RAIL_X, RAIL_X):                             # fixation des rails
        for y in (-14, 14):
            u = u.cut(cyl_z(3.4, 10, x, y, U_TOP[0] - 1))
    for x0 in (xi - 0.5, -xo - 0.5):                        # fixation des contrepoids (M4)
        for y in (-12, 12):
            u = u.cut(cyl_x(4.2, xo - xi + 1, x0, CW["y"] + y, CW_Z))
    return u


def p_pivot_moteur():
    """Pivot gauche : axe Ø8 serré dans le U renversé, roulement 608 dans le bras ;
    l'arbre du moteur entre dans l'empreinte à méplats de son extrémité."""
    xe = -ARM_X[0] + 0.4                                     # extrémité côté moteur
    p = cyl_x(8, xe + U_X[1], -U_X[1]).union(cyl_x(12, 2, -U_X[1] - 2))
    sock = cyl_x(BYJ["shaft_d"] + 0.1, 7, xe - 7).intersect(box_span(xe - 8, xe + 1, -1.55, 1.55, -3, 3))
    # l'arbre tourne avec le U : empreinte calée sur les méplats dans la pose exportée
    return p.cut(sock.rotate((0, 0, 0), (1, 0, 0), 90.0 - EL_REF))


def p_pivot_libre():
    return cyl_x(8, U_X[1] - ARM_X[0] + 1, ARM_X[0] - 1).union(cyl_x(12, 2, U_X[1]))


def p_contrepoids():
    """Bloc centré en x ; placé contre la face extérieure de chaque flanc."""
    b = box_span(-CW_T / 2, CW_T / 2, CW["y"] - CW_W / 2, CW["y"] + CW_W / 2,
                 CW_Z - CW["h"] / 2, CW_Z + CW["h"] / 2).edges("|X").fillet(3)
    for y in (-12, 12):
        b = b.cut(cyl_x(4.5, CW_T + 2, -CW_T / 2 - 1, CW["y"] + y, CW_Z))
    return b


def p_rail_panneau():
    r = box_span(-6, 6, -G.P["pan_H"] / 2, G.P["pan_H"] / 2, U_TOP[1], D_PAN)
    for y in (-14, 14, -G.P["pan_H"] / 2 + 6, G.P["pan_H"] / 2 - 6):
        r = r.cut(cyl_z(3.4, 14, 0, y, U_TOP[1] - 1))
    return r


def p_haut_colonne():
    return ring_z(COL_OD, COL_ID, 80, -80)


# ---------------------------------------------------------------------------
# ASSEMBLAGE
# ---------------------------------------------------------------------------
PARTS = {}
PANEL_PARTS = ("Cadre_Panneau", "Lamine_PV", "Cellules_PV", "Boite_Jonction")
TILT_PARTS = ("U_Renverse", "Pivot_Moteur", "Pivot_Libre", "Contrepoids", "Rail_Panneau") + PANEL_PARTS


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
    reg("U_Renverse", p_u_renverse(), "Al 6061-T6", COLORS["u"], "U renversé porte-panneau, entraîné en direct")
    reg("Pivot_Moteur", p_pivot_moteur(), "Acier inox 17-4PH", COLORS["steel"], "Pivot Ø8 côté moteur, empreinte à méplats")
    reg("Pivot_Libre", p_pivot_libre(), "Acier inox 17-4PH", COLORS["steel"], "Pivot Ø8 côté libre")
    reg("Contrepoids", p_contrepoids(), "Alliage de tungstène W-Ni-Fe", COLORS["cw"], "Contrepoids d'équilibrage")
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


def build_basculant(with_panel, with_cw=True):
    b = cq.Assembly(name="SA_Basculant")
    add(b, "U_Renverse")
    add(b, "Pivot_Moteur")
    add(b, "Pivot_Libre")
    if with_cw:
        xc = U_X[1] + CW_T / 2
        add(b, "Contrepoids", trans(xc, 0, 0), "Contrepoids_1")
        add(b, "Contrepoids", trans(-xc, 0, 0), "Contrepoids_2")
    add(b, "Rail_Panneau", trans(RAIL_X, 0, 0), "Rail_Panneau_1")
    add(b, "Rail_Panneau", trans(-RAIL_X, 0, 0), "Rail_Panneau_2")
    if with_panel:
        for n in PANEL_PARTS:
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
    # moteur d'élévation contre le bras gauche : arbre selon -X sur l'axe, corps sous l'axe
    add_motor(c, "Moteur_Elevation", trans(X_FACE_EL, 0, Z_T) * rot((1, 0, 0), 90) * rot((0, 1, 0), -90))
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


def tilt_mass_props(with_cw=True):
    """Masse, moment statique (repère basculant) et inertie autour de l'axe d'élévation."""
    flat = G.flatten(build_basculant(True, with_cw))
    M, S, J = 0.0, Vector(0, 0, 0), 0.0
    for n, s in flat:
        _k, m = mass_of(n, s)
        c = cq.Shape.centerOfMass(s)
        M += m
        S = S + c * m
        J += m * (c.y ** 2 + c.z ** 2)                      # inertie ponctuelle (approchée)
    return M, S, J


def equilibrer():
    """Dimensionne les contrepoids pour ramener le CdG de la partie basculante sur l'axe."""
    rho = DENS["Alliage de tungstène W-Ni-Fe"] * 1e-9
    for _ in range(4):                                      # le bas des flancs dépend de la hauteur
        build_parts(True)
        _M, S, _J = tilt_mass_props(with_cw=False)
        m_cw = -S.z / CW_Z                                  # masse totale des deux blocs
        CW["y"] = -S.y / m_cw
        CW["h"] = m_cw / 2 / (rho * CW_T * CW_W)
    return m_cw


# ---------------------------------------------------------------------------
# PRINCIPAL
# ---------------------------------------------------------------------------
POSES = {
    "Tete_Rotative_28BYJ48": (0.0, EL_REF, False),
    "Tete_Rotative_28BYJ48_avec_panneau": (0.0, EL_REF, True),
}


def main():
    m_cw = equilibrer()
    print(f"Contrepoids : 2 x {m_cw / 2 * 1000:.0f} g (tungstène, {CW_T:.0f} x {CW_W:.0f} x {CW['h']:.1f} mm), "
          f"centre à {-CW_Z:.0f} mm sous l'axe, décalé de {CW['y']:.1f} mm")

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
        if name != "Haut_Colonne_Trepied":
            cq.exporters.export(wp, os.path.join(OUT_PARTS, f"{name}.step"))

    # masses
    flat = G.flatten(results["Tete_Rotative_28BYJ48_avec_panneau"])
    tot = {"tete": 0.0, "panneau": 0.0}
    for n, s in flat:
        k, m = mass_of(n, s)
        if k != "Haut_Colonne_Trepied":
            tot["panneau" if k in PANEL_PARTS else "tete"] += m
    print(f"Masse de la tête : {tot['tete']:.2f} kg (dont contrepoids {m_cw:.2f} kg) ; panneau : {tot['panneau']:.2f} kg")

    # couple sur l'élévation, en prise directe
    M, S, J = tilt_mass_props()
    r0 = math.hypot(S.y, S.z) / M
    res = EQUILIBRAGE / 1000
    fr = 0.002                                              # 2 roulements 608-ZZ (ordre de grandeur)
    for lieu, g in (("Lune", 1.62), ("Terre", 9.81)):
        need = M * g * res + fr
        print(f"Élévation, {lieu} : défaut d'équilibrage {EQUILIBRAGE:.0f} mm -> {M * g * res:.3f} N·m "
              f"+ frottements {fr:.3f} = {need:.3f} N·m ; moteur {BYJ['torque']:.3f} N·m -> marge x{BYJ['torque'] / need:.1f}")
    print(f"Partie basculante : {M:.2f} kg, CdG résiduel à {r0:.2f} mm de l'axe, inertie {J * 1e-6:.4f} kg·m2")
    alpha = (BYJ["torque"] / 2) / (J * 1e-6)
    print(f"Accélération maxi conseillée (moitié du couple) : {math.degrees(alpha):.0f} °/s2")
    print(f"Maintien moteur coupé : frottement du réducteur >= {BYJ['friction']:.3f} N·m")
    print(f"Résolution : {360 / BYJ['steps']:.3f}° par demi-pas sur les deux axes")

    print("\nInterférences statiques :")
    for fname, assy in results.items():
        build_parts(POSES[fname][2])
        hits = G.interference(G.flatten(assy))
        print(f"  {fname}: {'aucune' if not hits else hits}")

    build_parts(True)
    worst = (1e9,)
    for el in (-2.0, 0.0, 15.0, 45.0, 75.0, 92.0):
        flat = G.flatten(build_head(0.0, el, "chk", True))
        mov = [(n, s) for n, s in flat if "/SA_Basculant/" in n
               and not inst_part(n).startswith(("Pivot", "Cellules"))]
        fix = [(n, s) for n, s in flat if "/SA_Basculant/" not in n]
        d = G.min_clearance(mov, fix, cutoff=30.0)
        if d[0] < worst[0]:
            worst = d + (el,)
    print(f"\nGarde mini partie basculante (élévation -2° à 92°) : {worst[0]:.1f} mm "
          f"({str(worst[1]).split('/')[-1]} / {str(worst[2]).split('/')[-1]}, él={worst[3]}°)")


if __name__ == "__main__":
    main()
