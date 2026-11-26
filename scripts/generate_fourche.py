#!/usr/bin/env python3
"""
Cas terrestre : tête à fourche, moteurs 28BYJ-48, tout imprimé en PETG (sauf le plateau, les tiges et la visserie).

Le panneau pivote autour de son plan médian, sur deux tiges d'acier Ø8 (roulements 608) portées par les deux
bras d'une fourche : son centre de gravité est à moins de 10 mm de l'axe, donc sans contrepoids, et un 28BYJ-48
suffit. Vis sans fin et roues dentées (100 dents en élévation, 120 en azimut, module 0,8) en PETG.

Réutilise les fonctions de generate_tracker.py (roulements, vis sans fin, roues, paliers, supports moteur,
moteur 28BYJ-48, panneau et capteur solaire).

Écrit dans « Fichiers 3D (CAO)/Cas Terrestre (démonstration)/ » :
  - Tete_Rotative_Fourche.step : la tête, avec visserie, inserts et tiges ;
  - Demo_Trepied.step : la tête sur le trépied, avec le lest ;
  - a_imprimer/ : les pièces imprimées, orientées pour l'impression (STL + STEP) ;
  - pieces_metal/ : le plateau d'aluminium de 5 mm (STEP + DXF) et les tiges (cotes dans le README).
Contrôles : interférences, prise des vis, garde du panneau, couples, stabilité du trépied.

Utilisation : python scripts/generate_fourche.py [--trepied] [--rien-ecrire]
"""
import math
import os
import sys

import cadquery as cq
from cadquery import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_tracker as G
import generate_tete_vis_sans_fin as T
from generate_tracker import box_span, cyl_x, cyl_z, trans, rot

OUT = os.path.join(G.RACINE, "Fichiers 3D (CAO)", "Cas Terrestre (démonstration)")
OUT_IMPR = os.path.join(OUT, "a_imprimer")
OUT_METAL = os.path.join(OUT, "pieces_metal")

Z_EL, Z_AZ = 100, 120                    # dents des roues d'élévation et d'azimut (module 0,8)
ZT = 300.0                               # hauteur de l'axe d'élévation (repère tête) : le panneau, long de 356 mm,
                                         # pend de 178 mm sous l'axe et doit passer au-dessus du plateau
PLAQUE = (92.0, 97.0)                    # plateau en aluminium de 5 mm, sous lequel passent les vis des bras
HW = 126.5                               # demi-largeur du panneau le long de l'axe d'élévation (côté de 253 mm)
E_FERR, E_MOY = 10.0, 8.0                # ferrure : plaque de 10 mm sur le cadre, moyeu de 8 mm
E_B = 9.0                                # épaisseur des bras
X_I = HW + E_FERR + E_MOY + 0.5          # face intérieure des bras (x = ±145) : 0,5 mm de jeu axial de chaque côté
X_E = X_I + E_B                          # face extérieure (x = ±154)
XC_EL = 163.0                            # centre de la roue d'élévation (x), à 1 mm du palier de la vis
DX_EL = XC_EL + 30.0                     # le bloc d'élévation du projet (x = -30) est décalé à x = XC_EL
X_SH = XC_EL + 24.0                      # fin de l'étagère (semelle du support moteur : ±24 mm)
D_TIGE = 8.0                             # tiges d'acier Ø8, roulements 608
Y_ARM = (-35.0, 42.0)                    # largeur des bras (le support moteur d'élévation passe à y < -40)
Y_FERR, Z_FERR = (-15.0, 15.0), (-7.0, 3.0)      # vis des ferrures dans le cadre (y, z, repère panneau)
CAPTEUR = -1                             # capteur solaire sur le petit côté haut (x local -1 du cadre)
DEC_PAN = -(G.P["pan_back"] + G.P["pan_T"] / 2)  # centre du cadre -> axe d'élévation
ECROU_X = HW - 1.5                       # face extérieure des écrous, dans le cadre
X_GRAIN = 4.0                            # moyeux : vis de pression à r = 10 (rayon du moyeu)


def regler():
    G.set_ajustements("petg")
    G.set_variante("28byj")
    G.VIS_EL = dict(m=0.8, z=Z_EL, dp=12.0, L=9.0, moyeu=8.0)
    G.VIS_AZ = dict(m=0.8, z=Z_AZ, dp=12.0, L=9.0, moyeu=8.0)
    G.Z_T = ZT
    G._maj_inserts()


# ---------------------------------------------------------------------------
# PIÈCES NOUVELLES

def trou_insert(wp, pt, d, genre="C"):
    i = G.INSERT[genre]
    v = Vector(*d)
    return wp.cut(G.cyl_dir(i["d_trou"], i["prof"] + 1.0, tuple(Vector(*pt) - v), d))


