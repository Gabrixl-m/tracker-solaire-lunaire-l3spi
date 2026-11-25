# Liste des composants — cas terrestre (démonstration : tête à fourche imprimée en PETG, moteurs 28BYJ-48)

La liste des composants à commander, telle qu'elle a été envoyée au professeur (15 références
Gotronic), est dans [`tracker_solaire_composants.pdf`](tracker_solaire_composants.pdf) : elle
date de l'ancien modèle (moteurs NEMA, conservé dans le
[modèle idéal personnel](.modele_ideal_personnel/Liste-composants.md)). Le présent document est
la liste complète du **modèle actuel à fourche** : mécanique, visserie, électronique et consommables.

Tout ce qu'il faut acheter pour **une tête rotative à fourche et vis sans fin** en version PETG et son
**capteur solaire** (4 photodiodes sous une croix d'ombre, [README principal](README.md) § 4 et
[README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md) § 7), en plus des pièces imprimées de
`Fichiers 3D (CAO)/Cas Terrestre (démonstration)/a_imprimer/` (voir le [README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md), § 2).
L'élévation tourne sur **deux tiges d'acier Ø8** (62 et 40 mm), et les vis sans fin sur deux
arbres d'acier Ø5. Le plateau qui porte les bras est une **plaque d'aluminium de 5 mm** à faire
découper (§ 4).

* La colonne « À chercher » donne le nom à taper sur les sites marchands (AliExpress,
  Amazon, etc.), où ces pièces sont presque toujours vendues sous leur nom anglais.
* Les prix sont **indicatifs** (ordre de grandeur, par article).
* Les roulements sont en **rose** dans les fichiers 3D. Ils sont tous **protégés** : prendre
  de préférence la version **ZZ** (flasques métalliques), sinon 2RS (joints caoutchouc).

| Palier d'une vis sans fin | Élévation de la fourche : bras, étagère, roue |
|---|---|
| ![Palier : joues, roulements, arbre, vis](docs%20%28extra%29/explications/palier_joues_roulements.png) | ![Élévation de la fourche](docs%20%28extra%29/fourche_detail_elevation.png) |

---

## 1. Mécanique

