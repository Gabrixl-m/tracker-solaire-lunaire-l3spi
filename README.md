# Tracker solaire lunaire deux axes — maquette 3D à l'échelle 1:1

Maquette CAO d'un tracker solaire destiné à la surface de la Lune. Elle comprend :
* un trépied déployable ;
* une **tête rotative à vis sans fin** (azimut + élévation, deux petits moteurs pas à pas
  pilotés par un ESP32) ;
* **le panneau photovoltaïque de 356 × 253 × 30 mm** ;
* un faisceau de câbles et une unité de contrôle posée au sol.

Les deux vis sans fin sont **irréversibles** : la tête tient le panneau dans toutes les
positions **moteurs coupés**, sans contrepoids, sur Terre comme sur la Lune.
Toutes les cotes sont en **millimètres, à taille réelle**.

| Vue d'ensemble (panneau à 40°) | Tête rotative à vis sans fin |
|---|---|
| ![Vue d'ensemble](docs/apercu_latitudemoyenne_iso.png) | ![Tête à vis sans fin](docs/apercu_latitudemoyenne_detail_tete.png) |
| ![Pôle Sud](docs/apercu_polesud_detail_tete_avant.png) | ![Pied et vis d'ancrage](docs/apercu_latitudemoyenne_detail_pied.png) |

---

## 1. Fichiers

| Fichier | Contenu |
|---|---|
| **`CAO/Cas_Reel/`** | **Cas réel** (Lune), cotes nominales : |
| `CAO/Cas_Reel/Tracker_Lunaire_PoleSud.step` | **Assemblage principal** : pose de fonctionnement au pôle Sud (site Artemis), Soleil à +1,5°, panneau quasi vertical |
| `CAO/Cas_Reel/Tracker_Lunaire_LatitudeMoyenne.step` | Même assemblage, pose « sites Apollo » : Soleil à 50°, panneau incliné à 40° |
| `CAO/Cas_Reel/Tete_Rotative_VisSansFin.step` | La tête rotative seule, avec le haut de la colonne et le panneau monté à 40° |
| `CAO/Cas_Reel/pieces/*.step` | Toutes les pièces seules (trépied, tête, panneau, unité au sol), chacune dans son repère de construction |
| **`CAO/Demo_Terre_PETG/`** | **Démonstration sur Terre**, tête imprimée en 3D en PETG, avec les jeux d'ajustement (voir § 12) : |
| `CAO/Demo_Terre_PETG/a_imprimer/*.stl` (et `.step`) | Les 16 pièces à imprimer, déjà orientées et posées sur le plateau |
| `CAO/Demo_Terre_PETG/Tete_Rotative_PETG.step` | L'assemblage de la tête imprimée (avec roulements, arbres Ø5, moteurs et vis), pour vérifier le montage |
| `CAO/Demo_Terre_PETG/Eprouvette_Ajustements.stl` | Éprouvette à imprimer en premier pour régler les ajustements sur ton imprimante |
| `docs/bilan_masse.csv` | Bilan de masse pièce par pièce (séparateur `;`, s'ouvre dans Excel) |
| `docs/apercu_*.png`, `docs/tete_vis_sans_fin_*.png` | Rendus du tracker (iso, face, profil, arrière, détails) et de la tête seule (dont deux coupes) |
| **`LISTE_ACHATS.md`** | **Liste d'achats** de la démonstration sur Terre : roulements, accouplements, arbres Ø5 des vis sans fin, moteurs, électronique, visserie, consommables, avec les noms à chercher et les quantités |
| `docs/explications/*.png` | Images annotées pour le montage : palier d'une vis sans fin (joues, roulements, arbre), vis sans fin imprimée (filet, moyeux, vis de blocage) et axe d'élévation imprimé (pivots, roulements 6801, roue) |
| `docs/optimisation_angle_jambes.md` | Optimisation de l'angle φ des jambes : exigences, résultats angle par angle, sensibilité |
| `generate_tracker.py` | Script paramétrique qui génère toute la CAO, le bilan de masse et les contrôles |
| `generate_tete_vis_sans_fin.py` | Exporte la tête seule, cale les vis, calcule les couples et la tenue moteurs coupés |
| `optimisation_angle.py` | Calcule l'angle φ optimal des jambes à partir des masses de la CAO |
| `render_apercu.py`, `render_tete_vis_sans_fin.py`, `render_explications.py` | Génèrent les rendus PNG et les images annotées |

### Ouvrir dans SolidWorks

Un fichier SolidWorks natif (`.SLDASM` / `.SLDPRT`) ne peut être écrit que par SolidWorks
lui-même. Le format STEP AP214 fourni s'ouvre directement comme un assemblage complet,
avec les noms des pièces, les sous-assemblages et les couleurs.

1. **Fichier › Ouvrir**, type *STEP AP203/214/242 (\*.step; \*.stp)*, puis choisir
   `CAO/Cas_Reel/Tracker_Lunaire_PoleSud.step`.
2. Si SolidWorks demande un modèle de document, prendre l'assemblage et la pièce **en mm**.
3. **Fichier › Enregistrer sous › Assemblage (\*.sldasm)**. Au premier enregistrement,
   SolidWorks crée les fichiers `.SLDPRT` de chaque pièce.
   Pour tout regrouper dans un dossier, utiliser **Fichier › Pack and Go**.

Repère : **Y vertical**, c'est-à-dire que le plan de dessus de SolidWorks correspond au sol.
* L'origine est au sol, sur l'axe d'azimut (**axe Y**).
* L'axe d'élévation est horizontal (**axe X** dans la pose de référence), à Y = 700 mm.
  Le sommet de la colonne, sur lequel repose la tête, est à Y = 544 mm.
* Les pièces arrivent fixes, sans contraintes. Pour animer le tracker :
  * libérer `SA_Tete_Orientable` et ajouter une contrainte coaxiale entre le moyeu de la `Chape` et les `Roulement_6806` ;
  * libérer `SA_Panneau` et ajouter une contrainte coaxiale entre les pivots (`Pivot_Entraine`, `Pivot_Libre`) et les `Roulement_608` (`Roulement_6801` dans la version PETG) ;
  * ajouter des contraintes d'engrenage entre `Vis_Azimut` et `Roue_Azimut_Fixe` (rapport 1:60), puis entre `Vis_Elevation` et `Roue_Elevation` (1:50).

Arborescence :

```
Tracker_Lunaire_PoleSud
├── SA_Trepied            colonne, colliers, 3 × Jambe_n, 3 × entretoises, 3 × patins, 3 × vis d'ancrage
├── SA_Tete_Fixe          fond et socle Ø62, 2 roulements 6806, roue d'azimut fixe (bronze)
├── SA_Tete_Orientable    chape en U (jaune), vis + moteur d'azimut, vis + moteur d'élévation,
│   │                     paliers, accouplements, roulements                                  ← tourne en azimut (Y)
│   └── SA_Panneau        chapeau en U renversé (bleu), pivots, roue d'élévation (bronze),
│                         2 rails, cadre, laminé, cellules, boîte de jonction                 ← tourne en élévation (X)
├── SA_Unite_Sol          unité de contrôle / batterie + radiateur
└── SA_Faisceau           faisceau de câbles
```

---

## 2. Tête rotative à vis sans fin

| Tête seule | Coupe : vis et roue d'élévation |
|---|---|
| ![Tête seule](docs/tete_vis_sans_fin_iso.png) | ![Coupe élévation](docs/tete_vis_sans_fin_coupe_elevation.png) |
| ![Côté moteurs](docs/tete_vis_sans_fin_cote_moteurs.png) | ![Coupe azimut](docs/tete_vis_sans_fin_coupe_azimut.png) |
| ![Avec panneau, côté moteurs](docs/tete_vis_sans_fin_avec_panneau.png) | ![Avec panneau, côté cellules](docs/tete_vis_sans_fin_avec_panneau_face.png) |

| Coupe par les axes (cas réel) : roulements en rose (6806 dans le socle, 608 dans les bras) |
|---|
| ![Coupe des roulements](docs/tete_vis_sans_fin_coupe_roulements.png) |

### Architecture

| Élément | Choix |
|---|---|
| **Socle** (brun) | Cylindre Ø62 posé sur la colonne du trépied, centré dedans par le fond et bloqué en rotation par une vis M3 radiale à travers la colonne. Il porte deux **roulements 6806** (Ø30/Ø42 × 7) et la **roue d'azimut, fixe**, posée à plat sur le socle et tenue par 3 vis M3 fraisées affleurantes, sous le passage de la vis d'azimut. Un passe-câble est orienté vers l'unité au sol |
| **Chape en U** (jaune) | Tourne en azimut sur les deux 6806. Sa plaque porte les **deux moteurs** et les deux vis. Ses bras portent les roulements de l'axe d'élévation (608 ; 6801 en version imprimée), à 156 mm au-dessus de la colonne (700 mm du sol) |
| **Chapeau en U renversé** (bleu) | Coiffe la chape. Il pivote sur deux pivots dans les roulements des bras et porte les deux rails du panneau. Cas réel : axes inox Ø8 sur 608. Démonstration : pivots **imprimés en PETG, Ø12**, sur 6801 (§ 12). Un **bossage** sur chaque flanc appuie sur la bague intérieure du roulement et règle le jeu axial |
| **Azimut (axe Y)** | **NEMA 11 de 45 mm** + vis sans fin m0,8 Ø12 sur la **roue bronze Z60 fixée sur le socle** : **60:1**. La vis roule autour de la roue, comme sur une tourelle. Le moteur tourne donc avec le panneau et ne se trouve jamais sur son chemin |
| **Élévation (axe X)** | **NEMA 17 de 34 mm** + vis sans fin m1 Ø16 sur la **roue bronze Z50** calée sur le pivot gauche du chapeau : **50:1**. Le moteur est à l'arrière de la chape, du côté opposé au panneau |
| **Vis** | Chaque vis tourne sur son arbre Ø5, porté par deux roulements 685. Ses deux moyeux appuient sur les bagues intérieures des 685, et une **lèvre** de chaque joue du palier retient leur bague extérieure : la poussée axiale de la vis va au palier. Un accouplement flexible la relie au moteur, si bien que le moteur ne reçoit pas cette poussée |
| **Liaison au panneau** | Deux rails 12 × 13 vissés sur le dessus du chapeau et sur l'aile arrière du cadre. Le dos du cadre est à 46 mm de l'axe d'élévation |
| **Passage des câbles** | Les câbles descendent par le moyeu creux de la chape, font une boucle dans le socle et sortent par le passe-câble |
| **Fixations** | Vis CHC M3 (M2,5 pour le NEMA 11), toutes modélisées. Chaque tête de vis est accessible, et aucune n'est sur le passage d'une pièce mobile. Le palier et le support du moteur d'azimut sont vissés à travers des **lumières** de la chape : on règle l'engrènement de la vis d'azimut en les faisant glisser |

### Roulements (en rose dans les fichiers 3D et les aperçus)

Tous les roulements sont **protégés** des deux côtés : flasques métalliques (**ZZ**,
conseillé) ou joints caoutchouc (**2RS**). Leurs cotes sont celles des roulements ouverts,
sauf pour le 685. Dans les fichiers 3D, la protection est l'anneau en retrait de 0,2 mm sur
chaque face.

| Réf. | Dimensions (Ø int. × Ø ext. × largeur) | Qté | Emplacement |
|---|---|---|---|
| **6806** (ISO 61806) | 30 × 42 × 7 mm | 2 | Azimut : dans le socle, autour du moyeu de la chape |
| **608** | 8 × 22 × 7 mm | 2 | Élévation, **cas réel** : dans les bras de la chape, sur les axes Ø8 du chapeau |
| **6801** (ISO 61801) | 12 × 21 × 5 mm | 2 | Élévation, **démonstration PETG** : remplace les 608, sur les pivots imprimés Ø12 |
| **685ZZ** ou **685-2RS** | 5 × 11 × 5 mm | 4 | Arbres des deux vis sans fin, deux par vis, dans les paliers |

**Aucune pièce ne touche la protection.** Une pièce qui tourne avec l'arbre n'appuie que sur la
bague intérieure, et une pièce fixe que sur la bague extérieure. Sinon, une pièce frotterait
sur la flasque ou sur le joint, ou bien une pièce fixe freinerait la bague qui tourne.

| Roulement | Appui sur la bague intérieure (Ø maxi) | Appui sur la bague extérieure (Ø mini) |
|---|---|---|
| 6806 (azimut) | Collerette du moyeu et rondelle d'arrêt : **Ø33** | Épaulement du socle entre les deux roulements, et dessous de la roue d'azimut : alésage **Ø40** |
| 608 / 6801 (élévation) | Bossage de chaque flanc du chapeau : **Ø11,5 / Ø14,2**, à 0,1 / 0,25 mm de la bague | Épaulement du bras de la chape : alésage **Ø19,8 / Ø19,5** |
| 685 (vis) | Épaulement de chaque moyeu de la vis : **Ø6,5**, à 0,15 mm de la bague | Lèvre de 1 mm de chaque joue du palier : alésage **Ø9,8** |

`generate_tete_vis_sans_fin.py` le vérifie à chaque génération, pour les deux versions. Il
contrôle les deux faces de chaque roulement : rien à moins de 0,3 mm de la protection, et
chaque bague n'est approchée que par ce qui tourne avec elle.

* **685** : prendre une version **protégée, ZZ ou 2RS**. Le 685 ouvert ne fait que 3 mm de
  large, alors que les paliers sont prévus pour 5 mm.
* **Démonstration sur Terre** : roulements acier standard, de préférence **ZZ**. Ils sont
  graissés à vie d'origine : ne pas les ouvrir ni les regraisser.
  * Les joints des 2RS frottent sur la bague intérieure. Les deux 6806-2RS freinent
    l'azimut d'environ 0,15 N·m (estimation), soit le tiers du couple du vent de 10 m/s.
  * Avec des 2RS, la marge de l'azimut au vent passe de ×2,3 à ×1,6 (vis graissée), et
    au-dessous de ×1 si la vis tourne à sec.
  * L'élévation n'est presque pas touchée : ×2,5 → ×2,3.
* **Montage** : enfoncer un roulement en poussant sur la bague qu'on emmanche. Dans un
  logement, c'est la bague extérieure : utiliser une douille de son diamètre, jamais un
  outil posé sur la flasque.
* **Cas réel (Lune)** : mêmes dimensions, en acier 440C, version **ZZ**. Les flasques
  métalliques arrêtent la poussière de régolithe sans frotter. La lubrification est sèche
  (MoS₂) : ni joint caoutchouc ni graisse, qui dégazeraient dans le vide.

**Pourquoi une vis sans fin.** Sans contrepoids, le panneau est forcément décentré : il doit
passer devant la chape pour devenir vertical. Son poids crée donc un couple sur l'axe
d'élévation, jusqu'à 0,8 N·m sur Terre. La vis sans fin est **irréversible** :
* le moteur fait tourner la roue ;
* la roue ne peut pas faire tourner la vis, parce que la pente du filet (3,6°) est plus
  faible que l'angle de frottement (environ 6°). C'est le principe du cric de voiture à vis.

Le panneau tient donc seul dans toutes les positions, même dans le vent et même en cas de
coupure de courant. Les moteurs ne sont alimentés que pendant les mouvements.

### Moteurs

| Axe | Moteur | Caractéristiques |
|---|---|---|
| Élévation | **NEMA 17, 42 × 42 × 34 mm** (type 17HS3401) | 0,28 N·m, 1,3 A, 2,4 Ω, 0,22 kg |
| Azimut | **NEMA 11, 28 × 28 × 45 mm** (type 11HS18-0674S) | 0,095–0,10 N·m, 0,67 A, 6,9 Ω, 0,14 kg |

À l'achat, prendre un NEMA 17 de 34 mm annoncé à **0,28 N·m**. Certains vendeurs vendent sous
la même référence une version à 0,23–0,25 N·m, qui ferait perdre 10 à 20 % de marge.

### Couples : besoins et marges dans tous les cas

Les besoins sont calculés par `generate_tete_vis_sans_fin.py` à partir de la CAO :
* partie basculante (chapeau, roue, rails, panneau) : 1,51 kg, dont 1,01 kg de panneau ;
* centre de gravité à 53,5 mm de l'axe, puisqu'il n'y a pas de contrepoids ;
* couple de gravité maximal (panneau vertical) : 0,79 N·m sur Terre et 0,13 N·m sur la Lune ;
* frottements : 0,01 N·m en élévation et 0,02 N·m en azimut ;
* vent de 10 m/s (36 km/h), sur Terre en extérieur. La pression dynamique vaut 60 Pa, soit
  environ 6,5 N sur le panneau. Le centre de poussée est décalé de 5 à 8 cm en vent oblique,
  ce qui donne **+0,35 N·m en élévation et 0,50 N·m en azimut**.

Le couple disponible vaut couple de maintien × 0,7 (couple en marche lente en micro-pas) ×
rapport × rendement de la vis. Le rendement d'une vis à un filet vaut 0,29 (élévation) et
0,30 (azimut), avec un frottement prudent μ = 0,15.

| Marge = disponible / besoin | Lune | Terre, intérieur | Terre, extérieur (vent 10 m/s) |
|---|---|---|---|
| Élévation (2,86 N·m disponibles) | ×20 | ×3,5 | **×2,5** |
| Azimut (1,22 N·m disponibles) | ×61 | ×41 | **×2,3** |

* **Le cas qui dimensionne est la démonstration sur Terre en extérieur.** On y vise une
  marge d'environ 2, sans surdimensionner. Les grandes marges sur la Lune viennent de
  l'absence de vent et de la gravité six fois plus faible : le même matériel doit aussi
  faire la démonstration à 1 g.
* **Chaque moteur est le plus petit moteur courant qui convient.** Avec le moteur juste en
  dessous, la marge en vent devient insuffisante :
  * élévation : NEMA 11 de 45 mm, ×0,85 ;
  * azimut : NEMA 11 court (32 mm, ≈ 0,05 N·m), ×1,2.

### Tenue moteurs coupés

| Cas | Ce qui tient | Résultat |
|---|---|---|
| **Terre**, vis graissées (μ ≈ 0,10) | La vis se bloque : hélice de 3,6° (élévation) et 3,8° (azimut), angle de frottement 5,7° | **Tient dans toutes les positions, même dans le vent** |
| Terre, frottement réduit par des vibrations (μ ≈ 0,05) | La vis peut redevenir réversible. Le couple résiduel du moteur coupé (0,016 N·m pour le NEMA 17, 0,005 N·m pour le NEMA 11) prend le relais | Tient : ×3,5 en élévation, ×2,4 en azimut |
| **Lune**, MoS₂ sous vide (μ ≈ 0,02) | La vis est réversible, mais la gravité ne donne que 0,13 N·m et il n'y a pas de vent | **Tient** : ×9 en élévation par le couple résiduel du moteur. En azimut, rien ne pousse |

Conséquences :
* **Aucun courant à l'arrêt** : drivers désactivés entre deux mouvements, donc consommation
  nulle. Le suivi consomme moins de 0,5 Wh par jour, ce qui compte pour la nuit lunaire de
  14 jours.
* **Pas de surchauffe dans le vide**, puisque les moteurs sont presque toujours coupés.
* **La position n'est pas perdue** : au réveil, le moteur bouge au plus d'un pas, soit
  0,036° au panneau.
* **Ne jamais forcer le panneau à la main** : on forcerait directement sur les dents de la
  roue en bronze. Pour le bouger, alimenter le moteur ou tourner l'arbre de la vis.

### Limites de vent (sur Terre)

| | Limite |
|---|---|
| Tourner sans perdre de pas | environ 24 m/s en élévation, **environ 15 m/s (55 km/h) en azimut** |
| Tenir moteurs coupés | environ 30 m/s : au-delà, ce sont les dents de bronze qui limitent |
| **Trépied non ancré** (pire orientation) | **basculement vers 16 m/s (58 km/h)** |

Au-delà d'environ 15 m/s, c'est le trépied qui limite. Pour une démonstration en extérieur,
planter les vis d'ancrage ou lester les pieds. Au-dessus de 10 m/s, mettre le panneau à plat
(élévation 90°), où le vent a le moins de prise, puis couper les moteurs.

### Résolution et vitesses (moteurs à 200 pas/tour, 1/16 de pas)

| | Élévation | Azimut |
|---|---|---|
| Pas entier au panneau | 0,036° | 0,030° |
| Micro-pas (1/16) | 0,0023° | 0,0019° |
| Vitesse conseillée | 14°/s (moteur à 120 tr/min) | 12°/s |

Le Soleil se déplace d'environ 0,5°/h sur la Lune et 15°/h sur Terre : un retour à plat ou
une remise en position prend quelques secondes.

**Plages de mouvement** :
* élévation de −2° à +92° (butées). Le panneau peut ainsi passer à la verticale au lever et
  au coucher du Soleil, et en permanence au pôle Sud ;
* azimut limité à ±180° par la boucle de câble, puis retour en arrière. Au pôle Sud, il faut
  un tour complet par jour lunaire : on revient en arrière une fois par jour, ou l'on monte
  un collecteur tournant dans le moyeu.

### Commande par ESP32

* **Drivers : 2 × TMC2209**, logique en 3,3 V. Ils sont pilotés par UART, sur un bus commun,
  avec les adresses 0 et 1 fixées par MS1/MS2.
* **Câblage** :
  * élévation : STEP GPIO 25, DIR GPIO 26 ;
  * azimut : STEP GPIO 32, DIR GPIO 33 ;
  * EN commun : GPIO 27 ;
  * UART : TX GPIO 17 vers PDN_UART à travers 1 kΩ, RX GPIO 16 ;
  * fins de course : GPIO 18 et 19, avec pull-up interne.
* **Alimentation : 12 V**, par exemple une batterie LiFePO4 4S de 12,8 V, avec 100 µF au
  plus près de chaque driver. L'ESP32 est alimenté par un abaisseur 12 V → 5 V.
* **Réglages** :
  * courant de marche (`rms_current`) : 1,3 A pour le NEMA 17, 0,67 A pour le NEMA 11 ;
  * 16 micro-pas, StealthChop ;
  * à l'arrêt : drivers désactivés par EN.
* **Bibliothèques Arduino** : `FastAccelStepper`, qui génère les impulsions STEP en matériel
  sur l'ESP32, avec rampes d'accélération, et `TMCStepper`, pour le courant et le micro-pas
  par UART.
* **Origine** :
  * un micro-switch en butée basse d'élévation (−2°) ;
  * un capteur à effet Hall et un aimant sur la roue fixe pour l'azimut.

  La détection de calage sans capteur (StallGuard) n'est pas fiable à basse vitesse,
  surtout derrière une vis sans fin.
* L'électronique (ESP32, drivers, batterie) est dans l'unité de contrôle au sol.

## 3. Panneau photovoltaïque

* **356 × 253 × 30 mm** : cadre aluminium en C (rebord avant et aile arrière de 12 mm),
  laminé verre 3,2 mm + EVA + face arrière, 72 cellules (9 × 8), boîte de jonction au dos.
* Monté en **format paysage** : l'axe d'élévation est parallèle au côté de 356 mm.
* Le dos du cadre est à **46 mm de l'axe d'élévation**. Ce décalage permet au panneau de
  passer à la verticale devant la chape. Son point le plus bas (≈ 571 mm du sol, à −2°)
  passe à côté du socle et de la roue d'azimut, et reste au-dessus de tout le trépied.
* Les coins en plastique noir visibles sur la photo du panneau sont des protections
  d'emballage. Ils ne sont pas modélisés.

## 4. Conditions lunaires et réponses de conception

| Contrainte lunaire | Conséquence sur le tracker |
|---|---|
| **Gravité 1,62 m/s² (1/6 g)**, **pas de vent** | Charges très faibles sur la tête et le trépied. Le couple dû au décentrage du panneau autour de l'axe d'élévation est six fois plus faible que sur Terre. Les essais au sol à 1 g, avec du vent, restent le cas le plus exigeant pour les moteurs. |
| **Vide** | **Soudage à froid** : chaque contact associe deux matériaux différents (vis en inox 17-4PH contre roues en bronze, roulements en acier 440C), avec une lubrification sèche au MoS₂. **Pas de convection** : les moteurs ne sont alimentés que pendant les mouvements, grâce aux vis irréversibles, et leur chaleur part par conduction vers la chape. Il faut des moteurs en version « vide » (graisses et isolants à faible dégazage), de même taille. |
| **Températures de −173 °C à +127 °C** | Jeu de denture de 0,1 mm. Jeu axial de 0,1 mm par côté entre les bossages du chapeau et les bagues intérieures des 608 : chapeau et chape sont dans le même alliage et se dilatent ensemble. Pas de plastique ordinaire dans la tête : le PLA d'un prototype imprimé en 3D se ramollit vers 60 °C. |
| **Régolithe abrasif et électrostatique** | Vis et roues à protéger par un soufflet ou un capot, connecteurs orientés vers le bas, câbles passés par l'axe d'azimut. |
| **Sol meuble et irrégulier** | Trépied à trois appuis, patins Ø120 à crampons sur rotule, jambes télescopiques, vis d'ancrage hélicoïdales (voir § 6). |
| **Jour lunaire de 29,5 jours terrestres, nuit de 14 jours** | Suivi très lent (≈ 0,5°/h), donc peu de pas moteur. Aucune consommation à l'arrêt grâce aux vis irréversibles. |

## 5. Choix de l'angle

Sur la Lune, l'axe de rotation n'est incliné que de **1,54°**. La hauteur du Soleil à midi
vaut donc presque exactement 90° moins la latitude du site :

* **Pôle Sud (programme Artemis)** : le Soleil reste à **±1,5° de l'horizon** et fait
  **un tour complet d'azimut par jour lunaire**. Le panneau est **quasi vertical** et
  l'azimut tourne en continu. C'est la pose du fichier principal.
* **Latitudes moyennes (sites Apollo, environ 20 à 26°N)** : le Soleil monte jusqu'à 64–70°.
  La pose fournie (Soleil à 50°) donne un panneau **incliné à 40°**.
* Au lever et au coucher du Soleil, **tout site** exige un panneau vertical, d'où la plage
  d'élévation de −2° à +92°.

## 6. Trépied

Le trépied est **dimensionné pour le panneau de 356 × 253 mm et la tête à vis sans fin**.
Architecture : trois jambes en Y à 120°, articulées sur un moyeu, avec entretoises vers un
collier inférieur coulissant, jambes télescopiques, patins sur rotule et ancrages.

### Angle φ des jambes : optimisé, **φ = 32,5°** (angle entre jambe et colonne)

L'articulation haute est fixée par le panneau : tout le trépied doit rester sous le volume
qu'il balaie. Elle est donc à 509 mm du sol, juste sous le socle de la tête. φ fixe alors
le rayon des pieds, la longueur des jambes et leur course télescopique.
`optimisation_angle.py` évalue chaque angle de 25° à 60° avec les masses et le centre de
gravité réels de la CAO, dans la pire orientation du panneau.

| Contrainte | Exigence | Effet de φ |
|---|---|---|
| **C1 Stabilité sans ancrage** | Tenir sur une pente de 15°, avec un caillou ou un enfoncement de 50 mm sous un pied, et 5° de marge | Plus φ est grand, plus les pieds sont écartés et plus le tracker est stable : **φ ≥ 32,5°** |
| **C2 Mise à niveau** | Les jambes télescopiques (deux tubes) remettent la tête de niveau sur une pente de 10° | Plus φ est grand, plus la course nécessaire croît vite : φ ≤ 52° |
| **C3 Garde au sol** | Pointe de la colonne à au moins 150 mm du sol | φ ≤ 49,4° |

Tous les autres critères se dégradent quand φ augmente : longueur et masse des jambes,
poussée reprise par les entretoises (le frottement au sol est six fois plus faible sur la
Lune), course de nivelage et emprise au sol. **L'optimum est donc le plus petit angle
admissible, 32,5°** (plage admissible : 32,5° à 49°). La rigidité latérale, maximale à 54,7°,
ne dimensionne pas sur la Lune, où il n'y a pas de vent.

La tête à vis sans fin est légère (tête + panneau : 2,8 kg) : le centre de gravité du
tracker est bas, ce qui permet cet angle faible.

L'optimum dépend des exigences. Par exemple, il passe à 38° pour une pente de 20° ou une
marge de 10°. Le détail est dans
[`docs/optimisation_angle_jambes.md`](docs/optimisation_angle_jambes.md). Si la masse
de la tête ou du panneau change, relancer `python optimisation_angle.py`.

### Dimensions qui en découlent

| Dimension | Ce qui l'a fixée |
|---|---|
| **Axe d'élévation à 700 mm** | Le point bas du panneau vertical doit rester nettement au-dessus du sol : il est à 571 mm. Plus haut, le tracker serait plus lourd et moins stable sans raison. |
| **Sommet de la colonne à 544 mm**, moyeu des jambes à 509 mm | La tête met l'axe d'élévation 156 mm au-dessus de la colonne. Tout le trépied reste sous le volume balayé par le panneau. |
| **Pieds sur un cercle de Ø738 mm**, jambes de 556 mm | Conséquence de φ = 32,5°. Basculement sans ancrage à 25,5° dans la pire orientation du panneau (exigé : 25,2°). |
| **Course télescopique ±77 mm**, bague de blocage | Remise à niveau sur une pente de 10°. Le tube inférieur Ø20 coulisse dans le tube supérieur Ø25 avec au moins 45 mm de recouvrement. |
| **Entretoises horizontales** Ø12 × 1, bride juste au-dessus de la bague | Meilleur bras de levier. Le collier inférieur se place à leur hauteur (306 mm). |
| **Tubes Ø25 × 1,5 et Ø20 × 1,5, colonne Ø50 × 2, axes Ø6 et Ø5** | Minimum pratique à cette échelle (manutention avec des gants de scaphandre, chocs). Ces sections ne sont pas calculées d'après le poids : à vérifier quand la masse sera figée. |
| **Patins Ø120 à crampons, rotule ±20°** | Pression sur le régolithe d'environ 340 Pa sur la Lune ; adaptation aux pentes et aux cailloux. |
| **Vis d'ancrage hélicoïdales Ø60, enfoncées de 400 mm** | Un piquet lisse tient par frottement, six fois plus faible que sur Terre. L'hélice s'appuie au contraire sur la couche compacte du régolithe, sous 30 cm. Les vis se posent avec une visseuse à travers l'anneau du patin. Sur Terre, elles servent aussi contre le vent (voir § 2). |

Le trépied pèse 4,3 kg.

## 7. Matériaux

| Élément | Cas réel (Lune) | Démonstration sur Terre (§ 12) |
|---|---|---|
| Socle, fond, chape, chapeau en U, paliers et supports de moteurs | Al 6061-T6 anodisé | **PETG imprimé** (le moyeu de la chape est imprimé à part) |
| Rondelle d'arrêt du moyeu | Inox 17-4PH | **PETG imprimé** |
| Roues des vis sans fin (azimut et élévation) | Bronze CuSn12 | **PETG imprimé** |
| Vis sans fin | Inox 17-4PH | **PETG imprimé** |
| Arbres des vis sans fin Ø5 | Inox 17-4PH | Acier, non imprimés : tige Ø5 rectifiée |
| Pivots d'élévation | Inox 17-4PH, Ø8 (dont un en D), sur 608 | **PETG imprimé**, Ø12 (l'entraîné en D), sur 6801 |
| Accouplements | Al 7075-T73 | Accouplements flexibles alu 5/5 du commerce |
| Roulements | 6806, 608, 685 **ZZ** en acier 440C, lubrification sèche (MoS₂) | 6806, **6801**, 685 **ZZ** (ou 2RS) en acier standard, graissés à vie d'origine |
| Lubrification des vis et des roues | MoS₂ sec | Graisse PTFE |
| Visserie | Inox ou titane | Vis CHC acier M3 et M2,5 |
| Moteurs | Version vide / spatiale (même taille) | NEMA 17 et NEMA 11 du commerce |
| Rails du panneau | Al 6061-T6 | Aluminium, non imprimés |
| Ferrures et colliers du trépied, axes, vis d'ancrage | Ti-6Al-4V | Non imprimés (métal) |
| Tubes de jambes, colonne, entretoises, patins | Al 7075-T73 anodisé dur | Non imprimés (aluminium) |
| Cadre du panneau | Al 6063-T5 | Al 6063-T5 (panneau du commerce) |

## 8. Caractéristiques principales

| Grandeur | Valeur |
|---|---|
| Hauteur de l'axe d'élévation | 700 mm |
| Angle des jambes | φ = 32,5° par rapport à la colonne (optimisé) |
| Emprise au sol | Pieds sur Ø738 mm, Ø858 mm hors patins (≈ Ø1040 mm avec les anneaux d'ancrage) |
| Panneau | 356 × 253 × 30 mm, 72 cellules |
| Puissance du panneau | ≈ 10 W crête sur Terre (valeur typique de ce format, à confirmer sur sa fiche) |
| Débattements | Azimut ±180° (boucle de câble), élévation −2° à +92° |
| Réductions | Azimut 60:1, élévation 50:1, vis sans fin irréversibles |
| Moteurs | NEMA 17 de 34 mm (élévation), NEMA 11 de 45 mm (azimut), pilotés par ESP32 + TMC2209 |
| Masse de la tête (partie fixe + partie tournante, hors panneau) | 1,81 kg, dont 0,36 kg de moteurs (1,19 kg en version PETG) |
| Masse de la partie qui bascule (panneau + chapeau + roue + rails) | 1,52 kg, dont 1,01 kg de panneau |
| Masse du trépied | 4,3 kg |
| Masse du tracker complet | 7,2 kg (poids lunaire ≈ 12 N) |

Le détail pièce par pièce est dans `docs/bilan_masse.csv`. Les moteurs et l'unité au sol ont
une **masse forfaitaire**, car leur intérieur n'est pas modélisé.

## 9. Vérifications effectuées par les scripts

* **Interférences pièce à pièce** dans les deux poses du tracker et dans la tête seule,
  en cotes réelles comme en version PETG : **aucune**.
  * Toutes les vis sont modélisées, avec leur tête et leur noyau : chaque tête est
    accessible, et aucune vis ne dépasse de son trou ni ne touche une autre pièce.
  * Ce contrôle a conduit à revoir plusieurs fixations : la roue d'azimut est vissée par en
    dessous de la vis qui la parcourt, et les vis du fond n'ont plus leur tête sur la colonne.
    Le palier et le support d'azimut sont vissés par-dessus, et des lamages laissent la place
    aux têtes des vis des moteurs.
* **Engrènement** : les vis sont calées sur leurs roues, avec les dents en prise et sans
  chevauchement :
  * à −2°, 40° et 92° d'élévation ;
  * à des azimuts quelconques (37° et 113°), ce qui valide la loi de rotation de la vis
    d'azimut.

  Sur la vis d'azimut, il reste un recouvrement de 0,2 mm³. Il vient de la roue modélisée
  à dents droites, alors qu'une vraie roue de vis sans fin est taillée à la fraise-mère.
* **Garde sur toute la plage de mouvement** (élévation de −2° à +92°, azimut sur 360°,
  `python generate_tracker.py --balayage`, environ 11 min) :
  * partie qui bascule (panneau + chapeau) face à tout le reste : 2,0 mm, c'est le jeu
    axial prévu entre les flancs du chapeau et les bras de la chape ; en butée basse, le
    cadre du panneau passe à 10,6 mm du socle ;
  * denture roue / vis d'élévation : contact flanc contre flanc, sans aucun chevauchement
    de −2° à 92° (vérifié tous les 15°) ;
  * chape, moteurs et vis face à la partie fixe (socle, trépied, faisceau) : 1,0 mm au plus
    près, entre l'accouplement d'azimut et le voile de la roue fixe, et entre le moyeu de
    la chape et la roue.
* **Stabilité** : basculement sans ancrage à 25,5° dans la pire orientation du panneau
  (`optimisation_angle.py`).
* **Relecture** des fichiers STEP produits : 177 solides, géométrie valide.

## 10. Limites

* Il s'agit d'une maquette de conception, pas d'un matériel qualifié pour le vol.
* Le panneau de 356 × 253 mm est un panneau terrestre (verre, EVA, boîte de jonction en
  plastique). Sur la Lune, les cycles thermiques et le vide le dégraderaient.
* Les moteurs NEMA du commerce ne sont pas prévus pour le vide ni pour −173 °C. Il faut
  leur équivalent en version vide ou spatiale : même taille, même couple, même pilotage.
* Les roues des vis sont modélisées à dents droites. Les vraies roues sont taillées pour
  leur vis (dents inclinées et creusées), ce qui augmente la portée et la durée de vie.
* Sur Terre, le trépied non ancré bascule vers 16 m/s de vent : l'ancrer pour les
  démonstrations en extérieur.
* Le dimensionnement mécanique (efforts, lancement, thermique) reste à faire une fois la
  masse définitive connue.

## 11. Régénérer ou modifier la CAO

Tous les paramètres sont regroupés en tête de `generate_tracker.py` :
* dans le dictionnaire `P` : dimensions du panneau, hauteur d'axe, décalage du panneau,
  angle et exigences du trépied ;
* dans `POSES` : les deux poses exportées ;
* dans les constantes de la tête : `Z_T`, `VIS_EL`, `VIS_AZ`, `MOT_EL`, `MOT_AZ`, et `PHASES`
  (calage des vis, donné par `generate_tete_vis_sans_fin.py`) ;
* dans `AJUSTEMENTS` : les deux jeux de cotes de la tête, `"reel"` et `"petg"` (§ 12).

Les cas de charge (`VENT_EL`, `VENT_AZ`, `K_RUN`, `MU_REPOS`…) sont en tête de
`generate_tete_vis_sans_fin.py`.

```bash
pip install -r requirements.txt
python generate_tracker.py                    # STEP + bilan de masse + contrôle d'interférences
python generate_tracker.py --balayage         # + garde sur toute la plage az/él
python generate_tete_vis_sans_fin.py          # tête seule (réel + PETG), fichiers à imprimer, couples, contrôles
python optimisation_angle.py                  # angle φ optimal des jambes (à reporter dans P["leg_angle"])
xvfb-run -a python render_apercu.py           # rendus du tracker (xvfb-run seulement sans écran)
xvfb-run -a python render_tete_vis_sans_fin.py   # rendus de la tête seule
```

## 12. Démonstration sur Terre : tête imprimée en 3D en PETG

Pour la démonstration, toute la partie rotative est imprimée en PETG, **vis sans fin
comprises**. Restent en métal : le trépied, les deux rails du panneau, et les pièces du
commerce qu'on ne peut pas imprimer de façon fiable (roulements, arbres Ø5 des vis sans fin,
moteurs, vis). Les **pivots d'élévation sont imprimés** eux aussi.

Les fichiers sont dans **`CAO/Demo_Terre_PETG/`**. Ce sont les mêmes pièces que le cas réel,
générées avec le jeu de cotes `"petg"` : les trous et les dentures ont des jeux qui
compensent l'impression, et quelques formes sont adaptées pour s'imprimer sans support.
L'assemblage imprimé complet, avec roulements, arbres, moteurs et toutes les vis, a été vérifié
par le script :
* **aucune interférence** entre pièces, vis comprises ;
* chaque tête de vis a sa place, et aucune vis ne dépasse de son trou ;
* les vis et les roues **engrènent sans chevauchement** à −2°, 30° et 92° d'élévation et à
  plusieurs azimuts ;
* garde de 2 mm de la partie basculante sur toute la course.

![Pièces à imprimer](docs/demo_petg_pieces_a_imprimer.png)

### Pièces à imprimer (`a_imprimer/`, déjà orientées sur le plateau)

| Pièce | Qté | Orientation (déjà appliquée) | Remarque |
|---|---|---|---|
| `Socle` | 1 | Debout, ouverture en bas | Cône à 45° sous le logement du 6806 bas : pas de support |
| `Fond_Socle` | 1 | Téton vers le haut | |
| `Roue_Azimut_Fixe` | 1 | Dessous plat sur le plateau | Denture m0,8 : buse 0,25 mm conseillée (voir réglages) |
| `Chape` | 1 | Plaque sur le plateau, bras vers le haut | Plus grande pièce : 108 × 84 × 88 mm |
| `Moyeu_Chape` | 1 | Collerette sur le plateau | Imprimé à part pour que la chape tienne à plat ; vissé sous la chape (3 × M3) |
| `Bague_Arret_Moyeu` | 1 | À plat | |
| `Chapeau_U` | 1 | Plaque sur le plateau, flancs vers le haut | Alésage Ø12 en D côté roue ; un bossage Ø14,2 sur la face intérieure de chaque flanc |
| `Roue_Elevation` | 1 | À plat, moyeu en haut | Alésage Ø12 en D |
| `Pivot_Entraine` | 1 | Couché sur son méplat | Ø12 en D, 34 mm tête comprise ; porte la roue. 100 % de remplissage |
| `Pivot_Libre` | 1 | Debout, tête en bas | Ø12, 19 mm tête comprise. 100 % de remplissage |
| `Vis_Elevation`, `Vis_Azimut` | 1 + 1 | Debout, axe vertical | 100 % de remplissage ; bordure (brim) conseillée |
| `Palier_Vis_Elevation`, `Palier_Vis_Azimut` | 1 + 1 | Semelle sur le plateau | Lèvre de 1 mm côté extérieur de chaque joue : le 685 s'enfonce depuis l'intérieur du U |
| `Support_Moteur_Elevation`, `Support_Moteur_Azimut` | 1 + 1 | Semelle sur le plateau | |

Environ 305 g de PETG (406 g si tout était plein).

**Réglages conseillés** :
* PETG, couches de 0,2 mm ;
* 4 périmètres, 40 % de remplissage gyroïde ;
* **100 %** pour les deux vis, les deux roues et les deux pivots ;
* compensation de la patte d'éléphant (≈ 0,2 mm) ;
* aucun support ;
* teinte claire de préférence : un PETG noir en plein soleil d'été peut approcher sa
  température de ramollissement (≈ 80 °C).

**Pour les quatre pièces dentées** : filet des vis de 0,95 mm (élévation) et 0,76 mm
(azimut) en tête, denture m0,8 de la roue d'azimut. Ça s'imprime avec une buse de 0,4 mm,
mais une **buse de 0,25 mm et des couches de 0,1 mm** donnent des dents nettement plus
justes.

### Pièces non imprimées (à acheter)

La liste complète, avec les noms à chercher sur les sites marchands, les quantités, les prix
indicatifs et l'électronique (ESP32, drivers, alimentation), est dans
**[`LISTE_ACHATS.md`](LISTE_ACHATS.md)**. En résumé, pour la mécanique :

| Article | Qté |
|---|---|
| Roulement **6806ZZ** (ISO 61806-2Z ; ou 6806-2RS), 30 × 42 × 7 mm | 2 |
| Roulement **6801ZZ** (ISO 61801-2Z ; ou 6801-2RS), 12 × 21 × 5 mm | 2 |
| Roulement **685ZZ** (ou 685-2RS), 5 × 11 × 5 mm — **pas le 685 ouvert, large de 3 mm** | 4 |
| Tige acier rectifiée Ø5, coupée à 52,5 mm (arbres des vis) : **le seul axe acier** | 2 |
| Accouplement flexible alu 5 mm / 5 mm, Ø19 × 25 mm (à chercher : `flexible shaft coupling 5mm x 5mm D19 L25`) | 2 |
| NEMA 17 34 mm (type 17HS3401, 0,28 N·m) et NEMA 11 45 mm (type 11HS18-0674S) | 1 + 1 |
| Vis CHC M3 : 1 × M3×6, 6 × M3×8, 4 × M3×10, 7 × M3×12, 4 × M3×14, 3 × M3×25 | 25 |
| Vis à tête fraisée M3×8 (roue d'azimut) | 3 |
| Vis CHC M2,5×8 (NEMA 11) | 4 |
| Vis sans tête M3×4 (blocage des vis sans fin sur leur arbre) | 2 |
| Graisse PTFE (vis, roues) | 1 |

Les deux pivots d'élévation sont **imprimés** (`Pivot_Entraine`, `Pivot_Libre`) : il n'y a
plus d'axe Ø8 à acheter. Ils passent à **Ø12** et les 608 deviennent des **6801** (12 × 21 × 5),
car un pivot PETG de Ø8 ne tiendrait pas le couple de la roue d'élévation (voir « Ce que
change le PETG »). Leur tête Ø18 de 2 mm sert d'épaulement contre le flanc du chapeau.

### Jeux d'ajustement de la version imprimée

| Ajustement | Cas réel | PETG | Pourquoi |
|---|---|---|---|
| Logements de roulements (608 / 6801, 685, 6806) | nominal | **+0,15 mm** | Les trous imprimés sortent plus petits ; on obtient un serrage léger du roulement |
| Alésage d'un axe (Ø5 acier des vis ; pivot Ø8 acier ou Ø12 PETG dans le chapeau et la roue) | nominal | **+0,10 mm**, en D côté roue (méplat à 5,25 mm de l'axe pour le Ø12) | Serré. Le méplat transmet le couple de la roue au chapeau, et une vis de pression bloque chaque vis sans fin |
| Pivots imprimés dans les 6801 | Ø8 acier | **Ø11,95** | Les diamètres extérieurs imprimés sortent un peu plus gros : serrage léger de la bague intérieure |
| Moyeu de la chape dans les 6806 | Ø30 | **Ø29,95** | Serrage léger de la bague intérieure |
| Téton du fond dans la colonne (Ø int. 46) | Ø45,5 | **Ø45,6** | Glissant |
| Trous de passage M3 / M2,5 | 3,4 / 2,9 | **3,5 / 3,0** | |
| Avant-trous M3 | 2,5 (taraudés) | **2,8** | Vis auto-taraudées dans le PETG, 4,5 mm de prise au moins |
| Centrage Ø22 des moteurs | 22,5 | **22,4** | |
| Jeu de denture des roues | 0,10 / 0,12 mm | **0,30 mm** | Imprécision des dents imprimées |
| Filet des vis | aminci de 0,15 m | **non aminci, tête raccourcie (0,85 m)** | Tout le jeu est pris sur la roue, et le filet reste assez épais pour l'impression |
| Entraxe vis / roue | nominal | **+0,15 mm**, puis réglé au montage | Lumières en azimut, cales en élévation |
| Bossages du chapeau sur les bagues intérieures des roulements de pivots | 0,10 mm par côté | **0,25 mm** par côté | Règlent le jeu axial du chapeau (0,5 mm en tout en PETG). Si le chapeau serre, poncer un bossage |

**Imprimer d'abord l'éprouvette** `Eprouvette_Ajustements.stl`, avec les mêmes réglages
que les pièces :
* trois logements de 6801 et trois de 685 : le jeu retenu, −0,1 mm et +0,1 mm ;
* un alésage Ø12 en D, un Ø5, un passage et un avant-trou M3 ;
* un téton Ø29,95 pour le 6806 et un téton Ø11,95 pour le 6801 (essayer un vrai roulement
  dessus : il doit entrer en forçant légèrement).

Si ton imprimante préfère un autre logement :
1. change la valeur dans `AJUSTEMENTS["petg"]`, en tête de `generate_tracker.py` ;
2. relance `python generate_tete_vis_sans_fin.py`.

Toutes les pièces sont alors régénérées avec ce jeu.

### Ordre de montage

| Le palier d'une vis sans fin | La vis sans fin imprimée |
|---|---|
| ![Palier : joues, roulements, arbre](docs/explications/palier_joues_roulements.png) | ![Vis sans fin : filet, moyeux](docs/explications/vis_sans_fin_moyeux.png) |

| L'axe d'élévation imprimé : pivots PETG Ø12, roulements 6801, roue |
|---|
| ![Axe d'élévation](docs/explications/axe_elevation.png) |

* **Le palier** est la pièce en U qui porte une vis sans fin. Ses deux parois sont les
  **joues** : chacune tient un roulement 685, et l'arbre acier Ø5 les traverse. Côté
  extérieur, une **lèvre** de 1 mm retient la bague extérieure du roulement : le 685
  s'enfonce depuis l'intérieur du U jusqu'à cette lèvre, et dépasse de 1 mm côté vis.
* **La vis sans fin imprimée** a, de chaque côté du filet, un **moyeu Ø12**. Les moyeux
  viennent en appui sur les bagues intérieures des 685 par un épaulement Ø6,5, qui ne
  touche pas la flasque. Ils calent la vis entre les joues.
  Une vis sans tête M3×4 dans un moyeu bloque la vis sans fin sur l'arbre.
* **L'accouplement flexible** relie l'axe du moteur à l'arbre :
  * 12,5 mm de chaque axe entrent dans l'accouplement, avec environ 1 mm d'écart entre les
    deux bouts ;
  * sa vis de serrage se serre sur le méplat de l'axe du moteur.

1. **Socle** : presser le 6806 bas par-dessous, jusqu'à l'épaulement, puis le 6806 haut
   par-dessus. Pousser sur la bague extérieure (douille ou tube de Ø40 à 42), jamais sur la
   flasque.
2. **Roue d'azimut** : la poser à plat sur le socle et la fixer par 3 vis fraisées M3×8, qui
   doivent affleurer : la vis d'azimut passe juste au-dessus.
3. **Moyeu** : l'enfiler par le haut, à travers la roue et les deux roulements. Visser la
   rondelle d'arrêt par-dessous (2 × M3×8).
4. **Fond** : 3 × M3×25 par-dessous, à travers le téton. Poser la tête sur la colonne :
   * percer la colonne Ø3,4 à 8 mm sous son sommet, face au trou du téton ;
   * mettre la vis anti-rotation M3×6.
5. **Chape** : sur l'établi, presser les deux 6801 dans les bras, par l'extérieur, jusqu'à
   l'épaulement. Monter ensuite la
   chaîne d'élévation :
   * le palier avec ses deux 685 (enfoncés depuis l'intérieur du U jusqu'à la lèvre), la vis
     sur sa tige Ø5 et sa vis de pression ;
   * l'accouplement, le support et le NEMA 17.

   Ces pièces sont vissées par-dessous la chape.
6. **Chapeau** : le présenter sur la chape, mettre la roue d'élévation entre les bras, puis
   enfiler le pivot imprimé en D à travers le flanc, le 6801 et la roue, méplat aligné avec
   ceux du flanc et de la roue. Mettre le pivot libre de l'autre côté, à travers le flanc
   et le 6801. Les deux pivots sont serrés dans le chapeau : une goutte de colle
   cyanoacrylate sous la tête les empêche de ressortir. Les bossages des flancs viennent
   contre les bagues intérieures des 6801 : le chapeau doit tourner librement, avec un
   léger jeu axial.
7. **Chape sur le moyeu** : 3 × M3×12 par-dessus.
8. **Chaîne d'azimut** : glisser le palier d'azimut (685, vis, tige) sous la chape, la vis
   venant en prise radialement avec la roue fixe. Mettre ensuite le support, le NEMA 11 et
   l'accouplement. Toutes ces vis se mettent par-dessus la chape, dans les lumières.
9. **Réglage des engrènements** (vis et roues graissées) :
   * en azimut, rapprocher le palier dans ses lumières jusqu'à supprimer le jeu, sans
     point dur sur un tour complet ;
   * en élévation, caler le palier par des rondelles ou du clinquant de 0,1 à 0,3 mm
     s'il y a trop de jeu.
10. **Rails et panneau** : les rails se vissent par-dessus le chapeau (4 × M3×14, têtes
    noyées dans les rails), puis le panneau se visse sur les rails.

### Ce que change le PETG en fonctionnement

* **Couples** : les vis et roues en PETG doivent être **graissées**.
  * Graissées (μ ≈ 0,15), les marges restent celles du cas réel : ×2,5 en élévation et ×2,3
    en azimut avec un vent de 10 m/s.
  * À sec (μ ≈ 0,30), elles tombent à ×1,4.
  * Ces marges sont celles des roulements **ZZ**. Avec des 2RS, les joints freinent : en
    azimut, ×1,6 graissé et moins de ×1 à sec (voir « Roulements », § 2).
* **Tenue moteurs coupés** : encore plus sûre qu'avec acier et bronze, car le frottement du
  PETG est plus élevé. Les deux vis sont irréversibles, même avec des vibrations.
* **Dents en PETG** : limiter le courant du moteur d'élévation à **0,9 A** (au lieu de
  1,3 A).
  * Si l'élévation se bloque (butée, fin de course raté), le moteur calé donne alors au plus
    2,8 N·m à la roue. Cela fait environ 35 MPa en pied de dent, soit 70 % de la résistance
    du PETG.
  * La marge au vent de 10 m/s reste de ×1,7, et de ×2,5 en intérieur.
  * Le NEMA 11 d'azimut peut rester à 0,67 A : en butée, sa roue voit au plus 22 MPa.
* **Pivots imprimés Ø12** : le pivot entraîné transmet le couple de la roue au chapeau.
  * En marche (poids du panneau et vent de 10 m/s, ≈ 1,2 N·m), il travaille à environ
    4 MPa en torsion. Moteur calé à 0,9 A (2,8 N·m), environ 9 MPa : le tiers de la
    résistance au cisaillement du PETG (≈ 30 MPa).
  * Un pivot PETG de Ø8 monterait à 28 MPa, à la limite de la rupture : d'où le Ø12 et
    les roulements 6801.
  * Il s'imprime **couché**, pour que les couches suivent l'axe. Imprimé debout, il
    casserait en torsion entre deux couches.
  * Le pivot libre ne porte que la moitié du poids de la partie basculante (≈ 7 N) : il
    peut s'imprimer debout.
* **Fluage** : sous une charge permanente, le PETG se déforme lentement. Entre deux
  démonstrations, garer le panneau **à plat (élévation 90°)**, où la pesanteur ne charge
  presque plus la denture.
