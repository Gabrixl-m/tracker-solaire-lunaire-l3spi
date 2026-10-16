"""Schéma électrique du tracker (démonstration sur Terre), au format QElectroTech.

Écrit Electronique/Schema_Electrique.qet : un projet QElectroTech 0.9 (s'ouvre aussi dans les
versions suivantes) avec trois folios :
  1. le schéma complet : alimentation 12 V / 5 V, Heltec WiFi LoRa 32 V4, 2 drivers TMC2209
     et leurs moteurs, capteur solaire (4 BPW34 + ADS1115), fin de course et capteur à effet Hall,
     et la mesure de l'énergie : panneau, régulateur de charge, batterie et deux wattmètres INA219
     (INA219B d'Adafruit sur le panneau, SEN0291 de DFRobot sur le 12 V du tracker) ;
  2. le brochage du Heltec V4, les câbles entre le boîtier et la tête, les données envoyées en LoRa ;
  3. le câblage : section (AWG) et type de fil de chaque liaison.

Chaque fil porte sa section (texte sur le fil, propriétés « Section du conducteur » et « Câble »),
et l'épaisseur de son trait suit cette section.

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

    for cle, nom, l1, l2, l3, shunt, haut in (
            ("ina219_adafruit", "Wattmètre INA219B (Adafruit 904)", "INA219B (Adafruit 904)",
             "shunt 0,1 Ω, ±3,2 A", "I2C 0x40 (A0, A1 ouverts)", "0,1 Ω", ("VCC", "SDA", "SCL")),
            ("ina219_sen0291", "Wattmètre INA219 (DFRobot SEN0291)", "SEN0291 (DFRobot)",
             "INA219, shunt 0,01 Ω, ±8 A", "I2C 0x45 (A0 = A1 = 1)", "0,01 Ω", ("SCL", "SDA", "VCC"))):
        s = symbole(cle, nom)
        s.rect(-70, -45, 140, 90, BLANC)
        s.ligne(-70, 0, -20, 0)                        # shunt sur le trajet du courant
        s.rect(-20, -5, 40, 10)
        s.ligne(20, 0, 70, 0)
        s.texte(-3.2 * len(shunt), -9, shunt, 6)
        s.texte(-66, -6, "VIN+", 6)
        s.texte(44, -6, "VIN-", 6)
        s.texte(-64, 18, l1, 7, True)
        s.texte(-64, 28, l2, 6)
        s.texte(-64, 38, l3, 6)
        s.borne("VIN+", -90, 0, "w", 20)
        s.borne("VIN-", 90, 0, "e", 20)
        for n, x in zip(haut, (-40, 0, 40)):
            s.texte(x - 2 * len(n) - 1, -34, n, 6)
            s.borne(n, x, -65, "n", 20)
        s.texte(48, 42, "GND", 6)
        s.borne("GND", 55, 65, "s", 20)

    s = symbole("panneau_pv", "Panneau photovoltaïque")
    s.rect(-25, -30, 50, 60, BLANC)
    s.ligne(-25, 30, 25, -30, FIN)
    for dx in (-14, -4):                               # rayons du Soleil
        s.ligne(dx - 16, -46, dx - 5, -35, FIN, "simple")
    s.texte(30, -19, "+", 8, True)
    s.texte(30, 12, "-", 8, True)
    s.borne("+", 45, -15, "e", 20)
    s.borne("-", 45, 15, "e", 20)

    s = symbole("regulateur", "Régulateur de charge solaire")
    s.rect(-70, -40, 140, 80, BLANC)
    s.texte(-40, -8, "Régulateur", 7, True)
    s.texte(-40, 2, "de charge solaire 12 V", 6)
    s.texte(-40, 11, "PWM ou MPPT,", 6)
    s.texte(-40, 20, "réglé LiFePO4", 6)
    for n, x, y, o in (("PV+", -90, -20, "w"), ("PV-", -90, 20, "w"), ("BAT+", 90, -20, "e"), ("BAT-", 90, 20, "e")):
        s.texte(-66 if o == "w" else 64 - 4 * len(n), y + 3, n, 6)
        s.borne(n, x, y, o, 20)

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

# section de chaque catégorie de fil : (AWG, mm², épaisseur du trait, fil à utiliser)
SECTIONS = {
    "bat": ("AWG 18", "0,82 mm²", 2.4, "fil souple, de la batterie (ou du bloc 12 V) au bornier X1"),
    "p12": ("AWG 20", "0,52 mm²", 1.8, "fil de câblage sur la plaque : 12 V et 0 V de puissance"),
    "p5": ("AWG 22", "0,33 mm²", 1.4, "fil de câblage sur la plaque : 5 V"),
    "mot": ("AWG 22", "0,33 mm²", 1.4, "câble souple 4 conducteurs, 1,5 m, paires torsadées A+/A-, B+/B-"),
    "log": ("AWG 24", "0,20 mm²", 1.0, "fil de câblage monobrin sur la plaque : signaux et 3,3 V"),
    "capt": ("AWG 26", "0,13 mm²", 1.0, "câble souple 2 ou 3 conducteurs, 1,5 m, vers la tête"),
    "sol": ("AWG 26", "0,13 mm²", 1.0, "câble souple blindé 6 conducteurs, 1,5 m, vers le capteur solaire"),
    "pv": ("AWG 20", "0,52 mm²", 1.8, "câble souple 2 conducteurs, du panneau au bornier X7 (par la boucle de câble)"),
    "reg": ("AWG 20", "0,52 mm²", 1.8, "câble souple 2 conducteurs, du bornier X7 au régulateur de charge"),
    "i2c": ("AWG 26", "0,13 mm²", 1.0, "câble 4 fils de J1 au module (STEMMA QT pour A4, Gravity pour A5)"),
    "ant": ("coaxial", "50 Ω", 1.0, "câble coaxial 50 Ω (1,13 mm ou RG178), IPEX vers SMA"),
    "gnss": ("fourni", "", 1.0, "câble fourni avec le module GNSS"),
}
DEFAUT_POT = {"12V": "p12", "5V": "p5", "3V3": "log", "0V": "log", None: "log"}


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

    def fil(self, a, ba, b, bb, via=(), num="", pot=None, aligne="AlignBottom", cat=None):
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
        self.fils.append((a.ids[ba], b.ids[bb], segs, num, pot, aligne, cat or DEFAUT_POT[pot]))

    def texte(self, x, y, t, taille=8, gras=False, mono=False):
        self.textes.append((x, y, t, taille, gras, mono))

    def cadre(self, x1, y1, x2, y2, titre=None, dx=6):
        self.cadres.append((x1, y1, x2, y2))
        if titre:
            self.texte(x1 + dx, y1 + 4, titre, 7, True)

    def xml(self, date):
        els = "".join(i.xml() for i in self.inst)
        fils = []
        for t1, t2, segs, num, pot, aligne, cat in self.fils:
            couleur = f' color="{COULEURS[pot]}"' if pot else ""
            seg = "".join(f'<segment orientation="{o}" length="{q(l)}"/>' for o, l in segs)
            awg, mm2, epaisseur, genre = SECTIONS[cat]
            # section écrite sur le fil s'il est assez long pour la porter ; toujours dans ses propriétés
            texte = f"{num} · {awg}" if num else awg
            visible = max(abs(l) for _o, l in segs) >= 40 if segs else False
            style = ' style="line-style: dashed"' if cat == "ant" else ""
            fils.append(f'<conductor x="0" y="0" terminal1="{t1}" terminal2="{t2}" freezeLabel="false" '
                        f'type="multi"{couleur}{style} bicolor="false" color2="#000000" dash-size="2" '
                        f'num={quoteattr(texte)} text_color="#000000" formula="" '
                        f'cable={quoteattr(genre)} bus="" function={quoteattr(num)} tension_protocol="" '
                        f'conductor_color="" conductor_section={quoteattr((awg + " " + mm2).strip())} '
                        f'numsize="6" condsize="{epaisseur}" displaytext="{1 if visible else 0}" '
                        f'onetextperfolio="0" vertirotatetext="270" horizrotatetext="0" '
                        f'horizontal-alignment="AlignHCenter" vertical-alignment="{aligne}">'
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
    f = Folio(1, "Schéma électrique complet", 30, 16)
    M, P12, P5, P33 = "masse", "p12", "p5", "p33"

    # ---- alimentation 5 V (le 12 V vient de la bande du bas : batterie, F1, S1, wattmètre A5) ----
    f.cadre(40, 40, 560, 600, "ALIMENTATION 5 V")
    f.texte(60, 70, "Le +12 V arrive de la batterie G1 par le fusible F1,\n"
                    "l'interrupteur S1 et le wattmètre A5 (bande du bas :\n"
                    "MESURE DE L'ÉNERGIE), puis par le bornier X1.", 7)
    u1 = f.el("lm2596", "U1", 330, 330, ("U1", -50, -66, 8, True),
              ("sortie réglée à 5,3 V", -50, -54, 6, False))
    f.fil(f.auto(P12, 230, 290), "1", u1, "IN+", pot="12V")
    f.fil(u1, "IN-", f.auto(M, 250, 420), "1", via=[("x", 250)], pot="0V", cat="p12")
    f.fil(u1, "OUT-", f.auto(M, 410, 420), "1", via=[("x", 410)], pot="0V", cat="p5")
    d1 = f.el("schottky", "D1", 450, 340, ("D1", -10, -26, 8, True), ("1N5819", -16, 10, 6, False))
    f.fil(u1, "OUT+", d1, "A", pot="5V")
    f.fil(d1, "K", f.auto(P5, 500, 300), "1", via=[("x", 500)], pot="5V")
    f.texte(60, 440, "D1 empêche le 5 V du port USB-C de remonter dans\n"
                     "l'abaisseur quand le Heltec est branché à l'ordinateur.\n"
                     "Régler U1 à 5,3 V au multimètre AVANT de brancher\n"
                     "le Heltec : il reçoit alors environ 5,0 V après D1.", 7)
    f.texte(60, 498, "SECTION DES FILS (écrite sur chaque fil ; détail au folio 3)", 7, True)
    f.texte(60, 512, "AWG 18 (0,82 mm²) : batterie ou bloc 12 V jusqu'au boîtier\n"
                     "AWG 20 (0,52 mm²) : 12 V et 0 V de puissance sur la plaque\n"
                     "AWG 22 (0,33 mm²) : moteurs (câble 4 conducteurs) et 5 V\n"
                     "AWG 24 (0,20 mm²) : signaux et 3,3 V sur la plaque\n"
                     "AWG 26 (0,13 mm²) : capteurs de la tête (blindé pour le solaire)\n"
                     "AWG 20 souple : câbles du panneau et du régulateur de charge\n"
                     "tirets : câble coaxial 50 Ω de l'antenne LoRa", 7)

    # ---- Heltec V4 ----------------------------------------------------------------------
    f.cadre(580, 40, 1040, 600, "COMMANDE ET RADIO LoRa")
    a1 = f.el("heltec", "A1", 820, 320, ("A1", -120, -176, 8, True))
    f.fil(f.auto(P5, 650, 230), "1", a1, "5V", pot="5V")
    f.fil(a1, "3V3", f.auto(P33, 620, 250), "1", pot="3V3")
    ant = f.el("antenne", "W1", 800, 70, ("W1", 12, -26, 8, True),
               ("antenne 868 MHz", 12, -14, 6, False), ("connecteur IPEX", 12, -5, 6, False))
    f.fil(ant, "1", a1, "ANT", cat="ant")
    gn = f.el("gnss", "A3", 960, 70, ("A3", -84, -24, 8, True))
    f.fil(gn, "1", a1, "GNSS", via=[("y", 125), ("x", 880)], cat="gnss")
    f.fil(a1, "GND", f.auto(M, 720, 530), "1", pot="0V", cat="p5")

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
        f.fil(c, "-", f.auto(M, 1360, yc - 30), "1", pot="0V", cat="p12")
        for b, x, cat in (("PDN_UART", 1220, "log"), ("GND", 1250, "log"), ("GNDM", 1280, "p12")):
            f.fil(u, b, f.auto(M, x, yc + 110), "1", pot="0V", cat=cat)
        m = f.el("moteur_pas", mref, 1600, yc + 20, (mref, 40, -50, 8, True), (mot, -70, 42, 6, False))
        for b_drv, b_mot, t in zip(("1A", "1B", "2A", "2B"), ("A+", "A-", "B+", "B-"), fils_m):
            f.fil(u, b_drv, m, b_mot, num=t, cat="mot")

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
    f.fil(p33c, "1", jk[0], "w", via=[(80, 680)], pot="3V3", cat="sol")
    for a, b in zip(jk, jk[1:]):
        f.fil(a, "e", b, "w", pot="3V3", cat="sol")
    ads = f.el("ads1115", "A2", 610, 920, ("A2", -50, -86, 8, True))
    for i, (x, nom) in enumerate(zip(xs, noms)):
        d = f.el("photodiode", f"D{i + 2}", x, 720, (f"D{i + 2}", 8, -20, 8, True),
                 (f"BPW34 {nom}", 8, 10, 6, False))
        if i < 3:
            f.fil(jk[i], "s", d, "K", pot="3V3", cat="sol")
        else:
            f.fil(jk[2], "e", d, "K", via=[("x", x)], pot="3V3", cat="sol")
        jn = f.auto("jonction", x, 790)
        f.fil(d, "A", jn, "n", cat="sol")
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
    jsda = f.auto("jonction", 760, ads.p("SDA")[1])
    jscl = f.auto("jonction", 800, ads.p("SCL")[1])
    f.fil(a1, "SDA", jsda, "n", num="SDA")
    f.fil(a1, "SCL", jscl, "n", num="SCL")
    f.fil(jsda, "w", ads, "SDA")
    f.fil(jscl, "w", ads, "SCL")

    # ---- origines : fin de course d'élévation et capteur à effet Hall d'azimut -----------------
    f.cadre(830, 620, 1300, 1030, "ORIGINES DES AXES", dx=90)
    f.cadre(845, 800, 1290, 1018, None)
    f.texte(1150, 804, "sur la tête rotative", 7, True)
    jf = f.auto("jonction", 860, 740)
    f.fil(a1, "FDC_EL", jf, "n")
    s2 = f.el("fin_course", "S2", 880, 900, ("S2", 44, -44, 8, True),
              ("micro-rupteur SPS75GCC", 44, -32, 6, False), ("butée basse d'élévation", 44, -23, 6, False),
              ("(-2°), branché sur NC :", 44, -14, 6, False), ("fil coupé = butée", 44, -5, 6, False))
    f.fil(jf, "s", s2, "NC", cat="capt")
    f.fil(s2, "C", f.auto(M, 880, 970), "1", pot="0V", cat="capt")
    r6 = f.el("resistance", "R6", 920, 710, ("R6", 8, -14, 8, True), ("10 kΩ", 8, -2, 6, False))
    f.fil(jf, "e", r6, "2", via=[("x", 920)])
    f.fil(f.auto(P33, 920, 660), "1", r6, "1", pot="3V3")

    jh = f.auto("jonction", 1140, 740)
    f.fil(a1, "HALL_AZ", jh, "n", via=[("y", 580), ("x", 1140)], num="HALL_AZ", aligne="AlignTop")
    b1 = f.el("hall", "B1", 1080, 920, ("B1", 36, 34, 8, True), ("A3144 nu, aimant sur", 36, 46, 6, False),
              ("la roue fixe. Pas de module", 36, 55, 6, False), ("KY-003 (tirage au 5 V)", 36, 64, 6, False))
    f.fil(jh, "s", b1, "OUT", via=[("y", 920)], cat="capt")
    f.fil(f.auto(P5, 1070, 840), "1", b1, "VCC", pot="5V", cat="capt")
    f.fil(b1, "GND", f.auto(M, 1090, 990), "1", pot="0V", cat="capt")
    r7 = f.el("resistance", "R7", 1200, 710, ("R7", 8, -14, 8, True), ("10 kΩ", 8, -2, 6, False))
    f.fil(jh, "e", r7, "2", via=[("x", 1200)])
    f.fil(f.auto(P33, 1200, 660), "1", r7, "1", pot="3V3")

    # ---- mesure de l'énergie : panneau, régulateur, batterie, deux wattmètres INA219 -------------
    f.cadre(40, 1050, 1780, 1290, "MESURE DE L'ÉNERGIE : PANNEAU, BATTERIE ET DEUX WATTMÈTRES INA219 (I2C)")
    f.cadre(55, 1095, 205, 1282, None)
    f.texte(61, 1099, "sur la tête rotative", 7, True)
    yl = 1170                                          # ligne du + : panneau -> A4 -> A6 ; G1 -> F1 -> S1 -> A5
    pv = f.el("panneau_pv", "PV1", 110, yl + 15, ("PV1", -25, 34, 8, True),
              ("panneau ≈ 10 W crête", -25, 46, 6, False), ("tension à vide < 26 V", -25, 55, 6, False))
    a4 = f.el("ina219_adafruit", "A4", 330, yl, ("A4", -100, -42, 8, True),
              ("production du panneau", -64, 52, 6, False))
    a6 = f.el("regulateur", "A6", 560, yl + 20, ("A6", -70, -58, 8, True),
              ("à côté de la batterie", -60, 46, 6, False))
    f2 = f.el("fusible", "F2", 695, yl, ("F2", -10, -24, 8, True), ("3 A", 10, -24, 6, False),
              ("en ligne, près", -26, 8, 6, False), ("de la batterie", -26, 16, 6, False))
    jb = f.auto("jonction", 740, yl)
    g1 = f.el("batterie", "G1", 740, yl + 45, ("G1", 14, 0, 8, True),
              ("LiFePO4 4S 12,8 V", 14, 12, 6, False), ("ou bloc secteur 12 V 3 A", 14, 21, 6, False))
    f1 = f.el("fusible", "F1", 830, yl, ("F1", -10, -24, 8, True), ("3 A", 10, -24, 6, False),
              ("en ligne, à moins de", -26, 8, 6, False), ("10 cm de la batterie", -26, 16, 6, False))
    s1 = f.el("interrupteur", "S1", 920, yl, ("S1", -10, -30, 8, True), ("marche / arrêt,", -26, 8, 6, False),
              ("sur le boîtier", -26, 16, 6, False))
    a5 = f.el("ina219_sen0291", "A5", 1060, yl, ("A5", 95, -42, 8, True),
              ("consommation du tracker", -64, 52, 6, False))
    f.fil(pv, "+", a4, "VIN+", num="PV+", pot="12V", cat="pv")
    f.fil(pv, "-", a6, "PV-", via=[("x", 200), ("y", 1275), ("x", 450)], num="PV-", cat="pv")
    f.fil(a4, "VIN-", a6, "PV+", pot="12V", cat="reg")
    f.fil(a6, "BAT+", f2, "1", pot="12V", cat="bat")
    f.fil(a6, "BAT-", f.auto(M, 670, yl + 65), "1", via=[("x", 670)], pot="0V", cat="bat")
    f.fil(f2, "2", jb, "w", pot="12V", cat="bat")
    f.fil(jb, "s", g1, "+", pot="12V", cat="bat")
    f.fil(g1, "-", f.auto(M, 740, yl + 95), "1", pot="0V", cat="bat")
    f.fil(jb, "e", f1, "1", pot="12V", cat="bat")
    f.fil(f1, "2", s1, "1", pot="12V", cat="bat")
    f.fil(s1, "2", a5, "VIN+", pot="12V", cat="bat")
    f.fil(a5, "VIN-", f.auto(P12, 1190, 1130), "1", via=[("x", 1190)], num="vers X1", pot="12V", cat="bat")
    for a, x in ((a4, a4.p("VCC")[0]), (a5, a5.p("VCC")[0])):
        f.fil(f.auto(P33, x, 1085), "1", a, "VCC", pot="3V3", cat="i2c")
        f.fil(a, "GND", f.auto(M, a.p("GND")[0], yl + 85), "1", pot="0V", cat="i2c")
    jsb = f.auto("jonction", 760, 1070)
    jscb = f.auto("jonction", 800, 1085)
    f.fil(jsda, "s", jsb, "n")
    f.fil(jscl, "s", jscb, "n")
    f.fil(jsb, "w", a4, "SDA", via=[("x", a4.p("SDA")[0])], cat="i2c")
    f.fil(jsb, "e", a5, "SDA", via=[("x", a5.p("SDA")[0])], cat="i2c")
    f.fil(jscb, "w", a4, "SCL", via=[("x", a4.p("SCL")[0])], cat="i2c")
    f.fil(jscb, "e", a5, "SCL", via=[("x", a5.p("SCL")[0])], cat="i2c")
    f.texte(1250, 1064,
            "A4 mesure ce que produit le panneau, A5 ce que consomme le tracker.\n"
            "Trois modules sur le même bus I2C (GPIO 3 et 4), adresses différentes :\n"
            "  A2 ADS1115 = 0x48 ; A4 INA219B = 0x40 (A0, A1 ouverts) ;\n"
            "  A5 SEN0291 = 0x45 (micro-interrupteurs A0 = 1 et A1 = 1).\n"
            "A4 et A5 sont alimentés en 3,3 V : leurs tirages I2C restent à 3,3 V.\n"
            "Le - du panneau va au PV- de A6 sans toucher le 0 V du boîtier : le\n"
            "montage convient à tout régulateur. A4 lit la tension du panneau si\n"
            "A6 est à masse négative commune, celle de la batterie sinon.\n"
            "Tension à vide du panneau (Voc, sur son étiquette) < 26 V, limite de A4.\n"
            "En intérieur sur le bloc secteur : pas de régulateur, A4 lit 0.\n"
            "Le panneau, le régulateur et la batterie se branchent sur X7 et X1 ;\n"
            "A4 et A5 sont dans le boîtier, à côté de la plaque (câbles I2C sur J1).", 7)

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

def tableau(lignes, largeurs):
    """Tableau en texte à chasse fixe : colonnes alignées, ligne de tirets sous l'en-tête."""
    def ligne(cols):
        return "  ".join(c.ljust(l) for c, l in zip(cols, largeurs)).rstrip()
    sortie = [ligne(lignes[0]), ligne(["-" * l for l in largeurs])]
    return "\n".join(sortie + [ligne(c) for c in lignes[1:]])