def p_ferrure(sg):
    """Ferrure du panneau (repère panneau) : plaque de 10 mm sur le grand côté du cadre, 4 vis M3 noyées,
    moyeu Ø20 pour la tige Ø8 (collée si on veut, bloquée par une vis de pression)."""
    x0, x1 = sorted((sg * HW, sg * (HW + E_FERR)))
    f = box_span(x0, x1, -22, 22, -14.5, 14.5).edges("|X").fillet(4)
    h0, h1 = sorted((sg * (HW + E_FERR), sg * (HW + E_FERR + E_MOY)))
    f = f.union(cyl_x(20.0, h1 - h0, h0, 0, 0))
    f = f.cut(cyl_x(D_TIGE + 0.1, 40, min(sg * (HW - 1), sg * (HW + 25)), 0, 0))
    for y in Y_FERR:
        for z in Z_FERR:
            xs = sg * (HW + 7.0)                  # fond du lamage : tête noyée dans la plaque
            a, b = sorted((sg * (HW - 1.0), xs))
            f = f.cut(cyl_x(G.AJ["passage_m3"], b - a + 1, a - 1, y, z))
            a2, b2 = sorted((xs, sg * (HW + E_FERR + 1.0)))
            f = f.cut(cyl_x(6.2, b2 - a2 + 1, a2, y, z))
    xg = sg * (HW + E_FERR + E_MOY / 2)           # vis de pression sur le moyeu
    f = trou_insert(f, (xg, 0, 10.0), (0, 0, -1))
    f = f.cut(G.cyl_dir(3.2, 4.0, (xg, 0, 10.0 - 3.8), (0, 0, -1)))
    return f


def p_roue_el():
    """Roue d'élévation Z100 (module 0,8), en x = 159..167, moyeu Ø20 jusqu'à 175 avec vis de pression."""
    xr = XC_EL - 4.0                             # roue de 8 mm centrée sur XC_EL
    g = G.gear_x(Z_EL, 0.8, 8.0, xr, backlash=G.AJ["jeu_denture"][0] / 0.8)
    g = g.union(cyl_x(20.0, 16.0, xr, 0, 0))
    g = g.cut(cyl_x(D_TIGE + 0.1, 20.0, xr - 1, 0, 0))
    for k in range(6):
        a = math.radians(60 * k)
        g = g.cut(cyl_x(8, 10, xr - 1, 22 * math.cos(a), 22 * math.sin(a)))
    xg = xr + 12.0
    g = trou_insert(g, (xg, 0, 10.0), (0, 0, -1))
    g = g.cut(G.cyl_dir(3.2, 4.0, (xg, 0, 10.0 - 3.8), (0, 0, -1)))
    return g, xr


def colonnes_pied(sg):
    """x (en valeur absolue) des deux colonnes de vis qui fixent un bras sur le plateau.
    Bras gauche : semelle vers l'intérieur (il s'imprime sur sa face extérieure) ; bras droit : vers l'extérieur
    (il s'imprime sur sa face intérieure, comme son étagère)."""
    return (X_I - 8.0, X_I + 4.5) if sg < 0 else (X_E - 5.0, X_E + 8.0)


def positions_pied(sg):
    return [(sg * x, y) for x in colonnes_pied(sg) for y in (-17.0, 17.0)]


def rainure_foot(wp, sg, positions):
    for x, y in positions:
        wp = trou_insert(wp, (x, y, PLAQUE[1]), (0, 0, 1))
    return wp


def p_bras(sg, zb):
    """Bras de la fourche (sg = +1 : droit, avec l'étagère de l'entraînement d'élévation ; -1 : gauche). Plaque de
    9 mm avec un seul roulement 608, comme à gauche : montage symétrique. Semelle de 6 mm vissée sur le plateau."""
    zh = ZT + 22
    xa, xb = sorted((sg * X_I, sg * X_E))
    b = box_span(xa, xb, Y_ARM[0], Y_ARM[1], PLAQUE[1], zh).edges("|X and >Z").fillet(20)
    if sg < 0:
        xf0, xf1 = sorted((sg * (X_I - 16.0), sg * X_E))          # semelle vers l'intérieur
    else:
        xf0, xf1 = sorted((sg * X_I, sg * (X_E + 15.0)))          # semelle vers l'extérieur
    b = b.union(box_span(xf0, xf1, -26, 26, PLAQUE[1], PLAQUE[1] + 6))
    b = rainure_foot(b, sg, positions_pied(sg))
    # alésages : tige Ø8 (Ø9 de jeu) et logement du roulement 608 (Ø22 + jeu d'impression), enfoncé depuis l'intérieur
    r608 = G.ROULEMENTS["608"]
    dr = r608["D"] + G.AJ["roulement"]
    xin0, xin1 = sorted((sg * (X_I - 1.0), sg * (X_E + 1.0)))
    b = b.cut(cyl_x(D_TIGE + 1.0, xin1 - xin0, xin0, 0, ZT))
    a, c = sorted((sg * (X_I - 0.5), sg * (X_I + r608["B"] + 0.3)))
    b = b.cut(cyl_x(dr, c - a, a, 0, ZT))
    if sg > 0:
        # étagère portant le palier et le support moteur d'élévation : de l'arm à y = -35, puis une avancée jusqu'à
        # y = -62 sous le support (qui est hors du bras), avec deux nervures contre le bras
        e = 7.0
        b = b.union(box_span(X_E, X_SH, -35.0, 30.0, zb - e, zb))
        b = b.union(box_span(XC_EL - 24.0, X_SH, -62.0, -35.0, zb - e, zb))
        for yy in (-35.0, 24.0):
            nerv = (cq.Workplane("XZ").polyline([(X_E, zb - e), (X_E, zb - e - 45), (X_E + 30, zb - e)]).close()
                    .extrude(-6).translate((0, yy, 0)))
            b = b.union(nerv)
        for x, y in G.TROUS_PALIER_EL + G.TROUS_SUPPORT_EL:
            b = b.cut(cyl_z(G.AJ["passage_m3"], e + 2, x + DX_EL, y, zb - e - 1))
    return b


