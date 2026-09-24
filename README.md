# Mon coach de musculation

Un agent Cursor qui connaît mon programme, m'explique chaque machine en détail, et adapte mes séances en fonction de ma progression et de mon état.

## La page à emmener à la salle

**[`programme.html`](programme.html)** — une page unique avec un onglet par séance, à ouvrir sur ton téléphone. Double-clic sur le fichier, ou glisse-le dans ton navigateur. Aucune connexion nécessaire, tout est dans le fichier.

| Onglet | Contenu |
|---|---|
| Séance 1 → Séance 4 | Le tableau des exercices, puis les fiches techniques dépliables |
| Échauffement · Abdos | Les blocs à faire avant et après |
| Prises & réglages · Progression · Nutrition & cardio | Les références |

Ce qu'elle apporte par rapport aux fichiers Markdown : un **minuteur de repos** en bas de l'écran (45 s à 3 min, avec un bip), les fiches techniques **dépliables** pour ne voir que l'exercice en cours, et un lien depuis chaque ligne du tableau vers la fiche correspondante.

> La page est **générée** depuis les fichiers Markdown, qui restent la source de vérité. Après toute modification du programme : `python3 outils/build-html.py`

## Comment on s'en sert

Ouvre une conversation dans ce projet et parle normalement. L'agent charge tout seul ses instructions, mon profil et mon journal.

| Ce que tu dis | Ce qu'il fait |
|---|---|
| « Quelle séance je fais aujourd'hui ? » | Regarde où tu en es dans la rotation, te demande comment tu te sens, et adapte la séance en conséquence |
| « Comment on tient la barre du tirage vertical ? » | Te donne la prise exacte, les réglages, les erreurs à éviter et une vidéo |
| « J'ai fini la séance 2, voilà mes charges… » | Écrit le fichier de journal, met à jour tes charges de référence, te dit quoi viser la prochaine fois |
| « J'ai mal dormi et j'ai des courbatures partout » | Classe la journée en orange ou rouge et allège la séance, ou te propose de la décaler |
| « Je stagne sur la presse à pecs » | Applique le protocole de stagnation : technique, sommeil, tempo, volume, puis changement d'exercice |
| « Fais le bilan de ma semaine » | Volume réalisé, ce qui progresse, ce qui bloque, et **une seule** modification pour la semaine suivante |
| « Je n'ai que 40 minutes » | Te dit quels exercices supprimer en priorité et lesquels garder absolument |
| « La machine est prise » | Te donne une substitution équivalente |

## Le programme en un coup d'œil

4 séances par semaine, une par groupe musculaire, avec des abdos en fin de chaque séance.

| Séance | Contenu | Détail |
|---|---|---|
| **S1** | Pecs · Triceps · Épaules | [programme/seance-1-pecs-triceps-epaules.md](programme/seance-1-pecs-triceps-epaules.md) |
| **S2** | Dos · Biceps | [programme/seance-2-dos-biceps.md](programme/seance-2-dos-biceps.md) |
| **S3** | Jambes | [programme/seance-3-jambes.md](programme/seance-3-jambes.md) |
| **S4** | Complémentaire : chaîne postérieure, épaules arrière, mouvements libres, cardio | [programme/seance-4-complementaire.md](programme/seance-4-complementaire.md) |

Rythme conseillé : `Lun S1 · Mar S2 · Mer repos · Jeu S3 · Ven S4 · week-end repos`

## Par où commencer

1. **Lis [guide-machines/00-prises-et-vocabulaire.md](guide-machines/00-prises-et-vocabulaire.md)** — 10 minutes, une seule fois. Après ça tu comprends n'importe quelle consigne de prise dans n'importe quelle vidéo.
2. **Complète [profil.md](profil.md)** : ton poids et ton tour de taille de départ.
3. **Lis la fiche de la séance 1** et les fiches techniques des 6 exercices, la veille de ta première séance.
4. **Fais la première séance très léger.** Les deux premières semaines servent à apprendre les mouvements, pas à performer.
5. **Note tes charges** et raconte ta séance à l'agent en rentrant. C'est ce qui déclenche tout le reste.

## Contenu du projet

```
├── programme.html                   La page à onglets à emmener à la salle (générée)
├── profil.md                        Mon niveau, mon objectif, mes charges de référence, mes mesures
├── programme/
│   ├── echauffement.md              10 min avant chaque séance + retour au calme
│   ├── seance-1-pecs-triceps-epaules.md
│   ├── seance-2-dos-biceps.md
│   ├── seance-3-jambes.md
│   ├── seance-4-complementaire.md
│   ├── abdos.md                     4 blocs différents, un par séance
│   └── nutrition-et-cardio.md       Recomposition : déficit, protéines, dosage du cardio
├── guide-machines/
│   ├── 00-prises-et-vocabulaire.md  Les 4 prises, le tempo, les réglages universels
│   ├── pecs-triceps-epaules.md      Fiches détaillées des 6 exercices de S1
│   ├── dos-biceps.md                                          … de S2
│   ├── jambes.md                                              … de S3
│   └── complementaire.md                                      … de S4
├── journal/
│   ├── README.md                    Pourquoi et comment tenir le journal
│   └── MODELE-seance.md             Le modèle à copier
├── outils/
│   └── build-html.py                Régénère programme.html depuis les .md
└── .cursor/skills/coach-musculation/
    ├── SKILL.md                     Les instructions de l'agent
    └── progression.md               Double progression, cycles de 4 semaines, stagnation, substitutions
```

## Ce que contient chaque fiche machine

Pour les 24 exercices du programme et les 9 exercices d'abdos :

**Muscles travaillés** · **Réglages de la machine, cran par cran** · **La prise exacte** : type, largeur, position des pouces, des poignets, où placer la poignée dans la main · **Position du corps** : pieds, bassin, dos, omoplates, tête · **Exécution** phase par phase · **Respiration** · **Tempo** chiffré · **Erreurs fréquentes** avec leur correction · **Sensation attendue**, et ce que tu ne dois pas sentir · **Quoi faire si ça fait mal** · **Deux vidéos**, une en français et une en anglais

## Avertissement

Ce projet donne des repères d'entraînement généraux. Ce ne sont pas des conseils médicaux.

Consulte un médecin avant de reprendre une activité physique si tu as un doute, et arrête immédiatement en cas de douleur vive, articulaire, persistante, ou de douleur thoracique. À la salle, les coachs sur place peuvent vérifier ta technique en direct : c'est gratuit, ils sont là pour ça, et aucun texte ni aucune vidéo ne remplace un œil extérieur sur tes trois premières séances.
