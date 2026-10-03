#!/usr/bin/env python3
"""
Tracker solaire lunaire deux axes (azimut + élévation) sur trépied déployable,
tête rotative à vis sans fin (irréversible : tient moteurs coupés, sans contrepoids).

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
OUT_CAD = os.path.join(HERE, "CAO", "Cas_Reel")
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
    pan_back=46.0,         # distance axe d'élévation -> dos du cadre (passe devant la chape à -2°)
    cell_nx=9, cell_ny=8,
    # Axes
    z_el=700.0,            # hauteur de l'axe d'élévation au-dessus du sol
    el_min=-2.0, el_max=92.0,   # butées mécaniques d'élévation
    # Trépied, dimensionné pour le panneau 356 x 253 et la tête à vis sans fin
    col_od=50.0, col_t=2.0,        # colonne centrale
    r_hinge=70.0,                  # articulation haute des jambes (hauteur : sous le socle de la tête)
    z_ball=40.0,                   # hauteur du centre de la rotule de pied
    leg_phis=(90.0, 210.0, 330.0), # jambes en Y, à 120° (repère Z-up)
    # Angle φ entre jambe et colonne : valeur optimale calculée par optimisation_angle.py
    leg_angle=32.5,
    tube_up=(25.0, 1.5), tube_low=(20.0, 1.5),  # tubes de jambe (Ø, épaisseur)
    r_lower_pin=52.0,              # axe d'entretoise sur le collier inférieur
    lug_off=28.0,                  # excentration de la chape d'entretoise sur la jambe
    # Exigences du trépied (utilisées par optimisation_angle.py)
    pente_stabilite=15.0,     # pente maxi sur laquelle le tracker tient sans ancrage (°)
    obstacle=50.0,            # caillou ou enfoncement sous un pied (mm)
    marge_basculement=5.0,    # marge de sécurité au basculement (°)
    pente_nivelage=10.0,      # pente maxi rattrapée par les jambes télescopiques (°)
    recouvrement_min=45.0,    # recouvrement mini des tubes télescopiques (mm)
    pad_d=120.0,                   # patin
    anchor_x=110.0, anchor_depth=400.0, anchor_helix_d=60.0,   # vis d'ancrage hélicoïdale
    # Unité de contrôle au sol et faisceau
    phi_box=30.0, r_box=950.0,
)

Z_T = 156.0                        # axe d'élévation au-dessus du sommet de la colonne (tête)
Z_EMB = P["z_el"] - Z_T            # sommet de la colonne = dessous du socle de la tête
P["z_hinge"] = Z_EMB - 35.0        # moyeu des jambes juste sous la tête

# Géométrie dérivée du trépied (fonction de l'angle φ des jambes)
LEG_L = LEG_BETA = None


def set_leg_geometry(phi):
    """Recalcule la géométrie des jambes pour un angle φ (°, entre jambe et colonne)."""
    global LEG_L, LEG_BETA
    b = math.radians(phi)
    h = P["z_hinge"] - P["z_ball"]
    LEG_BETA = phi
    LEG_L = h / math.cos(b)                              # articulation -> centre de rotule
    P["leg_angle"] = phi
    P["r_foot"] = P["r_hinge"] + h * math.tan(b)
    # jambes télescopiques : course ±t autour de la longueur nominale, assez pour
    # remettre la tête de niveau sur la pente de nivelage
    t = P["r_foot"] * math.tan(math.radians(P["pente_nivelage"])) / math.cos(b)
    P["course_telescopique"] = t
    P["s_low_start"] = 60.0 + t                          # rentré de t : butée à 60 mm de l'axe
    P["s_up_end"] = P["s_low_start"] + t + P["recouvrement_min"]
    # bride d'entretoise au plus bas du tube supérieur, juste au-dessus de la bague de
    # blocage (meilleur bras de levier) ; le collier inférieur se place à sa hauteur
    # pour que l'entretoise soit horizontale
    P["s_clamp"] = P["s_up_end"] - 36.0
    P["z_lower_collar"] = P["z_hinge"] - P["s_clamp"] * math.cos(b) - P["lug_off"] * math.sin(b)
    P["z_col_bot"] = P["z_lower_collar"] - 50.0


def course_telescopique_max(phi):
    """Course ±t maximale d'une jambe à deux tubes de longueur nominale L :
    rentrée de t, le bas du tube inférieur (L-t-60) doit rester sous la bague (s_up_end+20)."""
    L = (P["z_hinge"] - P["z_ball"]) / math.cos(math.radians(phi))
    return (L - 140.0 - P["recouvrement_min"]) / 3.0


set_leg_geometry(P["leg_angle"])


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
    "Bronze CuSn12":       8800.0,
    "PETG":                1270.0,
    "Acier (visserie)":    7850.0,
    "Verre 3,2 mm + EVA + backsheet (eq)": 2500.0,
    "Silicium polycristallin": 2330.0,
    "PPO (boîte de jonction)": 1100.0,
    "PTFE/cuivre (eq)":    2200.0,
}
# masses forfaitaires (kg) imposées pour les ensembles non détaillés
MASS_TARGET = {
    "Moteur_Elevation_NEMA17": 0.22,     # NEMA 17, 34 mm
    "Moteur_Azimut_NEMA11": 0.14,        # NEMA 11, 45 mm
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
    "socle":  cq.Color(0.45, 0.33, 0.25),
    "chape":  cq.Color(0.86, 0.72, 0.30),
    "u":      cq.Color(0.33, 0.45, 0.80),
    "brass":  cq.Color(0.80, 0.65, 0.30),
    "coupler": cq.Color(0.55, 0.60, 0.85),
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


def cyl_y(d, L, x, y0, z):
    """Cylindre d'axe Y, de y0 à y0+L."""
    return cq.Workplane("XZ").circle(d / 2).extrude(-L).translate((x, y0, z))


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
    od, t, z0 = P["col_od"], P["col_t"], P["z_col_bot"]
    tb = tube_z(od, t, Z_EMB - z0, z0)
    tb = tb.cut(cyl_dir(3.4, 8, (0, -od / 2 + 4, Z_EMB - 8), (0, -1, 0)))   # vis anti-rotation de la tête
    # embout inférieur conique creux (évite l'accumulation de régolithe)
    cone = cq.Workplane().add(cq.Solid.makeCone(od / 2, 6, 25, Vector(0, 0, z0), Vector(0, 0, -1)))
    cone = cone.cut(cq.Workplane().add(cq.Solid.makeCone(od / 2 - t, 4.5, 23, Vector(0, 0, z0), Vector(0, 0, -1))))
    return tb.union(cone)


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
    zc, od = P["z_hinge"], P["col_od"]
    body = ring_z(od + 16, od + 0.2, 44, zc - 22)
    for phi in P["leg_phis"]:
        cl = _clevis_pair(od / 2 + 4, P["r_hinge"], zc, 26, 5, 24, 12, 6.2)
        body = body.union(cl.rotate((0, 0, 0), (0, 0, 1), phi - 90))
    # vis de serrage sur la colonne
    rr = (od + 16) / 2 - 2
    for phi in P["leg_phis"]:
        a = math.radians(phi + 60)
        body = body.union(cyl_dir(8, 8, (rr * math.cos(a), rr * math.sin(a), zc - 12),
                                  (math.cos(a), math.sin(a), 0)))
    return body


def p_collier_inf():
    zc, od = P["z_lower_collar"], P["col_od"]
    body = ring_z(od + 10, od + 0.2, 30, zc - 15)
    for phi in P["leg_phis"]:
        cl = _clevis_pair(od / 2 + 2, P["r_lower_pin"], zc, 13, 4, 16, 8, 5.2)
        body = body.union(cl.rotate((0, 0, 0), (0, 0, 1), phi - 90))
    return body


# --- repère jambe : origine = axe d'articulation, axe X = axe de l'articulation,
#     jambe selon -Z, extérieur = +Y (avant rotation d'écartement)
def p_ferrure_jambe():
    D = P["tube_up"][0]
    body = cyl_x(24, 24, -12)
    body = body.union(box_span(-12, 12, -12, 12, -28, 0))
    body = body.union(cyl_z(D + 6, 35, z=-55))
    body = body.cut(cyl_z(D + 0.2, 26, z=-56))          # alésage du tube
    body = body.cut(cyl_x(6.2, 28, -14))                 # passage d'axe
    return body


