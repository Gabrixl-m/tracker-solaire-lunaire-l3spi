# Variante terrestre avec deux moteurs 28BYJ-48 (contrepoids obligatoire)

> **Document caché.** Il n'est lié depuis aucun autre README. Il décrit une **variante** de la
> démonstration terrestre dont les deux moteurs pas à pas (NEMA 17 et NEMA 11) sont remplacés par
> deux petits **28BYJ-48**. La version principale du projet (NEMA, sans contrepoids) n'est pas
> modifiée. **Cette variante est la seule du projet qui utilise un contrepoids.**
>
> **État : étude et calculs.** Les pièces 3D de cette variante (supports de moteur, platine du
> contrepoids avec inserts) ne sont pas encore modélisées : la liste de ce qui change est au § 5.
> Les marges du § 3 sont calculées par [`calcul_marges.py`](calcul_marges.py), avec le modèle de
> couples du projet (`scripts/generate_tete_vis_sans_fin.py`) : mêmes vis sans fin, mêmes
> frottements, mêmes couples de vent.

## 1. Verdict

| Question | Réponse |
|---|---|
| Les 28BYJ-48 suffisent-ils **sans** contrepoids ? | **Non.** L'élévation demande 0,93 N·m rien que pour porter le panneau ; un 28BYJ-48 en donne 0,50 N·m à la roue : marge de **×0,5, même en intérieur**. |
| Y a-t-il une autre solution que le contrepoids ? | Pas de raisonnable : il faudrait une vis sans fin d'environ 190 dents au lieu de 50 (soit une roue de près de 19 cm, et 27 minutes pour 90°), ou un second étage de réduction. Le contrepoids est plus simple. |
| Et **avec** contrepoids ? | **Oui**, avec une marge réduite au vent : ×17 (élévation) et ×21 (azimut) en intérieur, ×4 à 5 m/s, **×1,2 à 1,3 à 10 m/s** (valeurs nominales). |
| Limite d'utilisation | Suivi jusqu'à **6 m/s (22 km/h)** avec une marge d'au moins ×2, même avec un moteur faible. Au-delà, garer le panneau à plat. |
| Ce qui devient **obligatoire** | Contrepoids ; vis et roues **graissées** ; roulements **ZZ** (pas de 2RS) ; un seul moteur alimenté à la fois ; une extension d'entrées/sorties (§ 6). |

## 2. Le moteur 28BYJ-48

| Caractéristique | Valeur |
|---|---|
| Alimentation | 5 V, unipolaire, 5 fils (rouge = commun) |
| Résistance d'une bobine | environ 50 Ω, donc ≈ 100 mA par bobine allumée |
| Réduction intégrée | 64:1 nominal, **63,68:1** mesuré ; environ 4076 demi-pas par tour de l'arbre de sortie |
| Couple de sortie | **34,3 mN·m** à 120 Hz (« in-traction torque » de la fiche technique) |
| Frottement du réducteur | 600 à 1200 gf·cm (59 à 118 mN·m) : le réducteur tient le moteur coupé, mais il est en plastique |
| Arbre de sortie | Ø5 mm à deux méplats (3 mm entre méplats), court (environ 6 mm au-dessus du bossage de Ø9 mm) et **décentré de 8 mm** par rapport au corps (à vérifier au pied à coulisse sur les moteurs reçus) |
| Fixation | corps Ø28 mm, deux oreilles à 35 mm d'entraxe |
| Masse | environ 30 g, contre 220 g (NEMA 17) et 180 g (NEMA 11) |

