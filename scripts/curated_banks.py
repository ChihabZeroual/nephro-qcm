# -*- coding: utf-8 -*-
"""QCM DEMS rédigés à partir du texte extrait des PDF (cours CHU — pas de KDIGO externe)."""

CHAPTER = "Troubles hydro-électrolytiques et équilibre acido-basique"

# Les 7 autres PDF sont surtout en image : pas de texte fiable dans extracted/.
# Compléter après export texte/OCR (voir data/COURSES_PDF_LIMITATION.md).


def _q(
    topic: str,
    qid: str,
    question: str,
    options: dict,
    correct: list,
    explanation: dict,
    key_point: str,
    source_ref: str,
    notion: str,
    qtype: str = "knowledge",
    difficulty: int = 2,
    tags: list | None = None,
) -> dict:
    return {
        "id": qid,
        "chapter": CHAPTER,
        "topic": topic,
        "courseSlug": topic.replace(" ", "_"),
        "type": qtype,
        "question": question,
        "options": options,
        "correctAnswers": correct,
        "explanation": explanation,
        "keyPoint": key_point,
        "difficulty": difficulty,
        "tags": tags or [topic.split()[0].lower()],
        "notion": notion,
        "variantGroup": notion.lower().replace(" ", "-")[:40],
        "sourceRef": source_ref,
    }