def p_axe(d, span, head):
    shaft = cyl_x(d, span + 4, -span / 2)
    return shaft.union(cyl_x(head, 6, -span / 2 - 6))


def p_tube_sup():
    D, t = P["tube_up"]
    return tube_z(D, t, P["s_up_end"] - 32, -P["s_up_end"])


def p_bague_blocage():
    D, d, s = P["tube_up"][0], P["tube_low"][0], P["s_up_end"]
    ro = (D + 7) / 2
    b = ring_z(D + 7, D + 0.2, 20, -s).union(ring_z(D + 7, d + 0.2, 12, -s - 12))
    lever = box_span(-4, 4, ro - 1, ro + 18, -s - 8, -s + 8)
    lever = lever.union(cyl_x(10, 12, -6, ro + 18, -s))
    return b.union(lever)


def p_tube_inf():
    d, t = P["tube_low"]
    return tube_z(d, t, (LEG_L - 60) - P["s_low_start"], -(LEG_L - 60))


def p_embout_rotule():
    L, d = LEG_L, P["tube_low"][0]
    plug = cyl_z(d, 24, z=-(L - 36))             # s de L-60 à L-36 (bout du tube inférieur)
    neck = cyl_z(13, 37, z=-L)                   # col Ø13 jusqu'au centre de la rotule
    ball = cq.Workplane().sphere(11).translate((0, 0, -L))
    return plug.union(neck).union(ball)


def p_bride_entretoise():
    s, D, lo = P["s_clamp"], P["tube_up"][0], P["lug_off"]
    ring = ring_z(D + 7, D + 0.2, 22, -s - 11)
    lug = None                                   # chape tournée vers la colonne (-Y)
    for sgn in (1, -1):
        xa, xb = sorted((sgn * 6.5, sgn * 10.5))
        plate = box_span(xa, xb, -lo, -(D / 2 + 2), -s - 7, -s + 7)
        plate = plate.union(cyl_x(15, xb - xa, xa, -lo, -s))
        plate = plate.cut(cyl_x(5.2, xb - xa + 2, xa - 1, -lo, -s))
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
    eye0 = cyl_x(16, 12, -6).cut(cyl_x(5.2, 14, -7))
    eye1 = cyl_x(16, 12, -6, 0, length).cut(cyl_x(5.2, 14, -7, 0, length))
    t = tube_z(12, 1, length - 2 * 7, 7)
    return eye0.union(eye1).union(t)


def p_patin():
    """Repère patin : origine au sol sous la rotule, +X = direction radiale."""
    zb, R, ax = P["z_ball"], P["pad_d"] / 2, P["anchor_x"]
    b = math.radians(LEG_BETA)
    u = (-math.sin(b), 0.0, math.cos(b))                  # vers l'articulation
    base = cyl_z(2 * R, 4)
    # crampons sous la semelle (accroche dans le régolithe)
    for k in range(6):
        a = math.radians(30 + 60 * k)
        base = base.union(cq.Workplane().add(cq.Solid.makeCone(
            4, 0.5, 8, Vector(0.66 * R * math.cos(a), 0.66 * R * math.sin(a), 0), Vector(0, 0, -1))))
    ped = cq.Workplane().add(cq.Solid.makeCone(0.5 * R, 17, zb - 12, Vector(0, 0, 4), Vector(0, 0, 1)))
    ped = ped.cut(cq.Workplane().add(cq.Solid.makeCone(0.5 * R - 3, 12, 20, Vector(0, 0, 4), Vector(0, 0, 1))))
    # douille alignée sur l'axe nominal de la jambe (débattement de rotule ±20°)
    sock = cyl_dir(36, 30, (-22 * u[0], 0, zb - 22 * u[2]), u)
    body = base.union(ped).union(sock)
    # nervures radiales
    for k in range(6):
        rib = (cq.Workplane("XZ").polyline([(0.45 * R, 4), (0.87 * R, 4), (0.87 * R, 7), (24, zb - 14), (24, zb - 19)])
               .close().extrude(1.5, both=True))
        body = body.union(rib.rotate((0, 0, 0), (0, 0, 1), 60 * k))
    # anneau de la vis d'ancrage (côté extérieur) : l'hélice Ø60 passe dans l'alésage Ø64
    ring = cyl_z(80, 8, ax, 0, 0).union(box_span(R - 8, ax - 35, -10, 10, 0, 8))
    body = body.cut(cyl_z(8, 6, 0, 0, -1))       # évent du piédestal creux (pas de volume clos sous vide)
    body = body.union(ring)
    body = body.cut(cyl_z(P["anchor_helix_d"] + 4, 12, ax, 0, -2))
    # logement sphérique de la rotule (jeu 0,2 mm)
    body = body.cut(cq.Workplane().sphere(11.2).translate((0, 0, zb)))
    return body


def p_ancrage():
    """Vis d'ancrage hélicoïdale Ti : tige Ø12, hélice Ø60 dans la couche compacte."""
    H, B = P["anchor_depth"], P["anchor_helix_d"]
    shaft = cyl_z(12, H + 12, z=-H)
    tip = cq.Workplane().add(cq.Solid.makeCone(6, 0.5, 20, Vector(0, 0, -H), Vector(0, 0, -1)))
    z0 = -H + 15
    rm = (B / 2 + 5.5) / 2                        # rayon moyen de la spire (de Ø11 à B)
    helix = cq.Wire.makeHelix(pitch=20, height=20, radius=rm, center=Vector(0, 0, z0))
    flight = (cq.Workplane("XZ").center(rm, z0).rect(B / 2 - 5.5, 3)
              .sweep(cq.Workplane().add(helix), isFrenet=True))
    washer = cyl_z(76, 4, z=8)                    # appui sur l'anneau du patin
    hexa = cq.Workplane("XY").polygon(6, 19.6).extrude(14).translate((0, 0, 12))   # six pans de 17
    return shaft.union(tip).union(flight).union(washer).union(hexa)


# ---------------------------------------------------------------------------
# ENGRENAGES (profil en développante de cercle, angle de pression 20°) :
# roues des deux vis sans fin
# ---------------------------------------------------------------------------
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
# PIÈCES — TÊTE ROTATIVE À VIS SANS FIN
#   Repère tête : origine au sommet de la colonne (Z_EMB), Z vertical.
#   - Socle Ø62 fixé sur la colonne : deux roulements 6806 d'azimut et la roue
#     d'azimut, FIXE.
#   - Chape en U, qui tourne en azimut et porte les deux moteurs. La vis d'azimut
#     roule autour de la roue fixe, comme sur une tourelle.
#   - Chapeau en U renversé, qui pivote en élévation (axes Ø8 sur roulements 608)
#     et porte le panneau. La roue d'élévation est sur son pivot gauche.
#   Élévation : NEMA 17 de 34 mm + vis m1 Ø16 / roue Z50 (50:1).
#   Azimut    : NEMA 11 de 45 mm + vis m0,8 Ø12 / roue Z60 (60:1).
#   Les deux vis sont irréversibles : la tête tient moteurs coupés, sans contrepoids.
#   Chaque vis tourne sur son arbre (2 roulements 685), reliée au moteur par un
#   accouplement flexible : le moteur ne reçoit pas la poussée de la vis.
# ---------------------------------------------------------------------------
# AJUSTEMENTS : deux jeux de cotes pour les mêmes pièces.
#   "reel" : cas réel (pièces usinées), cotes nominales.
#   "petg" : démonstration sur Terre, pièces imprimées en 3D en PETG. Les trous
#            imprimés sortent plus petits et les dents moins précises : jeux
#            d'ajustement, dentures plus jeu, et quelques formes adaptées à
#            l'impression (moyeu de chape séparé, vis à moyeux, méplats).
#   set_ajustements("petg") avant build_head_parts().
AJUSTEMENTS = {
    "reel": dict(
        impression=False,
        roulement=0.0,          # logement de roulement : + sur le Ø
        serrage=0.0,            # alésage d'un axe acier fixé dans la pièce (Ø5 des vis, Ø8 des pivots)
        moyeu=0.0,              # Ø du moyeu de chape dans les bagues intérieures des 6806 (Ø30)
        colonne=45.5,           # Ø du téton de centrage dans la colonne (Ø intérieur 46)
        passage_m3=3.4,         # trou de passage M3
        taraud_m3=2.5,          # avant-trou M3 (taraudé)
        passage_m25=2.9,        # trou de passage M2,5 (NEMA 11)
        pilote=22.5,            # centrage Ø22 des moteurs
        jeu_denture=(0.10, 0.12),   # amincissement des dents des roues, mm (élévation, azimut)
        jeu_filet=0.15,         # amincissement du filet des vis (en modules)
        tete_filet=1.0,         # saillie du filet des vis (en modules)
        entraxe=0.0,            # augmentation des entraxes vis / roue (mm)
    ),
    "petg": dict(
        impression=True,
        roulement=0.15, serrage=0.10, moyeu=-0.05, colonne=45.6,
        passage_m3=3.5, taraud_m3=2.8, passage_m25=3.0, pilote=22.4,
        jeu_denture=(0.30, 0.30), jeu_filet=0.0, tete_filet=0.85, entraxe=0.15,
    ),
}
MODE = "reel"
AJ = AJUSTEMENTS[MODE]


