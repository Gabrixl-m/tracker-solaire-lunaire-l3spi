#!/usr/bin/env python3
"""
Tracker solaire lunaire deux axes (azimut + élévation) sur trépied déployable.

Génère, à l'échelle 1:1 (unités : mm), des assemblages STEP AP214 que
SolidWorks ouvre directement comme assemblage (pièces nommées + couleurs),
ainsi que chaque pièce seule, un bilan de masse et des contrôles de
collision sur toute la plage de mouvement.

Repère de construction : Z vertical, origine au sol sur l'axe azimut.
Repère exporté : Y vertical (convention SolidWorks : plan de dessus = sol).

Usage :  python generate_tracker.py              export + bilan + interférences
         python generate_tracker.py --no-check   export + bilan seulement
         python generate_tracker.py --balayage   + garde sur toute la plage az/él
"""

import csv
import math
import os
import sys

import cadquery as cq
from cadquery import Location, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CAD = os.path.join(HERE, "CAO")
OUT_PARTS = os.path.join(OUT_CAD, "pieces")
OUT_DOC = os.path.join(HERE, "docs")

# ---------------------------------------------------------------------------
# PARAMÈTRES DE CONCEPTION (mm, degrés)
# ---------------------------------------------------------------------------
P = dict(
    # Panneau photovoltaïque fourni : 356 x 253 x 30 mm (cadre alu), axe d'élévation // 356
    pan_L=356.0,           # longueur, parallèle à l'axe d'élévation
    pan_H=253.0,           # largeur, dans le plan de rotation en élévation
    pan_T=30.0,            # épaisseur (cadre)
    pan_back=60.0,         # distance axe d'élévation -> dos du cadre
    cell_nx=9, cell_ny=8,
    # Axes
    z_el=1000.0,           # hauteur de l'axe d'élévation au-dessus du sol
    el_min=-2.0, el_max=92.0,   # butées mécaniques d'élévation
    phi_motor_az=150.0,    # position du moteur d'azimut sous l'embase (entre deux jambes)
    # Trépied
    r_hinge=110.0, z_hinge=780.0,  # articulation haute des jambes
    r_foot=800.0, z_ball=65.0,     # centre de la rotule de pied
    leg_phis=(90.0, 210.0, 330.0), # orientation des jambes (repère Z-up)
    z_lower_collar=400.0,
    s_clamp=480.0,         # position de la bride d'entretoise le long de la jambe
    # Unité de contrôle au sol et faisceau
    phi_box=30.0, r_box=1400.0,
)

# Géométrie dérivée du trépied
_dr = P["r_foot"] - P["r_hinge"]
_dz = P["z_hinge"] - P["z_ball"]
LEG_L = math.hypot(_dr, _dz)                    # longueur articulation -> rotule
LEG_BETA = math.degrees(math.atan2(_dr, _dz))   # écartement / verticale


# ---------------------------------------------------------------------------
# MATÉRIAUX
# densité en kg/m3. "eq" = densité équivalente d'un volume de représentation
# (nid d'abeille, cellules, actionneurs complets, électronique...).
# ---------------------------------------------------------------------------
MAT = {
    "Ti-6Al-4V":           4430.0,
    "Al 7075-T73":         2810.0,
    "Al 6061-T6":          2700.0,
    "Al 6063-T5":          2700.0,
    "Acier inox 17-4PH":   7800.0,
    "Acier 440C":          7700.0,
    "Verre 3,2 mm + EVA + backsheet (eq)": 2500.0,
    "Silicium polycristallin": 2330.0,
    "PPO (boîte de jonction)": 1100.0,
    "PTFE/cuivre (eq)":    2200.0,
}
# masses forfaitaires (kg) imposées pour les ensembles non détaillés
MASS_TARGET = {
    "Moteur_PasAPas_Azimut": 0.36,       # NEMA 17, 48 mm
    "Moteur_PasAPas_Elevation": 0.36,
    "Unite_Controle_Corps": 17.0,        # batteries Li-ion, MPPT, OBC, drivers, chauffage
}

COL = {
    "ti":     cq.Color(0.55, 0.56, 0.58),
    "alu":    cq.Color(0.80, 0.81, 0.83),
    "alu_d":  cq.Color(0.66, 0.67, 0.70),
    "white":  cq.Color(0.93, 0.93, 0.92),
    "cell":   cq.Color(0.06, 0.10, 0.32),
    "back":   cq.Color(0.30, 0.30, 0.32),
    "cfrp":   cq.Color(0.15, 0.15, 0.16),
    "gold":   cq.Color(0.83, 0.66, 0.24),
    "black":  cq.Color(0.08, 0.08, 0.08),
    "orange": cq.Color(0.90, 0.45, 0.10),
    "glass":  cq.Color(0.20, 0.35, 0.55),
    "blue":   cq.Color(0.22, 0.52, 0.80),
    "grey":   cq.Color(0.60, 0.61, 0.63),
    "steel":  cq.Color(0.72, 0.72, 0.74),
    "pv":     cq.Color(0.10, 0.20, 0.50),
    "pv_bg":  cq.Color(0.88, 0.89, 0.91),
    "nema":   cq.Color(0.12, 0.12, 0.13),
}


# ---------------------------------------------------------------------------
# PRIMITIVES
# ---------------------------------------------------------------------------
def cyl_z(d, h, x=0.0, y=0.0, z=0.0):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z))


def tube_z(od, wall, h, z=0.0):
    return (cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall)
            .extrude(h).translate((0, 0, z)))


def ring_z(od, idia, h, z=0.0):
    return tube_z(od, (od - idia) / 2, h, z)


def cyl_x(d, L, x=0.0, y=0.0, z=0.0):
    return cq.Workplane("YZ").circle(d / 2).extrude(L).translate((x, y, z))


def box(a, b, c, x=0.0, y=0.0, z=0.0):
    return cq.Workplane("XY").box(a, b, c).translate((x, y, z))


