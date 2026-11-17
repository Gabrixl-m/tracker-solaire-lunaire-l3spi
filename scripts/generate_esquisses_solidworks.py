#!/usr/bin/env python3
"""
Découpe chaque pièce imprimée du cas terrestre en fonctions SolidWorks à base d'esquisses, puis
écrit les fichiers de données que lit la macro « SolidWorks (esquisses)/Reconstruire_Pieces.bas ».

Méthode, pour chaque pièce de « a_imprimer/ » :
  1. si la pièce est un prisme ou un solide de révolution, une seule fonction suffit ;
  2. sinon elle est coupée en tranches le long d'un axe (Z, X ou Y : celui qui donne le découpage
     le plus simple), aux hauteurs de ses sommets. Une tranche de section constante donne une
     extrusion ; une tranche de section variable (trou en travers, cône) est d'abord remplie ;
  3. ce qui a été rempli en trop est retiré, volume par volume : enlèvement extrudé (le long de
     X, Y, Z ou de l'axe d'un perçage oblique), enlèvement par révolution (cône, fraisure), ou à
     nouveau un empilement (étapes 2 et 3, signe inversé) ;
  4. les filets des deux vis sans fin sont refaits par un balayage le long d'une hélice, avec
     les paramètres du script d'origine (generate_tracker.p_vis) ;
  5. la pièce est reconstruite ici, fonction après fonction, et comparée à l'original. Le volume
     et le centre de gravité attendus après chaque fonction sont écrits dans le fichier : la
     macro s'en sert pour se contrôler.

Format des fichiers « donnees/<pièce>.txt » (cotes en mm, repère de la pièce) :
  PIECE <nom>
  F <ADD|CUT> EXT <dx dy dz> <a0> <a1> <V> <gx gy gz> <tolV> <tolG>   extrusion de a0 à a1 le long de d
  F <ADD|CUT> REV <px py pz> <dx dy dz> <V> <gx gy gz> <tolV> <tolG>   révolution complète autour de l'axe (p, d)
  F ADD HEL <rayon> <pas> <hauteur> <V> <gx gy gz> <tolV> <tolG>      balayage le long d'une hélice d'axe Z,
                                                        qui part du point (rayon, 0, 0) et monte à droite
  P <ox oy oz> <nx ny nz>                               plan de l'esquisse (point, normale)
  W                                                     début d'un contour fermé
  L x1 y1 z1 x2 y2 z2                                   segment
  C cx cy cz r                                          cercle
  A x1 y1 z1 x2 y2 z2 xm ym zm                          arc (début, fin, point milieu)
  S n x1 y1 z1 ... xn yn zn                             courbe passant par n points
  FIN
V, G : volume (mm³) et centre de gravité de la pièce une fois la fonction faite ; tolV, tolG : écarts
admis par la macro sur ces deux valeurs.

Usage : python scripts/generate_esquisses_solidworks.py [pièce ...]
"""
import glob
import math
import os
import sys

import cadquery as cq
from cadquery import Vector
from OCP.BRepAdaptor import BRepAdaptor_Surface

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RACINE, "Fichiers 3D (CAO)", "Cas Terrestre (démonstration)", "a_imprimer")
DOSSIER = os.path.join(RACINE, "SolidWorks (esquisses)")
OUT = os.path.join(DOSSIER, "donnees")
X, Y, Z = Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)
PROF_MAX = 3            # profondeur maximale des empilements imbriqués
VIS = ("Vis_Azimut", "Vis_Elevation")


# ----------------------------------------------------------------------------------------------
# outils géométriques
def perp(d):
    """Un vecteur unitaire perpendiculaire à d (un axe du repère si possible)."""
    for u in (X, Y, Z):
        if abs(u.dot(d)) < 1e-9:
            return u
    u = X if abs(d.x) < 0.9 else Y
    return (u - d * u.dot(d)).normalized()


def aligne(d):
    return max(abs(d.x), abs(d.y), abs(d.z)) > 1 - 1e-9


def canon(d):
    """Sens conventionnel d'une direction (première composante non nulle positive)."""
    d = d.normalized()
    d = Vector(*(0.0 if abs(c) < 1e-9 else c for c in d.toTuple()))
    for c in d.toTuple():
        if abs(c) > 1e-9:
            return d if c > 0 else d * -1
    return d


