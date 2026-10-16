"""Implantation du boîtier électronique de la démonstration, au format Fritzing (vue platine).

Écrit Electronique/Implantation_Boitier.fzz : une plaque à pastilles de 8 × 12 cm avec, à
l'échelle, tout ce qui reste au pied du trépied (Heltec WiFi LoRa 32 V4, 2 TMC2209, ADS1115,
abaisseur LM2596, borniers, résistances et condensateurs), et à côté d'elle, dans le boîtier,
les deux wattmètres INA219 (INA219B d'Adafruit pour le panneau, SEN0291 de DFRobot pour le
12 V du tracker). Ce qui est sur la tête (moteurs, fin de course, capteur Hall, photodiodes,
panneau) n'y est pas : on n'en voit que les borniers.

Pièces standard de Fritzing : LM2596, résistances, diode, interrupteur et plaque à pastilles. Le Heltec V4, le TMC2209, l'ADS1115,
les deux wattmètres, la barrette J1 et les borniers au pas de 5,08 mm n'existent pas dans
Fritzing (ou pas à l'échelle) : ils sont dessinés ici, à leurs dimensions réelles, et intégrés
au fichier.

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
TROUS = (46, 30)            # plaque de 46 × 30 trous : 119,4 × 78,7 mm (format « 8 × 12 cm »)


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


def bornier(n):
    """Bornier à vis au pas de 5,08 mm (type KF301), n pôles, vu de dessus, entrées des fils en haut."""
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
    return Piece(f"Bornier_{n}p", f"Bornier à vis {n} pôles, pas 5,08 mm", l, h, broches, "".join(d),
                 f"Bornier à vis {n} pôles au pas de 5,08 mm (KF301), {f(l)} x 7,6 mm.")


def elko(valeur="100µF", tension="25V", d=6.3):
    """Condensateur électrolytique radial vu de dessus (Ø6,3 mm, pattes au pas de 2,54 mm)."""
    r = d / 2
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


def cartouche(l, h, lignes):
    """Panneau de texte : lignes (texte, taille, gras)."""
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
        if mm % 10 == 0 and 0 < mm < longueur:
            d.append(txt(mm, 5.8, str(mm // 10), 2.0, "#333", "middle"))
    d.append(txt(0.6, 5.8, "0", 2.0, "#333"))
    d.append(txt(longueur - 0.6, 5.8, f"{longueur // 10} cm", 2.0, "#333", "end"))
    return Piece(f"Regle_{longueur}", f"Règle {longueur} mm", longueur, 7, [], "".join(d), "Règle graduée.")


def boitier(l, h, plaque, px):
    """Contour intérieur du boîtier, la plaque à px de la paroi gauche (USB-C) et centrée en hauteur ;
    repères des traversées."""
    py = (h - plaque[1]) / 2
    d = [f'<rect x="0.3" y="0.3" width="{f(l - 0.6)}" height="{f(h - 0.6)}" rx="2" fill="none" stroke="#5f6368" '
         f'stroke-width="0.6" stroke-dasharray="3,1.5"/>',
         txt(l / 2, h - 1.6, f"Boîtier : intérieur {l} × {h} mm (boîtier de 200 × 120 × 75 mm)", 2.2, "#3c4043",
             "middle", True),
         txt(px + 70, 2.9, "presse-étoupes : câbles des moteurs, du fin de course, du capteur Hall, du panneau "
             "et du régulateur", 1.6, "#3c4043", "middle"),
         txt(px + 100, h - 4.3, "presse-étoupe : câble du capteur solaire", 1.6, "#3c4043", "middle"),
         txt(2.0, py + 31.5, "découpe USB-C", 1.6, "#3c4043", "start", rot=-90),
         txt(l - 1.8, py + 52, "antenne LoRa (traversée SMA)", 1.6, "#3c4043", "start", rot=90),
         txt(2.0, py + 11.5, "entrée 12 V", 1.6, "#3c4043", "start", rot=-90)]
    return Piece(f"Boitier_{l}x{h}", f"Boîtier {l} x {h} mm", l, h, [], "".join(d), "Contour intérieur du boîtier.")


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
    hel, tmc, ads = heltec_v4(), tmc2209(), ads1115()
    b2, b3, b4, b5 = bornier(2), bornier(3), bornier(4), bornier(5)
    plaque = (PAS * (TROUS[0] + 1), PAS * (TROUS[1] + 1))
    bl, bh, bx = 190, 110, 15.3                 # intérieur du boîtier ; plaque à 15,3 mm de la paroi gauche
    k.piece(boitier(bl, bh, plaque, bx), "Boîtier", -bx, -(bh - plaque[1]) / 2, z=1.2)
    k.plaque(0, 0)

    # bord haut : arrivée 12 V (le fusible F1 est en ligne, près de la batterie), panneau, câbles vers la tête
    k.piece(b2, "X1 12 V", *sur_trou(b2, 0, 2), etiquette=(1, -3.2))
    k.piece(b4, "X7 panneau", *sur_trou(b4, 5, 2), etiquette=(trou(5, 2)[0] - 1, -3.2))
    for p, c, titre in ((b4, 15, "X2 moteur M1"), (b4, 24, "X3 moteur M2"), (b2, 33, "X4 FDC"),
                        (b3, 38, "X5 Hall")):
        x, _y = trou(c, 2)
        k.piece(p, titre, *sur_trou(p, c, 2), etiquette=(x - 2, -3.2))

    # Heltec V4, USB-C au bord gauche, et les deux drivers avec leurs 100 µF
    k.piece(hel, "A1 Heltec WiFi LoRa 32 V4", *sur_trou(hel, 1, 5), etiquette=(2, 40.5))
    el, ce = elko(), ceramique()
    for c, ref, cond in ((22, "U2 (élévation)", "C1"), (30, "U3 (azimut)", "C2")):
        x, y = sur_trou(tmc, c, 5)
        k.piece(tmc, ref, x, y, etiquette=(x, 10.4))
        k.piece(el, cond, *sur_trou(el, c + 5, 15), etiquette=(trou(c + 5, 15)[0] + 4.0, 38.4))
    j1 = barrette_2x4()
    k.piece(j1, "J1 I2C", *sur_trou(j1, 44, 12), etiquette=(120.2, 34.4))
    for i, titre in enumerate(("R5", "R6", "R7")):
        x, y = trou(39, 6 + 2 * i)
        k.standard("ResistorModuleID", "resistor.fzp", titre, x, y - 1.2,
                   (("resistance", "10kΩ"), ("pin spacing", "400 mil")), etiquette=(x + 11.5, y - 1.0))

    # bas : alimentation 5 V, convertisseur du capteur solaire et ses filtres
    k.standard("RioRand_LM2596_94ce9810d0922bc731e2f315085d46ab_1",
               "RioRand_LM2596_94ce9810d0922bc731e2f315085d46ab_1.fzp", "U1 LM2596 réglé à 5,3 V",
               1.0, 53.5, etiquette=(1, 77.3))
    k.standard("145554CBFC44diode", "diode_schottky_1N5817_300mil.fzp", "D1", 6.0, 46.0,
               (("part number", "1N5819"),), etiquette=(18, 45.2))
    k.piece(ads, "A2 ADS1115", *sur_trou(ads, 22, 25), etiquette=(56, 68.2))
    for i in range(4):
        x, y = trou(35, 17 + 2 * i)
        k.standard("ResistorModuleID", "resistor.fzp", f"R{i + 1}", x, y - 1.2,
                   (("resistance", "1kΩ"), ("tolerance", "±1%"), ("pin spacing", "400 mil")),
                   etiquette=(x - 3.4, y - 1.0))
    for i in range(4):
        c, r = 41 + 2 * (i % 2), 17 + 4 * (i // 2)
        k.piece(ce, f"C{i + 3}", *sur_trou(ce, c, r), etiquette=(trou(c, r)[0] - 0.8, trou(c, r)[1] + 2.0))
    k.piece(b5, "X6 capteur solaire", *sur_trou(b5, 34, 27), etiquette=(87, 73.3))

    # à droite de la plaque, sur entretoises : les deux wattmètres INA219
    a5, a4 = sen0291(), ina219_adafruit()
    k.piece(a5, "A5 SEN0291 (12 V)", plaque[0] + 9, 4, etiquette=(plaque[0] + 9, 1.6))
    k.piece(a4, "A4 INA219B (panneau)", plaque[0] + 11, 40, etiquette=(plaque[0] + 11, 37.6))

    # hors de la plaque : interrupteur sur la paroi du boîtier, règle, explications
    k.standard("Taiway-100-SP-X-T1-X-X-B1-M1_SPDT_miniature_toggle_switch",
               "Taiway-100-SP-X-T1-X-X-B1-M1_SPDT_miniature_toggle_switch.fzp", "S1",
               -14.0, 44.0, (("part number", "marche / arrêt"),), etiquette=(-14.0, 57.5))
    k.piece(regle(bl), "Règle", -bx, (plaque[1] + bh) / 2 + 2)
    k.piece(cartouche(80, 124, (
        ("Boîtier électronique, au pied du trépied", 2.6, True),
        ("Tout ce qui n'est pas sur la tête. Dessin à l'échelle.", 1.9, False),
        ("Plaque à pastilles 8 × 12 cm, 46 × 30 trous au pas de 2,54 mm.", 1.9, False),
        ("", 1.0, False),
        ("Hauteur au-dessus de la plaque", 2.1, True),
        ("TMC2209 sur barrettes, avec dissipateur : ≈ 20 mm", 1.9, False),
        ("Heltec V4 sur barrettes : ≈ 14 mm ; LM2596 : ≈ 14 mm", 1.9, False),
        ("100 µF : ≈ 12 mm ; borniers : ≈ 10 mm", 1.9, False),
        ("Avec 6 mm d'entretoises sous la plaque : boîtier", 1.9, False),
        ("d'au moins 50 mm de haut à l'intérieur.", 1.9, False),
        ("", 1.0, False),
        ("Modules sur barrettes femelles (démontables)", 2.1, True),
        ("Heltec 2 × 18, TMC2209 2 × 8 chacun, ADS1115 1 × 10.", 1.9, False),
        ("", 1.0, False),
        ("Wattmètres, à droite de la plaque, sur entretoises", 2.1, True),
        ("A5 SEN0291 (12 V du tracker, 0x45) : S1 -> IN+, IN- -> X1+.", 1.9, False),
        ("A4 INA219B (panneau, 0x40) : X7-1 -> VIN+, VIN- -> X7-3.", 1.9, False),
        ("Bus I2C par J1 (3V3, GND, SDA, SCL) : câble STEMMA QT", 1.9, False),
        ("pour A4, câble Gravity pour A5. Fils de puissance de A4", 1.9, False),
        ("et A5 le long de la paroi du haut (AWG 20 et AWG 18).", 1.9, False),
        ("", 1.0, False),
        ("Borniers à vis au pas de 5,08 mm", 2.1, True),
        ("X1 : 12 V (depuis A5 IN-) et 0 V (LOAD- du régulateur), AWG 18", 1.9, False),
        ("X2 et X3 : moteurs M1 et M2, 4 pôles, câble AWG 22", 1.9, False),
        ("X4 : fin de course, 2 pôles ; X5 : Hall, 3 pôles ; AWG 26", 1.9, False),
        ("X6 : capteur solaire, 5 pôles, câble blindé AWG 26", 1.9, False),
        ("X7 : panneau (1 +, 2 -) et régulateur (3 +, 4 -), AWG 20 ;", 1.9, False),
        ("X7-2 relié à X7-4 seulement, pas au 0 V.", 1.9, False),
        ("Sur la plaque : AWG 20 pour le 12 V et son 0 V, AWG 22", 1.9, False),
        ("pour le 5 V, AWG 24 pour les signaux (folio 3 du schéma).", 1.9, False),
        ("", 1.0, False),
        ("Repères", 2.1, True),
        ("Ceux du schéma électrique, qui donne le câblage :", 1.9, False),
        ("Electronique/Schema_Electrique.qet.", 1.9, False),
        ("Broches du Heltec utilisées par le tracker : en orange.", 1.9, False),
        ("", 1.0, False),
        ("Traversées du boîtier", 2.1, True),
        ("Gauche : entrée 12 V, interrupteur S1, USB-C. Le fusible F1", 1.9, False),
        ("est en ligne sur le fil, près de la sortie LOAD du régulateur", 1.9, False),
        ("(ou du bloc secteur en intérieur).", 1.9, False),
        ("Haut : moteurs, fin de course, Hall, panneau, régulateur.", 1.9, False),
        ("Bas : câble du capteur solaire. Droite : antenne LoRa", 1.9, False),
        ("(câble IPEX vers une traversée SMA).", 1.9, False),
    )), "Explications", 180, -15.6)
    k.ecrire(SORTIE)
    print(f"{SORTIE} : {len(k.instances)} éléments, {len(k.pieces)} pièces dessinées")


if __name__ == "__main__":
    main()
