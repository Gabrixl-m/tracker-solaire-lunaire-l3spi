#!/usr/bin/env python3
"""
Démonstration sur Terre : la tête PETG, le panneau et le capteur solaire vissés sur le trépied
photo réel (trépied Dexter de chantier, avec rotule et plateau à vis 1/4").

Le trépied est modélisé simplement, d'après des photos et deux cotes mesurées :
  - dessus du plateau à 600 mm du sol (sans la vis 1/4" qui dépasse) ;
  - pointes des pieds à 230 mm de l'axe, au sol.
Les autres cotes du trépied (tubes, corps, rotule) sont estimées sur les photos.

Ce script :
  - exporte l'assemblage CAO/Demo_Terre_PETG/Demo_Trepied_Dexter.step (Y-up, sol en y = 0) ;
  - vérifie les interférences et la garde entre la partie qui tourne et le trépied ;
  - calcule la stabilité : angle de basculement et vent de basculement, dans la pire
    orientation du panneau, sans lest et avec un lest suspendu sous le trépied ;
  - avec --rendus : rendus PNG dans docs/ (sur serveur : xvfb-run -a python ... --rendus).

Usage : python generate_demo_trepied.py [--rendus]
"""

import math
import os
import sys

import cadquery as cq
from cadquery import Vector

import generate_tete_vis_sans_fin as T
import generate_tracker as G
from generate_tracker import box_span, cyl_dir, cyl_z, rot, trans

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_STEP = os.path.join(HERE, "CAO", "Demo_Terre_PETG", "Demo_Trepied_Dexter.step")

# Trépied (repère Z-up, origine au sol sur l'axe ; jambes vers 90°, 210° et 330°)
DEXTER = dict(
    h_plateau=600.0,          # mesuré : sol -> dessus du plateau
    r_pieds=230.0,            # mesuré : axe -> pointe des pieds
    # estimé sur les photos :
    plateau=(62.0, 50.0, 10.0),   # plateau ovale à clip (long, large, épaisseur)
    vis=(5.0, 5.5),           # vis 1/4" (Ø du noyau, saillie au-dessus du plateau)
    rotule_h=62.0,            # rotule 3D : du dessus du corps au dessous du plateau
    corps=(46.0, 34.0),       # corps noir : rayon circonscrit (triangle arrondi), hauteur
    r_charniere=38.0,         # charnières des jambes
    tube=(24.0, 19.0, 1.0),   # tube haut, tube bas (Ø), épaisseur
    z_verrou=95.0,            # verrou à clip du tube bas (tube bas peu sorti)
    colonne=(20.0, 140.0),    # colonne centrale : Ø, bas (moyeu des entretoises)
    z_entretoise=118.0,       # attache des entretoises sur les jambes
    phis=(90.0, 210.0, 330.0),
)
COULEURS = {"alu": cq.Color(0.78, 0.79, 0.81), "noir": cq.Color(0.10, 0.10, 0.11),
            "bleu": cq.Color(0.10, 0.30, 0.62), "orange": cq.Color(0.96, 0.52, 0.12)}
G.MAT.setdefault("Plastique (trépied)", 1150.0)
G.MAT.setdefault("Al (trépied)", 2700.0)

# Cas de charge
RHO_AIR, CD_PANNEAU = 1.2, 1.2     # vent : pression dynamique x Cx du panneau (plaque plane)
LESTS = (0.0, 2.0, 3.0)             # lest suspendu sous le trépied (kg), à 50 mm du sol


def z_tete():
    """Hauteur (sol) de l'origine du repère tête : le dessous du fond est sur le plateau."""
    return DEXTER["h_plateau"] - G.z_fond_photo()


R_EMBOUT = 10.0                     # embout caoutchouc arrondi : il touche le sol à r_pieds


def geometrie_jambe():
    """Hauteur des charnières, inclinaison des jambes, longueur charnière -> centre de l'embout."""
    d = DEXTER
    zc = d["h_plateau"] - d["plateau"][2] - d["rotule_h"] - d["corps"][1] / 2   # axe des charnières
    beta = math.atan2(d["r_pieds"] - d["r_charniere"], zc - R_EMBOUT)
    return zc, beta, math.hypot(d["r_pieds"] - d["r_charniere"], zc - R_EMBOUT)


def le_long(phi, s):
    """Point de l'axe d'une jambe (azimut phi), à la distance s de la charnière."""
    zc, beta, _L = geometrie_jambe()
    r = DEXTER["r_charniere"] + s * math.sin(beta)
    a = math.radians(phi)
    return (r * math.cos(a), r * math.sin(a), zc - s * math.cos(beta))