def p_plateau():
    """Plateau d'aluminium de 5 mm (découpe laser) : bloc central (moyeu et entraînement d'azimut) et barre qui porte les
    deux bras, de x = -157 à +171 (le reste de la structure est dans 350 mm de large)."""
    z0, z1 = PLAQUE
    pl = box_span(-80, 80, -90, 48, z0, z1).edges("|Z").fillet(6).union(
        box_span(-157, 171, -30, 30, z0, z1).edges("|Z").fillet(6))
    pl = pl.cut(cyl_z(G.D_PASSAGE_MOYEU, 10, 0, 0, z0 - 1))
    for x, y in G.TROUS_MOYEU:
        pl = pl.cut(cyl_z(G.AJ["passage_m3"], 10, x, y, z0 - 1))
    for x, y in G.trous_palier_az() + G.TROUS_SUPPORT_AZ:
        pl = pl.cut(G.lumiere_y(G.AJ["passage_m3"], x, y, z0 - 1, z1 + 1))
    for sg in (-1, 1):
        for x, y in positions_pied(sg):
            pl = pl.cut(cyl_z(G.AJ["passage_m3"], 10, x, y, z0 - 1))
    return pl


def p_cadre():
    """Cadre du panneau (celui de generate_tracker.py, sans les trous des rails), avec les 8 trous Ø3,4 des ferrures
    dans les grands côtés (le cadre est ensuite tourné de 90° : l'axe d'élévation suit le côté de 253 mm) et les 2
    trous de l'équerre du capteur dans le petit côté x = -L/2."""
    L, H, T_, z0 = G.P["pan_L"], G.P["pan_H"], G.P["pan_T"], G.P["pan_back"]
    lip, w = 12.0, 1.5
    f = box_span(-L / 2, L / 2, -H / 2, H / 2, z0, z0 + T_)
    f = f.cut(box_span(-L / 2 + w, L / 2 - w, -H / 2 + w, H / 2 - w, z0 + w, z0 + T_ - w))
    f = f.cut(box_span(-L / 2 + lip, L / 2 - lip, -H / 2 + lip, H / 2 - lip, z0 + T_ - w - 1, z0 + T_ + 1))
    f = f.cut(box_span(-L / 2 + lip, L / 2 - lip, -H / 2 + lip, H / 2 - lip, z0 - 1, z0 + w + 1))
    zc = z0 + T_ / 2
    for sg in (-1, 1):                              # grands côtés y = ±H/2 : vue du cadre tourné, x = ∓H/2
        for xl in Y_FERR:
            for z in Z_FERR:
                y0 = (H / 2 - w - 1) if sg > 0 else -(H / 2 + 1)
                f = f.cut(G.cyl_y(3.4, w + 2, xl, y0, zc + z))
    for y in (-G.CAPTEUR["vis_y"], G.CAPTEUR["vis_y"]):
        f = f.cut(cyl_x(3.4, w + 2, -L / 2 - 1, y, G.CAPTEUR["z_vis"]))
    return f


def construire():
    regler()
    G.PARTS.clear()
    G.build_head_parts()
    zv = G.z_vis_el()
    zb = zv - 22.85                               # dessus de l'étagère = dessous de la semelle du palier
    z0 = G.Z_CHAPE
    G.Z_CHAPE = zb - 8                            # palier et support d'élévation : zb = Z_CHAPE + 8
    pal = G.p_palier_vis_el()
    pal = pal.cut(cyl_x(2 * (0.8 * (Z_EL + 2) / 2 + 0.3), 90, -90, 0, ZT))    # joues taillées sous la roue
    G.reg("Palier_Vis_Elevation", pal, "PETG", G.COL["chape"], "Palier de la vis d'élévation")
    G.reg("Support_Moteur_Elevation", G.p_support_moteur_el(), "PETG", G.COL["chape"], "Support du moteur d'élévation")
    G.Z_CHAPE = z0
    pa = G.p_palier_vis_az().cut(cyl_z(2 * (0.8 * (Z_AZ + 2) / 2 + 0.4), 60, 0, 0, 60))
    G.reg("Palier_Vis_Azimut", pa, "PETG", G.COL["chape"], "Palier de la vis d'azimut")
    roue, xr = p_roue_el()
    G.reg("Roue_Elevation", roue, "PETG", G.COL["brass"], f"Roue d'élévation m0,8 Z{Z_EL}")
    G.reg("Plateau_Alu", p_plateau(), "Al 6061-T6", G.COL["chape"], "Plateau en aluminium de 5 mm (découpe laser)")
    G.reg("Bras_Gauche", p_bras(-1, zb), "PETG", G.COL["u"], "Bras gauche de la fourche")
    G.reg("Bras_Droit", p_bras(1, zb), "PETG", G.COL["u"], "Bras droit de la fourche, avec l'étagère de l'élévation")
    G.reg("Ferrure_Gauche", p_ferrure(-1), "PETG", G.COL["u"], "Ferrure gauche du panneau")
    G.reg("Ferrure_Droite", p_ferrure(1), "PETG", G.COL["u"], "Ferrure droite du panneau")
    G.reg("Cadre_Panneau", p_cadre(), "Al 6063-T5", G.COL["alu"], "Cadre du panneau, percé pour les ferrures")
    xg0, xg1 = HW + 2.0, X_E - 0.5                 # tige gauche : de l'intérieur de la ferrure au bout du bras
    xd1 = XC_EL - 4.0 + 16.0 - 0.5                 # tige droite : jusqu'au bout du moyeu de la roue
    tg = cq.Workplane().add(cq.Solid.makeCylinder(D_TIGE / 2, xg1 - xg0, Vector(-xg1, 0, 0), Vector(1, 0, 0)))
    td = cq.Workplane().add(cq.Solid.makeCylinder(D_TIGE / 2, xd1 - xg0, Vector(xg0, 0, 0), Vector(1, 0, 0)))
    global LG_TIGE_G, LG_TIGE_D
    LG_TIGE_G, LG_TIGE_D = xg1 - xg0, xd1 - xg0
    G.reg("Tige_Gauche", tg, "Acier (visserie)", G.COL["steel"], f"Tige acier rectifiée Ø8 x {LG_TIGE_G:.0f}")
    G.reg("Tige_Droite", td, "Acier (visserie)", G.COL["steel"], f"Tige acier rectifiée Ø8 x {LG_TIGE_D:.0f}")
    G.reg("Roulement_608", G.roulement_x("608"), "Acier 440C", G.COL["roulement"], "Roulement 608ZZ 8 x 22 x 7")
    gr = cq.Workplane("XY").add(cq.Solid.makeCylinder(1.2, 6.0, Vector(0, 0, -6.0), Vector(0, 0, 1)))
    gr = gr.cut(cq.Workplane("XY").polygon(6, 1.5 / math.cos(math.radians(30))).extrude(1.6).translate((0, 0, -1.6)))
    G.reg("Vis_STHC_M3x6", gr, "Acier (visserie)", G.COL["vis"], "Vis sans tête M3 x 6 bout plat (ISO 4026)")
    return zb, zv, xr


