#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build app/data/questions.json from curated course-only QCM (scripts/curated_banks.py)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "data" / "questions.json"
DEMS_DIR = ROOT / "data" / "dems_qcm"

ORDER = [
    "Acidose métabolique",
    "Alcalose métabolique",
    "Hypercalcémie",
    "Hyperkaliémie",
    "Hypernatrémie",
    "Hyperphosphatémie",
    "Hypocalcémie",
    "Hypokaliémie",
    "Hyponatrémie",
    "Hypophosphatémie",
]


def main() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from curated_banks import CURATED_BY_TOPIC, all_curated  # noqa: WPS433

    DEMS_DIR.mkdir(parents=True, exist_ok=True)
    merged: list[dict] = []
    counts: dict[str, int] = {}

    for topic in ORDER:
        if topic in CURATED_BY_TOPIC:
            qs = CURATED_BY_TOPIC[topic]()
        else:
            qs = []
        fname = f"{topic}.json"
        (DEMS_DIR / fname).write_text(
            json.dumps(qs, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        counts[topic] = len(qs)
        merged.extend(qs)

    OUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Per course:")
    for topic, n in counts.items():
        print(f"  {topic}: {n}")
    print(f"Total: {len(merged)}")
    print(f"Written: {OUT}")
    if len(merged) < 120:
        print(
            "\nNote: 7 PDFs are image-only — see data/COURSES_PDF_LIMITATION.md",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
