# Optimisation de l'angle φ des jambes du trépied

Générée par `optimisation_angle.py` à partir des masses et centres de gravité de la CAO.

## Données fixées par la tête et le panneau

- Jambes en Y, à 120°. Articulation haute à r = 70 mm, z = 480 mm : juste sous l'embase de la tête. Le panneau vertical descend jusqu'à 571 mm et tout le trépied doit rester en dessous.
- Centre de la rotule de pied à z = 40 mm, soit une hauteur de jambe h = 440 mm.
- Tête + panneau : 4.99 kg. Le centre de gravité est pris dans la pire orientation du panneau (élévation de −2° à +92°, azimut sur 360°).

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
| 25.0° | 550 mm | 485 mm | 4.21 kg | 16.9° | 26.9° | 54 / 100 mm | 0.47 × charge | 42 % | non (C1) |
| 27.5° | 598 mm | 496 mm | 4.24 kg | 18.5° | 26.4° | 59 / 104 mm | 0.52 × charge | 49 % | non (C1) |
| 30.0° | 648 mm | 508 mm | 4.26 kg | 20.1° | 25.9° | 66 / 108 mm | 0.58 × charge | 56 % | non (C1) |
| 32.5° | 701 mm | 522 mm | 4.30 kg | 21.8° | 25.4° | 73 / 112 mm | 0.64 × charge | 63 % | non (C1) |
| 35.0° | 756 mm | 537 mm | 4.33 kg | 23.6° | 25.0° | 81 / 117 mm | 0.70 × charge | 70 % | non (C1) |
| **37.0°** | 803 mm | 551 mm | 4.36 kg | 25.0° | 24.7° | 89 / 122 mm | 0.75 × charge | 75 % | oui |
| 37.5° | 815 mm | 555 mm | 4.37 kg | 25.4° | 24.7° | 91 / 123 mm | 0.77 × charge | 76 % | oui |
| 40.0° | 878 mm | 574 mm | 4.41 kg | 27.3° | 24.3° | 101 / 130 mm | 0.84 × charge | 82 % | oui |
| 42.5° | 946 mm | 597 mm | 4.46 kg | 29.3° | 24.0° | 113 / 137 mm | 0.92 × charge | 87 % | oui |
| 45.0° | 1020 mm | 622 mm | 4.51 kg | 31.4° | 23.7° | 127 / 146 mm | 1.00 × charge | 92 % | oui |
| 47.5° | 1100 mm | 651 mm | 4.57 kg | 33.6° | 23.5° | 144 / 155 mm | 1.09 × charge | 95 % | non (C3) |
| 50.0° | 1189 mm | 685 mm | 4.65 kg | 35.9° | 23.2° | 163 / 167 mm | 1.19 × charge | 98 % | non (C3) |
| 52.5° | 1287 mm | 723 mm | 4.73 kg | 38.4° | 23.0° | 186 / 179 mm | 1.30 × charge | 100 % | non (C2, C3) |
| 55.0° | 1397 mm | 767 mm | 4.82 kg | 41.0° | 22.7° | 215 / 194 mm | 1.43 × charge | 100 % | non (C2, C3) |
| 57.5° | 1521 mm | 819 mm | 4.94 kg | 43.8° | 22.5° | 250 / 211 mm | 1.57 × charge | 99 % | non (C2, C3) |
| 60.0° | 1664 mm | 880 mm | 5.08 kg | 46.8° | 22.3° | 293 / 232 mm | 1.73 × charge | 97 % | non (C2, C3) |

**Plage admissible : φ de 37.0° à 46.0°. Optimum : φ = 37.0°**, le plus petit angle admissible, donc les jambes les plus courtes et les plus légères, la poussée la plus faible dans les entretoises, la plus petite course de nivelage et la plus petite emprise au sol.

La rigidité latérale est maximale à 54,7°, mais elle ne dimensionne pas sur la Lune : sans vent, seuls les pas des moteurs et les manipulations l'excitent.

## Sensibilité de l'optimum aux exigences

| Variante | φ optimal |
|---|---|
| Exigences de référence | 37.0° |
| Pente sans ancrage 10° | 31.0° |
| Pente sans ancrage 20° | 42.5° |
| Sans obstacle sous un pied | 30.0° |
| Obstacle de 100 mm | 41.5° |
| Marge de 10° | 42.5° |
| Nivelage sur 15° | aucun |