def set_ajustements(mode):
    """Choisit le jeu de cotes ("reel" ou "petg") ; reconstruire ensuite les pièces."""
    global MODE, AJ
    MODE, AJ = mode, AJUSTEMENTS[mode]


COL_ID = P["col_od"] - 2 * P["col_t"]
SOCLE_OD, SOCLE_ID = 62.0, 56.0
Z_ROUL1, Z_ROUL2 = 58.0, 45.0        # roulements 6806 d'azimut
Z_CHAPE = 92.0                       # dessous de la plaque de la chape
ARM_X = (40.0, 48.0)                 # bras de la chape
ARM_R = 24.0
U_X = (50.0, 56.0)                   # flancs du chapeau en U
U_TOP = (28.0, 33.0)                 # plaque du chapeau (distance à l'axe)
U_Y = 22.0
U_BAS = -25.0                        # bas des flancs (sous l'axe)
RAIL_X = 44.0                        # rails du panneau
X_ROUE = (-34.0, -26.0)              # roue d'élévation sur le pivot gauche
EL_REF = 40.0                        # élévation de référence du calage des vis
MEPLAT = 3.5                         # méplat des axes Ø8 en D (version imprimée) : à 3,5 mm de l'axe

MOT_EL = dict(c=42.3, L=34.0, pilot=22.0, holes=31.0, hole_d=3.0, shaft=24.0, hold=0.28,
              detent=0.016, amp=1.3, ohm=2.4, masse=0.22, nom="NEMA 17 42 x 42 x 34 mm (type 17HS3401)")
MOT_AZ = dict(c=28.2, L=45.0, pilot=22.0, holes=23.0, hole_d=2.5, shaft=20.0, hold=0.095,
              detent=0.005, amp=0.67, ohm=6.9, masse=0.14, nom="NEMA 11 28 x 28 x 45 mm (type 11HS18-0674S)")
# vis : module, nombre de dents de la roue, Ø primitif, longueur filetée, début du moyeu (version imprimée)
VIS_EL = dict(m=1.0, z=50, dp=16.0, L=10.0, moyeu=5.0)       # vis m1 Ø16 + roue Z50
VIS_AZ = dict(m=0.8, z=60, dp=12.0, L=9.0, moyeu=8.0)        # vis m0,8 Ø12 + roue fixe Z60
# vis d'azimut le long de X à la hauteur z ; roue fixe de z 72 à 80
AZ_VIS = dict(zr=(72.0, 80.0), z=76.0, palier=(14.0, 19.0), x_joint=-32.5, x_face=-52.5)
# vis d'élévation le long de Y, en x = -30, sous la roue
EL_VIS = dict(palier=(14.0, 19.0), y_joint=-32.5, y_face=-56.5)
B685 = (11.0, 5.0, 5.0)              # roulement 685 : Ø11 / Ø5 x 5
# calage angulaire des vis (dents en prise sans chevauchement) : recalculé et
# vérifié par generate_tete_vis_sans_fin.py pour chaque jeu de cotes
PHASES = {"reel": {"el": 30.0, "az": -1.9}, "petg": {"el": 30.0, "az": -1.9}}
PIECES_IMPRIMEES = ("Fond_Socle", "Socle", "Roue_Azimut_Fixe", "Chape", "Moyeu_Chape", "Bague_Arret_Moyeu",
                    "Palier_Vis_Azimut", "Support_Moteur_Azimut", "Vis_Azimut", "Palier_Vis_Elevation",
                    "Support_Moteur_Elevation", "Vis_Elevation", "Chapeau_U", "Roue_Elevation")


def entraxe_el():
    return VIS_EL["m"] * VIS_EL["z"] / 2 + VIS_EL["dp"] / 2 + AJ["entraxe"]


def y_vis_az():
    """Position Y de l'axe de la vis d'azimut (entraxe avec la roue fixe)."""
    return -(VIS_AZ["m"] * VIS_AZ["z"] / 2 + VIS_AZ["dp"] / 2 + AJ["entraxe"])


def z_vis_el():
    return Z_T - entraxe_el()


def roulement_x(od, idia, w):
    return cq.Workplane("YZ").circle(od / 2).circle(idia / 2).extrude(w)


def roulement_z(od, idia, w):
    r = ring_z(od, idia, w)
    m = (od + idia) / 2
    return r.cut(ring_z(m + 1.5, m - 1.5, 0.6, w - 0.6))


def trou_z(d, x, y, z0, z1):
    """Trou d'axe Z de z0 à z1."""
    return cyl_z(d, z1 - z0, x, y, z0)


def lumiere_y(d, x, y, z0, z1, course=0.6):
    """Trou oblong selon Y (±course) : réglage de l'entraxe de la vis d'azimut."""
    return (cq.Workplane("XY").center(x, y).slot2D(d + 2 * course, d, 90).extrude(z1 - z0)
            .translate((0, 0, z0)))


def p_nema(m):
    """Moteur pas à pas : face avant en z = 0, arbre Ø5 selon +Z, corps vers -Z."""
    c, L = m["c"], m["L"]
    body = box_span(-c / 2, c / 2, -c / 2, c / 2, -L, 0).edges("|Z").chamfer(c * 0.09)
    body = body.cut(box_span(-c, c, -c, c, -L + 6, -L + 7).cut(cyl_z(c * 0.95, 3, z=-L + 5)))  # rainure d'aspect
    body = body.union(cyl_z(m["pilot"], 2)).union(cyl_z(5, m["shaft"]))
    for sx in (-1, 1):
        for sy in (-1, 1):
            body = body.cut(cyl_z(m["hole_d"], 4.5, sx * m["holes"] / 2, sy * m["holes"] / 2, -4.5))
    return body.union(box_span(-6, 6, c / 2 - 1, c / 2 + 5, -L + 2, -L + 12))     # connecteur


def p_vis(v):
    """Vis sans fin à un filet, axe Z centré, alésage Ø5 (montée sur son arbre acier).
    Version imprimée : filet non aminci (tout le jeu est pris sur la roue), tête de filet
    raccourcie (plus épaisse à imprimer), et deux moyeux qui viennent en appui sur les
    bagues intérieures des 685 (calage axial), dont un avec une vis de pression M3."""
    m, dp, L = v["m"], v["dp"], v["L"]
    ha = AJ["tete_filet"] * m
    rr, h = dp / 2 - 1.25 * m, 1.25 * m + ha
    lead = math.pi * m
    t = lead / 2 - AJ["jeu_filet"] * m
    ta = math.tan(math.radians(20))
    w_root, w_tip = t + 2 * ta * 1.25 * m, t - 2 * ta * ha
    z0 = -L / 2 - lead
    helix = cq.Wire.makeHelix(pitch=lead, height=L + 2 * lead, radius=rr, center=Vector(0, 0, z0))
    prof = cq.Workplane("XZ").polyline([(rr - 0.3, z0 - w_root / 2), (rr + h, z0 - w_tip / 2),
                                        (rr + h, z0 + w_tip / 2), (rr - 0.3, z0 + w_root / 2)]).close()
    thread = prof.sweep(cq.Workplane().add(helix), isFrenet=True)
    # noyau aussi long que le filet (des faces confondues en bout font échouer l'union), puis coupe à L
    core = cyl_z(2 * rr, L + 2 * lead + 2, z=z0 - 1)
    w = core.union(thread).intersect(cyl_z(dp + 2 * ha + 1, L, z=-L / 2))
    if AJ["impression"]:
        e = EL_VIS["palier"][0] - 0.15            # appui à 0,15 mm des bagues intérieures des 685
        x0 = v["moyeu"]
        for s in (-1, 1):
            if x0 > L / 2:                        # col au Ø du noyau jusqu'au moyeu
                w = w.union(cyl_z(2 * rr, x0 - L / 2 + 0.2, z=(L / 2 - 0.1) if s > 0 else -x0 - 0.1))
            hub = cyl_z(12, e - 0.5 - x0, z=x0 - 0.1 if s > 0 else -(e - 0.6)).union(
                cyl_z(6.5, 0.6, z=(e - 0.6) if s > 0 else -e))
            w = w.union(hub)
        zh = (x0 + e - 0.6) / 2                   # vis de pression M3 sur le moyeu côté +Z
        w = w.cut(cyl_dir(AJ["taraud_m3"], 6.5, (0, 6.5, zh), (0, -1, 0)))
    return w.cut(cyl_z(5 + AJ["serrage"], 40, z=-20))


