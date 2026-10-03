# Liste d'achats — démonstration sur Terre (tête imprimée en PETG)

Tout ce qu'il faut acheter pour **une tête rotative à vis sans fin** en version PETG, en plus
des pièces imprimées de `CAO/Demo_Terre_PETG/a_imprimer/` (voir README, § 12).
Les deux pivots d'élévation sont **imprimés** : le seul axe en acier à acheter est la tige Ø5
des arbres des vis sans fin.

* La colonne « À chercher » donne le nom à taper sur les sites marchands (AliExpress,
  Amazon, etc.), où ces pièces sont presque toujours vendues sous leur nom anglais.
* Les prix sont **indicatifs** (ordre de grandeur, par article).
* Les roulements sont en **rose** dans les fichiers 3D. Ils sont tous **protégés** : prendre
  de préférence la version **ZZ** (flasques métalliques), sinon 2RS (joints caoutchouc).

| Palier d'une vis sans fin | Axe d'élévation imprimé |
|---|---|
| ![Palier : joues, roulements, arbre, vis](docs/explications/palier_joues_roulements.png) | ![Axe d'élévation : pivots PETG, roulements 6801](docs/explications/axe_elevation.png) |

---

## 1. Mécanique

| Article | Caractéristiques | Qté | À chercher | Où il va | ≈ Prix |
|---|---|---|---|---|---|
| **Roulement 6806ZZ** (ISO 61806-2Z) | 30 × 42 × 7 mm | 2 | `6806ZZ bearing 30x42x7` (ou `61806ZZ`) | Azimut : dans le socle, autour du moyeu de la chape | 3 € |
| **Roulement 6801ZZ** (ISO 61801-2Z) | 12 × 21 × 5 mm | 2 | `6801ZZ bearing 12x21x5` (ou `61801ZZ`) | Élévation : dans les bras de la chape, sur les pivots imprimés Ø12 | 1–2 € |
| **Roulement 685ZZ** | 5 × 11 × **5** mm | 4 | `685ZZ bearing 5x11x5` | Deux par vis sans fin, dans les joues des paliers | 1 € |
| **Accouplement flexible 5 mm / 5 mm** | Alésages Ø5 des deux côtés, Ø19 × 25 mm, alu | 2 | `flexible shaft coupling 5mm x 5mm D19 L25` | Relie l'axe de chaque moteur à l'arbre de sa vis sans fin (la pièce bleue) | 2–4 € |
| **Tige acier rectifiée Ø5** | Ø5 mm, au moins 110 mm | 1 | `linear shaft 5mm 150mm` (ou `5mm chrome steel rod`) | À couper en **2 × 52,5 mm** : les arbres des deux vis sans fin | 3–5 € |

**Pièges à éviter** :
* **ZZ plutôt que 2RS** : les deux versions ont les mêmes cotes et vont toutes les deux
  dans les pièces. Mais les joints caoutchouc des 2RS frottent :
  * les deux 6806-2RS freinent l'azimut d'environ 0,15 N·m ;
  * la marge du moteur d'azimut au vent de 10 m/s passe alors de ×2,3 à ×1,6.

  Si tu as déjà des 2RS, ça marche, à condition de bien graisser les vis sans fin.
* **685** : prendre une version protégée, **ZZ** (ou 2RS). Le 685 « ouvert » ne fait que
  3 mm de large, alors que les joues sont prévues pour 5 mm.
* **Accouplement** : bien **5 mm des deux côtés**. Les modèles 5 mm / 8 mm, très courants,
  sont faits pour les vis trapézoïdales d'imprimante 3D.
* **6801** : c'est un roulement fin (5 mm de large), à ne pas confondre avec le 6001
  (12 × 28 × 8), plus gros. Vérifier **12 × 21 × 5** dans l'annonce.
* **Pas d'axe Ø8** : les pivots d'élévation sont les pièces imprimées `Pivot_Entraine`
  et `Pivot_Libre`, en Ø12. Un pivot PETG de Ø8 casserait sous le couple de la roue.

## 2. Moteurs et électronique

| Article | Caractéristiques | Qté | À chercher | Rôle | ≈ Prix |
|---|---|---|---|---|---|
| **Moteur pas à pas NEMA 17, 34 mm** | 42 × 42 × 34 mm, **0,28 N·m**, 1,3 A, axe Ø5 à méplat | 1 | `17HS3401 stepper motor 0.28Nm` | Élévation | 10–15 € |
| **Moteur pas à pas NEMA 11, 45 mm** | 28 × 28 × 45 mm, 0,095–0,10 N·m, 0,67 A, axe Ø5 | 1 | `11HS18-0674S nema 11 stepper` | Azimut | 15–25 € |
| **Driver TMC2209** | Module UART, 3,3 V logique | 2 | `TMC2209 stepper driver UART` | Un par moteur | 4–6 € |
| **ESP32** | Carte de développement ESP32-WROOM-32 | 1 | `ESP32 DevKitC WROOM-32` | Commande des deux moteurs | 6–10 € |
| **Alimentation 12 V** | En intérieur : bloc secteur 12 V 3 A. En extérieur : batterie LiFePO4 4S 12,8 V | 1 | `12V 3A power supply` / `LiFePO4 12V battery` | Puissance des moteurs | 10 € / 40–80 € |
| **Abaisseur 12 V → 5 V** | Module à découpage, 1 A au moins | 1 | `LM2596 buck converter` (ou `MP1584`) | Alimente l'ESP32 | 2 € |
| **Condensateur 100 µF 25 V** | Électrolytique | 2 | `100uF 25V capacitor` | Un au plus près de chaque driver | 0,2 € |
| **Fin de course** | Micro-switch à levier | 1 | `KW12 micro limit switch` (ou `endstop switch`) | Origine de l'élévation, en butée basse | 1 € |
| **Capteur à effet Hall + aimant** | Capteur A3144 (ou module KY-003) + aimant néodyme 5 × 2 mm | 1 + 1 | `A3144 hall sensor`, `neodymium magnet 5x2mm` | Origine de l'azimut | 2 € |
| **Câbles** | Câbles moteurs 4 fils (souvent fournis avec les moteurs), fils Dupont, câble souple 4 fils d'environ 1,5 m | — | `stepper motor cable 4 pin`, `dupont wires` | Liaisons | 5 € |

Le câblage (broches de l'ESP32, réglage des TMC2209, bibliothèques) est décrit dans le
README, § 2, « Commande par ESP32 ».

## 3. Visserie

| Article | Qté | Où |
|---|---|---|
| Vis CHC M3 × 6 (ISO 4762) | 1 | Vis anti-rotation du socle sur la colonne |
| Vis CHC M3 × 8 | 6 | Rondelle d'arrêt du moyeu (2), NEMA 17 sur son support (4) |
| Vis CHC M3 × 10 | 4 | Palier et support du moteur d'azimut, par-dessus la chape |
| Vis CHC M3 × 12 | 7 | Chape sur le moyeu (3), palier et support d'élévation (4) |
| Vis CHC M3 × 14 | 8 | Rails sur le chapeau (4, par-dessus, têtes noyées), cadre du panneau sur les rails (4, par-dessous, têtes noyées) |
| Vis CHC M3 × 25 | 3 | Fond du socle |
| **Vis à tête fraisée M3 × 8** (ISO 10642) | 3 | Roue d'azimut sur le socle (doivent affleurer) |
| Vis CHC M2,5 × 8 | 4 | NEMA 11 sur son support |
| **Vis sans tête M3 × 4** (bout plat) | 2 | Blocage de chaque vis sans fin sur son arbre |
| Écrou M3 (ISO 4032) | 4 | Dans le cadre du panneau, sur l'aile arrière : un par vis des rails |

Le plus simple est d'acheter un coffret :
* **vis CHC M3** (`M3 socket head screw assortment`) ;
* **M2,5** ;
* quelques **vis fraisées M3 × 8** (`M3 countersunk screw 8mm`) ;
* **vis sans tête M3 × 4** (`M3x4 set screw`) ;
* **écrous M3** (`M3 hex nut`).

Dans le PETG, les vis M3 se vissent directement dans les avant-trous Ø2,8, sans taraudage.
Compter 10 à 15 € en tout.

## 4. Pièces métalliques non imprimées

| Article | Caractéristiques | Qté | À chercher | Remarque |
|---|---|---|---|---|
| **Rails du panneau** | Barre alu 12 × 12 mm, 2 × 253 mm | 2 | `aluminium square bar 12mm` | Le modèle prévoit 12 × 13 mm : avec une barre de 12 × 12, ajouter une rondelle de 1 mm entre chaque rail et le chapeau. Percer 4 trous Ø3,4 par rail : 2 à 14 mm de part et d'autre du milieu (vis du chapeau, lamage Ø6 × 3,5 dessus) et 1 à 6 mm de chaque bout (vis du panneau, lamage Ø6 × 3,5 dessous) |
| **Cadre du panneau** (le tien) | — | — | — | Percer 4 trous Ø3,4 dans l'aile arrière des deux grands côtés, au droit des rails : à 44 mm de part et d'autre du milieu, et à 6 mm du bord extérieur. L'aile doit faire au moins 10 mm de large |

## 5. Consommables

| Article | Qté | À chercher | ≈ Prix |
|---|---|---|---|
| **Filament PETG 1,75 mm** (teinte claire de préférence) | 1 bobine de 1 kg (environ 300 g utilisés) | `PETG filament 1.75mm 1kg` | 20 € |
| **Graisse PTFE** (vis sans fin et roues : obligatoire en PETG ; pas les roulements, graissés d'origine) | 1 tube | `PTFE grease` | 8 € |
| Colle cyanoacrylate (optionnel : vis sans fin sur leur arbre, pivots imprimés dans le chapeau) | 1 | `super glue` | 3 € |

## 6. Optionnel

| Article | Qté | Pour quoi |
|---|---|---|
| Lest de 2 à 3 kg (sac de sable, bouteille d'eau) | 1 | Démonstration en extérieur, contre le vent |

---

**Ordre de grandeur total** : environ **100 à 150 €** avec une alimentation secteur, sans
compter le trépied ni le panneau. Il faut ajouter environ 50 € pour une batterie LiFePO4
destinée à la démonstration en extérieur.