| Article | Caractéristiques | Qté | À chercher | Où il va | ≈ Prix |
|---|---|---|---|---|---|
| **Roulement 6806ZZ** (ISO 61806-2Z) | 30 × 42 × 7 mm | 2 | `6806ZZ bearing 30x42x7` (ou `61806ZZ`) | Azimut : dans le socle, autour du moyeu | 3 € |
| **Roulement 608ZZ** (ISO 60-2Z) | 8 × 22 × 7 mm | 3 | `608ZZ bearing 8x22x7` | Élévation : deux dans le boss du bras droit, un dans le boss du bras gauche ; les tiges Ø8 tournent dedans | 1 € |
| **Roulement 685ZZ** | 5 × 11 × **5** mm | 4 | `685ZZ bearing 5x11x5` | Deux par vis sans fin, dans les joues des paliers | 1 € |
| **Accouplement flexible 5 mm / 5 mm**, **Ø14 × 19 mm** | Alésages Ø5 des deux côtés, alu. L'arbre du 28BYJ-48 est court : un Ø19 × 25 ne convient pas | 2 | `flexible shaft coupling 5mm x 5mm D14 L19` | Relie l'axe de chaque moteur à l'arbre de sa vis sans fin | 2–4 € |
| **Tige acier rectifiée Ø5** | Ø5 mm, au moins 110 mm | 1 | `linear shaft 5mm 150mm` (ou `5mm chrome steel rod`) | À couper en **2 × 53 mm** : les arbres des deux vis sans fin | 3–5 € |
| **Tige acier rectifiée Ø8** | Ø8 mm (tolérance h6 si possible), 102 mm au moins : prendre 150 mm | 1 | `linear shaft 8mm 150mm` (ou `8mm chrome steel rod`) | À couper en **62 mm** (tige droite, porte la roue d'élévation) et **40 mm** (tige gauche) : l'axe d'élévation | 3–5 € |
| *ou* **Rond plein acier Ø5** (en magasin) | Acier laminé à chaud, Ø5 mm, 1 m (par exemple STANDERS chez Leroy Merlin) | 1 | `rond plein acier 5 mm` | Pour les arbres des vis seulement, moins précis : voir « Pièges à éviter ». **Pas pour l'axe Ø8** : il porte des roulements 608 | 4–5 € |
| Rondelle de calage 8 × 14 × 0,5 mm (DIN 988) | Inox ou acier | 2 | `DIN 988 shim washer 8x14x0.5` | Entre le boss droit et la roue d'élévation : réduisent le jeu axial du panneau à environ 0,3 mm | 1 € |

**Pièges à éviter** :
* **Axe d'élévation** : une tige **rectifiée Ø8** (acier ou inox), lisse : les bagues intérieures des
  608 ont un alésage de 8 mm. Un rond laminé à chaud (Ø7,8 à 8,2) ne convient pas.
* **Arbres des vis** : une tige **lisse et pleine, en acier, Ø5**. Pas de tige filetée : les
  roulements porteraient sur les sommets du filet. Pas de tube, ni d'aluminium. Avec un rond
  plein laminé à chaud plutôt qu'une tige rectifiée :
  * le mesurer au pied à coulisse et garder les deux morceaux les plus réguliers ;
  * enlever le vernis là où vont les roulements, la vis sans fin et l'accouplement ;
  * entre 4,90 et 4,98 mm, coller les bagues intérieures des roulements à la colle à
    roulements ;
  * au-dessus de 5,00 mm, le poncer en le faisant tourner dans une perceuse (grain 400 à
    600) ;
  * limer un petit méplat sous la vis sans tête.
* **ZZ plutôt que 2RS** : les deux versions ont les mêmes cotes et vont toutes les deux
  dans les pièces. Mais les joints caoutchouc des 2RS frottent :
  * les deux 6806-2RS freinent l'azimut d'environ 0,15 N·m, et les deux 685-2RS prennent le
    quart du couple du moteur ;
  * avec des **28BYJ-48 si faibles**, la marge de l'azimut au vent de 10 m/s passe alors de ×1,7 à
    environ ×0,9 : **prendre des ZZ**.
* **685** : prendre une version protégée, **ZZ** (ou 2RS). Le 685 « ouvert » ne fait que
  3 mm de large, alors que les joues sont prévues pour 5 mm.
* **Accouplement** : bien **5 mm des deux côtés**. Les modèles 5 mm / 8 mm, très courants,
  sont faits pour les vis trapézoïdales d'imprimante 3D.
* **608** : le roulement des patins à roulettes, 8 × 22 × 7 mm, très courant. Prendre des **ZZ**.
* **Accouplement** : si le Ø14 × 19 est introuvable, un Ø14 × 25 peut convenir, mais la CAO est
  faite pour 19 mm (le lamage du support est calculé pour cette longueur).

## 2. Moteurs et électronique

| Article | Caractéristiques | Qté | À chercher | Rôle | ≈ Prix |
|---|---|---|---|---|---|
| **Moteur 28BYJ-48, 5 V**, avec sa carte **ULN2003** (kit courant) | 5 V, unipolaire, 5 fils, réducteur intégré 63,68:1, **34,3 mN·m** à l'arbre (25 retenu dans les calculs), environ 100 mA par bobine, 28 mm de diamètre, 2 oreilles à 35 mm, arbre Ø5 à méplats court et décentré de 8 mm, 30 g | 2 | `28BYJ-48 5V stepper motor ULN2003 driver board` | Élévation et azimut. **Tester chaque moteur avant montage** : ils sont très dispersés (README du cas terrestre, § 9) | 3–5 € pièce |
| **Extension d'entrées/sorties MCP23017** (module ou composant) | 16 sorties sur l'I²C, adresse 0x20 (A0, A1, A2 à la masse, RESET au 3,3 V) | 1 | `MCP23017 module I2C` | Pilote les 8 entrées IN1 à IN4 des deux cartes ULN2003 : le Heltec n'a pas assez de broches libres | 1–3 € |
| **Résistance 10 kΩ**, 1/4 W (tirage vers la masse des sorties du MCP23017) | | 8 | `10k ohm resistor 1/4W` | Évite qu'une bobine s'allume à la mise sous tension (les sorties du MCP23017 sont alors en haute impédance) | 0,1 € |
| **Heltec WiFi LoRa 32 V4**, version 863–870 MHz | ESP32-S3R2 + radio LoRa SX1262, écran OLED, USB-C, antenne LoRa 868 MHz fournie (IPEX). Prendre le V4 standard, **pas la variante V4-R8** (brochage différent) | 1 | `Heltec WiFi LoRa 32 V4 868MHz` | Commande des moteurs, lecture des capteurs, envoi des données en LoRa | 20–30 € |
| Module GNSS L76K pour Heltec V4 (facultatif) | Se branche sur le connecteur GNSS de la carte | 1 | `Heltec V4 GNSS L76K` | Heure et position pour le calcul du Soleil | 8–12 € |
| **Convertisseur ADS1115** (module) | 16 bits, 4 entrées, I²C (adresse 0x48), résistances de tirage I²C sur le module | 1 | `ADS1115 module 16 bit I2C` | Lit les 4 photodiodes du capteur solaire | 2–4 € |
| **Wattmètre INA219B d'Adafruit** (904, STEMMA QT) — **déjà en stock** | Shunt 0,1 Ω, ±3,2 A, 26 V au plus, I²C 0x40 ; 25,6 × 20,4 mm | 1 | `Adafruit 904 INA219` | A4 : ce que produit le panneau (README du cas terrestre, § 6) | 13 € |
| **Wattmètre SEN0291 de DFRobot** (INA219) — **déjà en stock** | Shunt 0,01 Ω, ±8 A, 26 V au plus, I²C 0x40 à 0x45 par micro-interrupteurs (**mettre 0x45**) ; 30 × 22 mm, câble Gravity fourni | 1 | `DFRobot SEN0291` | A5 : ce que consomme le tracker sur le 12 V | 8 € |
| Câble STEMMA QT / Qwiic vers broches femelles | JST SH 4 broches vers 4 fiches femelles au pas de 2,54 mm, 15 cm environ | 1 | `STEMMA QT to female socket cable` | Relie A4 à la barrette J1 de la plaque | 1 € |
| Bloc secteur 12 V 3 A (facultatif) | Pour l'établi seulement, porte ouverte : branché sur F1 à la place du régulateur et de la batterie. En intérieur, la batterie chargée tient 1,5 à 6 jours | 1 | `12V 3A power supply` | Essais sur l'établi | 10 € |
| **Batterie 12 V, en extérieur** — **fournie** | **Plomb étanche** (AGM, sans entretien), 12 V, 5 Ah (60 Wh), 88 × 70 × 100 mm, environ 1,9 kg. Couchée dans le boîtier (70 mm dans la profondeur) : possible avec une batterie étanche, jamais tête en bas. **Pas de LiFePO4** : le régulateur SOL10UC3 ne charge que le plomb, le gel et l'EFB | 1 | `12V 5Ah sealed lead acid battery` | Stocke l'énergie du panneau ; le tracker tient 1,5 à 6 jours sans soleil | fournie |
| **Régulateur de charge PWM 10 A Velleman SOL10UC3** (Gotronic, réf. 27118) | Batteries 12 ou 24 V (reconnues au branchement), plomb, gel ou EFB ; panneau 32 V au plus ; sortie LOAD coupée quand la batterie est basse ; port USB 5 V 1,2 A ; consommation < 6 mA ; 80 × 110 × 25 mm | 1 | `Velleman SOL10UC3` | A6 : le panneau recharge la batterie, le tracker se branche sur la sortie LOAD ; A4 mesure ce que produit le panneau | 35,80 € |
| **Fusible 3 A** et porte-fusible **en ligne** | Fusible 5 × 20 mm rapide ; porte-fusible pour fil AWG 18 | 2 (F1 près de la sortie LOAD ; F2 entre le régulateur et la batterie, **à moins de 10 cm de la batterie**) + 2 fusibles de rechange | `inline fuse holder 5x20 18AWG`, `fuse 3A 5x20` | Protège tout le câblage (une batterie au plomb débite des centaines d'ampères en court-circuit) | 4 € |
| **Interrupteur étanche** marche / arrêt | IP65 au moins : à bascule avec capuchon en silicone, ou à levier avec soufflet ; 12 V continu, 3 A au moins | 1 | `waterproof rocker switch IP65 12V` | S1, sur la paroi du boîtier : coupe tout | 3 € |
| **Mini abaisseur 12 V → 5 V** | Module à découpage, entrée 5 à 30 V, **sortie fixe 5,0 V**, 3 A annoncés (1,5 à 2 A en réalité, il en faut **au moins 0,6 A** : Heltec, Hall et un moteur 28BYJ-48 à la fois), environ 18 × 13 mm. Vérifier à réception que c'est bien la version 5 V : **mesurer sa sortie (4,9 à 5,2 V) avant de brancher le Heltec** | 1 | `mini buck converter 5V fixed 3A 5-30V` | U1 : alimente le Heltec (par D1), le capteur Hall et les moteurs (avant D1) | 2 € |
| **Diode Schottky 1N5819** | 1 A, 40 V | 1 | `1N5819` | Entre l'abaisseur et le Heltec : le 5 V de l'USB-C ne remonte pas dans l'abaisseur | 0,2 € |
| **Condensateur 100 µF 25 V** | Électrolytique | 1 | `100uF 25V capacitor` | Sur le 5 V, près des cartes ULN2003 | 0,2 € |
| **Fin de course** | Micro-rupteur à levier SPS75GCC (Gotronic), ou KW12. Branché sur son contact NC | 2 (1 de rechange) | `SPS75GCC`, `KW12 micro limit switch` | Origine de l'élévation, en butée basse | 3 € |
| **Capteur à effet Hall + aimant** | Capteur **A3144 nu** + aimant néodyme 5 × 2 mm. Pas de module KY-003 : il tire sa sortie au 5 V, trop pour l'ESP32 | 1 + 1 | `A3144 hall sensor`, `neodymium magnet 5x2mm` | Origine de l'azimut | 2 € |
| **Résistance 10 kΩ**, 1/4 W | Résistances de tirage au 3,3 V | 2 | `10k ohm resistor 1/4W` | Fin de course (R6) et capteur Hall (R7) | 0,1 € |
| **Fil souple AWG 18** (0,82 mm²), rouge et noir | Multibrin, isolant PVC ou silicone | 1 m de chaque | `18AWG silicone wire red black` | Dans le boîtier : sortie LOAD → F1 → S1 → A5 → X1 ; régulateur → F2 → batterie | 3 € |
| **Câble souple 2 conducteurs AWG 20** (0,52 mm²) | Multibrin, rouge et noir, gaine extérieure ronde (pour le presse-étoupe) | 2 m | `2 core 20AWG flexible cable` | Panneau → A4 (le +) et régulateur (le −), par la boucle de câble ; à souder sur les cosses du panneau | 2 € |
| **Fil AWG 20** (0,52 mm²), rouge et noir | Pour souder sur la plaque | 0,5 m de chaque | `20AWG hook up wire` | 12 V et 0 V de puissance sur la plaque (entrée de U1) ; A4 → régulateur | 2 € |
| **Fil AWG 22** (0,33 mm²), orange et noir | Pour souder sur la plaque | 0,5 m de chaque | `22AWG hook up wire` | 5 V : U1 → D1 → Heltec, U1 → capteur Hall | 2 € |
| **Fil de câblage monobrin AWG 24** (0,20 mm²) | Coffret de plusieurs couleurs | 1 coffret | `24AWG solid hook up wire kit` | Signaux et 3,3 V sur la plaque (IN1 à IN8, I²C, filtres) | 6 € |
| **Câble souple 5 conducteurs AWG 24** | Multibrin ; un câble réseau multibrin ou un câble de commande convient | 2 × 1,5 m | `5 core 24AWG flexible cable` | Rallonge de chaque moteur (4 bobines et le commun rouge), des borniers X2 et X3 aux moteurs, dont le câble d'origine ne fait que 25 cm | 5 € |
| **Câble souple 4 conducteurs AWG 26** | Multibrin (on n'utilise que 2 ou 3 conducteurs) | 2 × 1,5 m | `4 core 26AWG flexible cable` | Fin de course (X4, 2 fils) et capteur Hall (X5, 3 fils) | 3 € |
| Fil à wrapper AWG 28 ou 30 | Fil fin isolé | quelques dizaines de cm | `30AWG wire wrap` | Pattes des photodiodes, dans le boîtier du capteur | 2 € |
| **Embouts de câblage** et pince à sertir | Coffret 0,25 / 0,5 / 0,75 mm² | 1 | `ferrule kit crimping tool` | Bouts des fils dans les borniers à vis | 10–15 € |
| **Photodiode BPW34** (Vishay ou Osram) | Photodiode PIN au silicium, boîtier 5,4 × 4,3 × 3,2 mm, surface sensible 7,5 mm² | 4 + 1 de rechange | `BPW34` (Gotronic : réf. 03472) | Capteur solaire, une par coin de la croix | 1 € |
| **Résistance 1 kΩ**, couche métallique, ±1 %, 1/4 W, 50 ppm/°C | Environ 1,5 V en plein soleil ; la même valeur sert en intérieur, l'ADS1115 changeant de calibre | 4 + 2 de rechange | `1k ohm metal film resistor 1% 1/4W` | Une par photodiode, de l'anode à la masse, à côté de l'ADS1115 | 0,1 € |
| **Condensateur céramique 100 nF**, 50 V, X7R | Filtre le bruit (constante de temps 0,1 ms avec 1 kΩ) | 4 | `100nF ceramic capacitor 50V` | Un par photodiode, en parallèle sur sa résistance | 0,1 € |
| **Câble souple blindé 6 conducteurs AWG 26** | Multibrin, avec blindage (tresse ou feuillard) relié au 0 V côté boîtier seulement. À défaut : câble réseau blindé F/UTP multibrin | 1,5 m | `6 core 26AWG shielded cable` | Du capteur solaire au bornier X6 : 3,3 V et les 4 signaux | 3 € |
| Gaine thermorétractable fine | Ø1,5 à 2,5 mm | quelques cm | `heat shrink tube 2mm` | Isole les soudures des pattes des photodiodes | 1 € |

**Montage du boîtier électronique** (voir le [README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md), § 6 ;
l'implantation `Electronique/Implantation_Boitier.fzz` est celle du modèle NEMA, avec ses TMC2209, et n'est
pas redessinée pour les 28BYJ-48 : les cartes ULN2003, de 31 × 35 mm, ne tiennent pas sur la plaque) :

| Article | Caractéristiques | Qté | À chercher | Rôle | ≈ Prix |
|---|---|---|---|---|---|
| **Plaque d'essais ECS1/2** (Gotronic, code 12041) | Époxy FR4, 80 × 100 mm, **pastilles carrées séparées** au pas de 2,54 mm, non étamée. L'implantation en utilise 24 × 30 : la couper à **28 × 34 trous** (≈ 71 × 87 mm, deux trous de marge tout autour), à la scie à métaux, puis, dans chaque coin, percer à Ø 3,2 mm le trou de la 2e rangée et de la 2e colonne (celui du bord est trop près de la découpe) pour les entretoises M3. Trous de 1 mm : bons pour toutes les pattes, sauf peut-être celles des borniers KF301, plus grosses ; s'ils forcent, agrandir leurs 10 trous à Ø 1,2 mm. Frotter le cuivre (gomme abrasive) juste avant de souder. Moins cher pour en avoir deux : l'ECS1 de 100 × 160 mm (code 12046, 7,20 €), coupée en deux. À défaut, une plaque 7 × 9 cm double face générique, si elle a bien 24 × 30 trous (certaines n'en ont que 23 × 31) | 1 | Gotronic 12041 | Reçoit toute l'électronique du boîtier | 5,90 € |
| **Barrettes femelles** au pas de 2,54 mm | Barrettes de 40 broches, à couper : 2 × 18 (Heltec), 1 × 10 (ADS1115), et pour le MCP23017 | 2 barrettes de 40 | `female header 2.54mm 40 pin` | Modules démontables | 2 € |
| **Barrette mâle** au pas de 2,54 mm, double rangée | À couper : 2 × 4 broches | 1 | `male header 2x40 2.54mm` | J1 : bus I²C des deux wattmètres (3V3, GND, SDA, SCL pour chacun) | 1 € |
| **Borniers à vis KF301**, pas de 5,08 mm, emboîtables | 3 de 2 pôles, 2 de 3 pôles (on les emboîte : 5 pôles = 2 + 3) | 5 | `KF301 2P 5.08mm`, `KF301 3P 5.08mm` | X1 (12 V : 2 pôles), X2 et X3 (moteurs : 5 pôles chacun) | 2 € |
| **Borniers à vis au pas de 2,54 mm** (DG308 ou équivalent) | Fils AWG 26 à 18, 6 A ; un de 2 pôles, un de 3, un de 5. Deux fois moins larges que les KF301 | 1 + 1 + 1 | `DG308 2.54mm screw terminal 2P`, `3P`, `5P` | X4 (fin de course), X5 (Hall), X6 (capteur solaire) | 2 € |
| **Boîtier étanche IP65 à porte sur charnières** | ABS ou polycarbonate, au moins 226 × 120 mm à l'intérieur (vu de face) et **80 mm de profondeur** intérieure (batterie couchée de 70 mm) : un boîtier d'environ 250 × 150 × 100 mm, ou plus grand. La porte reçoit le régulateur (110 × 80 mm). Vérifier les cotes **intérieures** : les vis et les charnières prennent de la place dans les coins. **Porte opaque, boîtier de couleur claire** (il chauffe moins au soleil) | 1 | `IP65 ABS enclosure hinged door 100mm deep` | Reçoit tout ce qui ne tourne pas avec la tête : plaque, wattmètres, batterie, fusibles ; le régulateur est vissé sous la porte | 20–30 € |
| Vis inox de la taille des trous du régulateur (M3 ou M4), avec **rondelle d'étanchéité** EPDM (ou joint torique) et écrou frein | Longueur : épaisseur de la porte + patte du régulateur + écrou. À défaut, adhésif double face pour l'extérieur (type VHB) | 4 | `M4 stainless screw sealing washer EPDM` | Fixent le régulateur sous la porte sans laisser entrer l'eau | 3 € |
| Gaine spirale Ø 10 mm, colliers et embases adhésives | 30 cm de gaine | 1 + 6 | `spiral wrap 10mm`, `adhesive cable tie mount` | Boucle des 6 fils du régulateur à la charnière, attachée de chaque côté | 3 € |
| **Presse-étoupes PG7** étanches (IP68) | Pour câbles de Ø3 à 6,5 mm | 6 + 1 de rechange | `PG7 cable gland IP68` | Câbles de la tête : moteurs M1 et M2, fin de course, Hall, capteur solaire, panneau | 4 € |
| **Entretoises M3** de 6 mm et vis M3 × 6 | Nylon ou laiton | 6 + 12 | `M3 standoff 6mm` | Fixent la plaque (4) et le SEN0291 (2) au fond du boîtier | 2 € |
| **Aérateur à membrane** M12, IP67 | Laisse passer l'air, pas l'eau | 1 | `M12 vent plug IP67 breathable` | Évite la condensation dans le boîtier fermé ; laisse sortir les gaz de la batterie | 2 € |
| Sangle de batterie ou deux équerres, et sachet de gel de silice | Sangle à boucle de 25 mm, ou équerres vissées au fond | 1 + 1 | `battery hold down strap`, `silica gel pack` | Tient la batterie (1,9 kg) ; absorbe l'humidité | 4 € |
| **Entretoises M2,5** de 6 mm et vis M2,5 × 6 | Nylon ou laiton | 4 + 8 | `M2.5 standoff 6mm` | Fixent l'INA219B d'Adafruit (trous de 2,5 mm) | 2 € |
| Câble IPEX (U.FL) vers **traversée SMA femelle étanche** (avec joint), et antenne 868 MHz articulée à connecteur SMA | Environ 10 cm | 1 + 1 | `IPEX to SMA female bulkhead waterproof`, `868MHz SMA antenna` | Sort l'antenne du boîtier fermé (elle porte plus loin) | 6 € |

Le câblage complet est sur le **schéma électrique**
([`Electronique/Schema_Electrique.pdf`](Electronique/Schema_Electrique.pdf), projet QElectroTech
`Electronique/Schema_Electrique.qet`) montre la version à NEMA et TMC2209 : à lire en remplaçant
les deux drivers par le MCP23017 et les cartes ULN2003. Le brochage du Heltec V4, les 28BYJ-48 avec le MCP23017 et les
bibliothèques sont décrits dans le [README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md), § 6. Le branchement du
capteur solaire est au § 7.

## 3. Visserie

Toute la visserie est **métrique à pas standard** (M3 × 0,5 et M2,5 × 0,45), sauf l'écrou du
trépied (1/4"-20 UNC). Prendre de l'**inox A2-70** (il ne rouille pas dehors), sinon de
l'acier zingué classe 8.8.

La longueur d'une vis CHC se mesure sous la tête ; celle d'une vis fraisée, hors tout. Chaque
longueur a été vérifiée dans la CAO par `scripts/generate_fourche.py` : la vis traverse
les pièces et mord dans la dernière sur la longueur indiquée (« prise »), sans toucher le fond
de son trou ni dépasser là où quelque chose tourne. Dans le PETG, **les vis se vissent dans des
inserts filetés en laiton, posés à chaud** (§ 3 bis) : 33 inserts, aucun filet n'est taillé
dans le plastique (sauf les 2 vis sans tête M3×4 des moyeux de vis sans fin, voir plus bas).
Longueurs choisies pour le plateau d'aluminium de 5 mm, l'étagère de 7 mm du bras et les parois de 1,5 mm du cadre.

**Vis**

| Vis (norme) | Qté | Où | Traverse | Se visse dans | Prise | Clé |
|---|---|---|---|---|---|---|
| **CHC M3 × 8** (ISO 4762 / DIN 912) | 2 | Bague d'arrêt sous le moyeu, par-dessous | Bague (3 mm) | Insert M3 × 5,7 du moyeu | 5,2 mm | 2,5 mm |
| **CHC M3 × 8** | 3 | Plateau d'aluminium sur le moyeu, par-dessus | Plateau (5 mm) | Insert M3 × 3 du moyeu | 3 mm (insert complet) | 2,5 mm |
| **CHC M3 × 8** + rondelle | 4 | Palier et support moteur d'azimut, par-dessus le plateau, dans les **lumières** | Rondelle (0,5 mm) + plateau (5 mm) | Insert M3 × 3 du palier / du support | 2,6 mm (insert complet) | 2,5 mm |
| **CHC M3 × 8** | 8 | Bras de la fourche sur le plateau, par-dessous (4 par bras) | Plateau (5 mm) | Insert M3 × 3 de la semelle du bras | 3 mm (insert complet) | 2,5 mm |
| **CHC M3 × 8** | 4 | Les deux 28BYJ-48 sur leur support, par les oreilles (2 par moteur) | Oreille (0,8 mm) + support (4 mm) | **Écrou M3** derrière l'oreille | Écrou complet | 2,5 mm |
| **CHC M3 × 10** | 3 | Fond sous le socle, par-dessous, têtes noyées | Fond (3,9 mm sous le lamage) | Insert M3 × 5,7 du socle | 5,6 mm | 2,5 mm |
| **CHC M3 × 10** | 4 | Palier et support moteur d'élévation, par-dessous l'étagère du bras droit | Étagère (7 mm) | Insert M3 × 3 du palier / du support | 3 mm (insert complet) | 2,5 mm |
| **CHC M3 × 10** | 2 | Équerre du capteur solaire contre le **long côté −Y** du cadre | Équerre (4 mm) + paroi du cadre (1,5 mm) | Écrou M3 posé dans le cadre | Écrou complet, dépasse de 2 mm | 2,5 mm |
| **CHC M3 × 10** | 2 | Boîtier du capteur sur son équerre, par-dessous | Équerre (4 mm) | Insert M3 × 5,7 du boîtier du capteur | 5,6 mm | 2,5 mm |
| **CHC M3 × 12** | 8 | Ferrures sur les petits côtés du cadre, depuis l'extérieur, têtes noyées dans la ferrure (4 par ferrure) | Ferrure + paroi du cadre (1,5 mm) | Écrou M3 posé dans le cadre | Écrou complet, dépasse de 2 mm | 2,5 mm |
| **Tête fraisée M3 × 6** (ISO 10642 / DIN 7991) | 3 | Roue d'azimut sur le socle : elles doivent affleurer | Roue (fraisure) | Insert M3 × 3 du socle | 3 mm (insert complet) | 2 mm |
| **Sans tête M3 × 4, bout plat** (ISO 4026 / DIN 913) | 2 | Une par vis sans fin, dans le trou radial du moyeu, serrée sur le méplat de l'arbre Ø5 | — | Moyeu de la vis sans fin (PETG, avant-trou Ø2,8) | — | 1,5 mm |
| **Sans tête M3 × 6, bout plat** | 4 | Blocage sur la tige Ø8 (limée d'un méplat de 0,5 mm) de la roue d'élévation, du collier et des deux ferrures | — | Insert M3 × 3 du moyeu / du collier | 3 mm | 1,5 mm |

Les vis de serrage des accouplements flexibles sont fournies avec eux. Il n'y a **plus de vis M2,5** : les 28BYJ-48 se fixent par leurs oreilles, avec des vis M3 et des écrous.

**Écrous et rondelles**

| Article (norme) | Dimensions | Qté | Où |
|---|---|---|---|
| **Écrou hexagonal M3** (ISO 4032 / DIN 934) | 5,5 mm sur plats, 2,4 mm d'épaisseur | 14 | 8 dans le cadre du panneau, un par vis de ferrure ; 4 derrière les oreilles des deux moteurs ; 2 contre le long côté −Y, pour l'équerre du capteur |
| **Écrou hexagonal 1/4"-20 UNC** (filetage des trépieds) | 7/16" = 11,1 mm sur plats, 7/32" = 5,6 mm d'épaisseur (un contre-écrou de 4 mm convient aussi) | 1 | Pris dans le fond : la tête se visse sur la vis 1/4" du trépied. Ce n'est pas un écrou M6 : le pas est différent |
| **Rondelle plate M3** (ISO 7089 / DIN 125-A) | 3,2 × 7 × 0,5 mm | 4 | Sous la tête des 4 vis d'azimut posées sur les lumières du plateau. Sans elle, la tête Ø5,5 ne porterait que sur 0,4 mm aux deux bouts d'une lumière de 4,7 mm et s'enfoncerait dans le PETG |

**Pas d'autre rondelle** (hors les deux rondelles de calage de l'axe d'élévation, § 1) : ailleurs, les têtes sont noyées dans des lamages (Ø6,2 et Ø6,5, trop
étroits pour une rondelle) ou portent sur un trou rond, et les écrous du cadre portent sur
l'aluminium. Pas de rondelle fendue (Grower) : elle marquerait le PETG.

**Serrage**

* **Dans un insert en laiton** : serrer normalement, environ 0,8 N·m (petit bras de la clé,
  fermement à la main), et on peut démonter autant de fois qu'on veut. Le filet est en laiton,
  pas en PETG : il ne s'arrache pas. Un insert bien posé résiste à plus de 100 N à l'arrachement.
* **Les 2 vis sans tête M3 × 4** des moyeux de vis sans fin (moyeu de seulement 4,35 mm) restent
  **taillées directement dans le PETG** (trou Ø2,8) : un insert n'y tiendrait pas, et la vis ne
  fait que serrer sur le méplat de l'arbre. Visser doucement, en revenant d'un demi-tour à
  chaque tour, et serrer légèrement (0,3 à 0,4 N·m, jusqu'à ce que le bout plat touche le méplat).
* **Dans un écrou** : M3 environ 0,8 N·m (petit bras de la clé, serré fermement à la main).
* **Vis de pression sur les tiges Ø8** (roue d'élévation, collier, ferrures) : limer d'abord sur la
  tige un méplat de 0,5 mm, puis serrer à fond. Une goutte de **frein-filet moyen** (Loctite 243)
  est conseillée sur ces quatre vis : elles transmettent le couple de la roue au panneau.
* **Frein-filet** (Loctite 243, moyen, facultatif) : une goutte sur les 2 vis sans tête, qui
  vibrent avec les vis sans fin. Jamais dans le PETG.

**Clés Allen** : 1,5 mm (vis sans tête), 2 mm (vis fraisées M3), 2,5 mm (vis CHC M3).

**Récapitulatif à acheter** : CHC M3 × 8 : 21 ; M3 × 10 : 11 ; M3 × 12 : 8 ; fraisées M3 × 6 : 3 ;
sans tête M3 × 4 : 2 ; sans tête M3 × 6 : 4 ; inserts à chaud M3 × 5,7 : 7 ; inserts à chaud M3 × 3 : 26 ;
écrous M3 : 14 ; écrou 1/4"-20 UNC : 1 ; rondelles M3 : 4 ; rondelles de calage 8 × 14 × 0,5 : 2. Prendre
quelques vis de rechange de chaque taille.

Le plus simple est d'acheter des coffrets en inox A2 :
* **vis CHC M3** (`M3 socket head screw assortment A2`), avec au moins 20 vis de 8 mm ;
* **vis fraisées M3 × 6** (`M3x6 countersunk screw ISO 10642`) ;
* **inserts filetés laiton à chaud**, deux tailles (§ 3 bis) ;
* **vis sans tête M3** (`M3x4 set screw flat point`, `M3x6 set screw flat point`) ;
* **écrous M3** (`M3 hex nut DIN 934`) et **rondelles M3** (`M3 washer DIN 125`) ;
* un **écrou 1/4"-20 UNC** (`1/4-20 UNC hex nut`).

Compter 10 à 15 € en tout.

## 3 bis. Inserts filetés à chaud (laiton)

Les vis M3 ne se vissent **pas** dans le plastique : elles se vissent dans des **inserts en
laiton moleté**, enfoncés à chaud dans des trous imprimés (le plastique fond autour du moletage
puis se fige). Le filet est en laiton : on peut démonter autant de fois qu'on veut.

| Insert | Qté | À chercher | Trou imprimé | Où |
|---|---|---|---|---|
| **M3 × 5,7 mm** (Ø extérieur ≈ 4,6 mm, moleté) | 7 | `M3 heat set insert 5.7mm` (ou `M3x5.7x4.6`) | **Ø4,0 × 6,5 mm** de profondeur | 3 dans les piliers du socle (fond), 2 dans le moyeu (bague d'arrêt), 2 dans le boîtier du capteur solaire |
| **M3 × 3 mm** (même diamètre extérieur) | 26 | `M3 heat set insert 3mm` (ou `M3x3x4.6`) | **Ø4,0 × 3,8 mm** de profondeur | 3 dans la roue d'azimut (socle), 3 dans le moyeu (plateau), 4 dans le palier et le support d'azimut, 4 dans le palier et le support d'élévation, **8 dans les semelles des bras**, 4 pour les **vis de pression** (roue d'élévation, collier, deux ferrures) |

**Dans la CAO**, les inserts sont modélisés (cylindres creux, Ø4,0 / Ø2,5) dans leurs trous :
c'est ce qui permet de contrôler la prise de chaque vis. **Autour de chaque trou** il y a au
moins **1,6 mm** de matière (4 périmètres) et **au moins 1,6 mm sous le fond** du trou, pour que
le plastique refoulé par le moletage ne perce pas la pièce.

**Pose** (pièces imprimées en PETG, trou d'insert tourné vers le haut si possible) :
1. Fer à souder réglé vers **220 à 250 °C**, avec une **pointe d'insert** (`heat set insert tip
   M3`, 5–8 €, souvent fournie en coffret avec les inserts) : la pointe a le même filet que
   l'insert et se retire sans l'entraîner. Température à valider sur l'éprouvette
   d'ajustements avant de poser les 33 inserts : trop froid, l'insert se coince ; trop chaud, le
   plastique coule et marque la surface.
2. Poser l'insert sur la pointe, l'engager droit dans le trou, et **laisser le fer descendre
   sous son propre poids** jusqu'à ce que l'insert affleure la surface (quelques secondes).
3. **Retirer le fer** en gardant l'insert droit, et poser tout de suite à plat une surface propre
   (une règle, une vis M3 vissée et dévissée) pour le dresser avant que le plastique ne fige.
4. Attendre le refroidissement complet (1 min) avant de visser.

**Exception** : les 2 vis sans tête M3 × 4 des moyeux de vis sans fin restent **dans le PETG**
(moyeu de 4,35 mm de long, trop court pour un insert, effort faible : elles ne font que serrer
sur le méplat de l'arbre).

**Outillage en plus** : une pointe d'insert M3 (voir ci-dessus). Le fer à souder réglable (en température) sert aussi à l'électronique.

## 4. Pièces métalliques non imprimées

| Article | Caractéristiques | Qté | À chercher | Remarque |
|---|---|---|---|---|
| **Plateau d'aluminium 5 mm** | Plaque de 506 × 138 mm (forme en T, voir `pieces_metal/Plateau_Alu.dxf`), aluminium 5 mm (5083, 5754 ou 6082), découpée **au laser ou au jet d'eau**, ou à la scie à métaux dans une tôle de 5 mm puis percée d'après le DXF. Trous Ø3,5 (vis des bras, du moyeu) et lumières de l'azimut ; passage Ø15 du moyeu | 1 | `découpe laser aluminium 5 mm sur plan DXF` | Il porte les deux bras et le moyeu. **Ébavurer** les bords |
| **Cadre du panneau** (celui du panneau acheté) | — | — | — | **Percer 8 trous Ø3,4 dans les deux petits côtés** (4 de chaque côté : à 15 mm de part et d'autre du milieu, à 7 mm sous et 3 mm au-dessus du plan médian du cadre), pour les ferrures ; **percer 2 trous Ø3,4 dans le long côté −Y**, pour l'équerre du capteur solaire. Les parois ne font que 1,5 mm : poser les écrous **dans** le cadre |

## 5. Consommables

| Article | Qté | À chercher | ≈ Prix |
|---|---|---|---|
| **Filament PETG 1,75 mm** (teinte claire de préférence) | 1 bobine de 1 kg (environ 400 à 450 g utilisés) | `PETG filament 1.75mm 1kg` | 20 € |
| **PETG noir** pour le boîtier du capteur solaire, qui doit être opaque | Environ 20 g : un reste de bobine suffit. À défaut, imprimer en clair et peindre en noir mat, intérieur des logements compris | `black PETG filament` | — |
| Colle chaude ou colle époxy (bloque les photodiodes dans leurs logements) | 1 | `hot glue` | 3 € |
| **Graisse PTFE** (vis sans fin et roues : obligatoire en PETG ; pas les roulements, graissés d'origine) | 1 tube | `PTFE grease` | 8 € |
| **Colle** cyanoacrylate, ou colle à roulements Loctite 641 : **les tiges Ø8 dans les moyeux des ferrures** (obligatoire) ; vis sans fin sur leur arbre (optionnel) | 1 | `super glue`, `Loctite 641` | 3–12 € |
| Frein-filet moyen (Loctite 243), facultatif | Sur les 4 vis de pression des tiges | 1 | `Loctite 243` | 8 € |
| **Pointe d'insert M3** pour fer à souder (pose des inserts à chaud, § 3 bis) | 1 | `heat set insert tip M3` | 5–8 € |
| Colle à roulements, type Loctite 641 (seulement si les arbres font moins de 4,98 mm) | 1 | `Loctite 641` | 8–12 € |

## 6. Optionnel

| Article | Qté | Pour quoi |
|---|---|---|
| Sacs de sable de 4 kg (environ 26 × 10 × 10 cm : sac solide rempli de 2,5 L de sable sec) | 2 | Lest contre le vent, de chaque côté du boîtier posé à plat sous le trépied (README du cas terrestre, § 8) |
| Sangle à boucle de 25 mm, 1,5 m | 1 | Fait le tour du boîtier et des deux sacs, puis du moyeu de la colonne du trépied ; tendue à la main |

---

Le panneau est un **Velleman SOL10P** (Gotronic, réf. 27128, 36,50 €) : 10 W, 17,6 V et
0,61 A au point de puissance maximale, 21,8 V à vide, 356 × 253 × 30 mm, 1,16 kg. C'est celui
de la CAO. Sa sortie est sur cosses à souder : souder le câble souple 2 × AWG 20.

**Ordre de grandeur total** : environ **90 à 140 €** avec une alimentation secteur, capteur solaire
compris (environ 8 €), sans compter le trépied, le panneau, ni les deux wattmètres (déjà en
stock). **Estimation, non vérifiée par des devis** : les deux 28BYJ-48 avec leurs cartes coûtent
beaucoup moins que les NEMA (environ 8 € contre 25 à 40 €) et il n'y a plus de TMC2209, mais le plateau
d'aluminium découpé s'y ajoute (15 à 30 €). Pour la démonstration en extérieur, il faut ajouter
36 € pour le régulateur SOL10UC3 (la batterie est fournie).