def p_accouplement():
    a = cyl_z(19, 25).cut(cyl_z(5, 27, z=-1))
    for z0 in (8.0, 15.0):
        a = a.cut(ring_z(20, 15, 1.2, z0))                  # fentes (accouplement flexible)
    return a


R_FOND = 20.0                        # vis du fond : par-dessous, à travers le téton (têtes dans la colonne)


def p_fond_socle():
    f = cyl_z(SOCLE_OD, 5).union(ring_z(AJ["colonne"], 36, 15, -15))     # centrage dans la colonne
    for k in range(3):
        a = math.radians(120 * k)
        f = f.cut(trou_z(AJ["passage_m3"], R_FOND * math.cos(a), R_FOND * math.sin(a), -16, 6))
    # anti-rotation : vis M3 radiale à travers la colonne, vissée dans le téton
    return f.cut(cyl_dir(AJ["taraud_m3"], 6, (0, -AJ["colonne"] / 2 - 1, -8), (0, 1, 0)))


def p_socle():
    d42 = 42 + AJ["roulement"]
    s = ring_z(SOCLE_OD, SOCLE_ID, 54, 5).union(cyl_z(SOCLE_OD, 6, z=59))
    s = s.union(ring_z(50, d42, 14, 45)).union(ring_z(d42, 36, 6, 52))
    if AJ["impression"]:            # cône à 45° sous le logement du roulement bas : imprimable sans support
        cone = cq.Solid.makeCone(SOCLE_ID / 2, 21.0, 7.0, Vector(0, 0, 38), Vector(0, 0, 1))
        s = s.union(cyl_z(SOCLE_ID + 0.5, 7, z=38).cut(cq.Workplane().add(cone)))
    s = s.cut(cyl_z(d42, 8, z=58)).cut(cyl_z(36, 20, z=50))
    a = math.radians(P["phi_box"])                                      # passe-câble, vers l'unité au sol
    s = s.cut(cyl_dir(13, 10, ((SOCLE_ID / 2 - 2) * math.cos(a), (SOCLE_ID / 2 - 2) * math.sin(a), 14),
                      (math.cos(a), math.sin(a), 0)))
    for k in range(3):                                                  # fixation du fond : pilier + nervure
        a = math.radians(120 * k)
        x, y = R_FOND * math.cos(a), R_FOND * math.sin(a)
        rib = box_span(R_FOND, SOCLE_ID / 2 + 0.5, -2, 2, 5, 13).rotate((0, 0, 0), (0, 0, 1), 120 * k)
        s = s.union(cyl_z(8, 8, x, y, 5)).union(rib).cut(cyl_z(AJ["taraud_m3"], 9, x, y, 4))
    for a in ANGLES_ROUE:                                               # fixation de la roue d'azimut
        c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
        s = s.cut(trou_z(AJ["taraud_m3"], R_VIS_ROUE * c, R_VIS_ROUE * sn, 58.5, 66))
    return s


ANGLES_ROUE = (90.0, 210.0, 330.0)   # vis de la roue d'azimut
R_VIS_ROUE = 28.0                    # hors de la denture, dans la collerette du socle
Z_VOILE = 67.5                       # dessus du voile de la roue d'azimut (vis fraisées affleurantes)


def p_roue_azimut():
    """Roue d'azimut Z60, fixe, posée à plat sur le socle (dessous plan : s'imprime sans support)
    et tenue par 3 vis M3 fraisées affleurantes, sous le passage de la vis d'azimut qui roule autour."""
    r = gear_z(VIS_AZ["z"], VIS_AZ["m"], 8, AZ_VIS["zr"][0], backlash=AJ["jeu_denture"][1] / VIS_AZ["m"])
    r = r.union(ring_z(50, 36, AZ_VIS["zr"][0] - 65, 65))
    r = r.union(ring_z(SOCLE_OD, 50 - 0.5, Z_VOILE - 65, 65))                     # voile
    r = r.cut(cyl_z(36, 30, z=60))
    for a in ANGLES_ROUE:
        x, y = R_VIS_ROUE * math.cos(math.radians(a)), R_VIS_ROUE * math.sin(math.radians(a))
        r = r.cut(trou_z(AJ["passage_m3"], x, y, 64, Z_VOILE + 1))
        fr = cq.Solid.makeCone(AJ["passage_m3"] / 2, 3.2, 1.6, Vector(x, y, Z_VOILE - 1.6), Vector(0, 0, 1))
        r = r.cut(cq.Workplane().add(fr)).cut(cyl_z(6.4, 1, x, y, Z_VOILE))         # fraisure à 90°
    return r


# trous de fixation dans la plaque de la chape (x, y)
TROUS_PALIER_EL = ((-30.0, -9.0), (-30.0, 9.0))          # vis par-dessous, taraudées dans le palier
TROUS_SUPPORT_EL = ((-46.0, -52.0), (-14.0, -52.0))      # vis par-dessous, taraudées dans le support
TROUS_SUPPORT_AZ = ((-49.0, -27.0), (-41.0, -27.0))      # vis par-dessus (lumières dans la chape)
TROUS_MOYEU = tuple((18 * math.cos(math.radians(a)), 18 * math.sin(math.radians(a))) for a in (30, 150, 270))
TROUS_BAGUE = ((12.5, 0.0), (-12.5, 0.0))                # bague d'arrêt vissée en bout de moyeu


def trous_palier_az():
    return tuple((x, y_vis_az()) for x in (-16.5, 16.5))  # vis par-dessus (lumières dans la chape)


def _moyeu(z_top):
    """Moyeu d'azimut : Ø30 dans les 6806, collerette Ø34 sur la bague intérieure du 6806 haut."""
    m = cyl_z(30 + AJ["moyeu"], z_top - 45, z=45).union(cyl_z(34, 2, z=65))
    for x, y in TROUS_BAGUE:
        m = m.cut(cyl_z(AJ["taraud_m3"], 8, x, y, 44))
    return m


def p_chape():
    xi, xo = ARM_X
    zc, zt = Z_CHAPE, Z_T
    plate = box_span(-xo, xo, -ARM_R, ARM_R, zc, zc + 8)
    plate = plate.union(box_span(-60, -2, -60, -ARM_R + 1, zc, zc + 8))         # queue : les deux moteurs
    c = plate.edges("|Z").fillet(5)
    arm = (cq.Workplane("YZ").moveTo(-ARM_R, zc).lineTo(ARM_R, zc).lineTo(ARM_R, zt)
           .threePointArc((0, zt + ARM_R), (-ARM_R, zt)).close().extrude(xo - xi))
    c = c.union(arm.translate((xi, 0, 0))).union(arm.translate((-xo, 0, 0)))
    if AJ["impression"]:            # moyeu imprimé à part (sinon la chape ne tient pas à plat), vissé dessous
        for x, y in TROUS_MOYEU:
            c = c.cut(trou_z(AJ["passage_m3"], x, y, zc - 1, zc + 9))
    else:
        c = c.union(_moyeu(zc))
    c = c.cut(cyl_z(20, zc + 10 - 40, z=40))                                     # passage des câbles
    c = c.cut(cyl_x(10, 2 * xo + 2, -xo - 1, 0, zt))
    d22 = 22 + AJ["roulement"]
    c = c.cut(cyl_x(d22, 7, xo - 7, 0, zt)).cut(cyl_x(d22, 7, -xo, 0, zt))       # logements des 608
    for x, y in TROUS_PALIER_EL + TROUS_SUPPORT_EL:          # passages : vis par-dessous
        c = c.cut(trou_z(AJ["passage_m3"], x, y, zc - 1, zc + 9))
    # palier et support d'azimut accrochés sous la plaque, vis par-dessus dans des lumières :
    # on règle l'entraxe vis / roue d'azimut en les faisant glisser selon Y
    for x, y in trous_palier_az() + TROUS_SUPPORT_AZ:
        c = c.cut(lumiere_y(AJ["passage_m3"], x, y, zc - 1, zc + 9))
    return c


