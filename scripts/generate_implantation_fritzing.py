"""Implantation du boîtier électronique de la démonstration, au format Fritzing (vue platine).

Écrit Electronique/Implantation_Boitier.fzz : une plaque à pastilles de 7 × 9 cm (24 × 30 trous)
avec, à l'échelle, tout ce qui reste au pied du trépied (Heltec WiFi LoRa 32 V4, 2 TMC2209,
ADS1115, mini abaisseur 5 V, borniers, résistances, diode et condensateurs), et à côté d'elle,
dans le même boîtier étanche, les deux wattmètres INA219 (INA219B d'Adafruit pour le panneau, SEN0291 de
DFRobot pour le 12 V du tracker), le régulateur de charge Velleman SOL10UC3, la batterie au plomb
et les deux fusibles en ligne F1 et F2. Ce qui est sur la tête (moteurs, fin de course, capteur
Hall, photodiodes, panneau) n'y est pas : on n'en voit que les borniers.

Pièces standard de Fritzing : résistances, interrupteur et plaque à pastilles. Le Heltec V4, le
TMC2209, l'ADS1115, le mini abaisseur, la diode, les deux wattmètres, la barrette J1 et les
borniers n'existent pas dans Fritzing (ou pas à l'échelle) : ils sont dessinés ici, à leurs
dimensions réelles, et intégrés au fichier.

La plaque est tassée au plus près : borniers des câbles de la tête au bord du haut, chacun
au-dessus de ce qu'il dessert (moteurs sur leurs drivers, capteurs sur l'ADS1115), Heltec en
bas avec son USB-C au bord, alimentation et bus I2C des wattmètres au bord droit. Aucune pièce
n'est cachée sous un module : tout reste visible et accessible.

Ouvrir le fichier dans Fritzing (gratuit, https://fritzing.org) : vue « Platine d'essai ».
Le câblage est celui du schéma électrique (Electronique/Schema_Electrique.qet).
"""
import os
import zipfile
from xml.sax.saxutils import escape, quoteattr

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "Electronique", "Implantation_Boitier.fzz")

PX = 90 / 25.4              # unités de la scène Fritzing : 90 px par pouce
PAS = 2.54                  # pas de la plaque à pastilles
TROUS = (30, 24)            # plaque de 30 × 24 trous, format « 7 × 9 cm » (90 × 70 mm)
REEL = (90.0, 70.0)         # dimensions réelles de la plaque, trous centrés


def f(v):
    return f"{v:.4g}" if abs(v) < 1000 else f"{v:.1f}"


# ---------------------------------------------------------------------------
# PIÈCES DESSINÉES ICI (dimensions réelles, en mm)

class Piece:
    """Pièce Fritzing : fichier .fzp et ses 4 dessins SVG (platine, schéma, circuit, icône)."""

    def __init__(self, cle, titre, l, h, broches, dessin, description, broche=1.1):
        self.cle, self.titre, self.l, self.h, self.broche = cle, titre, l, h, broche
        self.broches = broches              # [(nom, x, y)] en mm, coin haut gauche = (0, 0)
        self.dessin = dessin                # éléments SVG de la vue platine (sans les broches)
        self.description = description

    @property
    def module_id(self):
        return f"Tracker_{self.cle}"

    def fichiers(self):
        base = f"tracker_{self.cle.lower()}"
        imgs = {v: f"{v}/{base}_{v}.svg" for v in ("breadboard", "schematic", "pcb", "icon")}
        fzp = self.fzp(imgs)
        return base + ".fzp", fzp, {imgs[v]: getattr(self, f"svg_{v}")() for v in imgs}

    def _svg(self, l, h, corps, unite="mm"):
        return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{f(l)}{unite}" height="{f(h)}{unite}" viewBox="0 0 {f(l)} {f(h)}">{corps}</svg>\n')

    def svg_breadboard(self):
        b = self.broche
        pins = "".join(f'<rect id="connector{i}pin" x="{f(x - b / 2)}" y="{f(y - b / 2)}" width="{f(b)}" '
                       f'height="{f(b)}" fill="#c9b04a" stroke="#6b5a1a" stroke-width="0.15"/>'
                       for i, (_n, x, y) in enumerate(self.broches))
        return self._svg(self.l, self.h, f'<g id="breadboard">{self.dessin}{pins}</g>')

    def svg_icon(self):
        return self._svg(self.l, self.h, f'<g id="icon">{self.dessin}</g>')

    def svg_schematic(self):
        n = len(self.broches)
        l, h = 1.2, 0.1 * (n + 1)
        corps = [f'<rect x="0.3" y="0.02" width="0.6" height="{f(h - 0.04)}" fill="none" stroke="#000" '
                 f'stroke-width="0.01"/>',
                 f'<text x="0.6" y="{f(h / 2)}" font-size="0.07" text-anchor="middle" '
                 f'font-family="DroidSans">{escape(self.titre)}</text>']
        for i, (nom, _x, _y) in enumerate(self.broches):
            y = 0.1 * (i + 1)
            corps.append(f'<line id="connector{i}pin" x1="0" y1="{f(y)}" x2="0.3" y2="{f(y)}" stroke="#000" '
                         f'stroke-width="0.01"/><rect id="connector{i}terminal" x="0" y="{f(y - 0.005)}" '
                         f'width="0.01" height="0.01" fill="none"/>'
                         f'<text x="0.32" y="{f(y + 0.02)}" font-size="0.05" font-family="DroidSans">'
                         f'{escape(nom)}</text>')
        return self._svg(l, h, f'<g id="schematic">{"".join(corps)}</g>', "in")

    def svg_pcb(self):
        pads = "".join(f'<circle id="connector{i}pin" cx="{f(x)}" cy="{f(y)}" r="0.75" fill="none" '
                       f'stroke="#f7bd13" stroke-width="0.5"/>' for i, (_n, x, y) in enumerate(self.broches))
        cadre = (f'<g id="silkscreen"><rect x="0.1" y="0.1" width="{f(self.l - 0.2)}" '
                 f'height="{f(self.h - 0.2)}" fill="none" stroke="#fff" stroke-width="0.2"/></g>')
        return self._svg(self.l, self.h, f'{cadre}<g id="copper1"><g id="copper0">{pads}</g></g>')

    def fzp(self, imgs):
        conns = []
        for i, (nom, _x, _y) in enumerate(self.broches):
            conns.append(
                f'<connector id="connector{i}" type="male" name={quoteattr(nom)}><description>{escape(nom)}'
                f'</description><views><breadboardView><p layer="breadboard" svgId="connector{i}pin"/>'
                f'</breadboardView><schematicView><p layer="schematic" svgId="connector{i}pin" '
                f'terminalId="connector{i}terminal"/></schematicView><pcbView>'
                f'<p layer="copper0" svgId="connector{i}pin"/><p layer="copper1" svgId="connector{i}pin"/>'
                f'</pcbView></views></connector>')
        return (f'<?xml version="1.0" encoding="UTF-8"?>\n<module fritzingVersion="1.0.1" '
                f'moduleId="{self.module_id}"><version>1</version><author>Tracker solaire lunaire</author>'
                f'<title>{escape(self.titre)}</title><label>{escape(self.cle[:3])}</label>'
                f'<tags><tag>tracker</tag></tags><properties><property name="family">{escape(self.titre)}'
                f'</property></properties><description>{escape(self.description)}</description><views>'
                f'<iconView><layers image="{imgs["icon"]}"><layer layerId="icon"/></layers></iconView>'
                f'<breadboardView><layers image="{imgs["breadboard"]}"><layer layerId="breadboard"/></layers>'
                f'</breadboardView><schematicView><layers image="{imgs["schematic"]}"><layer '
                f'layerId="schematic"/></layers></schematicView><pcbView><layers image="{imgs["pcb"]}">'
                f'<layer layerId="copper0"/><layer layerId="silkscreen"/><layer layerId="copper1"/></layers>'
                f'</pcbView></views><connectors>{"".join(conns)}</connectors></module>\n')


