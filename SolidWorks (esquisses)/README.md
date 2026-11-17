# SolidWorks : les pièces imprimées du cas terrestre, avec leurs esquisses

[⬅ Retour au README principal](../README.md) · [Cas terrestre ➜](../Fichiers%203D%20%28CAO%29/Cas%20Terrestre%20%28d%C3%A9monstration%29/README.md)

Les fichiers STEP des 18 pièces imprimées n'ont **ni esquisses ni arbre de création** : SolidWorks
les ouvre comme des corps « importés », qu'on ne peut modifier qu'à coups de fonctions de
modification directe. Ce dossier permet de **refaire chaque pièce dans SolidWorks avec de vraies
esquisses et de vraies fonctions** (extrusions, enlèvements de matière, révolutions, balayage
hélicoïdal pour les filets), sans rien dessiner à la main : on lance une macro, une seule fois.

> **À savoir.** Un fichier `.SLDPRT` avec son arbre de création ne peut être écrit que par
> SolidWorks lui-même ; c'est pour cela que le dépôt contient une macro et pas les `.SLDPRT`.
> **La macro n'a pas pu être essayée ici** (pas de SolidWorks dans l'environnement de travail) :
> la géométrie qu'elle reçoit est vérifiée, la macro elle-même est à vérifier sur votre poste
> (voir « Si une pièce échoue »). Elle se contrôle toute seule après chaque fonction.

## Contenu

| Élément | Rôle |
|---|---|
| `Reconstruire_Pieces.bas` | la macro SolidWorks (VBA) |
| `donnees/<pièce>.txt` | pour chaque pièce, la liste des fonctions : plan d'esquisse, contours (segments, cercles, arcs, courbes), sens et longueur de l'extrusion, et le **volume et le centre de gravité attendus** après chaque fonction |
| `pieces/` | créé par la macro : un `.SLDPRT` par pièce et `journal.txt` |
| `../scripts/generate_esquisses_solidworks.py` | le script qui découpe les pièces et écrit `donnees/` (régénérable) |

## Utilisation

1. Ouvrir SolidWorks (pas besoin d'ouvrir un document) ; vérifier que les unités par défaut et le
   gabarit de pièce sont ceux de l'installation (la macro crée des pièces avec `NewPart`).
2. **Outils ▸ Macro ▸ Nouvelle…** (ou **Modifier**), enregistrer par exemple `essai.swp`, puis dans
   l'éditeur VBA : **Fichier ▸ Importer un fichier…** et choisir `Reconstruire_Pieces.bas`.
   Supprimer le module vide que SolidWorks avait créé s'il y en a un.
3. Garder le dossier `SolidWorks (esquisses)` **entier** : la macro lit `donnees\` à côté de
   `Reconstruire_Pieces.bas` ; si elle ne le trouve pas, elle demande où il est.
4. Lancer `main` (**F5**). Compter quelques minutes ; ne pas toucher à la fenêtre pendant ce temps.
5. À la fin, un message donne le bilan. Les pièces conformes sont dans `pieces\<nom>.SLDPRT`
   (et refermées) ; celles qui ont échoué s'appellent `<nom>_A_REPRENDRE.SLDPRT` et restent ouvertes.
   Tout est détaillé dans `pieces\journal.txt`.

Chaque pièce se retrouve ensuite avec son arbre : `Esquisse_01`, `Extrusion_01`,
`Enlevement_02`… On peut rouvrir une esquisse, changer une cote, ajouter une fonction.

## Comment c'est construit

- Chaque pièce est coupée en tranches le long d'un axe, aux hauteurs de ses sommets ; une tranche
  de section constante devient une extrusion. Ce qui a été comblé en trop (trous en travers,
  logements, cônes, fraisures) est retiré par des enlèvements de matière, extrudés ou de révolution.
- Les **filets des deux vis sans fin** sont refaits comme dans SolidWorks : un cercle, une hélice
  (pas π·m : 2,51 mm en azimut, 3,14 mm en élévation), un profil trapézoïdal de filet et un balayage le long de l'hélice,
  puis des enlèvements annulaires qui mettent le filet à longueur.
- Dans le script, chaque pièce reconstruite est **comparée à l'original** (différence de volume) ;
  le résultat est :

| Pièce | Fonctions | Écart de volume |
|---|---|---|
| Fond_Socle, Moyeu_Chape, Bague_Arret_Moyeu, Pivot_Libre, Pivot_Entraine, Roue_Elevation, Capteur_Solaire_Boitier, Capteur_Solaire_Support, Support_Moteur_Elevation, Palier_Vis_Elevation | 1 à 20 | < 0,001 % |
| Roue_Azimut_Fixe, Palier_Vis_Azimut, Support_Moteur_Azimut, Socle, Chapeau_U, Chape | 7 à 82 | < 0,001 % |
| Vis_Azimut, Vis_Elevation (filets) | 14 et 15 | 0,03 % et 0,001 % |

Pour les vis, le volume et le centre de gravité attendus après le balayage du filet sont calculés
par intégration numérique, et le centre de gravité final est recoupé avec la pièce d'origine (écart
0,0003 mm ; un filet à gauche donnerait 0,05 mm, ce qui permet de vérifier le sens de l'hélice).

## Contrôles faits par la macro

Après chaque fonction, la macro mesure le volume et le centre de gravité de la pièce et les compare
aux valeurs attendues du fichier. Si c'est faux (sens d'extrusion inversé, mauvais plan, hélice à
gauche…), elle supprime la fonction et essaie les autres réglages (8 pour une extrusion, 28 pour
l'hélice) ; elle retient ceux qui ont marché pour les fonctions suivantes. Si rien ne marche, la
fonction est notée en échec, **l'esquisse reste dans l'arbre** (renommée `…_A_REPRENDRE`) et la
macro passe à la suite.

## Si une pièce échoue

1. Ouvrir `pieces\journal.txt` : chaque fonction y est notée `OK` ou `ECHEC`, avec la cause connue
   (plan, extrusion, hélice) et, pour une extrusion, les cotes de départ et d'arrivée.
2. Les filets sont la partie la plus délicate de l'API de SolidWorks (hélice puis balayage). En cas
   d'échec, le cercle et le profil sont dans l'arbre : **Insertion ▸ Courbe ▸ Hélice/Spirale** sur
   le cercle (pas et hauteur dans `donnees/Vis_*.txt`, ligne `F ADD HEL`), puis **Bossage/Base balayé** avec le profil et
   l'hélice ; et les enlèvements de mise à longueur sont dans le fichier `donnees/Vis_*.txt`.
3. Sinon, envoyer `journal.txt` : la macro se corrige à partir de son contenu.

## Régénérer les données

```
python scripts/generate_esquisses_solidworks.py            # les 18 pièces
python scripts/generate_esquisses_solidworks.py Chape      # une seule
```

Le script lit `Fichiers 3D (CAO)/Cas Terrestre (démonstration)/a_imprimer/*.step`. À refaire si
une pièce imprimée change. Il a besoin de CadQuery (voir `requirements.txt`) et de quelques
minutes ; les deux vis sans fin utilisent beaucoup de mémoire (environ 1 Go).
