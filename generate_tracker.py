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
    # Panneau photovoltaïque (format paysage, axe d'élévation // grand côté)
    pan_L=1600.0,          # longueur, parallèle à l'axe d'élévation
    pan_H=1200.0,          # largeur, dans le plan de rotation en élévation
    pan_off=146.0,         # distance axe d'élévation -> face arrière du panneau
    pan_sub=20.0,          # épaisseur du substrat nid d'abeille
    pan_frame_w=25.0,      # largeur du cadre périphérique
    pan_frame_h=26.0,      # hauteur du cadre
    cell_t=2.0,            # couche cellules + verre de protection (représentation)
    cell_nx=20, cell_ny=15,
    cell_gap=2.0,
    # Axes
    z_el=1500.0,           # hauteur de l'axe d'élévation au-dessus du sol
    el_min=-2.0, el_max=92.0,   # butées mécaniques d'élévation
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
    "CFRP M55J/cyanate":   1650.0,
    "Nid d'abeille Al + peaux CFRP (eq)": 105.0,   # ~2,1 kg/m2 pour 20 mm
    "Cellules GaInP/GaAs/Ge + CMG (eq)":  550.0,   # ~1,1 kg/m2 pour 2 mm
    "PTFE/cuivre (eq)":    2200.0,
}
# masses forfaitaires (kg) imposées pour les ensembles non détaillés
MASS_TARGET = {
    "Carter_Actionneur_Azimut": 5.5,     # moteur sans balais + réducteur harmonique + roulements + codeur
    "Carter_Actionneur_Elevation": 4.8,
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
# PIÈCES — AZIMUT
# ---------------------------------------------------------------------------
def p_carter_azimut():
    fl = ring_z(200, 60, 12, 815)
    body = cyl_z(180, 158, z=827)
    top = cyl_z(170, 5, z=985)
    c = fl.union(body).union(top)
    # têtes de vis de la bride
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        c = c.union(cyl_z(13, 6, 92 * math.cos(a), 92 * math.sin(a), 827))
    # embase connecteur (sortie de faisceau vers le bas, entre deux jambes)
    a = math.radians(P["phi_box"])
    c = c.union(cyl_z(30, 25, 82 * math.cos(a), 82 * math.sin(a), 790))
    # passage central de câbles (arbre creux)
    c = c.cut(cyl_z(40, 200, z=800))
    return c


def p_plateau_azimut():
    plate = ring_z(196, 40, 12, 993)
    skirt = ring_z(196, 186, 33, 960)      # jupe labyrinthe anti-poussière
    return plate.union(skirt)


def p_mat():
    fl0 = ring_z(150, 82, 12, 1005)
    t = tube_z(90, 4, 1383 - 1017, 1017)
    fl1 = ring_z(150, 82, 12, 1383)
    m = fl0.union(t).union(fl1)
    # goussets de raidissement aux deux brides
    for z0, sgn in ((1017, 1), (1383, -1)):
        gus = (cq.Workplane("XZ").polyline([(44, 0), (72, 0), (44, 40 * sgn)]).close()
               .extrude(2, both=True).translate((0, 0, z0)))
        for k in range(4):
            m = m.union(gus.rotate((0, 0, 0), (0, 0, 1), 45 + 90 * k))
    return m


def p_carter_elevation():
    ze = P["z_el"]
    body = cyl_x(180, 216, -108, 0, ze)
    body = body.union(box_span(-70, 70, -70, 70, 1395, ze))
    # boîtier codeurs / inclinomètre (côté opposé au panneau, jamais balayé)
    body = body.union(box_span(-55, 55, -150, -60, 1420, 1490).edges("|X").fillet(8))
    return body


# ---------------------------------------------------------------------------
# PIÈCES — PANNEAU (repère panneau : origine sur l'axe d'élévation,
#                   X = axe, Z = normale au panneau, cellules côté +Z)
# ---------------------------------------------------------------------------
def p_flasque():
    f = cyl_x(140, 10, 110).cut(cyl_x(56, 12, 109))
    f = f.union(cq.Workplane("YZ").circle(35).circle(28).extrude(4).translate((120, 0, 0)))
    for k in range(6):
        a = math.radians(30 + 60 * k)
        f = f.union(cyl_x(11, 5, 120, 52 * math.cos(a), 52 * math.sin(a)))
    return f


def p_tube_torsion():
    return cq.Workplane("YZ").circle(35).circle(32).extrude(560 - 124).translate((124, 0, 0))


def _lisse_shape():
    """Lisse longitudinale (tube rectangulaire 30x25x2)."""
    L = 1520.0
    z0 = P["pan_off"] - 25
    outer = box(L, 30, 25, 0, 0, z0 + 12.5)
    inner = box(L + 2, 26, 21, 0, 0, z0 + 12.5)
    return outer.cut(inner)


def p_lisse():
    return _lisse_shape()


def p_nervure():
    off = P["pan_off"]
    prof = (cq.Workplane("YZ")
            .polyline([(-560, off), (560, off), (560, off - 26), (60, 30), (-60, 30), (-560, off - 26)])
            .close().extrude(4).translate((-2, 0, 0)))
    boss = cyl_x(94, 30, -15)
    rib = prof.union(boss)
    # allègements
    for yc, d, zc in ((-490, 22, off - 13), (-300, 40, off - 32), (-170, 52, off - 42),
                      (170, 52, off - 42), (300, 40, off - 32), (490, 22, off - 13)):
        rib = rib.cut(cyl_x(d, 10, -5, yc, zc))
    rib = rib.cut(cyl_x(70.2, 32, -16))                          # tube de torsion
    for ys in (-400, 400):                                       # passage des lisses
        rib = rib.cut(box(12, 30.4, 25.4, 0, ys, off - 12.5))
    return rib


def p_substrat():
    fw = P["pan_frame_w"]
    return box_span(-P["pan_L"] / 2 + fw, P["pan_L"] / 2 - fw,
                    -P["pan_H"] / 2 + fw, P["pan_H"] / 2 - fw,
                    P["pan_off"], P["pan_off"] + P["pan_sub"])


def p_cadre():
    L, H, fw, fh, off = P["pan_L"], P["pan_H"], P["pan_frame_w"], P["pan_frame_h"], P["pan_off"]
    w = 1.5
    outer = box_span(-L / 2, L / 2, -H / 2, H / 2, off, off + fh)
    inner = box_span(-L / 2 + fw, L / 2 - fw, -H / 2 + fw, H / 2 - fw, off - 1, off + fh + 1)
    ring = outer.cut(inner)
    void = (box_span(-L / 2 + w, L / 2 - w, -H / 2 + w, H / 2 - w, off + w, off + fh - w)
            .cut(box_span(-L / 2 + fw - w, L / 2 - fw + w, -H / 2 + fw - w, H / 2 - fw + w, off, off + fh)))
    return ring.cut(void)


def p_cellules():
    fw = P["pan_frame_w"]
    aw = P["pan_L"] - 2 * fw - 20
    ah = P["pan_H"] - 2 * fw - 20
    nx, ny, g = P["cell_nx"], P["cell_ny"], P["cell_gap"]
    cw = (aw - (nx - 1) * g) / nx
    ch = (ah - (ny - 1) * g) / ny
    z0 = P["pan_off"] + P["pan_sub"]
    sk = (cq.Sketch().rarray(cw + g, ch + g, nx, ny).rect(cw, ch))
    cells = cq.Workplane("XY").workplane(offset=z0).placeSketch(sk).extrude(P["cell_t"])
    return cells, cw, ch


def p_capteur_solaire():
    zt = P["pan_off"] + P["pan_frame_h"]
    y = -P["pan_H"] / 2 + P["pan_frame_w"] / 2
    b = box_span(-30, 30, y - 10, y + 10, zt, zt + 18).edges("|Z").fillet(3)
    w = cyl_z(12, 2, 0, y, zt + 18)
    return b.union(w)


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
    reg("Carter_Actionneur_Azimut", p_carter_azimut(), "Al 6061-T6", COL["white"],
        "Actionneur azimut coaxial (moteur + réducteur harmonique)")
    reg("Plateau_Azimut", p_plateau_azimut(), "Al 6061-T6", COL["alu"], "Plateau tournant + jupe labyrinthe")
    reg("Mat_Rotatif", p_mat(), "CFRP M55J/cyanate", COL["cfrp"], "Mât tournant Ø90x4")
    reg("Carter_Actionneur_Elevation", p_carter_elevation(), "Al 6061-T6", COL["white"],
        "Actionneur élévation double sortie")
    reg("Flasque_Sortie", p_flasque(), "Ti-6Al-4V", COL["ti"], "Flasque de sortie élévation")
    reg("Tube_Torsion", p_tube_torsion(), "CFRP M55J/cyanate", COL["cfrp"], "Demi-tube de torsion Ø70x3")
    reg("Nervure_Panneau", p_nervure(), "Al 7075-T73", COL["alu_d"], "Nervure de support du panneau")
    reg("Lisse_Panneau", p_lisse(), "CFRP M55J/cyanate", COL["cfrp"], "Lisse longitudinale 30x25x2")
    reg("Substrat_Panneau", p_substrat(), "Nid d'abeille Al + peaux CFRP (eq)", COL["back"],
        "Substrat nid d'abeille 20 mm")
    reg("Cadre_Panneau", p_cadre(), "CFRP M55J/cyanate", COL["alu"], "Cadre périphérique creux 25x26")
    cells, cw, ch = p_cellules()
    reg("Cellules_PV", cells, "Cellules GaInP/GaAs/Ge + CMG (eq)", COL["cell"],
        f"{P['cell_nx']*P['cell_ny']} modules de cellules triple jonction {cw:.1f}x{ch:.1f}")
    reg("Capteur_Solaire", p_capteur_solaire(), "Al 6061-T6", COL["black"], "Capteur solaire fin 2 axes")
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


def build_panel():
    p = cq.Assembly(name="SA_Panneau")
    add(p, "Flasque_Sortie", inst="Flasque_Sortie_D")
    add(p, "Flasque_Sortie", rot((0, 0, 1), 180), "Flasque_Sortie_G")
    add(p, "Tube_Torsion", inst="Tube_Torsion_D")
    add(p, "Tube_Torsion", rot((0, 0, 1), 180), "Tube_Torsion_G")
    add(p, "Nervure_Panneau", trans(450, 0, 0), "Nervure_D")
    add(p, "Nervure_Panneau", trans(-450, 0, 0), "Nervure_G")
    add(p, "Lisse_Panneau", trans(0, 400, 0), "Lisse_1")
    add(p, "Lisse_Panneau", trans(0, -400, 0), "Lisse_2")
    add(p, "Substrat_Panneau")
    add(p, "Cadre_Panneau")
    add(p, "Cellules_PV")
    add(p, "Capteur_Solaire")
    return p


def build_head(el):
    h = cq.Assembly(name="SA_Tete_Orientable")
    add(h, "Plateau_Azimut")
    add(h, "Mat_Rotatif")
    add(h, "Carter_Actionneur_Elevation")
    h.add(build_panel(), name="SA_Panneau",
          loc=trans(0, 0, P["z_el"]) * rot((1, 0, 0), el - 90))
    return h


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
    a = cq.Assembly(name="SA_Azimut_Fixe")
    add(a, "Carter_Actionneur_Azimut")
    root.add(a, name="SA_Azimut_Fixe", loc=TO_YUP)
    root.add(build_head(el), name="SA_Tete_Orientable", loc=TO_YUP * rot((0, 0, 1), az))
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
               "Flasque_Sortie_": "Flasque_Sortie", "Tube_Torsion_": "Tube_Torsion",
               "Nervure_": "Nervure_Panneau", "Lisse_": "Lisse_Panneau"}
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

    # pièces seules (repère local de la pièce, Z-up)
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
    p_bol = cells_area * 1361 * 0.30
    print(f"Surface active cellules : {cells_area:.3f} m2 -> {p_bol:.0f} W (BOL, 30 %, AM0)")

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
    fixed_names = ("SA_Trepied", "SA_Azimut_Fixe", "SA_Unite_Sol", "SA_Faisceau")
    interface = ("Flasque_Sortie", "Tube_Torsion", "Plateau_Azimut")   # jeux fonctionnels
    worst = {"panneau": (1e9,), "interface": (1e9,), "tete": (1e9,)}

    def keep(tag, res, *pose):
        if res[0] < worst[tag][0]:
            worst[tag] = res + pose

    for el in (P["el_min"], 0.0, 2.0, 30.0, 60.0, 88.0, P["el_max"]):
        for az in range(0, 120, 20):   # symétrie 120° du trépied
            assy = build_assembly(float(az), el, "chk")
            flat = flatten(assy)
            fixed = [(n, s) for n, s in flat if n.split("/")[1] in fixed_names]
            panel = [(n, s) for n, s in flat if "/SA_Panneau/" in n and "Cellules" not in n]
            head = [(n, s) for n, s in flat if "SA_Tete_Orientable" in n and "/SA_Panneau/" not in n]
            body = [(n, s) for n, s in panel if not n.split("/")[-1].startswith(interface)]
            itf = [(n, s) for n, s in panel if n.split("/")[-1].startswith(interface)]
            keep("panneau", min_clearance(body, fixed + head), az, el)
            keep("interface", min_clearance(itf, fixed + head), az, el)
            if el == 0.0:
                h = [(n, s) for n, s in head if not n.split("/")[-1].startswith(interface)]
                keep("tete", min_clearance(h, fixed), az, el)

    labels = {"panneau": "Panneau (cadre, nervures, lisses) <-> toute structure",
              "interface": "Jeu fonctionnel flasques / carter élévation",
              "tete": "Mât + carter élévation <-> partie fixe"}
    for tag, w in worst.items():
        print(f"  {labels[tag]} : garde mini {w[0]:.1f} mm "
              f"({w[1].split('/')[-1]} / {w[2].split('/')[-1]}, az={w[3]}°, él={w[4]}°)")


if __name__ == "__main__":
    main()