def p_moyeu_chape():
    """Version imprimée : moyeu d'azimut séparé, vissé sous la plaque de la chape (3 x M3)."""
    zc = Z_CHAPE
    m = _moyeu(zc - 5).union(cyl_z(42, 5, z=zc - 5))
    m = m.cut(cyl_z(20, zc + 2 - 40, z=40))
    for x, y in TROUS_MOYEU:
        m = m.cut(trou_z(AJ["taraud_m3"], x, y, zc - 6, zc + 1))
    return m


def p_bague_arret():
    """Rondelle d'arrêt sous le 6806 bas, vissée en bout de moyeu (2 x M3)."""
    b = ring_z(34, 20, 3, 42)
    for x, y in TROUS_BAGUE:
        b = b.cut(trou_z(AJ["passage_m3"], x, y, 41, 46))
    return b


def p_arbre_vis_az():
    x1 = AZ_VIS["palier"][1] + 1
    return cyl_x(5, x1 - AZ_VIS["x_joint"], AZ_VIS["x_joint"], y_vis_az(), AZ_VIS["z"])


def p_palier_vis_az():
    p0, p1 = AZ_VIS["palier"]
    y, z, zc = y_vis_az(), AZ_VIS["z"], Z_CHAPE
    d11 = B685[0] + AJ["roulement"]
    b = None
    for x0, x1 in ((p0, p1), (-p1, -p0)):
        pl = box_span(x0, x1, y - 9, y + 8, z - 7.5, zc).cut(cyl_x(d11, x1 - x0 + 2, x0 - 1, y, z))
        b = pl if b is None else b.union(pl)
    b = b.union(box_span(-p1, p1, y - 9, y + 8, zc - 5, zc))
    for x, yy in trous_palier_az():                       # taraudages, vis par-dessus la chape
        b = b.cut(trou_z(AJ["taraud_m3"], x, yy, zc - 4.5, zc + 1))
    return b


def p_support_moteur_az():
    m = MOT_AZ
    y, z, zc, xf = y_vis_az(), AZ_VIS["z"], Z_CHAPE, AZ_VIS["x_face"]
    s = box_span(xf, xf + 4, y - 16, y + 16, z - 16, zc)
    s = s.union(box_span(xf, xf + 15, y - 16, y + 7, zc - 5, zc))
    s = s.cut(cyl_x(AJ["pilote"], 10, xf - 1, y, z))
    for sy in (-1, 1):
        for sz in (-1, 1):
            s = s.cut(cyl_x(AJ["passage_m25"], 10, xf - 1, y + sy * m["holes"] / 2, z + sz * m["holes"] / 2))
    for sy in (-1, 1):                                    # lamages des têtes M2,5 sous la patte
        s = s.cut(cyl_x(6, 4, xf + 4, y + sy * m["holes"] / 2, z + m["holes"] / 2))
    for x, yy in TROUS_SUPPORT_AZ:                        # taraudages, vis par-dessus la chape
        s = s.cut(trou_z(AJ["taraud_m3"], x, yy, zc - 4.5, zc + 1))
    return s


def p_arbre_vis_el():
    y1 = EL_VIS["palier"][1] + 1
    return cyl_y(5, y1 - EL_VIS["y_joint"], -30, EL_VIS["y_joint"], z_vis_el())


def p_palier_vis_el():
    p0, p1 = EL_VIS["palier"]
    zv, zb = z_vis_el(), Z_CHAPE + 8
    d11 = B685[0] + AJ["roulement"]
    b = None
    for y0, y1 in ((p0, p1), (-p1, -p0)):
        pl = box_span(-38, -22, y0, y1, zb, Z_T - 24.5).cut(cyl_y(d11, y1 - y0 + 2, -30, y0 - 1, zv))
        b = pl if b is None else b.union(pl)
    b = b.union(box_span(-38, -22, -p1, p1, zb, zb + 5))
    for x, y in TROUS_PALIER_EL:
        b = b.cut(trou_z(AJ["taraud_m3"], x, y, zb - 1, zb + 4.5))
    return b


def p_support_moteur_el():
    m = MOT_EL
    zv, zb, yf = z_vis_el(), Z_CHAPE + 8, EL_VIS["y_face"]
    s = box_span(-54, -6, yf, yf + 4, zb, zv + 24)
    s = s.union(box_span(-54, -6, yf, yf + 22, zb, zb + 5))
    s = s.cut(cyl_y(AJ["pilote"], 6, -30, yf - 1, zv))
    for sx in (-1, 1):
        for sz in (-1, 1):
            s = s.cut(cyl_y(AJ["passage_m3"], 6, -30 + sx * m["holes"] / 2, yf - 1, zv + sz * m["holes"] / 2))
    for sx in (-1, 1):                                    # lamages des têtes M3 basses dans la semelle
        s = s.cut(cyl_y(7, 5, -30 + sx * m["holes"] / 2, yf + 4, zv - m["holes"] / 2))
    for x, y in TROUS_SUPPORT_EL:
        s = s.cut(trou_z(AJ["taraud_m3"], x, y, zb - 1, zb + 4.5))
    return s


# --- partie basculante (repère : origine sur l'axe d'élévation, X = axe, Z = normale au panneau)
def alesage_8(x0, L, d_plat=True):
    """Alésage Ø8 d'axe X ; en version imprimée, avec méplat (axe Ø8 en D) si d_plat."""
    d = 8 + AJ["serrage"]
    h = cyl_x(d, L, x0)
    if AJ["impression"] and d_plat:
        h = h.cut(box_span(x0 - 1, x0 + L + 1, -6, 6, MEPLAT + AJ["serrage"] / 2, 6))
    return h


def p_chapeau_u():
    xi, xo = U_X
    u = box_span(-xo, xo, -ARM_R, ARM_R, U_TOP[0], U_TOP[1])
    for x0, x1 in ((xi, xo), (-xo, -xi)):
        u = u.union(box_span(x0, x1, -U_Y, U_Y, U_BAS, U_TOP[1]).edges("|X and <Z").fillet(8))
    u = u.cut(alesage_8(-xo - 1, xo - xi + 2)).cut(alesage_8(xi - 1, xo - xi + 2, d_plat=False))
    for x in (-RAIL_X, RAIL_X):
        for y in (-14, 14):
            u = u.cut(cyl_z(AJ["taraud_m3"], 10, x, y, U_TOP[0] - 1))
    return u


def p_pivot_entraine():
    """Pivot gauche (acier) : serré dans le chapeau, tourne dans un 608, porte la roue d'élévation.
    Version imprimée : axe Ø8 en D, le méplat transmet le couple de la roue au chapeau."""
    p = cyl_x(8, U_X[1] + X_ROUE[1] + 2, -U_X[1]).union(cyl_x(12, 2, -U_X[1] - 2))
    if AJ["impression"]:
        p = p.cut(box_span(-U_X[1] - 3, X_ROUE[1] + 3, -6, 6, MEPLAT, 7))
    return p


def p_pivot_libre():
    return cyl_x(8, U_X[1] - ARM_X[0] + 1, ARM_X[0] - 1).union(cyl_x(12, 2, U_X[1]))


def p_roue_elevation():
    g = gear_x(VIS_EL["z"], VIS_EL["m"], X_ROUE[1] - X_ROUE[0], X_ROUE[0],
               backlash=AJ["jeu_denture"][0] / VIS_EL["m"])
    g = g.union(cyl_x(16, 4, X_ROUE[1])).cut(alesage_8(X_ROUE[0] - 2, 20))
    for k in range(5):
        a = math.radians(72 * k)
        g = g.cut(cyl_x(7, 12, X_ROUE[0] - 2, 15 * math.cos(a), 15 * math.sin(a)))
    return g


