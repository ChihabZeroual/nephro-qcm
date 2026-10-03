"""Clean extracted PDF text and extract fact-like sentences for QCM generation."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "extracted"
OUT = ROOT / "data" / "facts"


def clean_text(raw: str) -> str:
    t = raw.replace("fr-FR", " ")
    t = re.sub(r"(?<=[a-zàâäéèêëïîôùûüç])(?=[A-ZÀÂÄÉÈÊËÏÎÔÙÛÜÇ])", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?;])\s+", text)
    out: list[str] = []
    for p in parts:
        p = p.strip()
        if len(p) < 35 or len(p) > 320:
            continue
        if p.count(" ") < 4:
            continue
        if re.search(r"^[IVXLC]+\s*-", p):
            continue
        out.append(p)
    return out


def topic_from_filename(name: str) -> str:
    base = name.replace(".txt", "").replace("_", " ")
    return base


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    catalog: dict[str, object] = {}
    for path in sorted(EXTRACTED.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        cleaned = clean_text(raw)
        sentences = split_sentences(cleaned)
        topic = topic_from_filename(path.name)
        slug = path.stem
        payload = {
            "topic": topic,
            "chapter": "Troubles hydro-électrolytiques et équilibre acido-basique",
            "sourceFile": slug.replace("_", " ") + ".pdf",
            "sentences": sentences[:400],
            "charCount": len(cleaned),
        }
        (OUT / f"{slug}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        catalog[slug] = {
            "topic": topic,
            "facts": len(sentences),
            "chars": len(cleaned),
        }
        print(slug, "sentences", len(sentences), "chars", len(cleaned))

    (OUT / "_catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