def box_span(x0, x1, y0, y1, z0, z1):
    return box(x1 - x0, y1 - y0, z1 - z0,
               (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def cyl_dir(d, h, base, direction):
    """Cylindre plein de diamètre d, longueur h, depuis 'base' selon 'direction'."""
    s = cq.Solid.makeCylinder(d / 2, h, Vector(*base), Vector(*direction))
    return cq.Workplane().add(s)


def rot(axis, ang):
    return Location(Vector(0, 0, 0), Vector(*axis), ang)


def trans(x, y, z):
    return Location(Vector(x, y, z))


# ---------------------------------------------------------------------------
# PIÈCES — TRÉPIED (fixe)
# ---------------------------------------------------------------------------
def p_colonne():
    z0, z1 = 330.0, 815.0
    t = tube_z(80, 2.5, z1 - z0, z0)
    # bouchon inférieur conique creux (évite l'accumulation de régolithe)
    cone = cq.Workplane().add(cq.Solid.makeCone(40, 12, 40, Vector(0, 0, z0), Vector(0, 0, -1)))
    cone = cone.cut(cq.Workplane().add(cq.Solid.makeCone(37.5, 10, 37.5, Vector(0, 0, z0), Vector(0, 0, -1))))
    return t.union(cone)


def _clevis_pair(r_in, r_pin, z_pin, gap, thick, height, r_round, hole):
    """Chape à deux flasques, axe tangent (X), direction radiale +Y."""
    out = None
    for sgn in (1, -1):
        x0 = sgn * gap / 2
        x1 = sgn * (gap / 2 + thick)
        xa, xb = min(x0, x1), max(x0, x1)
        plate = box_span(xa, xb, r_in, r_pin, z_pin - height / 2, z_pin + height / 2)
        plate = plate.union(cyl_x(2 * r_round, xb - xa, xa, r_pin, z_pin))
        plate = plate.cut(cyl_x(hole, xb - xa + 2, xa - 1, r_pin, z_pin))
        out = plate if out is None else out.union(plate)
    return out


def p_collier_sup():
    zc = P["z_hinge"]
    body = ring_z(100, 80.2, 60, zc - 30)
    for phi in P["leg_phis"]:
        cl = _clevis_pair(46, P["r_hinge"], zc, 42, 7, 36, 18, 10.2)
        body = body.union(cl.rotate((0, 0, 0), (0, 0, 1), phi - 90))
    # vis de serrage sur la colonne
    for phi in P["leg_phis"]:
        a = math.radians(phi + 60)
        body = body.union(cyl_dir(12, 10, (48 * math.cos(a), 48 * math.sin(a), zc - 18),
                                  (math.cos(a), math.sin(a), 0)))
    return body


def p_collier_inf():
    zc = P["z_lower_collar"]
    body = ring_z(96, 80.2, 44, zc - 22)
    for phi in P["leg_phis"]:
        cl = _clevis_pair(46, 85, zc, 21, 5, 26, 13, 10.2)
        body = body.union(cl.rotate((0, 0, 0), (0, 0, 1), phi - 90))
    return body


# --- repère jambe : origine = axe d'articulation, axe X = axe de l'articulation,
#     jambe selon -Z, extérieur = +Y (avant rotation d'écartement)
def p_ferrure_jambe():
    body = cyl_x(36, 40, -20)
    body = body.union(box_span(-20, 20, -18, 18, -45, 0))
    body = body.union(cyl_z(48, 50, z=-80))
    body = body.cut(cyl_z(40.2, 36, z=-81))            # alésage du tube
    body = body.cut(cyl_x(10.2, 44, -22))               # passage d'axe
    return body


def p_axe(d=10.0, span=58.0, head=16.0):
    shaft = cyl_x(d, span + 4, -span / 2)
    return shaft.union(cyl_x(head, 6, -span / 2 - 6))


def p_tube_sup():
    return tube_z(40, 1.5, 700 - 50, -700)


def p_bague_blocage():
    b = ring_z(50, 40.2, 30, -700).union(ring_z(50, 34.2, 20, -720))
    lever = box_span(-6, 6, 25, 55, -712, -688)
    lever = lever.union(cyl_x(16, 20, -10, 55, -700))
    return b.union(lever)


def p_tube_inf():
    return tube_z(34, 1.5, (LEG_L - 100) - 620, -(LEG_L - 100))


def p_embout_rotule():
    L = LEG_L
    plug = cyl_z(34, 40, z=-(L - 60))            # s de L-100 à L-60 (bout du tube inférieur)
    neck = cyl_z(22, 61, z=-L)                   # col Ø22 jusqu'au centre de la rotule
    ball = cq.Workplane().sphere(18).translate((0, 0, -L))
    return plug.union(neck).union(ball)


def p_bride_entretoise():
    s = P["s_clamp"]
    ring = ring_z(52, 40.2, 36, -s - 18)
    lug = None                                   # chape tournée vers la colonne (-Y)
    for sgn in (1, -1):
        xa, xb = sorted((sgn * 10.5, sgn * 16.5))
        plate = box_span(xa, xb, -45, -20, -s - 11, -s + 11)
        plate = plate.union(cyl_x(24, xb - xa, xa, -45, -s))
        plate = plate.cut(cyl_x(10.2, xb - xa + 2, xa - 1, -45, -s))
        lug = plate if lug is None else lug.union(plate)
    return ring.union(lug)


def leg_loc(phi):
    a = math.radians(phi)
    return (trans(P["r_hinge"] * math.cos(a), P["r_hinge"] * math.sin(a), P["z_hinge"])
            * rot((0, 0, 1), phi - 90) * rot((1, 0, 0), LEG_BETA))


def leg_point(phi, local):
    """Coordonnées monde (Z-up) d'un point exprimé dans le repère jambe."""
    v = cq.Vertex.makeVertex(*local).moved(leg_loc(phi))
    return v.toTuple()


def p_entretoise(length):
    eye0 = cyl_x(26, 20, -10).cut(cyl_x(10.2, 22, -11))
    eye1 = cyl_x(26, 20, -10, 0, length).cut(cyl_x(10.2, 22, -11, 0, length))
    t = tube_z(20, 1.5, length - 2 * 11, 11)
    return eye0.union(eye1).union(t)


def p_patin():
    """Repère patin : origine au sol sous la rotule, +X = direction radiale."""
    zb = P["z_ball"]
    b = math.radians(LEG_BETA)
    u = (-math.sin(b), 0.0, math.cos(b))                  # vers l'articulation
    base = cyl_z(220, 5)
    # crampons sous la semelle (accroche dans le régolithe)
    for k in range(6):
        a = math.radians(30 + 60 * k)
        base = base.union(cq.Workplane().add(cq.Solid.makeCone(
            7, 1, 14, Vector(80 * math.cos(a), 80 * math.sin(a), 0), Vector(0, 0, -1))))
    ped = cq.Workplane().add(cq.Solid.makeCone(56, 30, zb - 5 - 10, Vector(0, 0, 5), Vector(0, 0, 1)))
    ped = ped.cut(cq.Workplane().add(cq.Solid.makeCone(52, 26, zb - 5 - 14, Vector(0, 0, 5), Vector(0, 0, 1))))
    # douille alignée sur l'axe nominal de la jambe (débattement de rotule ±20°)
    sock = cyl_dir(62, 48, (-40 * u[0], 0, zb - 40 * u[2]), u)
    body = base.union(ped).union(sock)
    # nervures radiales
    for k in range(6):
        a = 60 * k
        rib = (cq.Workplane("XZ").polyline([(50, 5), (104, 5), (104, 10), (40, zb - 22), (40, zb - 30)])
               .close().extrude(2.5, both=True))
        body = body.union(rib.rotate((0, 0, 0), (0, 0, 1), a))
    # patte de piquet d'ancrage (côté extérieur)
    lug = box_span(95, 140, -20, 20, 0, 14).union(cyl_z(40, 14, 140, 0, 0))
    body = body.cut(cyl_z(12, 7, 0, 0, -1))      # évent du piédestal creux (pas de volume clos sous vide)
    body = body.union(lug)
    body = body.cut(cyl_z(14.6, 40, 140, 0, -10))
    # logement sphérique de la rotule (jeu 0,2 mm)
    body = body.cut(cq.Workplane().sphere(18.2).translate((0, 0, zb)))
    return body


def p_piquet():
    """Piquet d'ancrage Ti Ø14, 450 mm enfoncés dans le régolithe."""
    shaft = cyl_z(14, 450 + 14, z=-450)
    tip = cq.Workplane().add(cq.Solid.makeCone(7, 0.5, 25, Vector(0, 0, -450), Vector(0, 0, -1)))
    head = cyl_z(30, 10, z=14)
    eye = (cq.Workplane("XZ").circle(14).circle(8).extrude(3, both=True)
           .translate((0, 0, 24 + 12)))
    return shaft.union(tip).union(head).union(eye)


# ---------------------------------------------------------------------------
# ENGRENAGES (profil en développante de cercle, angle de pression 20°)
# ---------------------------------------------------------------------------
Z_COURONNE, Z_PIGNON_AZ, M_AZ = 120, 18, 1.5      # azimut : rapport 120/18 = 6,67
Z_ROUE_EL, Z_PIGNON_EL, M_EL = 72, 24, 1.0        # élévation : rapport 72/24 = 3
ENTRAXE_AZ = M_AZ * (Z_COURONNE + Z_PIGNON_AZ) / 2    # 103,5 mm
ENTRAXE_EL = M_EL * (Z_ROUE_EL + Z_PIGNON_EL) / 2     # 48 mm


def gear_teeth(z, m, backlash=0.06, tip_relief=0.0, n=7):
    """Flancs d'une roue dentée droite : liste par dent de [(rayon, angle)] du pied
    vers la tête (flanc de gauche ; le flanc de droite est symétrique).
    Dent n°0 centrée sur l'axe +u ; backlash = amincissement de chaque dent (en modules)."""
    alpha = math.radians(20.0)
    rp = m * z / 2
    rb = rp * math.cos(alpha)
    ra = rp + m * (1 - tip_relief)
    rf = rp - 1.25 * m

    def inv(a):
        return math.tan(a) - a
    psi = math.pi / (2 * z) - backlash * m / (2 * rp)
    r0 = max(rb, rf)

    def half(r):
        return psi + inv(alpha) - inv(math.acos(min(1.0, rb / r)))
    involute = [(r, half(r)) for r in (r0 + (ra - r0) * i / (n - 1) for i in range(n))]
    radial = (rf, half(rb)) if rf < rb else None
    return involute, radial


def gear_solid(z, m, w, to3d, ext, **kw):
    """Roue dentée extrudée ; flancs en développante (B-spline), fond et tête rectilignes."""
    involute, radial = gear_teeth(z, m, **kw)

    def P3(r, t):
        return to3d(r * math.cos(t), r * math.sin(t))
    edges = []
    for k in range(z):
        c = 2 * math.pi * k / z
        left = [P3(r, c - a) for r, a in involute]
        right = [P3(r, c + a) for r, a in reversed(involute)]
        if radial:
            edges.append(cq.Edge.makeLine(P3(radial[0], c - radial[1]), left[0]))
        edges.append(cq.Edge.makeSpline(left))
        edges.append(cq.Edge.makeLine(left[-1], right[0]))
        edges.append(cq.Edge.makeSpline(right))
        end = right[-1]
        if radial:
            end = P3(radial[0], c + radial[1])
            edges.append(cq.Edge.makeLine(right[-1], end))
        cn = 2 * math.pi * (k + 1) / z
        nxt = (P3(radial[0], cn - radial[1]) if radial else P3(involute[0][0], cn - involute[0][1]))
        edges.append(cq.Edge.makeLine(end, nxt))
    face = cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))
    return cq.Workplane().add(cq.Solid.extrudeLinear(face, ext))