def txt(x, y, t, taille=1.0, coul="#fff", ancre="start", gras=False, rot=0):
    r = f' transform="rotate({rot} {f(x)} {f(y)})"' if rot else ""
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="DroidSans, Arial, sans-serif" font-size="{f(taille)}" '
            f'fill="{coul}" text-anchor="{ancre}"{" font-weight=" + chr(34) + "bold" + chr(34) if gras else ""}'
            f'{r}>{escape(t)}</text>')


def heltec_v4():
    """Heltec WiFi LoRa 32 V4 : 51,7 × 25,4 mm, USB-C à gauche, 2 × 18 broches (J3 en haut, J2 en bas)."""
    l, h = 51.7, 25.4
    x0 = (l - 17 * PAS) / 2
    j3 = ("GND", "3V3", "3V3", "37", "46", "45", "42", "41", "40", "39", "38", "1", "2", "3", "4", "5", "6", "7")
    j2 = ("GND", "5V", "Ve", "Ve", "44", "43", "RST", "0", "36", "35", "34", "33", "47", "48", "26", "21",
          "20", "19")
    utilises = {("J3", "3V3"), ("J3", "45"), ("J3", "3"), ("J3", "4"), ("J3", "6"), ("J2", "GND"),
                ("J2", "5V"), ("J2", "44"), ("J2", "43"), ("J2", "33"), ("J2", "47"), ("J2", "48")}
    d = [f'<rect x="0" y="0" width="{l}" height="{h}" rx="1.2" fill="#202124" stroke="#000" stroke-width="0.2"/>',
         '<rect x="-1.4" y="8.9" width="7.6" height="7.6" rx="1" fill="#c7cacc" stroke="#6d7175" '
         'stroke-width="0.25"/><rect x="-1.4" y="10.9" width="2" height="3.6" rx="0.8" fill="#55595d"/>',
         txt(1.6, 18.6, "USB-C", 0.9, "#e8eaed"),
         '<rect x="8.6" y="4.9" width="2.9" height="2.9" rx="0.3" fill="#d0d0d0"/>'
         '<circle cx="10.05" cy="6.35" r="0.85" fill="#3c4043"/>',
         '<rect x="8.6" y="17.6" width="2.9" height="2.9" rx="0.3" fill="#d0d0d0"/>'
         '<circle cx="10.05" cy="19.05" r="0.85" fill="#3c4043"/>',
         txt(8.0, 6.7, "PRG", 0.8, "#e8eaed", "end"), txt(8.0, 19.4, "RST", 0.8, "#e8eaed", "end"),
         '<rect x="13.5" y="4.6" width="28.5" height="16.2" rx="0.6" fill="#0d1b2a" stroke="#9aa0a6" '
         'stroke-width="0.25"/><rect x="16.5" y="6.8" width="22" height="11.4" fill="#16324f"/>',
         txt(27.5, 11.6, "OLED 0,96\"", 1.3, "#7fb3ff", "middle"),
         txt(27.5, 14.6, "Heltec WiFi LoRa 32 V4", 1.15, "#e8eaed", "middle", True),
         '<rect x="44" y="9" width="5.5" height="7.4" rx="0.4" fill="#3a3d41"/>',
         '<circle cx="47.6" cy="5.4" r="1.2" fill="#d4af37" stroke="#7a6420" stroke-width="0.2"/>',
         txt(44.3, 3.3, "IPEX", 0.8, "#e8eaed"), txt(46.7, 13.2, "LoRa", 0.85, "#e8eaed", "middle"),
         txt(46.7, 14.5, "SX1262", 0.75, "#e8eaed", "middle")]
    broches = []
    for rangee, noms, yp, yt in (("J3", j3, 1.27, 3.35), ("J2", j2, h - 1.27, h - 2.45)):
        for i, n in enumerate(noms):
            x = x0 + i * PAS
            if (rangee, n) in utilises and not (rangee == "J3" and n == "3V3" and i == 2):
                d.append(f'<rect x="{f(x - 1.15)}" y="{f(yt - 1.0)}" width="2.3" height="1.3" rx="0.3" '
                         f'fill="#f29900"/>')
            d.append(txt(x, yt, n, 0.85, "#fff", "middle"))
            broches.append((f"{rangee}-{i + 1} {n}", x, yp))
    d.append(txt(x0 - 2.4, 1.9, "J3", 0.9, "#9aa0a6"))
    d.append(txt(x0 - 2.4, h - 0.9, "J2", 0.9, "#9aa0a6"))
    return Piece("Heltec_V4", "Heltec WiFi LoRa 32 V4", l, h, broches, "".join(d),
                 "Heltec WiFi LoRa 32 V4 (ESP32-S3 + SX1262), 51,7 x 25,4 mm. Broches utilisées par le "
                 "tracker en orange.")


def tmc2209():
    """Module TMC2209 au format StepStick : 15,24 × 20,32 mm, 2 × 8 broches espacées de 12,7 mm."""
    l, h = 15.24, 20.32
    gauche = ("EN", "MS1", "MS2", "UART", "PDN", "CLK", "STEP", "DIR")
    droite = ("VM", "GND", "2B", "2A", "1A", "1B", "VIO", "GND")
    d = [f'<rect x="0" y="0" width="{l}" height="{h}" rx="0.5" fill="#1b5e3b" stroke="#0d2f1d" stroke-width="0.2"/>',
         '<rect x="3.4" y="4.6" width="8.4" height="8.4" rx="0.4" fill="#9aa0a6" stroke="#5f6368" '
         'stroke-width="0.2"/>']
    d += [f'<line x1="{f(4.2 + 0.95 * k)}" y1="4.9" x2="{f(4.2 + 0.95 * k)}" y2="12.7" stroke="#6b7075" '
          f'stroke-width="0.35"/>' for k in range(8)]
    d += ['<circle cx="7.62" cy="16.3" r="1.5" fill="#e8e8e8" stroke="#7a7a7a" stroke-width="0.2"/>'
          '<line x1="6.6" y1="16.3" x2="8.6" y2="16.3" stroke="#555" stroke-width="0.35"/>',
          txt(7.62, 3.3, "TMC2209", 1.25, "#fff", "middle", True),
          txt(7.62, 19.4, "Vref", 0.8, "#cfe8d8", "middle")]
    broches = []
    for col, noms, xp, xt, ancre in ((0, gauche, 1.27, 2.3, "start"), (1, droite, l - 1.27, l - 2.3, "end")):
        for i, n in enumerate(noms):
            y = 1.27 + i * PAS
            d.append(txt(xt, y + 0.3, n, 0.7, "#fff", ancre))
            broches.append((n, xp, y))
    return Piece("TMC2209", "Driver TMC2209 (StepStick)", l, h, broches, "".join(d),
                 "Module TMC2209 au format StepStick, 15,24 x 20,32 mm, avec son dissipateur.")