def etendue(s, d):
    if aligne(d):
        bb = s.BoundingBox()
        i = max(range(3), key=lambda k: abs(d.toTuple()[k]))
        lo, hi = ((bb.xmin, bb.xmax), (bb.ymin, bb.ymax), (bb.zmin, bb.zmax))[i]
        return (lo, hi) if d.toTuple()[i] > 0 else (-hi, -lo)
    axe = d.cross(Z)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, d.dot(Z)))))
    bb = s.rotate(Vector(0, 0, 0), axe, ang).BoundingBox()
    return bb.zmin, bb.zmax


def section(s, d, a):
    """Faces de la section de s par le plan perpendiculaire à d, à l'abscisse a."""
    try:
        pl = cq.Plane(origin=(d * a).toTuple(), xDir=perp(d).toTuple(), normal=d.toTuple())
        r = cq.Workplane(pl).add(s).section()
        return [f for f in r.faces().vals() if f.Area() > 1e-5]
    except Exception:
        return []


def aire(faces):
    return sum(f.Area() for f in faces)


def unir(solides):
    out = None
    for p in solides:
        if p is None:
            continue
        if out is None:
            out = p
            continue
        for tol in (None, 1e-4, 1e-3):                   # faces confondues : union avec tolérance
            try:
                out = out.fuse(p) if tol is None else out.fuse(p, tol=tol)
                break
            except Exception:
                pass
    try:
        return out.clean() if out is not None else None
    except Exception:
        return out


def prisme(faces, d, a0, a1, a_faces):
    """Solide : les faces (situées à l'abscisse a_faces) extrudées de a0 à a1 le long de d."""
    return unir(cq.Solid.extrudeLinear(f.translate(d * (a0 - a_faces)), d * (a1 - a0)) for f in faces)


def vol(s):
    try:
        return s.Volume() if s is not None else 0.0
    except Exception:
        return 0.0


def solides(s, vmin=0.004):
    return [x for x in s.Solids() if x.Volume() > vmin] if s is not None else []


def axes_des_faces(s):
    """Axes (point, direction) des faces cylindriques, coniques, toriques et sphériques de s."""
    out = []
    for f in s.Faces():
        t = f.geomType()
        ad = BRepAdaptor_Surface(f.wrapped)
        if t == "CYLINDER":
            ax = ad.Cylinder().Axis()
        elif t == "CONE":
            ax = ad.Cone().Axis()
        elif t == "TORUS":
            ax = ad.Torus().Axis()
        else:
            continue
        p, d = Vector(ax.Location()), canon(Vector(ax.Direction()))
        p = p - d * p.dot(d)                       # point de l'axe le plus proche de l'origine
        if not any((p - q).Length < 1e-4 and (d - e).Length < 1e-6 for q, e in out):
            out.append((p, d))
    return out


# ----------------------------------------------------------------------------------------------
# fonctions élémentaires : une esquisse plane + une extrusion ou une révolution
def convient(P, R, signe, T):
    """Le solide P peut-il servir à ajouter (ou enlever) R sans sortir de (ou entamer) la pièce T ?"""
    if P is None:
        return False
    eps = max(0.004, 2e-5 * R.Volume())
    if vol(R.cut(P)) > eps:
        return False
    return (vol(P.cut(T)) if signe == "ADD" else vol(P.intersect(T))) < eps


def essai_extrusion(R, signe, T):
    dirs = [Z, X, Y] + [d for _p, d in axes_des_faces(R) if not aligne(d)]
    for d in dirs:
        a0, a1 = etendue(R, d)
        if a1 - a0 < 0.02:
            continue
        am = (a0 + a1) / 2
        faces = section(R, d, am)
        if not faces:
            continue
        P = prisme(faces, d, a0, a1, am)
        if convient(P, R, signe, T):
            return dict(type="EXT", signe=signe, d=d, a0=a0, a1=a1, faces=faces, af=am, solide=P)
    return None