# ---------------------------------------------------------------------------
# VISSERIE ET INSERTS (repère tête, hors partie qui bascule)

def visserie_tete(zb):
    """[(type, point sous tête, direction d'insertion, nom)] de la partie fixe en élévation."""
    v = []
    z_top = PLAQUE[1]
    for x, y in G.TROUS_MOYEU:                                      # plateau -> moyeu, par-dessus
        v.append(("M3x8", (x, y, z_top), (0, 0, -1)))
    for x, y in G.TROUS_BAGUE:                                      # bague d'arrêt -> moyeu, par-dessous
        v.append(("M3x8", (x, y, 42), (0, 0, 1)))
    for x, y in G.trous_palier_az() + G.TROUS_SUPPORT_AZ:           # paliers d'azimut, sur les lumières
        v.append(("M3x8", (x, y, z_top + G.E_RONDELLE), (0, 0, -1)))
    for sg in (-1, 1):                                              # bras -> plateau, par-dessous
        for x, y in positions_pied(sg):
            v.append(("M3x8", (x, y, PLAQUE[0]), (0, 0, 1)))
    e = 7.0
    for x, y in G.TROUS_PALIER_EL + G.TROUS_SUPPORT_EL:             # palier et support d'élévation, par-dessous l'étagère
        v.append(("M3x10", (x + DX_EL, y, zb - e), (0, 0, 1)))
    ya, za = G.y_vis_az(), G.AZ_VIS["z"]
    me = G.MOT_28
    for sx in (-1, 1):                                              # oreilles des moteurs : vis + écrou
        v.append(("M3x8", (-30 + sx * me["entraxe"] / 2 + DX_EL, G.EL_VIS["y_face"] + 4, G.z_vis_el() + me["decal"]), (0, -1, 0)))
        v.append(("M3x8", (G.AZ_VIS["x_face"] + 4, ya + sx * me["entraxe"] / 2, za - me["decal"]), (-1, 0, 0)))
    return v


def inserts_tete(zb):
    """[(genre, point d'entrée, direction)] des pièces imprimées de la partie fixe en élévation et du plateau."""
    t = []
    z0 = G.Z_CHAPE
    for x, y in G.TROUS_MOYEU:
        t.append(("C", (x, y, z0), (0, 0, -1)))
    for x, y in G.TROUS_BAGUE:
        t.append(("L", (x, y, 45.0), (0, 0, 1)))
    for x, y in G.trous_palier_az() + G.TROUS_SUPPORT_AZ:
        t.append(("C", (x, y, z0), (0, 0, -1)))
    for sg in (-1, 1):
        for x, y in positions_pied(sg):
            t.append(("C", (x, y, PLAQUE[1]), (0, 0, 1)))
    for x, y in G.TROUS_PALIER_EL + G.TROUS_SUPPORT_EL:
        t.append(("C", (x + DX_EL, y, zb), (0, 0, 1)))
    return t