def ads1115():
    """Module ADS1115 : 28 × 17,5 mm, 10 broches le long d'un grand côté."""
    l, h = 28.0, 17.5
    noms = ("VDD", "GND", "SCL", "SDA", "ADDR", "ALRT", "A0", "A1", "A2", "A3")
    x0 = (l - 9 * PAS) / 2
    d = [f'<rect x="0" y="0" width="{l}" height="{h}" rx="1" fill="#4a2a7a" stroke="#24123f" stroke-width="0.2"/>',
         '<circle cx="2.2" cy="2.2" r="1.3" fill="#fff" stroke="#c9b04a" stroke-width="0.4"/>',
         f'<circle cx="{f(l - 2.2)}" cy="2.2" r="1.3" fill="#fff" stroke="#c9b04a" stroke-width="0.4"/>',
         '<rect x="11.5" y="5.2" width="5" height="3.2" rx="0.2" fill="#111"/>',
         txt(14, 3.4, "ADS1115", 1.4, "#fff", "middle", True),
         txt(14, 10.6, "16 bits, I2C 0x48", 0.9, "#e3d7f5", "middle")]
    broches = []
    for i, n in enumerate(noms):
        x = x0 + i * PAS
        d.append(txt(x, h - 3.0, n, 0.75, "#fff", "middle"))
        broches.append((n, x, h - 1.27))
    return Piece("ADS1115", "Convertisseur ADS1115", l, h, broches, "".join(d),
                 "Module ADS1115 (convertisseur 16 bits, 4 entrées, I2C), 28 x 17,5 mm.")


def ina219_adafruit():
    """Wattmètre INA219B d'Adafruit (904, version STEMMA QT) : 25,6 × 20,4 mm, bornier 2 points
    (VIN+, VIN-), 6 broches au pas de 2,54 mm le long du bas, deux prises STEMMA QT."""
    l, h = 25.6, 20.4
    noms = ("VCC", "GND", "SCL", "SDA", "VIN-", "VIN+")
    x0 = (l - 5 * PAS) / 2
    d = [f'<rect x="0" y="0" width="{l}" height="{h}" rx="1.5" fill="#1d1d1f" stroke="#000" stroke-width="0.2"/>']
    d += [f'<circle cx="{f(cx)}" cy="{f(cy)}" r="1.3" fill="#fff" stroke="#c9b04a" stroke-width="0.5"/>'
          for cx in (2.5, l - 2.5) for cy in (2.5, h - 2.5)]
    d += ['<rect x="5.2" y="1.2" width="8" height="7" rx="0.4" fill="#2e9d55" stroke="#1b5e33" stroke-width="0.2"/>',
          '<circle cx="7.2" cy="4.4" r="1.2" fill="#c0c4c8"/><circle cx="11.2" cy="4.4" r="1.2" fill="#c0c4c8"/>',
          txt(9.2, 9.6, "VIN+  VIN-", 0.8, "#fff", "middle"),
          '<rect x="14.6" y="2.0" width="5.2" height="2.6" fill="#e8e8e8"/>', txt(17.2, 3.8, "R100", 0.9, "#222", "middle"),
          '<rect x="14.6" y="6.0" width="5.4" height="3.4" rx="0.2" fill="#2b2b2b" stroke="#888" stroke-width="0.15"/>',
          '<rect x="0.6" y="11.0" width="3.0" height="4.4" fill="#f0eadc" stroke="#999" stroke-width="0.15"/>',
          '<rect x="{0}" y="11.0" width="3.0" height="4.4" fill="#f0eadc" stroke="#999" stroke-width="0.15"/>'.format(f(l - 3.6)),
          txt(l / 2, 12.6, "INA219B  0x40", 1.25, "#fff", "middle", True),
          txt(l / 2, 14.4, "panneau", 0.95, "#cfcfcf", "middle")]
    broches = []
    for i, n in enumerate(noms):
        x = x0 + i * PAS
        d.append(txt(x, h - 2.7, n, 0.7, "#fff", "middle"))
        broches.append((n, x, h - 1.27))
    return Piece("INA219_Adafruit", "Wattmètre INA219B Adafruit 904", l, h, broches, "".join(d),
                 "Wattmètre INA219B d'Adafruit (904), shunt 0,1 ohm, ±3,2 A, I2C 0x40, 25,6 x 20,4 mm.")


def sen0291():
    """Wattmètre SEN0291 de DFRobot (INA219, shunt 0,01 Ω) : 30 × 22 mm, bornier 3 points sur le
    côté gauche (IN+, IN-, GND), prise Gravity I2C, 4 pastilles VCC, GND, SCL, SDA."""
    l, h = 30.0, 22.0
    noms = ("VCC", "GND", "SCL", "SDA")
    d = [f'<rect x="0" y="0" width="{l}" height="{h}" rx="1.5" fill="#1d1d1f" stroke="#000" stroke-width="0.2"/>',
         '<rect x="0.6" y="2.4" width="7.4" height="15.4" rx="0.4" fill="#2e9d55" stroke="#1b5e33" stroke-width="0.2"/>']
    d += [f'<circle cx="4.3" cy="{f(5.1 + 5.0 * k)}" r="1.5" fill="#c0c4c8"/>' for k in range(3)]
    d += [txt(4.3, 19.6, "IN+ IN- GND", 0.75, "#fff", "middle"),
          '<circle cx="15.5" cy="3.4" r="1.6" fill="#fff" stroke="#c9b04a" stroke-width="0.7"/>',
          '<circle cx="15.5" cy="19.2" r="1.6" fill="#fff" stroke="#c9b04a" stroke-width="0.7"/>',
          '<rect x="22.0" y="1.0" width="7.4" height="6.0" fill="#f0eadc" stroke="#999" stroke-width="0.15"/>',
          txt(25.7, 8.4, "Gravity I2C", 0.75, "#fff", "middle"),
          '<rect x="9.6" y="7.0" width="6.0" height="2.6" fill="#e8e8e8"/>', txt(12.6, 8.8, "R010", 0.9, "#222", "middle"),
          '<rect x="17.2" y="9.6" width="4.4" height="2.4" fill="#c62828"/>', txt(19.4, 13.3, "A0 A1", 0.7, "#fff", "middle"),
          txt(14.5, 14.2, "SEN0291  0x45", 1.2, "#fff", "middle", True),
          txt(14.5, 15.8, "12 V du tracker", 0.9, "#cfcfcf", "middle")]
    broches = []
    for i, n in enumerate(noms):
        x = 21.4 + i * PAS - 1.27 * 3 + 2.54
        d.append(txt(x, h - 2.6, n, 0.65, "#fff", "middle"))
        broches.append((n, x, h - 1.1))
    return Piece("SEN0291", "Wattmètre SEN0291 DFRobot", l, h, broches, "".join(d),
                 "Wattmètre SEN0291 de DFRobot (INA219, shunt 0,01 ohm, ±8 A, I2C 0x45), 30 x 22 mm.")


def barrette_2x4():
    """Barrette mâle 2 × 4 broches (J1) : une colonne par wattmètre, 3V3, GND, SDA, SCL."""
    l, h = 2 * PAS, 4 * PAS
    d = [f'<rect x="0" y="0" width="{f(l)}" height="{f(h)}" fill="#202124" stroke="#000" stroke-width="0.15"/>']
    broches = []
    for j, mod in enumerate(("A5", "A4")):
        for i, n in enumerate(("3V3", "GND", "SDA", "SCL")):
            x, y = 1.27 + j * PAS, 1.27 + i * PAS
            d.append(f'<rect x="{f(x - 0.32)}" y="{f(y - 0.32)}" width="0.64" height="0.64" fill="#d4af37"/>')
            broches.append((f"{mod} {n}", x, y))
    return Piece("Barrette_2x4", "Barrette mâle 2 x 4 (bus I2C des wattmètres)", l, h, broches, "".join(d),
                 "Barrette mâle 2 x 4 au pas de 2,54 mm : 3,3 V, 0 V, SDA, SCL pour A5 et pour A4.", broche=0.6)