def gear_z(z, m, w, z0=0.0, **kw):
    """Roue d'axe Z, de z0 à z0+w."""
    return gear_solid(z, m, w, lambda u, v: Vector(u, v, z0), Vector(0, 0, w), **kw)


def gear_x(z, m, w, x0=0.0, **kw):
    """Roue d'axe X, de x0 à x0+w ; dent n°0 selon +Y."""
    return gear_solid(z, m, w, lambda u, v: Vector(x0, u, v), Vector(w, 0, 0), **kw)


# ---------------------------------------------------------------------------
# PIÈCES — TÊTE MÉCANIQUE CENTRALE (pan-tilt à engrenages)
#   Z_EMB : dessus de la colonne du trépied. Couronne d'azimut sur roulement,
#   étrier en U, moteur pas à pas d'azimut (axe vertical = Y SolidWorks)
#   sous l'embase, moteur pas à pas d'élévation (axe horizontal = X) dans l'étrier.
# ---------------------------------------------------------------------------
Z_EMB = 815.0              # dessous de l'embase = dessus de la colonne
Z_ROUL = Z_EMB + 8         # roulement d'azimut
Z_COUR = Z_ROUL + 12       # couronne d'azimut (épaisseur 15)
Z_ETR = Z_COUR + 15        # semelle de l'étrier


def p_nema17(shaft):
    """Moteur pas à pas NEMA 17 (42,3 x 42,3 x 48 mm). Face avant en z = 0, arbre selon +Z."""
    s, L = 42.3, 48.0
    body = box(s, s, L, 0, 0, -L / 2).edges("|Z").chamfer(4)
    body = body.union(cyl_z(22, 2))                                  # centrage Ø22
    body = body.union(cyl_z(5, shaft, z=2))                          # arbre Ø5
    body = body.union(box_span(-8, 8, s / 2, s / 2 + 6, -L + 4, -L + 16))   # connecteur
    return body