def p_rail():
    """Rail alu (non imprimé) : vissé sur le chapeau par-dessus, têtes noyées sous le panneau ;
    taraudé M3 à ses extrémités pour le cadre du panneau."""
    r = box_span(-6, 6, -P["pan_H"] / 2, P["pan_H"] / 2, U_TOP[1], P["pan_back"])
    for y in (-14, 14):
        r = r.cut(cyl_z(3.4, 20, 0, y, U_TOP[1] - 1)).cut(cyl_z(6.2, 4, 0, y, P["pan_back"] - LAMAGE_RAIL))
    for y in (-P["pan_H"] / 2 + 6, P["pan_H"] / 2 - 6):
        r = r.cut(cyl_z(2.5, 10, 0, y, P["pan_back"] - 9))
    return r


LAMAGE_RAIL = 3.5                    # profondeur du lamage des têtes de vis dans les rails


# --- visserie de la tête : vis CHC modélisées tête + noyau (Ø du fond de filet), pour que le
#     contrôle d'interférences vérifie aussi l'accès des têtes et la longueur des vis
def p_vis_chc(d, L):
    tete_d, tete_h, noyau = (5.5, 3.0, 2.4) if d == 3 else (4.5, 2.5, 2.0)
    return cyl_z(tete_d, tete_h).union(cyl_z(noyau, L, z=-L))


def p_vis_fraisee(d, L):
    """Vis à tête fraisée (ISO 10642) : dessus de tête en z = 0, longueur hors tout L."""
    tete = cq.Solid.makeCone(d / 2, 2.9, 1.55, Vector(0, 0, -1.55), Vector(0, 0, 1))
    return cq.Workplane().add(tete).union(cyl_z(0.8 * d, L, z=-L))


def loc_vis(p, d):
    """Vis posée sous tête au point p, enfoncée selon la direction d."""
    n = Vector(*d) * -1
    xd = Vector(1, 0, 0) if abs(n.x) < 0.9 else Vector(0, 1, 0)
    return Location(cq.Plane(origin=Vector(*p), xDir=xd.cross(n).cross(n) * -1, normal=n))


def visserie():
    """[(repère, type, point d'appui sous tête, direction d'insertion)] ; repères : 'fixe' et
    'chape' (repère tête), 'bascule' (repère de la partie basculante)."""
    v = []
    for k in range(3):                    # fond -> socle, par-dessous (têtes dans la colonne)
        a = math.radians(120 * k)
        v.append(("fixe", "M3x25", (R_FOND * math.cos(a), R_FOND * math.sin(a), -15), (0, 0, 1)))
    for a in ANGLES_ROUE:                 # roue d'azimut -> socle, vis fraisées affleurantes
        c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
        v.append(("fixe", "M3x8F", (R_VIS_ROUE * c, R_VIS_ROUE * sn, Z_VOILE), (0, 0, -1)))
    v.append(("fixe", "M3x6", (0, -P["col_od"] / 2, -8), (0, 1, 0)))     # anti-rotation, à travers la colonne
    for x, y in TROUS_BAGUE:              # rondelle d'arrêt -> moyeu
        v.append(("chape", "M3x8", (x, y, 42), (0, 0, 1)))
    if AJ["impression"]:                  # chape -> moyeu imprimé
        for x, y in TROUS_MOYEU:
            v.append(("chape", "M3x12", (x, y, Z_CHAPE + 8), (0, 0, -1)))
    for x, y in TROUS_PALIER_EL + TROUS_SUPPORT_EL:       # par-dessous la chape
        v.append(("chape", "M3x12", (x, y, Z_CHAPE), (0, 0, 1)))
    for x, y in trous_palier_az() + TROUS_SUPPORT_AZ:     # par-dessus la chape
        v.append(("chape", "M3x10", (x, y, Z_CHAPE + 8), (0, 0, -1)))
    zv, yf = z_vis_el(), EL_VIS["y_face"]
    for sx in (-1, 1):                    # moteurs sur leurs supports
        for sz in (-1, 1):
            v.append(("chape", "M3x8", (-30 + sx * MOT_EL["holes"] / 2, yf + 4, zv + sz * MOT_EL["holes"] / 2),
                      (0, -1, 0)))
            v.append(("chape", "M2.5x8", (AZ_VIS["x_face"] + 4, y_vis_az() + sx * MOT_AZ["holes"] / 2,
                                          AZ_VIS["z"] + sz * MOT_AZ["holes"] / 2), (-1, 0, 0)))
    for x in (-RAIL_X, RAIL_X):           # rails -> chapeau, têtes noyées
        for y in (-14, 14):
            v.append(("bascule", "M3x14", (x, y, P["pan_back"] - LAMAGE_RAIL), (0, 0, -1)))
    return v


def nom_vis(t):
    return f"Vis_FHC_{t[:-1]}" if t.endswith("F") else f"Vis_CHC_{t}"


def add_visserie(assy, repere):
    for i, (rp, t, p, d) in enumerate(visserie()):
        if rp == repere:
            add(assy, nom_vis(t), loc_vis(p, d), f"{nom_vis(t)}_{i}")


# ---------------------------------------------------------------------------
# PIÈCES — PANNEAU (repère : origine sur l'axe d'élévation,
#   X = axe d'élévation, Z = normale au panneau, cellules côté +Z)
# ---------------------------------------------------------------------------
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
    return b.union(cyl_y(12, 10, 0, 85, z0 - 7.2))


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
    """Faisceau : sort du passe-câble du socle (vers l'unité au sol), descend entre deux
    jambes et rejoint les connecteurs de l'unité de contrôle."""
    a = math.radians(P["phi_box"])
    c, s = math.cos(a), math.sin(a)
    r_end = P["r_box"] - BOX_L / 2 - 25
    z0 = Z_EMB + 14
    rz = [(SOCLE_ID / 2 + 0.5, z0), (55, z0 - 6), (85, z0 - 48), (110, z0 - 118), (160, z0 - 238),
          (260, z0 - 388), (380, 35), (500, 10), (r_end - 120, 10), (r_end - 50, 50), (r_end, 70)]
    pts = [Vector(r * c, r * s, z) for r, z in rz]
    tans = [Vector(c, s, 0), Vector(c, s, 0)]
    path = cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, tangents=tans)])
    prof = cq.Workplane(cq.Plane(origin=pts[0], xDir=(0, 0, 1), normal=(c, s, 0))).circle(6)
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
    build_tripod_parts()
    build_head_parts()


def build_tripod_parts():
    reg("Colonne_Centrale", p_colonne(), "Al 7075-T73", COL["alu"], "Colonne centrale Ø50x2 anodisée dur")
    reg("Collier_Superieur", p_collier_sup(), "Ti-6Al-4V", COL["ti"], "Moyeu d'articulation des jambes")
    reg("Collier_Inferieur", p_collier_inf(), "Ti-6Al-4V", COL["ti"], "Collier coulissant des entretoises")
    reg("Ferrure_Jambe", p_ferrure_jambe(), "Ti-6Al-4V", COL["ti"], "Ferrure d'articulation de jambe")
    reg("Axe_Articulation", p_axe(6, 36, 10), "Ti-6Al-4V", COL["alu_d"], "Axe Ø6 revêtu MoS2")
    reg("Tube_Jambe_Superieur", p_tube_sup(), "Al 7075-T73", COL["alu"], "Tube Ø25x1,5 anodisé dur")
    reg("Bague_Blocage", p_bague_blocage(), "Ti-6Al-4V", COL["orange"], "Bague de blocage télescopique")
    reg("Tube_Jambe_Inferieur", p_tube_inf(), "Al 7075-T73", COL["alu"], "Tube coulissant Ø20x1,5")
    reg("Embout_Rotule", p_embout_rotule(), "Ti-6Al-4V", COL["ti"], "Embout à rotule Ø22")
    reg("Bride_Entretoise", p_bride_entretoise(), "Ti-6Al-4V", COL["ti"], "Bride de fixation d'entretoise")
    reg("Patin", p_patin(), "Al 7075-T73", COL["alu_d"], "Patin Ø120 à crampons + logement de rotule")
    reg("Ancrage_Helicoidal", p_ancrage(), "Ti-6Al-4V", COL["orange"],
        "Vis d'ancrage hélicoïdale Ø60, 400 mm dans le régolithe")
    reg("Axe_Entretoise", p_axe(5, 21, 8), "Ti-6Al-4V", COL["alu_d"], "Axe Ø5")


