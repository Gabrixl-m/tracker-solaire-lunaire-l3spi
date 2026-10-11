"""Schéma électrique du tracker (démonstration sur Terre), au format QElectroTech.

Écrit Electronique/Schema_Electrique.qet : un projet QElectroTech 0.9 (s'ouvre aussi dans les
versions suivantes) avec deux folios :
  1. le schéma complet : alimentation 12 V / 5 V, Heltec WiFi LoRa 32 V4, 2 drivers TMC2209
     et leurs moteurs, capteur solaire (4 BPW34 + ADS1115), fin de course et capteur à effet Hall ;
  2. le brochage du Heltec V4, les câbles entre le boîtier et la tête, les données envoyées en LoRa.

Les symboles (norme IEC) sont dessinés ici et intégrés au projet : le fichier ne dépend d'aucune
bibliothèque d'éléments installée. Les fils sont tracés à l'équerre, sur la grille de 10 px.

Pour exporter les images et le PDF, ouvrir le projet dans QElectroTech : Fichier > Exporter
(PNG) et Fichier > Exporter en PDF.
"""
import os
import uuid
from xml.sax.saxutils import escape, quoteattr

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "Electronique", "Schema_Electrique.qet")

# uuid stables d'une génération à l'autre (diff git lisible)
_NS = uuid.UUID("6b3c1f2e-8d1a-4c55-9a4e-2f1f6c7d9e01")


def uid(*cle):
    return "{%s}" % uuid.uuid5(_NS, "/".join(str(c) for c in cle))


# ---------------------------------------------------------------------------
# SYMBOLES (définitions d'éléments QElectroTech)

TRAIT = "line-style:normal;line-weight:normal;filling:none;color:black"
FIN = "line-style:normal;line-weight:thin;filling:none;color:black"
PLEIN = "line-style:normal;line-weight:normal;filling:black;color:black"
BLANC = "line-style:normal;line-weight:normal;filling:white;color:black"
TIRETS = "line-style:dashed;line-weight:thin;filling:none;color:black"
ORI = {"n": 0, "e": 1, "s": 2, "w": 3}
POLICE = "Sans Serif,{},-1,5,50,0,0,0,0,0"
POLICE_GRAS = "Sans Serif,{},-1,5,75,0,0,0,0,0"


def q(v):
    return f"{v:g}"