def essai_revolution(R, signe, T):
    for p, d in axes_des_faces(R):
        cands = [u for u in (X, Y, Z) if abs(u.dot(d)) < 1e-9]
        cands.sort(key=lambda u: abs(p.dot(u)))          # de préférence un plan passant par l'origine
        n = cands[0] if cands else perp(d)
        u = n.cross(d)
        try:
            pl = cq.Plane(origin=p.toTuple(), xDir=d.toTuple(), normal=n.toTuple())
            faces = [f for f in cq.Workplane(pl).add(R).section().faces().vals() if f.Area() > 1e-6]
            demi = []
            for f in faces:                               # moitié du côté u > 0
                g = f.intersect(cq.Workplane(cq.Plane(origin=(p + u * 500).toTuple(), xDir=d.toTuple(),
                                                      normal=n.toTuple())).rect(4000, 1000).extrude(1, both=True).val())
                demi += [x for x in g.Faces() if x.Area() > 1e-6]
            if not demi:
                continue
            P = unir(cq.Solid.revolve(f.outerWire(), f.innerWires(), 360, p, p + d) for f in demi)
        except Exception:
            continue
        if convient(P, R, signe, T):
            return dict(type="REV", signe=signe, p=p, d=d, n=n, faces=demi, solide=P)
    return None


def tranches(R, d):
    """Empilement le long de d : [(a0, a1, faces, a_faces)], tranches voisines identiques réunies."""
    a_min, a_max = etendue(R, d)
    niv = {round(v.toTuple()[0] * d.x + v.toTuple()[1] * d.y + v.toTuple()[2] * d.z, 3) for v in R.Vertices()}
    niv |= {round(a_min, 3), round(a_max, 3)}
    for p, e in axes_des_faces(R):                       # génératrices extrêmes des perçages en travers
        if abs(e.dot(d)) < 0.999:
            niv.add(round(p.dot(d), 3))
    niv = sorted(a for a in niv if a_min - 1e-3 <= a <= a_max + 1e-3)
    niv = [a for i, a in enumerate(niv) if i == 0 or a - niv[i - 1] > 0.02]
    zones = []
    for a0, a1 in zip(niv, niv[1:]):
        h = a1 - a0
        ech = [a0 + h * t for t in (0.02, 0.25, 0.5, 0.75, 0.98)]
        secs = [section(R, d, a) for a in ech]
        ar = [aire(f) for f in secs]
        if max(ar) < 1e-4:
            continue
        constante = max(ar) - min(ar) < 1e-4 * max(ar) + 0.002
        if constante:
            pa, pb = prisme(secs[0], d, 0, 1, ech[0]), prisme(secs[4], d, 0, 1, ech[4])
            constante = pa is not None and pb is not None and vol(pa.cut(pb)) + vol(pb.cut(pa)) < 1e-4 * ar[2] + 0.002
        if constante:
            zones.append([a0, a1, secs[2], ech[2], ar[2]])
        else:                                            # section variable : ombre de la tranche
            ech = [a0 + h * t for t in [0.001, 0.999] + [(i + 0.5) / 24 for i in range(24)]]
            plein = unir(prisme(section(R, d, a), d, a0, a1, a) for a in ech)
            am = (a0 + a1) / 2
            f = section(plein, d, am)
            zones.append([a0, a1, f, am, aire(f)])
    reunies = []
    for z in zones:
        if reunies and abs(reunies[-1][1] - z[0]) < 1e-6 and abs(reunies[-1][4] - z[4]) < 1e-4 * z[4] + 0.002:
            pa = prisme(reunies[-1][2], d, 0, 1, reunies[-1][3])
            pb = prisme(z[2], d, 0, 1, z[3])
            if vol(pa.cut(pb)) + vol(pb.cut(pa)) < 1e-4 * z[4] + 0.002:
                reunies[-1][1] = z[1]
                continue
        reunies.append(z)
    return reunies


def empiler(R, signe, T, d):
    tr = tranches(R, d)
    fonctions = [dict(type="EXT", signe=signe, d=d, a0=a0, a1=a1, faces=f, af=af, solide=prisme(f, d, a0, a1, af))
                 for a0, a1, f, af, _ar in tr]
    plein = unir(f["solide"] for f in fonctions)
    reste = plein.cut(T) if signe == "ADD" else plein.intersect(T)   # ajouté ou enlevé en trop
    manque = vol(R.cut(plein))
    return fonctions, plein, solides(reste), manque