def assembler(zv, zb, el=40.0, az=0.0, avec_panneau=True, avec_visserie=True, phases=None):
    A = cq.Assembly(name="Tete_Rotative_Fourche")
    A.add(G.build_head_fixed(), name="SA_Tete_Fixe")
    h = cq.Assembly(name="SA_Tete_Orientable")
    for n in ("Plateau_Alu", "Moyeu_Chape", "Bague_Arret_Moyeu", "Bras_Gauche", "Bras_Droit"):
        G.add(h, n)
    ph = phases or {}
    a, ya = G.AZ_VIS, G.y_vis_az()
    G.add(h, "Palier_Vis_Azimut")
    G.add(h, "Arbre_Vis_Azimut")
    for i, x0 in enumerate(G.x_685(a["palier"]), 1):
        G.add(h, "Roulement_685", trans(x0, ya, a["z"]), f"Roulement_685_Az_{i}")
    loc_az = trans(0, ya, a["z"]) * rot((0, 1, 0), 90) * rot((0, 0, 1), ph.get("az", 0.0) + G.VIS_AZ["z"] * az)
    G.add(h, "Vis_Azimut", loc_az)
    G.add(h, "Vis_STHC_M3x4_Az", loc_az)
    G.add(h, "Accouplement", trans(a["x_joint"] - G.COUPLEUR["L"] / 2, ya, a["z"]) * rot((0, 1, 0), 90), "Accouplement_Az")
    G.add(h, "Support_Moteur_Azimut")
    G.add(h, "Moteur_Azimut_28BYJ", trans(a["x_face"], ya, a["z"]) * rot((0, 1, 0), 90) * rot((0, 0, 1), 90))
    d = trans(DX_EL, 0, 0)
    G.add(h, "Palier_Vis_Elevation", d)
    G.add(h, "Arbre_Vis_Elevation", d)
    for i, y0 in enumerate(G.x_685(G.EL_VIS["palier"]), 1):
        G.add(h, "Roulement_685", d * trans(-30, y0, zv) * rot((0, 0, 1), 90), f"Roulement_685_El_{i}")
    loc_el = d * trans(-30, 0, zv) * rot((1, 0, 0), -90) * rot((0, 0, 1), ph.get("el", 0.0) - G.VIS_EL["z"] * (el - G.EL_REF))
    G.add(h, "Vis_Elevation", loc_el)
    G.add(h, "Vis_STHC_M3x4_El", loc_el)
    G.add(h, "Accouplement", d * trans(-30, G.EL_VIS["y_joint"] - G.COUPLEUR["L"] / 2, zv) * rot((1, 0, 0), -90), "Accouplement_El")
    G.add(h, "Support_Moteur_Elevation", d)
    G.add(h, "Moteur_Elevation_28BYJ", d * trans(-30, G.EL_VIS["y_face"], zv) * rot((1, 0, 0), -90))
    me = G.MOT_28
    for i, sx in enumerate((-1, 1), 1):                              # écrous derrière les oreilles
        G.add(h, "Ecrou_M3", d * trans(-30 + sx * me["entraxe"] / 2, G.EL_VIS["y_face"] - me["oreille_ep"], zv + me["decal"])
              * rot((1, 0, 0), 90) * rot((0, 0, 1), 30), f"Ecrou_M3_Moteur_El_{i}")
        G.add(h, "Ecrou_M3", trans(a["x_face"] - me["oreille_ep"], ya + sx * me["entraxe"] / 2, a["z"] - me["decal"])
              * rot((0, 1, 0), -90) * rot((0, 0, 1), 30), f"Ecrou_M3_Moteur_Az_{i}")
    B = G.ROULEMENTS["608"]["B"]
    G.add(h, "Roulement_608", trans(X_I, 0, ZT), "Roulement_608_D")
    G.add(h, "Roulement_608", trans(-X_I - B, 0, ZT), "Roulement_608_G")
    if avec_visserie:
        for i, (t, p, dd) in enumerate(visserie_tete(zb)):
            G.add(h, G.nom_vis(t), G.loc_vis(p, dd), f"{G.nom_vis(t)}_{i}")
        for i, (x, y) in enumerate(G.trous_palier_az() + G.TROUS_SUPPORT_AZ):
            G.add(h, "Rondelle_M3", G.loc_vis((x, y, PLAQUE[1]), (0, 0, -1)), f"Rondelle_M3_{i}")
        for i, (g, pt, dd) in enumerate(inserts_tete(zb)):
            G.add(h, f"Insert_M3_{g}", G.loc_insert(pt, dd), f"Insert_M3_{g}_{i}")
    p = panneau_assy(avec_panneau, avec_visserie)
    h.add(p, name="SA_Panneau", loc=trans(0, 0, ZT) * rot((1, 0, 0), el - 90.0))
    A.add(h, name="SA_Tete_Orientable", loc=rot((0, 0, 1), az))
    return A


