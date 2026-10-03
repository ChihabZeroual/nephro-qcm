#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la banque QCM néphrologie (hydro-électrolytes / acido-basique)."""

from __future__ import annotations

import json
import random
import re
import unicodedata
from pathlib import Path

SEED = 42
CHAPTER = "Troubles hydro-électrolytiques et équilibre acido-basique"
MIN_PER_COURSE = 110
QUESTIONS_PER_NOTION = 10
LABELS = ("A", "B", "C", "D", "E")

OUTPUT = Path(__file__).resolve().parent.parent / "app" / "data" / "questions.json"

TYPE_CYCLE = (
    "knowledge",
    "knowledge",
    "comprehension",
    "clinical",
    "trap",
    "discrimination",
    "inverse",
    "knowledge",
    "comprehension",
    "clinical",
)

STEM_KNOWLEDGE = (
    "Concernant {label}, quelle proposition est exacte ?",
    "À propos de {label}, quelle affirmation est correcte ?",
    "{label} : indiquez la réponse juste.",
    "Parmi les items suivants sur {label}, lequel est vrai ?",
)

STEM_MULTI = (
    "Concernant {label}, quelle(s) proposition(s) est/sont exacte(s) ?",
    "À propos de {label}, cochez la (les) réponse(s) correcte(s).",
    "{label} : quelles affirmations sont fondées ?",
)

STEM_INVERSE = (
    "Concernant {label}, toutes les propositions sont exactes SAUF une. Laquelle ?",
    "À propos de {label}, une seule proposition est fausse. Laquelle ?",
)

STEM_TRAP = (
    "Concernant {label}, attention aux pièges : quelle proposition est exacte ?",
    "{label} (piège classique) : quelle réponse est correcte ?",
)

STEM_DISCRIM = (
    "Concernant {label}, quelle proposition est la plus discriminante au plan diagnostique ?",
    "{label} : quelle affirmation permet le mieux d'orienter la prise en charge ?",
)

STEM_CLINICAL = (
    "{vignette}\n\nQuelle proposition est la plus appropriée concernant {label} ?",
    "{vignette}\n\nQuelle conduite à tenir / quel mécanisme est le plus probable ({label}) ?",
)


def course_slug(topic: str) -> str:
    return topic.replace(" ", "_") if " " in topic else topic


def slug_id(text: str) -> str:
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:48] or "item"


def explain_option(text: str, is_correct: bool, key_point: str) -> str:
    if is_correct:
        return f"Exact : {text} — Point clé : {key_point}"
    return f"Inexact : « {text} » ne correspond pas aux données physiologiques/cliniques attendues ici. {key_point}"


FALLBACK_FALSES = (
    "Cette proposition est physiologiquement inexacte dans ce contexte clinique.",
    "Ce mécanisme est en contradiction avec les données néphrologiques usuelles.",
    "Cette réponse confond deux entités qu'il faut distinguer à l'examen.",
    "Affirmation erronée fréquemment retenue mais non validée par les recommandations.",
    "Cette option décrit une exception rare qui n'est pas la règle ici.",
    "Proposition inadaptée au mécanisme principal évoqué dans ce cours.",
)


def pick_options(
    rng: random.Random,
    truths: list[str],
    falses: list[str],
    n_correct: int,
) -> tuple[dict[str, str], list[str]]:
    n_correct = max(1, min(n_correct, 4, len(truths)))
    pool_f = [f for f in falses if f not in truths]
    need_wrong = 5 - n_correct
    while len(pool_f) < need_wrong:
        pool_f.append(rng.choice(FALLBACK_FALSES) + f" [{len(pool_f)}]")
    correct = rng.sample(truths, min(n_correct, len(truths)))
    wrong = rng.sample(pool_f, need_wrong)
    combined = correct + wrong
    rng.shuffle(combined)
    opts = {LABELS[i]: combined[i] for i in range(5)}
    correct_labels = [k for k, v in opts.items() if v in correct]
    return opts, correct_labels


def build_question(
    qid: str,
    topic: str,
    slug: str,
    notion_meta: dict,
    qtype: str,
    stem: str,
    options: dict[str, str],
    correct: list[str],
    difficulty: int,
) -> dict:
    kp = notion_meta["keyPoint"]
    expl = {k: explain_option(options[k], k in correct, kp) for k in LABELS}
    return {
        "id": qid,
        "chapter": CHAPTER,
        "topic": topic,
        "courseSlug": slug,
        "type": qtype,
        "question": stem,
        "options": options,
        "correctAnswers": sorted(correct),
        "explanation": expl,
        "keyPoint": kp,
        "difficulty": difficulty,
        "tags": notion_meta["tags"],
        "notion": notion_meta["notion"],
        "variantGroup": notion_meta["variantGroup"],
    }