def decomposer(R, signe, T, prof=0, axes=(Z, X, Y)):
    """-> (fonctions, volume non traité). Ajoute (ADD) ou enlève (CUT) le solide R, la pièce finale étant T."""
    f = essai_extrusion(R, signe, T) or essai_revolution(R, signe, T)
    if f:
        return [f], 0.0
    if prof >= PROF_MAX:
        return [], R.Volume()
    inverse = "CUT" if signe == "ADD" else "ADD"
    meilleur = None
    for d in axes:
        try:
            fonctions, _plein, restes, manque = empiler(R, signe, T, d)
        except Exception:
            continue
        directs, suite = [], []
        for r in restes:
            g = essai_extrusion(r, inverse, T) or essai_revolution(r, inverse, T)
            (directs if g else suite).append(g or r)
        cout = (round(manque + sum(vol(r) for r in suite), 2), len(fonctions) + len(directs))
        if meilleur is None or cout < meilleur[0]:
            meilleur = (cout, fonctions, directs, suite, manque)
        if cout[0] == 0:
            break
    if meilleur is None:
        return [], R.Volume()
    _cout, fonctions, directs, suite, manque = meilleur
    rate = manque
    fonctions = fonctions + directs
    for r in suite:
        g, v = decomposer(r, inverse, T, prof + 1)
        fonctions += g
        rate += v
    return fonctions, rate


# ----------------------------------------------------------------------------------------------
# vis sans fin : corps empilé, filet balayé le long d'une hélice, puis mise à longueur
def filet(nom, S):
    """-> (S sans son filet, fonction HEL, [volumes à enlever ensuite], hauteur du filet (z0, z1))."""
    import generate_tracker as G
    v = G.VIS_AZ if nom == "Vis_Azimut" else G.VIS_EL
    aj = G.AJUSTEMENTS["petg"]
    m, dp, L = v["m"], v["dp"], v["L"]
    ha = aj["tete_filet"] * m
    rr, h = dp / 2 - 1.25 * m, 1.25 * m + ha
    pas = math.pi * m
    t = pas / 2 - aj["jeu_filet"] * m
    ta = math.tan(math.radians(20))
    w_pied, w_tete = t + 2 * ta * 1.25 * m, t - 2 * ta * ha
    bb = S.BoundingBox()
    zc = (bb.zmin + bb.zmax) / 2
    z0, z1 = zc - L / 2, zc + L / 2
    rmax = rr + h + 0.5
    # corps sans filet : les deux bouts de la pièce, et entre eux un noyau propre (Ø du pied de filet, alésage)
    boite = lambda a, b: cq.Workplane("XY").rect(200, 200).extrude(b - a).val().translate(Z * a)
    alesage = min((w for f in section(S, Z, zc) for w in f.innerWires()), key=lambda w: w.BoundingBox().xlen)
    noyau = cq.Face.makeFromWires(cq.Wire.makeCircle(rr, Vector(0, 0, zc), Z), [alesage])
    corps = unir([S.intersect(boite(bb.zmin - 1, z0)), prisme([noyau], Z, z0, z1, zc), S.intersect(boite(z1, bb.zmax + 1))])
    haut = math.ceil((z1 + pas) * 10) / 10
    helice = cq.Wire.makeHelix(pitch=pas, height=haut, radius=rr, center=Vector(0, 0, 0))
    pts = [(rr - 0.3, -w_pied / 2), (rr + h, -w_tete / 2), (rr + h, w_tete / 2), (rr - 0.3, w_pied / 2)]
    prof = cq.Workplane("XZ").polyline(pts).close()
    balaye = prof.sweep(cq.Workplane().add(helice), isFrenet=True).val()
    face = cq.Face.makeFromWires(cq.Wire.makePolygon([Vector(x, 0, z) for x, z in pts], close=True))
    hel = dict(type="HEL", signe="ADD", r=rr, pas=pas, haut=haut, faces=[face], solide=balaye)
    return corps, hel, dict(rmax=rmax, bas=(-w_pied, z0), haut=(z1, haut + w_pied), pas=pas, zc=zc, L=L,
                            r0=rr - 0.3, r1=rr + h, w0=w_pied, w1=w_tete, h_helice=haut)