def build_head_parts():
    # tête rotative à vis sans fin (repère tête), en cotes réelles ou imprimées (voir AJUSTEMENTS)
    imp = AJ["impression"]

    def mat(reel):
        return "PETG" if imp else reel
    reg("Fond_Socle", p_fond_socle(), mat("Al 6061-T6"), COL["socle"], "Fond du socle, centrage dans la colonne")
    reg("Socle", p_socle(), mat("Al 6061-T6"), COL["socle"], "Socle Ø62 : roulements d'azimut, passe-câble")
    reg("Roulement_6806", roulement_z(42, 30, 7), "Acier 440C", COL["steel"], "Roulement d'azimut 6806")
    reg("Roue_Azimut_Fixe", p_roue_azimut(), mat("Bronze CuSn12"), COL["brass"],
        f"Roue d'azimut m{format(VIS_AZ['m'], 'g').replace('.', ',')} Z{VIS_AZ['z']}, fixée sur le socle")
    reg("Chape", p_chape(), mat("Al 6061-T6"), COL["chape"], "Chape en U (tourne en azimut, porte les moteurs)")
    if imp:
        reg("Moyeu_Chape", p_moyeu_chape(), "PETG", COL["chape"], "Moyeu d'azimut, vissé sous la chape")
    reg("Bague_Arret_Moyeu", p_bague_arret(), mat("Acier inox 17-4PH"), COL["steel"],
        "Rondelle d'arrêt du moyeu (2 x M3)")
    reg("Roulement_608", roulement_x(22, 8, 7), "Acier 440C", COL["steel"], "Roulement d'élévation 608")
    reg("Roulement_685", roulement_x(B685[0], B685[1], B685[2]), "Acier 440C", COL["steel"],
        "Roulement 685 (arbres des vis)")
    reg("Vis_Azimut", p_vis(VIS_AZ), mat("Acier inox 17-4PH"), COL["steel"],
        f"Vis sans fin d'azimut m{format(VIS_AZ['m'], 'g').replace('.', ',')} Ø{VIS_AZ['dp']:.0f}, un filet")
    reg("Arbre_Vis_Azimut", p_arbre_vis_az(), "Acier inox 17-4PH", COL["steel"], "Arbre Ø5 de la vis d'azimut")
    reg("Palier_Vis_Azimut", p_palier_vis_az(), mat("Al 6061-T6"), COL["chape"], "Palier de la vis d'azimut")
    reg("Support_Moteur_Azimut", p_support_moteur_az(), mat("Al 6061-T6"), COL["chape"],
        "Support du moteur d'azimut")
    reg("Moteur_Azimut_NEMA11", p_nema(MOT_AZ), "moteur", COL["nema"], f"Moteur pas à pas d'azimut : {MOT_AZ['nom']}")
    reg("Vis_Elevation", p_vis(VIS_EL), mat("Acier inox 17-4PH"), COL["steel"],
        f"Vis sans fin d'élévation m{format(VIS_EL['m'], 'g').replace('.', ',')} Ø{VIS_EL['dp']:.0f}, un filet")
    reg("Arbre_Vis_Elevation", p_arbre_vis_el(), "Acier inox 17-4PH", COL["steel"], "Arbre Ø5 de la vis d'élévation")
    reg("Palier_Vis_Elevation", p_palier_vis_el(), mat("Al 6061-T6"), COL["chape"], "Palier de la vis d'élévation")
    reg("Support_Moteur_Elevation", p_support_moteur_el(), mat("Al 6061-T6"), COL["chape"],
        "Support du moteur d'élévation")
    reg("Moteur_Elevation_NEMA17", p_nema(MOT_EL), "moteur", COL["nema"],
        f"Moteur pas à pas d'élévation : {MOT_EL['nom']}")
    reg("Accouplement", p_accouplement(), "Al 7075-T73", COL["coupler"], "Accouplement flexible 5/5")
    reg("Chapeau_U", p_chapeau_u(), mat("Al 6061-T6"), COL["u"], "Chapeau en U renversé porte-panneau")
    reg("Pivot_Entraine", p_pivot_entraine(), "Acier inox 17-4PH", COL["steel"],
        "Pivot Ø8 portant la roue d'élévation" + (" (axe en D)" if imp else ""))
    reg("Pivot_Libre", p_pivot_libre(), "Acier inox 17-4PH", COL["steel"], "Pivot Ø8 libre")
    reg("Roue_Elevation", p_roue_elevation(), mat("Bronze CuSn12"), COL["brass"],
        f"Roue d'élévation m{format(VIS_EL['m'], 'g').replace('.', ',')} Z{VIS_EL['z']}")
    reg("Rail_Panneau", p_rail(), "Al 6061-T6", COL["alu_d"], "Rail 12 x 13 vissé sur le cadre du panneau")
    for t in sorted({v[1] for v in visserie()}):
        d, L = t[1:].rstrip("F").split("x")
        if t.endswith("F"):
            reg(nom_vis(t), p_vis_fraisee(float(d), float(L)), "Acier (visserie)", COL["steel"],
                f"Vis à tête fraisée {t[:-1].replace('.', ',')} (ISO 10642)")
        else:
            reg(nom_vis(t), p_vis_chc(float(d), float(L)), "Acier (visserie)", COL["steel"],
                f"Vis CHC {t.replace('.', ',')} (ISO 4762)")
    # panneau
    reg("Cadre_Panneau", p_cadre_pv(), "Al 6063-T5", COL["alu"], "Cadre alu du panneau 356x253x30")
    reg("Lamine_PV", p_lamine(), "Verre 3,2 mm + EVA + backsheet (eq)", COL["pv_bg"],
        "Verre + EVA + face arrière")
    cells, cw, ch = p_cellules()
    reg("Cellules_PV", cells, "Silicium polycristallin", COL["pv"],
        f"{P['cell_nx']*P['cell_ny']} cellules {cw:.1f}x{ch:.1f}")
    reg("Boite_Jonction", p_boite_jonction(), "PPO (boîte de jonction)", COL["black"],
        "Boîte de jonction + presse-étoupe")
    # sol
    reg("Unite_Controle_Corps", p_unite_corps(), "Al 6061-T6", COL["gold"],
        "Unité de contrôle / stockage sous MLI (batterie, ESP32, drivers TMC2209)")
    reg("Unite_Controle_Radiateur", p_unite_radiateur(), "Al 6061-T6", COL["white"],
        "Radiateur zénithal (peinture blanche / OSR)")
    reg("Faisceau_Cables", p_faisceau(), "PTFE/cuivre (eq)", COL["black"], "Faisceau puissance + données Ø12")


def add(assy, name, loc=None, inst=None):
    wp, mat, col, _ = PARTS[name]
    assy.add(wp, name=inst or name, loc=loc or Location(), color=col)


def strut_geom(phi):
    """Points d'axe (repère monde Z-up) d'une entretoise."""
    a = math.radians(phi)
    rl = P["r_lower_pin"]
    p_in = (rl * math.cos(a), rl * math.sin(a), P["z_lower_collar"])
    p_out = leg_point(phi, (0, -P["lug_off"], -P["s_clamp"]))
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
        # patin + vis d'ancrage
        pl = trans(P["r_foot"] * math.cos(a), P["r_foot"] * math.sin(a), 0) * rot((0, 0, 1), phi)
        add(t, "Patin", pl, f"Patin_{i}")
        add(t, "Ancrage_Helicoidal", pl * trans(P["anchor_x"], 0, 0), f"Ancrage_{i}")
        # entretoise
        p_in, p_out = strut_geom(phi)
        rr = math.hypot(p_out[0], p_out[1]) - P["r_lower_pin"]
        dz = p_out[2] - p_in[2]
        L = math.hypot(rr, dz)
        gam = math.degrees(math.atan2(-rr, dz))
        name = f"Entretoise_{i}"
        if i == 1:      # longueur fonction de l'angle des jambes : recréée à chaque montage
            PARTS["Entretoise"] = (p_entretoise(L), "Al 7075-T73", COL["alu"], "Entretoise Ø12x1")
        wp, mat, col, _ = PARTS["Entretoise"]
        sl = trans(*p_in) * rot((0, 0, 1), phi - 90) * rot((1, 0, 0), gam)
        t.add(wp, name=name, loc=sl, color=col)
        add(t, "Axe_Entretoise", sl, f"Axe_Entretoise_Int_{i}")
        add(t, "Axe_Entretoise", sl * trans(0, 0, L), f"Axe_Entretoise_Ext_{i}")
    return t