def batterie_plomb():
    """Batterie au plomb étanche 12 V 5 Ah vue de dessus, posée debout dans le dessin : 70 × 88 mm,
    100 mm de haut (environ 106 mm avec ses bornes), bornes le long du bas : − à gauche, + à droite."""
    l, h = 70.0, 88.0
    d = [f'<rect x="0" y="0" width="{l}" height="{h}" rx="2" fill="#3a3d41" stroke="#1c1d1f" stroke-width="0.4"/>',
         '<rect x="0" y="9" width="70" height="7" fill="#8d9196"/>',
         '<rect x="5" y="75" width="8" height="8" rx="0.6" fill="#202124" stroke="#9aa0a6" stroke-width="0.3"/>',
         '<rect x="57" y="75" width="8" height="8" rx="0.6" fill="#d32f2f"/>',
         txt(18.5, 82, "−", 4.0, "#e8eaed", "middle", True), txt(51.5, 82, "+", 4.0, "#d32f2f", "middle", True),
         txt(37, 30, "G1 batterie plomb", 3.0, "#fff", "middle", True),
         txt(37, 35, "12 V 5 Ah", 3.0, "#fff", "middle", True),
         txt(37, 42, "88 × 70 × 100 mm", 2.2, "#e8eaed", "middle"),
         txt(37, 46.5, "≈ 1,9 kg", 2.2, "#e8eaed", "middle"),
         txt(37, 51, "pas de LiFePO4 avec A6", 2.2, "#e8eaed", "middle"),
         txt(37, 55.5, "sanglée (bande grise)", 2.2, "#e8eaed", "middle")]
    return Piece("Batterie_Plomb_5Ah", "Batterie plomb 12 V 5 Ah", l, h, [], "".join(d),
                 "Batterie au plomb étanche 12 V 5 Ah, 88 x 70 x 100 mm, vue de dessus.")


def regulateur_sol10uc3():
    """Régulateur PWM Velleman SOL10UC3, vissé sous la porte du boîtier : 110 × 80 mm, ses 6 bornes
    le long du bord tourné vers la charnière."""
    l, h = 110.0, 80.0
    d = [f'<rect x="0" y="0" width="{l}" height="{h}" rx="5" fill="#1e88e5" stroke="#0d47a1" stroke-width="0.5"/>']
    for i in range(6):
        x = 14 + 16.4 * i
        d.append(f'<circle cx="{f(x)}" cy="8" r="3.2" fill="#0d47a1" stroke="#90caf9" stroke-width="0.4"/>'
                 f'<line x1="{f(x - 2.2)}" y1="8" x2="{f(x + 2.2)}" y2="8" stroke="#90caf9" stroke-width="0.6"/>')
    d += ['<rect x="92" y="54" width="14" height="9" rx="0.8" fill="#cfd8dc" stroke="#455a64" stroke-width="0.4"/>',
          txt(99, 68, "USB", 2.2, "#fff", "middle")]
    d += [f'<circle cx="{f(14 + 7 * k)}" cy="70" r="1.6" fill="{c}"/>'
          for k, c in enumerate(("#66bb6a", "#ffca28", "#ef5350", "#66bb6a"))]
    d += [txt(55, 28, "A6 Velleman SOL10UC3", 3.4, "#fff", "middle", True),
          txt(55, 35, "régulateur PWM 10 A, sous la porte", 2.6, "#e3f2fd", "middle"),
          txt(55, 44, "bornes : panneau, batterie, LOAD", 2.4, "#e3f2fd", "middle"),
          txt(55, 50, "(ordre : voir le marquage)", 2.4, "#e3f2fd", "middle")]
    return Piece("Regulateur_SOL10UC3", "Régulateur PWM Velleman SOL10UC3", l, h, [], "".join(d),
                 "Régulateur de charge PWM Velleman SOL10UC3, 110 x 80 x 25 mm, vu de face.")


def porte(l, h, ecart, batterie):
    """Porte du boîtier, ouverte et rabattue sous lui autour de sa charnière (bord du haut), vue de
    l'intérieur : le dessin est le reflet du boîtier par rapport à la charnière. batterie : (x0, y0,
    x1, y1) de la batterie dans le boîtier, pour montrer où rien ne doit dépasser de la porte."""
    x0, y0, x1, y1 = batterie
    d = [f'<rect x="0.3" y="{f(ecart + 0.3)}" width="{f(l - 0.6)}" height="{f(h - 0.6)}" rx="3" fill="#fafafa" '
         f'stroke="#5f6368" stroke-width="0.7"/>',
         f'<rect x="{f(x0)}" y="{f(ecart + h - y1)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" rx="2" fill="none" '
         f'stroke="#9e9e9e" stroke-width="0.4" stroke-dasharray="2,1.2"/>',
         txt((x0 + x1) / 2, ecart + h - (y0 + y1) / 2 - 4, "porte fermée,", 2.2, "#757575", "middle"),
         txt((x0 + x1) / 2, ecart + h - (y0 + y1) / 2, "la batterie est ici :", 2.2, "#757575", "middle"),
         txt((x0 + x1) / 2, ecart + h - (y0 + y1) / 2 + 4, "rien sur cette zone", 2.2, "#757575", "middle", True),
         txt(l / 2, ecart + h - 4, "Porte ouverte, rabattue sous le boîtier, vue de l'intérieur", 2.4, "#3c4043",
             "middle", True)]
    for xc in (24, l - 24):                       # charnières
        d.append(f'<rect x="{f(xc - 6)}" y="-0.5" width="12" height="{f(ecart + 2)}" rx="1" fill="#9e9e9e" '
                 f'stroke="#616161" stroke-width="0.3"/>')
    d.append(txt(32, ecart / 2 + 0.8, "charnière", 1.8, "#3c4043"))
    # boucle des 6 fils du régulateur : de ses bornes, par la charnière, vers le boîtier
    d.append(f'<path d="M58,{f(ecart + 4)} C58,{f(ecart - 8)} 102,{f(ecart + 2)} 106,-1" fill="none" '
             f'stroke="#ef6c00" stroke-width="1.6" stroke-dasharray="3,1.5" stroke-linecap="round"/>')
    d.append(txt(110, ecart / 2 + 0.8, "6 fils souples en boucle (≈ 20 cm)", 1.8, "#ef6c00"))
    return Piece(f"Porte_{l}x{h}", f"Porte du boîtier {l} x {h} mm", l, ecart + h, [], "".join(d),
                 "Porte du boîtier étanche, ouverte, vue de l'intérieur, avec le régulateur vissé dessus.")


def porte_fusible(nom, vertical):
    """Porte-fusible en ligne 5 × 20 mm (fusible 3 A), serti sur le fil : 46 × 9 mm."""
    l, h = (9.0, 46.0) if vertical else (46.0, 9.0)
    d = [f'<rect x="0" y="0" width="{l}" height="{h}" rx="4" fill="#212121" stroke="#000" stroke-width="0.3"/>']
    if vertical:
        d.append(f'<rect x="1.5" y="17" width="6" height="12" rx="1" fill="#f5f5f5"/>')
        d.append(txt(4.5, 23, nom, 2.6, "#d32f2f", "middle", True, rot=-90))
    else:
        d.append(f'<rect x="17" y="1.5" width="12" height="6" rx="1" fill="#f5f5f5"/>')
        d.append(txt(23, 5.6, nom, 2.6, "#d32f2f", "middle", True))
    return Piece(f"Porte_fusible_{nom}", f"Porte-fusible en ligne {nom} (3 A)", l, h, [], "".join(d),
                 f"Porte-fusible en ligne 5 x 20 mm {nom}, fusible 3 A, serti sur le fil.")