def etats_filet(ajouts, coupes, g, v_corps, m_corps):
    """Volume et centre de gravité après le balayage du filet, puis après chaque enlèvement de mise à
    longueur, par intégration numérique en coordonnées cylindriques (les opérations booléennes du
    noyau géométrique sur le solide balayé ne sont pas fiables). -> [(V, G)], moment du filet en miroir."""
    import numpy as np
    nr, nt, dz = 200, 1440, 0.004
    zs = np.arange(g["bas"][0] - 0.5, g["haut"][1] + 0.5, dz) + dz / 2
    th = (np.arange(nt) + 0.5) * 2 * math.pi / nt
    tours = int(g["h_helice"] / g["pas"]) + 2
    acc = np.zeros((len(coupes) + 1, 4))                  # par « premier enlèvement qui retire la cellule »
    for i in range(nr):
        r = g["r0"] + (g["r1"] - g["r0"]) * (i + 0.5) / nr
        hw = (g["w0"] + (g["w1"] - g["w0"]) * (r - g["r0"]) / (g["r1"] - g["r0"])) / 2
        dans = np.zeros((nt, len(zs)), dtype=bool)
        for k in range(tours):                            # le profil suit l'hélice : z = pas·(θ/2π + k)
            zc = g["pas"] * (th / (2 * math.pi) + k)
            ok = zc <= g["h_helice"] + 1e-9
            dans |= ok[:, None] & (np.abs(zs[None, :] - zc[:, None]) <= hw)
        plein = np.zeros(len(zs), dtype=bool)
        for f in ajouts:
            if f["faces"][0].outerWire().BoundingBox().xlen / 2 > r:
                plein |= (zs >= f["a0"]) & (zs < f["a1"])
        dans &= ~plein[None, :]
        qui = np.full(len(zs), len(coupes))
        for j in reversed(range(len(coupes))):
            c = coupes[j]
            ri = min((w.BoundingBox().xlen / 2 for w in c["faces"][0].innerWires()), default=0.0)
            if ri < r:
                qui[(zs >= c["a0"]) & (zs < c["a1"])] = j
        dv = r * (g["r1"] - g["r0"]) / nr * (2 * math.pi / nt) * dz
        for j in range(len(coupes) + 1):
            m = dans[:, qui == j]
            zz = zs[qui == j]
            n_t = m.sum(axis=1)
            acc[j] += dv * np.array([m.sum(), (n_t * r * np.cos(th)).sum(), (n_t * r * np.sin(th)).sum(), (m * zz[None, :]).sum()])
    etats = []
    for j in range(len(coupes) + 1):                      # j enlèvements faits : restent les cellules des suivants
        e = acc[j:].sum(axis=0)
        V = v_corps + e[0]
        etats.append((V, (m_corps + Vector(e[1], e[2], e[3])) / V))
    return etats, acc[-1]




def mise_a_longueur(ajouts, g, zmin):
    """Enlèvements annulaires (autour de chaque tranche du corps) qui coupent le filet hors de sa zone."""
    out = []

    def anneau(ri, a0, a1):
        am = (a0 + a1) / 2
        ext = cq.Wire.makeCircle(g["rmax"], Vector(0, 0, am), Z)
        face = cq.Face.makeFromWires(ext, [cq.Wire.makeCircle(ri, Vector(0, 0, am), Z)] if ri > 0 else [])
        out.append(dict(type="EXT", signe="CUT", d=Z, a0=a0, a1=a1, faces=[face], af=am,
                        solide=prisme([face], Z, a0, a1, am)))

    anneau(0, g["bas"][0], zmin)                          # sous la pièce
    for lo, hi in (g["bas"], g["haut"]):
        for f in ajouts:
            a0, a1 = max(f["a0"], lo), min(f["a1"], hi)
            ri = f["faces"][0].outerWire().BoundingBox().xlen / 2
            if a1 - a0 > 1e-6 and ri < g["rmax"] - 1e-6:
                anneau(ri, a0, a1)
    return out