def panneau_assy(avec_panneau=True, avec_visserie=True):
    """Partie qui tourne en élévation (repère : origine sur l'axe d'élévation)."""
    p = cq.Assembly(name="SA_Panneau")
    G.add(p, "Ferrure_Gauche")
    G.add(p, "Ferrure_Droite")
    G.add(p, "Roue_Elevation")
    G.add(p, "Tige_Gauche")                                          # les deux tiges tournent avec le panneau
    G.add(p, "Tige_Droite")
    xr = XC_EL - 4.0
    if avec_visserie:
        xg = xr + 12.0
        G.add(p, "Insert_M3_C", G.loc_insert((xg, 0, 10.0), (0, 0, -1)), "Insert_M3_C_roue")
        G.add(p, "Vis_STHC_M3x6", G.loc_vis((xg, 0, 10.0), (0, 0, -1)), "Vis_STHC_M3x6_roue")
        for sg in (-1, 1):
            xgf = sg * (HW + E_FERR + E_MOY / 2)
            G.add(p, "Insert_M3_C", G.loc_insert((xgf, 0, 10.0), (0, 0, -1)), f"Insert_M3_C_ferrure_{sg}")
            G.add(p, "Vis_STHC_M3x6", G.loc_vis((xgf, 0, 10.0), (0, 0, -1)), f"Vis_STHC_M3x6_ferrure_{sg}")
            i = 0
            for y in Y_FERR:
                for z in Z_FERR:
                    i += 1
                    G.add(p, "Vis_CHC_M3x12", G.loc_vis((sg * (HW + 7.0), y, z), (-sg, 0, 0)), f"Vis_CHC_M3x12_ferrure_{sg}_{i}")
                    G.add(p, "Ecrou_M3", trans(sg * ECROU_X, y, z) * rot((0, 1, 0), -90 * sg), f"Ecrou_M3_ferrure_{sg}_{i}")
    if avec_panneau:
        pan = cq.Assembly(name="Panneau")
        for n in ("Cadre_Panneau", "Lamine_PV", "Cellules_PV", "Boite_Jonction"):
            G.add(pan, n)
        cap = cq.Assembly(name="Capteur")
        G.add_capteur(cap)
        if avec_visserie:
            for rp, t, pt, dd in G.visserie():
                if rp == "panneau" and t == "M3x10":
                    G.add(cap, G.nom_vis(t), G.loc_vis(pt, dd), f"{G.nom_vis(t)}_capteur_{len(cap.children)}")
            for rp, _pc, g, pt, dd in G.table_inserts():
                if rp == "panneau":
                    G.add(cap, f"Insert_M3_{g}", G.loc_insert(pt, dd), f"Insert_M3_{g}_capteur_{len(cap.children)}")
        pan.add(cap, name="Capteur", loc=rot((0, 0, 1), 180))        # capteur sur le petit côté x local = -L/2
        p.add(pan, name="SA_Cadre", loc=trans(0, 0, DEC_PAN) * rot((0, 0, 1), 90))   # cadre tourné : axe le long de 253 mm
    return p


# ---------------------------------------------------------------------------
# CALAGE, CONTRÔLES, COUPLES

def phase_vis(vis, roue, loc_fn, pas=10.0):
    def essai(k):
        return vis.moved(loc_fn(k)).intersect(roue).Volume()
    best = (0.0, essai(0.0))
    k = pas
    while best[1] > 1e-6 and k < 360:
        v = essai(k)
        if v < best[1] - 0.01:
            best = (k, v)
        k += pas
    st = pas
    for _ in range(3):
        if best[1] < 1e-6:
            break
        st /= 4
        for k in (best[0] + i * st for i in range(-3, 4) if i):
            v = essai(k)
            if v < best[1] - 0.01:
                best = (k, v)
    return best


def calage(zv):
    a, ya = G.AZ_VIS, G.y_vis_az()
    loc_az = lambda k: trans(0, ya, a["z"]) * rot((0, 1, 0), 90) * rot((0, 0, 1), k)
    wa = G.PARTS["Roue_Azimut_Fixe"][0].val()
    va = G.PARTS["Vis_Azimut"][0].val()
    k_az = phase_vis(va, wa, loc_az)
    d = trans(DX_EL, 0, 0)
    loc_el = lambda k: d * trans(-30, 0, zv) * rot((1, 0, 0), -90) * rot((0, 0, 1), k)
    wr = G.PARTS["Roue_Elevation"][0].val().moved(trans(0, 0, ZT) * rot((1, 0, 0), G.EL_REF - 90.0))
    k_el = phase_vis(G.PARTS["Vis_Elevation"][0].val(), wr, loc_el)
    return {"az": k_az[0], "el": k_el[0]}, k_az[1], k_el[1]


def couples(M_t, r):
    CC, g = 0.025, 9.81
    lam = math.atan(0.8 / 12.0)
    eta = math.tan(lam) / math.tan(lam + math.atan(0.15))
    out = []
    for axe, z, need0, vent in (("élévation", Z_EL, M_t * g * r / 1000 + 0.01, 0.35), ("azimut", Z_AZ, 0.03, 0.5)):
        dispo = CC * z * eta
        marges = ", ".join(f"{v} m/s ×{dispo / (need0 + vent * (v / 10) ** 2):.1f}" for v in (0, 6, 8, 10))
        out.append(f"{axe} : {z} dents, rendement {eta:.2f}, couple prudent {dispo:.2f} N·m, besoin sans vent {need0:.3f} N·m ; "
                   f"marges : {marges} ; 90° en {0.25 * 4076 * z / 120 / 60:.0f} min")
    return out


ORIENT = {
    # rotations (axe, angle) puis pose sur le plateau : bras et ferrures sur leur face intérieure (x vers le haut)
    "Bras_Droit": [((0, 1, 0), -90)], "Bras_Gauche": [((0, 1, 0), -90)],      # le gauche sur sa face extérieure (semelle vers l'intérieur)
    "Ferrure_Droite": [((0, 1, 0), -90)], "Ferrure_Gauche": [((0, 1, 0), 90)],
    "Roue_Elevation": [((0, 1, 0), -90)],
}
IMPRIMEES = ("Fond_Socle", "Socle", "Roue_Azimut_Fixe", "Moyeu_Chape", "Bague_Arret_Moyeu", "Palier_Vis_Azimut",
             "Support_Moteur_Azimut", "Vis_Azimut", "Palier_Vis_Elevation", "Support_Moteur_Elevation", "Vis_Elevation",
             "Roue_Elevation", "Bras_Droit", "Bras_Gauche", "Ferrure_Droite", "Ferrure_Gauche",
             "Capteur_Solaire_Boitier", "Capteur_Solaire_Support")