def tube(d, e, p0, p1):
    v = Vector(*p1) - Vector(*p0)
    t = cq.Solid.makeCylinder(d / 2, v.Length, Vector(*p0), v.normalized())
    return cq.Workplane().add(t.cut(cq.Solid.makeCylinder(d / 2 - e, v.Length, Vector(*p0), v.normalized())))


def bloc(a, b, c, centre, phi, beta):
    """Pavé a x b x c centré en 'centre', grand côté c le long d'une jambe (azimut phi, pente beta)."""
    s = cq.Solid.makeBox(a, b, c, Vector(-a / 2, -b / 2, -c / 2))
    s = s.rotate(Vector(), Vector(0, 1, 0), -math.degrees(beta)).rotate(Vector(), Vector(0, 0, 1), phi)
    return cq.Workplane().add(s.translate(Vector(*centre)))


def ovale(lx, ly, h, z0):
    return cq.Workplane("XY").ellipse(lx / 2, ly / 2).extrude(h).translate((0, 0, z0))


def barre(p0, p1, w, e):
    """Plat de largeur w (horizontale) et d'épaisseur e, de p0 à p1."""
    v = Vector(*p1) - Vector(*p0)
    n = v.cross(Vector(0, 0, 1)).normalized()
    pl = cq.Plane(origin=Vector(*p0) - n * (e / 2), xDir=v.normalized(), normal=n)
    return cq.Workplane(pl).rect(v.Length, w, centered=(False, True)).extrude(e)


def pieces_trepied():
    """Pièces du trépied, chacune déjà à sa place (repère Z-up, sol en z = 0)."""
    d = DEXTER
    zc, beta, L = geometrie_jambe()
    z_pl = d["h_plateau"] - d["plateau"][2]                   # dessous du plateau
    z_ct = z_pl - d["rotule_h"]                               # dessus du corps
    p = {}
    # corps noir : triangle arrondi, sommets vers les jambes
    rc, hc = d["corps"]
    pts = [(rc * math.cos(math.radians(f)), rc * math.sin(math.radians(f))) for f in d["phis"]]
    corps = cq.Workplane("XY").polyline(pts).close().extrude(hc).edges("|Z").fillet(14).translate((0, 0, z_ct - hc))
    p["Corps"] = (corps.cut(cyl_z(d["colonne"][0] + 0.5, hc + 2, z=z_ct - hc - 1)), "noir")
    # rotule 3D et plateau à clip, molettes orange
    rot3d = cyl_z(44, 12, z=z_ct).union(cq.Workplane().add(cq.Solid.makeSphere(16, Vector(0, 0, z_ct + 24), angleDegrees1=-90)))
    rot3d = rot3d.union(box_span(-14, 14, -14, 14, z_ct + 24, z_pl - 16)).union(ovale(66, 54, 16, z_pl - 16))
    p["Rotule"] = (rot3d, "noir")
    p["Plateau"] = (ovale(*d["plateau"][:2], d["plateau"][2], z_pl), "noir")
    p["Vis_1_4"] = (cyl_z(d["vis"][0], d["vis"][1] + 10, z=d["h_plateau"] - 10), "alu")
    molettes = cyl_dir(7, 30, (-12, 0, z_ct + 28), (-1, 0, 0)).union(cyl_dir(18, 12, (-40, 0, z_ct + 28), (-1, 0, 0)))
    molettes = molettes.union(cyl_dir(16, 10, (33, 0, z_pl - 8), (1, 0, 0)))                     # inclinaison
    molettes = molettes.union(box_span(-6, 6, 27, 40, z_pl - 12, z_pl - 2))                        # levier du clip
    a = math.radians(d["phis"][0] + 60)
    molettes = molettes.union(cyl_dir(16, 12, (40 * math.cos(a), 40 * math.sin(a), z_ct - hc / 2),
                                      (math.cos(a), math.sin(a), 0)))                                # colonne
    p["Molettes"] = (molettes, "orange")
    # colonne centrale et moyeu des entretoises
    zb = d["colonne"][1]
    p["Colonne"] = (tube(d["colonne"][0], 1.5, (0, 0, zb), (0, 0, z_ct - 2)), "alu")
    p["Moyeu"] = (cyl_z(34, 22, z=zb).cut(cyl_z(d["colonne"][0] + 0.2, 24, z=zb - 1)).union(cyl_z(24, 10, z=zb - 10)),
                  "orange")
    # jambes : charnière bleue, tube haut, verrou à clip, tube bas, embout ; entretoises
    for i, phi in enumerate(d["phis"], 1):
        s_v = (zc - d["z_verrou"]) / math.cos(beta)
        s_e = (zc - d["z_entretoise"]) / math.cos(beta)
        p[f"Charniere_{i}"] = (bloc(d["tube"][0] + 6, d["tube"][0] + 4, 36, le_long(phi, 8), phi, beta), "bleu")
        p[f"Tube_Haut_{i}"] = (tube(d["tube"][0], d["tube"][2], le_long(phi, 26), le_long(phi, s_v - 20)), "alu")
        p[f"Verrou_{i}"] = (bloc(d["tube"][0] + 6, d["tube"][0] + 6, 46, le_long(phi, s_v), phi, beta), "bleu")
        t = (d["tube"][0] / 2 + 5) * math.cos(math.radians(phi)), (d["tube"][0] / 2 + 5) * math.sin(math.radians(phi))
        cv = le_long(phi, s_v)
        p[f"Clip_{i}"] = (bloc(12, 5, 30, (cv[0] - t[1], cv[1] + t[0], cv[2]), phi, beta), "orange")
        p[f"Tube_Bas_{i}"] = (tube(d["tube"][1], d["tube"][2], le_long(phi, s_v + 23), le_long(phi, L - 28)), "alu")
        e0, e1 = Vector(*le_long(phi, L - 28)), Vector(*le_long(phi, L))
        emb = cyl_dir(2 * R_EMBOUT, 28, tuple(e0), tuple(e1 - e0))
        p[f"Embout_{i}"] = (emb.union(cq.Workplane().add(cq.Solid.makeSphere(R_EMBOUT, e1, angleDegrees1=-90))), "noir")
        a = math.radians(phi)
        pe = Vector(*le_long(phi, s_e)) - Vector(math.cos(a), math.sin(a), 0) * (d["tube"][0] / 2 + 1)
        p[f"Entretoise_{i}"] = (barre((17 * math.cos(a), 17 * math.sin(a), zb + 11), (pe.x, pe.y, pe.z), 12, 3), "alu")
    return p