# ----------------------------------------------------------------------------------------------
# écriture
def nb(x):
    s = f"{x:.5f}"
    return "0.00000" if s == "-0.00000" else s


def pt(p):
    return f"{nb(p.x)} {nb(p.y)} {nb(p.z)}"


def contours(faces, decal):
    """Lignes des contours des faces, ramenées dans le plan de l'esquisse (translation decal)."""
    lignes = []
    for f in faces:
        for w in [f.outerWire()] + list(f.innerWires()):
            lignes.append("W")
            for e in w.Edges():
                t = e.geomType()
                p0, p1 = e.startPoint() + decal, e.endPoint() + decal
                ferme = (p0 - p1).Length < 1e-6
                if t == "LINE":
                    lignes.append(f"L {pt(p0)} {pt(p1)}")
                elif t == "CIRCLE" and ferme:
                    lignes.append(f"C {pt(e.arcCenter() + decal)} {nb(e.radius())}")
                elif t == "CIRCLE":
                    lignes.append(f"A {pt(p0)} {pt(p1)} {pt(e.positionAt(0.5) + decal)}")
                else:                              # autre courbe : courbe passant par des points
                    k = max(6, min(40, int(e.Length() / 0.5) + 4))
                    for u0, u1 in (((0, 0.5), (0.5, 1)) if ferme else ((0, 1),)):
                        ps = [e.positionAt(u0 + (u1 - u0) * i / k) + decal for i in range(k + 1)]
                        lignes.append(f"S {len(ps)} " + " ".join(pt(p) for p in ps))
    return lignes


def ecrire(nom, fonctions):
    """Rejoue les fonctions, écrit le fichier de données -> solide reconstruit."""
    lignes, corps, v_prec = [f"PIECE {nom}"], None, 0.0
    for f in fonctions:
        if "etat" in f:                                   # état calculé à part (filets)
            v, g = f["etat"]
        else:
            if f["signe"] == "ADD":
                corps = f["solide"] if corps is None else corps.fuse(f["solide"])
            else:
                corps = corps.cut(f["solide"])
            corps = corps.clean()
            v, g = corps.Volume(), corps.Center()
        # tolérances du contrôle fait par la macro : volume (mm³) et centre de gravité (mm)
        tol_v = max(0.02, 0.03 * abs(v - v_prec)) + 1e-4 * v + f.get("tol_v", 0.0)
        etat = f"{v:.4f} {pt(g)} {tol_v:.4f} 0.01500"
        v_prec = v
        if f["type"] == "EXT":
            d = f["d"]
            lignes.append(f"F {f['signe']} EXT {pt(d)} {nb(f['a0'])} {nb(f['a1'])} {etat}")
            lignes.append(f"P {pt(Vector(0, 0, 0))} {pt(d)}")
            lignes += contours(f["faces"], d * -f["af"])
        elif f["type"] == "REV":
            lignes.append(f"F {f['signe']} REV {pt(f['p'])} {pt(f['d'])} {etat}")
            lignes.append(f"P {pt(f['p'])} {pt(f['n'])}")
            lignes += contours(f["faces"], Vector(0, 0, 0))
        else:
            lignes.append(f"F ADD HEL {nb(f['r'])} {nb(f['pas'])} {nb(f['haut'])} {etat}")
            lignes.append(f"P {pt(Vector(0, 0, 0))} {pt(Y)}")
            lignes += contours(f["faces"], Vector(0, 0, 0))
    lignes.append("FIN")
    with open(os.path.join(OUT, nom + ".txt"), "w", encoding="ascii", newline="\r\n") as fic:
        fic.write("\n".join(lignes) + "\n")
    return corps


def difference(a, b):
    """Volume de la différence symétrique de a et b (mm³) = 2·V(a ∪ b) − V(a) − V(b).
    Les opérations booléennes sans tolérance échouent parfois sur des faces confondues : on les
    refait avec une tolérance, et on retient le plus petit résultat (une opération ratée donne trop)."""
    va, vb, res = a.Volume(), b.Volume(), []
    for tol in (None, 1e-4, 1e-3):
        try:
            u = a.fuse(b) if tol is None else a.fuse(b, tol=tol)
            res.append(abs(2 * u.Volume() - va - vb))
        except Exception:
            pass
    return min(res) if res else float("nan")