def folio_brochage():
    f = Folio(2, "Brochage du Heltec V4 et liaisons", 30, 16)
    f.texte(60, 50, "Brochage du Heltec WiFi LoRa 32 V4 utilisé par le tracker", 11, True)
    f.texte(60, 84, tableau([
        ("Broche", "Connecteur", "Sens", "Signal", "Vers", "Remarque"),
        ("5V", "J2-2", "entrée", "+5 V", "D1 (abaisseur U1)", "alimentation de la carte, environ 5,0 V"),
        ("GND", "J2-1", "-", "0 V", "masse commune", ""),
        ("3V3", "J3-2, J3-3", "sortie", "+3,3 V", "U2 U3 A2 A4 A5 D2 à D5",
         "VIO des drivers, ADS1115, wattmètres, photodiodes, tirages"),
        ("GPIO47", "J2-13", "sortie", "STEP_EL", "U2 STEP", "impulsions de pas, élévation"),
        ("GPIO43", "J2-6", "sortie", "DIR_EL", "U2 DIR",
         "sens, élévation (TX0 : bouge au démarrage, sans effet : EN = 1)"),
        ("GPIO48", "J2-14", "sortie", "STEP_AZ", "U3 STEP", "impulsions de pas, azimut"),
        ("GPIO45", "J3-6", "sortie", "DIR_AZ", "U3 DIR",
         "sens, azimut (broche de démarrage : laissée basse par le driver)"),
        ("GPIO33", "J2-12", "sortie", "EN", "U2 EN, U3 EN", "0 = moteurs alimentés ; tirage R5 au 3,3 V"),
        ("GPIO3", "J3-14", "I2C", "SDA", "A2, A4, A5 : SDA", "Wire.begin(3, 4) ; bus I2C partagé par trois modules"),
        ("GPIO4", "J3-15", "I2C", "SCL", "A2, A4, A5 : SCL", ""),
        ("GPIO44", "J2-5", "entrée", "FDC_EL", "S2 NC (commun à 0 V)", "1 = butée atteinte OU fil coupé ; tirage R6"),
        ("GPIO6", "J3-17", "entrée", "HALL_AZ", "B1 OUT", "0 = aimant devant le capteur ; tirage R7"),
        ("IPEX", "-", "radio", "ANT", "W1", "antenne LoRa 868 MHz"),
        ("GNSS", "SH1.25 8 br", "-", "-", "A3 (facultatif)", "GPIO 34, 38 à 42 réservés au GNSS")],
        (6, 11, 6, 8, 22, 62)), 8, mono=True)
    f.texte(60, 300, "Broches de la carte à ne pas utiliser", 10, True)
    f.texte(60, 324,
            "GPIO0 bouton PRG (démarrage) - GPIO1 mesure de la batterie LiPo - GPIO2, 5, 7, 46 ampli radio (FEM)\n"
            "GPIO8 à 14 radio SX1262 - GPIO17, 18, 21 écran OLED - GPIO19, 20 USB - GPIO26 mémoire PSRAM\n"
            "GPIO34, 38 à 42 module GNSS - GPIO35 LED - GPIO36 Vext - GPIO37 commande de la mesure batterie\n"
            "Il ne reste donc que 9 broches libres sur les connecteurs : toutes sont utilisées ci-dessus. C'est pourquoi\n"
            "les TMC2209 sont réglés par leur potentiomètre (pas d'UART), et les photodiodes et les wattmètres sont lus\n"
            "par l'I2C : trois modules sur les deux mêmes broches, chacun à son adresse.", 8)
    f.texte(60, 420, "Bus I2C (GPIO 3 et 4, 100 kHz) : trois modules", 10, True)
    f.texte(60, 444, tableau([
        ("Repère", "Module", "Adresse", "Réglage de l'adresse", "Mesure"),
        ("A2", "ADS1115", "0x48", "ADDR à 0 V", "les 4 photodiodes du capteur solaire"),
        ("A4", "INA219B (Adafruit 904)", "0x40", "A0 et A1 ouverts (d'origine)",
         "panneau : tension et courant (shunt 0,1 Ω, ±3,2 A)"),
        ("A5", "SEN0291 (DFRobot, INA219)", "0x45", "micro-interrupteurs A0 = 1 et A1 = 1",
         "12 V du tracker : tension et courant (shunt 0,01 Ω, ±8 A)")],
        (6, 25, 7, 36, 56)), 8, mono=True)
    f.texte(60, 520, "Câbles du boîtier (au pied du trépied)", 10, True)
    f.texte(60, 544, tableau([
        ("Câble", "Bornier", "Conducteurs", "Signaux"),
        ("Moteur d'élévation M1", "X2", "4 × AWG 22", "A+ / A- (bobine A), B+ / B- (bobine B)"),
        ("Moteur d'azimut M2", "X3", "4 × AWG 22", "noir A+, vert A-, rouge B+, bleu B-"),
        ("Fin de course S2", "X4", "2 × AWG 26", "C (0 V), NC (FDC_EL)"),
        ("Capteur à effet Hall B1", "X5", "3 × AWG 26", "+5 V, 0 V, OUT (HALL_AZ)"),
        ("Capteur solaire", "X6", "5 × AWG 26 blindé", "+3,3 V (cathodes), PD_HG, PD_HD, PD_BG, PD_BD"),
        ("Panneau PV1", "X7-1, X7-2", "2 × AWG 20 souple", "PV+ (vers A4 VIN+), PV- (relié à X7-4 seulement)"),
        ("Régulateur de charge A6", "X7-3, X7-4", "2 × AWG 20 souple", "PV+ (depuis A4 VIN-), PV-"),
        ("Batterie G1, par F1 et S1", "A5, X1", "2 × AWG 18 souple", "+ : S1 -> A5 VIN+, A5 VIN- -> X1+ ; - : X1-"),
        ("Régulateur -> batterie", "-", "2 × AWG 18 souple", "BAT+ -> F2 -> G1+, BAT- -> G1- (hors du boîtier)"),
        ("Wattmètres A4 et A5", "J1", "4 fils chacun", "+3,3 V, 0 V, SDA, SCL (câbles STEMMA QT et Gravity)")],
        (25, 10, 17, 52)), 8, mono=True)
    f.texte(60, 712, "Les câbles de la tête (moteurs, capteurs, panneau) passent par le passe-câble du socle ; laisser une\n"
                     "boucle de câble près de l'axe d'élévation.", 8)
    f.texte(60, 762, "Données envoyées en LoRa : trame de 38 octets", 10, True)
    f.texte(60, 786, tableau([
        ("Octets", "Champ", "Type", "Unité"),
        ("0", "version de la trame (= 1)", "uint8", ""),
        ("1-2", "numéro du message", "uint16", "de 0 à 65535, puis repart à 0"),
        ("3-4", "azimut : consigne", "int16", "0,01°"),
        ("5-6", "azimut : position", "int16", "0,01°"),
        ("7-8", "élévation : consigne", "int16", "0,01°"),
        ("9-10", "élévation : position", "int16", "0,01°"),
        ("11-12", "erreur de pointage", "uint16", "0,001°"),
        ("13-20", "photodiodes HG, HD, BG, BD", "4 × int16", "valeur brute de l'ADS1115"),
        ("21", "état", "uint8", "bits : 0 butée basse, 1 aimant Hall, 2 moteurs alimentés, 3 GNSS valide,"),
        ("", "", "", "4 calibre intérieur de l'ADS1115, 5 A4 absent, 6 A5 absent"),
        ("22-23", "panneau : tension (A4)", "uint16", "mV"),
        ("24-25", "panneau : courant (A4)", "int16", "0,1 mA"),
        ("26-27", "12 V du tracker : tension (A5)", "uint16", "mV"),
        ("28-29", "12 V du tracker : courant (A5)", "int16", "mA"),
        ("30-33", "énergie produite par le panneau", "uint32", "mWh, cumulée depuis la mise sous tension"),
        ("34-37", "énergie consommée par le tracker", "uint32", "mWh, cumulée depuis la mise sous tension")],
        (6, 32, 9, 75)), 8, mono=True)
    f.texte(60, 1046,
            "Octets de poids faible en premier (little-endian, l'ordre de l'ESP32). Les wattmètres sont lus toutes les 0,2 s,\n"
            "l'énergie est cumulée entre deux messages. Ne pas dépasser le temps d'émission autorisé dans la bande 868 MHz\n"
            "(1 % en général) : 38 octets durent environ 0,3 s en SF9, donc un message par minute ; en SF12 (2 s), un toutes\n"
            "les 5 minutes.", 8)
    return f