class Symbole:
    """Définition d'un élément : primitives graphiques + bornes nommées."""

    def __init__(self, cle, nom):
        self.cle, self.nom = cle, nom
        self.prims, self.bornes = [], {}
        self.xs, self.ys = [0.0], [0.0]

    def _bb(self, *pts):
        for x, y in pts:
            self.xs.append(x)
            self.ys.append(y)

    def ligne(self, x1, y1, x2, y2, style=TRAIT, fin2="none"):
        self.prims.append(f'<line x1="{q(x1)}" y1="{q(y1)}" x2="{q(x2)}" y2="{q(y2)}" end1="none" '
                          f'end2="{fin2}" length1="1.5" length2="3" antialias="true" style="{style}"/>')
        self._bb((x1, y1), (x2, y2))

    def rect(self, x, y, w, h, style=TRAIT):
        self.prims.append(f'<rect x="{q(x)}" y="{q(y)}" width="{q(w)}" height="{q(h)}" rx="0" ry="0" '
                          f'antialias="false" style="{style}"/>')
        self._bb((x, y), (x + w, y + h))

    def cercle(self, cx, cy, d, style=TRAIT):
        self.prims.append(f'<circle x="{q(cx - d / 2)}" y="{q(cy - d / 2)}" diameter="{q(d)}" '
                          f'antialias="true" style="{style}"/>')
        self._bb((cx - d / 2, cy - d / 2), (cx + d / 2, cy + d / 2))

    def poly(self, pts, ferme=True, style=TRAIT):
        a = " ".join(f'x{i + 1}="{q(x)}" y{i + 1}="{q(y)}"' for i, (x, y) in enumerate(pts))
        self.prims.append(f'<polygon {a} closed="{"true" if ferme else "false"}" antialias="true" '
                          f'style="{style}"/>')
        self._bb(*pts)

    def texte(self, x, y, t, taille=7, gras=False, rot=0):
        """Texte statique, (x, y) = début de la ligne de base."""
        police = (POLICE_GRAS if gras else POLICE).format(taille)
        self.prims.append(f'<text x="{q(x)}" y="{q(y)}" text={quoteattr(t)} font="{police}" '
                          f'rotation="{rot}" color="#000000"/>')
        lg = 0.62 * taille * len(t)
        if rot == 0:
            self._bb((x, y - taille * 1.2), (x + lg, y + 2))
        else:
            self._bb((x - taille * 1.2, y - lg), (x + 2, y))

    def borne(self, nom, x, y, o, patte=0):
        """Borne en (x, y), orientée vers l'extérieur ; patte : longueur du trait vers l'intérieur."""
        self.bornes[nom] = (x, y, o)
        if patte:
            dx, dy = {"n": (0, 1), "s": (0, -1), "e": (-1, 0), "w": (1, 0)}[o]
            self.ligne(x, y, x + dx * patte, y + dy * patte)
        self._bb((x, y))

    def xml(self):
        x0 = int(min(self.xs) // 10 * 10 - 10)
        y0 = int(min(self.ys) // 10 * 10 - 10)
        x1 = int(-(-max(self.xs) // 10) * 10 + 10)
        y1 = int(-(-max(self.ys) // 10) * 10 + 10)
        bornes = [f'<terminal x="{q(x)}" y="{q(y)}" orientation="{o}" name={quoteattr(n)} type="Generic" '
                  f'uuid="{uid(self.cle, "borne", n)}"/>' for n, (x, y, o) in self.bornes.items()]
        return (f'<definition type="element" version="0.90" link_type="simple" width="{x1 - x0}" '
                f'height="{y1 - y0}" hotspot_x="{-x0}" hotspot_y="{-y0}">'
                f'<uuid uuid="{uid(self.cle, "definition")}"/>'
                f'<names><name lang="fr">{escape(self.nom)}</name><name lang="en">{escape(self.nom)}</name></names>'
                f'<elementInformations/><informations>Tracker solaire lunaire : symbole dessiné par '
                f'scripts/generate_schema_electrique.py</informations>'
                f'<description>{"".join(self.prims + bornes)}</description></definition>')


SYM = {}


def symbole(cle, nom):
    s = Symbole(cle, nom)
    SYM[cle] = s
    return s


def faire_symboles():
    # --- passifs, verticaux : bornes en haut (1) et en bas (2) -----------------------
    s = symbole("resistance", "Résistance")
    s.rect(-5, -15, 10, 30)
    s.borne("1", 0, -20, "n", 5)
    s.borne("2", 0, 20, "s", 5)

    s = symbole("condensateur", "Condensateur")
    s.ligne(-10, -3, 10, -3)
    s.ligne(-10, 3, 10, 3)
    s.borne("1", 0, -20, "n", 17)
    s.borne("2", 0, 20, "s", 17)

    s = symbole("condensateur_polarise", "Condensateur polarisé")
    s.ligne(-10, -3, 10, -3)
    s.rect(-10, 2, 20, 3, PLEIN)
    s.ligne(-9, -10, -5, -10)
    s.ligne(-7, -12, -7, -8)
    s.borne("+", 0, -20, "n", 17)
    s.borne("-", 0, 20, "s", 15)

    s = symbole("photodiode", "Photodiode")            # cathode en haut
    s.poly([(-7, 6), (7, 6), (0, -6)])
    s.ligne(-7, -6, 7, -6)
    for dy in (-12, -4):                               # rayons lumineux entrants
        s.ligne(-22, dy - 9, -11, dy, FIN, "simple")
    s.borne("K", 0, -20, "n", 14)
    s.borne("A", 0, 20, "s", 14)

    # --- deux bornes, horizontaux : gauche (1) et droite (2) -------------------------
    s = symbole("schottky", "Diode Schottky")         # anode à gauche
    s.poly([(-6, -7), (-6, 7), (6, 0)])
    s.poly([(3, -9), (3, -7), (6, -7), (6, 7), (9, 7), (9, 9)], ferme=False)
    s.borne("A", -20, 0, "w", 14)
    s.borne("K", 20, 0, "e", 14)

    s = symbole("fusible", "Fusible")
    s.rect(-15, -5, 30, 10)
    s.ligne(-20, 0, 20, 0)
    s.borne("1", -20, 0, "w")
    s.borne("2", 20, 0, "e")

    s = symbole("interrupteur", "Interrupteur")
    s.ligne(-20, 0, -10, 0)
    s.ligne(-10, 0, 10, -9)
    s.ligne(10, 0, 20, 0)
    s.ligne(10, 0, 10, -4)
    s.borne("1", -20, 0, "w")
    s.borne("2", 20, 0, "e")

    # --- source, alimentations, masse, jonction --------------------------------------
    s = symbole("batterie", "Source 12 V")
    for y0 in (-12, 4):
        s.ligne(-14, y0, 14, y0)
        s.rect(-8, y0 + 4, 16, 3, PLEIN)
    s.ligne(0, -30, 0, -12)
    s.ligne(0, 11, 0, 30)
    s.ligne(0, -4, 0, 4, TIRETS)
    s.texte(8, -18, "+", 9, True)
    s.borne("+", 0, -30, "n")
    s.borne("-", 0, 30, "s")

    for cle, t in (("p12", "+12 V"), ("p5", "+5 V"), ("p33", "+3,3 V")):
        s = symbole(cle, f"Alimentation {t}")
        s.ligne(-10, 0, 10, 0)
        s.ligne(0, 0, 0, 10)
        s.texte(-3 * len(t) + 1, -4, t, 7, True)
        s.borne("1", 0, 10, "s")

    s = symbole("masse", "Masse (0 V)")
    s.ligne(0, -10, 0, 0)
    s.ligne(-10, 0, 10, 0)
    s.ligne(-6, 4, 6, 4)
    s.ligne(-2, 8, 2, 8)
    s.borne("1", 0, -10, "n")

    s = symbole("jonction", "Jonction")
    s.cercle(0, 0, 5, PLEIN)
    for o, (x, y) in (("n", (0, -2)), ("s", (0, 2)), ("e", (2, 0)), ("w", (-2, 0))):
        s.borne(o, x, y, o)

    # --- modules ---------------------------------------------------------------------
    s = symbole("heltec", "Heltec WiFi LoRa 32 V4")
    s.rect(-120, -160, 240, 320, BLANC)
    s.texte(-108, -112, "Heltec WiFi LoRa 32 V4", 9, True)
    s.texte(-108, -98, "ESP32-S3 + radio LoRa SX1262", 6)
    s.texte(-108, -88, "(863-870 MHz), écran OLED, USB-C", 6)
    for txt, n, y in (("GPIO47  J2-13", "STEP_EL", -100), ("GPIO43  J2-6", "DIR_EL", -80),
                      ("GPIO33  J2-12", "EN", 0), ("GPIO48  J2-14", "STEP_AZ", 40),
                      ("GPIO45  J3-6", "DIR_AZ", 60)):
        s.texte(112 - 3.75 * len(txt), y + 3, txt, 6)
        s.borne(n, 140, y, "e", 20)
    for txt, n, y in (("5V  J2-2", "5V", -60), ("3V3  J3-2", "3V3", -40)):
        s.texte(-114, y + 3, txt, 6)
        s.borne(n, -140, y, "w", 20)
    for txt, n, x in (("ANT", "ANT", -20), ("GNSS", "GNSS", 60)):
        s.texte(x + 4, -150 + 3.9 * len(txt), txt, 6, rot=-90)
        s.borne(n, x, -180, "n", 20)
    for txt, n, x, broche in (("GND", "GND", -100, "J2-1"), ("GPIO3  SDA", "SDA", -60, "J3-14"),
                              ("GPIO4  SCL", "SCL", -20, "J3-15"), ("GPIO44  FDC_EL", "FDC_EL", 40, "J2-5"),
                              ("GPIO6  HALL_AZ", "HALL_AZ", 80, "J3-17")):
        s.texte(x + 4, 152, txt, 6, rot=-90)
        s.texte(x - 4, 200, broche, 6, rot=-90)
        s.borne(n, x, 180, "s", 20)
    s.texte(-108, -14, "GPIO réservés par la carte :", 6, True)
    for i, t in enumerate(("0 bouton PRG, 1 mesure batterie,", "2, 5, 7, 46 ampli radio,",
                           "8 à 14 radio SX1262,", "17, 18, 21 OLED, 19, 20 USB,",
                           "26 PSRAM, 35 LED, 36 Vext,", "37 mesure, 34 et 38 à 42 GNSS")):
        s.texte(-108, -2 + 10 * i, t, 6)

    for cle, ordre in (("tmc2209", ("STEP", "DIR", "EN")), ("tmc2209_b", ("EN", "STEP", "DIR"))):
        s = symbole(cle, "Driver TMC2209")
        s.rect(-60, -70, 120, 140, BLANC)
        s.texte(-40, 34, "TMC2209", 8, True)
        s.texte(-40, 46, "module StepStick", 6)
        for n, y in zip(ordre, (-40, -20, 0)):
            s.texte(-54, y + 3, n, 6)
            s.borne(n, -80, y, "w", 20)
        for n, y in (("1A", -10), ("1B", 10), ("2A", 30), ("2B", 50)):
            s.texte(42, y + 3, n, 6)
            s.borne(n, 80, y, "e", 20)
        for n, x in (("VIO", -40), ("MS1", -20), ("MS2", 0), ("VM", 40)):
            s.texte(x + 3, -66 + 3.9 * len(n), n, 6, rot=-90)
            s.borne(n, x, -90, "n", 20)
        for n, x, t in (("PDN_UART", -40, "PDN"), ("GND", -10, "GND"), ("GNDM", 20, "GND")):
            s.texte(x + 3, 66, t, 6, rot=-90)
            s.borne(n, x, 90, "s", 20)

    s = symbole("moteur_pas", "Moteur pas à pas")
    s.cercle(0, 0, 70)
    s.texte(-9, 2, "M", 14, True)
    s.poly([(-14, 16), (-14, 10), (-7, 10), (-7, 16), (0, 16), (0, 10), (7, 10), (7, 16), (14, 16)],
           ferme=False, style=FIN)
    for n, t, y in (("A+", "A+", -30), ("A-", "A-", -10), ("B+", "B+", 10), ("B-", "B-", 30)):
        xe = -(35 ** 2 - y ** 2) ** 0.5
        s.ligne(-60, y, xe, y)
        s.texte(-56, y - 2, t, 6)
        s.borne(n, -60, y, "w")

    s = symbole("lm2596", "Abaisseur LM2596")
    s.rect(-50, -40, 100, 80, BLANC)
    s.texte(-26, -20, "LM2596", 9, True)
    s.texte(-38, -8, "abaisseur réglable", 6)
    for n, t, y in (("IN+", "IN+", 10), ("IN-", "IN-", 30)):
        s.texte(-46, y + 3, t, 6)
        s.borne(n, -70, y, "w", 20)
    for n, t, y in (("OUT+", "OUT+", 10), ("OUT-", "OUT-", 30)):
        s.texte(22, y + 3, t, 6)
        s.borne(n, 70, y, "e", 20)

    s = symbole("ads1115", "Convertisseur ADS1115")
    s.rect(-50, -70, 100, 140, BLANC)
    s.texte(-44, -40, "ADS1115", 8, True)
    s.texte(-44, -28, "16 bits, I2C 0x48", 6)
    for n, y in (("A3", -10), ("A2", 10), ("A1", 30), ("A0", 50)):
        s.texte(-44, y + 3, n, 6)
        s.borne(n, -70, y, "w", 20)
    for n, y in (("VDD", -50), ("SDA", -30), ("SCL", -10), ("GND", 10), ("ADDR", 30), ("ALRT", 50)):
        s.texte(46 - 4 * len(n), y + 3, n, 6)
        s.borne(n, 70, y, "e", 20)

    s = symbole("hall", "Capteur à effet Hall A3144")
    s.rect(-30, -30, 60, 60, BLANC)
    s.rect(-16, -6, 20, 20, FIN)
    s.ligne(-16, -6, 4, 14, FIN)
    s.ligne(-16, 14, 4, -6, FIN)
    s.texte(-26, -18, "VCC", 6)
    s.texte(4, 26, "GND", 6)
    s.texte(9, 3, "OUT", 6)
    s.borne("VCC", -10, -50, "n", 20)
    s.borne("GND", 10, 50, "s", 20)
    s.borne("OUT", 50, 0, "e", 20)

    s = symbole("fin_course", "Fin de course (micro-rupteur)")
    s.ligne(0, 40, 0, 14)                              # commun
    s.cercle(0, 14, 3, PLEIN)
    s.ligne(0, 14, -15, -13)                           # lame au repos sur NC
    s.ligne(-20, -40, -20, -14)                        # contact NC
    s.ligne(-20, -14, -12, -14)
    s.ligne(20, -40, 20, -20)                          # contact NO
    s.ligne(20, -20, 9, -20)
    s.ligne(-7, 0, 22, 0, TIRETS)                      # levier
    s.cercle(27, 0, 10)
    s.texte(4, 34, "C", 6)
    s.texte(-34, -28, "NC", 6)
    s.texte(23, -28, "NO", 6)
    s.borne("C", 0, 40, "s")
    s.borne("NC", -20, -40, "n")
    s.borne("NO", 20, -40, "n")

    s = symbole("antenne", "Antenne")
    s.ligne(0, 20, 0, -10)
    s.poly([(-10, -20), (10, -20), (0, -6)], ferme=True)
    s.borne("1", 0, 20, "s")

    s = symbole("gnss", "Module GNSS L76K")
    s.rect(-60, -25, 120, 50, "line-style:dashed;line-weight:normal;filling:white;color:black")
    s.texte(-54, -8, "Module GNSS L76K", 7, True)
    s.texte(-54, 4, "facultatif : heure et position", 6)
    s.texte(-54, 13, "pour le calcul du Soleil", 6)
    s.borne("1", 0, 45, "s", 20)


# ---------------------------------------------------------------------------
# FOLIO : éléments placés, fils, textes, cadres

class Instance:
    def __init__(self, folio, sym, ref, x, y, textes=()):
        self.f, self.s, self.ref, self.x, self.y = folio, SYM[sym], ref, x, y
        self.textes = list(textes)        # (texte, dx, dy, taille, gras)
        self.ids = {}
        for n in self.s.bornes:
            folio.nid += 1
            self.ids[n] = folio.nid

    def p(self, borne):
        bx, by, _o = self.s.bornes[borne]
        return (self.x + bx, self.y + by)

    def o(self, borne):
        return self.s.bornes[borne][2]

    def xml(self):
        bornes = []
        for n, (bx, by, o) in self.s.bornes.items():
            dx, dy = {"n": (0, 4), "e": (-4, 0), "w": (4, 0), "s": (0, -4)}[o]
            bornes.append(f'<terminal x="{q(bx + dx)}" y="{q(by + dy)}" orientation="{ORI[o]}" '
                          f'id="{self.ids[n]}"/>')
        dyn = []
        for i, (t, dx, dy, taille, gras) in enumerate(self.textes):
            de_label = i == 0 and t == self.ref
            police = (POLICE_GRAS if gras else POLICE).format(taille)
            corps = (f"<text>{escape(t)}</text><info_name>label</info_name>" if de_label
                     else f"<text>{escape(t)}</text>")
            dyn.append(f'<dynamic_elmt_text x="{q(dx)}" y="{q(dy)}" rotation="0" frame="false" '
                       f'Halignment="AlignLeft" Valignment="AlignTop" font="{police}" '
                       f'uuid="{uid(self.f.num, self.ref, "texte", i)}" text_width="-1" '
                       f'keep_visual_rotation="true" text_from="{"ElementInfo" if de_label else "UserText"}">'
                       f'{corps}</dynamic_elmt_text>')
        return (f'<element x="{q(self.x)}" y="{q(self.y)}" z="10" orientation="0" '
                f'type="embed://import/tracker/{self.s.cle}.elmt" uuid="{uid(self.f.num, self.ref)}" '
                f'prefix="" freezeLabel="false"><terminals>{"".join(bornes)}</terminals><inputs/>'
                f'<elementInformations><elementInformation show="1" name="label">{escape(self.ref)}'
                f'</elementInformation></elementInformations><dynamic_texts>{"".join(dyn)}</dynamic_texts>'
                f'<texts_groups/></element>')


COULEURS = {"12V": "#c00000", "5V": "#d06000", "3V3": "#a07000", "0V": "#202060"}


class Folio:
    def __init__(self, num, titre, cols, rows):
        self.num, self.titre, self.cols, self.rows = num, titre, cols, rows
        self.nid = 1000 * num
        self.inst, self.fils, self.textes, self.cadres = [], [], [], []
        self.nauto = 0

    def el(self, sym, ref, x, y, *textes):
        i = Instance(self, sym, ref, x, y, textes)
        self.inst.append(i)
        return i

    def auto(self, sym, x, y):
        """Symbole sans repère affiché (masse, alimentations, jonctions)."""
        self.nauto += 1
        return self.el(sym, f"{sym}_{self.nauto}", x, y)

    def fil(self, a, ba, b, bb, via=(), num="", pot=None, aligne="AlignBottom"):
        """Fil de a.ba à b.bb, à l'équerre. via : points imposés (x, y), ou ('x', X) pour aller
        horizontalement jusqu'à X, ('y', Y) pour aller verticalement jusqu'à Y."""
        p1, p2 = a.p(ba), b.p(bb)
        pts = [p1]
        for v in via:
            if v[0] == "x":
                pts.append((v[1], pts[-1][1]))
            elif v[0] == "y":
                pts.append((pts[-1][0], v[1]))
            else:
                pts.append(v)
        x, y = pts[-1]
        if x != p2[0] and y != p2[1]:
            h1 = a.o(ba) in "ew" if len(pts) == 1 else pts[-2][1] == y
            h2 = b.o(bb) in "ew"
            if len(pts) == 1 and h1 and h2:              # en Z, coude vertical au milieu
                xm = round((x + p2[0]) / 20) * 10
                pts += [(xm, y), (xm, p2[1])]
            elif len(pts) == 1 and not h1 and not h2:    # en Z, coude horizontal au milieu
                ym = round((y + p2[1]) / 20) * 10
                pts += [(x, ym), (p2[0], ym)]
            elif h2:
                pts.append((x, p2[1]))
            else:
                pts.append((p2[0], y))
        pts.append(p2)
        segs = []
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if x1 != x2 and y1 != y2:
                raise ValueError(f"segment oblique {a.ref}.{ba} -> {b.ref}.{bb} : {pts}")
            if x1 != x2:
                segs.append(("horizontal", x2 - x1))
            elif y1 != y2:
                segs.append(("vertical", y2 - y1))
        self.fils.append((a.ids[ba], b.ids[bb], segs, num, pot, aligne))

    def texte(self, x, y, t, taille=8, gras=False, mono=False):
        self.textes.append((x, y, t, taille, gras, mono))

    def cadre(self, x1, y1, x2, y2, titre=None, dx=6):
        self.cadres.append((x1, y1, x2, y2))
        if titre:
            self.texte(x1 + dx, y1 + 4, titre, 7, True)

    def xml(self, date):
        els = "".join(i.xml() for i in self.inst)
        fils = []
        for t1, t2, segs, num, pot, aligne in self.fils:
            couleur = f' color="{COULEURS[pot]}"' if pot else ""
            seg = "".join(f'<segment orientation="{o}" length="{q(l)}"/>' for o, l in segs)
            fils.append(f'<conductor x="0" y="0" terminal1="{t1}" terminal2="{t2}" freezeLabel="false" '
                        f'type="multi"{couleur} bicolor="false" color2="#000000" dash-size="1" '
                        f'num={quoteattr(num)} text_color="#000000" formula="" cable="" bus="" function="" '
                        f'tension_protocol="" conductor_color="" conductor_section="" numsize="7" condsize="1" '
                        f'displaytext="{1 if num else 0}" onetextperfolio="0" vertirotatetext="270" '
                        f'horizrotatetext="0" horizontal-alignment="AlignHCenter" vertical-alignment="{aligne}">'
                        f'{seg}<sequentialNumbers/></conductor>')
        textes = []
        for x, y, t, taille, gras, mono in self.textes:
            famille = "Monospace" if mono else "Sans Serif"
            police = f"{famille},{taille},-1,5,{75 if gras else 50},0,0,0,0,0"
            # QElectroTech lit ces textes en HTML : retours à la ligne et espaces à préserver
            style = "white-space:pre; margin:0" + ("; font-family:monospace" if mono else "")
            html = f'<p style="{style}">' + "<br/>".join(escape(l) for l in t.split("\n")) + "</p>"
            textes.append(f'<input x="{q(x)}" y="{q(y)}" rotation="0" font="{police}" text={quoteattr(html)}/>')
        cadres = "".join(
            f'<shape type="Rectangle" x1="{q(x1)}" y1="{q(y1)}" x2="{q(x2)}" y2="{q(y2)}" rx="0" ry="0" '
            f'z="0" closed="0" is_movable="1"><pen color="#606060" widthF="1" style="DashLine"/>'
            f'<brush color="#000000" style="NoBrush"/></shape>' for x1, y1, x2, y2 in self.cadres)
        h = self.rows * 80 + 20
        return (f'<diagram title={quoteattr(self.titre)} order="{self.num}" folio="%id/%total" '
                f'version="0.90" author="Gabrixl-m" date="{date}" filename="Schema_Electrique.qet" '
                f'plant="Tracker solaire lunaire" locmach="Démonstration sur Terre" indexrev="A" '
                f'auto_page_num="" displayAt="bottom" cols="{self.cols}" colsize="60" rows="{self.rows}" '
                f'rowsize="80" height="{h}" displaycols="true" displayrows="true" '
                f'freezeNewElement="false" freezeNewConductor="false">'
                f'<defaultconductor type="multi" num="" numsize="7" condsize="1" displaytext="1"/>'
                f'<elements>{els}</elements><conductors>{"".join(fils)}</conductors>'
                f'<inputs>{"".join(textes)}</inputs><shapes>{cadres}</shapes></diagram>')


# ---------------------------------------------------------------------------
# FOLIO 1 : SCHÉMA COMPLET

def folio_schema():
    f = Folio(1, "Schéma électrique complet", 30, 13)
    M, P12, P5, P33 = "masse", "p12", "p5", "p33"

    # ---- alimentation 12 V et 5 V ----------------------------------------------------------
    f.cadre(40, 40, 560, 600, "ALIMENTATION")
    g1 = f.el("batterie", "G1", 100, 220, ("G1", 20, -20, 8, True),
              ("bloc secteur 12 V 3 A", 20, -6, 6, False),
              ("ou LiFePO4 4S 12,8 V", 20, 4, 6, False))
    f1 = f.el("fusible", "F1", 180, 120, ("F1", -10, -24, 8, True), ("3 A", 10, -24, 6, False))
    s1 = f.el("interrupteur", "S1", 280, 120, ("S1", -10, -30, 8, True), ("marche / arrêt", -26, 8, 6, False))
    j12 = f.auto("jonction", 360, 120)
    f.fil(g1, "+", f1, "1", via=[(100, 120)], pot="12V")
    f.fil(f1, "2", s1, "1", pot="12V")
    f.fil(s1, "2", j12, "w", pot="12V")
    f.fil(j12, "n", f.auto(P12, 360, 70), "1", pot="12V")
    f.fil(g1, "-", f.auto(M, 100, 290), "1", pot="0V")

    u1 = f.el("lm2596", "U1", 330, 330, ("U1", -50, -66, 8, True),
              ("sortie réglée à 5,3 V", -50, -54, 6, False))
    f.fil(j12, "s", u1, "IN+", via=[(360, 220), (240, 220), (240, 340)], pot="12V")
    f.fil(u1, "IN-", f.auto(M, 250, 420), "1", via=[("x", 250)], pot="0V")
    f.fil(u1, "OUT-", f.auto(M, 410, 420), "1", via=[("x", 410)], pot="0V")
    d1 = f.el("schottky", "D1", 450, 340, ("D1", -10, -26, 8, True), ("1N5819", -16, 10, 6, False))
    f.fil(u1, "OUT+", d1, "A", pot="5V")
    f.fil(d1, "K", f.auto(P5, 500, 300), "1", via=[("x", 500)], pot="5V")
    f.texte(60, 470, "D1 empêche le 5 V du port USB-C de remonter dans\n"
                     "l'abaisseur quand le Heltec est branché à l'ordinateur.\n"
                     "Régler U1 à 5,3 V au multimètre AVANT de brancher\n"
                     "le Heltec : il reçoit alors environ 5,0 V après D1.", 7)

    # ---- Heltec V4 ----------------------------------------------------------------------
    f.cadre(580, 40, 1040, 600, "COMMANDE ET RADIO LoRa")
    a1 = f.el("heltec", "A1", 820, 320, ("A1", -120, -176, 8, True))
    f.fil(f.auto(P5, 650, 230), "1", a1, "5V", pot="5V")
    f.fil(a1, "3V3", f.auto(P33, 620, 250), "1", pot="3V3")
    ant = f.el("antenne", "W1", 800, 100, ("W1", -110, -26, 8, True),
               ("antenne LoRa 868 MHz", -110, -14, 6, False), ("sur le connecteur IPEX", -110, -5, 6, False))
    f.fil(ant, "1", a1, "ANT")
    gn = f.el("gnss", "A3", 960, 70, ("A3", -84, -24, 8, True))
    f.fil(gn, "1", a1, "GNSS", via=[("y", 125), ("x", 880)])
    f.fil(a1, "GND", f.auto(M, 720, 530), "1", pot="0V")

    # ---- drivers et moteurs -----------------------------------------------------------------
    f.cadre(1060, 40, 1780, 600, "MOTEURS")
    f.cadre(1490, 60, 1770, 590, None)
    f.texte(1496, 64, "sur la tête rotative", 7, True)
    drv = {}
    for k, (ref, sym, yc, mref, mot, fils_m) in enumerate((
            ("U2", "tmc2209", 200, "M1", "NEMA 17 (17HS3401) : élévation",
             ("broche 1", "broche 4", "broche 3", "broche 6")),
            ("U3", "tmc2209_b", 480, "M2", "NEMA 11 (11HS18-0674S) : azimut",
             ("noir", "vert", "rouge", "bleu")))):
        u = f.el(sym, ref, 1260, yc, (ref, 66, 72, 8, True))
        drv[ref] = u
        top = yc - 110
        jv = f.auto("jonction", 1220, top)
        f.fil(f.auto(P33, 1220, top - 30), "1", jv, "n", pot="3V3")
        f.fil(jv, "s", u, "VIO", pot="3V3")
        jm = f.auto("jonction", 1240, top)
        f.fil(jv, "e", jm, "w", pot="3V3")
        f.fil(jm, "s", u, "MS1", pot="3V3")
        f.fil(jm, "e", u, "MS2", via=[("x", 1260)], pot="3V3")
        jvm = f.auto("jonction", 1300, top)
        f.fil(f.auto(P12, 1300, top - 30), "1", jvm, "n", pot="12V")
        f.fil(jvm, "s", u, "VM", pot="12V")
        c = f.el("condensateur_polarise", f"C{k + 1}", 1360, yc - 70,
                 (f"C{k + 1}", 12, -22, 8, True), ("100 µF 25 V", 12, -10, 6, False),
                 ("au plus près", 12, 0, 6, False))
        f.fil(jvm, "e", c, "+", via=[("x", 1360)], pot="12V")
        f.fil(c, "-", f.auto(M, 1360, yc - 30), "1", pot="0V")
        for b, x in (("PDN_UART", 1220), ("GND", 1250), ("GNDM", 1280)):
            f.fil(u, b, f.auto(M, x, yc + 110), "1", pot="0V")
        m = f.el("moteur_pas", mref, 1600, yc + 20, (mref, 40, -50, 8, True), (mot, -70, 42, 6, False))
        for b_drv, b_mot, t in zip(("1A", "1B", "2A", "2B"), ("A+", "A-", "B+", "B-"), fils_m):
            f.fil(u, b_drv, m, b_mot, num=t)

    # signaux de commande : Heltec -> drivers, sans croisement
    u2, u3 = drv["U2"], drv["U3"]
    f.fil(a1, "STEP_EL", u2, "STEP", via=[("x", 1080)], num="STEP_EL")
    f.fil(a1, "DIR_EL", u2, "DIR", via=[("x", 1100)], num="DIR_EL")
    f.fil(a1, "STEP_AZ", u3, "STEP", via=[("x", 1100)], num="STEP_AZ")
    f.fil(a1, "DIR_AZ", u3, "DIR", via=[("x", 1080)], num="DIR_AZ")
    jen = f.auto("jonction", 1120, 320)
    f.fil(a1, "EN", jen, "w", num="EN")
    f.fil(jen, "n", u2, "EN", via=[("y", 200)])
    f.fil(jen, "s", u3, "EN", via=[("y", 440)])
    r5 = f.el("resistance", "R5", 1160, 290, ("R5", 8, -16, 8, True), ("10 kΩ", 8, -4, 6, False))
    f.fil(jen, "e", r5, "2", via=[("x", 1160)])
    f.fil(f.auto(P33, 1160, 240), "1", r5, "1", pot="3V3")

    # ---- capteur solaire ---------------------------------------------------------------------
    f.cadre(40, 620, 740, 1030, "CAPTEUR SOLAIRE")
    f.cadre(60, 640, 480, 765, None)
    f.texte(250, 644, "sur le petit côté du cadre du panneau", 7, True)
    noms, xs = ("HG", "HD", "BG", "BD"), (120, 220, 320, 420)
    p33c = f.auto(P33, 80, 660)
    jk = [f.auto("jonction", x, 680) for x in xs[:-1]]
    f.fil(p33c, "1", jk[0], "w", via=[(80, 680)], pot="3V3")
    for a, b in zip(jk, jk[1:]):
        f.fil(a, "e", b, "w", pot="3V3")
    ads = f.el("ads1115", "A2", 610, 920, ("A2", -50, -86, 8, True))
    for i, (x, nom) in enumerate(zip(xs, noms)):
        d = f.el("photodiode", f"D{i + 2}", x, 720, (f"D{i + 2}", 8, -20, 8, True),
                 (f"BPW34 {nom}", 8, 10, 6, False))
        if i < 3:
            f.fil(jk[i], "s", d, "K", pot="3V3")
        else:
            f.fil(jk[2], "e", d, "K", via=[("x", x)], pot="3V3")
        jn = f.auto("jonction", x, 790)
        f.fil(d, "A", jn, "n")
        jr = f.auto("jonction", x + 30, 790)
        f.fil(jn, "e", jr, "w")
        r = f.el("resistance", f"R{i + 1}", x + 30, 830, (f"R{i + 1}", -26, -14, 7, True),
                 ("1 kΩ", -26, -4, 6, False))
        f.fil(jr, "s", r, "1")
        c = f.el("condensateur", f"C{i + 3}", x + 60, 830, (f"C{i + 3}", 8, -14, 7, True),
                 ("100 nF", 8, -4, 6, False))
        f.fil(jr, "e", c, "1", via=[("x", x + 60)])
        f.fil(r, "2", f.auto(M, x + 30, 870), "1", pot="0V")
        f.fil(c, "2", f.auto(M, x + 60, 870), "1", pot="0V")
        ent = f"A{i}"                     # HG (à gauche) passe le plus bas, sur A0
        f.fil(jn, "s", ads, ent, via=[("y", ads.p(ent)[1])], num=f"PD_{nom}")
    f.fil(ads, "VDD", f.auto(P33, 700, 840), "1", via=[("x", 700)], pot="3V3")
    jg = f.auto("jonction", 710, 950)
    f.fil(ads, "GND", jg, "n", via=[("x", 710)], pot="0V")
    f.fil(ads, "ADDR", jg, "w", pot="0V")
    f.fil(jg, "s", f.auto(M, 710, 1000), "1", pot="0V")
    f.fil(a1, "SDA", ads, "SDA", via=[("y", ads.p("SDA")[1])], num="SDA")
    f.fil(a1, "SCL", ads, "SCL", via=[("y", ads.p("SCL")[1])], num="SCL")

    # ---- origines : fin de course d'élévation et capteur à effet Hall d'azimut -----------------
    f.cadre(830, 620, 1300, 1030, "ORIGINES DES AXES", dx=90)
    f.cadre(845, 800, 1290, 1018, None)
    f.texte(1150, 804, "sur la tête rotative", 7, True)
    jf = f.auto("jonction", 860, 740)
    f.fil(a1, "FDC_EL", jf, "n")
    s2 = f.el("fin_course", "S2", 880, 900, ("S2", 44, -44, 8, True),
              ("micro-rupteur SPS75GCC", 44, -32, 6, False), ("butée basse d'élévation", 44, -23, 6, False),
              ("(-2°), branché sur NC :", 44, -14, 6, False), ("fil coupé = butée", 44, -5, 6, False))
    f.fil(jf, "s", s2, "NC")
    f.fil(s2, "C", f.auto(M, 880, 970), "1", pot="0V")
    r6 = f.el("resistance", "R6", 920, 710, ("R6", 8, -14, 8, True), ("10 kΩ", 8, -2, 6, False))
    f.fil(jf, "e", r6, "2", via=[("x", 920)])
    f.fil(f.auto(P33, 920, 660), "1", r6, "1", pot="3V3")

    jh = f.auto("jonction", 1140, 740)
    f.fil(a1, "HALL_AZ", jh, "n", via=[("y", 580), ("x", 1140)], num="HALL_AZ", aligne="AlignTop")
    b1 = f.el("hall", "B1", 1080, 920, ("B1", 36, 34, 8, True), ("A3144 nu, aimant sur", 36, 46, 6, False),
              ("la roue fixe. Pas de module", 36, 55, 6, False), ("KY-003 (tirage au 5 V)", 36, 64, 6, False))
    f.fil(jh, "s", b1, "OUT", via=[("y", 920)])
    f.fil(f.auto(P5, 1070, 840), "1", b1, "VCC", pot="5V")
    f.fil(b1, "GND", f.auto(M, 1090, 990), "1", pot="0V")
    r7 = f.el("resistance", "R7", 1200, 710, ("R7", 8, -14, 8, True), ("10 kΩ", 8, -2, 6, False))
    f.fil(jh, "e", r7, "2", via=[("x", 1200)])
    f.fil(f.auto(P33, 1200, 660), "1", r7, "1", pot="3V3")

    # ---- réglages -------------------------------------------------------------------------------
    f.cadre(1320, 620, 1780, 1030, "RÉGLAGES")
    f.texte(1330, 644,
            "Courant des moteurs : potentiomètre de chaque TMC2209\n"
            "(modules à R_sense = 0,11 Ω) : Vref = 1,41 × I\n"
            "  U2 / M1, NEMA 17 : 0,6 A en PETG -> Vref = 0,85 V\n"
            "     (cas réel : 1,0 A -> 1,41 V)\n"
            "  U3 / M2, NEMA 11 : 0,67 A -> Vref = 0,95 V\n"
            "Mesurer Vref entre GND et le potentiomètre.\n\n"
            "MS1 = MS2 = 3,3 V : 16 micro-pas.\n"
            "PDN_UART à la masse : courant réduit à l'arrêt.\n"
            "EN = 0 seulement pendant les mouvements ; à l'arrêt\n"
            "et au démarrage, EN = 1 (R5) : moteurs coupés, ils ne\n"
            "chauffent pas leurs supports en PETG.\n\n"
            "Capteur solaire : 1 kΩ par photodiode, dehors comme\n"
            "sous une lampe. L'ADS1115 change de calibre :\n"
            "±4,096 V au soleil, ±0,256 V en intérieur.\n\n"
            "LoRa : ne jamais émettre sans l'antenne W1.\n"
            "Tous les 0 V sont reliés entre eux.", 7)
    return f


# ---------------------------------------------------------------------------
# FOLIO 2 : BROCHAGE ET LIAISONS

def folio_brochage():
    f = Folio(2, "Brochage du Heltec V4 et liaisons", 30, 13)
    f.texte(60, 50, "Brochage du Heltec WiFi LoRa 32 V4 utilisé par le tracker", 11, True)
    f.texte(60, 90,
            "Broche   Connecteur  Sens     Signal    Vers                    Remarque\n"
            "------   ----------  -------  --------  ----------------------  ---------------------------------------------\n"
            "5V       J2-2        entrée   +5 V      D1 (abaisseur U1)       alimentation de la carte, environ 5,0 V\n"
            "GND      J2-1        -        0 V       masse commune\n"
            "3V3      J3-2, J3-3  sortie   +3,3 V    U2, U3, A2, D2 à D5     VIO des drivers, ADS1115, photodiodes, tirages\n"
            "GPIO47   J2-13       sortie   STEP_EL   U2 STEP                 impulsions de pas, élévation\n"
            "GPIO43   J2-6        sortie   DIR_EL    U2 DIR                  sens, élévation (TX0 : bouge au démarrage, sans effet : EN = 1)\n"
            "GPIO48   J2-14       sortie   STEP_AZ   U3 STEP                 impulsions de pas, azimut\n"
            "GPIO45   J3-6        sortie   DIR_AZ    U3 DIR                  sens, azimut (broche de démarrage : laissée basse par le driver)\n"
            "GPIO33   J2-12       sortie   EN        U2 EN, U3 EN            0 = moteurs alimentés ; tirage R5 au 3,3 V\n"
            "GPIO3    J3-14       I2C      SDA       ADS1115 SDA             Wire.begin(3, 4)\n"
            "GPIO4    J3-15       I2C      SCL       ADS1115 SCL\n"
            "GPIO44   J2-5        entrée   FDC_EL    S2 NC (commun à 0 V)    1 = butée atteinte OU fil coupé ; tirage R6\n"
            "GPIO6    J3-17       entrée   HALL_AZ   B1 OUT                  0 = aimant devant le capteur ; tirage R7\n"
            "IPEX     -           radio    ANT       W1                      antenne LoRa 868 MHz\n"
            "GNSS     SH1.25 8 br -        -         A3 (facultatif)         GPIO 34, 38 à 42 réservés au GNSS", 8, mono=True)
    f.texte(60, 330, "Broches de la carte à ne pas utiliser", 10, True)
    f.texte(60, 356,
            "GPIO0 bouton PRG (démarrage) - GPIO1 mesure de la batterie LiPo - GPIO2, 5, 7, 46 ampli radio (FEM)\n"
            "GPIO8 à 14 radio SX1262 - GPIO17, 18, 21 écran OLED - GPIO19, 20 USB - GPIO26 mémoire PSRAM\n"
            "GPIO34, 38 à 42 module GNSS - GPIO35 LED - GPIO36 Vext - GPIO37 commande de la mesure batterie\n"
            "Il ne reste donc que 9 broches libres sur les connecteurs : toutes sont utilisées ci-dessus. C'est pourquoi\n"
            "les TMC2209 sont réglés par leur potentiomètre (pas d'UART) et les photodiodes lues par un ADS1115 (I2C).", 8)
    f.texte(60, 470, "Liaisons entre le boîtier (au pied du trépied) et la tête", 10, True)
    f.texte(60, 496,
            "Câble                       Conducteurs  Signaux\n"
            "--------------------------  -----------  -----------------------------------------------\n"
            "Moteur d'élévation M1       4            A+ / A- (bobine A), B+ / B- (bobine B)\n"
            "Moteur d'azimut M2          4            noir A+, vert A-, rouge B+, bleu B-\n"
            "Fin de course S2            2            C (0 V), NC (FDC_EL)\n"
            "Capteur à effet Hall B1     3            +5 V, 0 V, OUT (HALL_AZ)\n"
            "Capteur solaire D2 à D5     5            +3,3 V (cathodes), PD_HG, PD_HD, PD_BG, PD_BD (anodes)\n"
            "Laisser une boucle de câble près de l'axe d'élévation ; tout passe par le passe-câble du socle.", 8, mono=True)
    f.texte(60, 650, "Données envoyées en LoRa (exemple)", 10, True)
    f.texte(60, 676,
            "angles d'azimut et d'élévation (consigne et position), 4 signaux du capteur solaire,\n"
            "erreur de pointage, état des origines, heure et position GNSS si le module A3 est branché.\n"
            "Ne pas dépasser le temps d'émission autorisé dans la bande 868 MHz (1 % en général) :\n"
            "un message toutes les 1 à 5 minutes suffit.", 8)
    return f


# ---------------------------------------------------------------------------

def projet(folios):
    date = "20261011"
    syms = "".join(f'<element name="{s.cle}.elmt">{s.xml()}</element>' for s in SYM.values())
    collection = ('<collection><category name="import"><names><name lang="fr">Éléments importés</name>'
                  '<name lang="en">Imported elements</name></names><category name="tracker"><names>'
                  '<name lang="fr">Tracker solaire</name><name lang="en">Solar tracker</name></names>'
                  f'{syms}</category></category></collection>')
    nouv = ('<newdiagrams><border cols="30" colsize="60" rows="13" rowsize="80" displaycols="true" '
            'displayrows="true"/><inset displayAt="bottom" title="Tracker solaire lunaire" author="Gabrixl-m" '
            f'date="{date}" folio="%id/%total" filename="Schema_Electrique.qet" plant="" locmach="" '
            'indexrev="" auto_page_num="" version=""/><conductors type="multi" num="" numsize="7" '
            'condsize="1" displaytext="1"/><report label="%f-%l%c"/><xrefs/>'
            '<conductors_autonums current_autonum="" freeze_new_conductors="false"/><folio_autonums/>'
            '<element_autonums current_autonum="" freeze_new_elements="false"/></newdiagrams>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<project title="Tracker solaire lunaire - schéma électrique" version="0.90">'
            f'<properties/>{nouv}{"".join(fo.xml(date) for fo in folios)}{collection}</project>\n')


def main():
    faire_symboles()
    folios = [folio_schema(), folio_brochage()]
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(projet(folios))
    n_el = sum(1 for fo in folios for i in fo.inst if "_" not in i.ref)
    print(f"{SORTIE} : {len(folios)} folios, {n_el} composants, {sum(len(fo.fils) for fo in folios)} fils")


if __name__ == "__main__":
    main()