def eprouvette():
    """Éprouvette de réglage du modèle à fourche : logements des 608 (bras de la fourche) et des 685 (paliers) en trois
    jeux, alésage Ø8 de la tige, passage M3, trou d'insert, téton Ø30 (bague intérieure d'un 6806) ; sur une paroi
    debout, les trous d'axe horizontal imprimés comme sur les paliers (685 et centrage du bossage du 28BYJ-48 en goutte)
    et un trou d'insert horizontal, comme dans la semelle des bras."""
    aj = G.AJ
    e = box_span(0, 112, 0, 62, 0, 6).edges("|Z").fillet(3)
    for i, dj in enumerate((-0.10, 0.0, 0.10)):           # 608 : Ø22
        e = e.cut(cyl_z(G.ROULEMENTS["608"]["D"] + aj["roulement"] + dj, 8, 16 + 26 * i, 16, -1))
    for i, dj in enumerate((-0.10, 0.0, 0.10)):           # 685 : Ø11
        e = e.cut(cyl_z(11 + aj["roulement"] + dj, 8, 10 + 15 * i, 46, -1))
    e = e.cut(cyl_z(D_TIGE + 0.1, 8, 57, 46, -1))          # tige Ø8 dans un moyeu ou une ferrure
    e = e.cut(cyl_z(D_TIGE + 1.0, 8, 70, 46, -1))          # tige Ø8 dans un bras (jeu de 0,5 mm)
    e = e.cut(cyl_z(aj["passage_m3"], 8, 83, 46, -1)).cut(cyl_z(G.INSERT["C"]["d_trou"], 5, 93, 46, 6 - G.INSERT["C"]["prof"]))
    e = e.union(cyl_z(30 + aj["moyeu"], 8, 95, 16, 6))     # téton du moyeu dans le 6806
    e = e.union(box_span(0, 112, 62, 70, 0, 30).edges("|Y").fillet(2))
    Y, Z, zc = (0, 1, 0), (0, 0, 1), 14.0
    e = e.cut(G.goutte(11 + aj["roulement"], 10, (20, 61, zc), Y, Z))
    e = e.cut(G.goutte(G.MOT_28["boss_d"] + 0.6, 10, (50, 61, zc), Y, Z))
    e = trou_insert(e, (80, 70.0, zc), (0, -1, 0))         # trou d'insert horizontal (semelle des bras, imprimés sur la face)
    return e


def exporter(avec_ecriture=True):
    os.makedirs(OUT_IMPR, exist_ok=True)
    os.makedirs(OUT_METAL, exist_ok=True)
    for f in os.listdir(OUT_IMPR):
        if f.endswith((".stl", ".step")):
            os.remove(os.path.join(OUT_IMPR, f))
    orient = dict(T.ORIENTATION)
    orient.update(ORIENT)
    for n in IMPRIMEES:
        wp = T.a_plat(G.PARTS[n][0], orient[n])
        cq.exporters.export(wp, os.path.join(OUT_IMPR, f"{n}.stl"), tolerance=0.01, angularTolerance=0.1)
        cq.exporters.export(wp, os.path.join(OUT_IMPR, f"{n}.step"))
    ep = eprouvette()
    cq.exporters.export(ep, os.path.join(OUT, "Eprouvette_Ajustements.stl"), tolerance=0.01, angularTolerance=0.1)
    cq.exporters.export(ep, os.path.join(OUT, "Eprouvette_Ajustements.step"))
    pl = G.PARTS["Plateau_Alu"][0]
    cq.exporters.export(pl, os.path.join(OUT_METAL, "Plateau_Alu.step"))
    try:
        cq.exporters.exportDXF(pl.faces("<Z"), os.path.join(OUT_METAL, "Plateau_Alu.dxf"))
    except Exception as e:                      # le DXF est un confort : le STEP suffit
        print("  DXF du plateau non écrit :", e)
    print(f"  {len(IMPRIMEES)} pièces à imprimer -> {OUT_IMPR} ; plateau -> {OUT_METAL}")


def trepied(zv, zb, ph):
    """Tête sur le trépied de la démonstration : assemblage STEP, garde, stabilité (calcul de generate_demo_trepied.py)."""
    import generate_demo_trepied as D
    noms = D.enregistrer_trepied()
    D.enregistrer_lest()

    def assemblage(az, el, noms_, name="Demo_Trepied", lest=True):
        root = cq.Assembly(name=name)
        tr = cq.Assembly(name="SA_Trepied")
        for n in noms_:
            G.add(tr, n)
        root.add(tr, name="SA_Trepied", loc=G.TO_YUP)
        if lest and D.NOMS_LEST[0] in G.PARTS:
            ls = cq.Assembly(name="SA_Lest")
            for n in D.NOMS_LEST:
                G.add(ls, n)
            root.add(ls, name="SA_Lest", loc=G.TO_YUP)
        root.add(assembler(zv, zb, el, az, True, True, ph), name="Tete", loc=G.TO_YUP * trans(0, 0, D.z_tete()))
        return root

    D.assemblage = assemblage
    build_panel0, pan_back0 = G.build_panel, G.P["pan_back"]
    G.build_panel = lambda with_panel=True: panneau_assy(True, False)
    G.P["pan_back"] = -G.P["pan_T"] / 2                      # centre du panneau sur l'axe d'élévation
    try:
        A = assemblage(0.0, 40.0, noms)
        if "--rien-ecrire" not in sys.argv:
            chemin = os.path.join(OUT, "Demo_Trepied.step")
            A.export(chemin)
            G.clean_step_names(chemin)
            print(f"  {chemin} ({os.path.getsize(chemin) / 1e6:.1f} Mo)")
        hits = G.interference(G.flatten(A))
        print(f"  trépied : interférences {'aucune' if not hits else hits}")
        g = D.garde(noms)
        print(f"  garde mini tête + panneau / trépied : {g[0]:.1f} mm ({g[1].split('/')[-1]} / {g[2].split('/')[-1]}, az={g[3]:g}°, él={g[4]:g}°)")
        s = D.stabilite(noms)
        print(f"  masses : trépied {s['m_trepied']:.2f} kg, charge sur la rotule {s['m_charge']:.2f} kg, dont partie qui bascule "
              f"{s['m_bascule']:.2f} kg ; axe d'élévation à {s['z_axe']:.0f} mm du sol")
        e = s["e_max"]
        print(f"  centre de gravité de la tête jusqu'à {e:.0f} mm de l'axe, soit {s['m_charge'] * 9.81 * e / 1000:.2f} N·m sur la rotule")
        for lest, ((ang, az, el), (v, azv, elv, sens), (ang_f, (v_f, sens_f))) in s["res"].items():
            print(f"  lest {lest:.0f} kg : basculement sans vent {ang:.1f}° ; vent de basculement {v:.1f} m/s = {v * 3.6:.0f} km/h "
                  f"(az={azv}°, él={elv:g}°) ; panneau tourné vers une jambe : {v_f * 3.6:.0f} km/h")
    finally:
        G.build_panel, G.P["pan_back"] = build_panel0, pan_back0