# ---------------------------------------------------------------------------
# FOLIO 3 : CÂBLAGE ET SECTIONS DES FILS

def folio_cablage():
    f = Folio(3, "Câblage et sections des fils", 30, 16)
    f.texte(60, 46, "Section de chaque fil", 11, True)
    f.texte(60, 84, tableau([
        ("Liaison", "De -> vers", "Courant", "Longueur", "Section", "Fil à utiliser"),
        ("Batterie ou bloc 12 V, +", "G1+ -> F1 -> S1 -> A5 -> X1", "1,5 A", "1 m", "AWG 18  0,82 mm²",
         "souple, rouge ; F1 à moins de 10 cm de G1"),
        ("Batterie ou bloc 12 V, 0 V", "G1- -> X1", "1,5 A", "1 m", "AWG 18  0,82 mm²", "souple, noir"),
        ("12 V sur la plaque", "X1 -> VM de U2 et U3, C1, C2, U1", "1,5 A", "< 15 cm", "AWG 20  0,52 mm²", "rouge"),
        ("0 V de puissance", "X1 -> U2, U3 (GND), C1, C2, U1", "1,5 A", "< 15 cm", "AWG 20  0,52 mm²", "noir"),
        ("5 V", "U1 OUT+ -> D1 -> A1 5V", "0,5 A", "< 10 cm", "AWG 22  0,33 mm²", "orange ; 0 V de U1 et de A1 : noir"),
        ("Moteur M1 (élévation)", "U2 1A 1B 2A 2B -> X2 -> M1", "1,0 A", "1,5 m", "AWG 22  0,33 mm²",
         "câble souple 4 conducteurs"),
        ("Moteur M2 (azimut)", "U3 1A 1B 2A 2B -> X3 -> M2", "0,67 A", "1,5 m", "AWG 22  0,33 mm²",
         "câble souple 4 conducteurs"),
        ("STEP, DIR, EN", "A1 -> U2, U3 ; R5", "< 1 mA", "< 10 cm", "AWG 24  0,20 mm²", "monobrin, une couleur par signal"),
        ("3,3 V, VIO, MS1, MS2, PDN", "A1 3V3 -> U2, U3, A2, J1, R5 à R7", "< 20 mA", "< 10 cm", "AWG 24  0,20 mm²",
         "monobrin, jaune ; 0 V : noir"),
        ("I2C (SDA, SCL)", "A1 GPIO3, GPIO4 -> A2, J1", "< 1 mA", "< 10 cm", "AWG 24  0,20 mm²", "monobrin"),
        ("I2C des wattmètres", "J1 -> A4, A5 (3,3 V, 0 V, SDA, SCL)", "< 2 mA", "< 20 cm", "AWG 26  0,13 mm²",
         "câble STEMMA QT (A4) et Gravity (A5)"),
        ("Filtres du capteur solaire", "R1 à R4, C3 à C6 -> A2 A0 à A3", "2 mA", "< 5 cm", "AWG 24  0,20 mm²", "monobrin"),
        ("Fin de course S2", "X4 -> S2 C et NC", "0,3 mA", "1,5 m", "AWG 26  0,13 mm²", "câble souple 2 conducteurs"),
        ("Capteur à effet Hall B1", "X5 -> B1 VCC, GND, OUT", "10 mA", "1,5 m", "AWG 26  0,13 mm²",
         "câble souple 3 conducteurs"),
        ("Capteur solaire", "X6 -> D2 à D5 (+3,3 V et 4 anodes)", "8 mA", "1,5 m", "AWG 26  0,13 mm²",
         "câble souple blindé, 6 conducteurs"),
        ("Pattes des photodiodes", "dans le boîtier du capteur", "2 mA", "5 cm", "AWG 28  0,08 mm²",
         "fil fin isolé (fil à wrapper)"),
        ("Panneau PV1", "PV1 -> X7-1, X7-2", "0,6 A", "2 m", "AWG 20  0,52 mm²",
         "câble souple 2 conducteurs, par la boucle de câble"),
        ("Wattmètre A4 (panneau)", "X7-1 -> A4 VIN+, A4 VIN- -> X7-3", "0,6 A", "< 20 cm", "AWG 20  0,52 mm²",
         "rouge ; X7-2 relié à X7-4 seulement"),
        ("Vers le régulateur A6", "X7-3, X7-4 -> A6 PV+, PV-", "0,6 A", "1 m", "AWG 20  0,52 mm²",
         "câble souple 2 conducteurs"),
        ("Wattmètre A5 (12 V)", "S1 -> A5 VIN+, A5 VIN- -> X1+", "1,5 A", "< 20 cm", "AWG 18  0,82 mm²", "souple, rouge"),
        ("Régulateur -> batterie", "A6 BAT+ -> F2 -> G1+, BAT- -> G1-", "0,6 A", "0,5 m", "AWG 18  0,82 mm²",
         "souple ; F2 à moins de 10 cm de G1"),
        ("Antenne LoRa", "A1 IPEX -> W1", "radio", "10 cm", "coaxial 50 Ω", "IPEX vers SMA, 1,13 mm ou RG178"),
        ("Module GNSS", "A1 -> A3", "-", "fourni", "-", "câble fourni avec le module")],
        (26, 35, 7, 8, 16, 48)), 9, mono=True)
    f.texte(60, 444, "Pourquoi ces sections", 11, True)
    f.texte(60, 470,
            "* Le courant fixe le minimum, la chute de tension le confirme. Résistance du cuivre : AWG 18 = 0,021 Ω/m,\n"
            "  AWG 20 = 0,033 Ω/m, AWG 22 = 0,053 Ω/m, AWG 24 = 0,084 Ω/m, AWG 26 = 0,134 Ω/m.\n"
            "* 12 V : 1,5 A au plus (les deux moteurs, environ 12 W, et le Heltec qui émet). En AWG 18 sur 2 × 1 m, la chute\n"
            "  n'est que de 0,06 V. Le fil entre la batterie et F1 n'est pas protégé par le fusible : il reste court (< 10 cm).\n"
            "  De même pour F2, sur le fil du régulateur.\n"
            "* Panneau : 0,6 A au plus (courant de court-circuit d'un panneau de 10 W). En AWG 20 sur 2 × 2 m, la chute est\n"
            "  de 0,08 V. Le câble suit ceux des moteurs dans la boucle : souple, multibrin.\n"
            "* Moteurs : 1,0 A au plus par bobine. En AWG 22 sur 2 × 1,5 m, la boucle fait 0,16 Ω contre plusieurs ohms\n"
            "  pour la bobine : le driver régule le courant, le moteur ne perd rien. Torsader A+ avec A-, et B+ avec B- :\n"
            "  moins de parasites rayonnés vers les capteurs.\n"
            "* Capteurs : quelques milliampères ; en AWG 26 sur 1,5 m, la chute est inférieure à 4 mV. Le câble du capteur\n"
            "  solaire est blindé (blindage relié au 0 V côté boîtier seulement) et passe à l'écart des câbles moteurs.\n"
            "* Tout ce qui bouge avec la tête (moteurs, capteurs, panneau) est en fil multibrin souple, jamais en monobrin :\n"
            "  il casse à force de plier. Sur la plaque, le monobrin AWG 24 se soude plus facilement.\n"
            "* Dans les borniers à vis, sertir un embout de câblage : 0,75 mm² pour l'AWG 18, 0,5 mm² pour l'AWG 20 et 22,\n"
            "  0,25 mm² pour l'AWG 24 et 26 (deux fils fins dans un embout de 0,5 mm² si besoin).", 9)
    f.texte(60, 720, "Correspondance AWG et mm²", 11, True)
    f.texte(60, 746,
            "AWG   Section    Diamètre du cuivre   Courant conseillé (fil isolé, en faisceau court)\n"
            "----  ---------  -------------------  -----------------------------------------------\n"
            "18    0,82 mm²   1,02 mm              5 A\n"
            "20    0,52 mm²   0,81 mm              3 A\n"
            "22    0,33 mm²   0,64 mm              2 A\n"
            "24    0,20 mm²   0,51 mm              1 A\n"
            "26    0,13 mm²   0,40 mm              0,5 A\n"
            "28    0,08 mm²   0,32 mm              0,3 A", 9, mono=True)
    f.texte(60, 892, "Dans QElectroTech, la section est aussi dans les propriétés de chaque fil (double-clic sur le fil :\n"
                     "« Section du conducteur »), avec le type de fil dans « Câble ». Sur le folio 1, l'épaisseur du trait\n"
                     "suit la section, et les fils trop courts pour porter le texte gardent la section de leur liaison.", 9)
    return f


# ---------------------------------------------------------------------------

def projet(folios):
    date = "20261011"
    syms = "".join(f'<element name="{s.cle}.elmt">{s.xml()}</element>' for s in SYM.values())
    collection = ('<collection><category name="import"><names><name lang="fr">Éléments importés</name>'
                  '<name lang="en">Imported elements</name></names><category name="tracker"><names>'
                  '<name lang="fr">Tracker solaire</name><name lang="en">Solar tracker</name></names>'
                  f'{syms}</category></category></collection>')
    nouv = ('<newdiagrams><border cols="30" colsize="60" rows="16" rowsize="80" displaycols="true" '
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
    folios = [folio_schema(), folio_brochage(), folio_cablage()]
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(projet(folios))
    n_el = sum(1 for fo in folios for i in fo.inst if "_" not in i.ref)
    print(f"{SORTIE} : {len(folios)} folios, {n_el} composants, {sum(len(fo.fils) for fo in folios)} fils")


if __name__ == "__main__":
    main()
