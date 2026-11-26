"""Exporte le schéma QElectroTech (Electronique/Schema_Electrique.qet) en PDF vectoriel et en images PNG.

QElectroTech n'a pas d'export en ligne de commande : ce script relit le fichier .qet (symboles, éléments,
fils, textes, cadres) et le redessine avec reportlab, une page par folio. Le résultat ressemble à
Fichier > Exporter de QElectroTech, sans en être la copie exacte (polices, épaisseurs).

    python scripts/exporter_schema.py                 # cas terrestre (28BYJ-48)
    python scripts/exporter_schema.py --nema          # ancien modèle idéal personnel (.modele_ideal_personnel/)

Écrit Schema_Electrique.pdf à côté du .qet, et un PNG par folio dans docs (extra)/electronique/
(schema_electrique.png, brochage_heltec.png, cablage_sections.png ; préfixe nema_ pour --nema).
Nécessite reportlab et pdftoppm (poppler).
"""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEMA = "--nema" in sys.argv
DOSSIER = os.path.join(RACINE, ".modele_ideal_personnel", "Electronique") if NEMA else os.path.join(RACINE, "Electronique")
QET = os.path.join(DOSSIER, "Schema_Electrique.qet")
PDF = os.path.join(DOSSIER, "Schema_Electrique.pdf")
IMAGES = os.path.join(RACINE, ".modele_ideal_personnel", "electronique") if NEMA else os.path.join(RACINE, "docs (extra)", "electronique")
NOMS = ("schema_electrique", "brochage_heltec", "cablage_sections")

POLICES = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Sans", POLICES + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", POLICES + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono", POLICES + "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("Mono-Bold", POLICES + "DejaVuSansMono-Bold.ttf"))
DECAL = {"0": (0, 4), "1": (-4, 0), "2": (0, -4), "3": (4, 0)}      # n, e, s, w : décalage mis dans le .qet


def couleur(c, defaut=(0, 0, 0)):
    c = (c or "").strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{6})", c)
    if not m:
        return defaut
    v = int(m.group(1), 16)
    return ((v >> 16) / 255, ((v >> 8) & 255) / 255, (v & 255) / 255)


def police(desc):
    """'Sans Serif,7,-1,5,75,...' -> (nom reportlab, taille)."""
    p = desc.split(",")
    gras = len(p) > 4 and p[4] == "75"
    mono = p[0].startswith("Mono")
    return ("Mono" if mono else "Sans") + ("-Bold" if gras else ""), float(p[1])


class Rendu:
    def __init__(self, c, h):
        self.c, self.h = c, h

    def y(self, y):
        return self.h - y

    def style(self, st):
        d = dict(kv.split(":", 1) for kv in (st or "").split(";") if ":" in kv)
        c = self.c
        c.setLineWidth({"thin": 0.5, "normal": 1.0, "hight": 1.8}.get(d.get("line-weight", "normal"), 1.0))
        c.setDash(*( ([3, 2], 0) if d.get("line-style") == "dashed" else ([], 0)))
        c.setStrokeColorRGB(0, 0, 0)
        fill = d.get("filling", "none")
        return {"none": None, "white": (1, 1, 1), "black": (0, 0, 0)}.get(fill)

    def prim(self, e, ox, oy):
        c, tag = self.c, e.tag
        a = e.attrib
        f = lambda k: float(a[k])
        fill = self.style(a.get("style"))
        if tag == "line":
            c.line(ox + f("x1"), self.y(oy + f("y1")), ox + f("x2"), self.y(oy + f("y2")))
        elif tag == "rect":
            if fill:
                c.setFillColorRGB(*fill)
            c.rect(ox + f("x"), self.y(oy + f("y") + f("height")), f("width"), f("height"),
                   stroke=1, fill=1 if fill else 0)
        elif tag == "circle":
            d = f("diameter")
            if fill:
                c.setFillColorRGB(*fill)
            c.circle(ox + f("x") + d / 2, self.y(oy + f("y") + d / 2), d / 2, stroke=1, fill=1 if fill else 0)
        elif tag == "polygon":
            pts, i = [], 1
            while f"x{i}" in a:
                pts.append((ox + f(f"x{i}"), self.y(oy + f(f"y{i}"))))
                i += 1
            p = c.beginPath()
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            if a.get("closed") == "true":
                p.close()
            if fill:
                c.setFillColorRGB(*fill)
            c.drawPath(p, stroke=1, fill=1 if fill else 0)
        elif tag == "text":
            nom, taille = police(a["font"])
            c.setFillColorRGB(0, 0, 0)
            c.setFont(nom, taille)
            rot = float(a.get("rotation", 0))
            c.saveState()
            c.translate(ox + f("x"), self.y(oy + f("y")))
            c.rotate(-rot)
            c.drawString(0, 0, a["text"])
            c.restoreState()