def bornier(n, droite=False):
    """Bornier à vis au pas de 5,08 mm (type KF301), n pôles, vu de dessus, entrées des fils en
    haut (ou à droite)."""
    l, h = n * 5.08, 7.6
    d = [f'<rect x="0" y="0" width="{f(l)}" height="{h}" rx="0.4" fill="#2e7d32" stroke="#1b4d1e" stroke-width="0.25"/>']
    broches = []
    for i in range(n):
        cx = 2.54 + i * 5.08
        d.append(f'<rect x="{f(cx - 1.6)}" y="0" width="3.2" height="1.6" fill="#173e19"/>'
                 f'<circle cx="{f(cx)}" cy="3.9" r="1.7" fill="#c0c4c8" stroke="#6d7175" stroke-width="0.2"/>'
                 f'<line x1="{f(cx - 1.1)}" y1="3.9" x2="{f(cx + 1.1)}" y2="3.9" stroke="#55595d" '
                 f'stroke-width="0.45"/>')
        broches.append((str(i + 1), cx, 6.35))
    cle, desc = f"Bornier_{n}p", f"Bornier à vis {n} pôles au pas de 5,08 mm (KF301), {f(l)} x 7,6 mm."
    if droite:                      # quart de tour : entrées à droite, pôle 1 en haut
        d = [f'<g transform="matrix(0 1 -1 0 {f(h)} 0)">{"".join(d)}</g>']
        broches = [(nom, h - y, x) for nom, x, y in broches]
        l, h, cle = h, l, cle + "_d"
    return Piece(cle, f"Bornier à vis {n} pôles, pas 5,08 mm", l, h, broches, "".join(d), desc)


def bornier_254(n):
    """Bornier à vis au pas de 2,54 mm (type DG308, fils AWG 26 à 18, 6 A), n pôles, vu de
    dessus, entrées des fils en haut."""
    l, h = n * 2.54, 6.2
    d = [f'<rect x="0" y="0" width="{f(l)}" height="{h}" rx="0.3" fill="#1565c0" stroke="#0b3c75" stroke-width="0.2"/>']
    broches = []
    for i in range(n):
        cx = 1.27 + i * 2.54
        d.append(f'<rect x="{f(cx - 0.8)}" y="0" width="1.6" height="1.0" fill="#0b3c75"/>'
                 f'<circle cx="{f(cx)}" cy="2.4" r="0.95" fill="#c0c4c8" stroke="#6d7175" stroke-width="0.15"/>'
                 f'<line x1="{f(cx - 0.6)}" y1="2.4" x2="{f(cx + 0.6)}" y2="2.4" stroke="#55595d" '
                 f'stroke-width="0.3"/>')
        broches.append((str(i + 1), cx, 4.6))
    return Piece(f"Bornier_254_{n}p", f"Bornier à vis {n} pôles, pas 2,54 mm", l, h, broches, "".join(d),
                 f"Bornier à vis {n} pôles au pas de 2,54 mm (DG308), {f(l)} x 6,2 mm.", broche=0.7)


def abaisseur_5v():
    """Mini abaisseur à découpage, sortie fixe 5,0 V (entrée 5 à 30 V) : 18 × 13 mm, 4 pastilles
    aux coins (OUT à gauche, IN à droite), soudé à plat par 4 pattes."""
    l, h = 18.0, 13.0
    pastilles = (("OUT+", 1.38, 1.42), ("OUT-", 1.38, 11.58), ("IN+", 16.62, 1.42), ("IN-", 16.62, 11.58))
    d = [f'<rect x="0" y="0" width="{l}" height="{h}" rx="0.6" fill="#1f3f8f" stroke="#0d1f4a" stroke-width="0.2"/>',
         '<rect x="5.6" y="3.0" width="6.8" height="6.8" rx="0.6" fill="#2b2b2b" stroke="#555" stroke-width="0.15"/>',
         txt(9.0, 7.0, "4R7", 1.4, "#ddd", "middle"),
         '<rect x="13.4" y="4.6" width="2.0" height="3.2" fill="#111"/>',
         '<rect x="2.6" y="5.2" width="2.2" height="2.6" fill="#c8a165"/>',
         txt(9.0, 11.9, "5 V fixe", 1.1, "#fff", "middle", True)]
    for nom, x, y in pastilles:
        d.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="1.05" fill="#d4af37" stroke="#7a6420" stroke-width="0.15"/>')
        dy = 2.9 if y < h / 2 else -1.7
        d.append(txt(x, y + dy, nom, 0.9, "#fff", "middle"))
    return Piece("Abaisseur_5V", "Mini abaisseur 5 V fixe", l, h, list(pastilles), "".join(d),
                 "Mini abaisseur à découpage, entrée 5 à 30 V, sortie fixe 5,0 V, 18 x 13 mm.", broche=0.8)


def diode_do41():
    """Diode Schottky 1N5819 (boîtier DO-41) couchée, pattes au pas de 400 mil ; cathode à gauche."""
    l, h = 11.0, 2.8
    d = ['<line x1="0.42" y1="1.4" x2="10.58" y2="1.4" stroke="#9e9e9e" stroke-width="0.6"/>',
         '<rect x="2.9" y="0.05" width="5.2" height="2.7" rx="0.5" fill="#212121"/>',
         '<rect x="3.3" y="0.05" width="0.8" height="2.7" fill="#cfd8dc"/>']
    return Piece("Diode_1N5819", "Diode Schottky 1N5819", l, h, [("K", 0.42, 1.4), ("A", 10.58, 1.4)], "".join(d),
                 "Diode Schottky 1N5819 (DO-41), couchée, pattes au pas de 10,16 mm.", broche=0.6)


def plaque_reelle(ix, iy):
    """Bords réels de la plaque 7 × 9 cm, avec ses 4 trous de fixation Ø3 : un cadre autour de la
    plaque de Fritzing (et de ses trous), dont le coin est en ix, iy."""
    l, h = REEL
    il, ih = PAS * (TROUS[0] + 1), PAS * (TROUS[1] + 1)
    d = [f'<path d="M0,0 H{f(l)} V{f(h)} H0 Z M{f(ix)},{f(iy)} V{f(iy + ih)} H{f(ix + il)} V{f(iy)} Z" '
         f'fill="#d9b06c" fill-rule="evenodd"/>',
         f'<rect x="0.2" y="0.2" width="{f(l - 0.4)}" height="{f(h - 0.4)}" rx="1" fill="none" stroke="#8a6a30" '
         f'stroke-width="0.35"/>']
    d += [f'<circle cx="{f(cx)}" cy="{f(cy)}" r="1.6" fill="#fff" stroke="#8a6a30" stroke-width="0.3"/>'
          for cx in (3.0, l - 3.0) for cy in (3.0, h - 3.0)]
    return Piece("Plaque_7x9", "Plaque à pastilles 7 x 9 cm", l, h, [], "".join(d),
                 "Contour de la plaque à pastilles 7 x 9 cm et ses trous de fixation.")


