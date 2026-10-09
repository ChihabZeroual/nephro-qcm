# Index des notions (analyse `data/course_text/*.md`)

Export lisible limité par la qualité d’extraction PDF. Les notions ci-dessous sont celles retenues pour la banque DEMS (texte médical exploitable).

## Hyperkaliémie (contenu riche — ~60 notions)

- **I Définition** : [K+] plasmatique > 5 mmol/l ; fausses hyperkaliémies (hémolyse, garrot, hyperleucocytose, thrombocytémie)
- **II Intérêt** : trouble fréquent (IRC, hémodialyse) ; urgence rythmique
- **III Physiologie** : répartition du K+ (muscle, hépatocytes, hématies, os, EC) ; transferts membranaires (insuline, catécholamines, alcalose, aldostérone vs acidose, hyperosmolarité)
- **IV Exploration** : kaliurèse, GTTK, QTCC, sécrétion tubulaire distale, DDP Na+/Cl-
- **V Clinique** : ECG (onde T, onde P, PR, QRS, TV/FV) ; neuromusculaire ; rénal (ammoniogenèse) ; digestif
- **VI Étiologie** : hypoaldostéronisme, pseudohypoaldostéronismes, Gordon, IRC, médicaments (IEC, ARAII, K+, héparine, bêtabloquants), transfert cellulaire (acidose, rhabdomyolyse, lyse)
- **VIII Traitement** : régime, arrêt médicaments, Kayexalate, calcium IV, insuline-glucose, dialyse, salbutamol

## Hypokaliémie (contenu riche — ~60 notions)

- **III Physiologie** : répartition et transferts du K+ (commun au cours K+)
- **IV Exploration** : kaliurèse, GTTK, tests (rénine, aldostérone, fludrocortisone, furosémide)
- **V Clinique** : ECG (ST, onde T, QT, arythmies) ; neuromusculaire ; digestif ; rénal (aquaporines, alcalose métabolique associée)
- **VI Étiologie** : hyperaldostéronisme (Conn, GRA), cortisol apparent minéralocorticoïde (11β-HSD, réglisse), DOC, Bartter, Gitelman, Liddle, déficit en magnésium, pertes digestives, tubulopathies
- **VIII Traitement** : aliments riches en K+, chlorure de K+, spironolactone, amiloride

## Hypercalcémie (extraction pauvre — 1 piste lisible)

- **VI Médicaments / toxiques cités** : lithium, calcium per os, vitamine A à forte dose, thiazidiques, amiloride, théophylline, tamoxifène, intoxication aluminique

## Acidose métabolique / Alcalose métabolique

- Texte français **non exploitable** dans `course_text` (fichiers PDF essentiellement binaires) → **0 QCM** générés (pas d’invention hors cours).

## Hypernatrémie / Hyponatrémie / Hypocalcémie / Hyperphosphatémie / Hypophosphatémie

- Très peu ou pas de phrases médicales lisibles après nettoyage → **0 QCM** pour l’instant (ré-export PDF amélioré nécessaire pour enrichir).

## Pipeline banque

1. `scripts/export_course_text.py` — PDF → `data/course_text/*.md`
2. `scripts/generate_dems_qcm.py` — cours → `data/dems_qcm/*.json`
3. `scripts/build_dems_bank.py` — fusion → `app/data/questions.json`