# ordre de priorité : une pièce est évidée de celles qui la précèdent (pas de chevauchement)
PRIORITE = ("Vis_1_4", "Molettes", "Clip", "Charniere", "Verrou", "Entretoise", "Moyeu", "Tube_Haut", "Tube_Bas",
            "Embout", "Colonne", "Plateau", "Rotule", "Corps")


def enregistrer_trepied():
    """Pièces du trépied dans G.PARTS (une pièce par instance : elles sont déjà placées)."""
    pieces = pieces_trepied()
    ordre = sorted(pieces, key=lambda n: next(i for i, k in enumerate(PRIORITE) if n.startswith(k)))
    faites = []
    for n in ordre:
        wp, c = pieces[n]
        bb = wp.val().BoundingBox()
        for m in faites:
            bm = pieces[m][0].val().BoundingBox()
            if not (bb.xmin > bm.xmax or bm.xmin > bb.xmax or bb.ymin > bm.ymax or bm.ymin > bb.ymax
                    or bb.zmin > bm.zmax or bm.zmin > bb.zmax):
                wp = wp.cut(pieces[m][0])
        pieces[n] = (wp, c)
        faites.append(n)
    noms = []
    for n, (wp, c) in pieces.items():
        nom = f"Trepied_Dexter_{n}"
        mat = "Al (trépied)" if c == "alu" else "Plastique (trépied)"
        G.reg(nom, wp, mat, COULEURS[c], f"Trépied photo Dexter (modèle simplifié) : {n.replace('_', ' ').lower()}")
        noms.append(nom)
    return noms


def assemblage(az, el, noms, name="Demo_Trepied_Dexter"):
    root = cq.Assembly(name=name)
    tr = cq.Assembly(name="SA_Trepied_Dexter")
    for n in noms:
        G.add(tr, n)
    root.add(tr, name="SA_Trepied_Dexter", loc=G.TO_YUP)
    zt = trans(0, 0, z_tete())
    root.add(G.build_head_fixed(), name="SA_Tete_Fixe", loc=G.TO_YUP * zt)
    root.add(G.build_head(az, el), name="SA_Tete_Orientable", loc=G.TO_YUP * zt * rot((0, 0, 1), az))
    return root


def masse_cdg(flat):
    _rows, m, c = G.mass_properties(flat)
    return m, G.to_zup(c)