def p_embase():
    a = math.radians(P["phi_motor_az"])
    mx, my = ENTRAXE_AZ * math.cos(a), ENTRAXE_AZ * math.sin(a)
    t = 8.0
    plate = cyl_z(200, t, z=Z_EMB)
    plate = plate.union(cyl_z(64, t, mx, my, Z_EMB))
    plate = plate.union(box_span(0, ENTRAXE_AZ, -30, 30, Z_EMB, Z_EMB + t)
                        .rotate((0, 0, 0), (0, 0, 1), P["phi_motor_az"]))
    plate = plate.union(ring_z(74.5, 50, 10, Z_EMB - 10))            # centrage dans la colonne
    ab = math.radians(P["phi_box"])                                  # embase connecteur (vers le bas)
    plate = plate.union(cyl_z(30, 25, 82 * math.cos(ab), 82 * math.sin(ab), Z_EMB - 25))
    plate = plate.cut(cyl_z(40, 40, z=Z_EMB - 20))                   # passage central des câbles
    plate = plate.cut(cyl_z(23, 20, mx, my, Z_EMB - 5))              # centrage moteur
    for k in range(4):
        b = a + math.radians(45 + 90 * k)
        plate = plate.cut(cyl_z(3.4, 20, mx + 21.9 * math.cos(b), my + 21.9 * math.sin(b), Z_EMB - 5))
    return plate


def p_roulement_azimut():
    r = ring_z(90, 50, 12, Z_ROUL)
    return r.cut(ring_z(72, 68, 2, Z_ROUL + 11))                     # joint visible bague int./ext.


def p_couronne():
    g = gear_z(Z_COURONNE, M_AZ, 15, Z_COUR, tip_relief=0.1)
    g = g.cut(cyl_z(50, 20, z=Z_COUR - 2))                           # passage des câbles
    g = g.cut(ring_z(152, 76, 7, Z_COUR + 8))                        # allègement (voile de 8 mm)
    for k in range(6):
        b = math.radians(30 + 60 * k)
        g = g.cut(cyl_z(5.5, 20, 31 * math.cos(b), 31 * math.sin(b), Z_COUR - 2))
    return g


def p_pignon_azimut():
    return gear_z(Z_PIGNON_AZ, M_AZ, 15).cut(cyl_z(5, 20, z=-2))


def p_etrier():
    zt = P["z_el"]
    e = box_span(-58, 58, -35, 35, Z_ETR, Z_ETR + 8).cut(cyl_z(40, 20, z=Z_ETR - 5))
    prof = [(-35, Z_ETR), (35, Z_ETR), (35, zt + 12), (22, zt + 35), (-22, zt + 35), (-35, zt + 12)]
    for x0 in (50.0, -58.0):
        e = e.union(cq.Workplane("YZ").polyline(prof).close().extrude(8).translate((x0, 0, 0)))
    e = e.cut(cyl_x(12.2, 140, -70, 0, zt))                          # paliers de l'axe d'élévation
    zm = zt - ENTRAXE_EL
    e = e.cut(cyl_x(22.5, 12, 48, 0, zm))                            # centrage moteur d'élévation
    for dy in (-15.5, 15.5):
        for dz in (-15.5, 15.5):
            e = e.cut(cyl_x(3.4, 12, 48, dy, zm + dz))
    for x0 in (-58.0, 50.0):                                         # fixation sur la couronne
        for y0 in (-22.0, 22.0):
            e = e.union(cyl_z(8, 3, (x0 + 4) * 0.8, y0, Z_ETR + 8))
    return e


def p_palier():
    zt = P["z_el"]
    c = cyl_x(40, 5, -63, 0, zt).cut(cyl_x(12.2, 8, -65, 0, zt))
    for k in range(6):
        b = math.radians(60 * k)
        c = c.union(cyl_x(5, 1.5, -64.5, 14 * math.cos(b), zt + 14 * math.sin(b)))
    return c


def p_pignon_elevation():
    g = gear_x(Z_PIGNON_EL, M_EL, 8).cut(cyl_x(5, 12, -2))
    for k in range(3):
        b = math.radians(120 * k)
        g = g.cut(cyl_x(3, 12, -2, 7 * math.cos(b), 7 * math.sin(b)))
    return g


# ---------------------------------------------------------------------------
# PIÈCES — PANNEAU ET SUPPORT (repère : origine sur l'axe d'élévation,
#   X = axe d'élévation, Z = normale au panneau, cellules côté +Z)
# ---------------------------------------------------------------------------
def p_arbre_elevation():
    return cyl_x(12, 138, -66)


def p_roue_elevation():
    g = gear_x(Z_ROUE_EL, M_EL, 8, 60).cut(cyl_x(12, 12, 58))
    for k in range(6):
        b = math.radians(30 + 60 * k)
        g = g.cut(cyl_x(9, 12, 58, 22 * math.cos(b), 22 * math.sin(b)))
    return g


def p_support_panneau():
    d = P["pan_back"]
    s = cyl_x(30, 90, -45)
    web = [(-12, 0), (12, 0), (30, d - 10), (-30, d - 10)]
    for x0 in (35.0, -41.0):
        s = s.union(cq.Workplane("YZ").polyline(web).close().extrude(6).translate((x0, 0, 0)))
    s = s.union(box_span(-100, 100, -30, 30, d - 10, d - 5))
    s = s.cut(cyl_x(12, 100, -50))
    for x0 in (-80, 80):
        for y0 in (-18, 18):
            s = s.cut(cyl_z(4.5, 10, x0, y0, d - 12))
    return s


def p_rail_fixation():
    d = P["pan_back"]
    r = box_span(-10, 10, -P["pan_H"] / 2, P["pan_H"] / 2, d - 5, d)
    for y0 in (-18, 18, -P["pan_H"] / 2 + 6, P["pan_H"] / 2 - 6):
        r = r.cut(cyl_z(4.5, 10, 0, y0, d - 7))
    return r


def p_cadre_pv():
    """Cadre aluminium en C (paroi 1,5 mm, rebord avant et aile arrière de 12 mm)."""
    L, H, T, z0 = P["pan_L"], P["pan_H"], P["pan_T"], P["pan_back"]
    lip, w = 12.0, 1.5
    f = box_span(-L / 2, L / 2, -H / 2, H / 2, z0, z0 + T)
    f = f.cut(box_span(-L / 2 + w, L / 2 - w, -H / 2 + w, H / 2 - w, z0 + w, z0 + T - w))
    f = f.cut(box_span(-L / 2 + lip, L / 2 - lip, -H / 2 + lip, H / 2 - lip, z0 + T - w - 1, z0 + T + 1))
    f = f.cut(box_span(-L / 2 + lip, L / 2 - lip, -H / 2 + lip, H / 2 - lip, z0 - 1, z0 + w + 1))
    return f


def _z_laminate():
    top = P["pan_back"] + P["pan_T"] - 1.5 - 0.2       # sous le rebord avant
    return top - 3.2, top


def p_lamine():
    z0, z1 = _z_laminate()
    return box_span(-P["pan_L"] / 2 + 2, P["pan_L"] / 2 - 2, -P["pan_H"] / 2 + 2, P["pan_H"] / 2 - 2, z0, z1)