def main():
    zb, zv, xr = construire()
    ph, v_az, v_el = calage(zv)
    print(f"calage az {ph['az']:.1f}° ({v_az:.3f} mm3), él {ph['el']:.1f}° ({v_el:.3f} mm3) ; axe d'élévation z = {ZT:g}, "
          f"entraxe {G.entraxe_el():.2f} mm")
    A = assembler(zv, zb, 40.0, 0.0, True, True, ph)
    chemin = os.path.join(OUT, "Tete_Rotative_Fourche.step")
    if "--rien-ecrire" not in sys.argv:
        os.makedirs(OUT, exist_ok=True)
        A.export(chemin)
        G.clean_step_names(chemin)
        print(f"  {chemin} ({os.path.getsize(chemin) / 1e6:.1f} Mo)")
    flat = G.flatten(A)
    hits = G.interference(flat)
    print(f"  interférences (pose 40°) : {'aucune' if not hits else hits}")
    T.verifier_prise(flat)
    pire = (1e9,)
    for el in (10.0, 15.0, 30.0, 40.0, 60.0, 80.0, 92.0):          # le cahier des charges demande 15° à 90°
        for az in (0.0, 90.0):
            fl = G.flatten(assembler(zv, zb, el, az, True, True, ph))
            h2 = G.interference(fl)
            if h2:
                print(f"  interférence él={el} az={az} : {h2}")
            mov = [(n, s) for n, s in fl if "/SA_Panneau/" in n and "Roue_Elevation" not in n and "Ferrure" not in n
                   and "Vis_" not in n and "Ecrou" not in n and "Insert" not in n]
            fix = [(n, s) for n, s in fl if "/SA_Panneau/" not in n and "Vis_Elevation" not in n and "Roulement" not in n
                   and "Vis_" not in n and "Ecrou" not in n and "Insert" not in n]
            dd = G.min_clearance(mov, fix, cutoff=40.0)
            if dd[0] < pire[0]:
                pire = dd + (el,)
    print(f"  garde mini panneau / fourche : {pire[0]:.1f} mm ({str(pire[1]).split('/')[-1]} / {str(pire[2]).split('/')[-1]}, él={pire[3]})")
    A90 = assembler(zv, zb, 90.0, 0.0, True, True, ph)
    f90 = G.flatten(A90)
    _r, M_t, cg_t = G.mass_properties([x for x in f90 if "/SA_Panneau/" in x[0]])
    _r, M_h, cg_h = G.mass_properties(f90)
    r = math.hypot(cg_t.y, cg_t.z - ZT)
    xs, ys, zs = [], [], []
    for n, sh in f90:
        if any(k in n for k in ("Cadre_Panneau", "Lamine_PV", "Cellules_PV", "Boite_Jonction", "/Capteur")):
            continue
        b_ = sh.BoundingBox()
        xs += [b_.xmin, b_.xmax]; ys += [b_.ymin, b_.ymax]; zs += [b_.zmin, b_.zmax]
    print(f"  enveloppe de la structure hors panneau (cahier des charges : 350 x 350 x 350) : "
          f"{max(xs) - min(xs):.0f} x {max(ys) - min(ys):.0f} x {max(zs) - min(zs):.0f} mm "
          f"(x de {min(xs):.0f} à {max(xs):.0f}, y de {min(ys):.0f} à {max(ys):.0f}, z de {min(zs):.0f} à {max(zs):.0f})")
    print(f"  partie qui bascule : {M_t:.2f} kg, CdG à {r:.1f} mm de l'axe ; tête complète {M_h:.2f} kg, CdG à z = {cg_h.z:.0f} mm")
    for l in couples(M_t, r):
        print("  " + l)
    if "--rien-ecrire" not in sys.argv:
        exporter()
    trepied(zv, zb, ph)
    G.set_variante(None)
    G.set_ajustements("reel")
    return A


if __name__ == "__main__":
    main()