Sources : [fiche technique 28BYJ-48](https://cdn.shopify.com/s/files/1/0015/7571/4865/files/datasheet_28BYJ-48.pdf),
[fiche 52Pi](https://wiki.52pi.com/images/3/3a/Stepper-Motor-28BJY-48-Datasheet.pdf).
Une autre fiche donne un couple d'au moins 78,4 mN·m pour une variante différente : **elle n'est
pas retenue**.

**Pourquoi 34,3 mN·m et pas plus.** Les NEMA du projet sont donnés en couple de *maintien* : le
script applique un facteur 0,7 pour passer au couple *en marche*. Les 34,3 mN·m du 28BYJ-48 sont
déjà un couple en marche, à l'arbre de sortie : ils sont pris tels quels. Le calcul utilise aussi
une valeur **prudente de 25 mN·m**, pour la dispersion d'un moteur à l'autre, l'usure du réducteur
et une alimentation à 4,5 V.

**Vitesse.** À 120 demi-pas par seconde (vitesse où le couple est garanti), l'arbre fait environ
1,8 tr/min. Pour 90° de roue : **7 min en élévation et 8,5 min en azimut**. C'est long pour la
mise en position initiale, sans importance pour le suivi (une correction de 0,25° se fait en
quelques secondes). Résolution : 0,0018° par demi-pas en élévation, 0,0015° en azimut.

## 3. Couples et marges

Couple disponible **à la roue** = couple du moteur × nombre de dents × rendement de la vis. Les vis
sont celles du projet : 50:1 en élévation (rendement 0,29 graissé, 0,17 à sec), 60:1 en azimut
(0,31 et 0,18).

| Couple à la roue (N·m) | Élévation | Azimut |
|---|---|---|
| NEMA du projet (référence) | 2,08 | 1,22 |
| 28BYJ-48 nominal, graissé | **0,50** | **0,63** |
| 28BYJ-48 prudent (25 mN·m), graissé | 0,36 | 0,46 |
| 28BYJ-48 nominal, à sec | 0,29 | 0,37 |

**Couple à fournir.** En élévation, le panneau pèse sur la denture : partie basculante de
**1,51 kg, centre de gravité à 61,9 mm de l'axe**, soit 0,92 N·m, plus 0,01 N·m de frottement.
Le vent de 10 m/s ajoute 0,35 N·m en élévation et 0,50 N·m en azimut. Le couple du vent varie
comme le carré de la vitesse.

**Marges, 28BYJ-48 nominal, graissé :**

| | Sans contrepoids | Avec contrepoids |
|---|---|---|
| Élévation, intérieur | **×0,5** (ne tient pas) | **×17** |
| Élévation, vent de 10 m/s | ×0,4 | **×1,3** |
| Azimut, intérieur | ×21 | ×21 |
| Azimut, vent de 10 m/s | ×1,2 | ×1,2 |

Le contrepoids ramène le centre de gravité sur l'axe : il ne reste que le déséquilibre résiduel
(bloc pesé à ± 2 % : 0,02 N·m, pris en compte) et le vent. L'azimut ne dépend pas du contrepoids.

**Marge selon le vent, avec contrepoids, nominal, graissé :**

| Vent | 3 m/s | 5 m/s | 8 m/s | 10 m/s |
|---|---|---|---|---|
| Élévation | ×8,1 | ×4,3 | ×2,0 | ×1,3 |
| Azimut | ×8,4 | ×4,0 | ×1,8 | ×1,2 |

**Vent maximal que le moteur peut encore vaincre** (marge de ×1) :

| | Élévation | Azimut |
|---|---|---|
| Nominal, graissé | 11,6 m/s | 10,9 m/s |
| Prudent (25 mN·m), graissé | 9,8 m/s | 9,2 m/s |
| Nominal, **à sec** | 8,6 m/s | 8,2 m/s |
| Prudent, à sec | 7,2 m/s | 6,9 m/s |

On retient une **limite de suivi de 6 m/s (22 km/h)** : marge de ×2,3 en élévation et ×2,2 en
azimut avec le moteur prudent, graissé. Cette variante **ne tient pas la marge de ×1,5 à ×2 visée
par la version principale au vent de 10 m/s**. Si le vent dépasse la limite, le moteur peut
décrocher (perte de pas) ; il n'y a pas de dégât, les vis sans fin tenant le panneau moteurs
coupés. Garer alors le panneau à plat (élévation 90°).

**Ce qui devient obligatoire**
* **Roulements ZZ uniquement.** Les joints d'un 2RS freinent : 0,008 N·m pour la paire de 685
  (le quart du couple du moteur !) et 0,15 N·m pour la paire de 6806 d'azimut. Avec des 2RS,
  la marge de l'azimut à 10 m/s tomberait à ×0,9.
* **Graisse PTFE** sur les vis et les roues. À sec, la marge à 10 m/s passe sous ×1 (×0,8 en
  élévation, ×0,7 en azimut).
* **Dents en PETG** : à 0,5 à 0,6 N·m, la contrainte en pied de dent est d'environ **6 à 8 MPa**,
  contre 37 MPa moteur calé avec le NEMA 17. Les dents sont plus ménagées, et il n'y a pas de
  courant à limiter. Le fusible mécanique devient le réducteur plastique du 28BYJ-48 lui-même.
* **Fluage** : avec le contrepoids, la pesanteur ne charge plus la denture. Garer à plat reste
  conseillé pour le vent.

## 4. Le contrepoids

Le contrepoids est **celui qui avait été étudié pour la version NEMA** (commit `3cdd766` de
l'historique git, retiré ensuite de la version principale) : il n'est pas à redessiner, seulement
à adapter aux inserts.

| Élément | Valeur |
|---|---|
| Bloc d'acier doux | 30 × 70 × 55 mm, **905 g**, centré à 100 mm sous l'axe d'élévation, décalé de 3 mm en Y, côté +X (le côté −X est pris par le moteur d'azimut) |
| Partie qui bascule | 2,46 kg, centre de gravité à (31 ; 0,0 ; 0,0) mm : **sur l'axe d'élévation** |
| Platine imprimée | PETG, 4 mm, 41 g, vissée sur le flanc +X du chapeau (4 vis M3×8) ; le bloc est vissé sur la platine (4 vis M3×10, taraudages M3 de 9 mm dans le bloc) |
| Garde mini | 2 mm sur toute la course ; aucune interférence (vérifié sur la CAO du commit `3cdd766`) |

**Réglage à la pesée.** 1 % de masse du bloc (9 g) déplace le centre de gravité de 0,37 mm. Couper
le bloc, le peser et le limer sur sa hauteur jusqu'à **905 g à ± 2 %** : l'erreur restante est de
0,02 N·m au plus. Contrôle : poser la partie basculante sur ses deux pivots, sur deux appuis de
même hauteur : elle doit rester dans **n'importe quelle position**.

**À adapter dans cette variante** : les inserts à chaud. Dans le flanc du chapeau, les 4 trous de
la platine deviennent des trous d'insert M3×3 (Ø4,0 × 3,8 mm, flanc de 6 mm donc 2,2 mm de
matière derrière).

**Effet sur le trépied.** Charge sur la rotule : environ 3,3 kg dans la version NEMA, avec le
contrepoids. Les moteurs 28BYJ-48 pèsent environ 0,34 kg de moins que les NEMA, donc la
stabilité est un peu meilleure que les valeurs de la version à contrepoids (vent de basculement
de 31, 41 et 60 km/h avec 0, 3 et 11 kg de lest, pente de 8,8°, 14,9° et 27,0°). **À recalculer
avec `scripts/verification_stabilite.py` une fois la CAO faite.** Le lest et le trépied ne sont
pas modifiés.

## 5. Ce qui change dans la mécanique

| Pièce | Changement |
|---|---|
| `Support_Moteur_Elevation`, `Support_Moteur_Azimut` | **À redessiner** pour un moteur de Ø28 mm : deux oreilles à 35 mm d'entraxe, trous Ø3,4 (M3 passent dans les trous Ø4,2 des oreilles), corps Ø28 mm dans un logement, arbre décentré de 8 mm sur l'axe de la vis. La face avant du moteur est plus proche de l'accouplement que celle d'un NEMA (arbre de 6 mm au lieu de 23,5 et 20 mm). |
| Accouplement | Celui du projet (Ø19 × 25, alésage 12,5 mm de chaque côté) convient mal : l'arbre du 28BYJ-48 est court. Prendre un accouplement flexible **plus petit, Ø5 / Ø5, environ Ø14 × 25 mm** (`flexible shaft coupling 5mm 5mm D14 L25`), vis de serrage sur un méplat de l'arbre. À défaut, accouplement imprimé à alésage en D côté moteur, mais il tolère moins le défaut d'alignement. |
| `Chapeau_U` | 4 trous d'insert M3×3 dans le flanc +X pour la platine du contrepoids. |
| `Support_Contrepoids` | Pièce du commit `3cdd766`, à reprendre avec ses inserts. |
| Vis des moteurs | 2 vis M3 par moteur dans les oreilles (4 en tout), contre 4 M3×8 et 4 M2,5×6 dans la version NEMA. Longueur à fixer à la modélisation. |
| Reste | Roues, vis sans fin, paliers, pivots, roulements, chape, socle, fond, capteur solaire : **inchangés**. |

## 6. Électronique

On remplace les deux **TMC2209** (et leur 12 V) par deux **cartes ULN2003** alimentées en 5 V,
fournies avec le moteur dans les kits courants.

**Problème de broches.** Le Heltec V4 n'a que 9 broches libres, toutes utilisées (voir le README
du cas terrestre, § 6). La version NEMA en consacre 5 aux moteurs (STEP_EL 47, DIR_EL 43,
STEP_AZ 48, DIR_AZ 45, EN 33). Un 28BYJ-48 sur ULN2003 en demande **4 par moteur, soit 8**. Il en
manque 3.

