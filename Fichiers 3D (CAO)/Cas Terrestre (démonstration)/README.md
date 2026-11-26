# 🌍 Cas terrestre (démonstration en PETG, tête à fourche, moteurs 28BYJ-48)

[⬅ Retour au README principal](../../README.md) · [Cas lunaire ➜](../Cas%20Lunaire/README.md)

Une tête à **fourche étroite** imprimée en PETG, avec le panneau et le capteur solaire, vissée sur un
trépied (§ 8) :

| Vue d'ensemble, panneau à 40° | Côté moteurs |
|---|---|
| ![Sur un trépied](../../docs%20%28extra%29/trepied_fourche_iso.png) | ![Côté moteurs](../../docs%20%28extra%29/trepied_fourche_arriere.png) |
| ![De profil](../../docs%20%28extra%29/trepied_fourche_profil.png) | ![La tête sur la rotule du trépied](../../docs%20%28extra%29/trepied_fourche_detail.png) |

C'est **le modèle qu'on construit** : ce document donne tout ce qu'il faut pour le fabriquer,
de l'impression au boîtier électronique. Le panneau, le capteur solaire et le principe de la
commande, communs aux deux cas, sont décrits dans le [README principal](../../README.md).

> **Cahier des charges L3 : la structure tient dans 350 × 350 × 350 mm** (le panneau, lui, peut
> déborder). La CAO mesure **344 × 139 × 343 mm** hors panneau. Pour y arriver, le panneau est monté
> **dans le sens de sa largeur** : l'axe d'élévation suit son petit côté de 253 mm (et non les 356 mm),
> si bien que les deux bras de la fourche ne sont écartés que de 290 mm (§ 1).
>
> **Moteurs imposés : deux 28BYJ-48.** Ce sont de petits moteurs (version **12 V**), 15 à 20 fois moins
> forts que les NEMA du cas lunaire. Ils ne peuvent pas faire basculer un panneau dont le
> centre de gravité est loin de l'axe : **la tête a donc été redessinée à zéro, en fourche, pour
> que le panneau soit équilibré par sa géométrie**, sans contrepoids (§ 1). L'ancien modèle
> terrestre (NEMA 17 et NEMA 11, tête à chape) est conservé dans le
> [modèle idéal personnel](../../.modele_ideal_personnel/README.md), document caché ; la variante
> 28BYJ-48 à contrepoids, abandonnée au profit de la fourche, dans la
> [Variante 28BYJ-48](../../.variante_28BYJ-48/README.md).

**Sommaire**

