# Néphro QCM Coach

Application web **responsive** (PC + téléphone) de révision QCM pour les **10 cours** du dossier :

- Acidose / alcalose métabolique
- Hyper/hypo : natrémie, kaliémie, calcémie, phosphatémie

## Démarrage

1. Générer la banque (1220 QCM) si besoin :

   ```bat
   scripts\run_generate.bat
   ```

2. Lancer l'application :

   ```bat
   start-app.bat
   ```

3. Ouvrir : [http://localhost:8080](http://localhost:8080)

   Sur téléphone (même Wi‑Fi) : `http://<IP-du-PC>:8080`

4. **Installer (PWA)** : menu du navigateur → « Ajouter à l'écran d'accueil ».

## Fonctionnalités

- 🩺 **Entraînement** : correction immédiate, explication A–E, 📌 à retenir, analyse des oublis vs faux choix
- 📝 **Examen** : chronomètre, correction à la fin
- 🔴 **Mes lacunes** / 🧠 **Je n'oublie plus** : sessions ciblées selon l'historique
- 📊 **Tableau de bord**, 📅 historique, ⭐ favoris, ❌ erreurs, 🔎 recherche, 📚 par cours
- **Profil de maîtrise** par `notion` (niveaux 0–5, répétition espacée) — stockage **local** (`localStorage`)

## Fichiers

| Chemin | Rôle |
|--------|------|
| `app/` | Interface PWA |
| `app/data/questions.json` | Banque générée |
| `scripts/generate_bank.py` | Générateur (seed 42) |
| `scripts/pdf_extract_stdlib.py` | Extraction texte PDF (optionnel) |
| `extracted/` | Textes extraits des PDF |

## Source des questions

Les QCM sont produits par `generate_bank.py` à partir d'un référentiel structuré aligné sur les thèmes des PDF. Les PDF PowerPoint compressés ne permettent pas toujours une extraction fiable ; vous pouvez enrichir le référentiel dans `generate_bank.py` puis regénérer.

## Progression

Toutes les données utilisateur restent **sur votre appareil** (aucun serveur requis).

## GitHub Pages (téléphone, partout)

Voir **`GITHUB_PAGES.md`** (workflow `.github/workflows/pages.yml` déjà prêt).  
URL finale : `https://VOTRE_USER.github.io/NOM_DU_REPO/`