def p_cellules():
    _z0, z1 = _z_laminate()
    nx, ny, g = P["cell_nx"], P["cell_ny"], 2.0
    aw, ah = P["pan_L"] - 2 * 12 - 12, P["pan_H"] - 2 * 12 - 12
    cw, ch = (aw - (nx - 1) * g) / nx, (ah - (ny - 1) * g) / ny
    sk = cq.Sketch().rarray(cw + g, ch + g, nx, ny).rect(cw, ch)
    cells = cq.Workplane("XY").workplane(offset=z1).placeSketch(sk).extrude(0.15)
    return cells, cw, ch


def p_boite_jonction():
    z0, _z1 = _z_laminate()
    b = box_span(-30, 30, 40, 85, z0 - 14.2, z0 - 0.2).edges("|Z").fillet(4)
    return b.union(cyl_y_(12, 10, 0, 85, z0 - 7.2))


def cyl_y_(d, L, x, y0, z):
    return cq.Workplane("XZ").circle(d / 2).extrude(-L).translate((x, y0, z))


# ---------------------------------------------------------------------------
# PIÈCES — SOL
# ---------------------------------------------------------------------------
BOX_L, BOX_W, BOX_H = 420.0, 320.0, 240.0


def p_unite_corps():
    """Repère unité : origine au sol, +X vers le tracker."""
    b = box(BOX_L, BOX_W, BOX_H, 0, 0, 20 + BOX_H / 2).edges("|Z").fillet(10)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b = b.union(cyl_z(40, 20, sx * (BOX_L / 2 - 40), sy * (BOX_W / 2 - 40), 0))
    # connecteurs côté tracker
    for yy in (-50, 0, 50):
        b = b.union(cyl_x(30, 25, BOX_L / 2, yy, 70))
    # poignées de manutention (gants EVA)
    for sy in (-1, 1):
        y0 = sy * BOX_W / 2
        for xx in (-80, 80):
            b = b.union(box_span(xx - 8, xx + 8, *sorted((y0, y0 + sy * 45)), 172, 188))
        b = b.union(box_span(-88, 88, *sorted((y0 + sy * 30, y0 + sy * 45)), 172, 188))
    return b


def p_unite_radiateur():
    return box(BOX_L + 20, BOX_W + 20, 3, 0, 0, 20 + BOX_H + 1.5)


def p_faisceau():
    a = math.radians(P["phi_box"])
    c, s = math.cos(a), math.sin(a)
    r_end = P["r_box"] - BOX_L / 2 - 25
    rz = [(82, 790), (95, 700), (170, 520), (330, 260), (520, 60), (720, 10),
          (950, 10), (r_end - 60, 55), (r_end, 70)]
    pts = [Vector(r * c, r * s, z) for r, z in rz]
    tans = [Vector(0, 0, -1), Vector(c, s, 0)]
    path = cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, tangents=tans)])
    prof = cq.Workplane(cq.Plane(origin=pts[0], xDir=(c, s, 0), normal=(0, 0, -1))).circle(9)
    return prof.sweep(cq.Workplane().add(path), transition="round")


# ---------------------------------------------------------------------------
# ASSEMBLAGE
# ---------------------------------------------------------------------------
PARTS = {}     # nom -> (Workplane, matériau, couleur, description)


def reg(name, wp, mat, col, desc):
    PARTS[name] = (wp, mat, col, desc)
    return wp


def build_parts():
    PARTS.clear()
    reg("Colonne_Centrale", p_colonne(), "Al 7075-T73", COL["alu"], "Colonne centrale Ø80x2,5 anodisée dur")
    reg("Collier_Superieur", p_collier_sup(), "Ti-6Al-4V", COL["ti"], "Moyeu d'articulation des jambes")
    reg("Collier_Inferieur", p_collier_inf(), "Ti-6Al-4V", COL["ti"], "Collier coulissant des entretoises")
    reg("Ferrure_Jambe", p_ferrure_jambe(), "Ti-6Al-4V", COL["ti"], "Ferrure d'articulation de jambe")
    reg("Axe_Articulation", p_axe(), "Ti-6Al-4V", COL["alu_d"], "Axe Ø10 revêtu MoS2")
    reg("Tube_Jambe_Superieur", p_tube_sup(), "Al 7075-T73", COL["alu"], "Tube Ø40x1,5 anodisé dur")
    reg("Bague_Blocage", p_bague_blocage(), "Ti-6Al-4V", COL["orange"], "Bague de blocage télescopique")
    reg("Tube_Jambe_Inferieur", p_tube_inf(), "Al 7075-T73", COL["alu"], "Tube coulissant Ø34x1,5")
    reg("Embout_Rotule", p_embout_rotule(), "Ti-6Al-4V", COL["ti"], "Embout à rotule Ø36")
    reg("Bride_Entretoise", p_bride_entretoise(), "Ti-6Al-4V", COL["ti"], "Bride de fixation d'entretoise")
    reg("Patin", p_patin(), "Al 7075-T73", COL["alu_d"], "Patin Ø220 à crampons + logement de rotule")
    reg("Piquet_Ancrage", p_piquet(), "Ti-6Al-4V", COL["orange"], "Piquet d'ancrage régolithe 450 mm")
    reg("Axe_Entretoise", p_axe(10, 33, 16), "Ti-6Al-4V", COL["alu_d"], "Axe Ø10")
    reg("Embase_Tete", p_embase(), "Al 6061-T6", COL["blue"], "Embase fixe de la tête (sur la colonne)")
    reg("Roulement_Azimut", p_roulement_azimut(), "Acier 440C", COL["steel"],
        "Roulement d'azimut à section mince Ø90/Ø50")
    reg("Moteur_PasAPas_Azimut", p_nema17(36), "Acier 440C", COL["nema"],
        "Moteur pas à pas NEMA 17 d'azimut (axe vertical)")
    reg("Pignon_Azimut", p_pignon_azimut(), "Acier inox 17-4PH", COL["steel"],
        f"Pignon d'azimut m{M_AZ} Z{Z_PIGNON_AZ}")
    reg("Couronne_Azimut", p_couronne(), "Al 7075-T73", COL["orange"],
        f"Couronne d'azimut m{M_AZ} Z{Z_COURONNE}, anodisée dur + MoS2")
    reg("Etrier_Tete", p_etrier(), "Al 6061-T6", COL["grey"], "Étrier en U de la tête")
    reg("Palier_Elevation", p_palier(), "Al 6061-T6", COL["grey"], "Chapeau de palier d'élévation")
    reg("Moteur_PasAPas_Elevation", p_nema17(22), "Acier 440C", COL["nema"],
        "Moteur pas à pas NEMA 17 d'élévation (axe horizontal)")
    reg("Pignon_Elevation", p_pignon_elevation(), "Acier inox 17-4PH", COL["grey"],
        f"Pignon d'élévation m{M_EL} Z{Z_PIGNON_EL}")
    reg("Arbre_Elevation", p_arbre_elevation(), "Ti-6Al-4V", COL["steel"], "Axe d'élévation Ø12")
    reg("Roue_Elevation", p_roue_elevation(), "Al 7075-T73", COL["black"],
        f"Roue d'élévation m{M_EL} Z{Z_ROUE_EL}, anodisée noire + MoS2")
    reg("Support_Panneau", p_support_panneau(), "Al 6061-T6", COL["alu_d"], "Berceau de fixation du panneau")
    reg("Rail_Fixation_Panneau", p_rail_fixation(), "Al 6061-T6", COL["alu_d"], "Rail 20x5 vissé sur le cadre")
    reg("Cadre_Panneau", p_cadre_pv(), "Al 6063-T5", COL["alu"], "Cadre alu du panneau 356x253x30")
    reg("Lamine_PV", p_lamine(), "Verre 3,2 mm + EVA + backsheet (eq)", COL["pv_bg"],
        "Verre + EVA + face arrière")
    cells, cw, ch = p_cellules()
    reg("Cellules_PV", cells, "Silicium polycristallin", COL["pv"],
        f"{P['cell_nx']*P['cell_ny']} cellules {cw:.1f}x{ch:.1f}")
    reg("Boite_Jonction", p_boite_jonction(), "PPO (boîte de jonction)", COL["black"],
        "Boîte de jonction + presse-étoupe")
    reg("Unite_Controle_Corps", p_unite_corps(), "Al 6061-T6", COL["gold"],
        "Unité de contrôle / stockage sous MLI")
    reg("Unite_Controle_Radiateur", p_unite_radiateur(), "Al 6061-T6", COL["white"],
        "Radiateur zénithal (peinture blanche / OSR)")
    reg("Faisceau_Cables", p_faisceau(), "PTFE/cuivre (eq)", COL["black"], "Faisceau puissance + données Ø18")