def hyperkaliemie() -> list[dict]:
    t = "Hyperkaliémie"
    s = f"{t} —"
    out = []

    def add(notion, question, opts, correct, expl, kp, sec):
        out.append(
            _q(t, f"HK-{len(out)+1:02d}", question, opts, correct, expl, kp, f"{s} {sec}", notion)
        )

    add(
        "Définition",
        "Concernant l'hyperkaliémie, quelle proposition correspond au cours ?",
        {
            "A": "Elle se définit par une [K+] plasmatique > 5 mmol/l.",
            "B": "Elle se définit par une [K+] plasmatique > 6,5 mmol/l.",
            "C": "Elle se définit par une [K+] plasmatique < 3,5 mmol/l.",
            "D": "Elle correspond toujours à une hyperkaliémie vraie sans artefact.",
            "E": "Elle est définie uniquement sur l'ECG.",
        },
        ["A"],
        {
            "A": "Exact : seuil > 5 mmol/l cité dans le cours.",
            "B": "Faux : le seuil du cours est > 5 mmol/l.",
            "C": "Faux : cela décrit une hypokaliémie.",
            "D": "Faux : le cours insiste sur les fausses hyperkaliémies à écarter.",
            "E": "Faux : la définition est biologique ; l'ECG est un outil de gravité.",
        },
        "[K+] plasmatique > 5 mmol/l.",
        "I Définition",
    )

    add(
        "Fausses hyperkaliémies",
        "Quelles situations peuvent donner une fausse hyperkaliémie selon le cours ? (une ou plusieurs réponses)",
        {
            "A": "Hémolyse lors d'un prélèvement difficile ou garrot serré",
            "B": "Centrifugation tardive du prélèvement",
            "C": "Hyperleucocytose majeure (> 100 000/mm³)",
            "D": "Thrombocytémie > 10⁶/mm³",
            "E": "Hypoaldostéronisme primaire",
        },
        ["A", "B", "C", "D"],
        {
            "A": "Exact : cité parmi les causes de fausse hyperkaliémie.",
            "B": "Exact : cité dans le cours.",
            "C": "Exact : cité dans le cours.",
            "D": "Exact : cité dans le cours.",
            "E": "Faux : cause d'hyperkaliémie vraie, pas une fausse hyperkaliémie de prélèvement.",
        },
        "Écarter d'abord les fausses hyperkaliémies (prélèvement, leucocytes, plaquettes).",
        "I Définition — fausses hyperkaliémies",
    )

    add(
        "Distribution du potassium",
        "Concernant la distribution du potassium, quelle affirmation est exacte ?",
        {
            "A": "Environ 90 % du potassium est échangeable en 24 h.",
            "B": "Environ 2 % du potassium se trouve dans le compartiment extracellulaire.",
            "C": "Le muscle représente environ 78 % du potassium intracellulaire cité.",
            "D": "Le potassium est entièrement contenu dans le plasma.",
            "E": "La kaliémie normale du cours est 2,5–3,5 mmol/l.",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : 90 % échangeable en 24 h.",
            "B": "Exact : seulement 2 % dans le SEC.",
            "C": "Exact : muscle 78 % (hépatocytes 6 %, hématies 6 %).",
            "D": "Faux : la majeure partie est intracellulaire.",
            "E": "Faux : kaliémie 3,5–5 mmol/l dans le cours.",
        },
        "K+ surtout intracellulaire ; kaliémie 3,5–5 mmol/l.",
        "III Rappel physiologique — distribution",
    )

    add(
        "Transferts transmembranaires",
        "Quels facteurs favorisent l'entrée du K+ dans la cellule (baisse de kaliémie) selon le cours ?",
        {
            "A": "Insuline",
            "B": "Catécholamines",
            "C": "Alcalose",
            "D": "Aldostérone (effet sur les transferts cellulaires cité)",
            "E": "Acidose",
        },
        ["A", "B", "C", "D"],
        {
            "A": "Exact : facteur cité.",
            "B": "Exact : facteur cité.",
            "C": "Exact : facteur cité.",
            "D": "Exact : cité avec insuline et catécholamines.",
            "E": "Faux : l'acidose favorise la sortie du K+ vers l'extérieur.",
        },
        "Insuline, catécholamines, alcalose, aldostérone → entrée cellulaire du K+.",
        "III Rappel physiologique — balance interne",
    )

    add(
        "Balance externe",
        "Concernant la balance externe du potassium, quelle proposition est exacte ?",
        {
            "A": "Les pertes rénales représentent environ 90–95 % des sorties de K+ ingéré.",
            "B": "Les pertes fécales sont habituellement faibles (5–10 %).",
            "C": "Les pertes sudorales sont négligeables dans le cours.",
            "D": "L'excrétion rénale de K+ n'est pas régulée.",
            "E": "100 % du K+ filtré est réabsorbé sans sécrétion distale.",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : 90–95 % par voie rénale.",
            "B": "Exact : 5–10 % fécal en physiologie.",
            "C": "Exact : sueurs négligeables.",
            "D": "Faux : régulation rénale majeure.",
            "E": "Faux : sécrétion dans le TCC possible.",
        },
        "90–95 % des sorties de K+ sont rénales.",
        "III Rappel physiologique — balance externe",
    )

    add(
        "GTTK",
        "À propos du GTTK, quelle proposition correspond au cours ?",
        {
            "A": "Il est habituellement entre 6 et 12 chez le sujet sain.",
            "B": "Un GTTK < 10 traduit un GTTK inadapté.",
            "C": "Il reflète la capacité de sécrétion de K+ dans le TCC.",
            "D": "Un GTTK élevé signifie toujours une hypokaliémie.",
            "E": "Il ne dépend pas de la réabsorption de sodium dans le TCC.",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : 6–12 chez le sujet sain.",
            "B": "Exact : < 10 = inadapté.",
            "C": "Exact : lié à la sécrétion de K+ au TCC.",
            "D": "Faux : non affirmé ainsi dans le cours.",
            "E": "Faux : lié à la réabsorption de Na+ et au gradient.",
        },
        "GTTK normal 6–12 ; < 10 = inadapté.",
        "IV Exploration — GTTK",
    )

    add(
        "GTTK inadapté — mécanismes",
        "Un GTTK inadapté peut être lié selon le cours à :",
        {
            "A": "Une réabsorption trop lente de Na+ par rapport au Cl− dans le TCC",
            "B": "Une réabsorption trop rapide de Cl− par rapport au Na+ dans le TCC",
            "C": "Une diminution de la différence de potentiel transepithélial luminal négatif",
            "D": "Une hyperkaliémie par excès d'insuline uniquement",
            "E": "Une alcalose métabolique isolée sans autre mécanisme",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : mécanisme cité.",
            "B": "Exact : mécanisme cité.",
            "C": "Exact : inhibe la sécrétion de K+.",
            "D": "Faux : l'insuline fait entrer le K+ dans la cellule.",
            "E": "Faux : non présenté comme seule cause dans ce passage.",
        },
        "GTTK bas : déséquilibre Na+/Cl− au TCC → moins de sécrétion de K+.",
        "IV Exploration — GTTK inadapté",
    )

    add(
        "Étiologies GTTK inadapté",
        "Parmi ces causes d'hyperkaliémie par GTTK inadapté, lesquelles sont citées au cours ?",
        {
            "A": "Insuffisance surrénalienne aiguë ou chronique",
            "B": "Maladie/addiction à l'aldostérone induite par les médicaments",
            "C": "Pseudo-hypoaldostéronisme type 1",
            "D": "Hyperplasie congénitale des surrénales",
            "E": "IRC sévère avec DFG < 30 ml/min/1,72 m²",
        },
        ["A", "B", "C", "D", "E"],
        {
            "A": "Exact : cité.",
            "B": "Exact : cité.",
            "C": "Exact : cité.",
            "D": "Exact : cité.",
            "E": "Exact : cité avec seuil de DFG.",
        },
        "GTTK inadapté : hypoaldostéronisme, pseudohypoaldostéronisme, IRC sévère…",
        "VI Étiologies — GTTK inadapté",
    )

    add(
        "Transfert cellulaire",
        "Quelles causes d'hyperkaliémie par transfert cellulaire sont citées ?",
        {
            "A": "Acidoses minérales aiguës",
            "B": "Diabète déséquilibré",
            "C": "Destruction cellulaire (rhabdomyolyse, hémolyse, lyse tumorale…)",
            "D": "Digitaliques, bêtabloquants, succinylcholine",
            "E": "Paralysie périodique familiale de Gamstorp",
        },
        ["A", "B", "C", "D", "E"],
        {k: "Exact : cité dans le cours." for k in "ABCDE"},
        "Transfert cellulaire : acidose, DKA, lyse, digitaliques/BB, Gamstorp.",
        "VI Étiologies — transfert cellulaire",
    )

    add(
        "Syndromes hypoaldostérone",
        "Concernant l'hyperkaliémie, quelle association est citée au cours ?",
        {
            "A": "Syndrome hypo-rénine hypo-aldostérone",
            "B": "Pseudo-hypoaldostéronisme type 2 (syndrome de Gordon)",
            "C": "Syndrome néphrotique avec perte massive de K+",
            "D": "Hyperaldostéronisme primaire avec hypokaliémie",
            "E": "SIADH avec hyponatrémie",
        },
        ["A", "B"],
        {
            "A": "Exact : cité.",
            "B": "Exact : Gordon type 2 cité.",
            "C": "Faux : pas dans cette liste d'hyperkaliémie.",
            "D": "Faux : contexte d'hypokaliémie.",
            "E": "Faux : autre trouble, pas cité ici.",
        },
        "Gordon et hypo-rénine hypo-aldostérone : hyperkaliémie.",
        "VI Étiologies",
    )

    add(
        "Médicaments hyperkaliémiants",
        "Quels médicaments ou traitements sont cités comme favorisant l'hyperkaliémie ?",
        {
            "A": "IEC et ARAII",
            "B": "Diurétiques épargneurs de potassium (spironolactone…)",
            "C": "Héparine non fractionnée",
            "D": "Bêtabloquants",
            "E": "Furosémide seul comme cause principale dans ce passage",
        },
        ["A", "B", "C", "D"],
        {
            "A": "Exact : cité.",
            "B": "Exact : cité.",
            "C": "Exact : cité.",
            "D": "Exact : cité.",
            "E": "Faux : non cité comme cause dans cette énumération.",
        },
        "IEC, ARAII, épargneurs K+, héparine, bêtabloquants.",
        "VI Étiologies — médicaments",
    )

    add(
        "Clinique cardiaque",
        "Sur le plan cardiaque, le cours associe l'hyperkaliémie à :",
        {
            "A": "Des troubles du rythme pouvant aller jusqu'à l'arrêt cardiaque",
            "B": "Une urgence diagnostique et thérapeutique",
            "C": "Des modifications ECG progressives (onde T, QRS, onde P…)",
            "D": "Une bradycardie sinusale bénigne sans risque",
            "E": "L'absence de signes ECG jusqu'à 7 mmol/l systématiquement",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : pronostic grave, troubles du rythme.",
            "B": "Exact : urgence citée.",
            "C": "Exact : modifications ECG citées.",
            "D": "Faux : minimiser le risque est incorrect.",
            "E": "Faux : le cours lie ECG et gravité.",
        },
        "Hyperkaliémie = urgence ; ECG et troubles du rythme.",
        "V Clinique — cardiaque",
    )

    add(
        "Clinique neuromusculaire",
        "Quelles manifestations neuromusculaires sont citées ?",
        {
            "A": "Paresthésies des extrémités et péri-buccales",
            "B": "Hypotonie musculaire et faiblesse",
            "C": "Paralysie flasque symétrique",
            "D": "Crampes isolées comme seul signe obligatoire",
            "E": "Tremblements fins type hyperthyroïdie",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : cité.",
            "B": "Exact : cité.",
            "C": "Exact : cité.",
            "D": "Faux : non présenté comme signe unique obligatoire.",
            "E": "Faux : non cité.",
        },
        "Signes neuro-musculaires : paresthésies, faiblesse, paralysie flasque.",
        "V Clinique — neuromusculaire",
    )

    add(
        "Atteinte rénale",
        "L'hyperkaliémie peut entraîner selon le cours :",
        {
            "A": "Une acidose métabolique par dépression de l'ammoniogenèse",
            "B": "Une ammoniurie diminuée dans certains contextes",
            "C": "Une polyurie osmotique isolée",
            "D": "Une alcalose respiratoire compensatrice systématique",
            "E": "Une hypocalciurie par hyperparathyroïdie",
        },
        ["A", "B"],
        {
            "A": "Exact : atteinte rénale citée.",
            "B": "Exact : lien avec hypoaldostéronisme / uropathie obstructive cité.",
            "C": "Faux : non cité ici.",
            "D": "Faux : non cité ainsi.",
            "E": "Faux : hors contenu de ce passage.",
        },
        "Atteinte rénale : acidose métabolique, ammoniogenèse.",
        "V Clinique — rénale",
    )

    add(
        "Bilan diagnostique",
        "Le bilan diagnostique de l'hyperkaliémie cité comprend en 1ère intention :",
        {
            "A": "Ionogramme sanguin avec réserve alcaline, urée, glycémie",
            "B": "Ionogramme urinaire, urée, diurèse des 24 h",
            "C": "GDS, Mg²+, rénine, aldostérone en 2ème intention",
            "D": "Test à la 9α-fluorocortisone et test au furosémide cités en 2ème intention",
            "E": "Biopsie rénale systématique en urgence",
        },
        ["A", "B", "C", "D"],
        {
            "A": "Exact : 1ère intention.",
            "B": "Exact : 1ère intention.",
            "C": "Exact : 2ème intention.",
            "D": "Exact : 2ème intention.",
            "E": "Faux : non cité.",
        },
        "1ère intention : sang + urines ; 2ème : rénine, aldostérone, tests.",
        "VII Démarches diagnostiques",
    )

    add(
        "Traitement — principes",
        "Concernant le traitement de l'hyperkaliémie, le cours vise à :",
        {
            "A": "Corriger l'hyperkaliémie dans les meilleurs délais",
            "B": "Protéger le myocarde (calcium IV si indication)",
            "C": "Transférer le K+ vers l'intracellulaire (insuline-glucose, bêta-2…)",
            "D": "Éliminer le K+ (diurétiques, résines, dialyse selon contexte)",
            "E": "Administrer du KCl IV systématiquement",
        },
        ["A", "B", "C", "D"],
        {
            "A": "Exact : but cité.",
            "B": "Exact : cardioprotection citée.",
            "C": "Exact : transfert cellulaire cité.",
            "D": "Exact : élimination du K+ citée.",
            "E": "Faux : contre-productif.",
        },
        "Buts : corriger vite, protéger le cœur, transférer K+, éliminer K+.",
        "VIII Traitement",
    )

    add(
        "Traitement — précisions",
        "Quelles mesures thérapeutiques sont mentionnées dans le cours ?",
        {
            "A": "Régime pauvre en potassium",
            "B": "Arrêt des médicaments hyperkaliémiants (IEC, ARAII, épargneurs K+…)",
            "C": "Perfusion glucose-insuline",
            "D": "Bicarbonate de sodium (avec contre-indications citées : OAP, oligurie…)",
            "E": "Salbutamol en nébulisation",
        },
        ["A", "B", "C", "D", "E"],
        {k: "Exact : cité dans le cours." for k in "ABCDE"},
        "Traitement : régime, arrêt médicaments, insuline-glucose, bicarbonate, salbutamol.",
        "VIII Traitement — moyens",
    )

    add(
        "Dialyse",
        "Concernant la dialyse dans l'hyperkaliémie, le cours indique :",
        {
            "A": "L'hémodialyse corrige rapidement l'hyperkaliémie",
            "B": "Elle peut corriger une acidose métabolique associée",
            "C": "La dialyse péritonéale est toujours plus rapide que l'hémodialyse",
            "D": "Elle est inutile en urgence",
            "E": "Elle remplace toujours le calcium IV",
        },
        ["A", "B"],
        {
            "A": "Exact : hémodialyse efficace rapidement.",
            "B": "Exact : cité.",
            "C": "Faux : DP moins efficace pour correction rapide selon le cours.",
            "D": "Faux : indiquée dans certains cas.",
            "E": "Faux : calcium et dialyse ont des rôles différents.",
        },
        "HD rapide pour K+ et acidose ; DP moins rapide.",
        "VIII Traitement — dialyse",
    )

    add(
        "Intérêt de la question",
        "Pourquoi l'hyperkaliémie est-elle importante selon le cours ?",
        {
            "A": "Trouble hydro-électrolytique fréquent (IRC, hémodialyse)",
            "B": "Urgence diagnostique et thérapeutique (troubles du rythme)",
            "C": "Pronostic potentiellement grave",
            "D": "Toujours asymptomatique",
            "E": "Sans lien avec la mortalité cardiaque",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : fréquence IRC/HD.",
            "B": "Exact : urgence rythmique.",
            "C": "Exact : gravité.",
            "D": "Faux : signes cliniques possibles.",
            "E": "Faux : contraire au cours.",
        },
        "Fréquent, urgent (rythme), grave.",
        "II Intérêt de la question",
    )

    return out