def stabilite(noms):
    """Basculement sans vent et vent de basculement, dans toutes les orientations du panneau.
    Trois ensembles : le fixe (trépied + partie fixe de la tête), la partie qui tourne en azimut
    sans le panneau, et la partie qui bascule ; on fait tourner leurs centres de gravité."""
    fl = G.flatten(assemblage(0.0, 90.0, noms, "stab"))
    trep = [x for x in fl if "/SA_Trepied_Dexter/" in x[0]]
    tete_fixe = [x for x in fl if "/SA_Tete_Fixe/" in x[0]]
    tourne = [x for x in fl if "/SA_Tete_Orientable/" in x[0] and "/SA_Panneau/" not in x[0]]
    m0, c0 = masse_cdg(trep)
    m1, c1 = masse_cdg(tete_fixe)
    m2, c2 = masse_cdg(tourne)
    _rows, m3, c3 = G.mass_properties(G.flatten(G.build_panel(True)))     # repère panneau (Z-up)
    d = DEXTER
    zt = z_tete()
    a_ar = d["r_pieds"] / 2                                       # distance axe -> arête d'appui
    normales = [math.radians(f + 60) for f in d["phis"]]          # normales sortantes des arêtes
    pan_c = (0.0, 0.0, G.P["pan_back"] + G.P["pan_T"] / 2)        # centre du panneau (repère panneau)
    s_pan = G.P["pan_L"] * G.P["pan_H"] * 1e-6

    def panneau(az, el, v):
        """Point du repère panneau -> monde (Z-up), pour une pose."""
        a, e = math.radians(az), math.radians(el - 90.0)
        x, y, z = v
        y, z = y * math.cos(e) - z * math.sin(e), y * math.sin(e) + z * math.cos(e)   # Rx(él - 90)
        z += G.Z_T
        x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)   # Rz(az)
        return x, y, z + zt

    def pose(az, el):
        """Centres de gravité (monde) : tête + panneau seuls, et tout l'ensemble sans lest."""
        a = math.radians(az)
        c2r = (c2.x * math.cos(a) - c2.y * math.sin(a), c2.x * math.sin(a) + c2.y * math.cos(a), c2.z)
        c3w = panneau(az, el, (c3.x, c3.y, c3.z))
        mt = m1 + m2 + m3
        tete = [(m1 * u + m2 * v + m3 * w) / mt for u, v, w in zip((c1.x, c1.y, c1.z), c2r, c3w)]
        return tete

    def cas(az, el, lest):
        """(angle de basculement sans vent, vent de basculement, sens) pour une pose et un lest."""
        tete = pose(az, el)
        mt = m1 + m2 + m3
        M = m0 + mt + lest
        cg = [(m0 * u + mt * v + lest * w) / M for u, v, w in zip((c0.x, c0.y, c0.z), tete, (0.0, 0.0, 50.0))]
        n0, o = panneau(az, el, (0, 0, 1)), panneau(az, el, (0, 0, 0))
        nh = (n0[0] - o[0], n0[1] - o[1])                         # normale du panneau, à plat : |nh| = cos(él)
        pc = panneau(az, el, pan_c)                               # centre de poussée
        coef = 0.5 * RHO_AIR * CD_PANNEAU * s_pan * math.cos(math.radians(el))   # poussée = coef x v²
        ang, vent = 90.0, (1e9, "")
        for ne in normales:
            m_e = (math.cos(ne), math.sin(ne))
            bras = a_ar - (cg[0] * m_e[0] + cg[1] * m_e[1])       # CdG -> arête, à plat
            ang = min(ang, math.degrees(math.atan2(bras, cg[2])))
            r_pc = a_ar - (pc[0] * m_e[0] + pc[1] * m_e[1])
            for sgn in (1, -1):                                    # vent de dos (+n) ou de face (-n)
                f_h = sgn * (nh[0] * m_e[0] + nh[1] * m_e[1])      # poussée horizontale vers l'arête
                f_v = sgn * math.sin(math.radians(el))             # poussée verticale (> 0 : soulève)
                mt_v = coef * (f_h * pc[2] + f_v * r_pc) / 1000    # moment de renversement / v²
                if mt_v > 0 and bras > 0:
                    v = math.sqrt(M * 9.81 * bras / 1000 / mt_v)
                    if v < vent[0]:
                        vent = (v, "de dos" if sgn == 1 else "de face")
        return ang, vent

    els = (-2.0, 0.0, 15.0, 30.0, 45.0, 60.0, 75.0, 92.0)
    res = {}
    for lest in LESTS:
        pa, pv = (90.0,), (1e9,)
        for az in range(0, 360, 5):
            for el in els:
                ang, (v, sens) = cas(float(az), el, lest)
                if ang < pa[0]:
                    pa = (ang, az, el)
                if v < pv[0]:
                    pv = (v, az, el, sens)
        # panneau tourné vers une jambe (az = 0), vertical, vent de dos : le cas le plus favorable
        fav = cas(0.0, 0.0, lest)
        res[lest] = (pa, pv, fav)
    # charge sur la rotule : excentration maxi du centre de gravité de la tête et du panneau
    e_max = max(math.hypot(*pose(float(az), el)[:2]) for az in range(0, 360, 30) for el in els)
    return dict(m_trepied=m0, m_charge=m1 + m2 + m3, m_bascule=m3, z_axe=zt + G.Z_T, res=res, e_max=e_max)


