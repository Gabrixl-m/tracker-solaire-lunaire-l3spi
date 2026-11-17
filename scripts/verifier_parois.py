"""Contrôle des épaisseurs de paroi des pièces imprimées (cas terrestre).

Coupe la pièce en tranches, en fait un volume de voxels et repère la matière qu'une sphère de
diamètre T ne peut pas parcourir (zones plus minces que T), en écartant les liserés d'arêtes
vives et les zones de moins de 1 mm3.

Utilisation : python scripts/verifier_parois.py <pas en mm> <T en mm> <pièce> [<pièce> ...]
Exemple     : python scripts/verifier_parois.py 0.15 1.6 Palier_Vis_Azimut Socle
Les pièces dentées (Vis_*, Roue_*) sont à exclure : leurs dents sont minces par nature. Pas de
0,1 à 0,2 mm ; lancer les grosses pièces une par une (mémoire).
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cadquery as cq
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import generate_tracker as G, generate_tete_vis_sans_fin as T

PX = float(sys.argv[1]) if sys.argv[1].replace(".","").isdigit() else 0.2
def poly(w):
    n = max(8, int(w.Length() / (PX * 1.5)))
    return [w.positionAt(i / n) for i in range(n)]
def voxels(s):
    b = s.BoundingBox(); lo = (b.xmin - 1, b.ymin - 1, b.zmin - 1)
    W = int((b.xlen + 2) / PX) + 1; H = int((b.ylen + 2) / PX) + 1; D = int((b.zlen + 2) / PX) + 1
    vol = np.zeros((D, H, W), dtype=bool)
    for k in range(D):
        z = lo[2] + (k + 0.5) * PX
        try:
            r = cq.Workplane("XY", origin=(0, 0, z)).add(s).section()
            faces = [f for f in r.faces().vals() if f.Area() > 1e-4]
        except Exception:
            continue
        if not faces: continue
        img = Image.new("L", (W, H), 0); d = ImageDraw.Draw(img)
        for f in faces:
            for j, w in enumerate([f.outerWire()] + list(f.innerWires())):
                p = [((v.x - lo[0]) / PX, (v.y - lo[1]) / PX) for v in poly(w)]
                if len(p) >= 3: d.polygon(p, fill=255 if j == 0 else 0)
        vol[k] = np.array(img) > 0
    return vol, lo
def analyser(nom, Tmm):
    s = G.PARTS[nom][0].val()
    vol, lo = voxels(s)
    edt = ndi.distance_transform_edt(vol).astype(np.float32)
    r = (Tmm / 2) / PX - 0.5
    coeur = edt >= r
    ouv = ndi.distance_transform_edt(~coeur).astype(np.float32) <= r
    mince = vol & ~ouv & (edt >= 0.40 / PX)               # écarte les liserés des arêtes vives
    del ouv, coeur
    lab, n = ndi.label(mince, structure=np.ones((3, 3, 3)))
    out = []
    if n:
        objs = ndi.find_objects(lab)
        for k, sl in enumerate(objs, 1):
            zone = lab[sl] == k
            v = zone.sum() * PX ** 3
            ep = 2 * edt[sl][zone].max() * PX
            if v < 1.0: continue
            zz, yy, xx = np.nonzero(zone)
            c = (lo[0] + (sl[2].start + xx.mean() + 0.5) * PX, lo[1] + (sl[1].start + yy.mean() + 0.5) * PX, lo[2] + (sl[0].start + zz.mean() + 0.5) * PX)
            out.append((ep, v, c, (xx.max() - xx.min() + 1) * PX, (yy.max() - yy.min() + 1) * PX, (zz.max() - zz.min() + 1) * PX))
    return sorted(out, key=lambda t: (round(t[0], 1), -t[1]))
if __name__ == "__main__":
    G.set_ajustements("petg"); T.build_parts()
    Tmm = float(sys.argv[2])
    for nom in sys.argv[3:]:
        r = analyser(nom, Tmm)
        print(f"## {nom} : zones plus minces que {Tmm} mm (épaisseur, volume, centre, étendue x/y/z) : {len(r)}", flush=True)
        for ep, v, c, ex, ey, ez in r[:12]:
            print(f"   ~{ep:.2f} mm ; {v:6.1f} mm3 ; centre ({c[0]:.1f}, {c[1]:.1f}, {c[2]:.1f}) ; {ex:.1f} x {ey:.1f} x {ez:.1f} mm", flush=True)
