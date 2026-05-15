"""Gemeinsame Fixtures für classifier-Tests."""

from __future__ import annotations

import csv
import random
from pathlib import Path

import pytest

from ai_text_cleaner.features.schema import FEATURE_NAMES

pytest.importorskip("sklearn")


def _row(label: str, source_id: str, values: dict[str, float]) -> dict:
    row: dict = {"source_id": source_id, "label": label, "pos_available": 1}
    for name in FEATURE_NAMES:
        row[name] = float(values.get(name, 0.0))
    return row


@pytest.fixture
def synthetic_csvs(tmp_path: Path) -> tuple[Path, Path]:
    """Erzeugt zwei CSVs mit linear trennbaren Klassen (für Sanity-Tests).

    Human-Klasse: niedrige Em-Dash-Rate, hohe Wort-Varianz.
    AI-Klasse:    hohe Em-Dash-Rate, niedrige Wort-Varianz.
    """
    rng = random.Random(42)
    human_csv = tmp_path / "human.csv"
    ai_csv = tmp_path / "ai.csv"
    header = ["source_id", "label", "pos_available", *FEATURE_NAMES]

    def write(path: Path, label: str, em_dash_mean: float, variance_mean: float, n: int) -> None:
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=header)
            writer.writeheader()
            for i in range(n):
                em_dash = max(0.0, rng.gauss(em_dash_mean, 1.0))
                variance = max(0.0, rng.gauss(variance_mean, 0.05))
                writer.writerow(
                    _row(
                        label,
                        f"{label}-{i:04d}",
                        {
                            "em_dash_per_1000_words": em_dash,
                            "variance_ratio": variance,
                            "mean_sentence_length": rng.uniform(10, 25),
                            "type_token_ratio": rng.uniform(0.3, 0.7),
                        },
                    )
                )

    write(human_csv, "human", em_dash_mean=0.5, variance_mean=0.6, n=100)
    write(ai_csv, "ai", em_dash_mean=8.0, variance_mean=0.2, n=100)
    return human_csv, ai_csv