def garde(noms):
    """Garde mini entre ce qui tourne (tête orientable et panneau) et le trépied + partie fixe."""
    pire = (1e9,)
    for el in (-2.0, 30.0, 92.0):
        for az in (0.0, 60.0, 120.0, 180.0, 240.0, 300.0):
            fl = G.flatten(assemblage(az, el, noms, "g"))
            mob = [x for x in fl if "/SA_Tete_Orientable/" in x[0]]
            tr = [x for x in fl if "/SA_Trepied_Dexter/" in x[0]]
            dd = G.min_clearance(mob, tr, cutoff=60.0)
            if dd[0] < pire[0]:
                pire = dd + (az, el)
    return pire


def rendus(noms):
    from render_apercu import build_renderer, shoot
    sun = tuple(v / math.sqrt(0.45 ** 2 + 0.75 ** 2 + 0.6 ** 2) for v in (0.45, 0.75, -0.6))
    assy = assemblage(0.0, 40.0, noms)
    r = build_renderer(assy, sun)
    r.SetBackground(0.80, 0.86, 0.93)                  # ciel de jour : démonstration sur Terre
    f0 = (0, 520, 0)
    shoot(r, "demo_trepied_dexter_iso.png", (1350, 1050, -1500), focal=f0, angle=34)
    shoot(r, "demo_trepied_dexter_profil.png", (2300, 560, 0), focal=f0, angle=30)
    shoot(r, "demo_trepied_dexter_arriere.png", (-1200, 1000, 1500), focal=f0, angle=34)
    r = build_renderer(assy, sun, ground=False)
    r.SetBackground(0.80, 0.86, 0.93)
    shoot(r, "demo_trepied_dexter_detail.png", (-560, 820, 520), focal=(0, 650, 0), angle=30)


def main():
    G.set_ajustements("petg")
    T.build_parts()
    noms = enregistrer_trepied()
    if "--rendus" in sys.argv:
        rendus(noms)
        return
    assy = assemblage(0.0, 40.0, noms)
    assy.export(OUT_STEP)
    G.clean_step_names(OUT_STEP)
    back = cq.importers.importStep(OUT_STEP)
    print(f"{OUT_STEP} ({os.path.getsize(OUT_STEP) / 1e6:.1f} Mo) : {len(back.solids().vals())} solides, "
          f"valide={back.val().isValid()}")
    zc, beta, L = geometrie_jambe()
    print(f"trépied : charnières à {zc:.0f} mm du sol, jambes de {L:.0f} mm à {math.degrees(beta):.1f}° de la "
          f"verticale ; axe d'élévation à {z_tete() + G.Z_T:.0f} mm du sol")
    hits = G.interference(G.flatten(assy))
    print(f"interférences : {'aucune' if not hits else hits}")
    g = garde(noms)
    print(f"garde mini tête orientable + panneau / trépied : {g[0]:.1f} mm "
          f"({g[1].split('/')[-1]} / {g[2].split('/')[-1]}, az={g[3]:g}°, él={g[4]:g}°)")
    s = stabilite(noms)
    print(f"masses : trépied {s['m_trepied']:.2f} kg (estimée), charge sur la rotule (tête + panneau) "
          f"{s['m_charge']:.2f} kg, dont partie qui bascule {s['m_bascule']:.2f} kg")
    e = s["e_max"]
    print(f"charge sur la rotule : centre de gravité jusqu'à {e:.0f} mm de l'axe, "
          f"soit {s['m_charge'] * 9.81 * e / 1000:.2f} N·m à tenir par ses blocages")
    for lest, ((ang, az, el), (v, azv, elv, sens), (ang_f, (v_f, sens_f))) in s["res"].items():
        print(f"  lest {lest:.0f} kg : pire cas : basculement sans vent à {ang:.1f}° de pente (az={az}°, "
              f"él={el:g}°), vent de basculement {v:.1f} m/s = {v * 3.6:.0f} km/h (vent {sens}, az={azv}°, "
              f"él={elv:g}°) ; panneau tourné vers une jambe : {ang_f:.1f}°, {v_f:.1f} m/s = {v_f * 3.6:.0f} km/h")
    G.set_ajustements("reel")


if __name__ == "__main__":
    main()