def add(assy, name, loc=None, inst=None):
    wp, mat, col, _ = PARTS[name]
    assy.add(wp, name=inst or name, loc=loc or Location(), color=col)


def strut_geom(phi):
    """Points d'axe (repère monde Z-up) d'une entretoise."""
    a = math.radians(phi)
    p_in = (85 * math.cos(a), 85 * math.sin(a), P["z_lower_collar"])
    p_out = leg_point(phi, (0, -45, -P["s_clamp"]))
    return p_in, p_out


def build_tripod():
    t = cq.Assembly(name="SA_Trepied")
    add(t, "Colonne_Centrale")
    add(t, "Collier_Superieur")
    add(t, "Collier_Inferieur")
    leg = cq.Assembly(name="SA_Jambe")
    for n in ("Ferrure_Jambe", "Axe_Articulation", "Tube_Jambe_Superieur", "Bague_Blocage",
              "Tube_Jambe_Inferieur", "Embout_Rotule", "Bride_Entretoise"):
        add(leg, n)
    for i, phi in enumerate(P["leg_phis"], 1):
        t.add(leg, name=f"Jambe_{i}", loc=leg_loc(phi))
        a = math.radians(phi)
        # patin + piquet
        pl = trans(P["r_foot"] * math.cos(a), P["r_foot"] * math.sin(a), 0) * rot((0, 0, 1), phi)
        add(t, "Patin", pl, f"Patin_{i}")
        add(t, "Piquet_Ancrage", pl * trans(140, 0, 0), f"Piquet_{i}")
        # entretoise
        p_in, p_out = strut_geom(phi)
        rr = math.hypot(p_out[0], p_out[1]) - 85
        dz = p_out[2] - p_in[2]
        L = math.hypot(rr, dz)
        gam = math.degrees(math.atan2(-rr, dz))
        name = f"Entretoise_{i}"
        PARTS.setdefault("Entretoise", (p_entretoise(L), "Al 7075-T73", COL["alu"], "Entretoise Ø20x1,5"))
        wp, mat, col, _ = PARTS["Entretoise"]
        sl = trans(*p_in) * rot((0, 0, 1), phi - 90) * rot((1, 0, 0), gam)
        t.add(wp, name=name, loc=sl, color=col)
        add(t, "Axe_Entretoise", sl, f"Axe_Entretoise_Int_{i}")
        add(t, "Axe_Entretoise", sl * trans(0, 0, L), f"Axe_Entretoise_Ext_{i}")
    return t


def build_panel(el):
    """Partie qui tourne en élévation (repère panneau)."""
    p = cq.Assembly(name="SA_Panneau")
    add(p, "Arbre_Elevation")
    add(p, "Roue_Elevation", rot((1, 0, 0), -90))          # une dent face au pignon (el = 90°)
    add(p, "Support_Panneau")
    add(p, "Rail_Fixation_Panneau", trans(80, 0, 0), "Rail_Fixation_1")
    add(p, "Rail_Fixation_Panneau", trans(-80, 0, 0), "Rail_Fixation_2")
    add(p, "Cadre_Panneau")
    add(p, "Lamine_PV")
    add(p, "Cellules_PV")
    add(p, "Boite_Jonction")
    return p


def build_head(az, el):
    """Partie qui tourne en azimut : couronne, étrier, moteur et pignon d'élévation."""
    h = cq.Assembly(name="SA_Tete_Orientable")
    add(h, "Couronne_Azimut", rot((0, 0, 1), P["phi_motor_az"]))
    add(h, "Etrier_Tete")
    add(h, "Palier_Elevation")
    zm = P["z_el"] - ENTRAXE_EL
    add(h, "Moteur_PasAPas_Elevation", trans(50, 0, zm) * rot((0, 1, 0), 90))
    psi = el - 90.0
    th = 90.0 - 180.0 / Z_PIGNON_EL - psi * Z_ROUE_EL / Z_PIGNON_EL
    add(h, "Pignon_Elevation", trans(60, 0, zm) * rot((1, 0, 0), th))
    h.add(build_panel(el), name="SA_Panneau", loc=trans(0, 0, P["z_el"]) * rot((1, 0, 0), psi))
    return h


def build_head_fixed(az):
    """Partie fixe de la tête : embase, roulement, moteur et pignon d'azimut."""
    f = cq.Assembly(name="SA_Tete_Fixe")
    add(f, "Embase_Tete")
    add(f, "Roulement_Azimut")
    a = math.radians(P["phi_motor_az"])
    mx, my = ENTRAXE_AZ * math.cos(a), ENTRAXE_AZ * math.sin(a)
    add(f, "Moteur_PasAPas_Azimut", trans(mx, my, Z_EMB) * rot((0, 0, 1), P["phi_motor_az"]))
    th = P["phi_motor_az"] + 180.0 - 180.0 / Z_PIGNON_AZ - az * Z_COURONNE / Z_PIGNON_AZ
    add(f, "Pignon_Azimut", trans(mx, my, Z_COUR) * rot((0, 0, 1), th))
    return f