def elko(valeur="100µF", tension="25V", d=6.3, vertical=False):
    """Condensateur électrolytique radial vu de dessus (Ø6,3 mm, pattes au pas de 2,54 mm).
    vertical : pattes l'une au-dessus de l'autre (+ en haut), sous le centre de la boîte."""
    r = d / 2
    if vertical:
        dessin = (f'<circle cx="{f(r)}" cy="{f(r)}" r="{f(r)}" fill="#1d2b5c" stroke="#0b1430" stroke-width="0.2"/>'
                  f'<path d="M0,{f(r)} A{f(r)},{f(r)} 0 0 0 {f(d)},{f(r)} L{f(d - 0.1)},{f(r + 1.3)} '
                  f'A{f(r)},{f(r)} 0 0 1 0.1,{f(r + 1.3)} Z" fill="#9fb3d9"/>'
                  + txt(r, r - 1.5, valeur, 0.95, "#fff", "middle") + txt(r, r + 0.4, tension, 0.85, "#fff", "middle")
                  + txt(r, r + 2.6, "−", 1.4, "#1d2b5c", "middle"))
        return Piece("Elko_100uF_v", f"Condensateur électrolytique {valeur} {tension}", d, d,
                     [("+", r, r - 1.27), ("-", r, r + 1.27)], dessin,
                     f"Condensateur électrolytique radial {valeur} {tension}, Ø{d} mm, vu de dessus.", broche=0.6)
    dessin = (f'<circle cx="{f(r)}" cy="{f(r)}" r="{f(r)}" fill="#1d2b5c" stroke="#0b1430" stroke-width="0.2"/>'
              f'<path d="M{f(r)},0 A{f(r)},{f(r)} 0 0 1 {f(r)},{f(d)} L{f(r + 1.3)},{f(d - 0.1)} '
              f'A{f(r)},{f(r)} 0 0 0 {f(r + 1.3)},0.1 Z" fill="#9fb3d9"/>'
              f'<circle cx="{f(r)}" cy="{f(r)}" r="{f(r * 0.62)}" fill="none" stroke="#7c8fb8" stroke-width="0.25"/>'
              + txt(r - 0.6, r - 0.4, valeur, 0.95, "#fff", "middle") + txt(r - 0.6, r + 0.9, tension, 0.85, "#fff",
                                                                           "middle")
              + txt(r + 2.3, r + 0.4, "−", 1.4, "#1d2b5c", "middle"))
    return Piece("Elko_100uF", f"Condensateur électrolytique {valeur} {tension}", d, d,
                 [("+", r - 1.27, r + 2.0), ("-", r + 1.27, r + 2.0)], dessin,
                 f"Condensateur électrolytique radial {valeur} {tension}, Ø{d} mm, vu de dessus.", broche=0.6)


def ceramique():
    """Condensateur céramique 100 nF vu de dessus, 4 × 2,5 mm, pattes au pas de 2,54 mm."""
    dessin = ('<rect x="0" y="0" width="4" height="2.5" rx="1" fill="#2f6db5" stroke="#1a3f6b" stroke-width="0.15"/>'
              + txt(2, 1.6, "104", 1.0, "#fff", "middle"))
    return Piece("Ceramique_100nF", "Condensateur céramique 100 nF", 4, 2.5,
                 [("1", 0.73, 1.25), ("2", 3.27, 1.25)], dessin,
                 "Condensateur céramique 100 nF (code 104), vu de dessus.", broche=0.5)


def cartouche(l, lignes):
    """Panneau de texte : lignes (texte, taille, gras) ; sa hauteur suit le texte."""
    h = round(4.5 + sum(t * 1.45 for _l, t, _g in lignes) + 0.5, 1)
    d = [f'<rect x="0" y="0" width="{l}" height="{h}" rx="1.5" fill="#fff8e1" stroke="#f29900" stroke-width="0.5"/>']
    y = 4.5
    for t, taille, gras in lignes:
        if t:
            d.append(txt(3, y, t, taille, "#202124", "start", gras))
        y += taille * 1.45
    return Piece("Cartouche", "Explications", l, h, [], "".join(d), "Explications de l'implantation.")