def hypokaliemie() -> list[dict]:
    t = "Hypokaliémie"
    s = f"{t} —"
    out = []

    def add(notion, question, opts, correct, expl, kp, sec):
        out.append(
            _q(t, f"HYPOK-{len(out)+1:02d}", question, opts, correct, expl, kp, f"{s} {sec}", notion)
        )

    add(
        "Distribution K+",
        "Les données de distribution du K+ rappelées dans le cours d'hypokaliémie incluent :",
        {
            "A": "Environ 90 % du potassium échangeable en 24 h",
            "B": "Environ 2 % du potassium dans le compartiment extracellulaire",
            "C": "Muscle ≈ 78 % du potassium intracellulaire",
            "D": "Kaliémie normale 6–7 mmol/l",
            "E": "100 % du K+ est plasmatique",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : rappel physiologique identique au cours.",
            "B": "Exact : 2 % SEC.",
            "C": "Exact : répartition citée.",
            "D": "Faux : kaliémie 3,5–5 mmol/l.",
            "E": "Faux : majeure partie intracellulaire.",
        },
        "Même rappel : K+ intracellulaire, kaliémie 3,5–5.",
        "III Rappel physiologique",
    )

    add(
        "Transferts K+",
        "Quels facteurs favorisent l'entrée du K+ dans la cellule selon le cours ?",
        {
            "A": "Insuline",
            "B": "Catécholamines",
            "C": "Alcalose",
            "D": "Acidose",
            "E": "Bêtabloquants (effet cité sur transfert)",
        },
        ["A", "B", "C"],
        {
            "A": "Exact.",
            "B": "Exact.",
            "C": "Exact.",
            "D": "Faux : sortie du K+ vers l'extérieur.",
            "E": "Faux : cité plutôt côté hyperkaliémie.",
        },
        "Insuline, catécholamines, alcalose → entrée de K+.",
        "III Rappel physiologique — transferts",
    )

    add(
        "Hyperaldostéronisme primitif",
        "Concernant l'hyperaldostéronisme primitif, le cours cite :",
        {
            "A": "Syndrome de Conn",
            "B": "HTA sensible à la dexaméthasone",
            "C": "Hypokaliémie associée",
            "D": "Hyperkaliémie constante",
            "E": "Absence d'hypertension artérielle",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : Conn cité.",
            "B": "Exact : HTA sensible dexaméthasone citée.",
            "C": "Exact : contexte d'hypokaliémie.",
            "D": "Faux : hyperaldostéronisme → perte de K+.",
            "E": "Faux : HTA associée.",
        },
        "Conn : HTA + hypokaliémie (sensibilité dexaméthasone citée).",
        "VI Étiologies — hyperaldostéronisme",
    )

    add(
        "Cortisol / Cushing",
        "Quelles entités liées au cortisol sont citées ?",
        {
            "A": "Déficit en 11β-hydroxystéroïde déshydrogénase",
            "B": "Syndrome d'excès apparent en minéralocorticoïdes",
            "C": "Acide glycyrrhizique (réglisse) — déficit acquis",
            "D": "Syndrome de Cushing ou traitement par corticoïdes",
            "E": "Acétate de fludrocortisone",
        },
        ["A", "B", "C", "D", "E"],
        {k: "Exact : cité dans le cours." for k in "ABCDE"},
        "11β-HSD, réglisse, Cushing/corticoïdes, fludrocortisone.",
        "VI Étiologies — cortisol",
    )

    add(
        "DOC",
        "Concernant la désoxycorticostérone (DOC), le cours mentionne :",
        {
            "A": "Tumeur sécrétant de la DOC",
            "B": "Blocage de la 11β-hydroxylase",
            "C": "Blocage de la 17α-hydroxylase",
            "D": "Hypokaliémie possible dans ce contexte",
            "E": "Hyperkaliémie obligatoire",
        },
        ["A", "B", "C", "D"],
        {
            "A": "Exact.",
            "B": "Exact.",
            "C": "Exact.",
            "D": "Exact : activité minéralocorticoïde.",
            "E": "Faux : effet minéralocorticoïde → perte de K+.",
        },
        "Tumeur à DOC, déficits enzymatiques 11β/17α.",
        "VI Étiologies — DOC",
    )

    add(
        "Bartter et Gitelman",
        "À propos des tubulopathies, le cours indique :",
        {
            "A": "Syndrome de Bartter : type « furosémide-like »",
            "B": "Syndrome de Gitelman : type « thiazidique-like »",
            "C": "Déficit en magnésium peut être associé (Gitelman)",
            "D": "Bartter se traite uniquement par supplémentation en KCl sans autre mesure",
            "E": "Gitelman donne toujours une hyperkaliémie",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : Bartter furosémide-like.",
            "B": "Exact : Gitelman thiazidique-like.",
            "C": "Exact : magnésium cité.",
            "D": "Faux : simplification non citée.",
            "E": "Faux : hypokaliémie.",
        },
        "Bartter = furosémide-like ; Gitelman = thiazidique-like.",
        "VI Étiologies — tubulopathies",
    )

    add(
        "Acidose métabolique",
        "Une situation citée pouvant s'accompagner d'hypokaliémie est :",
        {
            "A": "Situation clinique avec bicarbonaturie",
            "B": "Acidose métabolique chronique avec augmentation des pertes digestives",
            "C": "Alcalose métabolique isolée sans autre mécanisme",
            "D": "Hyperaldostéronisme avec rétention de K+",
            "E": "IRC terminale sans diurétiques",
        },
        ["A", "B"],
        {
            "A": "Exact : bicarbonaturie citée.",
            "B": "Exact : acidose métabolique chronique citée.",
            "C": "Faux : alcalose favorise entrée de K+.",
            "D": "Faux : aldostérone augmente pertes de K+.",
            "E": "Faux : non cité ainsi.",
        },
        "Bicarbonaturie et acidose métabolique chronique : pertes de K+.",
        "VI Étiologies — digestif / acidose",
    )

    add(
        "Amphotéricine B",
        "Concernant l'amphotéricine B, le cours précise :",
        {
            "A": "90 % situé en intracellulaire (rappel de distribution)",
            "B": "Peut entraîner des pertes urinaires de K+",
            "C": "Traitement par amphotéricine B cité comme cause d'hypokaliémie",
            "D": "Protège toujours contre l'hypokaliémie",
            "E": "N'affecte pas le tubule",
        },
        ["B", "C"],
        {
            "A": "Faux : chiffre de distribution générale, pas spécifique amphotéricine.",
            "B": "Exact : pertes urinaires.",
            "C": "Exact : cité.",
            "D": "Faux.",
            "E": "Faux : toxicité tubulaire citée.",
        },
        "Amphotéricine B → hypokaliémie (pertes urinaires).",
        "VI Étiologies — médicaments",
    )

    add(
        "Clinique",
        "Les manifestations cliniques de l'hypokaliémie citées incluent :",
        {
            "A": "Faiblesse musculaire",
            "B": "Troubles du rythme cardiaque",
            "C": "Constipation / troubles digestifs possibles",
            "D": "Hyperréflexie ostéotendineuse",
            "E": "Polyurie osmotique obligatoire",
        },
        ["A", "B", "C"],
        {
            "A": "Exact : faiblesse musculaire.",
            "B": "Exact : troubles du rythme.",
            "C": "Exact : sphère digestive citée.",
            "D": "Faux : plutôt hyporéflexie.",
            "E": "Faux : non cité comme obligatoire.",
        },
        "Faiblesse, arythmies, troubles digestifs.",
        "V Clinique",
    )

    add(
        "ECG",
        "Sur l'ECG, l'hypokaliémie peut se manifester par :",
        {
            "A": "Onde T plate ou effondrée",
            "B": "Onde U",
            "C": "Allongement du QT",
            "D": "Onde T en pic hyperacut",
            "E": "Élargissement du QRS typique de l'hyperkaliémie sévère",
        },
        ["A", "B"],
        {
            "A": "Exact : onde T citée.",
            "B": "Exact : onde U citée.",
            "C": "Faux : plutôt allongement QT/U selon contexte — pas l'élément principal cité ici.",
            "D": "Faux : signe d'hyperkaliémie.",
            "E": "Faux : hyperkaliémie.",
        },
        "ECG : onde T plate, onde U.",
        "V Clinique — ECG",
    )

    add(
        "Bilan",
        "Le bilan d'une hypokaliémie doit rechercher selon le cours :",
        {
            "A": "La cause (pertes digestives, urinaires, médicaments…)",
            "B": "Une alcalose métabolique ou respiratoire associée",
            "C": "Une hypertension (contexte hyperaldostéronisme)",
            "D": "Une hyperkaliémie associée systématique",
            "E": "Un déficit en magnésium éventuel",
        },
        ["A", "B", "C", "E"],
        {
            "A": "Exact : démarche étiologique.",
            "B": "Exact : alcalose et pertes de K+ liées.",
            "C": "Exact : Conn / minéralocorticoïdes.",
            "D": "Faux : hypokaliémie.",
            "E": "Exact : magnésium cité (Gitelman).",
        },
        "Chercher cause, alcalose, HTA, magnésium.",
        "VII Démarches diagnostiques",
    )

    add(
        "Traitement — principes",
        "Le traitement de l'hypokaliémie selon le cours comprend :",
        {
            "A": "Corriger la cause",
            "B": "Supplémentation en potassium (voie orale ou IV selon gravité)",
            "C": "Corriger le magnésium si déficit",
            "D": "Administrer des épargneurs de potassium en cas de surdosage",
            "E": "Arrêter les diurétiques hypokaliémiants si possible",
        },
        ["A", "B", "C", "E"],
        {
            "A": "Exact.",
            "B": "Exact.",
            "C": "Exact : magnésium.",
            "D": "Faux : aggravation.",
            "E": "Exact : diurétiques cités parmi les causes.",
        },
        "Traiter la cause + K+ ± Mg²+.",
        "VIII Traitement",
    )

    add(
        "Urgence",
        "Une hypokaliémie sévère est dangereuse car :",
        {
            "A": "Risque d'arythmie cardiaque",
            "B": "Risque de paralysie musculaire",
            "C": "Toujours bénigne sans traitement",
            "D": "Sans retentissement neuromusculaire possible",
            "E": "Ne nécessite jamais de supplémentation IV",
        },
        ["A", "B"],
        {
            "A": "Exact : troubles du rythme.",
            "B": "Exact : faiblesse/paralysie.",
            "C": "Faux.",
            "D": "Faux.",
            "E": "Faux : formes sévères peuvent nécessiter IV.",
        },
        "Gravité : rythme et muscle.",
        "V Clinique — gravité",
    )

    return out


