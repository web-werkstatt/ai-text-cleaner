"""End-to-End-Test für scripts/extract_features.py mit tmp-Fixtures."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def tmp_corpus(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "doc1.txt").write_text(
        "Das ist ein erster Satz. Und das ist ein zweiter Satz.\n\n"
        "Zweiter Absatz mit Gedankenstrich — und Pointe.",
        encoding="utf-8",
    )
    (raw / "doc2.txt").write_text(
        "Nur ein kurzer Text.",
        encoding="utf-8",
    )
    return raw


def _run_script(input_dir: Path, output: Path, label: str) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "extract_features.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--input",
            str(input_dir),
            "--output",
            str(output),
            "--label",
            label,
            "--workers",
            "1",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_creates_csv_with_correct_header(tmp_corpus: Path, tmp_path: Path) -> None:
    output = tmp_path / "features.csv"
    result = _run_script(tmp_corpus, output, "human")
    assert result.returncode == 0, f"stderr={result.stderr}\nstdout={result.stdout}"
    assert output.exists()

    with output.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert len(rows) == 2
    assert all(r["label"] == "human" for r in rows)
    assert all("source_id" in r and r["source_id"] for r in rows)
    assert all("mean_sentence_length" in r for r in rows)


def test_idempotent_skip(tmp_corpus: Path, tmp_path: Path) -> None:
    output = tmp_path / "features.csv"
    first = _run_script(tmp_corpus, output, "human")
    assert first.returncode == 0

    second = _run_script(tmp_corpus, output, "human")
    assert second.returncode == 0
    assert "Nichts zu tun" in second.stdout

    with output.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