def regle(longueur):
    """Règle graduée en mm, numérotée en cm."""
    d = [f'<rect x="0" y="0" width="{longueur}" height="7" fill="#fffbe6" stroke="#8a7a3a" stroke-width="0.2"/>']
    for mm in range(longueur + 1):
        h = 3.2 if mm % 10 == 0 else (2.2 if mm % 5 == 0 else 1.3)
        d.append(f'<line x1="{mm}" y1="0" x2="{mm}" y2="{h}" stroke="#333" stroke-width="0.15"/>')
        if mm % 10 == 0 and 0 < mm < longueur - 8:
            d.append(txt(mm, 5.8, str(mm // 10), 2.0, "#333", "middle"))
    d.append(txt(0.6, 5.8, "0", 2.0, "#333"))
    d.append(txt(longueur - 0.6, 5.8, f"{longueur // 10} cm", 2.0, "#333", "end"))
    return Piece(f"Regle_{longueur}", f"Règle {longueur} mm", longueur, 7, [], "".join(d), "Règle graduée.")


def boitier(l, h):
    """Contour intérieur du boîtier étanche ; repères des traversées (presse-étoupes et interrupteur
    en haut, antenne, USB-C et aérateur à gauche, charnière de la porte en bas)."""
    d = [f'<rect x="0.3" y="0.3" width="{f(l - 0.6)}" height="{f(h - 0.6)}" rx="3" fill="none" stroke="#5f6368" '
         f'stroke-width="0.7" stroke-dasharray="3,1.5"/>',
         txt(l - 38, 5.2, f"Boîtier étanche IP65 à porte : intérieur {l} × {h} mm,", 2.2, "#3c4043", "middle",
             True),
         txt(l - 38, 9.4, "120 mm de haut (boîtier d'environ 220 × 150 × 140 mm)", 2.0, "#3c4043", "middle"),
         txt(60, 3.0, "6 presse-étoupes PG7 : moteurs M1 et M2, fin de course, Hall, capteur solaire, panneau",
             1.8, "#3c4043", "middle"),
         txt(2.2, 50, "antenne LoRa (traversée SMA étanche)", 1.8, "#3c4043", "start", rot=-90),
         txt(2.2, 82, "pas de découpe USB-C", 1.8, "#3c4043", "start", rot=-90),
         f'<circle cx="0.3" cy="{f(h - 10)}" r="2.6" fill="#90a4ae" stroke="#37474f" stroke-width="0.4"/>',
         txt(2.2, h - 14, "aérateur (M12, IP67)", 1.8, "#3c4043", "start", rot=-90)]
    return Piece(f"Boitier_{l}x{h}", f"Boîtier étanche {l} x {h} mm", l, h, [], "".join(d),
                 "Contour intérieur du boîtier étanche.")


# ---------------------------------------------------------------------------
# CROQUIS FRITZING

class Croquis:
    def __init__(self):
        self.instances, self.pieces, self.index = [], {}, 100

    def _inst(self, module, chemin, titre, x, y, z, props=(), couche="breadboard", etiquette=None, extra=""):
        self.index += 1
        p = "".join(f'<property name="{k}" value={quoteattr(v)}/>' for k, v in props)
        tg = ""
        if etiquette:
            ex, ey = etiquette
            tg = (f'<titleGeometry visible="true" x="{f(ex * PX)}" y="{f(ey * PX)}" z="{f(z + 10)}" '
                  f'xOffset="0" yOffset="0" textColor="#000000" fontSize="5"/>')
        self.instances.append(
            f'<instance moduleIdRef={quoteattr(module)} modelIndex="{self.index}" path={quoteattr(chemin)}>{p}'
            f'<title>{escape(titre)}</title>{extra}<views><breadboardView layer="{couche}">'
            f'<geometry x="{f(x * PX)}" y="{f(y * PX)}" z="{f(z)}"/>{tg}</breadboardView>'
            f'<schematicView layer="schematic"><geometry x="{f(x * PX)}" y="{f(y * PX + 2000)}" z="2.5"/>'
            f'</schematicView><pcbView layer="copper0"><geometry x="{f(x * PX)}" y="{f(y * PX + 4000)}" '
            f'z="2.5"/></pcbView></views></instance>')

    def piece(self, p, titre, x, y, etiquette=None, z=2.5):
        """Pièce dessinée ici, placée par son coin haut gauche (mm, repère de la plaque)."""
        self.pieces[p.module_id] = p
        self._inst(p.module_id, f"tracker_{p.cle.lower()}.fzp", titre, x, y, z, etiquette=etiquette)

    def standard(self, module, fzp, titre, x, y, props=(), etiquette=None):
        self._inst(module, f"/usr/share/fritzing/parts/core/{fzp}", titre, x, y, 2.6, props, etiquette=etiquette)

    def plaque(self, x, y):
        cols, rangs = TROUS
        self._inst(f"{cols}.{rangs}PerfboardModuleID", "", "Plaque à pastilles", x, y, 1.5,
                   (("size", f"{cols}.{rangs}"),), couche="breadboardbreadboard")

    def ecrire(self, chemin):
        fz = ('<?xml version="1.0" encoding="UTF-8"?>\n<module fritzingVersion="1.0.1">'
              '<views><view name="breadboardView" backgroundColor="#ffffff" gridSize="0.1in" showGrid="0" '
              'alignToGrid="0" viewFromBelow="0"/><view name="schematicView" backgroundColor="#ffffff" '
              'gridSize="0.1in" showGrid="1" alignToGrid="1" viewFromBelow="0"/><view name="pcbView" '
              'backgroundColor="#333333" gridSize="0.05in" showGrid="1" alignToGrid="1" viewFromBelow="0"/>'
              f'</views><instances>{"".join(self.instances)}</instances></module>\n')
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        def ajouter(z, nom, contenu):       # date fixe : fichier identique d'une génération à l'autre
            info = zipfile.ZipInfo(nom, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, contenu)

        with zipfile.ZipFile(chemin, "w") as z:
            ajouter(z, "Implantation_Boitier.fz", fz)
            for p in self.pieces.values():
                nom, fzp, svgs = p.fichiers()
                ajouter(z, "part." + nom, fzp)
                for img, svg in svgs.items():
                    ajouter(z, "svg." + img.replace("/", "."), svg)


def trou(c, r):
    """Centre du trou (colonne c, rang r) de la plaque, en mm depuis son coin haut gauche."""
    return (PAS * (c + 1), PAS * (r + 1))


def sur_trou(p, c, r, i=0):
    """Coin haut gauche de la pièce p pour que sa broche i tombe sur le trou (c, r)."""
    tx, ty = trou(c, r)
    _n, bx, by = p.broches[i]
    return (tx - bx, ty - by)


def main():
    k = Croquis()
    hel, tmc, ads, u1 = heltec_v4(), tmc2209(), ads1115(), abaisseur_5v()
    b4, t2, t3, t5 = bornier(4), bornier_254(2), bornier_254(3), bornier_254(5)
    el, ce, j1, d1 = elko(vertical=True), ceramique(), barrette_2x4(), diode_do41()

    # boîtier : plaque réelle à 12 mm de la paroi gauche (place pour un câble USB-C coudé) et
    # à 14 mm de celle du haut (arrivée des câbles des presse-étoupes)
    rx = PAS - (REEL[0] - (TROUS[0] - 1) * PAS) / 2      # coin de la plaque réelle, repère de Fritzing
    ry = PAS - (REEL[1] - (TROUS[1] - 1) * PAS) / 2
    bl, bh, ecart = 196, 120, 12                         # intérieur du boîtier ; place de la charnière
    bx, by = 12 - rx, 14 - ry                            # coin de la plaque de Fritzing dans le boîtier
    k.piece(boitier(bl, bh), "Boîtier", -bx, -by, z=1.2)
    k.piece(plaque_reelle(-rx, -ry), "Plaque 7 × 9 cm", rx, ry, z=1.3)
    k.plaque(0, 0)

    def dedans(x, y):
        """Position dans le boîtier (depuis le coin intérieur haut gauche) -> repère de la plaque."""
        return (x - bx, y - by)

    # bord haut : les câbles de la tête, chacun au-dessus de ce qu'il dessert
    for p, c, titre in ((b4, 1, "X2 moteur M1"), (b4, 9, "X3 moteur M2"), (t2, 17, "X4 FDC"),
                        (t3, 20, "X5 Hall"), (t5, 24, "X6 capteur solaire")):
        k.piece(p, titre, *sur_trou(p, c, 2), etiquette=(trou(c, 2)[0] - 1.5, -2.6))

    # les deux drivers sous leurs borniers, chacun avec son 100 µF contre VM et GND
    for c, ref, cond, cc in ((0, "U2 (élévation)", "C1", 7), (9, "U3 (azimut)", "C2", 16)):
        x, y = sur_trou(tmc, c, 4)
        k.piece(tmc, ref, x, y, etiquette=(x, 9.0))
        k.piece(el, cond, *sur_trou(el, cc, 4), etiquette=(trou(cc, 4)[0] - 1.2, 17.6))

    # ADS1115 sous X6 : les 4 photodiodes tombent droit sur A0 à A3 ; filtres juste dessous
    k.piece(ads, "A2 ADS1115", *sur_trou(ads, 19, 11), etiquette=(48.4, 11.6))
    for i in range(4):
        x, y = trou(20, 13 + i)
        k.standard("ResistorModuleID", "resistor.fzp", f"R{i + 1}", x - 0.37, y - 1.28,
                   (("resistance", "1kΩ"), ("tolerance", "±1%"), ("pin spacing", "400 mil")),
                   etiquette=(50.2, y - 1.0))
        k.piece(ce, f"C{i + 3}", *sur_trou(ce, 26, 13 + i), etiquette=(64.3, y - 1.0))

    # Heltec V4 en bas, USB-C au bord gauche ; le long du bas, D1 et les tirages, près de leurs broches
    k.piece(hel, "A1 Heltec WiFi LoRa 32 V4", *sur_trou(hel, 0, 13), etiquette=(1.0, 31.9))
    k.piece(d1, "D1", *sur_trou(d1, 0, 23), etiquette=(trou(1, 23)[0] - 0.6, 62.4))
    for c, titre in ((5, "R6"), (10, "R5"), (15, "R7")):
        x, y = trou(c, 23)
        k.standard("ResistorModuleID", "resistor.fzp", titre, x - 0.37, y - 1.28,
                   (("resistance", "10kΩ"), ("pin spacing", "400 mil")), etiquette=(x + 3.6, 62.4))

    # bord droit, vers l'énergie : bus I2C des wattmètres, abaisseur 5 V, arrivée 12 V
    k.piece(j1, "J1 I2C", *sur_trou(j1, 28, 13), etiquette=(72.0, 31.9))
    k.piece(u1, "U1 abaisseur 5 V", *sur_trou(u1, 20, 18), etiquette=(52.0, 60.4))
    x1 = bornier(2, droite=True)
    k.piece(x1, "X1 12 V", *sur_trou(x1, 29, 18), etiquette=(72.0, 56.6))

    # énergie : batterie debout à droite de la plaque, bornes vers la charnière (− à gauche, + à
    # droite), F2 juste devant son + ; couloir de câblage de 18 mm entre la plaque et la batterie ;
    # wattmètres sous la plaque ; interrupteur sur la paroi du haut
    batterie = (120, 14, 190, 102)
    k.piece(batterie_plomb(), "G1 batterie", *dedans(batterie[0], batterie[1]))
    k.piece(porte_fusible("F2", False), "F2 (près de G1+)", *dedans(128, 106), etiquette=dedans(105.0, 108.6))
    a4, a5 = ina219_adafruit(), sen0291()
    k.piece(a4, "A4 INA219B (panneau)", *dedans(14, 90), etiquette=dedans(14, 111.6))
    k.piece(a5, "A5 SEN0291 (12 V)", *dedans(48, 89.5), etiquette=dedans(48, 112.6))
    k.standard("Taiway-100-SP-X-T1-X-X-B1-M1_SPDT_miniature_toggle_switch",
               "Taiway-100-SP-X-T1-X-X-B1-M1_SPDT_miniature_toggle_switch.fzp", "S1",
               *dedans(104, -13.4), (("part number", "marche / arrêt, étanche"),),
               etiquette=dedans(118, -12.6))

    # la porte, ouverte sous le boîtier : régulateur vissé dessus, au droit de la plaque et des
    # wattmètres (porte fermée), jamais au droit de la batterie ; F1 contre ses bornes
    def porte_ouverte(x, y):
        """Position sur la porte (depuis son coin, côté charnière) -> repère de la plaque."""
        return (x - bx, bh - by + ecart + y)

    k.piece(porte(bl, bh, ecart, batterie), "Porte", -bx, bh - by, z=1.2)
    k.piece(regulateur_sol10uc3(), "A6 régulateur SOL10UC3", *porte_ouverte(8, 6))
    k.piece(porte_fusible("F1", False), "F1 (sortie LOAD)", *porte_ouverte(124, 4),
            etiquette=porte_ouverte(124, 14.6))

    # règle, explications
    k.piece(regle(bl), "Règle", -bx, 2 * bh - by + ecart + 5)
    k.piece(cartouche(86, (
        ("Boîtier étanche, au pied du trépied", 2.6, True),
        ("Tout ce qui n'est pas sur la tête, régulateur, batterie et", 1.9, False),
        ("fusibles compris : seuls la tête et le panneau sont dehors.", 1.9, False),
        ("Dessin à l'échelle : le boîtier vu de dessus et, sous lui,", 1.9, False),
        ("sa porte ouverte, vue de l'intérieur.", 1.9, False),
        ("", 1.0, False),
        ("Plaque à pastilles 7 × 9 cm, 24 × 30 trous", 2.1, True),
        ("Pas de 2,54 mm ; 4 trous de fixation Ø3 (entretoises M3).", 1.9, False),
        ("En haut, les câbles de la tête, chacun au-dessus de ce", 1.9, False),
        ("qu'il dessert : moteurs (X2, X3) sur leurs drivers, capteurs", 1.9, False),
        ("(X4 à X6) sur l'ADS1115. À droite, vers l'énergie : J1 (I2C", 1.9, False),
        ("des wattmètres), U1 et X1 (12 V). En bas, le Heltec, USB-C", 1.9, False),
        ("au bord, avec D1 et R5 à R7 près de leurs broches.", 1.9, False),
        ("Aucune pièce sous un module : tout reste accessible.", 1.9, False),
        ("", 1.0, False),
        ("Hauteur au-dessus de la plaque", 2.1, True),
        ("TMC2209 sur barrettes, avec dissipateur : ≈ 20 mm", 1.9, False),
        ("Heltec V4 et ADS1115 sur barrettes : ≈ 14 mm", 1.9, False),
        ("100 µF : ≈ 12 mm ; borniers : ≈ 10 mm ; U1 : ≈ 5 mm", 1.9, False),
        ("Batterie : 100 mm de haut (≈ 106 avec ses bornes) ;", 1.9, False),
        ("boîtier de 120 mm au moins à l'intérieur.", 1.9, False),
        ("Plaque sur entretoises de 6 mm.", 1.9, False),
        ("", 1.0, False),
        ("Modules sur barrettes femelles (démontables)", 2.1, True),
        ("Heltec 2 × 18, TMC2209 2 × 8 chacun, ADS1115 1 × 10.", 1.9, False),
        ("", 1.0, False),
        ("Alimentation 5 V", 2.1, True),
        ("U1 : mini abaisseur, sortie fixe 5,0 V, 18 × 13 mm, soudé", 1.9, False),
        ("à plat par 4 pattes. Mesurer sa sortie (4,9 à 5,2 V) avant", 1.9, False),
        ("de poser le Heltec. Le Hall (X5) est pris avant D1 ; le", 1.9, False),
        ("Heltec, après D1, reçoit ≈ 4,7 V.", 1.9, False),
        ("", 1.0, False),
        ("Borniers à vis", 2.1, True),
        ("Pas de 5,08 mm (KF301) : X1, 12 V (depuis A5 IN-) et 0 V", 1.9, False),
        ("(LOAD- du régulateur), AWG 18 ; X2 et X3, moteurs, AWG 22.", 1.9, False),
        ("Pas de 2,54 mm (DG308), câbles AWG 26 : X4 fin de course,", 1.9, False),
        ("2 pôles ; X5 Hall, 3 pôles ; X6 capteur solaire, 5 pôles.", 1.9, False),
        ("Sur la plaque : AWG 20 pour le 12 V et son 0 V, AWG 22", 1.9, False),
        ("pour le 5 V, AWG 24 pour les signaux (folio 3 du schéma).", 1.9, False),
        ("", 1.0, False),
        ("Wattmètres, sous la plaque, sur entretoises", 2.1, True),
        ("A5 SEN0291 (12 V du tracker, 0x45) : S1 -> IN+, IN- -> X1+.", 1.9, False),
        ("A4 INA219B (panneau, 0x40) : panneau + -> VIN+, VIN- ->", 1.9, False),
        ("PV+ de A6 ; panneau - sur PV- de A6, jamais au 0 V.", 1.9, False),
        ("Bus I2C par J1 (3V3, GND, SDA, SCL) : câble STEMMA QT", 1.9, False),
        ("pour A4, câble Gravity pour A5.", 1.9, False),
        ("", 1.0, False),
        ("Repères", 2.1, True),
        ("Ceux du schéma électrique, qui donne le câblage :", 1.9, False),
        ("Electronique/Schema_Electrique.qet.", 1.9, False),
        ("Broches du Heltec utilisées par le tracker : en orange.", 1.9, False),
        ("", 1.0, False),
        ("Énergie", 2.1, True),
        ("G1 batterie plomb 12 V 5 Ah, debout à droite de la plaque,", 1.9, False),
        ("sanglée, bornes vers la charnière : - à gauche, + à droite.", 1.9, False),
        ("F2 : porte-fusible en ligne sur le fil G1+ -> A6, juste", 1.9, False),
        ("devant G1+ (moins de 10 cm). F1 : sur le fil LOAD+, sur", 1.9, False),
        ("la porte, contre la borne LOAD. Fusibles 3 A ; un fusible", 1.9, False),
        ("protège le fil qui le suit : les deux fils + qui passent la", 1.9, False),
        ("charnière (BAT+ et LOAD+) sont donc protégés.", 1.9, False),
        ("Brancher G1 en premier, puis le panneau, puis LOAD.", 1.9, False),
        ("", 1.0, False),
        ("Régulateur A6 sous la porte", 2.1, True),
        ("Vissé par 4 vis inox à rondelle d'étanchéité (ou collé).", 1.9, False),
        ("Porte fermée, il descend de 35 mm (25 mm et ses fils) au-", 1.9, False),
        ("dessus de la plaque et des wattmètres, qui montent à", 1.9, False),
        ("34 mm au plus : jamais au-dessus de la batterie (106 mm).", 1.9, False),
        ("Ses 6 fils passent la charnière en une boucle souple", 1.9, False),
        ("(multibrin, gaine spirale), attachée de chaque côté, à", 1.9, False),
        ("l'intérieur du joint : la porte ne doit pas les pincer.", 1.9, False),
        ("", 1.0, False),
        ("Étanchéité (IP65)", 2.1, True),
        ("6 presse-étoupes PG7 sur une même paroi, câbles avec", 1.9, False),
        ("une boucle d'égouttement. S1 étanche (capuchon).", 1.9, False),
        ("Traversée SMA étanche, aérateur à membrane, sachet", 1.9, False),
        ("de gel de silice. Pas de découpe USB-C : reprogrammer", 1.9, False),
        ("porte ouverte (câble USB-C coudé), ou par le WiFi (OTA).", 1.9, False),
        ("Boîtier opaque et clair, à l'ombre : A6, sur la porte, ne", 1.9, False),
        ("supporte que 55 °C, et la batterie craint la chaleur.", 1.9, False),
    )), "Explications", bl - bx + 12, -by)
    k.ecrire(SORTIE)
    print(f"{SORTIE} : {len(k.instances)} éléments, {len(k.pieces)} pièces dessinées")


if __name__ == "__main__":
    main()