**Solution : un MCP23017** (16 sorties, sur l'I²C déjà en place) :
* alimenté en **3,3 V**, adresse **0x20** (A0, A1, A2 à la masse), aucun conflit avec les
  adresses 0x48, 0x40 et 0x45 déjà présentes ;
* ses 8 sorties pilotent IN1 à IN4 des deux cartes ULN2003 ; les 5 broches du Heltec libérées
  (47, 43, 48, 45, 33) restent disponibles ;
* **8 résistances de 10 kΩ vers la masse** sur les sorties : à la mise sous tension, le MCP23017
  a ses sorties en haute impédance, et sans tirage une bobine pourrait s'allumer au démarrage ;
* alternative : un 74HC595 (3 broches : données, horloge, verrou) plus une 4ᵉ pour OE.

| Signal | Vers |
|---|---|
| MCP23017 GPA0 à GPA3 | IN1 à IN4 de la carte d'élévation |
| MCP23017 GPB0 à GPB3 | IN1 à IN4 de la carte d'azimut |
| 5 V (sortie de U1, **avant la diode D1**, comme le capteur Hall) | broche + des deux cartes ULN2003 |
| 0 V | broche − des deux cartes, 0 V du boîtier |

**Alimentation.** Un 28BYJ-48 tire environ 0,2 A à 5 V. Le mini abaisseur U1 doit donc fournir
au moins **0,6 A** (Heltec, Hall, un moteur) : vérifier la référence du module. **Ne jamais
faire tourner les deux moteurs ensemble** : le suivi corrige l'élévation, puis l'azimut. Le
12 V n'alimente plus que U1 : la batterie, le régulateur et les wattmètres ne changent pas.
Le 100 µF des anciens drivers n'est plus utile ; garder 100 µF sur le 5 V des cartes.

**À l'arrêt, les 8 sorties à 0** : une bobine alimentée en continu dissipe environ 1 W et
chaufferait le support en PETG. Les vis sans fin tiennent le panneau moteurs coupés, comme dans
la version principale. Les sorties sont mises à 0 entre deux corrections.

**Séquence demi-pas** (ordre des fils de la carte ULN2003, IN1 à IN4 sur les bits 0 à 3 du
quartet de chaque moteur) :

```cpp
// 8 phases pour un 28BYJ-48 sur ULN2003 : IN1 = bit 0 ... IN4 = bit 3
const uint8_t PHASES[8] = {0b0001, 0b0011, 0b0010, 0b0110, 0b0100, 0b1100, 0b1000, 0b1001};
// une phase = une écriture I2C de 2 octets (registre OLATA ou OLATB du MCP23017)
// pour tourner à l'envers : parcourir le tableau dans l'autre sens
// vitesse : 120 phases par seconde (environ 1,8 tr/min de l'arbre de sortie), pas plus tant
// que le couple n'a pas été mesuré à plus haute fréquence
```

Les 4 bobines sont brochées dans l'ordre bleu, rose, jaune, orange pour IN1 à IN4 sur les cartes
courantes : **vérifier le sens et l'ordre sur le moteur reçu**, une inversion fait vibrer l'arbre
sans le faire tourner.

Fin de course d'élévation, Hall d'azimut, capteur solaire (ADS1115), wattmètres, LoRa : **sans
changement**.

## 7. Nomenclature : ce qui change

| Retiré (version NEMA) | Ajouté (variante 28BYJ-48) |
|---|---|
| NEMA 17 (Usongshine 17HS3401), NEMA 11 (11HS18-0674S) | 2 × **28BYJ-48 5 V**, avec leurs cartes ULN2003 |
| 2 × driver TMC2209 | 1 × **MCP23017** (module ou composant) + 8 × 10 kΩ |
| 2 × accouplement flexible 5 mm / 5 mm, Ø19 × 25 | 2 × accouplement flexible **Ø5 / Ø5, Ø14 × 25 mm** (ou imprimé) |
| 4 × M3×8 + 4 × M2,5×6 (moteurs) | 4 × M3 (oreilles des moteurs) |
| | **Contrepoids** : bloc d'acier doux 30 × 70 × 55 mm (≈ 0,9 kg), platine imprimée, 4 × M3×8, 4 × M3×10, 4 inserts M3×3 |

Le coût des moteurs et des drivers baisse nettement (deux 28BYJ-48 avec cartes valent quelques
euros pièce), le bloc d'acier est peu cher. Tout le reste de la nomenclature est celui de
[`Liste-composants.md`](../Liste-composants.md).

## 8. À valider sur le banc avant de modéliser

1. **Mesurer le couple réel de chaque moteur**, avant tout montage : arbre horizontal, un bras
   de 100 mm fixé sur l'arbre, une masse accrochée au bout. À 5 V et 120 phases/s, le moteur doit
   lever **25 g** (prudent) et idéalement **35 g** (nominal) sans perdre de pas. Si un moteur
   n'y arrive pas, le changer : ils sont très dispersés.
2. **Contrôler le couple à la roue** une fois la tête assemblée (avec le contrepoids) : accrocher
   une masse de 300 g à 100 mm de l'axe d'élévation (0,29 N·m, ce que le moteur doit encore
   vaincre à sec) ; le moteur doit faire tourner la roue.
3. **Vérifier l'équilibre** du contrepoids (pesée, puis les deux appuis, § 4).
4. **Mesurer l'arbre du 28BYJ-48** (longueur, méplats, décentrage) avant de dessiner les supports.
5. **Tester la fréquence maximale** : monter peu à peu de 120 à 300 phases/s. Le couple baisse
   avec la fréquence : si le moteur décroche à 200, ne pas aller au-delà de 120.

## 9. Pour aller plus loin

* **Gagner du couple**, au prix d'un montage moins simple : la version **bipolaire** du
  28BYJ-48 (on coupe la liaison du fil rouge commun sur le moteur) est souvent citée pour donner
  un meilleur couple, mais il faut la mesurer ; elle demande un driver bipolaire (A4988, DRV8833)
  et 4 broches par moteur.
* **Augmenter le couple à la roue** en gardant les moteurs : agrandir la vis d'élévation (plus de
  dents). Cela coûte en vitesse et en place.
* **Garer à plat** (élévation 90°) dès que le vent dépasse la limite de 6 m/s : le panneau
  prend alors beaucoup moins le vent, et la version à contrepoids reste stable (voir § 4).