def exporter():
    arbre = ET.parse(QET).getroot()
    defs = {}
    for el in arbre.iter("element"):
        d = el.find("definition")
        if d is not None and "name" in el.attrib:
            desc = d.find("description")
            bornes = {t.attrib["name"]: (float(t.attrib["x"]), float(t.attrib["y"]), t.attrib["orientation"])
                      for t in desc.findall("terminal")}
            defs[el.attrib["name"][:-5]] = (list(desc), bornes)
    c = None
    for dg in arbre.findall("diagram"):
        cols, rows = int(dg.attrib["cols"]), int(dg.attrib["rows"])
        W = cols * float(dg.attrib["colsize"]) + 50
        H = rows * float(dg.attrib["rowsize"]) + 70
        if c is None:
            c = canvas.Canvas(PDF, pagesize=(W, H))
        c.setPageSize((W, H))
        c.translate(25, 0)                                  # marge gauche pour les numéros de ligne
        r = Rendu(c, H - 25)
        c.setLineWidth(0.8)
        c.setStrokeColorRGB(0, 0, 0)
        c.rect(0, 25, W - 50, H - 50)
        c.setFont("Sans", 8)
        for i in range(cols):
            c.drawCentredString(30 + 60 * i, H - 12, str(i + 1))
        for j in range(rows):
            c.drawCentredString(-12, r.y(40 + 80 * j), chr(65 + j))
        c.setFont("Sans-Bold", 9)
        c.drawString(10, 12, f"{dg.attrib['title']}  -  {dg.attrib['plant']}  -  {dg.attrib['locmach']}  "
                             f"-  folio {dg.attrib['order']}/3  -  {dg.attrib['author']}")
        # cadres
        for sh in dg.find("shapes"):
            a = sh.attrib
            x1, y1, x2, y2 = (float(a[k]) for k in ("x1", "y1", "x2", "y2"))
            c.setStrokeColorRGB(0.4, 0.4, 0.4)
            c.setLineWidth(0.8)
            c.setDash([4, 3], 0)
            c.rect(x1, r.y(y2), x2 - x1, y2 - y1)
        c.setDash([], 0)
        # éléments : position des bornes pour les fils
        pos = {}
        for el in dg.find("elements"):
            ex, ey = float(el.attrib["x"]), float(el.attrib["y"])
            cle = el.attrib["type"].rsplit("/", 1)[1][:-5]
            prims, bornes = defs[cle]
            for p in prims:
                if p.tag != "terminal":
                    r.prim(p, ex, ey)
            for t in el.find("terminals"):
                o = t.attrib["orientation"]
                dx, dy = DECAL[o]
                pos[t.attrib["id"]] = (ex + float(t.attrib["x"]) - dx, ey + float(t.attrib["y"]) - dy)
            for t in el.find("dynamic_texts"):
                nom, taille = police(t.attrib["font"])
                c.setFillColorRGB(0, 0, 0)
                c.setFont(nom, taille)
                c.drawString(ex + float(t.attrib["x"]), r.y(ey + float(t.attrib["y"]) + taille * 0.95),
                             t.find("text").text or "")
        # fils
        for cd in dg.find("conductors"):
            a = cd.attrib
            x, y = pos[a["terminal1"]]
            pts = [(x, y)]
            longest = (0, None)
            for sg in cd.findall("segment"):
                l = float(sg.attrib["length"])
                nx, ny = (x + l, y) if sg.attrib["orientation"] == "horizontal" else (x, y + l)
                if abs(l) > longest[0]:
                    longest = (abs(l), ((x + nx) / 2, (y + ny) / 2, sg.attrib["orientation"]))
                pts.append((nx, ny))
                x, y = nx, ny
            c.setStrokeColorRGB(*couleur(a.get("color")))
            c.setLineWidth(float(a.get("condsize", 1)))
            c.setDash(*(([4, 3], 0) if "dashed" in a.get("style", "") else ([], 0)))
            p = c.beginPath()
            p.moveTo(pts[0][0], r.y(pts[0][1]))
            for px, py in pts[1:]:
                p.lineTo(px, r.y(py))
            c.drawPath(p, stroke=1, fill=0)
            c.setDash([], 0)
            if a.get("displaytext") == "1" and longest[1]:
                mx, my, ori = longest[1]
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Sans", 5.5)
                if ori == "horizontal":
                    c.drawCentredString(mx, r.y(my) + 2, a.get("num", ""))
                else:
                    c.saveState()
                    c.translate(mx - 2, r.y(my))
                    c.rotate(90)
                    c.drawCentredString(0, 0, a.get("num", ""))
                    c.restoreState()
        # textes libres (HTML : un paragraphe, lignes séparées par <br/>)
        for it in dg.find("inputs"):
            a = it.attrib
            nom, taille = police(a["font"])
            html = a["text"]
            gras = nom.endswith("Bold")
            mono = nom.startswith("Mono")
            html = re.sub(r"<br\s*/?>", "\n", html)
            txt = re.sub(r"<[^>]+>", "", html)
            txt = txt.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            c.setFillColorRGB(0, 0, 0)
            c.setFont(nom, taille)
            y = float(a["y"]) + taille
            for ligne in txt.split("\n"):
                c.drawString(float(a["x"]), r.y(y), ligne)
                y += taille * 1.32
        c.showPage()
    c.save()
    print(f"{PDF}")
    os.makedirs(IMAGES, exist_ok=True)
    prefixe = ""
    for i, nom in enumerate(NOMS, 1):
        base = os.path.join(IMAGES, prefixe + nom)
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PDF, base], check=True)
        print(f"{base}.png")


if __name__ == "__main__":
    exporter()