PANEL_PARTS = ("Cadre_Panneau", "Lamine_PV", "Cellules_PV", "Boite_Jonction")


def build_panel(with_panel=True):
    """Partie qui tourne en élévation (repère : origine sur l'axe d'élévation)."""
    p = cq.Assembly(name="SA_Panneau")
    add(p, "Chapeau_U")
    add(p, "Pivot_Entraine")
    add(p, "Pivot_Libre")
    add(p, "Roue_Elevation")
    add(p, "Rail_Panneau", trans(RAIL_X, 0, 0), "Rail_Panneau_1")
    add(p, "Rail_Panneau", trans(-RAIL_X, 0, 0), "Rail_Panneau_2")
    add_visserie(p, "bascule")
    if with_panel:
        for n in PANEL_PARTS:
            add(p, n)
    return p


def build_head(az, el, with_panel=True):
    """Partie qui tourne en azimut (repère tête) : chape, vis, moteurs, chapeau et panneau."""
    h = cq.Assembly(name="SA_Tete_Orientable")
    add(h, "Chape")
    if AJ["impression"]:
        add(h, "Moyeu_Chape")
    add(h, "Bague_Arret_Moyeu")
    add(h, "Roulement_608", trans(ARM_X[1] - 7, 0, Z_T), "Roulement_608_1")
    add(h, "Roulement_608", trans(-ARM_X[1], 0, Z_T), "Roulement_608_2")
    # azimut : vis le long de X qui roule autour de la roue fixe, NEMA 11 en bout côté -X
    a, ya = AZ_VIS, y_vis_az()
    add(h, "Palier_Vis_Azimut")
    add(h, "Arbre_Vis_Azimut")
    for i, x0 in enumerate((a["palier"][0], -a["palier"][1]), 1):
        add(h, "Roulement_685", trans(x0, ya, a["z"]), f"Roulement_685_Az_{i}")
    add(h, "Vis_Azimut", trans(0, ya, a["z"]) * rot((0, 1, 0), 90)
        * rot((0, 0, 1), PHASES[MODE]["az"] + VIS_AZ["z"] * az))
    add(h, "Accouplement", trans(a["x_joint"] - 12.5, ya, a["z"]) * rot((0, 1, 0), 90), "Accouplement_Az")
    add(h, "Support_Moteur_Azimut")
    add(h, "Moteur_Azimut_NEMA11", trans(a["x_face"], ya, a["z"]) * rot((0, 1, 0), 90))
    # élévation : vis le long de Y sous la roue, NEMA 17 court à l'arrière (côté opposé au panneau)
    zv = z_vis_el()
    add(h, "Palier_Vis_Elevation")
    add(h, "Arbre_Vis_Elevation")
    for i, y0 in enumerate((EL_VIS["palier"][0], -EL_VIS["palier"][1]), 1):
        add(h, "Roulement_685", trans(-30, y0, zv) * rot((0, 0, 1), 90), f"Roulement_685_El_{i}")
    add(h, "Vis_Elevation", trans(-30, 0, zv) * rot((1, 0, 0), -90)
        * rot((0, 0, 1), PHASES[MODE]["el"] - VIS_EL["z"] * (el - EL_REF)))
    add(h, "Accouplement", trans(-30, EL_VIS["y_joint"] - 12.5, zv) * rot((1, 0, 0), -90), "Accouplement_El")
    add(h, "Support_Moteur_Elevation")
    add(h, "Moteur_Elevation_NEMA17", trans(-30, EL_VIS["y_face"], zv) * rot((1, 0, 0), -90))
    add_visserie(h, "chape")
    h.add(build_panel(with_panel), name="SA_Panneau", loc=trans(0, 0, Z_T) * rot((1, 0, 0), el - 90.0))
    return h


def build_head_fixed():
    """Partie fixe de la tête (repère tête) : socle, roulements d'azimut, roue d'azimut."""
    f = cq.Assembly(name="SA_Tete_Fixe")
    add(f, "Fond_Socle")
    add(f, "Socle")
    add(f, "Roulement_6806", trans(0, 0, Z_ROUL1), "Roulement_6806_1")
    add(f, "Roulement_6806", trans(0, 0, Z_ROUL2), "Roulement_6806_2")
    add(f, "Roue_Azimut_Fixe")
    add_visserie(f, "fixe")
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
    head = TO_YUP * trans(0, 0, Z_EMB)
    root.add(build_head_fixed(), name="SA_Tete_Fixe", loc=head)
    root.add(build_head(az, el), name="SA_Tete_Orientable", loc=head * rot((0, 0, 1), az))
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
    aliases = {"Patin_": "Patin", "Ancrage_": "Ancrage_Helicoidal", "Axe_Entretoise_": "Axe_Entretoise"}
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


def min_clearance(moving, fixed, cutoff=40.0):
    """Distance mini entre deux groupes ; les paires dont les boîtes englobantes sont
    à plus de 'cutoff' mm ne sont pas calculées (résultat alors = cutoff)."""
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.Extrema import Extrema_ExtFlag_MIN
    best = (cutoff, "> seuil", "> seuil")
    for na, a in moving:
        ba = a.BoundingBox()
        for nb, b in fixed:
            bb = b.BoundingBox()
            gap = max(ba.xmin - bb.xmax, bb.xmin - ba.xmax, ba.ymin - bb.ymax,
                      bb.ymin - ba.ymax, ba.zmin - bb.zmax, bb.zmin - ba.zmax)
            if gap > best[0]:
                continue
            ext = BRepExtrema_DistShapeShape()      # minimum seul : bien plus rapide
            ext.LoadS1(a.wrapped)
            ext.LoadS2(b.wrapped)
            ext.SetFlag(Extrema_ExtFlag_MIN)
            ext.SetMultiThread(True)
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
    print(f"Angle de basculement mini (sans ancrage) : {tipping(cgt):.1f}°")
    pad_area = math.pi * (P["pad_d"] / 2000) ** 2
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
        print("\n(contrôle de garde sur toute la plage : relancer avec --balayage)")
        return

    print("\nContrôle de garde sur toute la plage de mouvement :")
    fixed_names = ("SA_Trepied", "SA_Tete_Fixe", "SA_Unite_Sol", "SA_Faisceau")
    tilt_itf = ("Pivot_", "Roue_Elevation")       # pivots dans leurs roulements, roue en prise avec la vis
    contacts = {"Chape": ("Roulement_6806",), "Bague_Arret_Moyeu": ("Roulement_6806",),
                "Vis_Azimut": ("Roue_Azimut_Fixe",)}     # moyeu dans ses roulements, vis en prise
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
            body = [(n, s) for n, s in panel if not n.split("/")[-1].startswith(tilt_itf)]
            roue = [(n, s) for n, s in panel if n.split("/")[-1].startswith("Roue_Elevation")]
            keep("panneau", min_clearance(body, fixed + head), az, el)
            keep("interface", min_clearance(roue, [x for x in head if "Vis_Elevation" in x[0]]), az, el)
            if el == 0.0:
                for n, s in head:
                    fx = [x for x in fixed if part_key(x[0]) not in contacts.get(part_key(n), ())]
                    keep("tete", min_clearance([(n, s)], fx), az, el)

    labels = {"panneau": "Panneau + chapeau <-> toute structure",
              "interface": "Engrènement roue d'élévation / vis (jeu de denture)",
              "tete": "Chape, moteurs, vis <-> partie fixe (socle, trépied, faisceau)"}
    for tag, w in worst.items():
        print(f"  {labels[tag]} : garde mini {w[0]:.1f} mm "
              f"({w[1].split('/')[-1]} / {w[2].split('/')[-1]}, az={w[3]}°, él={w[4]}°)")


if __name__ == "__main__":
    main()