def traiter(chemin):
    nom = os.path.splitext(os.path.basename(chemin))[0]
    S = cq.importers.importStep(chemin).val()
    note = ""
    attendu = None
    if nom in VIS:
        corps, hel, g = filet(nom, S)
        fonctions, rate = decomposer(corps, "ADD", corps, axes=(Z,))
        ajouts = [f for f in fonctions if f["signe"] == "ADD"]
        coupes = mise_a_longueur(ajouts, g, S.BoundingBox().zmin)
        avant = None
        for f in fonctions:
            avant = f["solide"] if avant is None else (avant.fuse(f["solide"]) if f["signe"] == "ADD" else avant.cut(f["solide"]))
        m_avant = avant.Center() * avant.Volume()
        etats, e_fin = etats_filet(ajouts, coupes, g, avant.Volume(), m_avant)
        suite, v_prec = [], None
        for f, e in zip([hel] + coupes, etats):
            if v_prec is None or v_prec - e[0] > 0.01:    # un enlèvement qui ne retire rien est inutile
                f["etat"], f["tol_v"] = e, 2.0
                suite.append(f)
                v_prec = e[0]
        fonctions += suite
        # contrôle indépendant de l'état final : le filet de la pièce d'origine, tourné autour de Z
        m_filet = S.Center() * S.Volume() - m_avant
        ang = 2 * math.pi * (g["zc"] - g["L"] / 2 - g["pas"]) / g["pas"]
        c, s = math.cos(ang), math.sin(ang)
        g_ind = (m_avant + Vector(c * m_filet.x - s * m_filet.y, s * m_filet.x + c * m_filet.y, m_filet.z)) / S.Volume()
        g_miroir = (m_avant + Vector(e_fin[1], -e_fin[2], e_fin[3])) / etats[-1][0]
        attendu = (S.Volume(), g_ind, g_miroir, etats[-1])
        note = " ; filet identique, décalé en rotation autour de l'axe"
    else:
        fonctions, rate = decomposer(S, "ADD", S)
    corps = ecrire(nom, fonctions)
    if attendu:                                           # le filet est tourné : comparer au calcul indépendant
        ecart = abs(attendu[3][0] - attendu[0])
        note += (f" ; centre de gravité à {(attendu[3][1] - attendu[1]).Length:.4f} mm du calcul indépendant"
                 f" (un filet à gauche serait à {(attendu[2] - attendu[3][1]).Length:.3f} mm)")
    else:
        ecart = difference(corps, S)
    n = {k: sum(1 for f in fonctions if f["type"] == k[0] and f["signe"] == k[1])
         for k in (("EXT", "ADD"), ("EXT", "CUT"), ("REV", "ADD"), ("REV", "CUT"), ("HEL", "ADD"))}
    obl = sum(1 for f in fonctions if f["type"] == "EXT" and not aligne(f["d"]))
    print(f"{nom:26s} {len(fonctions):3d} fonctions (extrusions +{n[('EXT', 'ADD')]} -{n[('EXT', 'CUT')]}"
          f", révolutions +{n[('REV', 'ADD')]} -{n[('REV', 'CUT')]}, hélice {n[('HEL', 'ADD')]}, obliques {obl}) ; "
          f"écart {ecart:8.3f} mm³ sur {S.Volume():8.0f} ({100 * ecart / S.Volume():.3f} %) ; non traité {rate:.3f} mm³{note}",
          flush=True)
    return dict(nom=nom, n=len(fonctions), ecart=ecart, volume=S.Volume(), rate=rate, detail=n, obliques=obl)


def main():
    os.makedirs(OUT, exist_ok=True)
    noms = sys.argv[1:]
    chemins = sorted(glob.glob(os.path.join(SRC, "*.step")))
    if noms:
        chemins = [c for c in chemins if os.path.splitext(os.path.basename(c))[0] in noms]
    return [traiter(c) for c in chemins]


if __name__ == "__main__":
    main()