def build_ground():
    g = cq.Assembly(name="SA_Unite_Sol")
    add(g, "Unite_Controle_Corps")
    add(g, "Unite_Controle_Radiateur")
    return g


# Passage Z-up (construction) -> Y-up (SolidWorks)
TO_YUP = rot((1, 0, 0), -90)


def build_assembly(az, el, name):
    root = cq.Assembly(name=name)
    root.add(build_tripod(), name="SA_Trepied", loc=TO_YUP)
    root.add(build_head_fixed(az), name="SA_Tete_Fixe", loc=TO_YUP)
    root.add(build_head(az, el), name="SA_Tete_Orientable", loc=TO_YUP * rot((0, 0, 1), az))
    ab = math.radians(P["phi_box"])
    root.add(build_ground(), name="SA_Unite_Sol",
             loc=TO_YUP * trans(P["r_box"] * math.cos(ab), P["r_box"] * math.sin(ab), 0)
             * rot((0, 0, 1), P["phi_box"] + 180))
    fa = cq.Assembly(name="SA_Faisceau")
    add(fa, "Faisceau_Cables")
    root.add(fa, name="SA_Faisceau", loc=TO_YUP)
    return root


# ---------------------------------------------------------------------------
# ANALYSES
# ---------------------------------------------------------------------------
def flatten(assy, loc=None):
    """[(chemin, shape en repère monde)] pour toutes les pièces."""
    loc = loc or Location()
    out = []
    cur = loc * assy.loc
    for obj in ([assy.obj] if assy.obj is not None else []):
        shapes = obj.vals() if isinstance(obj, cq.Workplane) else [obj]
        comp = cq.Compound.makeCompound([s for s in shapes if isinstance(s, cq.Shape)])
        out.append((assy.name, comp.moved(cur)))
    for ch in assy.children:
        for n, s in flatten(ch, cur):
            out.append((f"{assy.name}/{n}", s))
    return out


def part_key(inst):
    base = inst.split("/")[-1]
    if base in PARTS:
        return base
    for k in sorted(PARTS, key=len, reverse=True):
        if base.startswith(k):
            return k
    aliases = {"Patin_": "Patin", "Piquet_": "Piquet_Ancrage", "Axe_Entretoise_": "Axe_Entretoise",
               "Rail_Fixation_": "Rail_Fixation_Panneau"}
    for a, k in aliases.items():
        if base.startswith(a):
            return k
    raise KeyError(inst)


def clean_step_names(path):
    """Nomme chaque pièce partagée par son nom de pièce (ex. 'Patin_1' -> 'Patin'),
    pour que SolidWorks crée Patin.SLDPRT utilisé 3 fois."""
    import re
    txt = open(path, encoding="utf-8", errors="replace").read()

    def sub(m):
        n = m.group(1)
        try:
            k = part_key(n)
        except KeyError:
            return m.group(0)       # sous-assemblage : nom conservé
        return f"PRODUCT('{k}','{k}'"
    txt = re.sub(r"PRODUCT\('([^']*)','\1'", sub, txt)
    open(path, "w", encoding="utf-8").write(txt)


def mass_properties(flat):
    rows, M, S = [], 0.0, Vector(0, 0, 0)
    for inst, shp in flat:
        k = part_key(inst)
        vol = shp.Volume()
        rho = MASS_TARGET[k] / vol if k in MASS_TARGET else MAT[PARTS[k][1]] * 1e-9
        m = vol * rho
        c = cq.Shape.centerOfMass(shp)
        rows.append((inst, k, PARTS[k][1] if k not in MASS_TARGET else "masse forfaitaire", vol, m, c))
        M += m
        S = S + c * m
    return rows, M, S * (1.0 / M)


def to_zup(v):
    # inverse de TO_YUP : (x, y, z)_Yup -> (x, -z, y)_Zup
    return Vector(v.x, -v.z, v.y)


def tipping(cg_zup):
    feet = []
    for phi in P["leg_phis"]:
        a = math.radians(phi)
        feet.append((P["r_foot"] * math.cos(a), P["r_foot"] * math.sin(a)))
    angs = []
    for i in range(3):
        (x1, y1), (x2, y2) = feet[i], feet[(i + 1) % 3]
        # distance du projeté du CdG à l'arête (côté intérieur)
        nx, ny = y2 - y1, -(x2 - x1)
        n = math.hypot(nx, ny)
        d = abs((cg_zup.x - x1) * nx + (cg_zup.y - y1) * ny) / n
        angs.append(math.degrees(math.atan2(d, cg_zup.z)))
    return min(angs)


def min_clearance(moving, fixed):
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    best = (1e9, None, None)
    for na, a in moving:
        for nb, b in fixed:
            ba, bb = a.BoundingBox(), b.BoundingBox()
            gap = max(ba.xmin - bb.xmax, bb.xmin - ba.xmax, ba.ymin - bb.ymax,
                      bb.ymin - ba.ymax, ba.zmin - bb.zmax, bb.zmin - ba.zmax)
            if gap > best[0]:
                continue
            ext = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
            ext.Perform()
            d = ext.Value()
            if d < best[0]:
                best = (d, na, nb)
    return best


def interference(flat, tol=1.0):
    """Volumes d'interpénétration (> tol mm3) entre pièces d'un même assemblage."""
    hits = []
    bbs = [(n, s, s.BoundingBox()) for n, s in flat]
    for i in range(len(bbs)):
        for j in range(i + 1, len(bbs)):
            na, a, ba = bbs[i]
            nb, b, bb = bbs[j]
            if (ba.xmin > bb.xmax or bb.xmin > ba.xmax or ba.ymin > bb.ymax or
                    bb.ymin > ba.ymax or ba.zmin > bb.zmax or bb.zmin > ba.zmax):
                continue
            v = a.intersect(b).Volume()
            if v > tol:
                hits.append((na, nb, v))
    return hits


# ---------------------------------------------------------------------------
# PRINCIPAL
# ---------------------------------------------------------------------------
POSES = {
    # nom de fichier : (azimut tête [deg], élévation soleil [deg], description)
    "Tracker_Lunaire_PoleSud": (160.0, 1.5,
        "Site de référence pôle Sud (Artemis) : soleil à +1,5° d'élévation, panneau quasi vertical"),
    "Tracker_Lunaire_LatitudeMoyenne": (180.0, 50.0,
        "Latitude moyenne (sites Apollo), soleil à 50° : panneau incliné à 40°"),
}