def hypercalcemie() -> list[dict]:
    t = "Hypercalcémie"
    s = f"{t} —"
    drugs = [
        ("Lithium", "Le lithium est cité parmi les causes d'hypercalcémie."),
        ("Apport excessif de calcium per os", "Un apport excessif de calcium per os est cité."),
        ("Vitamine A à forte dose", "La vitamine A à forte dose est citée."),
        ("Diurétique thiazidique", "Les diurétiques thiazidiques sont cités."),
        ("Amiloride", "L'amiloride est cité."),
        ("Tamoxifène (anti-estrogène)", "Le tamoxifène est cité."),
        ("Intoxication aluminique", "L'intoxication aluminique est citée."),
    ]
    out = []
    pool = [d[1] for d in drugs]
    for i, (label, truth) in enumerate(drugs, 1):
        falses = [p for p in pool if p != truth][:4]
        while len(falses) < 4:
            falses.append("Cette cause n'est pas listée dans le cours pour l'hypercalcémie.")
        opts = {"A": truth, "B": falses[0], "C": falses[1], "D": falses[2], "E": falses[3]}
        out.append(
            _q(
                t,
                f"HCa-{i:02d}",
                f"Concernant l'hypercalcémie, quelle cause médicamenteuse ou toxique est citée au cours ?",
                opts,
                ["A"],
                {
                    "A": f"Exact : {truth}",
                    "B": "Faux : autre item de la liste ou non cité.",
                    "C": "Faux : autre item de la liste ou non cité.",
                    "D": "Faux : autre item de la liste ou non cité.",
                    "E": "Faux : autre item de la liste ou non cité.",
                },
                truth,
                f"{s} VI Étiologie — médicaments/toxiques",
                label,
            )
        )
    return out


def all_curated() -> list[dict]:
    return hyperkaliemie() + hypokaliemie() + hypercalcemie()


CURATED_BY_TOPIC = {
    "Hyperkaliémie": hyperkaliemie,
    "Hypokaliémie": hypokaliemie,
    "Hypercalcémie": hypercalcemie,
}