def questions_for_notion(
    rng: random.Random,
    topic: str,
    slug: str,
    notion: dict,
    seen: set[str],
    id_seq: list[int],
) -> list[dict]:
    out: list[dict] = []
    truths = notion["truths"]
    falses = notion["falses"]
    label = notion["shortLabel"]
    vignette = notion.get("vignette")

    for vi in range(QUESTIONS_PER_NOTION):
        qtype = TYPE_CYCLE[vi % len(TYPE_CYCLE)]
        diff = max(1, min(5, notion["difficulty"] + (vi % 3) - 1))

        if qtype == "knowledge":
            stem = STEM_KNOWLEDGE[vi % len(STEM_KNOWLEDGE)].format(label=label)
            opts, correct = pick_options(rng, truths, falses, 1)
        elif qtype == "comprehension":
            stem = STEM_MULTI[(vi // 2) % len(STEM_MULTI)].format(label=label)
            n_c = 2 if vi % 2 == 0 else 3
            opts, correct = pick_options(rng, truths, falses, n_c)
        elif qtype == "inverse":
            stem = STEM_INVERSE[vi % len(STEM_INVERSE)].format(label=label)
            inv_falses = [f for f in falses if f not in truths] or list(FALLBACK_FALSES)
            false_one = rng.choice(inv_falses)
            n_true = min(4, len(truths))
            true_pick = rng.sample(truths, n_true)
            while len(true_pick) < 4:
                true_pick.append(rng.choice(truths))
            combined = true_pick + [false_one]
            rng.shuffle(combined)
            opts = {LABELS[i]: combined[i] for i in range(5)}
            correct = [k for k, v in opts.items() if v == false_one]
        elif qtype == "trap":
            stem = STEM_TRAP[vi % len(STEM_TRAP)].format(label=label)
            opts, correct = pick_options(rng, truths, falses, 1)
        elif qtype == "discrimination":
            stem = STEM_DISCRIM[vi % len(STEM_DISCRIM)].format(label=label)
            opts, correct = pick_options(rng, truths[: max(3, len(truths))], falses, 1)
        elif qtype == "clinical":
            v = vignette or (
                f"Cas clinique : patient de {40 + vi} ans, hospitalisé pour {topic.lower()} "
                f"avec signes d'instabilité et bilan biologique perturbé."
            )
            stem = STEM_CLINICAL[vi % len(STEM_CLINICAL)].format(vignette=v, label=label)
            opts, correct = pick_options(rng, truths, falses, 1)
        else:
            stem = STEM_KNOWLEDGE[0].format(label=label)
            opts, correct = pick_options(rng, truths, falses, 1)

        sig = stem + "\n" + "\n".join(sorted(opts.values()))
        attempt = 0
        while stem in seen or sig in seen:
            attempt += 1
            stem = (
                f"{stem} — variante {notion['variantGroup']}-{vi + 1}-{attempt}"
            )
            sig = stem + "\n" + "\n".join(sorted(opts.values()))
            if attempt > 12:
                break
        if stem in seen or sig in seen:
            continue
        seen.add(stem)
        seen.add(sig)

        id_seq[0] += 1
        qid = f"{slug}-{id_seq[0]:05d}"
        out.append(
            build_question(qid, topic, slug, notion, qtype, stem, opts, correct, diff)
        )
    return out


def generate_course(
    rng: random.Random,
    topic: str,
    notions: list[dict],
    seen: set[str],
    id_seq: list[int],
) -> list[dict]:
    slug = course_slug(topic)
    qs: list[dict] = []
    for notion in notions:
        qs.extend(questions_for_notion(rng, topic, slug, notion, seen, id_seq))
    while len(qs) < MIN_PER_COURSE:
        for notion in notions:
            extra = notion.copy()
            extra["shortLabel"] = extra["shortLabel"] + f" — complément {len(qs)}"
            batch = questions_for_notion(rng, topic, slug, extra, seen, id_seq)
            qs.extend(batch)
            if len(qs) >= MIN_PER_COURSE:
                break
    return qs


# --- Données embarquées par cours (notions + vérités / distracteurs) ---

def _n(
    variant_group: str,
    notion: str,
    short_label: str,
    key_point: str,
    tags: list[str],
    difficulty: int,
    truths: list[str],
    falses: list[str],
    vignette: str | None = None,
) -> dict:
    return {
        "variantGroup": variant_group,
        "notion": notion,
        "shortLabel": short_label,
        "keyPoint": key_point,
        "tags": tags,
        "difficulty": difficulty,
        "truths": truths,
        "falses": falses,
        "vignette": vignette,
    }


def _parse_course_block(topic: str, block: str) -> list[dict]:
    notions: list[dict] = []
    for section in block.strip().split("\n\n"):
        if not section.strip():
            continue
        lines = [ln.strip() for ln in section.strip().splitlines() if ln.strip()]
        meta = lines[0].split("|")
        if len(meta) < 6:
            raise ValueError(f"Métadonnées invalides pour {topic}: {lines[0]}")
        vg, notion, short, kp, diff_s, tag_s = meta[:6]
        vignette = None
        truths: list[str] = []
        falses: list[str] = []
        for ln in lines[1:]:
            if ln.startswith("V|"):
                vignette = ln[2:].strip()
            elif ln.startswith("+"):
                truths.append(ln[1:].strip())
            elif ln.startswith("-"):
                falses.append(ln[1:].strip())
        notions.append(
            _n(
                vg,
                notion,
                short,
                kp,
                [t.strip() for t in tag_s.split(",") if t.strip()],
                int(diff_s),
                truths,
                falses,
                vignette,
            )
        )
    return notions


def _all_course_blocks() -> dict[str, str]:
    return {
        "Acidose métabolique": ACIDOSE_BLOCK,
        "Alcalose métabolique": ALCALOSE_BLOCK,
        "Hypercalcémie": HYPERCALCEMIE_BLOCK,
        "Hyperkaliémie": HYPERKALIEMIE_BLOCK,
        "Hypernatrémie": HYPERNATREMIE_BLOCK,
        "Hyperphosphatémie": HYPERPHOSPHATEMIE_BLOCK,
        "Hypocalcémie": HYPOCALCEMIE_BLOCK,
        "Hypokaliémie": HYPOKALIEMIE_BLOCK,
        "Hyponatrémie": HYPNATREMIE_BLOCK,
        "Hypophosphatémie": HYPOPHOSPHATEMIE_BLOCK,
    }


# ---------------------------------------------------------------------------
# Banques par cours (format section : meta puis + vérité / - erreur, V|vignette)
# ---------------------------------------------------------------------------

ACIDOSE_BLOCK = r"""
am-def|Définition de l'acidose métabolique|définition de l'acidose métabolique|Acidose métabolique : baisse du bicarbonate avec acidémie (pH bas).|1|acidose,définition
+ L'acidose métabolique associe une baisse du HCO3- et une acidémie (pH < 7,38).
+ La compensation respiratoire attendue est une hyperventilation avec baisse de la PaCO2.
+ Une acidémie peut exister sans acidose métabolique (acidose respiratoire aiguë).
+ Le diagnostic repose sur le pH, PaCO2 et bicarbonates sur gaz du sang artériel.
- L'acidose métabolique se définit par une élévation isolée de la PaCO2.
- Le pH est toujours normal dans l'acidose métabolique pure.
- La compensation ventilatoire provoque une élévation chronique de la PaCO2.
- Le bicarbonate augmente typiquement dans l'acidose métabolique.

am-gap|Trou anionique en acidose|trou anionique plasmatique|TA = Na+ - (Cl- + HCO3-) ; un TA élevé oriente vers acidoses à anions non mesurés.|2|acidose,gap
+ Le trou anionique (TA) classique = Na+ - (Cl- + HCO3-).
+ Un TA élevé suggère des anions acides non mesurés (lactate, cétones, toxiques).
+ Le TA peut être artificiellement bas en hypoalbuminémie (corriger selon albumine).
+ Un TA normal n'élimine pas une acidose métabolique (formes hyperchlorémiques).
- Le TA se calcule en ajoutant le potassium au chlore et au bicarbonate au numérateur.
- Un TA élevé exclut l'acidose diabétique.
- L'albumine n'influence pas le trou anionique.
- Le TA est toujours > 20 mmol/L dans l'acidose métabolique.

am-gap-high|Acidoses à TA élevé|acidoses à trou anionique élevé|Causes : cétoacidose, lactate, intoxications, insuffisance rénale, Rhabdomyolyse.|2|acidose,gap,cétoacidose
+ La cétoacidose diabétique et alcoolique sont des causes majeures de TA élevé.
+ L'acidose lactique survient en choc, sepsis, metformine, ischémie tissulaire.
+ Méthanol et éthylène glycol élèvent le TA (oxalate, formate, glycolate).
+ L'insuffisance rénale avancée peut majorer le TA (sulfates, phosphates, urate).
- La diarrhée chronique est la cause typique d'acidose à TA élevé.
+ L'acidurie paradoxale peut accompagner certaines acidoses sévères.
- Les RTA proximales donnent classiquement un TA élevé marqué.
- L'intoxication à l'aspirine se manifeste uniquement par une alcalose.

am-gap-norm|Acidoses hyperchlorémiques|acidoses à trou anionique normal|Diarrhée, pertes digestives de HCO3-, RTA, acidose urétéro-sigmoïdienne.|3|acidose,RTA,hyperchlorémique
+ Les pertes de bicarbonate digestif (diarrhée, fistules) donnent une acidose hyperchlorémique.
+ Les tubulopathies (RTA type 1, 2, 4) entraînent souvent un TA normal avec hyperchlorémie.
+ L'acidose après résolution de cétoacidose peut être hyperchlorémique (perte de cétons).
+ L'urétéro-sigmoïdostomie peut provoquer une acidose hyperchlorémique par réabsorption de Cl-.
- Toutes les acidoses métaboliques ont un TA supérieur à 16 mmol/L.
- La RTA distale (type 1) est définie par une alcalose métabolique.
- La diarrhée provoque typiquement un TA très élevé.
- L'administration de chlorure de sodium corrige l'acidose par pertes digestives.

am-rta|Acidoses tubulaires rénales|RTA et acidose métabolique|RTA1 : défaut d'acidification distale ; RTA2 : défaut de réabsorption proximale ; RTA4 : hypoaldostéronisme.|3|acidose,RTA,néphro
+ La RTA type 1 (distale) associe acidose, urine inappropriément alcaline, risque de lithiases.
+ La RTA type 2 (proximale) peut s'accompagner de pertes de bicarbonate et hypokaliémie.
+ La RTA type 4 est liée à un déficit en aldostérone ou résistance (souvent hyperK+).
+ Les causes médicamenteuses incluent amphotéricine B, inhibiteurs de l'anhydrase carbonique.
- La RTA type 1 se caractérise par une urine systématiquement acide en acidose.
- La RTA type 4 est typiquement associée à une hypokaliémie sévère.
- L'amphotéricine B provoque une alcalose métabolique par excès de bicarbonate.
- Les patients RTA n'ont jamais de troubles du calcium.

am-comp|Compensation respiratoire|compensation ventilatoire de l'acidose|Réponse hyperventilatoire ; relation de Winter pour acidoses métaboliques.|2|acidose,Winter,compensation
+ La compensation attendue diminue la PaCO2 d'environ 1,2 mmHg par mmol/L de baisse du HCO3-.
+ La formule de Winter : PaCO2 attendue ≈ (1,5 × HCO3-) + 8 (±2).
+ Une PaCO2 supérieure à l'attendu évoque une acidose respiratoire associée.
+ Une PaCO2 inférieure à l'attendu évoque une alcalose respiratoire associée.
- La compensation ventilatoire augmente la PaCO2 dans l'acidose métabolique.
- Winter s'applique aux alcaloses métaboliques.
- La compensation est complète en quelques minutes.
- Le patient acidosé retient volontairement le CO2 pour corriger le pH.

am-delta|Delta gap et delta ratio|rapport delta/delta|Évalue un trouble acido-basique mixte en acidose à TA élevé.|4|acidose,delta,mixte
+ Delta gap = TA mesuré - TA normal (souvent 12).
+ Delta ratio = delta gap / (24 - HCO3-) ; >2 suggère alcalose métabolique associée.
+ Delta ratio < 1 suggère une acidose hyperchlorémique associée.
+ Utile en cétoacidose traitée ou sepsis avec troubles mixtes.
- Le delta ratio ne s'utilise jamais en pratique clinique.
- Un delta ratio normal exclut tout trouble mixte.
- Le delta gap remplace le trou anionique initial.
- Delta ratio > 2 signifie acidose respiratoire associée.

am-cad|Cétoacidose diabétique|CAD et acidose|Hyperglycémie, cétonémie, TA élevé ; traitement : insuline, fluides, K+.|3|acidose,CAD,urgence
V|Homme de 28 ans, polyurie et vomissements depuis 48 h. pH 7,15, HCO3- 8 mmol/L, glycémie 3,2 g/L, cétonurie +++.
+ La CAD associe hyperglycémie, acidose à TA élevé et cétones (β-hydroxybutyrate).
+ Le traitement initial repose sur les solutés isotoniques puis l'insuline IV après vérification du K+.
+ Le potassium doit être supplémenté si K+ < 3,3 mmol/L avant insuline.
+ Le bicarbonate IV est réservé aux formes très sévères (pH < 6,9) ou instabilité hémodynamique.
- L'insuline est toujours la première ligne avant toute expansion volémique.
- La glycémie normale exclut une CAD.
- Les cétones disparaissent avant la correction de l'hyperglycémie dans tous les cas.
- Le seul traitement de la CAD est le bicarbonate massif.

am-lact|Acidose lactique|acidose lactique|Type A (hypoxie) vs B (métabolique) ; metformine, biguanides, sepsis.|3|acidose,lactate,sepsis
+ L'acidose lactique type A survient en hypoperfusion, anémie sévère, intoxication CO.
+ L'acidose lactique type B inclut metformine, linezolide, déficits enzymatiques, lymphomes.
+ Le lactate > 4 mmol/L en contexte de sepsis est un critère de gravité.
+ Traiter la cause (réanimation, arrêt toxique) prime sur le bicarbonate.
- Le lactate est toujours normal en choc septique.
- La metformine ne provoque jamais d'acidose lactique.
- Le bicarbonate est systématique dès que lactate > 2 mmol/L.
- L'acidose lactique se traduit par un TA normal.

am-tox|Intoxications à TA élevé|intoxications acides| Méthanol, éthylène glycol, aspirine (phases mixtes).|4|acidose,toxique,urgence
+ Le méthanol produit formiate et peut entraîner une acidose sévère avec atteinte visuelle.
+ L'éthylène glycol donne acide oxalique et insuffisance rénale aiguë.
+ Le fomepizole ou l'éthanol bloquent l'alcool déshydrogénase en intoxication aux glycols/méthanol.
+ L'hémodialyse est indiquée en intoxication sévère avec acidose refractaire.
- L'aspirine provoque uniquement une acidose métabolique sans phase respiratoire.
- Le méthanol abaisse le trou anionique.
- L'éthylène glycol n'affecte pas les reins.
- Le traitement des glycolés repose uniquement sur le bicarbonate oral.

am-tx|Traitement de l'acidose métabolique|prise en charge de l'acidose|Corriger la cause ; bicarbonate sélectif ; précautions K+ et volume.|3|acidose,traitement,bicarbonate
+ La priorité est de traiter la cause (perfusion, insuline, dialyse, antidote).
+ Le bicarbonate IV est discuté si pH très bas ou conséquences cardiaques majeures.
+ Une correction trop rapide peut induire une hypokaliémie et une alcalose de rebond.
+ En IRC terminale, la dialyse corrige l'acidose urémique.
- Le bicarbonate est indiqué dans toute acidose avec pH < 7,35 sans exception.
- Corriger rapidement le pH à 7,45 est recommandé en CAD.
- L'acidose chronique légère de l'IRC doit toujours être corrigée par bicarbonate IV en bolus.
- Les solutés glucosés hypertoniques sont le traitement de première intention.

am-ur|Acidose urémique|acidose de l'insuffisance rénale|Accumulation d'acides organiques sulfureux ; indication dialyse.|2|acidose,IRC,dialyse
+ L'insuffisance rénale chronique entraîne une acidose métabolique hyperchlorémique puis à TA élevé.
+ Le déficit en bicarbonate chronique favorise l'ostéodystrophie et la cachexie.
+ Les chélateurs de phosphate et régimes peuvent influencer l'équilibre acido-basique.
+ La dialyse péritonéale ou hémodialyse corrige l'acidose résistante.
- L'acidose urémique disparaît spontanément sans épuration.
- Le TA est toujours normal en IRC terminale.
- Le bicarbonate oral est contre-indiqué en IRC.
- L'acidose urémique est une acidose respiratoire.

am-min|Acidose minérale|inhibiteurs de l'anhydrase carbonique|Acetazolamide, topiramate : pertes urinaires de HCO3-.|2|acidose,médicament,AC
+ Les inhibiteurs de l'anhydrase carbonique provoquent une acidose métabolique hyperchlorémique.
+ L'acetazolamide est utilisé en glaucome et maladie du montagne mais peut acidifier.
+ Le topiramate peut entraîner acidose et lithiases urinaires.
+ La correction repose sur l'arrêt du médicament si possible et mesures symptomatiques.
- L'acetazolamide provoque une alcalose métabolique chronique.
- Les inhibiteurs AC augmentent la réabsorption tubulaire de bicarbonate.
- L'acidose sous topiramate est toujours à TA élevé majeur.
- Ces médicaments n'ont aucun effet sur le pH urinaire.
"""

ALCALOSE_BLOCK = r"""
al-def|Définition alcalose métabolique|définition de l'alcalose métabolique|Alcalose métabolique : élévation du HCO3- avec alcalémie.|1|alcalose,définition
+ L'alcalose métabolique associe HCO3- élevé et pH > 7,42 (alcalémie).
+ Une alcalémie peut exister sans alcalose métabolique (hyperventilation aiguë).
+ La compensation respiratoire est une hypoventilation avec hausse de PaCO2.
+ Le diagnostic repose sur gaz du sang et ionogramme.
- L'alcalose métabolique se définit par une baisse du bicarbonate.
- La PaCO2 diminue en compensation de l'alcalose métabolique.
- Le pH est toujours normal dans l'alcalose métabolique.
- L'alcalémie chronique est sans conséquence clinique.

al-cl|Chlorurie et classification|chlorurie dans l'alcalose|Chlorurie urinaire aide à distinguer pertes vs rétention (volume).|2|alcalose,Cl,classification
+ Une chlorurie urinaire basse (< 20 mmol/L) suggère une alcalose chloro-sensible (pertes GI, diurétiques anciens).
+ Une chlorurie élevée avec HTA évoque hyperaldostéronisme ou sténose réno-vasculaire.
+ La chlorurie aide à guider la supplémentation en NaCl.
+ Les vomissements entraînent pertes de HCl et alcalose avec déplétion volémique.
- La chlorurie urinaire est toujours > 40 mmol/L dans les vomissements.
- Une chlorurie basse indique une surcharge volémique.
- Le chlorure urinaire n'a aucun intérêt en alcalose.
- L'alcalose post-hypercapnie a une chlorurie toujours élevée.

al-vol|Alcalose chloro-sensible|alcalose chloro-sensible|Correction par NaCl ; pertes digestives, diurétiques de l'anse.|2|alcalose,volume,NaCl
+ L'expansion par NaCl corrige l'alcalose chloro-sensible chez le patient hypovolémique.
+ Les pertes gastriques (sonde, vomissements) sont une cause fréquente.
+ Les diurétiques de l'anse et thiazidiques peuvent entretenir l'alcalose.
+ La contraction volémique stimule la réabsorption de HCO3- proximale.
- Le NaCl aggrave l'alcalose chloro-sensible.
- Les diurétiques de l'anse provoquent une acidose métabolique systématique.
- La correction volémique n'influence pas le bicarbonate.
- Les pertes digestives de HCO3- sont la cause principale.

al-k|Hypokaliémie et alcalose|interaction K+ et alcalose|Hypokaliémie entretient l'alcalose par échanges H+/K+ et sécrétion H+.|3|alcalose,hypokaliémie,mécanisme
+ L'hypokaliémie favorise la réabsorption rénale de HCO3- et la sécrétion d'H+.
+ Corriger le potassium est essentiel pour corriger l'alcalose résistante.
+ Les diurétiques causent souvent alcalose ET hypokaliémie.
+ Les glycosides cardiaques sont plus toxiques en hypokaliémie associée à alcalose.
- L'hyperkaliémie entretient classiquement l'alcalose métabolique.
- Le potassium n'a aucun rôle dans la réabsorption du bicarbonate.
- L'alcalose corrige toujours spontanément l'hypokaliémie.
- Les pertes urinaires de K+ diminuent en alcalose.

al-hyper|Hyperaldostéronisme|hyperaldostéronisme et alcalose|HTA, hypokaliémie, alcalose ; chlorurie élevée.|3|alcalose,aldostérone,HTA
+ L'hyperaldostéronisme primaire peut associer HTA, hypokaliémie et alcalose métabolique.
+ La chlorurie urinaire est typiquement élevée malgré l'hypovolémie relative.
+ Le traitement peut inclure antagonistes de l'aldostérone ou chirurgie adénome.
+ Le syndrome de Liddle mime une hyperminéralocorticisme avec alcalose.
- L'hyperaldostéronisme provoque une acidose métabolique.
- La pression artérielle est normale dans l'hyperaldostéronisme primaire.
- La chlorurie est basse dans l'hyperaldostéronisme.
- L'aldostérone diminue la sécrétion distale de H+.

al-post|Alcalose post-hypercapnie|alcalose post-hypercapnie|Après correction rapide de PaCO2 chez BPCO ; chlorurie basse.|3|alcalose,BPCO,post-hypercapnie
+ Survient après correction trop rapide de l'hypercapnie chronique.
+ Le HCO3- reste élevé alors que PaCO2 chute, générant une alcalose.
+ Traitement : chlorure, parfois acetazolamide si persistante.
+ Prévention par correction progressive de la PaCO2 en ventilation mécanique.
- L'alcalose post-hypercapnie nécessite toujours une dialyse d'urgence.
- Elle survient uniquement chez le sujet jeune sans BPCO.
- La chlorurie est très élevée dès le début.
- Le bicarbonate plasmatique est bas au moment de l'hypercapnie chronique.

al-milk|Syndrome du lait et alcalose|syndrome du lait-alcali|Ingestion de calcium et absorbants ; hypercalcémie possible.|2|alcalose,calcium,médicament
+ Le syndrome du lait et alcali associe alcalose, hypercalcémie et insuffisance rénale fonctionnelle.
+ Les antiacides à base de calcium et bicarbonate sont en cause.
+ L'arrêt des absorbants et réhydratation sont le traitement.
+ Peut mimer une crise hypercalcémique.
- Le syndrome du lait-alcali provoque une acidose profonde.
- Il n'y a jamais d'atteinte rénale.
- L'hypercalcémie est absente.
- Seul le traitement chirurgical est efficace.

al-comp|Compensation respiratoire|compensation de l'alcalose métabolique|PaCO2 augmente d'environ 0,7 mmHg par mmol/L de HCO3- au-dessus de 24.|2|alcalose,compensation
+ La compensation attendue augmente la PaCO2 (~0,7 mmHg par mmol/L de HCO3- supplémentaire).
+ Une PaCO2 plus basse que prévu suggère une alcalose respiratoire associée.
+ Une PaCO2 plus haute suggère une acidose respiratoire associée.
+ La compensation est limitée par l'hypoxémie chez le BPCO.
- La PaCO2 diminue en alcalose métabolique compensée.
- La compensation est complète en 30 minutes.
- La formule de Winter s'applique à l'alcalose métabolique.
- L'alcalose métabolique n'a jamais de compensation.

al-bartter|Bartter et Gitelman|tubulopathies avec alcalose|Bartter : anse ; Gitelman : distal ; hypokaliémie et alcalose.|3|alcalose,Bartter,Gitelman
+ Le syndrome de Bartter affecte la branche ascendante épaisse (diurétique-like).
+ Gitelman touche le canal thiazide-sensible avec hypomagnésémie fréquente.
+ Les deux associent hypokaliémie, alcalose et risque de déshydratation.
+ Le traitement inclut anti-aldostérone, AINS, magnésium (Gitelman).
- Bartter et Gitelman provoquent une acidose métabolique.
- La pression artérielle est élevée dans ces syndromes.
- L'hypokaliémie est absente.
- Ces syndromes ne touchent pas le néphron distal.

al-diag|Diagnostic différentiel|diagnostic différentiel de l'alcalose|Vomissements vs hyperaldostéronisme vs diurétiques.|3|alcalose,diagnostic
+ Les vomissements donnent alcalose chloro-sensible avec hypovolémie.
+ L'hyperaldostéronisme donne HTA et chlorurie élevée.
+ Les diurétiques sont une cause iatrogène fréquente hospitalière.
+ Mesurer clairons, ionogramme, aldostérone/ rénine oriente l'étiologie.
- L'acidose respiratoire est la principale cause d'alcalose métabolique.
- La chlorurie est inutile pour le diagnostic.
- L'alcalose ne survient jamais chez le patient sous IEC.
- Le pH urinaire est toujours alcalin en alcalose métabolique.

al-tx|Traitement alcalose|traitement de l'alcalose métabolique|NaCl, KCl, corriger cause ; acetazolamide si chloro-résistante.|3|alcalose,traitement
+ Supplémentation en chlorure (NaCl) si chloro-sensible et hypovolémique.
+ Correction du potassium indispensable si hypokaliémie associée.
+ Arrêt des diurétiques ou antagonistes minéralocorticoïdes selon cause.
+ Acetazolamide peut être utilisé en alcalose chloro-résistante chez l'insuffisant cardiaque.
- Le bicarbonate IV est le traitement de première intention.
- L'acetazolamide aggrave l'alcalose chloro-sensible hypovolémique.
- La transfusion de plaquettes corrige l'alcalose.
- Le traitement ne nécessite jamais de surveiller le potassium.

al-hereditary|Formes héréditaires|alcalose tubulaire héréditaire|Rare ; défauts de réabsorption Cl-/HCO3-.|4|alcalose,génétique,rare
+ Certaines mutations de transporteurs provoquent alcalose persistante dès l'enfance.
+ Le bilan génétique peut être discuté en formes réfractaires.
+ Complications : retard statural, hypokaliémie chronique.
+ Prise en charge multidisciplinaire néphrologie/pédiatrie.
- Les formes héréditaires sont toujours associées à HTA sévère.
- L'alcalose héréditaire disparaît à l'adolescence.
- Le traitement est uniquement dialytique dès le diagnostic.
- Ces patients ont une hyperkaliémie constante.

al-icu|Alcalose en réanimation|alcalose iatrogène en soins critiques|Ventilation mécanique, transfusions, citrate.|3|alcalose,réa,iatrogène
V|Patiente ventilée pour détresse respiratoire, PaCO2 abaissée rapidement à 30 mmHg, pH 7,55, HCO3- 30 mmol/L.
+ La ventilation mécanique excessive peut induire une alcalose respiratoire aiguë.
+ Les transfusions massives (citrate) peuvent contribuer à une alcalose métabolique.
+ Distinguer alcalose primaire respiratoire vs métabolique sur gaz du sang sériels.
+ Ajuster les paramètres ventilatoires pour éviter l'alcalose iatrogène.
- L'alcalose en réanimation est toujours métabolique chloro-sensible.
- Le citrate des CCP diminue le pH systématiquement.
- Une PaCO2 basse ne modifie pas le pH.
- Il faut toujours administrer du bicarbonate en alcalose iatrogène.
"""

HYPERCALCEMIE_BLOCK = r"""
hc-def|Définition hypercalcémie|définition de l'hypercalcémie|Calcium ionisé élevé ; symptômes neuro, digestifs, rénaux.|1|calcium,définition
+ L'hypercalcémie symptomatique se voit souvent au-delà de 3 mmol/L de calcium total (selon albumine).
+ Le calcium ionisé est la mesure la plus fiable si albumine basse ou pH perturbé.
+ Formule de correction : Ca corr ≈ Ca mesuré + 0,02 × (40 - albumine g/L).
+ Les signes cliniques incluent confusion, constipation, polyurie, douleurs osseuses.
- L'hypercalcémie se définit par une calcémie toujours < 2 mmol/L.
- Le calcium ionisé n'est jamais nécessaire en pratique.
- L'albumine n'influence pas le calcium total.
- L'hypercalcémie provoque toujours une hypocalciurie.

hc-pth|Hypercalcémie PTH-dépendante|hyperparathyroïdie primaire|PTH élevée ou inappropriée normale ; adénome, hyperplasie.|2|calcium,PTH,parathyroïde
+ L'hyperparathyroïdie primaire est une cause fréquente d'hypercalcémie chronique légère.
+ PTH élevée ou normale inappropriée avec calcémie haute oriente vers HPT primaire.
+ L'ostéoporose, lithiases et fatigue sont des manifestations.
+ La chirurgie parathyroïdienne est curative si adénome unique.
- L'HPT primaire s'accompagne d'une PTH effondrée.
- La calcémie est toujours normale dans l'HPT primaire.
- Les lithiases sont absentes.
- L'échographie cervicale est inutile avant dosage PTH.

hc-malig|Hypercalcémie maligne|PTHrP et ostéolyse|PTH-related peptide, métastases osseuses, myélome.|3|calcium,cancer,PTHrP
+ Le PTH-related peptide (PTHrP) médie l'hypercalcémie de nombreux cancers solides.
+ Les métastases ostéolytiques libèrent du calcium (myélome, sein, poumon).
+ Les lymphomes peuvent produire du calcitriol et hypercalcémie.
+ Traitement urgent : hydratation IV, bisphosphonates ou dénosumab.
- L'hypercalcémie maligne a une PTH toujours très élevée.
- Les bisphosphonates sont contre-indiqués en hypercalcémie.
- Le myélome ne cause jamais d'hypercalcémie.
- L'hydratation aggrave l'hypercalcémie.

hc-vitd|Vitamine D et hypercalcémie|intoxication à la vitamine D|Granulomatoses, supplémentation excessive.|3|calcium,vitamine D,sarcoidose
+ L'intoxication à la vitamine D ou calcitriol augmente l'absorption intestinale du calcium.
+ La sarcoïdose et autres granulomatoses synthétisent du calcitriol.
+ PTH est généralement basse en hypercalcémie vitamine D dépendante.
+ Traitement : arrêt vitamine D, glucocorticoïdes parfois, hydratation.
- La vitamine D ne peut pas provoquer d'hypercalcémie.
- La PTH est toujours élevée en sarcoïdose.
- Les granulomatoses diminuent la calcémie.
- Le calcitriol abaisse l'absorption du calcium.

hc-immob|Immobilisation et hypercalcémie|immobilisation prolongée|Hypercalcémie chez sujet jeune avec remodelage osseux rapide.|2|calcium,immobilisation
+ L'immobilisation prolongée peut entraîner une résorption osseuse et hypercalcémie.
+ Plus fréquent chez adolescents ou patients neurologiques.
+ La rééducation et hydratation participent au traitement.
+ Distinguer d'une hyperparathyroïdie associée.
- L'immobilisation provoque une hypocalcémie systématique.
- Seuls les sujets âgés sont concernés.
- La PTH est toujours effondrée sans signification.
- L'hypercalcémie d'immobilisation nécessite une parathyroïdectomie.

hc-med|Médicaments|médicaments hypercalcémiants|Thiazidiques, lithium, vitamine A, théophylline.|2|calcium,médicament
+ Les thiazidiques diminuent la calciurie et peuvent révéler une hypercalcémie.
+ Le lithium peut augmenter la sécrétion de PTH.
+ Arrêt ou adaptation du médicament causal si possible.
+ Surveillance ionogramme sous thiazidiques chez sujet à risque.
- Les diurétiques de l'anse augmentent la calcémie.
- Le lithium abaisse toujours la PTH.
- La vitamine A n'a aucun effet sur le calcium.
- Les thiazidiques sont traitement de l'hypercalcémie aiguë.

hc-renal|Atteinte rénale|néphrocalcinose et IRC|Hypercalcémie chronique peut entraîner néphropathie.|3|calcium,rein,néphrocalcinose
+ L'hypercalcémie chronique peut provoquer une néphropathie par précipitation de calcium.
+ La polyurie d'hypercalcémie peut causer une déshydratation et aggravation.
+ La fonction rénale doit être surveillée pendant le traitement.
+ La dialyse peut être nécessaire en hypercalcémie réfractaire sévère.
- L'hypercalcémie protège les reins.
- La néphrocalcinose n'existe pas.
- La polyurie est due à l'ADH élevée uniquement.
- La dialyse est impossible en hypercalcémie.

hc-tx|Traitement aigu|traitement de l'hypercalcémie aiguë|NaCl 0,9%, furosémide après repletion, calcitonine, bisphosphonates.|3|calcium,traitement,urgence
V|Femme de 62 ans, confusion et vomissements. Calcium 3,8 mmol/L, créatinine 180 µmol/L, déshydratée.
+ L'hydratation par NaCl 0,9% est la première étape (souvent 200-300 mL/h avec surveillance).
+ La calcitonine agit rapidement mais effet transitoire (tachyphylaxie).
+ Les bisphosphonates IV (acide zolédronique) ont un effet en 24-72 h.
+ Le dénosumab peut être utilisé si insuffisance rénale sévère contre-indiquant bisphosphonates.
- Le traitement initial est le seul bicarbonate oral.
- La furosémide doit précéder toute expansion volémique.
- Les bisphosphonates agissent en quelques minutes.
- L'hydratation est contre-indiquée si créatinine élevée.

hc-ecg|Signes ECG et urgences|ECG de l'hypercalcémie|QT raccourci ; bradycardie, bloc à haut risque si très élevée.|2|calcium,ECG,urgence
+ L'hypercalcémie peut raccourcir l'intervalle QT à l'ECG.
+ Des troubles du rythme et une bradycardie peuvent survenir si calcémie très élevée.
+ L'hypercalcémie sévère est une urgence thérapeutique.
+ Correction rapide de la déshydratation améliore la tolérance cardiaque.
- L'hypercalcémie allonge systématiquement le QT.
- L'ECG est toujours normal.
- Aucun risque cardiaque avant 4 mmol/L.
- Le QT court est spécifique de l'hypocalcémie uniquement.

hc-fam|HPT familiale|hypercalcémie familiale hypocalciurique|Mutation CaSR ; calcémie élevée stable, calciurie basse.|4|calcium,génétique,CaSR
+ L'hypercalcémie familiale bénigne hypocalciurique (FBH) est liée au récepteur du calcium.
+ PTH normale ou légèrement élevée, calciurie/clearance calcique basse.
+ Pas de chirurgie parathyroïdienne (risque d'hypoparathyroïdie).
+ Distinguer d'un adénome avant intervention cervicale.
- La FBH nécessite une parathyroïdectomie systématique.
- La calciurie est très élevée dans la FBH.
- La calcémie fluctue de façon anarchique.
- La FBH provoque une hypocalcémie.

hc-dial|Dialyse et hypercalcémie|épuration en hypercalcémie sévère|Hémodialyse sans calcium dialysat si réfractaire.|3|calcium,dialyse
+ L'hémodialyse est indiquée en hypercalcémie menaçante réfractaire au traitement médical.
+ Utiliser un bain de dialyse pauvre en calcium si besoin.
+ Surveiller le calcium post-dialyse et rechuter.
+ Associer traitement de la cause sous-jacente (myélome, cancer).
- La dialyse augmente toujours la calcémie.
- Le dialysat doit être enrichi en calcium en hypercalcémie sévère.
- La dialyse est inutile si bisphosphonates disponibles.
- L'épuration péritonéale est contre-indiquée.

hc-chronic|Hypercalcémie chronique légère|suivi de l'hypercalcémie chronique|Surveillance osseuse, fonction rénale, indication chirurgicale.|2|calcium,suivi
+ Une hypercalcémie légère persistante mérite bilan étiologique (PTH, PTHrP, vitamine D).
+ Densitométrie osseuse si HPT primaire.
+ Éviter la déshydratation et médicaments aggravants.
+ Réévaluer l'indication chirurgicale selon guidelines (calcémie, symptômes, os).
- Aucun suivi n'est nécessaire si calcémie à 3,5 mmol/L.
- La densitométrie est inutile.
- L'hypercalcémie chronique ne touche pas les os.
- La chirurgie est obligatoire dès calcémie > 2,6 mmol/L sans symptôme.
"""

HYPERKALIEMIE_BLOCK = r"""
hk-def|Définition hyperkaliémie|définition de l'hyperkaliémie|K+ plasmatique > 5 mmol/L ; risque arythmogène.|1|potassium,définition
+ L'hyperkaliémie est généralement définie par K+ > 5,0 mmol/L (seuils labo variables).
+ Le risque cardiaque augmente surtout au-delà de 6,5 mmol/L et si ascension rapide.
+ Faux hyperkaliémies existent (hémolyse, thrombocytose, fist de poing).
+ Le potassium ionisé ou gaz du sang peut confirmer en cas de doute.
- L'hyperkaliémie est sans danger jusqu'à 8 mmol/L.
- La fist de poing augmente toujours le potassium réel.
- Le K+ ne dépend pas de la fonction rénale.
- L'hyperkaliémie allonge le QT.

hk-ecg|ECG hyperkaliémie|signes ECG de l'hyperkaliémie|Ondes T amples, élargissement QRS, disparition onde P.|2|potassium,ECG,urgence
+ Les ondes T « en chapiteau » sont un signe précoce classique.
+ L'élargissement du QRS et le pattern sinusoïdal précèdent l'arrêt cardiaque.
+ L'ECG peut être normal malgré hyperkaliémie modérée (ne pas rassurer).
+ Un ECG doit être fait en urgence si K+ > 6 ou symptômes.
- L'hyperkaliémie raccourcit le QT de façon typique.
- L'onde P augmente en amplitude en hyperkaliémie.
- L'ECG est toujours pathologique si K+ > 5 mmol/L.
- Le QRS se rétrécit en hyperkaliémie sévère.

hk-renal|Élimination rénale|insuffisance rénale et hyperkaliémie|GFR basse, hypoaldostéronisme, médicaments.|2|potassium,IRC,élimination
+ La fonction rénale est le principal régulateur de l'élimination du potassium.
+ L'hypoaldostéronisme (IRC, AI, diabète) réduit la sécrétion distale de K+.
+ Les inhibiteurs de l'enzyme de conversion et ARAII majorent le risque.
+ Les sels de potassium et substituts alimentaires sont cofacteurs fréquents.
- La dialyse n'élimine jamais le potassium.
- Les IEC diminuent le potassium plasmatique.
- L'aldostérone n'influence pas la kaliémie.
- L'IRC est protectrice contre l'hyperkaliémie.

hk-shift|Déplacement transcellulaire|shift transcellulaire du potassium|Acidose, nécrose, rhabdomyolyse, succinylcholine.|3|potassium,shift,urgence
+ L'acidose métabolique déplace le K+ vers le compartiment extracellulaire.
+ La rhabdomyolyse libère massivement du potassium des cellules musculaires.
+ La succinylcholine peut augmenter le K+ en dépolarisation (risque si dénervation).
+ Le traitement inclut stabilisation membrane, shift intracellulaire, élimination.
- L'alcalose provoque une sortie de potassium vers le sang.
- La rhabdomyolyse abaisse le potassium.
- La succinylcholine est sans effet sur le K+.
- Le shift transcellulaire n'existe pas cliniquement.

hk-tx-acute|Traitement hyperkaliémie aiguë|urgence hyperkaliémique|Gluconate Ca, insuline-glucose, β2, résines, dialyse.|3|potassium,traitement,urgence
V|Homme de 70 ans, IRC stade 5, K+ 7,2 mmol/L, QRS élargi à l'ECG, PA 90/50.
+ Le gluconate de calcium IV stabilise la membrane cardiaque sans baisser le K+.
+ Insuline + glucose fait entrer le K+ dans les cellules (surveillance hypoglycémie).
+ Les β2-mimétiques nébulisés ou IV contribuent au shift intracellulaire.
+ La dialyse est le traitement d'élimination ultime si IR sévère.
- Le bicarbonate est toujours la première ligne même sans acidose.
- Le gluconate de calcium diminue immédiatement le K+ plasmatique.
- Les résines à l'actif charcoal sont utilisées en première intention IV.
- L'insuline est contre-indiquée si glycémie normale.

hk-resin|Résines échangeuses|résines de potassium|Kayexalate (sodium polystyrène sulfonate) ; effet lent, constipation.|2|potassium,résine
+ Les résines échangent Na+ contre K+ dans le colon (effet en heures).
+ Attention : nécrose intestinale rare, surtout post-op ou constipation.
+ Sorbitol était associé mais risque digestif ; hydratation et surveillance.
+ Moins utile en urgence vitale immédiate que shift et dialyse.
- Les résines agissent en quelques secondes.
- Elles sont sans risque digestif.
- Elles remplacent la dialyse en IRA complète.
- Le Kayexalate augmente le potassium.

hk-pseudo|Pseudo-hyperkaliémie|fausse hyperkaliémie|Prélèvement difficile, hémolyse, leucocytose très élevée.|2|potassium,prélèvement
+ Reprélèvement sur tube correct, sans fist de poing prolongée.
+ Potassium plasmatique élevé avec gaz du sang normal suggère pseudo-hyperkaliémie.
+ Thrombocytose et leucocytose extrêmes peuvent fausser le résultat.
+ Ne pas traiter agressivement sans confirmation si doute.
- Toute hyperkaliémie au labo est vraie.
- L'hémolyse abaisse le potassium mesuré.
- Le prélèvement artériel est impossible pour K+.
- La pseudo-hyperkaliémie nécessite dialyse d'urgence.

hk-ald|Aldostérone et résistance|hypoaldostéronisme|Diabète, AI, héparine, triméthoprime.|3|potassium,aldostérone
+ L'insuffisance surrénalienne diminue la sécrétion d'aldostérone et retient le K+.
+ Le triméthoprime bloque ENaC comme amiloride et hyperkaliémie.
+ L'héparine non fractionnée peut inhiber l'aldostérone.
+ Le syndrome de Gordon (PHA type 2) associe HTA et hyperkaliémie.
- L'hyperaldostéronisme cause l'hyperkaliémie.
- Le triméthoprime augmente la kaliurèse.
- L'héparine augmente l'aldostérone.
- Le diabète protège du potassium élevé.

hk-tubular|Tubulopathies hyperkaliémiques|tubulopathies avec hyperK+|RTA type 4, obstructif, médicaments K-sparing.|3|potassium,RTA,tubule
+ La RTA type 4 combine acidose hyperkaliémique et hypoaldostéronisme relatif.
+ L'amiloride et spironolactone diminuent l'élimination du potassium.
+ L'obstruction urinaire aiguë peut retarder l'élimination du K+.
+ Traitement : arrêt médicaments, fludrocortisone si AI, dialyse si besoin.
- La RTA type 1 est typiquement hyperkaliémique.
- Les diurétiques épargneurs de potassium abaissent le K+.
- L'obstruction urinaire hypokaliémise toujours.
- La spironolactone est indiquée pour traiter l'hyperkaliémie.

hk-chronic|Hyperkaliémie chronique|prise en charge chronique|régime, arrêt médicaments, patiromer/cyclosilicate.|2|potassium,chronique
+ Réduction apports alimentaires en potassium si nécessaire.
+ Réviser IEC/ARAII, spironolactone, AINS, triméthoprime.
+ Les chélateurs de potassium (patiromer, zirconium cyclosilicate) peuvent aider.
+ Surveillance rapprochée en insuffisance rénale avancée.
- Le régime sans potassium est inutile en IRC.
- Les IEC peuvent être poursuivis sans surveillance en IRC terminale.
- Les chélateurs remplacent toute dialyse.
- L'hyperkaliémie chronique n'existe pas.

hk-dial|Dialyse et potassium|épuration du potassium|Bain de dialyse sans potassium en urgence.|3|potassium,dialyse
+ L'hémodialyse est très efficace pour abaisser le potassium rapidement.
+ Bain de dialyse adapté (souvent K 2-3 mmol/L, sans K en urgence extrême).
+ Surveillance post-dialyse : rebond par shift et apports.
+ Indiquée si traitement médical insuffisant ou IR terminale.
- La dialyse augmente le potassium.
- Le dialysat riche en potassium est utilisé en hyperkaliémie.
- La dialyse péritonéale est plus rapide que l'hémodialyse pour le K+.
- Aucune surveillance n'est requise pendant la dialyse.

hk-peaks|Rebond et surveillance|rebond post-traitement|K+ peut rebondir après insuline ; planifier élimination.|3|potassium,surveillance
+ Le shift intracellulaire est temporaire ; prévoir élimination rénale ou dialyse.
+ Contrôles répétés du K+ et ECG jusqu'à stabilisation.
+ Identifier et traiter la cause (obstruction, médicament, acidose).
+ Éviter les apports oraux/IV de potassium pendant la phase aiguë.
- Un seul contrôle suffit après insuline.
- Le rebond n'existe pas.
- L'ECG n'a plus besoin d'être suivi après une dose de calcium.
- On peut reprendre les sels de potassium le jour même.
"""

HYPERNATREMIE_BLOCK = r"""
hn-def|Définition hypernatrémie|définition de l'hypernatrémie|Na+ > 145 mmol/L ; déficit d'eau libre.|1|sodium,définition
+ L'hypernatrémie reflète généralement un déficit d'eau par rapport au sodium.
+ Elle est souvent associée à une hyperosmolarité plasmatique.
+ Les symptômes neurologiques (confusion, convulsions) apparaissent si installation rapide ou sévère.
+ Les sujets âgés et nourrissons sont particulièrement vulnérables.
- L'hypernatrémie signifie toujours un excès de sodium total massif.
- Le sodium plasmatique ne corrèle pas à l'osmolarité.
- Elle est toujours asymptomatique.
- L'hypernatrémie est définie par Na+ < 135 mmol/L.

hn-mech|Physiopathologie|perte d'eau vs apport de Na+|Diabète insipide, pertes insensibles, apports salés.|2|sodium,mécanisme
+ Les pertes d'eau libre (peau, poumons) sans compensation augmentent le Na+.
+ Le diabète insipide central ou néphrogénique entraîne une polyurie hypotonique.
+ L'apport excessif de NaCl (perfusions, alimentation entérale) peut hypernatrémiser.
+ La soif normale est le principal mécanisme de protection chez l'adulte conscient.
- L'hypernatrémie résulte toujours d'une perte de sodium.
- La soif est absente chez tout adulte malade.
- Le diabète insipide diminue le volume urinaire.
- Les pertes insensibles diluent le sodium.

hn-di|Diabète insipide|diabète insipide et hypernatrémie|Polyurie hypotonique ; test désopressine.|3|sodium,DI,vasopressine
+ Le DI central répond à la desmopressine (concentration urinaire).
+ Le DI néphrogénique ne répond pas (cause médicamenteuse, hypercalcémie).
+ L'osmolarité urinaire basse avec plasma hyperosmolaire est évocatrice.
+ Traitement : desmopressine si central, traitement cause si néphrogénique.
- Le DI se manifeste par oligurie.
- La desmopressine est efficace dans le DI néphrogénique lithium.
- L'urine est toujours concentrée en DI.
- L'hypernatrémie est absente en DI non traité.

hn-elder|Sujet âgé|hypernatrémie du sujet âgé|Défaut de soif, dépendance, fièvre, sondes.|2|sodium,âge,iatrogène
V|Homme de 88 ans, aphasie, Na+ 158 mmol/L, prise orale impossible depuis 3 jours, fièvre 38,5°C.
+ La diminution de la soif et l'impossibilité d'accès à l'eau favorisent l'hypernatrémie.
+ Les infections et fièvre augmentent les pertes insensibles.
+ Réhydratation progressive (eau libre entérale ou glucose 5%).
+ Surveillance neurologique rapprochée pendant correction.
- L'hypernatrémie du sujet âgé ne nécessite jamais de traitement.
- Il faut corriger le Na+ en moins de 2 h à la valeur normale.
- La fièvre diminue les pertes d'eau.
- Les sondes gastriques empêchent l'hypernatrémie.

hn-tx|Vitesse de correction|traitement de l'hypernatrémie|Correction lente : max 10-12 mmol/L/24 h pour éviter œdème cérébral.|3|sodium,traitement,neuro
+ Une correction trop rapide peut provoquer un œdème cérébral et convulsions.
+ Objectif : diminuer le Na+ progressivement sur 24-48 h.
+ Utiliser eau libre (enterale, IV hypotonique) selon hémodynamique.
+ Traiter la cause (DI, fièvre, hyperglycémie osmotique).
- Corriger 20 mmol/L de Na+ en 6 h est recommandé.
- L'œdème cérébral survient si correction lente.
- Le NaCl 3% est le traitement de l'hypernatrémie.
- La vitesse de correction n'a pas d'importance.

hn-hypergly|Hyperglycémie et Na+|correction du sodium en hyperglycémie|Hyperglycémie abaisse Na+ mesuré ; corriger si besoin.|2|sodium,glucose
+ Chaque 3,3 mmol/L (60 mg/dL) de glycémie au-dessus de normal abaisse Na+ d'environ 1 mmol/L.
+ Corriger le sodium pour estimer la natrémie réelle en présence d'hyperglycémie.
+ Traiter l'hyperglycémie peut faire monter le Na+ apparent (eau vers intracellulaire).
+ Surveiller la natrémie pendant traitement insulinique.
- L'hyperglycémie augmente toujours le sodium mesuré.
- Aucune correction n'est nécessaire en CAD.
- L'insuline n'influence pas le sodium.
- Le Na+ corrigé est inférieur au Na+ mesuré en hyperglycémie.

hn-loss|Pertes d'eau|pertes cutanées et digestives|Brûlures, sudation, diarrhée hypotonique.|2|sodium,pertes
+ Les brûlures étendues augmentent les pertes insensibles d'eau.
+ Une diarrhée hypotonique peut entraîner hypernatrémie si apports insuffisants.
+ Les patients ventilés ont des pertes respiratoires accrues.
+ Réhydratation et couverture des pertes quotidiennes.
- Les diarrhées provoquent toujours une hyponatrémie.
- Les brûlures n'affectent pas l'équilibre hydrique.
- La ventilation mécanique diminue les pertes d'eau.
- Les pertes digestives sont toujours hypertoniques.

hn-iatro|Iatrogénie|hypernatrémie iatrogène|Perfusions hypertoniques, bicarbonate, nutrition.|3|sodium,iatrogène
+ Administration de NaCl 3% ou multiples bolus salés peut hypernatrémiser.
+ Solutions hypertoniques en réanimation doivent être monitorées.
+ Nutrition entérale concentrée sans eau libre adjointe est un facteur.
+ Bilan entrées-sorties strict en réanimation.
- Les perfusions glucosées hypernatrémisent toujours.
- L'iatrogénie est impossible en milieu hospitalier.
- Le bicarbonate 8,4% n'apporte pas de sodium.
- La nutrition entérale ne contient jamais de sodium.

hn-neuro|Signes neurologiques|neurologie de l'hypernatrémie|Confusion, spasticité, hémorragie, coma.|2|sodium,neurologie
+ Le cerveau se déshydrate en hypernatrémie hyperosmolaire.
+ Convulsions et hémorragies intracrâniennes sont des complications graves.
+ Les symptômes dépendent de la rapidité d'installation.
+ Prise en charge en milieu surveillé si sévère.
- L'hypernatrémie améliore toujours l'état neurologique.
- Les convulsions n'ont aucun lien avec le Na+.
- L'installation lente est toujours symptomatique majeure.
- Le coma est absent si Na+ < 160 mmol/L.

hn-ped|Pédiatrie|hypernatrémie du nourrisson|Diarrhée, préparation lactée inadéquate.|3|sodium,pédiatrie
+ Les nourrissons ont une surface cutanée relative élevée et soif limitée.
+ Préparations lactées mal diluées ou apports salés excessifs sont des causes.
+ Correction prudente avec surveillance du poids et diurèse.
+ Éducation parentale sur reconstitution des biberons.
- L'hypernatrémie néonatale n'existe pas.
- Les nourrissons compensent toujours par la soif.
- La dilution excessive du lait artificiel provoque hypernatrémie.
- Aucune surveillance spécifique n'est requise.

hn-diag|Diagnostic étiologique|bilan de l'hypernatrémie|Osmolarité, diurèse, ADH, médicaments.|2|sodium,diagnostic
+ Calculer l'osmolarité plasmatique et urinaire.
+ Distinguer déficit d'apport d'eau vs pertes vs diabète insipide.
+ Rechercher médicaments (lithium, anticholinergiques).
+ Bilan de déshydratation et fonction rénale.
- L'osmolarité urinaire est toujours > 800 mOsm/kg en hypernatrémie.
- Le lithium n'affecte pas la concentration urinaire.
- Le bilan étiologique est inutile.
- L'ADH est toujours effondrée en hypernatrémie.

hn-chronic|Hypernatrémie chronique|formes chroniques|Adaptation cérébrale avec idées osmotiques.|3|sodium,chronique
+ Le cerveau produit des idées osmotiques en hypernatrémie chronique.
+ Correction trop rapide malgré adaptation expose à l'œdème cérébral.
+ Correction encore plus prudente si hypernatrémie > 48 h.
+ Réévaluer les apports d'eau à long terme (sonde, aide sociale).
- Le cerveau ne s'adapte jamais.
- La correction rapide est sans risque si chronique.
- Les idées osmotiques disparaissent en quelques minutes.
- L'hypernatrémie chronique est bénigne sans traitement.
"""

HYPERPHOSPHATEMIE_BLOCK = r"""
hp-def|Définition hyperphosphatémie|définition de l'hyperphosphatémie|Phosphate plasmatique élevé ; souvent IRC.|1|phosphate,définition
+ L'hyperphosphatémie est fréquente en insuffisance rénale chronique avancée.
+ Le phosphate plasmatique normal est environ 0,8-1,45 mmol/L (selon labo).
+ Elle participe au syndrome phospho-calcique de l'IRC.
+ Peut être asymptomatique ou contribuer aux symptômes urémiques.
- L'hyperphosphatémie est rare en IRC.
- Le phosphate n'a aucun rôle osseux.
- L'hyperphosphatémie abaisse toujours la PTH.
- Le phosphate plasmatique est indépendant de l'alimentation.

hp-renal|IRC et hyperphosphatémie|phosphore en insuffisance rénale|Diminution de l'excrétion rénale principale cause.|2|phosphate,IRC,néphro
+ La baisse du DFG réduit l'élimination urinaire du phosphate.
+ L'hyperphosphatémie stimule la PTH (hyperparathyroïdie secondaire).
+ Le syndrome phospho-calcique inclut ostéodystrophie et calcifications vasculaires.
+ Les chélateurs de phosphate et dialyse sont des piliers thérapeutiques.
- L'IRC augmente l'excrétion urinaire de phosphate.
- La PTH diminue en hyperphosphatémie.
- Le phosphate n'influence pas l'os de l'IRC.
- La dialyse n'élimine pas le phosphate.

hp-tumor|Lyse tumorale|syndrome de lyse tumorale|Hyperphosphatémie, hyperkaliémie, hyperuricémie, hypocalcémie.|3|phosphate,lyse,urgence
V|Jeune homme avec lymphome, chimiothérapie débutée hier : phosphate 2,5 mmol/L, K+ 6,1, Ca 1,9 mmol/L, uricémie élevée.
+ La lyse tumorale libère phosphate intracellulaire dans le sang.
+ Hyperkaliémie et hyperuricémie associées ; hypocalcémie par précipitation.
+ Prévention par hydratation, allopurinol ou rasburicase selon protocoles.
+ Dialyse possible en forme sévère réfractaire.
- La lyse tumorale abaisse le phosphate.
- L'hypocalcémie est absente.
- L'allopurinol est inutile.
- La chimiothérapie ne déclenche jamais de lyse.

hp-rhabdo|Rhabdomyolyse|rhabdomyolyse et phosphate|Libération cellulaire avec hyperphosphatémie et hyperkaliémie.|3|phosphate,rhabdomyolyse
+ La destruction musculaire libère phosphate, potassium et myoglobine.
+ Insuffisance rénale aiguë par néphrotoxicité de la myoglobine.
+ Hydratation agressive et alcalinisation parfois discutées.
+ Surveillance diurèse et épuration si besoin.
- La rhabdomyolyse diminue le phosphate plasmatique.
- La myoglobine protège les reins.
- L'hyperphosphatémie est un signe de bon pronostic.
- Aucune hyperkaliémie n'est attendue.

hp-vitd|Vitamine D et phosphate|vitamine D et absorption|Intoxication vitamine D peut augmenter phosphate et calcium.|2|phosphate,vitamine D
+ Le calcitriol augmente l'absorption intestinale de phosphate et calcium.
+ L'intoxication aux analogues de vitamine D est une cause d'hyperphosphatémie.
+ PTH souvent basse dans ce contexte.
+ Arrêt de l'excès de vitamine D et traitement symptomatique.
- La vitamine D abaisse le phosphate.
- L'intoxication vitamine D n'affecte pas le calcium.
- La PTH est toujours très élevée.
- Le phosphate urinaire augmente massivement.

hp-tx|Traitement chélateurs|chélateurs de phosphate|Carbonate de calcium, sevelamer, lanthane, ferric citrate.|2|phosphate,traitement,chélateur
+ Les chélateurs se prennent au repas pour lier le phosphate alimentaire.
+ Le carbonate de calcium peut corriger hypocalcémie mais risque calcifications.
+ Sevelamer et lanthane sans calcium ; ferric citrate possible.
+ Adhésion et timing des prises sont essentiels à l'efficacité.
- Les chélateurs se prennent à jeun le matin uniquement.
- Le sevelamer augmente le phosphate absorbé.
- Aucun effet sur la PTH.
- Les chélateurs remplacent la dialyse en urgence de lyse.

hp-dial|Dialyse et phosphate|épuration du phosphate|Hémodialyse efficace ; dialyse péritonéale quotidienne.|2|phosphate,dialyse
+ L'hémodialyse élimine le phosphate ; fréquence et durée influencent le contrôle.
+ La dialyse péritonéale continue peut mieux contrôler que HD intermittente.
+ Objectifs de phosphate selon recommandations KDIGO en IRC.
+ Associer régime et chélateurs entre séances.
- La dialyse augmente le phosphate plasmatique.
- Une séance HD hebdomadaire suffit toujours.
- Le phosphate ne traverse pas la membrane de dialyse.
- La dialyse péritonéale est inefficace sur le phosphate.

hp-diet|Régime|restriction phosphorée|réduire produits laitiers, additifs phosphatés.|2|phosphate,régime
+ Les additifs phosphatés des aliments industriels sont très absorbables.
+ Limiter produits laitiers, colas, charcuteries riches en phosphate.
+ Éducation diététique avec néphrologue et diététicien.
+ Complément aux chélateurs, pas substitut seul en IRC avancée.
- Le régime sans restriction est recommandé en IRC terminale.
- Les additifs phosphatés ne sont pas absorbés.
- Le poisson n'apporte jamais de phosphate.
- Le régime augmente le phosphate sanguin.

hp-calc|Relation calcium-phosphate|produit Ca×P|Risque calcifications si produit calcium × phosphate élevé.|3|phosphate,calcium,IRC
+ Un produit calcium × phosphate élevé favorise calcifications vasculaires et tissulaires.
+ Contrôler simultanément calcémie et phosphatémie en IRC.
+ Les chélateurs sans calcium peuvent être préférés si calcémie haute.
+ La PTH doit être dans une cible adaptée (éviter adénome et ostéoporose urémique).
- Le produit Ca×P n'a aucune signification clinique.
- L'hyperphosphatémie protège des calcifications.
- La calcémie n'interagit pas avec le phosphate.
- La PTH doit être abolie complètement.

hp-acute|Hyperphosphatémie aiguë|formes aiguës symptomatiques|Lyse, IRA, intoxication ; traiter cause et épurer.|3|phosphate,urgence
+ Identifier lyse tumorale, rhabdomyolyse, IRA obstructive.
+ Hydratation et épuration extra-rénale si troubles hydro-électrolytiques associés.
+ Ne pas oublier hypocalcémie symptomatique liée à la précipitation.
+ Surveillance cardiaque si hyperkaliémie associée.
- L'hyperphosphatémie aiguë est toujours bénigne.
- Aucun lien avec le potassium.
- L'hypocalcémie est impossible.
- Le traitement est uniquement oral.

hp-pseudo|Pseudo-hyperphosphatémie|interférences analytiques|Hémolyse, thrombocytose peuvent fausser rarement.|2|phosphate,labo
+ Reprélèvement si résultat incohérent avec clinique.
+ Vérifier tube, délai, hémolyse sur bilan associé.
+ Contexte biologique global (fonction rénale, Ca, K).
+ Ne pas surtraiter sur un seul résultat douteux.
- Toute hyperphosphatémie est vraie.
- L'hémolyse abaisse le phosphate mesuré.
- Aucune interference analytique n'existe.
- Le prélèvement veineux est impossible pour le phosphate.

hp-secondary|Hyperparathyroïdie secondaire|HPT secondaire à l'hyperphosphatémie|Phosphate élevé stimule PTH ; vitamine D déficiente.|3|phosphate,PTH,IRC
+ L'hyperphosphatémie chronique est un stimulus majeur à la PTH en IRC.
+ La carence en vitamine D et l'hypocalcémie aggravent l'HPT secondaire.
+ Analogues vitamine D et calcimimétiques (cinacalcet) font partie du traitement.
+ Parathyroïdectomie si HPT sévère résistante.
- L'hyperphosphatémie inhibe la PTH.
- La vitamine D n'a pas de rôle en néphrologie.
- Le cinacalcet augmente la PTH.
- La parathyroïdectomie est interdite en IRC.
"""

HYPOCALCEMIE_BLOCK = r"""
hcy-def|Définition hypocalcémie|définition de l'hypocalcémie|Ca total bas ; privilégier calcium ionisé si doute.|1|calcium,définition
+ L'hypocalcémie symptomatique survient souvent si calcium ionisé est bas.
+ Correction pour albumine : Ca corr ≈ Ca mesuré + 0,02 × (40 - albumine).
+ Signes : paresthésies, tétanie, signe de Chvostek/Trousseau, QT long.
+ Urgence si convulsions ou bronchospasme.
- L'hypocalcémie allonge toujours le QT à l'ECG de façon impossible à voir.
- Le calcium ionisé est identique au calcium total sans albumine.
- L'hypocalcémie est toujours asymptomatique.
- La calcémie normale exclut tout trouble du calcium.

hcy-pth|Hypocalcémie PTH-élevée|hypoparathyroïdie et résistance|PTH haute : carence vit D, IRC, résistance PTH.|2|calcium,PTH,vitamine D
+ Une PTH élevée avec hypocalcémie évoque carence en vitamine D ou pseudohypoparathyroïdie.
+ En IRC, l'hypocalcémie stimule une PTH secondaire élevée.
+ La pseudohypoparathyroïdie associe PTH élevée et résistance aux effets de la PTH.
+ Dosage 25-OH vitamine D et calcémie corrigée orientent le diagnostic.
- Une PTH élevée exclut toute hypocalcémie.
- La carence en vitamine D abaisse la PTH.
- L'IRC diminue toujours la PTH.
- La pseudohypoparathyroïdie a une PTH effondrée.

hcy-hypopara|Hypoparathyroïdie|hypoparathyroïdie vraie|PTH basse post-chirurgie thyroïdienne, auto-immune.|3|calcium,hypoparathyroïdie
+ La chirurgie thyroïdienne/parathyroïdienne est une cause fréquente.
+ PTH basse inappropriée avec hypocalcémie et phosphatémie souvent normale ou haute.
+ Traitement : calcium oral, calcitriol, parfois PTH recombinante.
+ Surveillance rénale (néphrocalcinose) sous supplémentation.
- L'hypoparathyroïdie s'accompagne d'une PTH très élevée.
- Le phosphate est toujours bas.
- Aucun traitement n'est nécessaire.
- La chirurgie cervicale ne touche jamais les parathyroïdes.

hcy-vitd|Carence vitamine D|carence en vitamine D|Ostéomalacie, myopathie, hypocalcémie avec PTH élevée.|2|calcium,vitamine D
+ La carence en vitamine D diminue l'absorption intestinale du calcium.
+ PTH secondairement élevée (hyperparathyroïdie secondaire).
+ Supplémentation en cholécalciférol ou ergocalciférol selon protocole.
+ Rechercher malabsorption, insuffisance hépatique, néphropathie.
- La vitamine D n'influence pas la calcémie.
- La PTH est basse en carence vitamine D.
- L'ostéomalacie n'existe pas.
- Seul le calcitriol oral est utilisé d'emblée sans bilan.

hcy-acute|Hypocalcémie aiguë|urgence hypocalcémique|Gluconate de calcium IV si tétanie, convulsions.|3|calcium,traitement,urgence
V|Femme post-thyroïdectomie J1, fourmillements, carpédège, Ca 1,75 mmol/L, QT allongé.
+ Le gluconate de calcium IV (voie centrale si possible) en urgence symptomatique.
+ Perfusion continue possible ; surveiller infiltration tissulaire en périphérique.
+ Ajouter calcitriol et calcium oral dès que possible.
+ Magnésium bas peut entraîner hypocalcémie réfractaire (corriger Mg).
- Le bicarbonate IV est le traitement de l'hypocalcémie aiguë.
- Le calcium IV est contre-indiqué si QT long.
- Le magnésium n'a aucun lien avec le calcium.
- Aucune surveillance ECG n'est requise.

hcy-mg|Magnésium et calcium|hypomagnésémie|Hypomagnésémie entraîne hypocalcémie et résistance PTH.|3|calcium,magnésium
+ L'hypomagnésémie sévère bloque la sécrétion et l'action de la PTH.
+ Causes : alcoolisme, diurétiques, chimiothérapie, malabsorption.
+ Corriger le magnésium pour permettre correction du calcium.
+ Surveillance ECG (torsades de pointes).
- L'hypomagnésémie augmente la calcémie.
- Le magnésium n'affecte pas la PTH.
- La supplémentation en calcium suffit sans magnésium.
- Les torsades sont liées à l'hypercalcémie uniquement.

hcy-pancreas|Pancréatite aiguë|pancréatite et hypocalcémie|Précipitation de savons de calcium ; signe de mauvais pronostic.|3|calcium,pancréatite
+ L'hypocalcémie en pancréatite aiguë sévère est un critère de gravité (Ranson, BISAP).
+ Mécanisme : saponification des graisses péripancréatiques.
+ Ne pas surcorriger agressivement sans indication symptomatique.
+ Traitement prioritaire de la pancréatite et réanimation.
- L'hypercalcémie est typique de la pancréatite.
- L'hypocalcémie est signe de bon pronostic.
- La saponification augmente le calcium ionisé.
- Le calcium doit être normalisé en urgence systématique.

hcy-trans|Transfusion massive|citrate et hypocalcémie|Citrate des CCP chélate le calcium ; surveiller en réa.|3|calcium,transfusion,réa
+ Le citrate anticoagulant des produits sanguins peut hypocalcémiser en perfusion rapide.
+ Surveillance du calcium ionisé pendant transfusion massive.
+ Supplémentation en gluconate de calcium si besoin.
+ Insuffisance hépatique réduit métabolisme du citrate (risque accru).
- Le citrate augmente le calcium libre.
- Les transfusions n'affectent jamais la calcémie.
- Aucune surveillance en réanimation.
- L'insuffisance hépatique protège de l'hypocalcémie.

hcy-diag|Signes cliniques|signes de l'hypocalcémie|Chvostek, Trousseau, crampes, laryngospasme.|2|calcium,clinique
+ Le signe de Chvostek : contraction faciale à percussion du nerf facial.
+ Le signe de Trousseau : spasmes carpopédaux au brassard.
+ Paresthésies péri-buccales et des extrémités sont fréquentes.
+ Convulsions et bronchospasme en formes sévères.
- Chvostek est spécifique à 100% de l'hypocalcémie.
- Trousseau est normal chez tout sujet sain.
- Aucun signe neurologique en hypocalcémie.
- Le laryngospasme est typique de l'hypercalcémie.

hcy-chronic|Hypocalcémie chronique|formes chroniques|Cataracte, encéphalopathie, anomalies dentaires.|2|calcium,chronique
+ L'hypocalcémie chronique peut entraîner cataracte et calcifications intracrâniennes.
+ Suivi régulier calcémie, phosphate, fonction rénale.
+ Éducation sur signes d'alerte et observance du calcitriol.
+ Densité osseuse peut être augmentée en hypoparathyroïdie.
- L'hypocalcémie chronique protège des cataractes.
- Aucun suivi n'est nécessaire.
- Le calcitriol est toujours inutile chroniquement.
- Les dents sont toujours normales.

hcy-drug|Médicaments|médicaments hypocalcémiants|Bisphosphonates, calcitonine, cinacalcet, phénobarbital.|2|calcium,médicament
+ Les bisphosphonates inhibent la résorption osseuse et peuvent abaisser le calcium.
+ Le cinacalcet diminue la PTH et peut hypocalcémiser.
+ Revoir les traitements en cas d'hypocalcémie inexpliquée.
+ Adapter posologie ou substituer selon contexte.
- Les bisphosphonates augmentent la calcémie.
- Le cinacalcet est indiqué pour traiter l'hypercalcémie en augmentant Ca.
- Les antiépileptiques n'influencent pas la vitamine D.
- Aucun médicament n'abaisse le calcium.

hcy-alk|Alcalose et calcium|alcalose et calcium ionisé|Alcalémie augmente liaison à l'albumine et baisse Ca ionisé.|3|calcium,alcalose
+ En alcalose, le calcium ionisé diminue même si calcium total stable.
+ Correction de l'alcalose peut améliorer les symptômes hypocalcémiques.
+ Gaz du sang avec calcium ionisé si doute peri-opératoire.
+ Ne pas oublier ce mécanisme en hyperventilation.
- L'alcalose augmente le calcium ionisé.
- Le calcium total augmente en alcalose.
- L'alcalose n'a aucun effet symptomatique.
- Le calcium ionisé est inutile en réanimation.
"""

HYPOKALIEMIE_BLOCK = r"""
hko-def|Définition hypokaliémie|définition de l'hypokaliémie|K+ < 3,5 mmol/L ; risque arythmie et paralysie.|1|potassium,définition
+ L'hypokaliémie majore le risque d'arythmies, notamment sous digoxine.
+ Une baisse de 1 mmol/L de K+ peut correspondre à un déficit de 200-400 mmol.
+ Les symptômes incluent fatigue, crampes, constipation, polyurie.
+ Hypokaliémie sévère (< 2,5) peut provoquer paralysie et détresse respiratoire.
- L'hypokaliémie est sans danger sous digoxine.
- Le potassium intracellulaire est identique au plasmatique.
- L'hypokaliémie provoque toujours hyperkaliémie au ECG.
- K+ < 4 mmol/L est toujours normal.

hko-ecg|ECG hypokaliémie|signes ECG|Ondes U, aplatisement T, QT long, extrasystoles.|2|potassium,ECG
+ L'apparition d'ondes U est classique en hypokaliémie.
+ Aplatissement ou inversion des ondes T peut être observé.
+ Risque de torsades de pointes si QT long associé.
+ ECG recommandé si hypokaliémie modérée à sévère ou symptômes.
- L'hypokaliémie raccourcit le QT systématiquement.
- Les ondes T deviennent toujours pointues.
- L'ECG est toujours normal si K+ > 3 mmol/L.
- Aucun risque arythmique existe.

hko-renal|Pertes rénales|pertes rénales de potassium|Diurétiques, hyperaldostéronisme, tubulopathies.|2|potassium,rein,diurétique
+ Les diurétiques de l'anse et thiazidiques augmentent la kaliurèse.
+ L'hyperaldostéronisme et le hypercorticisme augmentent les pertes de K+.
+ Le syndrome de Gitelman et Bartter associent hypokaliémie et alcalose.
+ Rechercher hypertension (Conn) vs normotension (Gitelman).
- Les diurétiques épargnent toujours le potassium.
- L'aldostérone diminue les pertes urinaires de K+.
- Gitelman provoque une hyperkaliémie.
- Les pertes rénales n'existent pas.

hko-digest|Pertes digestives|pertes digestives de potassium|Diarrhée, fistules, laxatifs.|2|potassium,digestif
+ Les diarrhées profuses entraînent des pertes importantes de K+.
+ Les laxatifs et villosité adénomateuse peuvent hypokaliémiser.
+ Réhydratation avec solutions contenant potassium si besoin.
+ Associer souvent une alcalose métabolique (pertes H+).
- La diarrhée augmente le potassium plasmatique.
- Les laxatifs augmentent le K+.
- Les pertes digestives n'entraînent jamais d'alcalose.
- Le potassium n'est pas présent dans les selles.

hko-shift|Shift intracellulaire|entrée du potassium dans les cellules|Insuline, β2-agonistes, alcalose, réalimentation.|3|potassium,shift
+ L'insuline fait entrer le potassium dans les cellules (traitement DKA).
+ Les β2-mimétiques et alcalose métabolique favorisent l'hypokaliémie.
+ Le syndrome de refeeding peut hypokaliémiser brutalement.
+ Anticiper supplémentation en réalimentation du malnutri.
- L'acidose fait entrer le K+ dans les cellules.
- L'insuline augmente le potassium plasmatique.
- Le refeeding augmente le K+.
- L'alcalose n'affecte pas le potassium.

hko-tx|Traitement hypokaliémie|supplémentation en potassium|KCl oral privilégié ; perfusion IV surveillée si sévère.|3|potassium,traitement
V|Femme sous furosémide, K+ 2,6 mmol/L, crampes, sans troubles de conduction à l'ECG.
+ Le chlorure de potassium oral est souvent suffisant si voie digestive OK.
+ Perfusions IV à débit limité (souvent ≤ 10-20 mmol/h) avec monitoring cardiaque si IV central.
+ Corriger magnésium concomitant (déficit en Mg entrave correction K+).
+ Arrêter ou réduire diurétique/laxatif causal si possible.
- Le KCl IV en bolus rapide est recommandé systématiquement.
- Le magnésium n'influence pas le potassium.
- L'oral est contre-indiqué si K+ < 3,5 mmol/L.
- Les diurétiques doivent être poursuivis sans supplément.

hko-mg|Magnésium|hypomagnésémie associée|Hypokaliémie réfractaire tant que Mg bas.|3|potassium,magnésium
+ L'hypomagnésémie entraîne pertes rénales de potassium persistantes.
+ Supplémenter Mg2+ (sulfate de magnésium) en hypokaliémie réfractaire.
+ Fréquent chez alcooliques et sous diurétiques.
+ Surveillance rénale et réflexes en perfusion Mg IV.
- Le magnésium n'a aucun rôle dans l'hypokaliémie.
- Corriger le K+ suffit toujours sans Mg.
- L'hypomagnésémie est impossible sous diurétiques.
- Le Mg oral est toujours inefficace.

hko-acid|Alcalose et hypokaliémie|alcalose métabolique|Vomissements entretiennent alcalose et pertes de K+.|3|potassium,alcalose
+ Les vomissements causent pertes de HCl et hypokaliémie.
+ L'alcalose favorise shift du K+ intracellulaire.
+ Traitement : antiémétiques, NaCl, KCl, corriger cause.
+ Chlorurie basse en alcalose post-vomissements.
- Les vomissements provoquent une acidose.
- L'alcalose augmente le potassium plasmatique.
- Le NaCl est inutile en hypokaliémie des vomissements.
- La chlorurie est toujours > 40 mmol/L.

hko-dig|Digoxine et hypokaliémie|digoxine|Hypokaliémie majore toxicité digitale.|3|potassium,digoxine
+ Même hypokaliémie modérée peut déclencher arythmies sous digoxine.
+ Corriger K+ avant et pendant traitement digitalique.
+ Hyperkaliémie peut survenir en intoxication digitique sévère (paradoxe).
+ ECG surveillé si association.
- La digoxine protège des arythmies en hypokaliémie.
- Le potassium n'influence pas la digoxine.
- L'intoxication digitique donne toujours hypokaliémie.
- Aucune surveillance n'est requise.

hko-periodic|Hypokaliémie périodique|paralysie hypokaliémique périodique|Canalopathies ; crises de faiblesse musculaire.|4|potassium,génétique
+ Crises de paralysie avec hypokaliémie, souvent déclenchées par repas glucidiques ou effort.
+ Mutation canaux ioniques (souvent calcium) — bilan génétique spécialisé.
+ Traitement aigu : potassium oral ; prévention : acetazolamide parfois.
+ Distinguer d'hyperthyroïdie associée (forme thyrotoxique).
- La paralysie périodique survient toujours avec hyperkaliémie.
- Aucune composante génétique n'existe.
- L'acetazolamide aggrave toujours les crises.
- Le repas glucidique corrige le potassium.

hko-redist|Redistribution post-traitement|hypokaliémie après correction acidose|Après insuline en CAD, K+ peut chuter fortement.|3|potassium,CAD
+ Avant insuline en CAD, le K+ peut être normal ou élevé malgré déficit total.
+ L'insuline corrige l'acidose et fait chuter le K+ plasmatique.
+ Supplémenter potassium dans perfusions selon kaliémie et diurèse.
+ Surveillance horaire en phase initiale de traitement.
- Le K+ augmente toujours après insuline en CAD.
- Aucun déficit total de potassium en CAD.
- L'insuline n'affecte pas le potassium.
- La supplémentation K+ est interdite en CAD.

hko-chronic|Hypokaliémie chronique|conséquences chroniques|Néphropathie hypokaliémique, diabète, HTA.|2|potassium,chronique
+ L'hypokaliémie chronique peut entraîner néphropathie tubulo-interstitielle.
+ Risque d'hyperglycémie et intolérance glucidique.
+ Peut contribuer à hypertension résistante.
+ Correction prolongée et traitement étiologique.
- L'hypokaliémie chronique protège les reins.
- Aucun effet métabolique n'existe.
- La pression artérielle baisse toujours en hypokaliémie.
- La néphropathie hypokaliémique est réversible instantanément.
"""

HYPNATREMIE_BLOCK = r"""
hna-def|Définition hyponatrémie|définition de l'hyponatrémie|Na+ < 135 mmol/L ; distinguer hypo-osmolaire.|1|sodium,définition
+ L'hyponatrémie est fréquente à l'hôpital, surtout chez le sujet âgé.
+ Distinguer hypo-osmolaire vraie, hyperosmolaire (hyperglycémie) et pseudo-hyponatrémie.
+ Les symptômes neurologiques dépendent de la rapidité et de la sévérité.
+ L'hyponatrémie sévère (< 120) peut être fatale sans prise en charge adaptée.
- L'hyponatrémie est toujours hyperosmolaire.
- Le sodium ne dépend pas de l'eau corporelle totale.
- Elle est toujours asymptomatique.
- Na+ 134 mmol/L est toujours pathologique majeur.

hna-osm|Osmolarité et classification|osmolarité plasmatique|Hypo-osmolaire vraie vs hyperglycémie vs hyperlipidémie.|2|sodium,osmolarité
+ En hyperglycémie, corriger le sodium ou calculer osmolarité effective.
+ La pseudo-hyponatrémie (hyperlipidémie, hyperprotéinémie) donne Na+ bas avec osmolarité normale.
+ L'osmolarité urinaire aide à distinguer SIADH vs hypovolémie.
+ Mesurer osmolarité plasmatique en toute hyponatrémie persistante.
- L'osmolarité plasmatique est inutile en hyponatrémie.
- L'hyperglycémie abaisse l'osmolarité.
- La pseudo-hyponatrémie est une urgence dialytique systématique.
- L'osmolarité urinaire est toujours < 100 en toute hyponatrémie.

hna-vole|Hyponatrémie hypovolémique|hypovolémie et hyponatrémie|Pertes de Na+ et eau, remplissage NaCl, correction eau libre.|2|sodium,hypovolémie
+ Les pertes digestives, diurétiques, insuffisance surrénale peuvent hypovolémiser et hyponatrémiser.
+ Signes de déshydratation : hypotension, tachycardie, soif.
+ Traitement : NaCl isotonique puis eau libre selon évolution.
+ L'osmolarité urinaire peut être > 100 malgré hypovolémie (ADH).
- L'hypovolémie provoque toujours hypernatrémie.
- Le NaCl 0,9% aggrave l'hyponatrémie hypovolémique.
- L'ADH est toujours supprimée en hypovolémie.
- Aucun signe clinique n'existe.

hna-euvol|SIADH|syndrome de sécrétion inappropriée d'ADH|Euvolémie, osmolarité urinaire inappropriément élevée.|3|sodium,SIADH
+ SIADH : hyponatrémie hypo-osmolaire, euvolémie clinique, urine concentrée.
+ Causes : pneumopathies, SNC, médicaments (ISRS, carbamazépine).
+ Traitement : restriction hydrique, sel oral, tolvaptan (antagoniste V2) selon contexte.
+ Corriger lentement pour éviter myélinolyse centropontine.
- Le SIADH associe une hypervolémie clinique majeure.
- L'urine est toujours diluée en SIADH.
- La restriction hydrique est inutile.
- Le tolvaptan augmente l'ADH.

hna-hyper|Hyponatrémie hypervolémique|hypervolémie|Insuffisance cardiaque, cirrhose, néphrose.|3|sodium,hypervolémie
+ L'activation neurohumorale retient eau et sodium malgré hypervolémie effective.
+ Hyponatrémie est marqueur de mauvais pronostic en insuffisance cardiaque.
+ Traitement : restriction sodée et hydrique, diurétiques, tolvaptan parfois.
+ Distinguer d'une hypovolémie masquée.
- L'hypervolémie provoque hypernatrémie.
- Les diurétiques sont contre-indiqués.
- L'hyponatrémie est bon signe prognostique en IC.
- L'ADH est absente en hypervolémie.

hna-tx|Vitesse de correction|correction de l'hyponatrémie|Max 8-10 mmol/L/24 h (chronique) ; 4-6 mmol/L/24 h si risque OCP.|3|sodium,traitement,OCP
V|Femme alcoolique, Na+ 108 mmol/L, confusion, installation sur plusieurs jours.
+ Correction trop rapide risque myélinolyse centropontine (OCP).
+ Objectif : hausse limitée du Na+ sur 24 h selon guidelines.
+ Utiliser NaCl hypertonique prudent en symptomatique sévère avec surveillance.
+ Contrôles du Na+ toutes les 2-4 h en correction active.
- Corriger 20 mmol/L en 12 h est recommandé en hyponatrémie chronique.
- L'OCP survient si correction lente.
- Le NaCl 3% est toujours contre-indiqué.
- Aucun monitoring n'est nécessaire.

hna-acute|Hyponatrémie aiguë|formes aiguës post-op ou hydro|Peut tolérer correction un peu plus rapide si < 48 h.|3|sodium,aigu
+ Installation en moins de 48 h : risque neurologique aigu par œdème cérébral.
+ Peut nécessiter correction plus rapide si convulsions (NaCl 3% bolus).
+ Distinguer chronique vs aigu guide la vitesse de correction.
+ Bilan étiologique après stabilisation.
- L'aigu et le chronique se traitent identiquement sans limite.
- L'œdème cérébral n'existe qu'en hypernatrémie.
- Les convulsions n'imposent pas de correction.
- L'hyponatrémie aiguë est toujours asymptomatique.

hna-beer|Bière potoman|polydipsie et bière potoman|Apports d'eau hypotoniques excessifs, apports protéiques faibles.|2|sodium,bière,polydipsie
+ Le syndrome de la bière potoman : très faible apport soluté avec excès d'eau.
+ Urine très diluée, osmolarité urinaire basse après arrêt des apports.
+ Traitement : restriction hydrique stricte, apports salés progressifs.
+ Distinguer de la polydipsie psychiatrique.
- La bière potoman provoque hypernatrémie.
- L'urine est concentrée typiquement.
- Aucune restriction hydrique n'est nécessaire.
- Le syndrome n'existe pas.

hna-thiaz|Hyponatrémie aux thiazidiques|diurétiques thiazidiques|Hyponatrémie hypovolémique ou euvolémique fréquente chez âgé.|2|sodium,thiazide
+ Les thiazidiques diminuent capacité rénale à diluer l'urine.
+ Hyponatrémie souvent dans les premières semaines de traitement.
+ Arrêt du diurétique et NaCl si hypovolémie.
+ Surveillance Na+ à l'initiation chez sujet âgé.
- Les thiazidiques provoquent hypernatrémie.
- L'hyponatrémie survient uniquement après des années.
- L'arrêt du thiazide est inutile.
- Les thiazidiques augmentent la dilution urinaire maximale.

hna-adrenal|Insuffisance surrénalienne|insuffisance surrénalienne|Déficit en aldostérone et cortisol ; hyponatrémie hypovolémique.|3|sodium,surrénale
+ L'insuffisance surrénalienne primaire perd sel et eau (hyperkaliémie associée).
+ La forme secondaire peut hyponatrémiser sans hyperkaliémie classique.
+ Traitement : hydrocortisone et fludrocortisone si primaire.
+ Urgence surrénalienne si choc et hyponatrémie sévère.
- L'insuffisance surrénalienne donne hypernatrémie.
- L'hyperkaliémie est absente en forme primaire.
- Les corticoïdes aggravent l'hyponatrémie.
- Aucun traitement hormonal n'est requis.

hna-pseudo|Pseudo-hyponatrémie|pseudo-hyponatrémie|Hypertriglycéridémie ou paraprotéinémie faussent Na+ par méthode indirecte.|2|sodium,labo
+ Sodium par méthode indirecte artificiellement bas si phase lipémique/protéique.
+ Osmolarité plasmatique mesurée normale ou basse selon cas.
+ Dosage direct ou correction selon protocole labo.
+ Ne pas surcorriger une fausse hyponatrémie.
- La pseudo-hyponatrémie a une osmolarité très élevée toujours.
- Elle nécessite dialyse d'urgence.
- Le triglycéride n'influence pas le sodium.
- Toute hyponatrémie au labo est vraie.

hna-chronic|Hyponatrémie chronique|conséquences chroniques|Chutes, fractures, cognition ; corriger prudemment.|2|sodium,chronique
+ L'hyponatrémie chronique modérée associe risque de chutes et fractures.
+ Peut affecter attention et marche chez le sujet âgé.
+ Correction partielle parfois suffisante pour symptômes.
+ Éviter surcorrection avec rebond hypernatrémique.
- L'hyponatrémie chronique est toujours bénigne.
- Aucun risque osseux n'existe.
- La correction rapide est sans danger si chronique.
- Les symptômes neurologiques n'existent qu'en aigu.
"""

HYPOPHOSPHATEMIE_BLOCK = r"""
hph-def|Définition hypophosphatémie|définition de l'hypophosphatémie|Phosphate < 0,8 mmol/L ; sévère si < 0,3.|1|phosphate,définition
+ L'hypophosphatémie sévère peut entraîner faiblesse musculaire et défaillance respiratoire.
+ Le phosphate est essentiel au métabolisme énergétique (ATP).
+ Fréquente en réanimation et dénutrition.
+ Dosage du phosphate plasmatique à interpréter selon contexte clinique.
- L'hypophosphatémie est toujours asymptomatique.
- Le phosphate n'intervient pas dans l'ATP.
- Phosphate à 0,5 mmol/L est toujours normal.
- Aucune forme sévère n'existe.

hph-refeed|Syndrome de refeeding|refeeding et phosphate|Chute du phosphate après réalimentation du malnutri.|3|phosphate,refeeding,urgence
V|Homme anorexique, IMC 14, réalimentation entérale débutée : phosphate 0,4 mmol/L J2, faiblesse généralisée.
+ La réintroduction nutritionnelle augmente besoins en phosphate intracellulaire.
+ Hypophosphatémie, hypokaliémie, hypomagnésémie possibles (syndrome de refeeding).
+ Prévention : réalimentation progressive, supplémentation phosphore/électrolytes.
+ Surveillance biologique rapprochée les premiers jours.
- Le refeeding augmente toujours le phosphate plasmatique.
- Aucune supplémentation n'est nécessaire.
- Le syndrome de refeeding ne touche pas le phosphate.
- La réalimentation doit être maximale dès J1.

hph-resp|Défaillance respiratoire|hypophosphatémie et muscle|Paralysie diaphragmatique possible si phosphate très bas.|3|phosphate,respi,urgence
+ L'hypophosphatémie sévère peut paralyser le muscle strié dont diaphragme.
+ Surveillance de la capnie et de la force musculaire.
+ Supplémentation IV ou oral selon sévérité et tolérance digestive.
+ Associer correction Mg et K souvent nécessaire.
- Le phosphate n'affecte pas la fonction musculaire.
- La défaillance respiratoire est due uniquement à l'infection.
- L'oral est toujours suffisant si phosphate < 0,2 mmol/L.
- Aucun lien avec l'ATP existe.

hph-alcool|Alcoolisme|alcoolisme et phosphate|Malnutrition, vitamine D, redistribution.|2|phosphate,alcool
+ L'alcoolisme chronique associe carences multiples (phosphate, Mg, K).
+ L'acidose et sevrage peuvent modifier les shifts de phosphate.
+ Supplémentation vitaminique (thiamine avant glucose) et électrolytes.
+ Prévenir syndrome de refeeding au sevrage alcoolique hospitalisé.
- L'alcool augmente le phosphate plasmatique.
- La thiamine est inutile avant glucose.
- Le sevrage alcoolique n'affecte pas les électrolytes.
- L'alcoolisme protège du refeeding.

hph-diab|Acidocétose et phosphate|phosphate en CAD|Phosphate plasmatique peut être normal ou élevé initialement malgré déficit total.|3|phosphate,diabète,CAD
+ En CAD, le phosphate sort des cellules puis chute après insuline.
+ Supplémenter phosphate seulement si sévère et symptomatique (risque hypocalcémie).
+ L'insuline entraîne entrée intracellulaire du phosphate.
+ Surveiller phosphate, K, Mg pendant traitement CAD.
- Le phosphate est toujours bas dès l'admission en CAD.
- L'insuline augmente le phosphate durablement sans rebond.
- La supplémentation phosphate est systématique d'emblée.
- Aucun déficit total n'existe en CAD.

hph-renal|Pertes rénales|hyperparathyroïdie et phosphate urinaire|Hyperparathyroïdie augmente phosphaturie.|2|phosphate,PTH,rein
+ La PTH élevée diminue la réabsorption tubulaire de phosphate.
+ Certaines tubulopathies (Fanconi) entraînent phosphaturie et hypophosphatémie.
+ Ostéomalacie hypophosphatémique acquise (tumeurs productrices de FGF23).
+ Rechercher phosphaturie avec rapport phosphate/créatinine urinaire.
- La PTH augmente le phosphate plasmatique toujours.
- Le Fanconi augmente la réabsorption de phosphate.
- Le FGF23 n'existe pas cliniquement.
- La phosphaturie est sans intérêt diagnostique.

hph-tumor|Ostéomalacie oncogénique|tumeur à FGF23|Hypophosphatémie persistante, phosphaturie, vitamine D normale.|4|phosphate,FGF23,cancer
+ Les tumeurs mésenchymateuses peuvent sécréter FGF23 et hypophosphatémiser.
+ Recherche de tumeur (IRM, DOTATATE) si hypophosphatémie chronique inexpliquée.
+ Traitement : résection tumorale ou burosumab (anti-FGF23) selon cas.
+ Distinguer carence vitamine D simple.
- Le FGF23 augmente le phosphate plasmatique.
- Aucune tumeur n'est en cause de l'hypophosphatémie.
- La vitamine D est toujours très basse dans ce syndrome.
- La résection tumorale est inutile.

hph-tx|Traitement|supplémentation en phosphate|K-phosphate oral ou IV prudent ; risque hypocalcémie.|3|phosphate,traitement
+ Le phosphate oral (ex. glycero-phosphate) si forme légère et digestive OK.
+ Perfusions de phosphate IV à débit contrôlé avec surveillance Ca et CaPO4.
+ Corriger concomitamment magnésium et potassium.
+ Éviter précipitation avec calcium en perfusion même voie.
- Le phosphate IV peut être mélangé librement au calcium gluconate même poche.
- L'oral est contre-indiqué si phosphate > 0,8 mmol/L.
- Aucun risque d'hypocalcémie n'existe.
- Le magnésium est sans importance.

hph-shift|Redistribution intracellulaire|shift du phosphate|Insuline, alcalose, catecholamines après stress.|2|phosphate,shift
+ L'insuline et la réalimentation font entrer le phosphate dans les cellules.
+ Phase de stress initial peut libérer phosphate puis chute secondaire.
+ Anticiper en nutrition parentérale et post-opératoire.
+ Monitoring biologique post-chirurgie bariatrique et greffe.
- L'insuline augmente le phosphate plasmatique durablement.
- L'alcalose n'affecte pas le phosphate.
- Le stress augmente toujours le phosphate sans rebond.
- La chirurgie bariatrique n'affecte pas les électrolytes.

hph-bone|Rachitisme et ostéomalacie|os et phosphate bas|Rachitisme hypophosphatémique, traitement phosphate + calcitriol.|3|phosphate,os,pédiatrie
+ Les formes héréditaires (X-liée) entraînent fuite rénale de phosphate.
+ Traitement chronique par phosphate et calcitriol sous surveillance.
+ Retard de croissance et déformations osseuses chez l'enfant.
+ Suivi néphrologique et rhumatologique pédiatrique.
- L'hypophosphatémie n'affecte jamais l'os.
- Le calcitriol est contre-indiqué.
- Les formes héréditaires disparaissent à l'âge adulte.
- Aucun rachitisme n'est lié au phosphate.

hph-lab|Interprétation biologique|bilan phosphatémie|Dosage matin, relation avec magnésium et vitamine D.|2|phosphate,bilan
+ Interpréter avec calcémie, PTH, 25-OH vitamine D, magnésium.
+ Phosphaturie (TmP/GFR ou rapport P/Cr urinaire) si hypophosphatémie persistante.
+ Variations post-prandiales modérées possibles.
+ Éviter interprétation isolée sans clinique.
- Le phosphate ne varie jamais dans la journée.
- La PTH est inutile en hypophosphatémie.
- La vitamine D n'interagit pas avec le phosphate.
- Le rapport P/Cr urinaire est toujours normal en hypophosphatémie.

hph-icu|Réanimation|hypophosphatémie en soins critiques|Fréquente, aggrave pronostic si sévère.|3|phosphate,réa
+ Jusqu'à 80% des patients en réanimation peuvent être hypophosphatémiques à un moment.
+ Facteurs : nutrition, dialyse, sepsis, alcalose, transfusions.
+ Supplémentation guidée par seuils et symptômes.
+ Intégrer au bilan global des troubles hydro-électrolytiques.
- L'hypophosphatémie est impossible en réanimation.
- Elle améliore le pronostic.
- La dialyse augmente toujours le phosphate en réa.
- Aucune supplémentation n'est faite en unité de soins intensifs.
"""

COURSE_NOTIONS: dict[str, list[dict]] = {
    topic: _parse_course_block(topic, block)
    for topic, block in _all_course_blocks().items()
}


def main() -> None:
    rng = random.Random(SEED)
    seen: set[str] = set()
    id_seq = [0]
    all_q: list[dict] = []
    counts: dict[str, int] = {}

    for topic in _all_course_blocks().keys():
        qs = generate_course(rng, topic, COURSE_NOTIONS[topic], seen, id_seq)
        counts[topic] = len(qs)
        all_q.extend(qs)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as fh:
        json.dump(all_q, fh, ensure_ascii=False, indent=2)

    print(f"Total questions : {len(all_q)}")
    print(f"Fichier : {OUTPUT} ({OUTPUT.stat().st_size} octets)")
    for topic, n in counts.items():
        print(f"  - {topic}: {n}")


if __name__ == "__main__":
    main()

