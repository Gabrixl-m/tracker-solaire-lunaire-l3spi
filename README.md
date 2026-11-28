# Tracker solaire lunaire deux axes — maquette 3D à l'échelle 1:1

**➜ [Cas lunaire](Fichiers%203D%20%28CAO%29/Cas%20Lunaire/README.md) · [Cas terrestre, à construire](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md) ·
[Liste des composants](Liste-composants.md) ·
[Modèle idéal personnel](.modele_ideal_personnel/README.md) ·
[Variante 28BYJ-48](.variante_28BYJ-48/README.md)**

Un **tracker solaire à deux axes** : une tête rotative oriente un panneau photovoltaïque vers le
Soleil, en azimut et en élévation, grâce à deux petits moteurs pas à pas et à un **capteur
solaire** (4 photodiodes sous une croix d'ombre). Le projet a été conçu pour la **surface de la
Lune**, puis décliné en une **maquette à construire sur Terre**, imprimée en 3D.

Le cœur du projet est la **tête à vis sans fin** : ses deux vis sont **irréversibles**, si bien
qu'elle tient le panneau dans toutes les positions **moteurs coupés**, sans contrepoids, sur
Terre comme sur la Lune. Toutes les cotes sont en **millimètres, à taille réelle**.

**Licence : [CC BY-NC-SA 4.0](LICENSE).** Libre pour un usage personnel, scolaire ou associatif,
en citant l'auteur ; **usage commercial interdit** (§ 6).

| Cas lunaire (panneau à 40°) | Cas terrestre, sur un trépied |
|---|---|
| ![Vue d'ensemble du cas lunaire](docs%20%28extra%29/apercu_latitudemoyenne_iso.png) | ![Cas terrestre sur un trépied](docs%20%28extra%29/trepied_fourche_iso.png) |

## 1. Deux modèles : choisir le sien

Les deux modèles partagent le même principe (deux axes, deux vis sans fin irréversibles, sans
contrepoids), le même panneau, le même capteur solaire et le même principe de commande (§ 2 à 5
ci-dessous). Le cas terrestre a cependant une **tête à fourche**, redessinée pour des moteurs
**28BYJ-48** imposés : la tête décrite au § 2 est celle du cas lunaire, et les différences du cas
terrestre sont dans son README. Chacun a son propre document, dans son dossier :
`Fichiers 3D (CAO)/Cas Lunaire/` et `Fichiers 3D (CAO)/Cas Terrestre (démonstration)/`. Dans
tout le projet, la **« démonstration »** désigne le cas terrestre.

| | 🌙 **Cas lunaire** | 🌍 **Cas terrestre** (démonstration en PETG) |
|---|---|---|
| **Ce que c'est** | L'étude de conception du tracker pour la Lune : pôle Sud (programme Artemis) ou sites Apollo | Une tête **à fourche** à moteurs 28BYJ-48, imprimée en PETG (avec un plateau d'aluminium et des tiges d'acier), vissée sur un trépied : **c'est celui qu'on construit** |
| **Matériaux** | Aluminium, bronze, inox, titane ; roulements secs (MoS₂) pour le vide | PETG imprimé, plateau d'aluminium, tiges d'acier, roulements et visserie du commerce |
| **Support** | Trépied déployable du projet, axe d'élévation à 700 mm | Trépied (vis 1/4"), axe à 902 mm |
| **On y trouve** | Conditions lunaires, choix de l'angle, trépied, matériaux, couples et marges, vérifications, limites | Principe de la fourche, pièces à imprimer et à acheter, réglages, montage pas à pas, électronique complète, boîtier étanche, énergie, LoRa |
| **Fichiers** | `Fichiers 3D (CAO)/Cas Lunaire/` (STEP) | `Fichiers 3D (CAO)/Cas Terrestre (démonstration)/` (STL et STEP), `Electronique/`, `Liste-composants.md` |
| **Documentation** | **➜ [README du cas lunaire](Fichiers%203D%20%28CAO%29/Cas%20Lunaire/README.md)** | **➜ [README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md)** |

**Les chiffres, côte à côte :**

| Grandeur | Cas lunaire | Cas terrestre |
|---|---|---|
| Support du panneau | Chape et chapeau en U, panneau sur deux rails | **Fourche étroite** : panneau tourné de 90°, pivotant autour de son plan médian sur deux tiges d'acier Ø8 ; structure de 344 × 139 × 343 mm |
| Pivots d'élévation | Inox Ø8 sur roulements 608 | Tiges d'acier Ø8, un roulement 608 par bras |
| Moteurs | NEMA 17 (élévation) et NEMA 11 (azimut) | **2 × 28BYJ-48** (12 V), cartes ULN2003 et MCP23017 |
| Roues des vis sans fin | Bronze, 50 et 60 dents | PETG, **100 et 120 dents** |
| Masse de la tête (hors panneau) | 1,86 kg | 1,51 kg |
| Partie qui bascule (panneau, ferrures, tiges, roue, capteur) | 1,73 kg, centre de gravité à 55,7 mm de l'axe | 1,32 kg, centre de gravité à **9,4 mm** de l'axe |
| Alimentation des moteurs | 12 V, 1,0 A (NEMA 17) | 12 V, environ 0,12 A, un seul moteur à la fois |
| Marge d'élévation, vent de 10 m/s | ×2,7 | ×1,6 (moteur prudent) ; suivi limité à 8 m/s (×2,2) |
| Marge d'azimut, vent de 10 m/s | ×2,3 | ×1,7 (moteur prudent) |
| Lubrification des vis et des roues | MoS₂ sec | Graisse PTFE (obligatoire) |
| Roulements | Acier 440C, ZZ, MoS₂ | Acier standard, ZZ (ou 2RS), graissés d'origine |

---

## 2. La tête rotative à vis sans fin (cas lunaire ; principe commun aux deux modèles)

> Ce paragraphe décrit la tête du **cas lunaire**, à chape en U. La tête du **cas terrestre** est
> une **fourche** : mêmes vis sans fin, mêmes paliers, même socle et mêmes roulements d'azimut,
> mais le panneau pivote autour de son plan médian sur deux tiges d'acier, et les roues sont plus
> grandes (100 et 120 dents). Voir le [README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md), § 1.

| Tête seule | Coupe : vis et roue d'élévation |
|---|---|
| ![Tête seule](docs%20%28extra%29/tete_vis_sans_fin_iso.png) | ![Coupe élévation](docs%20%28extra%29/tete_vis_sans_fin_coupe_elevation.png) |
| ![Côté moteurs](docs%20%28extra%29/tete_vis_sans_fin_cote_moteurs.png) | ![Coupe azimut](docs%20%28extra%29/tete_vis_sans_fin_coupe_azimut.png) |
| ![Avec panneau, côté moteurs](docs%20%28extra%29/tete_vis_sans_fin_avec_panneau.png) | ![Avec panneau, côté cellules](docs%20%28extra%29/tete_vis_sans_fin_avec_panneau_face.png) |

### Architecture

La tête est un **mécanisme de pointage bi-axe azimut-élévation (AE)** : un axe vertical pour
tourner (azimut), un axe horizontal porté par lui pour incliner (élévation), et une fourche
(la chape) qui porte le panneau. Le choix de ce schéma est expliqué dans la bibliographie,
à la fin, avec l'article qui l'a guidé.

| Élément | Choix |
|---|---|
| **Socle** (brun) | Cylindre Ø62 posé sur la colonne du trépied, centré dedans par le fond et bloqué en rotation par une vis M3 radiale à travers la colonne. Il porte deux **roulements 6806** (Ø30/Ø42 × 7) et la **roue d'azimut, fixe**, posée à plat sur le socle et tenue par 3 vis M3 fraisées affleurantes, sous le passage de la vis d'azimut. Un passe-câble est orienté vers l'unité au sol |
| **Chape en U** (jaune) | Tourne en azimut sur les deux 6806. Sa plaque porte les **deux moteurs** et les deux vis. Ses bras portent les roulements de l'axe d'élévation (608), à 156 mm au-dessus de la colonne (700 mm du sol) |
| **Chapeau en U renversé** (bleu) | Coiffe la chape. Il pivote sur deux pivots dans les roulements des bras et porte les deux rails du panneau. Axes inox Ø8 sur roulements 608. Un **bossage** sur chaque flanc appuie sur la bague intérieure du roulement et règle le jeu axial |
| **Azimut (axe Y)** | **NEMA 11 de 45 mm** + vis sans fin m0,8 Ø12 sur la **roue bronze Z60 fixée sur le socle** : **60:1**. La vis roule autour de la roue, comme sur une tourelle. Le moteur tourne donc avec le panneau et ne se trouve jamais sur son chemin |
| **Élévation (axe X)** | **NEMA 17 de 34 mm** + vis sans fin m1 Ø16 sur la **roue bronze Z50** calée sur le pivot gauche du chapeau : **50:1**. Le moteur est à l'arrière de la chape, du côté opposé au panneau |
| **Vis** | Chaque vis tourne sur son arbre Ø5, porté par deux roulements 685. Ses deux moyeux appuient sur les bagues intérieures des 685, et une **lèvre** de chaque joue du palier retient leur bague extérieure : la poussée axiale de la vis va au palier. Un accouplement flexible la relie au moteur, si bien que le moteur ne reçoit pas cette poussée |
| **Liaison au panneau** | Deux rails 12 × 13 vissés sur le dessus du chapeau (4 × M3, par-dessus) et sur l'aile arrière du cadre (4 × M3 par-dessous, écrous dans le cadre). Le dos du cadre est à 46 mm de l'axe d'élévation |
| **Passage des câbles** | Les câbles descendent par le moyeu creux de la chape, font une boucle dans le socle et sortent par le passe-câble |
| **Fixations** | Vis CHC M3 (M2,5 pour le NEMA 11), toutes modélisées. Chaque tête de vis est accessible, et aucune n'est sur le passage d'une pièce mobile. Le palier et le support du moteur d'azimut sont vissés à travers des **lumières** de la chape, avec une rondelle sous chaque tête : on règle l'engrènement de la vis d'azimut en les faisant glisser |

**Le cahier des charges L3 impose une structure de 350 × 350 × 350 mm au plus** (panneau excepté) : la fourche du cas
terrestre mesure 344 × 139 × 343 mm, parce que le panneau y est monté dans le sens de sa largeur (axe
d'élévation le long du côté de 253 mm).

Le cas terrestre garde le socle, la roue d'azimut fixe, le moyeu, les paliers et les vis sans
fin, imprimés en PETG et fixés sur la vis 1/4" d'un trépied, mais **remplace la chape, le chapeau
et les rails par une fourche** (plateau d'aluminium, deux bras imprimés, panneau sur deux tiges
d'acier) : le panneau y est équilibré par sa géométrie, ce qui permet d'utiliser des moteurs
28BYJ-48
([README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md)).

**Roulements** : deux **6806** en azimut, deux **608** (lunaire) ou trois **608** (terrestre, fourche) en
élévation, quatre **685** sur les arbres des vis. Tous sont protégés (**ZZ**), et aucune pièce
ne touche leurs flasques : le détail est dans chaque README de modèle.

**Pourquoi une vis sans fin.** Sans contrepoids, le panneau est forcément décentré : il doit
passer devant la chape pour devenir vertical. Son poids crée donc un couple sur l'axe
d'élévation, jusqu'à 0,95 N·m sur Terre (la fourche du cas terrestre supprime ce décentrage : 0,13 N·m). La vis sans fin est **irréversible** :
* le moteur fait tourner la roue ;
* la roue ne peut pas faire tourner la vis, parce que la pente du filet (3,6°) est plus
  faible que l'angle de frottement (environ 6°). C'est le principe du cric de voiture à vis.

Le panneau tient donc seul dans toutes les positions, même dans le vent et même en cas de
coupure de courant. Les moteurs ne sont alimentés que pendant les mouvements.

### Moteurs

| Axe | Moteur (cas lunaire) | Caractéristiques |
|---|---|---|
| Élévation | **NEMA 17, 42 × 42 × 34 mm** (type 17HS3401) | 0,34 N·m, 1,0 A, axe Ø5 × 23,5 à méplat, ≈ 0,22 kg |
| Azimut | **NEMA 11, 28 × 28 × 45 mm** (type 11HS18-0674S) | 0,10 N·m (0,095 retenu dans les calculs, par prudence), 0,67 A, 6,8 Ω, 0,18 kg, axe Ø5 × 20 à méplat |

Ce sont des moteurs du commerce : ils donnent la taille et le couple de référence. Pour le
vol, il faut leur équivalent en version vide ou spatiale, de même taille
([README du cas lunaire](Fichiers%203D%20%28CAO%29/Cas%20Lunaire/README.md), § 9).

**Cas terrestre : deux 28BYJ-48** (12 V, réducteur intégré 63,68:1, 34,3 mN·m à l'arbre, 25
retenu par prudence, environ 30 g), un par axe. Ils sont imposés, et c'est pour eux que la tête
a été refaite en fourche ([README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md), § 1, § 3 et § 9).

### Résolution et vitesses (cas lunaire : moteurs à 200 pas/tour, 1/16 de pas)

| | Élévation | Azimut |
|---|---|---|
| Pas entier au panneau | 0,036° | 0,030° |
| Micro-pas (1/16) | 0,0023° | 0,0019° |
| Vitesse conseillée | 14°/s (moteur à 120 tr/min) | 12°/s |
| Vitesse des corrections de suivi | 0,5°/s | 0,5°/s |

Le Soleil se déplace d'environ 0,5°/h sur la Lune et 15°/h sur Terre : un retour à plat ou
une remise en position prend quelques secondes avec les NEMA du cas lunaire.

**Cas terrestre** (28BYJ-48 : 4076 demi-pas par tour, roues de 100 et 120 dents, 120 demi-pas
par seconde) : 0,0009° et 0,0007° par demi-pas, 0,5° en 5 à 6 s, **90° en 14 min (élévation) et
17 min (azimut)**. C'est lent, sans importance pour le suivi.

**Plages de mouvement** :
* élévation de −2° à +92° (butées). Le panneau peut ainsi passer à la verticale au lever et
  au coucher du Soleil, et en permanence au pôle Sud ;
* azimut limité à ±180° par la boucle de câble, puis retour en arrière. Au pôle Sud, il faut
  un tour complet par jour lunaire : on revient en arrière une fois par jour, ou l'on monte
  un collecteur tournant dans le moyeu.

## 3. Le panneau photovoltaïque

* **Velleman SOL10P** (Gotronic, réf. 27128) : silicium polycristallin, **10 W** ; **17,6 V
  et 0,61 A** au point de puissance maximale, **21,8 V à vide** (Voc). La fiche compte 36
  cellules (4 × 9) ; on en voit 72 (9 × 8) sur la face avant.
* **356 × 253 × 30 mm** : cadre aluminium en C (rebord avant et aile arrière de 12 mm),
  laminé verre 3,2 mm + EVA + face arrière, boîte de jonction au dos, sortie sur cosses à
  souder.
* Monté en **format paysage** : l'axe d'élévation est parallèle au côté de 356 mm.
* **Masse : 1,16 kg (pesée)**. Le modèle en tient compte (`P["pan_masse"]` dans
  `scripts/generate_tracker.py`) : couples, stabilité et angle des jambes sont calculés avec.
* **Fixation, cas lunaire** : 4 vis M3×14 par-dessous traversent les bouts des rails (têtes
  noyées) et l'aile arrière du cadre, avec un écrou M3 posé dans le cadre. Il faut percer 4 trous Ø3,4
  dans l'aile arrière des grands côtés : à 44 mm de part et d'autre du milieu, à 6 mm du bord
  extérieur. Vérifier que l'aile arrière du vrai cadre fait au moins 10 mm.
* **Fixation, cas terrestre** : le panneau est pris par **deux ferrures imprimées** sur ses grands
  côtés (4 vis M3×12 par ferrure, écrous dans le cadre) : percer 8 trous Ø3,4 dans les grands
  côtés ([README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md), § 3).
* **Capteur solaire** (§ 4) : sur le petit côté du pivot libre dans le cas lunaire (2 trous Ø3,4,
  à 9 mm de part et d'autre du milieu et à 12 mm du dos du cadre) ; **sur le petit côté haut dans le
  cas terrestre**, les grands côtés étant pris par les ferrures.
* **Électricité** : un câble souple 2 × AWG 20, soudé sur les cosses de la boîte de jonction,
  descend par la boucle de câble jusqu'au boîtier. Son + passe par le wattmètre A4, qui mesure
  ce que produit le panneau, puis va au régulateur de charge ; son − va droit au régulateur
  ([README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md), § 6). Ses 21,8 V à vide
  restent sous les 26 V que supporte A4.
* Le dos du cadre est à **46 mm de l'axe d'élévation**. Ce décalage permet au panneau de
  passer à la verticale devant la chape. Son point le plus bas (≈ 571 mm du sol, à −2°)
  passe à côté du socle et de la roue d'azimut, et reste au-dessus de tout le trépied.
* Les coins en plastique noir visibles sur la photo du panneau sont des protections
  d'emballage. Ils ne sont pas modélisés.

## 4. Le capteur solaire

| Le capteur sur le petit côté du cadre | Coupe par deux photodiodes |
|---|---|
| ![Capteur solaire](docs%20%28extra%29/explications/capteur_solaire.png) | ![Coupe du capteur solaire](docs%20%28extra%29/explications/capteur_solaire_coupe.png) |

### Principe : 4 photodiodes et une croix d'ombre

Quatre photodiodes **BPW34** sont placées aux quatre coins d'une **croix opaque de 20 mm de
haut**, parallèle à la normale du panneau.
* Quand le panneau vise exactement le Soleil, la croix ne fait d'ombre sur aucune
  photodiode : les quatre reçoivent la même lumière.
* Dès qu'il s'en écarte, l'ombre d'un mur de la croix couvre une partie des deux photodiodes
  du côté opposé au Soleil : 0,37 mm d'ombre pour 1° d'écart.
* Chaque photodiode voit le ciel par une **fenêtre de 2,2 × 2,2 mm**, un peu plus petite
  que sa puce (environ 2,7 mm de côté). Le bord intérieur de la fenêtre prolonge la face
  du mur : l'ombre mord sur la fenêtre dès le moindre écart. Il n'y a **pas de zone
  morte** autour du pointage parfait.
* **Réponse** : le rapport des signaux (plus bas) varie d'environ **9 % par degré**, de façon
  linéaire jusqu'à ±6°. Au-delà, il sature mais garde son signe : tant que le Soleil est
  devant le panneau, le capteur indique dans quel sens tourner.

Les photodiodes sont repérées **HG, HD, BG, BD** :
* **haut / bas** (H, B) le long du côté de 253 mm, celui qui bascule en élévation. Le
  « haut » est le côté du bord supérieur du panneau quand il est incliné ;
* **gauche / droite** (G, D) le long du côté de 356 mm, parallèle à l'axe d'élévation.

### Montage sur le cadre

* Le capteur est au milieu du **petit côté du cadre, côté du pivot libre**, à l'opposé de la
  roue d'élévation. Il tourne avec le panneau et mesure donc l'erreur du panneau lui-même.
* Il est **à côté des cellules**, pas au-dessus. Pour qu'il leur fasse de l'ombre, il faudrait
  que le Soleil soit à plus de 40° de l'axe du panneau, ce qui n'arrive pas en suivi.
* Les photodiodes sont 1 mm au-dessus du rebord avant du cadre : le cadre ne leur fait pas
  d'ombre non plus.
* L'**équerre** se visse contre le petit côté avec 2 vis M3×10. Leurs écrous M3 sont
  posés à l'intérieur du cadre, sous le laminé, et on les atteint par le dos ouvert du panneau,
  comme ceux des rails. Il faut percer 2 trous Ø3,4 dans le petit côté : à 9 mm de part et
  d'autre du milieu et à 12 mm du dos du cadre.
* Le **boîtier** se visse sur l'équerre par-dessous (2 vis M3×10 dans des avant-trous).
* La croix est alors parallèle à la normale du panneau, à l'impression près. Inutile de
  régler plus finement : un défaut de 1° ne coûte que 0,015 % de puissance (plus bas).

### Ce que fait le programme

```
H = HG + HD    B = BG + BD    G = HG + BG    D = HD + BD    S = H + B
erreur d'élévation = (H − B) / S      environ 0,087 par degré
erreur d'azimut    = (G − D) / S
```

* Les rapports ne dépendent pas de la force du Soleil. Un voile léger ou une poussière
  uniforme sur le capteur ne déplacent pas leur zéro.
* **Étalonnage, une seule fois** : poser une feuille de papier calque sur la croix, au soleil.
  Les 4 photodiodes reçoivent alors la même lumière. Noter les 4 valeurs, et en déduire un
  coefficient par photodiode (moyenne des 4 / sa valeur), pour corriger leurs petites
  différences.
* Si S est trop faible (nuage, nuit), ignorer le capteur et rester sur la position calculée.
* Si l'erreur est sous 0,022 (≈ 0,25°), ne pas bouger, pour que le panneau n'oscille pas.
  Au-delà, corriger de 0,5° : le panneau se place 0,25° **en avance** sur le Soleil, qui le
  rattrape puis le dépasse. Sur Terre, cela fait une correction toutes les 2 minutes environ
  (cadence détaillée au [README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md), § 7).
* En azimut, diviser l'erreur par cos(élévation) avant de la convertir en pas : près du
  zénith, l'azimut doit beaucoup tourner pour corriger une petite erreur (voir la
  bibliographie).
* Au premier essai, vérifier le **sens** de chaque correction et l'inverser dans le programme
  s'il le faut. Le sens dépend du câblage, et du sens dans lequel le boîtier est vissé.

Il n'est pas utile de viser plus juste : une erreur de 1° ne fait perdre que 0,015 % de la
puissance du panneau, et 5° seulement 0,4 %.

La **stratégie de suivi** diffère d'un modèle à l'autre :
* **sur la Lune**, les photodiodes pilotent et le calcul sert de secours
  ([README du cas lunaire](Fichiers%203D%20%28CAO%29/Cas%20Lunaire/README.md)) ;
* **sur Terre**, le calcul fait le gros du pointage et les photodiodes corrigent ; la cadence
  des corrections, la fabrication et le branchement du capteur sont dans le
  [README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md).

## 5. La commande

* **Électronique** : un ESP32 dans l'unité de contrôle au sol, avec la batterie. **Cas
  lunaire** : deux drivers **TMC2209** (16 micro-pas, StealthChop) ; pour le vol, il faudrait leurs
  équivalents résistants aux rayonnements. **Cas terrestre** : les deux **28BYJ-48** se pilotent par
  des cartes **ULN2003** commandées par un **MCP23017** sur l'I²C (le Heltec n'a pas assez de
  broches libres), alimentées en 12 V.
* **Courants de marche** : 1,0 A pour le NEMA 17 et 0,67 A pour le NEMA 11 (cas lunaire) ;
  environ 0,12 A à 12 V pour un 28BYJ-48 (cas terrestre), **un seul moteur à la fois**.
* **À l'arrêt, les moteurs sont coupés** (drivers coupés, ou sorties du MCP23017 à 0) : les vis
  tiennent seules, donc ni courant ni échauffement entre deux mouvements.
* **Origines** :
  * un micro-switch en butée basse d'élévation (−2°) ;
  * un capteur à effet Hall et un aimant sur la roue fixe pour l'azimut.

  La détection de calage sans capteur (StallGuard) n'est pas fiable à basse vitesse,
  surtout derrière une vis sans fin.
* **Suivi du Soleil** : capteur solaire et calcul de la position du Soleil (§ 4).

Le câblage détaillé (carte Heltec, brochage, réglages, boîtier étanche, énergie, LoRa) est
dans le [README du cas terrestre](Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md), § 6. Le cas lunaire reprend
le même principe.

## 6. Fichiers, scripts et licence

### Organisation du dépôt

```
Fichiers 3D (CAO)/
  Cas Lunaire/                     cas lunaire : assemblages et pièces seules (STEP), et son README
  Cas Terrestre (démonstration)/   cas terrestre (fourche, 28BYJ-48) : pièces à imprimer (STL + STEP), plateau d'aluminium (DXF), assemblages, et son README
docs (extra)/                      rendus, images annotées, guide de la visserie, bilan de masse, optimisation des jambes
Electronique/                      schéma électrique (QElectroTech, PDF) et implantation du boîtier (Fritzing)
scripts/                           scripts Python qui génèrent la CAO, les contrôles et les rendus
Liste-composants.md                liste des composants à acheter pour le cas terrestre (fourche, 28BYJ-48)
tracker_solaire_composants.pdf     liste des composants à commander, telle qu'elle a été envoyée au professeur
requirements.txt                   dépendances Python
LICENSE                            licence CC BY-NC-SA 4.0
```

Le détail des fichiers de chaque modèle est à la fin de son README. Fichiers communs :

| Fichier | Contenu |
|---|---|
| `docs (extra)/bilan_masse.csv` | Bilan de masse pièce par pièce (séparateur `;`, s'ouvre dans Excel) |
| `docs (extra)/apercu_*.png`, `docs (extra)/tete_vis_sans_fin_*.png`, `docs (extra)/trepied_fourche_*.png` | Rendus du tracker (iso, face, profil, arrière, détails), de la tête seule (dont deux coupes) et de la démonstration sur trépied |
| **`docs (extra)/visserie/`** | **Guide de la visserie** (`README.md`) : planche de tous les modèles à l'échelle avec leurs quantités, puis vues éclatées de la tête, du panneau, du capteur solaire et du fond de la démonstration, étape par étape (vis en orange, rondelles et écrous en vert clair) |
| `docs (extra)/optimisation_angle_jambes.md` | Optimisation de l'angle φ des jambes : exigences, résultats angle par angle, sensibilité |
| `scripts/generate_tracker.py` | Script paramétrique qui génère toute la CAO, le bilan de masse et les contrôles |
| `scripts/generate_tete_vis_sans_fin.py` | Exporte la tête seule du cas lunaire, cale les vis, calcule les couples et la tenue moteurs coupés ; écrit aussi la tête NEMA en PETG du modèle idéal personnel (`.modele_ideal_personnel/`) |
| **`scripts/generate_fourche.py`** | **Génère le cas terrestre** (tête à fourche, 28BYJ-48) : CAO complète avec tiges, visserie et inserts, pièces à imprimer, plateau d'aluminium (DXF), éprouvette, contrôles (interférences, prise des vis, garde, couples, stabilité), et sa tête sur le trépied |
| `scripts/render_fourche.py` | Rendus du cas terrestre (`docs (extra)/fourche_*.png`, `trepied_fourche_*.png`) |
| `scripts/generate_demo_trepied.py` | Trépied et lest de la démonstration, vérification des interférences et calcul de la stabilité (basculement, vent) ; utilisé par `generate_fourche.py`, et seul pour la tête du modèle idéal personnel |
| `scripts/verification_stabilite.py` | Vérifie par un calcul indépendant la stabilité sur le trépied de la tête du modèle idéal personnel (vent de toutes les directions, glissement, planche lestée, incertitudes) ; **non relancé pour la fourche** |
| `scripts/optimisation_angle.py` | Calcule l'angle φ optimal des jambes à partir des masses de la CAO |
| `scripts/generate_schema_electrique.py` | Écrit le schéma électrique au format QElectroTech (symboles, composants, fils) |
| `scripts/generate_implantation_fritzing.py` | Écrit l'implantation du boîtier au format Fritzing (Heltec V4, ULN2003A, MCP23017, ADS1115 et borniers dessinés à l'échelle ; `--nema` : ancien modèle à TMC2209 ; `--apercu` : images PNG sans Fritzing) |
| `scripts/exporter_schema.py` | Exporte le schéma .qet en PDF et en PNG (sans QElectroTech) |
| `scripts/render_apercu.py`, `scripts/render_tete_vis_sans_fin.py`, `scripts/render_explications.py`, `scripts/render_visserie.py` | Génèrent les rendus PNG, les images annotées et les vues de la visserie |
| [`tracker_solaire_composants.pdf`](tracker_solaire_composants.pdf) | Liste des composants à commander, telle qu'elle a été envoyée au professeur (15 références Gotronic) |
| `requirements.txt` | Dépendances Python (CadQuery) |
| `LICENSE` | Licence du projet : CC BY-NC-SA 4.0 (voir plus bas) |

### Ouvrir dans SolidWorks

Un fichier SolidWorks natif (`.SLDASM` / `.SLDPRT`) ne peut être écrit que par SolidWorks
lui-même. Le format STEP AP214 fourni s'ouvre directement comme un assemblage complet,
avec les noms des pièces, les sous-assemblages et les couleurs.

Code couleur de la visserie dans les assemblages (`Tracker_Lunaire_*.step`,
`Tete_Rotative_*.step`, `Demo_Trepied.step`) :
* **orange** : toutes les vis (CHC et FHC M3, vis sans tête M3×4 de blocage des vis sans
  fin, vis 1/4"-20 du plateau du trépied) ;
* **vert clair** : les rondelles et les écrous qui vont avec (rondelles M3, écrous M3,
  écrou 1/4"-20).

Les rendus PNG suivent le même code. La visserie y est éclairée plus fort et cernée de noir,
et un bandeau en bas de l'image rappelle les deux couleurs.

Les autres pièces qui étaient orange ont changé de teinte pour éviter la confusion : bague
de blocage et ancrages en gris titane, molettes et clips du trépied de la démonstration en gris. Les
fichiers de pièces seules (`pieces/*.step`) n'ont pas de couleur. Si les couleurs
n'apparaissent pas, cocher l'import des couleurs dans les options d'import STEP de
SolidWorks.

1. **Fichier › Ouvrir**, type *STEP AP203/214/242 (\*.step; \*.stp)*, puis choisir
   `Fichiers 3D (CAO)/Cas Lunaire/Tracker_Lunaire_PoleSud.step`.
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
  * libérer `SA_Panneau` et ajouter une contrainte coaxiale entre les pivots (`Pivot_Entraine`, `Pivot_Libre`) et les `Roulement_608` (cas terrestre : `Tige_Gauche` et `Tige_Droite`) ;
  * ajouter des contraintes d'engrenage entre `Vis_Azimut` et `Roue_Azimut_Fixe` (rapport 1:60), puis entre `Vis_Elevation` et `Roue_Elevation` (1:50 ; cas terrestre : 1:120 et 1:100).

L'arborescence des assemblages est dans chaque README de modèle.

### Régénérer ou modifier la CAO

Les scripts sont dans `scripts/` et se lancent depuis la racine du dépôt. Tous les
paramètres sont regroupés en tête de `scripts/generate_tracker.py` :
* dans le dictionnaire `P` : dimensions du panneau, hauteur d'axe, décalage du panneau,
  angle et exigences du trépied ;
* dans `POSES` : les deux poses exportées ;
* dans les constantes de la tête : `Z_T`, `VIS_EL`, `VIS_AZ`, `MOT_EL`, `MOT_AZ`, et `PHASES`
  (calage des vis, donné par `scripts/generate_tete_vis_sans_fin.py`) ;
* dans `AJUSTEMENTS` : les deux jeux de cotes de la tête, `"reel"` et `"petg"` (cas terrestre).

Les cas de charge (`VENT_EL`, `VENT_AZ`, `K_RUN`, `MU_REPOS`…) sont en tête de
`scripts/generate_tete_vis_sans_fin.py`. Ceux du trépied de la démonstration (`TREPIED_DEMO`, lests) sont en tête
de `scripts/generate_demo_trepied.py`.

```bash
pip install -r requirements.txt
python scripts/generate_tracker.py                    # STEP + bilan de masse + contrôle d'interférences
python scripts/generate_tracker.py --balayage         # + garde sur toute la plage az/él
python scripts/generate_tete_vis_sans_fin.py          # tête seule (réel + PETG), fichiers à imprimer, couples, contrôles
python scripts/generate_fourche.py                    # cas terrestre (fourche, 28BYJ-48) : CAO, STEP, STL, DXF, contrôles, tête sur trépied
python scripts/generate_demo_trepied.py               # tête NEMA (modèle idéal personnel) sur trépied : STEP, contrôles, stabilité
xvfb-run -a python scripts/render_fourche.py                       # rendus du cas terrestre (fourche)
python scripts/verification_stabilite.py              # stabilité de la tête NEMA (modèle idéal personnel), calcul indépendant
python scripts/optimisation_angle.py                  # angle φ optimal des jambes (à reporter dans P["leg_angle"])
python scripts/generate_schema_electrique.py          # schéma électrique 28BYJ-48 (Electronique/*.qet) ; --nema : ancien modèle
python scripts/exporter_schema.py                     # PDF et PNG du schéma (ou Fichier > Exporter dans QElectroTech)
python scripts/generate_implantation_fritzing.py --apercu   # implantation du boîtier (Electronique/*.fzz) et ses images
xvfb-run -a python scripts/render_apercu.py           # rendus du tracker (xvfb-run seulement sans écran)
xvfb-run -a python scripts/render_tete_vis_sans_fin.py             # rendus de la tête seule
xvfb-run -a python scripts/render_tete_vis_sans_fin.py --plateau   # pièces à imprimer sur le plateau
xvfb-run -a python scripts/render_explications.py                  # images annotées (docs (extra)/explications/)
xvfb-run -a python scripts/render_visserie.py                      # visserie : planche et vues éclatées (docs (extra)/visserie/)
```

### Licence

Tout le projet (fichiers CAO STEP et STL, images, documents et scripts) est sous licence
**Creative Commons Attribution - Pas d'utilisation commerciale - Partage dans les mêmes
conditions 4.0 International (CC BY-NC-SA 4.0)**. Le texte complet est dans
[`LICENSE`](LICENSE).

| Autorisé | Interdit |
|---|---|
| Consulter, télécharger, imprimer les pièces, construire le tracker pour soi, pour un projet scolaire ou un club | Vendre les fichiers, les pièces imprimées ou un tracker construit d'après le projet |
| Modifier et améliorer le projet, et partager ces modifications | Utiliser le projet dans un produit ou un service payant |
| Le présenter (exposé, démonstration, salon) | Republier une version modifiée sous une autre licence, ou sans citer l'auteur |

**Pour réutiliser le projet**, il faut citer l'auteur et la licence, par exemple :
« Tracker solaire lunaire deux axes, par Gabrixl-m, sous licence CC BY-NC-SA 4.0 », avec un
lien vers ce dépôt. Pour un usage commercial, il faut une autorisation écrite de l'auteur :
le contacter par GitHub.

Les marques et références de produits citées (moteurs, roulements, photodiodes, magasins)
appartiennent à leurs propriétaires. Les logiciels utilisés par les scripts, comme CadQuery
(licence Apache 2.0), ne sont pas inclus dans ce dépôt et gardent leur propre licence.

---

# Bibliographie

## Choix du mode de rotation : le schéma azimut-élévation (AE)

Lien de l'article : <https://scispace.com/pdf/follow-that-ground-station-and-double-the-data-throughput-12phqvc5d9.pdf>

**[1]** P. Garner, N. Phillips, A. Cawthorne, A. da Silva Curiel, P. Davies, L. Boland
(Surrey Satellite Technology Ltd, SSTL), *« Follow that Ground Station! And double the data
throughput using polarization diversity »*, 23rd Annual AIAA/USU Conference on Small
Satellites, Logan (Utah), 2009, article SSC09-VI-8.

Je me suis appuyé sur cet article pour choisir le mode de rotation du tracker. Il décrit le
développement par SSTL d'un mécanisme de pointage d'antenne à deux axes (APM) pour le
satellite d'observation NigeriaSat-2. Ce n'est pas un tracker solaire, mais le problème est
le même : orienter un objet plat vers une cible qui se déplace dans le ciel, avec un
mécanisme léger, peu coûteux et sobre en énergie.

**Ce que montre l'article :**
* **Orientation mécanique plutôt qu'électronique.** SSTL écarte les antennes à balayage
  électronique (complexes, chères, gourmandes, débattement limité) au profit d'un mécanisme
  orientable : faible consommation, grand débattement, facile à agrandir. L'article note
  même qu'un seul axe du mécanisme pourrait servir d'entraînement de panneau solaire (SADM).
* **Trois architectures à deux axes comparées** : X-Y, azimut-élévation (AE) et plateau
  oscillant (« swashplate »).
  * Le schéma **X-Y est rejeté**, car son débattement est insuffisant.
  * Les deux autres sont construits en modèles d'ingénierie et testés en endurance.
  * La conception finale retenue est **azimut-élévation**, avec les modules d'entraînement
    (moteurs, roulements, engrenages) mis au point sur le plateau oscillant.
* **Le résultat, l'APM AE-90**, est qualifié en vibrations et en vide thermique, et a dépassé
  100 000 cycles. Il pointe à mieux que 1°, sur ±270° en azimut et ±114,7° en élévation. Il
  pèse 2,7 kg et consomme environ 3,4 W quand les deux axes bougent.
* **Autres choix de conception** :
  * composants du commerce (COTS) pour réduire le coût ;
  * passage des câbles par l'axe d'azimut grâce à une boucle de câble (jusqu'à 540°),
    plutôt que par un collecteur tournant ;
  * axes équilibrés pour éviter un verrou de lancement.

**Ce que j'en ai repris :**

| Choix de l'article [1] | Dans ce tracker |
|---|---|
| Schéma **azimut-élévation** plutôt que X-Y, pour le débattement | Azimut sur ±180° et élévation de −2° à +92° : tout le ciel est couvert. Au pôle Sud lunaire, le Soleil fait le tour de l'horizon en un jour lunaire : l'azimut le suit naturellement |
| Un axe par coordonnée de la cible | Les deux coordonnées du Soleil (azimut, hauteur), calculées par l'ESP32, donnent directement les angles des deux moteurs : commande simple. Les deux erreurs du capteur solaire (haut / bas, gauche / droite) corrigent chacune un moteur (§ 4) |
| Boucle de câble plutôt qu'un collecteur tournant | Câbles par le moyeu creux de la chape, boucle dans le socle, azimut limité à ±180° puis retour |
| Composants du commerce | Moteurs NEMA 17 et 11 (cas lunaire) ou 28BYJ-48 (cas terrestre), roulements standard (6806, 608, 685), accouplements, ESP32 |
| Même module d'entraînement sur les deux axes | Chaque axe : moteur, accouplement, vis sans fin sur 2 roulements 685 dans un palier, roue |
| Orientation mécanique pour la faible consommation | Moteurs coupés entre deux corrections |

**Ce qui diffère, et pourquoi :**
* **La vitesse.** L'APM suit le passage d'un satellite à plus de 20°/s. Le Soleil avance de
  15°/h sur Terre et de 0,5°/h sur la Lune. J'ai donc choisi des **vis sans fin
  irréversibles** (50:1 et 60:1) plutôt que des axes équilibrés : elles tiennent le panneau
  moteurs coupés, sans contrepoids (voir § 2).
* **Le verrou de lancement.** SSTL équilibre ses deux axes pour s'en passer. Ici, le
  panneau n'est pas équilibré : une version lunaire réelle aura besoin d'un verrou de
  lancement ([README du cas lunaire](Fichiers%203D%20%28CAO%29/Cas%20Lunaire/README.md), § 9).
* **La limite connue du schéma AE : le zénith.** Quand la cible passe près de la verticale,
  l'azimut doit tourner très vite pour la suivre.
  * Au pôle Sud lunaire, le Soleil reste à quelques degrés de l'horizon : le cas ne se
    présente jamais.
  * À La Réunion (21° S, sous les tropiques), le Soleil passe presque au zénith vers midi en
    été. Mais près du zénith, un retard d'azimut ne compte presque pas : 30° de retard à 88°
    de hauteur ne font qu'environ 1° d'erreur de pointage, soit moins de 0,02 % de perte.
