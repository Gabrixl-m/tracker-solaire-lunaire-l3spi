# Optimisation de l'angle φ des jambes du trépied

Générée par `optimisation_angle.py` à partir des masses et centres de gravité de la CAO.

## Données fixées par la tête et le panneau

- Jambes en Y, à 120°. Articulation haute à r = 70 mm, z = 509 mm : juste sous le socle de la tête. Le panneau vertical descend jusqu'à 571 mm et tout le trépied doit rester en dessous.
- Centre de la rotule de pied à z = 40 mm, soit une hauteur de jambe h = 469 mm.
- Tête + panneau : 2.77 kg. Le centre de gravité est pris dans la pire orientation du panneau (élévation de −2° à +92°, azimut sur 360°).

## Exigences

| Exigence | Valeur |
|---|---|
| Pente maxi sans ancrage (C1) | 15° |
| Obstacle ou enfoncement sous un pied (C1) | 50 mm |
| Marge de sécurité au basculement (C1) | 5° |
| Pente rattrapée par les jambes télescopiques (C2) | 10° |
| Recouvrement mini des tubes (C2) | 45 mm |

## Résultats selon φ

| φ | Ø des pieds | Jambe | Masse trépied | Basculement | Exigé (C1) | Course ± nécessaire / possible (C2) | Poussée entretoise | Rigidité latérale | Admissible |
|---|---|---|---|---|---|---|---|---|---|
| 25.0° | 577 mm | 517 mm | 4.24 kg | 20.3° | 26.6° | 56 / 111 mm | 0.47 × charge | 42 % | non (C1) |
| 27.5° | 628 mm | 529 mm | 4.27 kg | 22.0° | 26.1° | 62 / 115 mm | 0.52 × charge | 49 % | non (C1) |
| 30.0° | 682 mm | 542 mm | 4.30 kg | 23.8° | 25.6° | 69 / 119 mm | 0.58 × charge | 56 % | non (C1) |
| **32.0°** | 726 mm | 553 mm | 4.33 kg | 25.3° | 25.2° | 75 / 123 mm | 0.62 × charge | 62 % | oui |
| 32.5° | 738 mm | 556 mm | 4.33 kg | 25.6° | 25.2° | 77 / 124 mm | 0.64 × charge | 63 % | oui |
| 35.0° | 797 mm | 573 mm | 4.37 kg | 27.5° | 24.8° | 86 / 129 mm | 0.70 × charge | 70 % | oui |
| 37.5° | 860 mm | 591 mm | 4.41 kg | 29.5° | 24.4° | 96 / 135 mm | 0.77 × charge | 76 % | oui |
| 40.0° | 927 mm | 612 mm | 4.45 kg | 31.5° | 24.1° | 107 / 142 mm | 0.84 × charge | 82 % | oui |
| 42.5° | 1000 mm | 636 mm | 4.51 kg | 33.7° | 23.8° | 120 / 150 mm | 0.92 × charge | 87 % | oui |
| 45.0° | 1078 mm | 663 mm | 4.56 kg | 35.9° | 23.5° | 134 / 159 mm | 1.00 × charge | 92 % | oui |
| 47.5° | 1164 mm | 694 mm | 4.63 kg | 38.2° | 23.3° | 152 / 170 mm | 1.09 × charge | 95 % | oui |
| 50.0° | 1258 mm | 730 mm | 4.70 kg | 40.6° | 23.0° | 173 / 182 mm | 1.19 × charge | 98 % | non (C3) |
| 52.5° | 1362 mm | 770 mm | 4.79 kg | 43.1° | 22.8° | 197 / 195 mm | 1.30 × charge | 100 % | non (C2, C3) |
| 55.0° | 1480 mm | 818 mm | 4.89 kg | 45.8° | 22.6° | 227 / 211 mm | 1.43 × charge | 100 % | non (C2, C3) |
| 57.5° | 1612 mm | 873 mm | 5.02 kg | 48.7° | 22.4° | 265 / 229 mm | 1.57 × charge | 99 % | non (C2, C3) |
| 60.0° | 1765 mm | 938 mm | 5.17 kg | 51.7° | 22.2° | 311 / 251 mm | 1.73 × charge | 97 % | non (C2, C3) |

**Plage admissible : φ de 32.0° à 49.0°. Optimum : φ = 32.0°**, le plus petit angle admissible, donc les jambes les plus courtes et les plus légères, la poussée la plus faible dans les entretoises, la plus petite course de nivelage et la plus petite emprise au sol.

La rigidité latérale est maximale à 54,7°, mais elle ne dimensionne pas sur la Lune : sans vent, seuls les pas des moteurs et les manipulations l'excitent.

## Sensibilité de l'optimum aux exigences

| Variante | φ optimal |
|---|---|
| Exigences de référence | 32.0° |
| Pente sans ancrage 10° | 26.5° |
| Pente sans ancrage 20° | 37.5° |
| Sans obstacle sous un pied | 25.0° |
| Obstacle de 100 mm | 37.0° |
| Marge de 10° | 37.5° |
| Nivelage sur 15° | 32.0° |