def main():
    check = "--no-check" not in sys.argv
    sweep = "--balayage" in sys.argv
    os.makedirs(OUT_PARTS, exist_ok=True)
    os.makedirs(OUT_DOC, exist_ok=True)

    print(f"Jambe : L = {LEG_L:.1f} mm, écartement = {LEG_BETA:.1f}° / verticale")
    build_parts()
    # l'entretoise dépend de la géométrie : on la crée via build_tripod
    build_tripod()

    # pièces seules (repère local de la pièce, Z-up) ; on repart d'un dossier propre
    for f in os.listdir(OUT_PARTS):
        if f.endswith(".step"):
            os.remove(os.path.join(OUT_PARTS, f))
    for name, (wp, mat, col, desc) in PARTS.items():
        cq.exporters.export(wp, os.path.join(OUT_PARTS, f"{name}.step"))

    results = {}
    for fname, (az, el, desc) in POSES.items():
        assy = build_assembly(az, el, fname)
        path = os.path.join(OUT_CAD, f"{fname}.step")
        assy.export(path)
        clean_step_names(path)
        flat = flatten(assy)
        rows, M, cg = mass_properties(flat)
        results[fname] = (assy, flat, rows, M, cg)
        print(f"\n{fname}: {desc}\n  -> {path}  ({os.path.getsize(path)/1e6:.1f} Mo, {len(flat)} occurrences)")

    # bilan de masse (pose pôle Sud)
    _, flat, rows, M, cg = results["Tracker_Lunaire_PoleSud"]
    agg = {}
    for inst, k, mat, vol, m, c in rows:
        e = agg.setdefault(k, [0, 0.0, mat, PARTS[k][3]])
        e[0] += 1
        e[1] += m
    with open(os.path.join(OUT_DOC, "bilan_masse.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Piece", "Quantite", "Materiau", "Masse totale (kg)", "Description"])
        for k, (q, m, mat, desc) in sorted(agg.items(), key=lambda kv: -kv[1][1]):
            w.writerow([k, q, mat, f"{m:.3f}", desc])
        w.writerow(["TOTAL", "", "", f"{M:.2f}", ""])

    tracker_rows = [r for r in rows if not r[0].split("/")[1].startswith(("SA_Unite_Sol", "SA_Faisceau"))]
    Mt = sum(r[4] for r in tracker_rows)
    cgt = Vector(0, 0, 0)
    for r in tracker_rows:
        cgt = cgt + r[5] * r[4]
    cgt = to_zup(cgt * (1 / Mt))
    print(f"\nMasse totale (avec unité sol + faisceau) : {M:.1f} kg")
    print(f"Masse tracker seul : {Mt:.1f} kg  -> poids lunaire {Mt*1.62:.0f} N (terrestre {Mt*9.81:.0f} N)")
    print(f"CdG tracker (pôle Sud) : x={cgt.x:.0f} y={cgt.y:.0f} z={cgt.z:.0f} mm")
    print(f"Angle de basculement mini (sans piquets) : {tipping(cgt):.1f}°")
    pad_area = math.pi * 0.110 ** 2
    print(f"Pression sous patin (Lune) : {Mt*1.62/3/pad_area:.0f} Pa")

    # CdG tracker pour la pose latitude moyenne
    _, _, rows2, _, _ = results["Tracker_Lunaire_LatitudeMoyenne"]
    tr2 = [r for r in rows2 if not r[0].split("/")[1].startswith(("SA_Unite_Sol", "SA_Faisceau"))]
    cg2 = Vector(0, 0, 0)
    for r in tr2:
        cg2 = cg2 + r[5] * r[4]
    cg2 = to_zup(cg2 * (1 / Mt))
    print(f"CdG tracker (lat. moyenne) : z={cg2.z:.0f} mm, basculement mini {tipping(cg2):.1f}°")

    cells_area = sum(f.Area() for f in PARTS["Cellules_PV"][0].faces(">Z").vals()) / 1e6
    print(f"Surface de cellules : {cells_area:.4f} m2")

    # relecture des fichiers STEP produits
    for fname in POSES:
        back = cq.importers.importStep(os.path.join(OUT_CAD, f"{fname}.step"))
        print(f"Relecture {fname}.step : {len(back.solids().vals())} solides, valide={back.val().isValid()}")

    if not check:
        return

    print("\nContrôle d'interférences statiques (pièce à pièce) :")
    for fname, (assy, flat, *_rest) in results.items():
        hits = interference(flat)
        print(f"  {fname}: {'aucune' if not hits else hits}")

    if not sweep:
        print("\n(contrôle de garde sur toute la plage : relancer avec --balayage, ~10 min)")
        return

    print("\nContrôle de garde sur toute la plage de mouvement :")
    fixed_names = ("SA_Trepied", "SA_Tete_Fixe", "SA_Unite_Sol", "SA_Faisceau")
    tilt_itf = ("Arbre_Elevation", "Roue_Elevation")     # axe dans ses paliers, roue en prise
    az_itf = ("Couronne_Azimut",)                          # couronne en prise avec le pignon d'azimut
    worst = {"panneau": (1e9,), "interface": (1e9,), "tete": (1e9,)}

    def keep(tag, res, *pose):
        if res[0] < worst[tag][0]:
            worst[tag] = res + pose

    for el in (P["el_min"], 0.0, 2.0, 30.0, 60.0, 88.0, P["el_max"]):
        for az in range(0, 120, 20):   # symétrie 120° du trépied
            assy = build_assembly(float(az), el, "chk")
            flat = flatten(assy)
            fixed = [(n, s) for n, s in flat if n.split("/")[1] in fixed_names]
            panel = [(n, s) for n, s in flat if "/SA_Panneau/" in n]
            head = [(n, s) for n, s in flat if "SA_Tete_Orientable" in n and "/SA_Panneau/" not in n]
            body = [(n, s) for n, s in panel if not n.split("/")[-1].startswith(tilt_itf)]
            roue = [(n, s) for n, s in panel if n.split("/")[-1].startswith("Roue_Elevation")]
            keep("panneau", min_clearance(body, fixed + head), az, el)
            keep("interface", min_clearance(roue, [x for x in head if "Pignon" in x[0]]), az, el)
            if el == 0.0:
                h = [(n, s) for n, s in head if not n.split("/")[-1].startswith(az_itf)]
                keep("tete", min_clearance(h, fixed), az, el)

    labels = {"panneau": "Panneau + berceau <-> toute structure",
              "interface": "Engrènement roue d'élévation / pignon (jeu de denture)",
              "tete": "Étrier + moteur d'élévation <-> partie fixe"}
    for tag, w in worst.items():
        print(f"  {labels[tag]} : garde mini {w[0]:.1f} mm "
              f"({w[1].split('/')[-1]} / {w[2].split('/')[-1]}, az={w[3]}°, él={w[4]}°)")


if __name__ == "__main__":
    main()