1. [Pourquoi une fourche, et ce qui change](#1-pourquoi-une-fourche-et-ce-qui-change)
2. [Pièces à imprimer (`a_imprimer/`, déjà orientées sur le plateau)](#2-pièces-à-imprimer-a_imprimer-déjà-orientées-sur-le-plateau)
3. [Pièces à acheter](#3-pièces-à-acheter)
4. [Jeux d'ajustement, éprouvette, inserts et parois](#4-jeux-dajustement-éprouvette-inserts-et-parois)
5. [Ordre de montage](#5-ordre-de-montage)
6. [Commande : Heltec WiFi LoRa 32 V4 et 28BYJ-48](#6-commande--heltec-wifi-lora-32-v4-et-28byj-48)
7. [Capteur solaire de la démonstration](#7-capteur-solaire-de-la-démonstration)
8. [Sur un trépied](#8-sur-un-trépied)
9. [Couples, marges et tenue de la version PETG](#9-couples-marges-et-tenue-de-la-version-petg)
10. [Fichiers de ce dossier et du boîtier électronique](#10-fichiers-de-ce-dossier-et-du-boîtier-électronique)
11. [Questions pièges et leurs réponses](#11-questions-pièges-et-leurs-réponses)

## 1. Pourquoi une fourche, et ce qui change

### Le problème du 28BYJ-48

Le 28BYJ-48 (12 V, réducteur intégré 63,68:1) donne **34,3 mN·m** à son arbre, soit **25 mN·m en
valeur prudente** (dispersion d'un moteur à l'autre, usure du réducteur, alimentation à 10,8 V, soit 12 V − 10 %),
contre 0,34 N·m pour le NEMA 17 de l'ancien modèle. Dans la tête à chape, l'axe d'élévation est
**sous le cadre, à 46 mm de son dos** : la partie qui bascule (1,51 kg) a son centre de gravité
à **62 mm de l'axe**, et le panneau pèse en permanence sur la denture : **0,93 N·m rien que pour
le tenir**. Avec la vis sans fin 50:1 de cette tête, un 28BYJ-48 donne 0,36 N·m à la roue :
marge de ×0,4, **il ne tient pas, même sans vent**. Trois leviers étaient possibles : réduire le
couple de pesanteur, augmenter la démultiplication, améliorer le rendement. La fourche agit sur
les deux premiers.

### Le principe

Dans une **fourche**, le panneau tourne **autour de son propre plan médian**, sur deux
**tiges d'acier Ø8** fixées à ses grands côtés (356 mm) par deux ferrures imprimées : **l'axe
d'élévation est donc parallèle au côté de 253 mm**. Les tiges tournent dans **un roulement 608
par bras** (montage symétrique). Le centre de gravité de la partie qui bascule tombe à **9 mm de
l'axe** (au lieu de 62) : le couple de pesanteur résiduel n'est plus que de **0,13 N·m**. Aucun contrepoids n'est nécessaire. Le couple disponible vient
d'une roue plus grande : **100 dents en élévation et 120 en azimut** (au lieu de 50 et 60), en
gardant le module 0,8 des vis sans fin, imprimées en PETG.

| Axe | Roue | Couple prudent à la roue | 90° en | Résolution |
|---|---|---|---|---|
| Élévation | 100 dents, Ø80 mm | 0,76 N·m | 14 min | 0,0009° par demi-pas |
| Azimut | 120 dents, Ø96 mm | 0,91 N·m | 17 min | 0,0007° par demi-pas |

C'est long pour une mise en position (le moteur tourne à 120 demi-pas par seconde, soit
1,8 tr/min), sans importance pour le suivi, qui ne fait que des corrections de 0,5° (§ 7).

### Tenir dans 350 × 350 × 350 mm

Le cahier des charges impose 350 mm au plus pour la structure, panneau excepté. Une fourche dont
les bras encadrent le côté de 356 mm du panneau y dépasserait forcément (519 mm dans une version
précédente de cette tête). En tournant le panneau de 90°, les bras n'encadrent plus que 253 mm :

| Dimension de la structure (hors panneau) | Valeur mesurée sur la CAO | Limite |
|---|---|---|
| Largeur (axe d'élévation) | **344 mm** : x de −157 à +187 (bras gauche, plateau, bras droit, étagère du moteur d'élévation) | 350 |
| Profondeur | **139 mm** | 350 |
| Hauteur | **343 mm** : de −2 à 341 mm (le haut est la roue d'élévation, Ø82) | 350 |

Conséquences de ce choix :
* le panneau, de 356 mm, **pend de 178 mm sous l'axe** quand il est presque vertical : l'axe est
  donc relevé à **300 mm** au-dessus de la base (240 mm avant), pour que le panneau passe
  au-dessus du plateau. Garde mesurée sur la CAO : **au moins 13,7 mm** entre le panneau (cadre,
  laminé, capteur) et la structure, de 5° à 92° d'élévation (le cahier des charges demande 15° à 90°) ;
* l'axe d'élévation est à **902 mm du sol** sur le trépied (758 mm pour l'ancienne tête à chape) ;
* **les marges de la structure sont courtes** : 7 mm sur la hauteur, 6 mm sur la largeur. Une
  tolérance d'impression de 1 mm sur les bras ne les consomme pas, mais l'ajout d'un butoir ou d'un
  support d'aimant ailleurs que dans ces limites demande de revérifier.

![Tête à fourche, panneau à 40°](../../docs%20%28extra%29/fourche_iso.png)

### Ce qui change, pièce par pièce

| Élément | Cas lunaire | Démonstration sur Terre (ce document) |
|---|---|---|
| Support du panneau | Chape et chapeau en U, panneau sur deux rails, Al 6061-T6 | **Fourche étroite** : un **plateau d'aluminium de 5 mm** (découpe laser, `pieces_metal/`) qui porte deux **bras imprimés** de 9 mm |
| Pivots d'élévation | Inox 17-4PH Ø8 (dont un en D), sur 608 | **Deux tiges d'acier rectifié Ø8** (25 et 46 mm), sur **un 608 par bras**, fixées au panneau par des **ferrures imprimées** (vis de pression, colle facultative) |
| Axe d'élévation | Sous le cadre | **Dans le plan médian du panneau**, parallèle à son côté de 253 mm, à 902 mm du sol sur le trépied (contre 758 mm pour la tête à chape) |
| Roues des vis sans fin | Bronze CuSn12, 50 et 60 dents | **PETG imprimé, 100 et 120 dents**, module 0,8 |
| Vis sans fin | Inox 17-4PH | **PETG imprimé** |
| Moteurs | NEMA 17 et NEMA 11 (version vide) | **2 × 28BYJ-48 12 V**, avec cartes **ULN2003** |
| Accouplements | Al 7075-T73, Ø19 × 25 | Accouplement flexible alu **Ø5 / Ø5, Ø14 × 19 mm** (arbre court du 28BYJ-48) |
| Drivers | TMC2209 | **Cartes ULN2003 + MCP23017** (extension de broches sur l'I²C), § 6 |
| Socle, fond, moyeu, bague d'arrêt, paliers, supports | Al 6061-T6 anodisé | **PETG imprimé** |
| Panneau | Velleman SOL10P | Velleman SOL10P : **cadre percé de 8 trous** (ferrures) dans les grands côtés |
| Capteur solaire | Boîtier à croix et équerre, Al, photodiodes qualifiées | Boîtier et équerre **imprimés** (PETG noir), photodiodes BPW34 ; sur le **petit côté haut** du cadre |
| Roulements | 6806, 608, 685 **ZZ** en acier 440C | 6806, **608**, 685 **ZZ** en acier standard |
| Lubrification | MoS₂ sec | **Graisse PTFE**, obligatoire |
| Visserie | Inox ou titane | Vis CHC M3 en inox A2, **inserts à chaud** en laiton |

L'architecture à deux axes, les rapports de la commande, le panneau et le principe du capteur
solaire sont ceux du [README principal](../../README.md). Le cas lunaire, lui, **n'est pas
modifié**.

### Ce qui a été vérifié sur la CAO

L'assemblage complet (roulements, tiges, arbres, moteurs, inserts et toute la visserie) est
contrôlé par `scripts/generate_fourche.py` :
* **aucune interférence** entre pièces, vis, écrous et inserts, à 40° d'élévation, et de 10° à
  92° à deux azimuts ; la même chose sur le trépied ;
* **garde du panneau** sur toute la course (5° à 92°) : au moins 13,7 mm entre le panneau et la
  structure ; seule la tige frôle son alésage de 0,5 mm dans le bras (c'est un jeu de 0,5 mm
  autour de la tige, qui tourne dans le roulement) ;
* **enveloppe de la structure** : 344 × 139 × 343 mm, dans les 350 mm du cahier des charges ;
* **prise des vis** : au moins 2,6 mm dans un insert court de 3 mm (c'est-à-dire l'insert
  complet), 5,2 mm dans un insert long, les écrous en prise sur toute leur hauteur ;
* les vis sans fin et les roues **engrènent sans chevauchement** (calage calculé) ;
* partie qui bascule : **1,32 kg, centre de gravité à 9,4 mm de l'axe** ; tête complète
  (partie fixe, panneau et capteur) : **2,67 kg**.

## 2. Pièces à imprimer (`a_imprimer/`, déjà orientées sur le plateau)

Les 18 pièces sont orientées pour l'impression et posées sur le plateau virtuel (z = 0).

![Pièces à imprimer](../../docs%20%28extra%29/fourche_pieces_a_imprimer.png)

| Pièce | Qté | Orientation (déjà appliquée) | Remarque |
|---|---|---|---|
| `Bras_Droit` | 1 | **Sur sa face intérieure**, étagère vers le haut | Plaque de 9 mm, 225 mm de haut, un 608. Porte la roue d'élévation à l'extérieur et l'**étagère** de l'entraînement d'élévation (plaque de 7 mm avec deux nervures, debout à l'impression) ; semelle de fixation vers l'extérieur |
| `Bras_Gauche` | 1 | **Sur sa face extérieure** (la semelle de fixation est vers l'intérieur, elle ressort vers le haut) | Plaque de 9 mm, 225 mm de haut, un 608 : le même montage que le bras droit |
| `Ferrure_Droite`, `Ferrure_Gauche` | 1 + 1 | Sur la face intérieure, moyeu Ø20 vers le haut | Se vissent sur les **grands côtés** du cadre (4 × M3 chacune) ; la tige Ø8 est bloquée par une vis de pression (colle facultative) |
| `Roue_Elevation` | 1 | À plat, moyeu en haut | **100 dents**, module 0,8, Ø82 ; moyeu Ø20 ; 6 allègements. 100 % de remplissage |
| `Roue_Azimut_Fixe` | 1 | Dessous plat sur le plateau | **120 dents**, Ø98 ; buse 0,25 mm conseillée (denture) |
| `Vis_Elevation`, `Vis_Azimut` | 1 + 1 | Debout, axe vertical | 100 % de remplissage ; bordure (brim) conseillée |
| `Palier_Vis_Elevation`, `Palier_Vis_Azimut` | 1 + 1 | Semelle sur le plateau | Lèvre de 1,6 mm côté extérieur de chaque joue : le 685 s'enfonce depuis l'intérieur du U ; les joues sont taillées pour passer sous la grande roue |
| `Support_Moteur_Elevation`, `Support_Moteur_Azimut` | 1 + 1 | Semelle sur le plateau | Plaque de 4 mm pour un 28BYJ-48 (2 oreilles à 35 mm), lamage Ø17 pour l'accouplement |
| `Socle` | 1 | Debout, ouverture en bas | Cône à 45° sous le logement du 6806 bas : pas de support |
| `Fond_Socle` | 1 | Dessus sur le plateau | Se visse sur la vis 1/4" du trépied : écrou 1/4" pris dans un logement hexagonal |
| `Moyeu_Chape` | 1 | Collerette sur le plateau | Le moyeu qui porte le plateau d'aluminium ; 3 inserts M3×3 (plateau) et 2 inserts M3×5,7 (bague d'arrêt) |
| `Bague_Arret_Moyeu` | 1 | À plat | |
| `Capteur_Solaire_Boitier` | 1 | Croix en haut | **PETG noir**, 100 % de remplissage : il doit être opaque (§ 7) |
| `Capteur_Solaire_Support` | 1 | Plaque sur le plateau, âme vers le haut | Équerre du capteur, vissée sur le **petit côté haut** du cadre |

**Pourquoi les bras et les ferrures sont couchés sur leur face intérieure.** Les efforts
(panneau, vent, poussée des vis sans fin) agissent dans le plan du bras. Imprimé à plat, ce
plan est **parallèle aux couches** : le bras est très raide dans ce plan (flexion en tête
estimée à moins de 0,01 mm à 10 m/s de vent, hors plan : environ 0,03 mm), et aucune charge
ne tire une couche loin de la suivante. Les trous des roulements et des tiges sont alors
**verticaux** à l'impression, donc ronds. Seuls les 4 trous d'insert de la semelle de chaque
bras sont horizontaux (Ø4 × 3,8 mm) : **les essayer sur l'éprouvette** (§ 4).

**Attention : les deux bras font 225 mm de haut**, au-dessus du plafond de 200 mm du cahier des
charges pour une pièce FDM. Ils sont à **découper en deux** (par exemple un pied et une tête
assemblés par un recouvrement et des vis M3) : ce découpage n'est **pas encore dessiné**.

Une des pièces est **en aluminium, découpée au laser ou au jet d'eau** (ou à la scie à métaux
dans une tôle de 5 mm) : `pieces_metal/Plateau_Alu.dxf` (et `.step`), plaque de 328 × 138 mm
et de 5 mm, avec ses trous. Le cadre du panneau est percé de 8 + 2 trous Ø3,4 (§ 3).

Environ 750 g de PETG si tout était plein, 400 à 450 g avec 4 périmètres et 40 % de
remplissage, plus 26 g pour le capteur solaire.

**Réglages conseillés** :
* PETG, couches de 0,2 mm ;
* 4 périmètres, 40 % de remplissage gyroïde ;
* **100 %** pour les deux vis sans fin, les deux roues et les ferrures ;
* compensation de la patte d'éléphant (≈ 0,2 mm) ;
* aucun support : à confirmer dans le trancheur, surtout sous l'étagère du bras droit et ses
  nervures ;
* teinte claire de préférence : un PETG noir en plein soleil d'été peut approcher sa
  température de ramollissement (≈ 80 °C).

**Pour les pièces dentées** (deux roues, deux vis) : filet des vis de 0,95 mm (élévation) et
0,76 mm (azimut) en tête. Ça s'imprime avec une buse de 0,4 mm, mais une **buse de 0,25 mm et
des couches de 0,1 mm** donnent des dents nettement plus justes.

## 3. Pièces à acheter

La liste complète, avec les noms à chercher sur les sites marchands, les quantités, les prix
indicatifs et l'électronique, est dans **[`Liste-composants.md`](../../Liste-composants.md)**.
En résumé, pour la mécanique :

| Article | Qté |
|---|---|
| Roulement **6806ZZ** (ISO 61806-2Z ; ou 6806-2RS), 30 × 42 × 7 mm | 2 |
| Roulement **608ZZ** (ou 608-2RS), 8 × 22 × 7 mm | 3 |
| Roulement **685ZZ** (ou 685-2RS), 5 × 11 × 5 mm — **pas le 685 ouvert, large de 3 mm** | 4 |
| **Tige d'acier rectifiée Ø8**, coupée à **46 mm** (côté roue) et **25 mm** (côté gauche) : 71 mm en tout, prendre 100 mm | 1 |
| Tige acier rectifiée Ø5, coupée à 53 mm (arbres des vis) | 2 |
| Accouplement flexible alu 5 mm / 5 mm, **Ø14 × 19 mm** (`flexible shaft coupling 5mm 5mm D14 L19`) | 2 |
| **Moteur 28BYJ-48, 12 V**, avec sa carte **ULN2003** | 2 |
| **Plateau d'aluminium 5 mm**, découpé d'après `pieces_metal/Plateau_Alu.dxf` | 1 |
| Vis CHC M3 : 21 × M3×8, 11 × M3×10, 8 × M3×12 | 40 |
| Vis à tête fraisée M3×6 (roue d'azimut) | 3 |
| Vis sans tête M3×4 (blocage des vis sans fin) | 2 |
| Vis sans tête M3×6, bout plat (blocage des tiges) | 3 |
| **Insert fileté laiton à chaud** M3 × 5,7 mm (trou imprimé Ø4,0 × 6,5) | 7 |
| **Insert fileté laiton à chaud** M3 × 3 mm (trou imprimé Ø4,0 × 3,8) | 25 |
| Écrou M3 (ferrures, oreilles des moteurs, équerre du capteur) | 14 |
| Rondelle M3 (ISO 7089, 3,2 × 7 × 0,5), sous les vis d'azimut posées sur les lumières | 4 |
| Rondelle de calage 8 × 14 × 0,5 mm (DIN 988) | 2 |
| Écrou 1/4"-20 UNC (filetage des trépieds, 7/16" sur plats) | 1 |
| Graisse PTFE (vis, roues) | 1 |
| Photodiodes BPW34, résistances de 1 kΩ, condensateurs de 100 nF, convertisseur ADS1115 (capteur solaire) | 4 + 4 + 4 + 1 |

Toute la visserie, avec ses quantités et ses prises : § 5, « Visserie en bref », et
[`docs (extra)/visserie/`](../../docs%20%28extra%29/visserie/README.md).

**Le cadre du panneau est à percer** (Velleman SOL10P, cadre en aluminium) :
* **8 trous Ø3,4 dans les deux grands côtés** (356 mm ; 4 de chaque côté : à 15 mm de part et
  d'autre du milieu, et à 7 mm sous et 3 mm au-dessus du plan médian du cadre), pour les
  ferrures. Le gabarit est la ferrure elle-même (4 trous, entraxe 30 × 10 mm) ;
* **2 trous Ø3,4 dans l'un des petits côtés** (253 mm), pour l'équerre du capteur solaire.

Les parois du cadre ne font que 1,5 mm : les écrous M3 sont posés **dans** le cadre, et on
les atteint par le dos ouvert du panneau. Percer le cadre avant d'y poser les ferrures.

### Roulements de la démonstration

Ce sont ceux du cas lunaire ([README du cas lunaire](../Cas%20Lunaire/README.md), § 1), en
acier standard.

| Réf. | Dimensions (Ø int. × Ø ext. × largeur) | Qté | Emplacement |
|---|---|---|---|
| **608** | 8 × 22 × 7 mm | 2 | Élévation : un dans chaque bras (montage symétrique), enfoncé depuis l'intérieur ; les tiges Ø8 tournent dedans |
| **6806** | 30 × 42 × 7 mm | 2 | Azimut : dans le socle, autour du moyeu |
| **685** | 5 × 11 × 5 mm | 4 | Deux par vis sans fin, dans les joues des paliers |

* Prendre de préférence des **ZZ**. Ils sont graissés à vie d'origine : ne pas les ouvrir ni
  les regraisser. **Avec les 28BYJ-48, c'est presque obligatoire** : les joints d'un 2RS
  frottent et prennent une part importante du faible couple (0,008 N·m pour la paire de 685 :
  le quart du couple du moteur ; environ 0,15 N·m pour la paire de 6806 d'azimut).
* **685** : prendre une version **protégée, ZZ ou 2RS**. Le 685 ouvert ne fait que 3 mm de
  large, alors que les paliers sont prévus pour 5 mm.
* **Montage** : enfoncer un roulement en poussant sur la bague qu'on emmanche. Dans un
  logement, c'est la bague extérieure : utiliser une douille de son diamètre, jamais un
  outil posé sur la flasque.

### Moteurs

Le **28BYJ-48 12 V** est livré avec sa carte **ULN2003** dans les kits courants (la carte accepte 5 à 12 V). La fiche technique du moteur reçu est celle du 12 V ; les cotes ci-dessous en viennent.

| Caractéristique | Valeur |
|---|---|
| Alimentation | **12 V**, unipolaire, 5 fils (rouge = commun) |
| Résistance d'une bobine | **200 Ω ±7 %**, soit **60 mA** par bobine allumée (≈ 1,4 W avec deux bobines) |
| Réduction intégrée | 64:1 nominal, **63,68:1** mesuré ; environ 4076 demi-pas par tour de l'arbre de sortie |
| Couple de sortie | **> 34,3 mN·m** à 120 Hz (25 mN·m retenu dans les calculs, par prudence) ; couple d'auto-maintien ≥ 450 gf·cm, frottement 800 à 1800 gf·cm ; fréquence de fonctionnement indiquée : 100 pas/s |
| Arbre de sortie | Ø5 à deux méplats (3 mm entre méplats, longueur 6 mm depuis le bout), **10 mm au-dessus de la face du corps** (bossage de 1,5 mm compris), **décentré de 8 mm** par rapport au corps ; méplats perpendiculaires à la ligne des oreilles |
| Fixation | corps Ø28 mm, deux oreilles à 35 mm d'entraxe, bossage Ø9 × 1,5 mm |
| Masse | environ 30 g |

> **Moteurs en 12 V (confirmé).** La fiche technique est celle du 28BYJ-48 **12 V**. Il est alimenté en **12 V**, par le 12 V du tracker (après le wattmètre A5), directement sur la carte ULN2003 (elle accepte 5 à 12 V). **Un 12 V alimenté en 5 V ne donnerait qu'environ 2,4 fois moins de couple (5/12) : ne jamais le brancher sur le 5 V de U1.** À réception, vérifier l'étiquette « 12V » et les 200 Ω entre le fil rouge et chaque autre fil. Le couple annoncé (34,3 mN·m) est mesuré à 120 Hz ; la fiche indique 100 pas/s en fonctionnement : si un moteur décroche à 120 phases/s, descendre à 100 (le tour de 90° passe alors de 14 à 17 minutes à l'élévation et de 17 à 20 à l'azimut).

Sources : [fiche technique 28BYJ-48](https://cdn.shopify.com/s/files/1/0015/7571/4865/files/datasheet_28BYJ-48.pdf),
[fiche 52Pi](https://wiki.52pi.com/images/3/3a/Stepper-Motor-28BJY-48-Datasheet.pdf). Ces cotes
viennent de fiches techniques courantes : **à vérifier au pied à coulisse sur les moteurs
reçus** (§ 9).

## 4. Jeux d'ajustement, éprouvette, inserts et parois

| Ajustement | Cas lunaire | PETG | Pourquoi |
|---|---|---|---|
| Logements de roulements (608, 685, 6806) | nominal | **+0,15 mm** | Les trous imprimés sortent plus petits ; on obtient un serrage léger du roulement |
| Alésage d'un axe (Ø5 acier des vis ; tige Ø8 dans les ferrures et la roue) | nominal | **+0,10 mm** | Serré. Une vis de pression bloque chaque vis sans fin et chaque tige |
| Alésage de la tige Ø8 dans les bras | | **Ø9** (jeu de 0,5 mm) | La tige tourne dans les 608, pas dans le plastique |
| Moyeu dans les 6806 | Ø30 | **Ø29,95** | Serrage léger de la bague intérieure |
| Fixation sur le trépied | Téton Ø45,5 dans la colonne Ø46 | **Écrou 1/4" captif**, logement de 11,4 mm sur plats (écrou de 11,1) | La vis du trépied tire l'écrou sur un plancher de 1,6 mm et serre le fond sur le moyeu |
| Trous de passage M3 | 3,4 | **3,5** | |
| Trous des **inserts à chaud** M3 | Ø4,0 (insert de 4,6 mm moleté) | **Ø4,0** × 6,5 mm (long) ou × 3,8 mm (court) | Le plastique fond autour du moletage : pas de jeu à ajouter. 1,6 mm de matière autour et sous chaque trou |
| Avant-trous M3 des 2 vis sans tête des vis sans fin | 2,5 (taraudés) | **2,8** | Seules vis auto-taraudées dans le PETG : elles ne font que serrer sur le méplat de l'arbre |
| Jeu de denture des roues | 0,10 / 0,12 mm | **0,30 mm** | Imprécision des dents imprimées |
| Filet des vis | aminci de 0,15 m | **non aminci, tête raccourcie (0,85 m)** | Tout le jeu est pris sur la roue, et le filet reste assez épais pour l'impression |
| Entraxe vis / roue | nominal | **+0,15 mm**, puis réglé au montage | Lumières en azimut, clinquant en élévation |
| **Trous d'axe horizontal à l'impression** : logements des 685 (joues des paliers), passage du bossage du 28BYJ-48 | cylindriques | **en goutte** | Le haut d'un trou horizontal imprimé s'affaisse : il sortirait ovale et trop petit. La goutte ajoute deux pans à 45° vers le haut. Les trous verticaux (608, 6806, tiges, roues, vis) restent ronds |

**Imprimer d'abord l'éprouvette** `Eprouvette_Ajustements.stl`, avec les mêmes réglages que les
pièces :
* trois logements de **608** (le jeu retenu, −0,1 mm et +0,1 mm) et trois logements de 685 ;
* un alésage **Ø8,1** (moyeux), un alésage **Ø9** (bras), un passage M3 et un
  **trou d'insert Ø4,0 × 3,8 mm** (poser un insert M3×3 pour régler la température du fer) ;
* un téton Ø29,95 pour le 6806 (essayer un vrai roulement dessus : il doit entrer en forçant
  légèrement) ;
* sur la paroi debout, comme sur les pièces : un logement de 685 en goutte, le passage du
  bossage du 28BYJ-48 (Ø9,6, en goutte) et un **trou d'insert horizontal**, tel que ceux
  de la semelle des bras.

Ce qu'on doit obtenir :
* les roulements entrent **en forçant légèrement**, à la main ou avec un serre-joint, et ne
  ressortent pas tout seuls ;
* la tige Ø8 passe dans le Ø8,1 en poussant (elle sera collée) et librement dans le Ø9 ;
* l'insert horizontal se pose droit, sans que le trou s'ovalise.

Un roulement qui tombe tout seul : le jeu est trop grand. Un roulement qui ne rentre pas même
au serre-joint : le jeu est trop petit.

Si ton imprimante préfère un autre logement :
1. change la valeur dans `AJUSTEMENTS["petg"]`, en tête de `scripts/generate_tracker.py` ;
2. relance `python scripts/generate_fourche.py`.

Toutes les pièces sont alors régénérées avec ce jeu.

**Retouches possibles au montage**, car une imprimante n'est jamais exacte au dixième près :
* la vis sans fin serre entre ses deux 685 : poncer légèrement l'épaulement Ø6,5 d'un moyeu ;
* un 608 entre trop dur dans un bras : passer un foret Ø22 à la main, sans perceuse ;
* engrènements : réglés au montage (lumières en azimut, clinquant en élévation), voir l'étape 11.

### Inserts à chaud et épaisseurs de paroi

**Les vis M3 ne sont pas vissées dans le plastique** : elles se vissent dans des **inserts filetés
en laiton, posés à chaud** dans des trous imprimés. Le fer à souder fait fondre le PETG autour du
moletage de l'insert, qui se fige ensuite : le filet est en laiton, donc on peut monter et
démonter sans abîmer la pièce. Il y en a **32** :

| Insert | Qté | Trou imprimé | Où |
|---|---|---|---|
| **M3 × 5,7 mm** (long) | 7 | Ø4,0 × 6,5 mm | 3 dans les piliers du socle (fond), 2 dans le moyeu (bague d'arrêt), 2 dans le boîtier du capteur solaire |
| **M3 × 3 mm** (court) | 25 | Ø4,0 × 3,8 mm | 3 dans le socle (roue d'azimut), 3 dans le moyeu (plateau), 4 dans les paliers et supports d'azimut, 4 dans le palier et le support d'élévation, **8 dans les semelles des deux bras**, et **3 vis de pression** : dans chaque ferrure (2) et le moyeu de la roue d'élévation (1) |

Le script modélise chaque insert dans son trou et **mesure la prise de chaque vis dans l'insert** :
M3×10 et M3×8 dans un insert long : 5,6 et 5,2 mm ; M3×8, M3×10 et M3×6 dans un insert court :
au moins 2,6 mm, c'est-à-dire l'insert complet (3 mm). Les longueurs ont été choisies pour la
fourche : plateau de 5 mm (M3×8), étagère de 7 mm (M3×10), cadre de 1,5 mm (M3×12 + écrou).

**Règle de conception** : chaque insert est entouré d'au moins **1,6 mm de plastique** (4
périmètres de 0,4 mm) et a au moins **1,6 mm de matière sous le fond du trou**. Les inserts
des vis de pression sont posés **par la surface du moyeu** (Ø20), vers l'axe : un trou de Ø3,2
le prolonge jusqu'à la tige Ø8, et la vis M3×6 passe à travers l'insert pour serrer la tige.

**Pose** : fer à souder à **220-250 °C** avec une pointe d'insert M3 (température à valider sur
l'éprouvette). Poser l'insert sur la pointe, l'engager droit dans le trou, laisser le fer
descendre jusqu'à ce que l'insert affleure, retirer le fer en gardant l'insert droit, puis le
dresser avec une surface plane avant refroidissement. Poser les 32 inserts **avant**
l'assemblage.

**Exception** : les 2 vis sans tête M3×4 des vis sans fin restent taillées dans le PETG (moyeu
de 4,35 mm, trop court pour un insert ; elles ne font que serrer sur le méplat de l'arbre).

**Épaisseurs de paroi.** Avec une buse de 0,4 mm et 4 périmètres, une paroi pleine fait
1,6 mm. Les pièces reprises du projet (socle, fond, moyeu, bague, roues, vis, paliers) ont été
vérifiées dans le projet précédent. Celles de la fourche l'ont été avec `scripts/verifier_parois.py`
(pas de 0,2 mm, `FOURCHE=1 python scripts/verifier_parois.py 0.2 1.6 Bras_Droit Bras_Gauche
Ferrure_Droite Palier_Vis_Elevation Support_Moteur_Elevation`) :
**aucune zone sous 1,6 mm** dans les deux bras, la ferrure droite (la gauche en est le symétrique),
le palier et le support d'élévation. La roue d'élévation n'est pas contrôlée (ses dents sont minces par nature).

## 5. Ordre de montage

| Le palier d'une vis sans fin | La vis sans fin imprimée |
|---|---|
| ![Palier : joues, roulements, arbre](../../docs%20%28extra%29/explications/palier_joues_roulements.png) | ![Vis sans fin : filet, moyeux](../../docs%20%28extra%29/explications/vis_sans_fin_moyeux.png) |

| Le côté de l'élévation : bras droit, étagère, moteur, roue | La structure, sans panneau |
|---|---|
| ![Détail de l'élévation](../../docs%20%28extra%29/fourche_detail_elevation.png) | ![Structure](../../docs%20%28extra%29/fourche_structure.png) |

* **Le palier** est la pièce en U qui porte une vis sans fin. Ses deux parois sont les
  **joues** : chacune tient un roulement 685, et l'arbre acier Ø5 les traverse. Côté
  extérieur, une **lèvre** de **1,6 mm** retient la bague extérieure du roulement : le 685
  s'enfonce depuis l'intérieur du U jusqu'à cette lèvre, et dépasse de 1 mm côté vis.
* **La vis sans fin imprimée** a, de chaque côté du filet, un **moyeu Ø12**. Les moyeux
  viennent en appui sur les bagues intérieures des 685 par un épaulement Ø6,5, qui ne
  touche pas la flasque. Une vis sans tête M3×4 dans un moyeu bloque la vis sans fin sur l'arbre.
* **L'accouplement flexible Ø14 × 19** relie l'arbre du moteur à l'arbre de la vis. L'arbre
  du 28BYJ-48 est court (10 mm) : il entre de 8,1 mm dans l'accouplement, qui s'engage de 2,1 mm dans
  le lamage Ø17 du support (0,4 mm de jeu avec le bossage). Le bout de l'arbre du moteur reste à
  1,4 mm de celui de la vis. Les axes du moteur, de l'accouplement et de l'arbre de la vis sont
  confondus (écart nul dans la CAO, voir « Montage de l'accouplement » plus bas).
* **Le panneau tourne sur ses deux tiges** : la tige droite (46 mm) passe dans le 608 du bras
  droit et la ferrure, et porte la roue d'élévation à l'extérieur du bras ; la tige gauche (25 mm)
  passe dans le 608 du bras gauche et la ferrure. La roue et chaque ferrure sont bloquées par une
  vis de pression sur un **méplat limé sur la tige** (0,5 mm). Les bagues des 608 tournent
  librement : c'est l'**axe d'élévation**. Il n'y a **plus de collier** : les moyeux des deux
  ferrures, à 0,5 mm de la face intérieure de chaque bras, font butée dans les deux sens. Le **jeu
  axial** du panneau est ainsi d'environ **1 mm** en tout. Pour qu'il ne décale pas la roue par
  rapport à la vis sans fin, le réduire à 0,3 mm avec **une rondelle de calage** (8 × 14 × 0,5 mm,
  type DIN 988) entre le moyeu de chaque ferrure et son bras.

0. **Inserts** : poser à chaud les 32 inserts M3 dans leurs trous (§ 4), sur toutes les pièces
   qui en portent, avant tout assemblage.
1. **Socle** : presser le 6806 bas par-dessous, jusqu'à l'épaulement, puis le 6806 haut
   par-dessus. Pousser sur la bague extérieure (douille ou tube de Ø40 à 42), jamais sur la
   flasque.
2. **Roue d'azimut** : la poser à plat sur le socle et la fixer par 3 vis fraisées M3×6, qui
   se vissent dans 3 inserts M3×3 du socle et doivent affleurer : la vis d'azimut passe juste au-dessus.
3. **Moyeu** : l'enfiler par le haut, à travers la roue et les deux roulements. Visser la
   bague d'arrêt par-dessous (2 × M3×8, dans 2 inserts M3×5,7 du moyeu).
4. **Fond** : poser l'écrou 1/4" dans son logement hexagonal, par le dessus. Visser ensuite
   le fond sous le socle avec 3 × M3×10, têtes noyées par-dessous : l'écrou est alors
   prisonnier. Poser la tête sur le trépied et la visser sur la vis 1/4" du plateau.
5. **Plateau d'aluminium** : le poser sur le moyeu et le visser par-dessus (3 × M3×8, dans
   3 inserts M3×3 du moyeu).
6. **Chaîne d'azimut**, sous le plateau : le palier (2 × 685, vis sans fin sur sa tige Ø5
   avec sa vis de pression), l'accouplement, le support et le 28BYJ-48 (2 × M3×8 et deux
   écrous M3 derrière les oreilles). La vis vient en prise **radialement** avec la roue
   fixe. Les 4 vis M3×8 du palier et du support se mettent **par-dessus le plateau**, dans les
   lumières, chacune avec une rondelle M3 sous la tête.
7. **Bras** : poser chaque bras sur le plateau et le visser **par-dessous** (4 × M3×8 par bras,
   dans les 4 inserts de sa semelle). Presser un 608 dans chaque bras, **par l'intérieur** (côté
   panneau), jusqu'au fond du logement.
8. **Chaîne d'élévation**, sur l'étagère du bras droit : le palier (2 × 685, vis sans fin,
   arbre Ø5 et vis de pression), l'accouplement, le support et le 28BYJ-48 (2 × M3×8 et deux
   écrous). Le palier et le support se vissent **par-dessous l'étagère** (4 × M3×10,
   dans les inserts de leurs semelles).
9. **Panneau et ferrures** : visser chaque ferrure sur un **grand côté** du cadre (4 × M3×12
   depuis l'extérieur, têtes noyées dans la ferrure, écrou M3 dans le cadre).
10. **Tiges** : présenter le panneau entre les bras, le moyeu des ferrures vers l'extérieur.
    Enfiler la tige gauche depuis l'extérieur à travers le 608 gauche et le moyeu de la ferrure
    (vis de pression sur le méplat), puis la tige droite à travers le 608 droit et la ferrure,
    et enfin la roue d'élévation sur son extrémité. **Placer la roue dans le plan de la vis sans
    fin** (elle engrène avec elle), puis serrer sa vis de pression ; intercaler les rondelles de
    calage pour supprimer le jeu axial.
11. **Réglage des engrènements** (vis et roues graissées) :
    * en azimut, rapprocher le palier dans ses lumières jusqu'à supprimer le jeu, sans
      point dur sur un tour complet ;
    * en élévation, s'il y a trop de jeu, caler la semelle du palier d'un clinquant de 0,1 mm ;
      si la vis est trop serrée, poncer la semelle.
12. **Capteur solaire** (§ 7) : coller les 4 BPW34 dans le boîtier et les câbler, visser le
    boîtier sur son équerre (2 × M3×10 par-dessous), puis l'équerre contre le **petit côté haut**
    du cadre (2 × M3×10, écrous M3 posés dans le cadre).

**Équilibrage** : une fois le panneau monté sur ses tiges, **le lâcher à plusieurs inclinaisons**
(moteur débranché, vis sans fin retirée du contact si besoin). Il doit rester à peu près où on
le met : le centre de gravité n'est qu'à 9 mm de l'axe. S'il bascule nettement d'un côté,
chercher ce qui est mal placé (capteur, câbles) avant de toucher au moteur.

### Monter l'accouplement flexible sur l'arbre du moteur

**Les deux diamètres que l'on voit sur le moteur** (fiche technique du 28BYJ-48, cotes reprises dans la CAO) :

| Partie | Cotes | Rôle |
|---|---|---|
| **Bossage** (la « collerette » qui sort de la face) | **Ø9** (Ø7,8 sur certaines fiches), 1,5 mm de haut | Centre le moteur dans le trou Ø9,6 de la plaque du support. **L'accouplement n'y touche pas** |
| **Arbre de sortie** | **Ø5 (−0,1)**, **10 mm depuis la face** du corps, soit **8,5 mm** qui dépassent du bossage : 2,5 mm ronds, puis **6 mm à deux méplats** distants de **3 mm** | C'est lui qui entre dans l'accouplement |

L'alésage de l'accouplement est **rond, Ø5** : l'arbre y entre quelle que soit son orientation (les méplats sont à l'intérieur du cercle). La vis de serrage de l'accouplement doit simplement tomber **sur un méplat** : on tourne l'accouplement autour de l'arbre avant de serrer, l'arbre n'a pas à être orienté. Sur la fiche, les méplats sont **perpendiculaires à la ligne des deux oreilles** : leurs normales sont verticales (axe Z de la tête), donc la vis de serrage est au-dessus ou au-dessous de l'arbre.

**Ordre à suivre (accouplement d'abord sur le moteur, sur l'établi) :**

1. Enfiler l'accouplement par sa moitié « moteur » sur l'arbre jusqu'à **0,4 mm du bossage** (une cale de carton de 0,4 mm). L'arbre est alors engagé de **8,1 mm** sur les 9,5 mm de la moitié, et son bout s'arrête à **1,4 mm** du milieu de l'accouplement : les deux arbres ne se touchent jamais.
2. Tourner l'accouplement pour que sa vis de serrage soit **sur un méplat**, du côté qui sera accessible une fois monté : **vers le haut (+Z) à l'élévation, vers le bas (−Z) à l'azimut**. Serrer la vis (M3 à six pans creux, environ 0,5 N·m ; une goutte de frein-filet faible).
3. Poser le moteur sur son support : le **bossage entre dans le trou Ø9,6** de la plaque, le **bout de l'accouplement dans le lamage Ø17** (2,1 mm), l'**arbre acier de la vis sans fin** entre dans l'autre moitié de l'accouplement (9,5 mm engagés). Serrer les deux vis M3×8 des oreilles **en poussant le moteur vers le fond de l'accouplement**.
4. Serrer la deuxième vis de serrage sur l'arbre de la vis sans fin, par le même côté (+Z / −Z). L'arbre est **rond** : lui limer d'abord un **méplat de 0,5 mm** au droit de la vis, sinon elle le marque et peut glisser. Orienter ce méplat vers +Z (élévation) ou −Z (azimut) avant de bloquer la vis sans fin sur son arbre.
5. Vérifier à la main que la vis sans fin tourne sans point dur sur un tour complet, moteur hors tension.

**Alignement des trois axes (arbre du moteur, accouplement, arbre de la vis sans fin).** Dans la CAO, les trois axes sont **confondus** : à l'élévation comme à l'azimut, le centre de chaque section est à la même position à **0,000 mm** près (arbre du moteur, accouplement, arbre de la vis). Ce n'est pas un hasard : l'arbre du moteur est placé sur l'axe de l'arbre de la vis (le corps, lui, est décentré de 8 mm ; c'est l'arbre, pas le corps, qui est sur l'axe). Le **jeu de 1,4 mm** entre le bout de l'arbre du moteur et le début de l'arbre de la vis est aussi mesuré. En réalité, l'alignement dépend de l'impression du support : le bossage Ø9 dans un trou Ø9,6 laisse **±0,3 mm** (±0,9 mm si le bossage est de Ø7,8). L'accouplement flexible absorbe ce défaut (plusieurs dixièmes de millimètre de décalage, 1 à 2° d'angle). Pour ne pas le solliciter, serrer les vis des oreilles **après** avoir engagé l'arbre de la vis dans l'accouplement.

**Accès aux vis de serrage** (clé à six pans de 2,5 mm, vérifié sur la CAO avec un dégagement libre de 60 mm) : à l'azimut, **par le bas, tout droit**, pour les deux vis ; à l'élévation, **par le haut, clé inclinée de 25°** (clé à rotule) : la roue d'élévation et le bras droit gênent une clé droite. Les vis des deux moitiés sont à 4,75 mm de chaque extrémité de l'accouplement (à ajuster à l'accouplement reçu : sur le plan du fabricant).

### Visserie en bref

* Dans les fichiers 3D et les images, les **vis sont en orange**, les **rondelles et les
  écrous en vert clair**.
* Presque tout est en **vis CHC M3** (tête cylindrique à six pans creux), de 8 à 12 mm. S'y
  ajoutent 3 vis fraisées M3×6 sous la roue d'azimut et des **vis sans tête** : 2 M3×4 qui
  bloquent les vis sans fin sur leur arbre, 3 M3×6 qui bloquent les tiges (la roue et les deux
  ferrures).

| Vis (norme) | Qté | Où | Se visse dans |
|---|---|---|---|
| **CHC M3 × 8** | 21 | Bague d'arrêt sous le moyeu (2), plateau sur le moyeu (3), palier et support d'azimut sur le plateau (4), bras sur le plateau (8), oreilles des deux 28BYJ-48 (4) | Inserts M3×5,7 et M3×3 ; écrous M3 pour les moteurs |
| **CHC M3 × 10** | 11 | Fond sous le socle (3), palier et support d'élévation sous l'étagère (4), capteur solaire (4) | Inserts M3×5,7 et M3×3 ; écrous M3 pour l'équerre |
| **CHC M3 × 12** | 8 | Ferrures sur le cadre (4 par ferrure) | Écrous M3 dans le cadre |
| **Fraisée M3 × 6** | 3 | Roue d'azimut sur le socle | Inserts M3×3 |
| **Sans tête M3 × 4**, bout plat | 2 | Vis sans fin sur leur arbre | PETG (avant-trou Ø2,8) |
| **Sans tête M3 × 6**, bout plat | 3 | Roue d'élévation et deux ferrures, sur la tige | Inserts M3×3 |

Écrous M3 : **14** (8 ferrures, 4 moteurs, 2 capteur). Rondelles M3 : **4**. Écrou 1/4" : 1.
Clés Allen : 1,5 mm (sans tête), 2 mm (fraisées), 2,5 mm (CHC).

Le guide détaillé de la visserie, avec les vues éclatées des pièces reprises du projet, est
dans **[docs (extra)/visserie/](../../docs%20%28extra%29/visserie/README.md)**.

## 6. Commande : Heltec WiFi LoRa 32 V4 et 28BYJ-48

La carte de commande est un **Heltec WiFi LoRa 32 V4** : un ESP32-S3 avec une radio LoRa
SX1262 (863–870 MHz), un écran OLED et un port USB-C. Il pilote les deux moteurs, lit le
capteur solaire et les origines, mesure l'énergie produite par le panneau et consommée par le
tracker, et envoie toutes ces données en LoRa.

Le **schéma électrique complet** est un projet QElectroTech :
[`Electronique/Schema_Electrique.qet`](../../Electronique/Schema_Electrique.qet), avec son export
[`Electronique/Schema_Electrique.pdf`](../../Electronique/Schema_Electrique.pdf) (3 folios, à
imprimer en A3). Il est généré par `scripts/generate_schema_electrique.py`. Chaque fil y porte
sa section (AWG), et l'épaisseur du trait suit cette section.

| Folio 1 : schéma complet | Folio 2 : brochage et liaisons | Folio 3 : section des fils |
|---|---|---|
| ![Schéma électrique](../../docs%20%28extra%29/electronique/schema_electrique.png) | ![Brochage du Heltec V4](../../docs%20%28extra%29/electronique/brochage_heltec.png) | ![Section des fils](../../docs%20%28extra%29/electronique/cablage_sections.png) |

> **État du schéma et de l'implantation.** Les fichiers de `Electronique/` (schéma QElectroTech, PDF, implantation Fritzing) sont ceux du **modèle idéal personnel** (NEMA 17 et NEMA 11, deux TMC2209) : **ils ne sont pas redessinés pour les 28BYJ-48**. Tout le reste (alimentation, mesure de l'énergie, capteur solaire, LoRa, câbles de la tête) est identique. Ce qui change pour le modèle à fourche est décrit dans ce paragraphe : à la place de chaque TMC2209, une carte (ou une puce) ULN2003, pilotée par un MCP23017 sur l'I²C ; les moteurs 28BYJ-48 de 12 V sont alimentés directement en 12 V par les cartes ULN2003 ; le mini abaisseur U1 ne sert plus qu'au Heltec et au capteur Hall.

**Brochage.** Le Heltec V4 garde pour lui la plupart de ses GPIO : radio et son ampli (2, 5,
7, 8 à 14, 46), écran (17, 18, 21), USB (19, 20), mémoire (26), GNSS (34, 38 à 42), LED,
mesure de la batterie, bouton PRG. Il ne reste que **9 broches libres** sur ses connecteurs.
Un 28BYJ-48 sur ULN2003 demande **4 broches par moteur, soit 8**, plus les 4 du reste du
tracker (I²C, fin de course, Hall) : il en manque 3.

**Solution : un MCP23017**, extension de 16 sorties sur l'I²C déjà en place :
* alimenté en **3,3 V**, adresse **0x20** (A0, A1, A2 à la masse), RESET au 3,3 V : aucun conflit avec
  les adresses 0x48 (ADS1115), 0x40 et 0x45 (wattmètres) ;
* ses 8 sorties pilotent IN1 à IN4 des deux cartes ULN2003 (GPA0 à GPA3 : élévation ; GPB0 à
  GPB3 : azimut) ;
* **8 résistances de 10 kΩ vers la masse** sur les sorties : à la mise sous tension, le MCP23017
  a ses sorties en haute impédance, et sans tirage une bobine pourrait s'allumer au démarrage ;
* alternative : un 74HC595 (3 broches : données, horloge, verrou) plus une 4ᵉ pour OE.

| GPIO | Connecteur | Signal | Vers |
|---|---|---|---|
| 3 | J3-14 | SDA | bus I²C : ADS1115 (capteur solaire), INA219B et SEN0291 (wattmètres), **MCP23017** |
| 4 | J3-15 | SCL | bus I²C |
| 44 | J2-5 | FDC_EL | fin de course d'élévation (contact NC) ; tirage R6 |
| 6 | J3-17 | HALL_AZ | capteur à effet Hall d'azimut ; tirage R7 |
| 47, 43, 48, 45, 33 | J2-13, J2-6, J2-14, J3-6, J2-12 | libres | ex-STEP, DIR et EN des TMC2209 : **plus utilisées** |

Deux autres choix découlent de ce brochage, comme avant :
* **les 4 photodiodes sont lues par un ADS1115** (convertisseur 16 bits, 4 entrées, sur
  l'I²C) au lieu des entrées analogiques de l'ESP32. Il est plus précis, et son gain réglable
  évite de changer les résistances entre le soleil et une lampe (§ 7) ;
* **les deux wattmètres sont aussi sur l'I²C** : quatre modules sur les deux mêmes broches,
  chacun à son adresse.

```cpp
// Heltec WiFi LoRa 32 V4 : broches du tracker
#define PIN_SDA       3   // I2C : MCP23017 0x20, ADS1115 0x48, INA219B 0x40, SEN0291 0x45 ; Wire.begin(PIN_SDA, PIN_SCL)
#define PIN_SCL       4
#define PIN_FDC_EL   44   // U0RXD ; 1 = butée basse atteinte, ou fil coupé
#define PIN_HALL_AZ   6   // 0 = aimant devant le capteur
// moteurs : plus de STEP/DIR/EN, tout passe par le MCP23017 (registres OLATA = élévation, OLATB = azimut)
```

GPIO 44 est l'UART0 de l'ESP32-S3. Le moniteur série passe par l'USB : dans l'IDE
Arduino, garder **« USB CDC On Boot : Enabled »**, et ne jamais appeler `Serial0.begin()`.
Prendre le **V4 « standard »** (ESP32-S3R2), pas la variante **V4-R8**, dont le brochage est
différent.

**Alimentation.**
* Le 12 V vient de la **sortie LOAD du régulateur solaire** A6 (Velleman SOL10UC3). Celui-ci
  charge une **batterie au plomb étanche de 12 V et 5 Ah** avec le panneau. Le courant passe ensuite par
  un **fusible de 3 A** et un **interrupteur** (F1, S1), puis par le wattmètre A5, qui mesure
  la consommation du tracker, avant d'arriver sur la plaque (X1). Sur l'établi, porte
  ouvert, un bloc secteur 12 V 3 A peut remplacer le régulateur et la batterie, sur F1.
* **F1 et F2 sont des porte-fusibles en ligne**, sertis sur les fils, **dans le boîtier** :
  * **F1 à la sortie LOAD** du régulateur : il protège les fils qui vont à la plaque ;
  * **F2 sur le fil entre la batterie et le régulateur, à moins de 10 cm du + de la
    batterie**. Le fil qui le précède n'est protégé par rien, et une batterie au plomb en
    court-circuit débite des centaines d'ampères : il doit rester le plus court possible.

  Un fusible ne protège que ce qui vient après lui : chacun est donc au plus près de sa
  source.
* Le 12 V va au **mini abaisseur 5 V** (U1, environ 18 × 13 mm), qui alimente le Heltec et le capteur
  Hall, et **directement aux cartes ULN2003** (moteurs de 12 V). **U1 doit fournir au moins 0,5 A**
  (Heltec avec WiFi et capteur Hall) : vérifier la référence du module. Un condensateur de
  **100 µF 25 V** sur le 12 V, près des cartes ULN2003.
* U1 a une **sortie fixe de 5,0 V** : **la mesurer au multimètre (4,9 à 5,2 V) avant de
  brancher le Heltec**. Le 5 V passe ensuite par une diode Schottky 1N5819 (D1) : le Heltec
  reçoit environ 4,7 V, assez pour son régulateur 3,3 V, et le 5 V de l'USB-C ne remonte pas
  dans l'abaisseur quand la carte est branchée à l'ordinateur.
* Le **capteur Hall B1 est alimenté avant D1**, directement par U1 : l'A3144 demande 4,5 V au
  moins. Les **cartes ULN2003 ne sont pas sur le 5 V** : leur + est au 12 V de la plaque.
* Le 3,3 V du Heltec alimente le MCP23017, l'ADS1115, les deux wattmètres, les
  photodiodes et les résistances de tirage. Tous les 0 V sont reliés, sauf le − du panneau
  (voir plus bas, « Mesure de l'énergie »).

**Moteurs : 2 × 28BYJ-48 sur cartes ULN2003.** Les cartes sont livrées avec les moteurs dans les
kits courants ; elles pilotent chaque bobine par un transistor Darlington. Les entrées IN1 à IN4
sont reliées aux sorties du MCP23017 (3,3 V suffisent), et le + de la carte au **12 V**.
* **Un seul moteur alimenté à la fois** : le suivi corrige l'élévation, puis l'azimut. Jamais les deux
  ensemble (le courant de 12 V ne double pas, et le fusible et le wattmètre A5 n'ont à tenir qu'un moteur).
* **À l'arrêt, les 8 sorties à 0** : une bobine alimentée en continu dissipe environ 1,4 W (deux bobines : 12 V, 200 Ω) et
  chaufferait le support en PETG. Les vis sans fin tiennent le panneau moteurs coupés. Les
  sorties sont mises à 0 entre deux corrections.
* **Séquence demi-pas**, 8 phases (IN1 à IN4 sur les bits 0 à 3 du quartet de chaque moteur) :

```cpp
// 8 phases pour un 28BYJ-48 sur ULN2003 : IN1 = bit 0 ... IN4 = bit 3
const uint8_t PHASES[8] = {0b0001, 0b0011, 0b0010, 0b0110, 0b0100, 0b1100, 0b1000, 0b1001};
// une phase = une écriture I2C de 2 octets (registre OLATA ou OLATB du MCP23017)
// pour tourner à l'envers : parcourir le tableau dans l'autre sens
// vitesse : 120 phases par seconde (environ 1,8 tr/min de l'arbre de sortie), pas plus tant
// que le couple n'a pas été mesuré à plus haute fréquence
```

* **Ordre des fils** : bleu, rose, jaune, orange pour IN1 à IN4 sur les cartes courantes, rouge au
  **+ 12 V**. **Vérifier le sens et l'ordre sur le moteur reçu** : une inversion fait vibrer l'arbre
  sans le faire tourner. Au multimètre, environ 200 Ω entre le rouge et chaque autre fil, environ
  400 Ω entre deux fils de bobines différentes d'une même paire.
* Si un moteur tourne à l'envers, inverser son sens dans le programme.
* **Rallonge** : le câble d'origine du moteur est court (environ 25 cm). Le prolonger avec un
  câble souple 5 conducteurs (§ plus bas), vers un bornier de la plaque.

**Origines.**
* **Fin de course S2** (micro-rupteur SPS75GCC) en butée basse d'élévation (−2°). Son commun
  va au 0 V, son contact **NC** au GPIO 44, avec une résistance de tirage de 10 kΩ. Si un fil
  se coupe, l'ESP32 lit « butée atteinte » et arrête le moteur, au lieu de laisser le
  panneau taper en bout de course.
* **Capteur à effet Hall B1** (A3144) et un aimant sur la roue fixe pour l'azimut. Il est
  alimenté en 5 V, et sa sortie (collecteur ouvert) est tirée au 3,3 V par 10 kΩ. Prendre un
  **A3144 nu** : le module KY-003 tire sa sortie au 5 V, trop pour l'ESP32.
* La détection de calage sans capteur (StallGuard) n'est pas fiable à basse vitesse,
  surtout derrière une vis sans fin.

**Mesure de l'énergie : deux wattmètres INA219.** Les deux modules mesurent chacun une
tension et un courant. L'ESP32 en tire la puissance, et l'énergie en wattheures. Ils
partagent le bus I²C de l'ADS1115 : aucune broche en plus.

| Repère | Module | Branché sur | Shunt, calibre | Adresse I²C |
|---|---|---|---|---|
| A4 | **INA219B d'Adafruit** (904) | le + du panneau, entre le panneau et le régulateur de charge : **ce que produit le panneau** | 0,1 Ω, ±3,2 A | 0x40 (A0 et A1 ouverts, réglage d'origine) |
| A5 | **SEN0291 de DFRobot** (INA219) | le + de la batterie, après F1 et S1 : **ce que consomme tout le tracker** (moteurs, Heltec, capteurs) | 0,01 Ω, ±8 A | 0x45 : mettre ses deux micro-interrupteurs A0 et A1 sur 1 |

* **Pourquoi cette répartition.** Le panneau débite 0,6 A au plus. Le shunt de 0,1 Ω de
  l'INA219B mesure ce courant dix fois plus finement que celui de 0,01 Ω (0,1 mA au lieu de
  1 mA). Le 12 V du tracker monte à 1,5 A, et le fusible F1 est de 3 A : le SEN0291, prévu
  pour 8 A, garde de la marge.
* **Câblage** (bande « Mesure de l'énergie » du folio 1 du schéma) :
  * **A5** : le fil qui vient de S1 arrive sur IN+. Un fil AWG 18 relie IN− à X1+, l'entrée
    12 V de la plaque. GND va au 0 V.
  * **A4** : le + du panneau arrive directement sur le bornier VIN+ de A4, et VIN− va au PV+
    du régulateur. **Le − du panneau va directement au PV− du régulateur**, jamais au 0 V du
    boîtier. Certains régulateurs coupent le −, d'autres le + : ainsi, le montage convient
    aux deux. A4 lit la tension du panneau avec un
    régulateur à « masse négative commune », celle de la batterie avec les autres.
  * Les deux modules sont alimentés en **3,3 V** par le Heltec, par la barrette J1 (3V3, GND,
    SDA, SCL) : un câble STEMMA QT pour A4, le câble Gravity pour A5. Leurs résistances de
    tirage I²C tirent alors au 3,3 V. L'ESP32 ne supporte pas 5 V sur ses broches.
* **Tension du panneau.** L'INA219 supporte 26 V au plus. Le panneau SOL10P fait 21,8 V à
  vide : c'est bon. Un panneau « 24 V » (Voc ≈ 43 V) détruirait A4.
* **Pour que le panneau débite, il lui faut une charge.** En extérieur, c'est le
  **régulateur de charge PWM Velleman SOL10UC3** (A6, Gotronic réf. 27118). Il recharge la
  batterie, et le tracker se branche sur sa sortie LOAD : le tracker devient autonome.
  * **Il ne charge que les batteries au plomb, gel ou EFB, pas les LiFePO4.** La batterie
    fournie, au plomb étanche de 12 V et 5 Ah (88 × 70 × 100 mm), convient. Le panneau la
    charge à 0,6 A au plus, soit un huitième de sa capacité : bien en dessous du quart que
    supporte une batterie au plomb.
  * Sa sortie LOAD est **coupée quand la batterie est trop basse** : le régulateur protège
    ainsi la batterie au plomb, qu'une décharge profonde abîme. Les vis sans fin tiennent le
    panneau en place, moteurs coupés. Quand la batterie remonte, le Heltec redémarre : les
    énergies cumulées et le numéro de message repartent de 0.
  * **Le 0 V du boîtier vient de LOAD− seulement.** Le − du panneau va au PV− du régulateur,
    celui de la batterie à BAT−, sans toucher le 0 V du boîtier. Certains régulateurs
    coupent le −, d'autres le + : ainsi, le montage convient aux deux, et la coupure de
    LOAD reste active.
  * **Ordre de branchement : la batterie d'abord** (le régulateur reconnaît alors 12 V et
    non 24 V), puis le panneau, puis la sortie LOAD. Débrancher dans l'ordre inverse.
  * Le régulateur a son propre fusible, **F2, à moins de 10 cm de la batterie**. Son port
    USB (5 V, 1,2 A) n'est pas utilisé.
  * Sur l'établi, avec un bloc secteur à la place du régulateur et de la batterie, A4 lit
    0 A. **Ne jamais brancher un régulateur de charge sur un bloc secteur.** En intérieur,
    la batterie chargée tient 1,5 à 6 jours.
* **Ce que lit A4.**
  * Un régulateur PWM relie le panneau à la batterie. Le panneau travaille alors à la
    tension de la batterie, environ 13 V, au lieu de ses 17,6 V : il donne ses 0,6 A, soit
    environ **8 W au lieu de 10 W** en plein soleil.
  * Quand la batterie est pleine, le régulateur hache puis coupe le courant du panneau. A4
    lit alors moins, voire 0 A, même en plein soleil : le panneau ne donne que ce que la
    batterie accepte. La moyenne de l'INA219 (68 ms) et le cumul toutes les 0,2 s lissent
    ce hachage.
* **Ordre de grandeur du bilan** (à confirmer avec A4 et A5) :
  * le panneau produit environ 30 Wh par jour de beau temps (8 W pendant 4 heures
    équivalentes de plein soleil) ;
  * le tracker consomme surtout par le Heltec, en continu : quelques dixièmes de watt,
    soit 5 à 20 Wh par jour. Les moteurs ne tournent que 1 % du temps ;
  * la batterie de 12 V et 5 Ah stocke 60 Wh. On n'en utilise que la moitié pour ne pas
    l'abîmer, soit 30 Wh : le tracker tient **1,5 à 6 jours sans soleil** selon ce que
    consomme le Heltec (1,5 jour au pire). Une journée de beau temps (≈ 30 Wh) remplit cette
    moitié. Pour tenir plus longtemps, il faut réduire la consommation du Heltec : WiFi coupé
    hors des mises à jour, écran éteint, sommeil léger entre deux corrections.
* **Étalonnage.** DFRobot demande d'étalonner le courant du SEN0291 :
  1. mettre un multimètre en série (calibre 10 A) pendant un mouvement des moteurs ;
  2. diviser le courant du multimètre par celui que lit A5 ;
  3. mettre ce rapport dans le programme (`kTracker` ci-dessous).

  Faire de même pour A4 au soleil (`kPanneau`).

```cpp
#include <Wire.h>
#include <DFRobot_INA219.h>

DFRobot_INA219_IIC inaPanneau(&Wire, INA219_I2C_ADDRESS1);  // A4 : INA219B Adafruit, 0x40
DFRobot_INA219_IIC inaTracker(&Wire, INA219_I2C_ADDRESS4);  // A5 : SEN0291, 0x45
const float R_PANNEAU = 0.1, R_TRACKER = 0.01;  // shunts (ohms)
float kPanneau = 1.0, kTracker = 1.0;           // étalonnage au multimètre

bool initWattmetre(DFRobot_INA219_IIC &ina) {
  if (!ina.begin()) return false;               // absent : signalé dans la trame LoRa
  ina.setBRNG(eIna219BusVolRange_32V);
  ina.setPGA(eIna219PGABits_8);                 // ±320 mV sur le shunt
  ina.setBADC(eIna219AdcBits_12, eIna219AdcSample_128);
  ina.setSADC(eIna219AdcBits_12, eIna219AdcSample_128);   // moyenne sur 68 ms : lisse les à-coups des moteurs
  ina.setMode(eIna219SAndBVolCon);
  return true;
}

// toutes les 0,2 s : courant = tension du shunt / résistance du shunt, énergie cumulée
float mA(DFRobot_INA219_IIC &ina, float r, float k) { return k * ina.getShuntVoltage_mV() / r; }
// energie_mWh += ina.getBusVoltage_V() * mA(...) * 0.2 / 3600;
```

Le même calcul sert pour les deux modules : seule la valeur du shunt change. On évite ainsi
le réglage de calibration propre à chaque bibliothèque.

**LoRa.**
* L'**antenne 868 MHz** fournie se visse sur le connecteur IPEX. **Ne jamais émettre sans
  elle** : l'étage de sortie peut griller.
* Les données partent dans une **trame de 38 octets**, octets de poids faible en premier
  (l'ordre de l'ESP32). Elle est aussi au folio 2 du schéma.

  | Octets | Champ | Type | Unité |
  |---|---|---|---|
  | 0 | version de la trame (= 1) | uint8 | |
  | 1–2 | numéro du message | uint16 | de 0 à 65 535, puis repart à 0 |
  | 3–6 | azimut : consigne, position | 2 × int16 | 0,01° |
  | 7–10 | élévation : consigne, position | 2 × int16 | 0,01° |
  | 11–12 | erreur de pointage | uint16 | 0,001° |
  | 13–20 | photodiodes HG, HD, BG, BD | 4 × int16 | valeur brute de l'ADS1115 |
  | 21 | état | uint8 | bits : 0 butée basse, 1 aimant Hall, 2 moteurs alimentés, 3 GNSS valide, 4 calibre intérieur de l'ADS1115, 5 A4 absent, 6 A5 absent |
  | 22–23 | panneau : tension (A4) | uint16 | mV |
  | 24–25 | panneau : courant (A4) | int16 | 0,1 mA |
  | 26–27 | 12 V du tracker : tension (A5) | uint16 | mV |
  | 28–29 | 12 V du tracker : courant (A5) | int16 | mA |
  | 30–33 | énergie produite par le panneau | uint32 | mWh, cumulée depuis la mise sous tension |
  | 34–37 | énergie consommée par le tracker | uint32 | mWh, cumulée depuis la mise sous tension |

  Le récepteur obtient la puissance (tension × courant), et l'énergie d'une journée par
  différence entre deux messages. La comparaison des deux énergies montre si le panneau
  couvre la consommation du tracker.
* Dans la bande 868 MHz, chaque émetteur ne doit occuper le canal que 1 % du temps en
  général. 38 octets durent environ 0,3 s en SF9 : un message par minute. En SF12 (2 s), un
  message toutes les 5 minutes.
* La réception se fait sur un second module LoRa, ou par LoRaWAN (The Things Network) si une
  passerelle est à portée.

**GNSS (facultatif).** Le module L76K de Heltec se branche sur le connecteur GNSS de la carte.
Il donne l'heure et la position pour le calcul de la position du Soleil (§ 7).

**Bibliothèques Arduino.**
* `Adafruit_MCP23X17` : sorties du MCP23017 (ou écritures directes de OLATA/OLATB, plus rapides). Pas de
  bibliothèque de pas à pas : la séquence de 8 phases se pilote par une minuterie, à 120 phases par
  seconde.
* `Adafruit_ADS1X15` : lecture de l'ADS1115.
* `DFRobot_INA219` : lecture des deux wattmètres (elle règle aussi leur moyenne).
* La bibliothèque Heltec (« Heltec ESP32 Dev-Boards ») ou `RadioLib` pour la radio. Sur le
  V4, l'ampli de sortie se commande par les GPIO 7, 2 et 46 : partir des exemples Heltec.
* `TinyGPSPlus` pour le GNSS.
* `ArduinoOTA` (fournie avec le cœur ESP32) : mise à jour du programme par le WiFi, sans
  ouvrir le boîtier étanche.

**Câbles : section de chaque fil** (détail au folio 3 du schéma). La section dépend du
courant et de la longueur. Elle est écrite sur chaque fil du schéma, et dans ses propriétés
QElectroTech (« Section du conducteur »).

| Liaison | Courant | Longueur | Section | Fil |
|---|---|---|---|---|
| Sortie LOAD du régulateur (ou bloc 12 V) → F1 → S1 → A5 → X1, et 0 V | 1,5 A | < 30 cm | **AWG 18** (0,82 mm²) | souple, rouge et noir, dans le boîtier |
| 12 V et 0 V sur la plaque (entrée de U1 et cartes ULN2003, un seul moteur à la fois) | 0,4 A | < 15 cm | **AWG 22** (0,33 mm²) | rouge et noir |
| 5 V : U1 → D1 → Heltec, U1 → capteur Hall (X5), et leur 0 V | 0,5 A | < 10 cm | **AWG 22** (0,33 mm²) | orange et noir |
| Moteurs M1 et M2 (cartes ULN2003 → X2, X3 → moteur) | 0,06 A par bobine, sous 12 V | 1,5 m | **AWG 24** (0,20 mm²) | câble souple 5 conducteurs par moteur : 4 bobines et le commun (rouge) |
| Entrées IN1 à IN8 des cartes, 3,3 V, I²C, filtres du capteur | < 20 mA | < 10 cm | **AWG 24** (0,20 mm²) | monobrin |
| Fin de course S2 (X4) et capteur Hall B1 (X5) | 10 mA | 1,5 m | **AWG 26** (0,13 mm²) | câble souple 2 et 3 conducteurs |
| Capteur solaire (X6) | 8 mA | 1,5 m | **AWG 26** (0,13 mm²) | câble souple **blindé** 6 conducteurs |
| Pattes des photodiodes, dans le boîtier du capteur | 2 mA | 5 cm | **AWG 28** (0,08 mm²) | fil fin isolé (fil à wrapper) |
| Panneau → A4 (le +) et régulateur (le −) | 0,6 A | 2 m | **AWG 20** (0,52 mm²) | câble souple 2 conducteurs, par la boucle de câble |
| A4 (VIN−) → régulateur de charge (PV+) | 0,6 A | < 20 cm | **AWG 20** (0,52 mm²) | rouge, dans le boîtier |
| Régulateur → F2 → batterie | 0,6 A | < 20 cm | **AWG 18** (0,82 mm²) | souple, rouge et noir, dans le boîtier ; F2 à moins de 10 cm de la batterie |
| I²C des wattmètres (J1 → A4, A5) | < 2 mA | < 20 cm | **AWG 26** (0,13 mm²) | câble STEMMA QT (A4) et câble Gravity (A5) |
| Antenne LoRa | radio | 10 cm | coaxial 50 Ω | IPEX vers SMA (1,13 mm ou RG178) |

* En AWG 18, la chute de tension sur l'aller-retour du 12 V (2 × 1 m, 1,5 A) n'est que de
  0,06 V. Un moteur 28BYJ-48 12 V a des bobines de 200 Ω : la résistance du câble de 1,5 m en AWG 24
  (environ 0,25 Ω par fil) ne change rien.
* **Tout ce qui va vers la tête est en multibrin souple** (câble du panneau compris), jamais
  en monobrin, qui casse à force de plier dans la boucle de câble.
* Torsader les 5 fils de chaque moteur ensemble : ils rayonnent moins de parasites vers les capteurs.
* Le câble du capteur solaire passe à l'écart des câbles moteurs. Son blindage est relié au
  0 V **côté boîtier seulement**.
* Dans les borniers à vis, sertir un **embout de câblage** : 0,75 mm² pour l'AWG 18,
  0,5 mm² pour l'AWG 20 et 22, 0,25 mm² pour l'AWG 24 et 26.

**Installation.** Tout ce qui ne tourne pas avec la tête est dans **un seul boîtier
étanche (IP65)**, au pied du trépied : plaque, wattmètres, régulateur, batterie et fusibles.
Seuls restent dehors la tête (moteurs, fin de course, capteur Hall, capteur solaire) et le
panneau. Leurs câbles descendent par le passe-câble du socle et entrent dans le boîtier par
des presse-étoupes (folio 2 du schéma : nombre de conducteurs par câble).

### Implantation du boîtier électronique

L'électronique tient sur une **plaque à pastilles de 7 × 9 cm** (24 × 30 trous utilisés : une
plaque d'essais ECS1/2 en époxy, coupée à 28 × 34 trous, voir la liste des composants), tassée au
plus près. Le même boîtier étanche reçoit aussi les deux wattmètres, la batterie, les
fusibles et le régulateur de charge, vissé sous la porte. L'implantation est dessinée à
l'échelle dans Fritzing :
[`Electronique/Implantation_Boitier.fzz`](../../Electronique/Implantation_Boitier.fzz), à ouvrir dans
Fritzing (gratuit), vue « Platine d'essai ». Le fichier est généré par
`scripts/generate_implantation_fritzing.py`.

![Implantation du boîtier électronique](../../docs%20%28extra%29/electronique/implantation_boitier.png)

| La plaque à pastilles, de plus près |
|---|
| ![Plaque à pastilles 7 × 9 cm](../../docs%20%28extra%29/electronique/plaque_pastilles.png) |

* **Organisation de la plaque** : chaque pièce est à côté de ce qu'elle dessert, ce qui
  raccourcit les fils.
  * **En haut**, les borniers des câbles de la tête : ceux des moteurs (X2, X3) au-dessus de
    leurs cartes ULN2003, ceux des capteurs (X4 à X6) au-dessus de l'ADS1115. Les 4 photodiodes de X6
    tombent droit sur les entrées A0 à A3.
  * **Au milieu**, le MCP23017 avec ses 8 résistances de tirage, et l'ADS1115 avec ses filtres
    juste dessous (R1 à R4, C3 à C6). **Les cartes ULN2003** du kit mesurent environ 31 × 35 mm : elles
    **ne tiennent pas** sur la plaque de 7 × 9 cm déjà pleine. Deux solutions : la **puce ULN2003A**
    (DIP-16, 20 × 7 mm) soudée sur la plaque à la place de chaque TMC2209, ou les deux cartes
    fixées au fond du boîtier, à côté de la plaque. **L'implantation Fritzing n'est pas redessinée.**
  * **En bas**, le Heltec, USB-C au bord gauche. D1 et les résistances de tirage R5 à R7 sont le
    long du bas, près des broches qu'elles desservent.
  * **Au bord droit**, vers l'énergie : J1 (bus I²C des wattmètres), le mini abaisseur U1 et X1
    (12 V, fils entrant par la droite).
  * Aucune pièce n'est cachée sous un module : tout reste visible, mesurable et réparable.
* **Modules sur barrettes femelles**, pour pouvoir les retirer : Heltec V4 (2 × 18 broches),
  ADS1115 (1 × 10) et MCP23017. Les résistances, les condensateurs et la diode
  sont soudés. U1 est posé à plat, tenu par 4 pattes (des chutes de pattes de résistance)
  soudées dans ses pastilles et dans la plaque.
* **Wattmètres A4 et A5 sous la plaque**, sur entretoises (M2,5 pour l'INA219B, M3 pour le
  SEN0291). Leur bus I²C arrive par la **barrette mâle J1** (2 × 4 broches : 3V3, GND, SDA, SCL
  pour chacun).
* **Batterie G1 couchée** à droite de la plaque : vue de face (porte ouverte), elle fait
  100 mm de large et 88 mm de haut, et seulement **70 mm dans la profondeur** du boîtier. Ses
  bornes sortent de la face gauche, le − au-dessus du +, dans le couloir de câblage. Tenue par
  une sangle (ou des équerres) : 1,9 kg ne doivent pas se promener dans le boîtier.
  * Couchée, elle doit être **étanche (AGM, « VRLA », sans entretien)** : c'est le cas des
    batteries au plomb 12 V 5 Ah de ce format, qui marchent dans toutes les positions sauf
    **tête en bas**. Pas de batterie à bouchons (plomb ouvert, électrolyte liquide).
* Le fusible en ligne **F2**, entre le + de la batterie et le régulateur, est sous la batterie :
  moins de 10 cm de fil depuis le +.
* **Couloir de câblage** de 18 mm entre la plaque et la batterie : on y range les fils, et les
  bornes de la batterie y sortent.
* **Régulateur A6 vissé sous la porte**, comme sur les stations solaires de terrain : il ne
  prend plus de place au fond du boîtier.
  * **Fixation** : 4 vis inox dans ses trous de fixation, avec une **rondelle d'étanchéité**
    (EPDM ou joint torique) sous chaque tête, côté extérieur, et un écrou frein à l'intérieur.
    Sans elles, chaque trou laisserait entrer l'eau. À défaut, le coller avec un adhésif double
    face pour l'extérieur (type VHB) : la porte reste sans trou.
  * **Place** : porte fermée, il avance d'environ 35 mm (25 mm d'épaisseur, plus ses fils)
    devant la plaque et les wattmètres, qui n'avancent que de 35 mm au plus : 70 mm sur les
    80 mm de profondeur. Il ne doit **jamais** être devant la batterie : 70 mm de batterie +
    35 mm de régulateur dépassent les 80 mm du boîtier. Le dessin montre la porte ouverte,
    avec la zone à laisser libre.
  * **Ses 6 fils passent par la charnière** : fil multibrin souple (jamais de monobrin, qui
    casse à force de plier), réunis dans une gaine spirale. Laisser une **boucle d'environ
    20 cm** pour que la porte s'ouvre en grand sans tirer. Attacher la boucle de chaque côté de
    la charnière (colliers sur embases adhésives), **à l'intérieur du joint** : la porte ne
    doit pas pincer les fils en se fermant.
  * **F1** est posé sur la porte, contre la borne LOAD : un fusible protège le fil qui le suit.
    Les deux fils + qui passent la charnière (BAT+ après F2, LOAD+ après F1) sont donc
    protégés.
  * Ses voyants font face à l'intérieur : on les voit porte ouverte. Les mesures de A4 et A5
    arrivent de toute façon par LoRa.
* **Interrupteur S1** sur la paroi des presse-étoupes.
* **USB-C du Heltec au bord de la plaque, sans découpe** (elle casserait l'étanchéité). Il reste
  environ 14 mm jusqu'à la paroi : on reprogramme porte ouverte avec un câble USB-C coudé,
  ou sans rien ouvrir par le WiFi (mise à jour OTA).
* **Borniers à vis** au bord de la plaque : au pas de 5,08 mm (KF301) pour le 12 V et les
  moteurs, au pas de 2,54 mm (DG308, fils AWG 26 à 18) pour les capteurs, deux fois moins
  larges.

  | Bornier | Pôles | Pas | Câble |
  |---|---|---|---|
  | X1 | 2 | 5,08 mm | 12 V (depuis A5 IN−) et 0 V (depuis LOAD− du régulateur) |
  | X2 | 5 | 5,08 mm | moteur M1 (élévation) : 4 bobines et le commun 12 V |
  | X3 | 5 | 5,08 mm | moteur M2 (azimut) : 4 bobines et le commun 12 V |
  | X4 | 2 | 2,54 mm | fin de course S2 |
  | X5 | 3 | 2,54 mm | capteur à effet Hall B1 (+5 V pris avant D1) |
  | X6 | 5 | 2,54 mm | capteur solaire |

  Le panneau n'a pas de bornier sur la plaque : il se branche directement sur A4 et sur le
  régulateur.
* **Hauteur au-dessus de la plaque** : ≈ 14 mm pour le Heltec, l'ADS1115 et le MCP23017, ≈ 12 mm pour le 100 µF, ≈ 10 mm pour les
  borniers, ≈ 5 mm pour U1.
* **Boîtier** : **étanche IP65, à porte sur charnières**, au moins 226 × 120 mm à l'intérieur
  (vu de face) et **80 mm de profondeur** intérieure, de la porte fermée au fond : la batterie
  couchée y prend 70 mm, la plaque 35 mm plus les 35 mm du régulateur de la porte. Soit un
  boîtier d'environ 250 × 150 × 100 mm, ou plus grand. La porte doit faire au moins 110 × 80 mm à l'intérieur pour recevoir le
  régulateur. Vérifier les cotes intérieures : les vis et les charnières prennent de la place
  dans les coins. **Porte opaque et de couleur claire** : un couvercle transparent n'apporte
  plus rien (le régulateur cache l'écran du Heltec et tourne ses voyants vers l'intérieur), et
  il chauffe plus au soleil. La plaque est posée sur 4 entretoises M3 de 6 mm, dans ses trous
  de fixation. Avec la batterie, l'ensemble pèse environ 3 kg.
* **Traversées du boîtier**, toutes étanches :
  * **6 presse-étoupes PG7**, sur une même paroi : moteurs M1 et M2, fin de course, capteur
    Hall, capteur solaire, panneau. Faire faire à chaque câble une **boucle d'égouttement**
    (un U plus bas que le presse-étoupe) : l'eau qui coule le long du câble tombe avant
    d'arriver au boîtier ;
  * l'**interrupteur S1, étanche** (à bascule avec capuchon en silicone, ou à levier avec
    soufflet) ;
  * l'antenne LoRa à l'extérieur, par un câble IPEX vers une **traversée SMA étanche** (avec
    joint) : une antenne enfermée dans le boîtier porte moins loin. Une antenne articulée se
    redresse verticalement ;
  * un **aérateur à membrane** (M12, IP67) : il laisse passer l'air mais pas l'eau. Le boîtier
    chauffe le jour et refroidit la nuit : sans lui, il aspire de l'air humide par les joints,
    et l'eau se condense dedans. Il laisse aussi sortir les traces de gaz qu'une batterie au
    plomb peut dégager en fin de charge. Ajouter un sachet de gel de silice.
* **Chaleur** : un boîtier clair, à l'ombre (sous le trépied, par exemple). En plein soleil, un
  boîtier fermé dépasse vite 50 °C : la batterie s'use bien plus vite au chaud, et le
  régulateur, sur la porte, est prévu pour 55 °C au plus.
* **Lest** : posé à plat sous le trépied et sanglé au moyeu de la colonne, entre deux sacs de
  sable, le boîtier sert aussi de lest contre le vent (§ 8). Laisser alors du mou aux câbles,
  et tourner la paroi des presse-étoupes à l'opposé du vent dominant.

## 7. Capteur solaire de la démonstration

Le capteur est celui du [README principal](../../README.md) (§ 4) : même boîtier, même croix,
mêmes photodiodes BPW34. Pour la
démonstration, le boîtier et son équerre sont imprimés. **Il est fixé sur le petit côté haut
du cadre** (le côté de 253 mm qui monte quand le panneau s'incline) : les grands côtés portent les ferrures.

| Pièce | Impression |
|---|---|
| `Capteur_Solaire_Boitier` | **PETG noir**, croix en haut, **100 %** de remplissage (18 g). Un PETG clair laisse passer la lumière à travers les murs et fausse la mesure. À défaut, le peindre en noir mat, intérieur des logements compris. Il chauffe au soleil comme tout objet noir, mais ne porte aucune charge |
| `Capteur_Solaire_Support` | N'importe quelle couleur, plaque sur le plateau (8 g). Les trous de l'âme sont en goutte |

1. Repérer la cathode de chaque BPW34 au multimètre, en position diode. Quand l'appareil
   affiche environ 0,5 V, la pointe rouge est sur l'anode et la noire sur la cathode.
2. Glisser chaque BPW34 dans son logement **par en dessous**, face transparente vers le
   haut, jusqu'au plancher. La pousser contre le coin du logement **du côté de la croix**, de
   la même façon pour les quatre, puis la bloquer par un point de colle chaude par-dessous.
3. Relier les 4 cathodes au fil du 3,3 V, et souder un fil sur chaque anode. Isoler les
   soudures (gaine thermorétractable ou colle chaude).
4. Faire passer le câble (5 fils : 3,3 V et les 4 signaux) par le passage carré de
   l'équerre, puis le long du cadre et de la fourche, avec les câbles des moteurs. Laisser une boucle près
   de l'axe d'élévation (le panneau bascule de plus de 90°).

**Branchement**, identique pour chacune des 4 photodiodes (folio 1 du schéma électrique,
§ 6). Les résistances, les condensateurs et l'ADS1115 sont dans le boîtier électronique,
pas dans le capteur :

```
3,3 V ──────── cathode   BPW34   anode ──┬───────┬──────► ADS1115 : A0 (HG), A1 (HD),
                                         │       │                  A2 (BG), A3 (BD)
                                       1 kΩ    100 nF
                                         │       │
GND ─────────────────────────────────────┴───────┘
```

**La résistance : 1 kΩ, à couche métallique, ±1 %, 1/4 W.**
* En plein soleil (≈ 1000 W/m²), la fenêtre de 2,2 × 2,2 mm reçoit environ 4,8 mW. La BPW34
  en tire environ 0,3 A/W sur le spectre solaire, soit **≈ 1,5 mA**, entre 1,2 et 2 mA selon
  le ciel et l'exemplaire.
* Avec 1 kΩ, cela fait **≈ 1,5 V** sur l'entrée, entre 1,2 et 2 V. L'ADS1115, réglé sur son
  calibre ±4,096 V, le lit à environ 12 000 points, et une erreur de 0,1° change le signal
  d'environ 190 points. Sur la Lune, le Soleil plus fort (1361 W/m²) donnerait environ 2 V :
  encore dans le calibre.
* La photodiode garde au moins 1,3 V de polarisation inverse (3,3 V − 2 V) : sa réponse reste
  linéaire. La résistance ne dissipe que ≈ 2 mW.
* ±1 % et couche métallique : les 4 résistances restent égales et varient peu avec la
  température, ce qui compte puisque le programme compare les 4 signaux. L'étalonnage au
  papier calque (README principal, § 4) corrige ce qui reste.
* **En intérieur, sous une lampe**, la lumière est 10 à 50 fois plus faible : 30 à 150 mV.
  On garde les mêmes 1 kΩ. Le programme passe l'ADS1115 sur un calibre plus petit
  (±0,256 V, 7,8 µV par point), ce qui donne encore 4 000 à 19 000 points. Règle simple :
  si le signal le plus fort dépasse 90 % du calibre, prendre le calibre au-dessus ; s'il
  tombe sous 20 %, celui en dessous.
* Le **condensateur de 100 nF** (céramique, 50 V) en parallèle sur chaque résistance filtre le
  bruit : avec 1 kΩ, il lisse au-delà d'environ 1,6 kHz, bien plus vite que le Soleil ne bouge.
* Lecture : 128 mesures par seconde (réglage par défaut), les 4 entrées l'une après l'autre,
  moyenne de 8 à 16 tours.

### Stratégie de suivi sur Terre : le calcul et les photodiodes ensemble

1. **Le calcul fait le gros du pointage.** Avec l'heure et la position données par le GPS du
   Heltec V4 (ou réglées à la main), l'ESP32 calcule l'azimut et la hauteur du Soleil. Le
   calcul marche le matin, sous les nuages, et permet de revenir vers l'est la nuit. Mais il
   ne connaît pas l'orientation de la tête : où est le nord, et si le trépied est de niveau.
2. **Les photodiodes corrigent l'erreur restante** dès que le Soleil est assez fort. L'ESP32
   **retient l'écart** entre les angles calculés et les angles où le capteur a centré le
   Soleil. Quand un nuage passe, le calcul seul reste juste.

### Cadence du suivi : une petite correction toutes les 2 minutes

Le panneau ne suit pas le Soleil en continu. Il le rattrape **par petites corrections**,
avec les moteurs coupés entre deux corrections :

1. **Toutes les 10 secondes**, l'ESP32 lit les 4 photodiodes et recalcule la position du
   Soleil.
2. **Tant que l'écart reste sous 0,25°**, il ne bouge pas.
3. **Dès qu'il atteint 0,25°**, il tourne l'axe concerné de **0,5°**. Le panneau se place
   ainsi 0,25° en avance : le Soleil le rattrape, le dépasse, et l'écart revient à 0,25°
   environ **2 minutes plus tard** (le Soleil avance de 15° par heure, soit 0,25° par minute).
4. Chaque axe se corrige seul, et **jamais les deux moteurs ensemble** (§ 6). La cadence varie dans la
   journée : l'élévation s'arrête presque vers midi, alors que l'azimut accélère vers midi en été.
5. Si le ciel est couvert (signal trop faible), le panneau suit la position calculée, avec
   la même règle.
6. Le soir, il revient vers l'est pour le lever du lendemain, **en un seul mouvement lent** : à
   120 demi-pas par seconde, la roue d'azimut tourne à 0,09°/s, soit **environ 35 minutes pour
   un demi-tour** (180°). C'est long, mais la nuit n'a aucune importance.

**Une correction n'est pas un à-coup.**
* 0,5°, c'est le diamètre apparent du Soleil. Cela représente environ **570 demi-pas** de moteur en
  élévation et **680 en azimut** (4076 demi-pas par tour de l'arbre, roue de 100 et 120 dents),
  d'environ 0,0009° et 0,0007° chacun.
* La correction dure **5 à 6 secondes** et glisse sans saut. Il n'y a pas de rampe : à 120 demi-pas
  par seconde, le moteur démarre sans décrocher.
* Les sorties du MCP23017 sont à 0 hors mouvement : **aucun courant dans les bobines**. Comme la vis
  sans fin bloque le moteur quand il est coupé, il repart exactement de là où il s'était arrêté.

**Pourquoi pas un suivi continu.** Il faudrait garder les moteurs alimentés en permanence :
environ 1,4 W par moteur (deux bobines à 12 V, 60 mA chacune, à 200 Ω), de quoi chauffer et ramollir
leur support en PETG, et un gaspillage pour un panneau qui produit 8 W en plein soleil. Avec la
cadence ci-dessus, les moteurs sont alimentés moins de 2 % du temps, et l'écart de pointage ne
dépasse jamais 0,25°, soit 0,001 % de puissance perdue.

**Pour une vidéo en accéléré** (time-lapse), on peut descendre le seuil à 0,05° et la
correction à 0,1° : le panneau se recale alors toutes les 25 secondes environ, et le
mouvement paraît continu à l'écran. La consommation reste de quelques dizaines de mW.

## 8. Sur un trépied

![Fond sur trépied](../../docs%20%28extra%29/explications/fond_trepied.png)

La version PETG se visse directement sur la **vis 1/4" du plateau d'un trépied**.
Le fond contient un écrou 1/4"-20 pris dans un logement hexagonal. Les câbles sortent
par le passe-câble du socle, puisque le centre est occupé par la vis. Le cas lunaire garde sa
colonne Ø50.

* **Serrer fermement** la tête sur la vis. C'est ce serrage qui empêche la tête de tourner
  sur le trépied quand le moteur d'azimut force : il lui faut environ 0,5 N·m dans un vent de 10 m/s,
  et au plus 1,2 N·m si le moteur donne tout son couple. Un serrage à la main, ferme, sur le caoutchouc du plateau,
  en tient plusieurs N·m.
* La vis du trépied doit dépasser du plateau d'au moins **4,5 mm**. Au-delà de 7 mm, elle
  dépasse simplement dans le socle, sans gêner.
* **Bloquer la rotule** du trépied (panoramique et inclinaison) et la mettre **de niveau**.
  La tête et le panneau pèsent 2,7 kg : vérifier la charge maximale du trépied.
* **Stabilité** : un trépied léger bascule bien plus tôt que le trépied du projet.
  Le calcul est fait ci-dessous pour un trépied courant.

### Le trépied modélisé : dimensions et stabilité

Les images de la démonstration montée sur ce trépied sont en tête de ce document.

L'assemblage complet est dans **`Fichiers 3D (CAO)/Cas Terrestre (démonstration)/Demo_Trepied.step`** : tête
PETG, panneau, capteur solaire et trépied, posé sur le sol en y = 0. Le trépied et le lest sont
générés par `scripts/generate_demo_trepied.py`, la tête par `scripts/generate_fourche.py`, qui
assemble le tout et fait les contrôles.

Le trépied y est modélisé simplement, à partir de deux cotes mesurées :
* le dessus du plateau est à **600 mm** du sol (sans la vis 1/4" qui dépasse) ;
* les pointes des pieds sont à **230 mm** de l'axe, au sol.

Le reste (tubes, corps, rotule) est estimé sur les photos.

**Ce que ça donne :**
* l'axe d'élévation est à **902 mm** du sol (758 mm pour l'ancienne tête à chape : il faut le
  relever pour que le panneau, long de 356 mm, passe au-dessus du plateau). Panneau vertical, son
  bord haut est à environ 1,08 m et son point le plus bas à environ 0,72 m ;
* **aucune interférence**. Ce qui tourne (tête, vis, panneau) passe à **36 mm** au plus près du
  trépied, panneau vertical (les molettes de la rotule restent en dessous) ;
* charge sur la rotule : tête et panneau font **2,65 kg**. Leur centre de gravité s'écarte
  jusqu'à 12 mm de l'axe, ce qui fait 0,3 N·m que les blocages de la rotule doivent tenir ;
* masse du trépied estimée à 0,9 kg (à peser : plus lourd, il serait un peu plus stable).

**Stabilité.** C'est le point faible : les pieds ne sont qu'à 23 cm de l'axe. Les bords du
triangle d'appui sont donc à 11,5 cm du centre, alors que l'axe est à 90 cm du sol et que le
panneau déporte son centre de gravité.

Le calcul est fait dans toutes les orientations du panneau, avec un vent perpendiculaire au
panneau (coefficient de force 1,2) et la prise au vent de la tête et des jambes.
(Le second calcul indépendant, `scripts/verification_stabilite.py`, n'a **pas** été relancé pour
cette tête.)

| Lest sous le trépied | Pente de basculement (pire orientation) | Vent de basculement (pire orientation) |
|---|---|---|
| Aucun | 8,7° | **7,5 m/s (27 km/h)** |
| Boîtier électronique seul (3 kg) | 15,4° | 10,3 m/s (37 km/h) |
| **Boîtier + 2 sacs de sable de 4 kg (11 kg)** | 28,5° | **15,3 m/s (55 km/h)** |

La tête à fourche est plus haute que l'ancienne (axe à 902 mm au lieu de 758) mais son centre de
gravité est mieux centré : le vent de basculement est pratiquement le même (27, 37 et 55 km/h contre
26, 37 et 57 km/h). **Le vent de démonstration du cahier des charges, 5 m/s (18 km/h), est
tenu même sans lest** (basculement à 7,5 m/s : un vent 2,3 fois plus fort en effort).

### Version lestée, sans toucher au trépied

| Le lest sous le trépied | Vue d'ensemble |
|---|---|
| ![Lest sous le trépied](../../docs%20%28extra%29/trepied_fourche_lest.png) | ![Sur un trépied](../../docs%20%28extra%29/trepied_fourche_iso.png) |

Sans modifier le trépied, **seul le poids compte** : le vent qui renverse l'ensemble croît
comme la racine carrée de la masse totale. **Un lest de 11 kg au lieu de 3 kg gagne 19 km/h** (38 → 57 km/h). Mettre le **panneau à plat** (élévation 90°) double environ le vent de basculement (chiffre de l'ancienne tête, **non recalculé** pour celle-ci). Les autres leviers (recentrer le centre de gravité, abaisser la tête, orienter une jambe, limiter la course) avaient été chiffrés sur l'ancienne tête : ils n'apportaient que 1 à 2 km/h, et n'ont pas été recalculés.

La tête imprimée reste donc telle qu'elle est. La version lestée ajoute seulement :

* **Le boîtier électronique posé à plat sous le trépied**, porte vers le haut, au centre :
  avec sa batterie, il pèse 3 kg. La batterie étanche accepte cette position.
* **Deux sacs de sable de 4 kg**, un de chaque côté du boîtier (environ 26 × 10 × 10 cm
  chacun). Le sable ne perce pas l'étanchéité d'un toit.
* **Une sangle à boucle de 25 mm** : un tour autour du boîtier et des deux sacs, puis autour
  du moyeu de la colonne centrale, **tendue à la main**. Le lest reste posé : il ne se balance
  pas et ne charge pas le trépied en temps normal. Il ne tire sur le trépied que si une rafale
  commence à le soulever.
* Le lest est décalé de 20 mm, à l'opposé d'une jambe, pour laisser 20 mm au verrou de cette
  jambe. Rien n'est fixé sur les jambes ni sur les pieds.

**Consignes de vent** (rafales annoncées par Météo-France ; le suivi s'arrête à 8 m/s, § 9) :

| Rafales | Quoi faire |
|---|---|
| Jusqu'à 29 km/h (8 m/s) | Fonctionnement normal : marge d'au moins ×2 sur les moteurs |
| 29 à 70 km/h | Panneau à plat, moteurs coupés ; lest de 11 kg en place |
| Plus de 70 km/h, ou toute vigilance | Rentrer le tracker |

* **À vérifier sur le vrai trépied** : la charge qu'il supporte. Une forte rafale lui fait
  porter jusqu'à 11 kg de lest en plus des 2,7 kg de la tête. Faire l'essai : soulever le
  trépied lesté par sa colonne, les verrous des jambes ne doivent pas glisser. Rentrer les
  tubes du bas à fond si possible.
* **Sur un toit** : placer l'ensemble à 2 m au moins du bord (le vent y accélère) et
  l'attacher par une longe à un point fixe, pour que rien ne puisse tomber du bâtiment.
* **Mettre le panneau à plat** dès qu'on laisse le tracker sans surveillance, la nuit et par
  ciel couvert : il ne produit rien, et il tient alors deux fois plus de vent.
* **En intérieur, sans lest** : ça tient, sur un sol à peu près plat.
* **Rotule** : serrer fermement les deux blocages (panoramique et inclinaison), mettre le
  plateau de niveau avec la bulle, et vérifier que le clip du plateau est bien verrouillé. Si
  la rotule se dévisse du trépied et que le filetage dessous est un 1/4", la tête PETG peut s'y
  visser directement : plus rigide, et 7 cm plus bas.

### Pour aller plus loin : élargir la base

Le lest ne corrige pas le vrai défaut, l'écartement des pieds (23 cm). Pour tenir davantage,
il faut fixer les trois pieds sur une **planche de 60 × 60 cm** qui porte 10 kg de lest :
l'ensemble ne bascule alors qu'à 89 km/h (103 km/h avec une planche de 80 × 80 cm) : chiffres de l'ancienne tête, **non recalculés** pour celle-ci. Cette
solution demande de sangler ou de visser les pieds du trépied sur la planche.

## 9. Couples, marges et tenue de la version PETG

Calculés par `scripts/generate_fourche.py`, avec le modèle de couples du projet (mêmes vis sans fin,
mêmes frottements, mêmes couples de vent) et la **partie qui bascule de cette tête : 1,32 kg,
centre de gravité à 9,4 mm de l'axe**, soit 0,12 N·m de pesanteur résiduelle (0,13 N·m avec le frottement). Hypothèses :
**moteur prudent de 25 mN·m**, vis et roues **graissées** (μ ≈ 0,15, rendement 0,30), roulements
**ZZ**, couple de vent du projet (0,35 N·m en élévation et 0,50 N·m en azimut à 10 m/s, variant comme
le carré de la vitesse).

| Marge = disponible / besoin | Intérieur | 6 m/s (22 km/h) | 8 m/s (29 km/h) | 10 m/s (36 km/h) |
|---|---|---|---|---|
| **Élévation** : 0,76 N·m disponibles | ×5,8 | **×3,0** | **×2,1** | **×1,6** |
| **Azimut** : 0,91 N·m disponibles | ×30,5 | ×4,4 | **×2,6** | **×1,7** |

Avec un moteur « nominal » (34,3 mN·m au lieu de 25), toutes les marges sont multipliées par 1,37.

* **Limite de suivi : 8 m/s (29 km/h).** On vise ×1,5 à ×2 pour un moteur pas à pas : c'est tenu
  jusqu'à 8 m/s sur les deux axes, et encore ×1,6 à 10 m/s. Au-delà, **garer le panneau à plat**
  (élévation 90°), où le vent pousse à peine.
* **Le moteur qui décroche ne casse rien** : il perd des pas, la vis sans fin tient le panneau,
  les dents ne voient pas plus que le couple du réducteur du 28BYJ-48 (voir plus bas). Il faut
  alors re-référencer les axes (fin de course et capteur Hall, § 6).
* **Le cas qui dimensionne est l'élévation dans le vent**, et non plus le poids du panneau.

### Ce que change le PETG en fonctionnement

* **Couples** : les vis et roues en PETG doivent être **graissées**.
  * À sec (μ ≈ 0,30), le rendement tombe de 0,30 à 0,18 : l'élévation n'a plus que ×1,7 à 6 m/s, et **moins
    de ×1 à 10 m/s** (×0,93) ; l'azimut ×2,5 à 6 m/s et environ ×1 à 10 m/s : **graisser**.
  * Ces marges sont celles des roulements **ZZ**. Avec des 2RS, les joints freinent : environ
    0,008 N·m pour la paire de 685 (à retirer du couple du moteur, soit le quart de celui-ci) et
    environ 0,15 N·m pour la paire de 6806 (à retirer à la roue d'azimut). À 10 m/s, la marge
    tomberait à environ ×1,1 en élévation et **environ ×0,9 en azimut** (le moteur ne suit plus) ; à
    8 m/s, ×1,5 et ×1,3.
* **Tenue moteurs coupés** : les deux vis sont **irréversibles** : angle de frottement d'environ
  8,5° (PETG graissé, μ ≈ 0,15) contre 3,8° pour la pente du filet. Le panneau ne descend pas tout seul,
  même avec des vibrations.
* **Dents en PETG** : au couple maximal que le moteur peut donner à la roue (environ 1 N·m en
  élévation, 1,2 N·m en azimut, moteur nominal), l'effort sur une dent est d'environ **25 N**, soit
  une contrainte d'environ **7 MPa** en pied de dent (même méthode que pour la variante 28BYJ-48 : 6 à
  8 MPa pour 27 N), à comparer à environ 50 MPa de résistance du PETG. **Les dents ne sont plus
  le maillon faible** : le réducteur en plastique du 28BYJ-48 lâche bien avant elles.
* **Chemin du couple de l'élévation** (ordres de grandeur, à confirmer par un essai au montage) :
  la roue transmet son couple à la tige par une **vis de pression sur un méplat** (M3, rayon de la
  tige 4 mm : environ 250 N pour 1 N·m), puis la tige le transmet à la ferrure par **sa propre vis de
  pression** (et la colle si on en met : elle est facultative, pour rester démontable), puis la
  ferrure au cadre par **4 vis M3** dans la paroi de 1,5 mm (environ 17 N par vis, 3 MPa d'appui
  sur l'aluminium). Les **maillons à surveiller sont les deux vis de pression sur la tige** : limer
  un vrai méplat et les freiner (Loctite 243, facultatif).
* **Tiges et roulements** : le panneau pèse 1,2 kg, soit 12 N répartis sur deux roulements 608
  dont la charge admissible dépasse le kilonewton : sans enjeu. Les bras sont hauts (225 mm) et
  minces (9 mm) : estimation par un calcul de poutre, à confirmer par la simulation demandée par le
  cahier des charges : en flexion dans leur plan (efforts du vent), environ 0,01 mm à 5 m/s ; hors
  plan (réaction de la vis sans fin, environ 6 N), de l'ordre de 0,1 mm en tête.
* **Énergie** : alimenté, un 28BYJ-48 consomme environ 1,4 W (deux bobines à 12 V et 200 Ω ; en demi-pas, 1,1 W en moyenne). Les
  sorties du MCP23017 sont à 0 entre deux corrections : moins de 20 mW en moyenne.
* **Fluage** : sous une charge permanente, le PETG se déforme lentement. Le panneau étant équilibré,
  la denture n'est presque pas chargée au repos : garer à plat reste conseillé entre deux
  démonstrations, surtout pour le vent.

### À valider avant de commander et d'imprimer

1. **Mesurer le couple réel de chaque 28BYJ-48**, avant tout montage : arbre horizontal, un bras de
   100 mm fixé sur l'arbre, une masse accrochée au bout. À 12 V et 120 phases/s, le moteur doit lever
   **25 g** (prudent) et idéalement **35 g** (nominal) sans perdre de pas. S'il n'y arrive pas, le
   changer : ils sont très dispersés.
2. **Mesurer le moteur reçu** avant d'imprimer les supports : arbre (10 mm au-dessus de la
   face, méplats de 3 mm), bossage (Ø9 × 1,5 mm), décentrage de 8 mm, entraxe des oreilles (35 mm),
   trous Ø4,2. Les supports sont modélisés sur ces cotes ; une différence de 0,5 mm se rattrape au
   lamage, pas davantage.
3. **Vérifier l'équilibre** du panneau monté (§ 5, « Équilibrage ») et le couple à la roue : accrocher
   une masse de 300 g à 100 mm de l'axe d'élévation (0,29 N·m) : le moteur doit encore faire tourner la roue.
4. **Tester la fréquence maximale** : monter peu à peu de 120 à 300 phases/s. Le couple baisse avec la
   fréquence : si le moteur décroche à 200, ne pas aller au-delà de 120.
5. **Le couple de vent est celui de la géométrie précédente** (0,35 et 0,50 N·m à 10 m/s) : avec le
   pivot au centre du panneau, il est sans doute un peu plus faible en élévation, mais les bras ajoutent
   de la prise au vent. **À mesurer** avant de compter sur la marge de ×1,6 à 10 m/s.
6. **Contrôler les ferrures et les semelles des bras à l'impression** : les trous d'insert horizontaux des semelles
   des bras sont le point à regarder en premier (§ 2 et § 4). `scripts/verifier_inserts.py` n'a pas été adapté à
   la fourche : la prise des vis est vérifiée par `scripts/generate_fourche.py`.

### Conformité au cahier des charges L3 (partie Matière)

| Exigence | État de cette tête |
|---|---|
| Structure ≤ 350 × 350 × 350 mm (panneau hors enveloppe) | ✅ **344 × 139 × 343 mm** mesuré sur la CAO (§ 1) |
| Chaîne embase → azimut → fourche → élévation → cadre ; axe d'élévation au plus près du centre de gravité | ✅ Fourche étroite, centre de gravité à 9 mm de l'axe |
| Réduction pour le 28BYJ-48, maintien moteur coupé | ✅ Vis sans fin irréversibles, marge ≥ ×2 jusqu'à 8 m/s (calcul) |
| Élévation 15° à 90°, azimut ≥ 180° | ✅ CAO contrôlée de 5° à 92° d'élévation ; azimut ±180° géré par le logiciel. **Butées mécaniques et fins de course : non modélisées** |
| Vent de démonstration 5 m/s | ✅ Moteurs : marge ×3 ou plus. Trépied : basculement à 27 km/h sans lest |
| Montage symétrique en élévation | ✅ Un 608 par bras |
| Matériau PETG ou ASA ; pas de PLA | ✅ PETG |
| Pièces FDM ≤ 200 × 200 × 200 mm, parois ≥ 1,6 mm | ⚠️ Parois vérifiées, toutes les pièces ≤ 200 mm **sauf les deux bras (225 mm de haut)** : ils sont à **découper en deux** (découpage justifié) ou à faire valider |
| Démontable : vis, inserts, pas de collage irréversible | ✅ Colle facultative sur les tiges ; **photodiodes collées à la colle chaude** |
| Roulement d'azimut 6202 recommandé | ⚠️ Deux 6806 (30 × 42 × 7) : à justifier par le calcul |
| Composants du commerce pris dans le kit du FabLab | ⚠️ Le **plateau d'aluminium** (328 mm) et les **tiges d'acier Ø8** n'en font pas partie |
| Interfaces : aimants AS5600, 4 LDR, batterie dans l'embase | ❌ Non faites : micro-rupteur et capteur Hall, photodiodes BPW34, batterie dans un boîtier sous le trépied |
| Livrables : plans ISO 128 / 1101, simulation SolidWorks (SF ≥ 2), contrôle dimensionnel, fiches d'interface, maquette testée | ❌ Non faits. Coaxialité ≤ 0,2 mm des deux 608 : les bras sont repérés par des vis dans des trous de 3,5 mm, **sans pion de positionnement** |

## 10. Fichiers de ce dossier et du boîtier électronique

| Fichier | Contenu |
|---|---|
| `Fichiers 3D (CAO)/Cas Terrestre (démonstration)/a_imprimer/*.stl` (et `.step`) | Les 18 pièces à imprimer (16 pour la tête, 2 pour le capteur solaire), déjà orientées et posées sur le plateau |
| `Fichiers 3D (CAO)/Cas Terrestre (démonstration)/pieces_metal/` | `Plateau_Alu.dxf` et `.step` : le plateau d'aluminium de 5 mm à découper (328 × 138 mm) |
| `Fichiers 3D (CAO)/Cas Terrestre (démonstration)/Tete_Rotative_Fourche.step` | L'assemblage de la tête (avec roulements, tiges, arbres Ø5, moteurs, inserts et toute la visserie), pour vérifier le montage |
| `Fichiers 3D (CAO)/Cas Terrestre (démonstration)/Eprouvette_Ajustements.stl` | Éprouvette à imprimer en premier pour régler les ajustements sur ton imprimante (§ 4) |
| `Fichiers 3D (CAO)/Cas Terrestre (démonstration)/Demo_Trepied.step` | La démonstration complète sur un trépied : tête PETG, panneau, capteur solaire, trépied et lest (§ 8) |
| `scripts/generate_fourche.py` | **Génère tout ce qui précède** (CAO, STEP, STL, DXF) et fait les contrôles : interférences, prise des vis, garde, couples et marges, stabilité |
| `scripts/render_fourche.py` | Les images de ce document (`docs (extra)/fourche_*.png` et `trepied_fourche_*.png`) |
| **[`Electronique/Schema_Electrique.qet`](../../Electronique/Schema_Electrique.qet)** | Schéma électrique, projet QElectroTech, **version NEMA / TMC2209 : à redessiner pour les 28BYJ-48** (§ 6) |
| [`Electronique/Schema_Electrique.pdf`](../../Electronique/Schema_Electrique.pdf) | Le même schéma en PDF, à imprimer en A3 ; images dans `docs (extra)/electronique/` |
| **[`Electronique/Implantation_Boitier.fzz`](../../Electronique/Implantation_Boitier.fzz)** | Implantation du boîtier électronique dans Fritzing, **version NEMA / TMC2209** (§ 6) |
| **[`Liste-composants.md`](../../Liste-composants.md)** | **Liste des composants** de la démonstration sur Terre : roulements, accouplements, tiges, moteurs, électronique, visserie, consommables, avec les noms à chercher et les quantités |
| `docs (extra)/explications/*.png` | Images annotées pour le montage : palier d'une vis sans fin, vis sans fin imprimée, fond sur trépied, capteur solaire (vue et coupe) |

Arborescence de l'assemblage de la tête dans SolidWorks : celle du cas lunaire
([README du cas lunaire](../Cas%20Lunaire/README.md), § 10), avec en plus le sous-ensemble
`SA_Panneau` (panneau, ferrures, tiges et roue d'élévation) qui tourne autour de l'axe
d'élévation.

Régénération, depuis la racine du dépôt :

```
python scripts/generate_fourche.py                 # CAO, STEP, STL, DXF, contrôles, tête sur le trépied
xvfb-run -a python scripts/render_fourche.py       # images
```

## 11. Questions pièges et leurs réponses

Les questions qu'on peut nous poser pour nous faire dire une erreur sur le cas terrestre, avec
la réponse courte et l'endroit où elle est détaillée.

### Moteurs et structure

| Question piège | Réponse |
|---|---|
| « Pourquoi des 28BYJ-48, si faibles ? » | **Ils sont imposés.** Ils donnent 34 mN·m (25 en valeur prudente) contre 340 pour un NEMA 17. On a donc redessiné la tête pour qu'ils suffisent (§ 1). |
| « Pourquoi une fourche et pas un contrepoids ? » | **Un contrepoids ajoute 0,9 kg et ne laisse que ×1,3 de marge à 10 m/s.** La fourche met l'axe dans le plan médian du panneau : le centre de gravité tombe à 9 mm de l'axe, sans masse en plus, et la marge à 10 m/s est de ×1,6 (§ 1 et § 9). La variante à contrepoids est dans le document caché [Variante 28BYJ-48](../../.variante_28BYJ-48/README.md). |
| « Les 28BYJ-48 suffisent-ils vraiment ? » | **Oui, jusqu'à 8 m/s (29 km/h), avec une marge d'au moins ×2,** moteur prudent, vis graissées. Au-delà, le panneau se gare à plat (§ 9). **Et à condition de tester chaque moteur :** ils sont très dispersés. |
| « Que se passe-t-il si le moteur décroche dans une rafale ? » | **Rien de grave** : il perd des pas, la vis sans fin tient le panneau, les dents ne voient jamais plus que le couple du réducteur du 28BYJ-48. Il faut re-référencer les axes (§ 9). |
| « Pourquoi ne pas piloter les moteurs directement par le Heltec ? » | **Il n'a que 9 broches libres** et il en faut 8 pour les moteurs en plus du reste. Un MCP23017 sur l'I²C les remplace (§ 6). |
| « Pourquoi une plaque d'aluminium dans un modèle tout imprimé ? » | **Elle porte les deux bras sur 328 mm** : en PETG elle fléchirait et ne tiendrait pas sur beaucoup d'imprimantes. C'est, avec les tiges, les roulements et la visserie, ce qu'on ne peut pas imprimer (§ 2). |
| « Pourquoi des tiges d'acier et pas des pivots imprimés ? » | **Les 608 demandent un axe Ø8 rectifié** : une tige imprimée n'aurait ni ce diamètre ni cet état de surface. L'acier encaisse sans souci le poids du panneau et le couple de la roue (§ 9). Les ferrures, elles, sont imprimées. |
| « Tout cela est-il vérifié ? » | **En CAO oui** (interférences, prises de vis, garde, marges, stabilité) ; **rien n'est mesuré sur une pièce réelle**. Les points à valider avant impression sont au § 9. |

### Matériaux et impression 3D

| Question piège | Réponse |
|---|---|
| « Pourquoi du PETG et pas du PLA, plus facile à imprimer ? » | **Le PLA se ramollit vers 60 °C** : au soleil de La Réunion, une pièce sombre dépasse cette température. Le PETG tient jusqu'à environ 80 °C, il casse moins net et il supporte mieux l'humidité (§ 2). |
| « Donc le PETG tient au soleil sans limite ? » | **Non.** Il faut une teinte claire : un PETG noir en plein soleil d'été approche sa température de ramollissement. Seul le boîtier du capteur solaire est noir, et il ne porte aucune charge. Les UV font aussi vieillir le PETG : c'est une démonstration, pas une installation permanente (§ 2 et § 7). |
| « Des engrenages en plastique, c'est solide ? » | **Oui, parce que le moteur est faible.** Au couple maximal du 28BYJ-48, une dent travaille à environ 7 MPa pour environ 50 MPa de résistance : le réducteur du moteur lâche avant (§ 9). |
| « Une pièce imprimée sort aux cotes du dessin ? » | **Non.** Les trous sortent trop petits et le haut d'un trou horizontal s'affaisse. D'où les jeux d'ajustement (+0,15 mm sur les logements de roulements), les trous en goutte, et l'éprouvette à imprimer en premier (§ 4). |
| « Peu importe le sens d'impression d'un bras ? » | **Non.** Les bras et les ferrures s'impriment couchés sur leur face intérieure : les efforts sont alors dans le plan des couches et jamais perpendiculaires à elles (§ 2). |
| « Vous imprimez tout à 100 % de remplissage pour que ce soit solide ? » | **Non.** La résistance vient surtout des parois : 4 périmètres et 40 % de remplissage suffisent. Seuls les vis sans fin, les roues et les ferrures sont pleins (§ 2). |
| « Vous vissez directement dans le plastique ? » | **Non**, sauf deux petites vis sans tête : toutes les autres se vissent dans des **inserts filetés en laiton, posés à chaud** (32 au total, § 4). Le filet est en laiton, donc on démonte autant qu'on veut ; chaque insert est entouré de 1,6 mm de plastique au moins. |
| « Le plastique garde sa forme sous charge ? » | **Non, il flue** : sous une charge permanente, il se déforme lentement. Le panneau est équilibré, donc la denture est peu chargée ; on gare le panneau à plat entre deux démonstrations (§ 9). |

### Lubrification

| Question piège | Réponse |
|---|---|
| « Vous lubrifiez au MoS₂, comme sur la Lune ? » | **Non : sur Terre, une graisse suffit.** On prend une graisse PTFE, prévue pour les plastiques (§ 1). |
| « Graisser les vis sans fin, c'est facultatif ? » | **Non, c'est obligatoire.** À sec, le rendement tombe de 0,30 à 0,18 : la marge d'élévation passe sous ×1 à 10 m/s (§ 9). |
| « Si vous graissez, le frottement baisse : la vis n'est plus irréversible ? » | **Elle le reste.** PETG graissé : angle de frottement d'environ 8,5°, plus du double de la pente du filet (3,8°). Le panneau tient moteurs coupés, même avec des vibrations (§ 9). |
| « Il faut aussi graisser les roulements ? » | **Non.** Les roulements ZZ sont graissés à vie : on ne les ouvre pas (§ 3). |
| « ZZ ou 2RS, c'est pareil ? » | **Non, et avec des moteurs si faibles, c'est important.** Les joints des 2RS frottent : à 10 m/s, la marge de l'azimut passe sous ×1 (environ ×0,9) et celle de l'élévation à environ ×1,1 (§ 3 et § 9). |

### Mécanique, vent et stabilité

| Question piège | Réponse |
|---|---|
| « La vis sans fin bloque le panneau : il ne risque donc rien dans le vent ? » | **Le panneau ne tourne pas, mais l'ensemble peut se renverser.** Les pieds du trépied ne sont qu'à 23 cm de l'axe : sans lest, il bascule à 28 km/h (§ 8). |
| « Il suffit de l'alourdir un peu ? » | **Il en faut beaucoup.** Le vent de basculement croît comme la racine carrée de la masse : 38 km/h avec 3 kg de lest, 57 km/h avec 11 kg. D'où les consignes : à plat au-dessus de 29 km/h, rentré au-dessus de 70 km/h (§ 8). |
| « Un moteur pas à pas tient sa position : pourquoi le couper ? » | **Le maintenir alimenté coûterait environ 1 W par moteur** et chaufferait leur support en PETG. Les vis tiennent le panneau gratuitement (§ 6 et § 7). |
| « En coupant les moteurs, vous perdez la position ? » | **Non.** La vis bloque le moteur : il repart d'où il s'est arrêté, à un demi-pas près (moins de 0,001° au panneau). |
| « Sans codeur, comment savez-vous où est le panneau ? » | Par le **comptage des demi-pas** depuis deux origines : un micro-rupteur en élévation, un capteur Hall en azimut. Les marges de couple évitent les pas perdus, et les photodiodes corrigent sur la vraie cible, le Soleil (§ 6 et § 7). |
| « On peut bouger le panneau à la main pour le régler ? » | **Jamais.** On forcerait sur les dents en PETG et sur le réducteur du moteur. On alimente le moteur, ou on tourne l'arbre de la vis. |
| « Votre tête est imprimée, donc elle tiendrait aussi sur la Lune ? » | **Non.** La démonstration valide la cinématique, la commande et le suivi, pas les matériaux (voir le README du cas lunaire, § 11). |

### Énergie et électronique

| Question piège | Réponse |
|---|---|
| « Votre panneau de 10 W produit 10 W ? » | **Non.** 10 W est une puissance de crête, à 25 °C sous 1000 W/m². Avec le régulateur PWM, le panneau travaille à la tension de la batterie (environ 13 V) : il donne environ 8 W en plein soleil, et environ 30 Wh par jour de beau temps (§ 6). |
| « Le suivi deux axes rapporte donc plus d'énergie qu'il n'en coûte ? » | **Pas sur un panneau aussi petit.** Un suivi deux axes rapporte de l'ordre de 30 % de plus qu'un panneau fixe, soit une dizaine de Wh par jour ici. Or l'électronique, surtout la carte Heltec, consomme 5 à 20 Wh par jour. C'est un démonstrateur : le principe devient rentable sur de grands panneaux (§ 6, à confirmer avec les deux wattmètres). |
| « Une erreur de pointage de 5° fait perdre 5 % ? » | **Non : 0,4 %.** La perte suit le cosinus de l'erreur. À 1°, elle n'est que de 0,015 %. Le suivi à 0,25° près sert à éviter que le panneau oscille, pas à gagner de la puissance (README principal, § 4). |
| « Pourquoi un régulateur PWM et pas un MPPT ? » | Un MPPT tirerait environ 10 W au lieu de 8. Le PWM est plus simple et moins cher ; on accepte de perdre 20 % (§ 6). |
| « Une batterie au lithium serait mieux ? » | **Pas avec ce régulateur** : le SOL10UC3 ne charge que le plomb, le gel et l'EFB (§ 6). |
| « Le fusible protège la batterie ? » | **Il protège le fil qui le suit.** Il est donc au plus près de la source : à moins de 10 cm du + de la batterie (§ 6). |
| « Tous les moins sont reliés ensemble ? » | **Pas celui du panneau.** Il va seulement au régulateur, qui peut couper le −. Le 0 V du boîtier vient de la sortie LOAD (§ 6). |
| « L'ESP32 supporte le 5 V du capteur Hall ? » | **Non, ses broches s'arrêtent à 3,3 V.** Le capteur est alimenté en 5 V, mais sa sortie à collecteur ouvert est tirée au 3,3 V. D'où un A3144 nu, et pas un module qui tire sa sortie au 5 V (§ 6). |
| « Vous pouvez émettre en LoRa en continu ? » | **Non.** Dans la bande 868 MHz, on n'occupe le canal que 1 % du temps : un message de 38 octets par minute en SF9 (§ 6). |
| « Le capteur solaire marche par temps couvert ? » | **Non.** Quand le signal est trop faible, le tracker suit la position calculée du Soleil (§ 7). |
| « À La Réunion, le Soleil est au sud à midi ? » | **Non, au nord presque toute l'année** (21° de latitude sud). En été austral, il passe presque au zénith : l'azimut doit alors tourner vite, mais un retard coûte très peu (bibliographie du README principal). |
| « IP65, donc le boîtier peut aller sous l'eau ? » | **Non.** IP65 veut dire étanche à la poussière et aux jets d'eau, pas à l'immersion. L'aérateur à membrane évite la condensation (§ 6). |
