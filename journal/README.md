# Journal d'entraînement

C'est le fichier le plus important du projet. **Sans journal, l'agent ne peut pas adapter tes séances** : il ne saura pas quelles charges tu utilises, ce qui progresse, ce qui stagne, ni comment tu récupères. Il ne pourra que te redonner le programme de départ.

## Convention de nommage

```
journal/2026-09-29-seance-1.md
journal/2026-09-30-seance-2.md
journal/2026-10-02-seance-3.md
journal/2026-10-03-seance-4.md
```

Toujours au format `AAAA-MM-JJ-seance-N.md`. Le tri alphabétique correspond alors au tri chronologique, et l'agent retrouve immédiatement la dernière séance de chaque groupe musculaire.

## Comment remplir

**Le plus simple** : ne remplis rien pendant la séance. Note tes charges et tes répétitions sur ton téléphone dans les notes, ou photographie l'écran de la machine. En rentrant, dis à l'agent :

> « J'ai fait la séance 1 aujourd'hui. Presse à pecs 3 séries de 12 à 25 kg, développé incliné 10-10-9 à 10 kg, pec deck 15-15-13 à 20 kg, développé épaules 12-11-10 à 15 kg, élévations latérales 15-15-15 à 4 kg, triceps corde 15-14-12 à 15 kg. J'ai dormi 7 h, énergie 8/10, pas de douleur. »

Il créera le fichier, le remplira, mettra à jour les charges de référence dans `profil.md` et te dira quoi viser la prochaine fois.

**Si tu préfères écrire toi-même** : copie [MODELE-seance.md](MODELE-seance.md) et remplis-le.

## Le minimum vital

Si tu ne notes qu'une seule chose, note **la charge et les répétitions de chaque série**. C'est ce qui pilote la progression.

Si tu peux en noter trois de plus, par ordre d'utilité :

1. **Les répétitions en réserve (RIR)** — sans elles, on ne sait pas si tu peux monter la charge
2. **La qualité technique sur 5** — c'est ce qui empêche de monter trop vite
3. **Tes heures de sommeil et ton énergie** — c'est ce qui permet d'expliquer une mauvaise séance autrement que par « je stagne »

## Ce que l'agent en fait

| Donnée du journal | Ce qu'elle déclenche |
|---|---|
| Charges et répétitions | La double progression : quand monter, de combien |
| Technique /5 | Un blocage de la progression si la technique est en dessous de 4 |
| Sommeil, énergie, courbatures | Le classement vert / orange / rouge de la séance suivante |
| 3 séances sans progrès sur un exercice | Le protocole de stagnation de `progression.md` |
| 2 séances orange ou rouge dans la semaine | Le déclenchement anticipé d'une semaine allégée |
| Réglages en crans | Un gain de temps réel à la salle, et des charges comparables d'une semaine à l'autre |
| Machines indisponibles | Des substitutions prêtes à l'avance pour tes horaires |
| Douleurs récurrentes | Un changement d'exercice, ou une orientation vers un professionnel de santé |
