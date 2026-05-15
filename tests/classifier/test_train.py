"""Sanity-Tests für classifier/train.py auf synthetischen, linear trennbaren Daten."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_text_cleaner.classifier.train import train_classifier


def test_logreg_trains_and_separates(synthetic_csvs: tuple[Path, Path]) -> None:
    human, ai = synthetic_csvs
    report = train_classifier(human, ai, model_type="logreg")
    assert report.val_metrics.auc > 0.8
    assert report.test_metrics.auc > 0.8
    assert report.bundle.model_type == "logreg"
    assert len(report.bundle.feature_names) >= 20


def test_gbm_trains_and_separates(synthetic_csvs: tuple[Path, Path]) -> None:
    human, ai = synthetic_csvs
    report = train_classifier(human, ai, model_type="gbm")
    assert report.val_metrics.auc > 0.8
    assert report.test_metrics.auc > 0.8
    assert report.bundle.model_type == "gbm"


def test_empty_csv_raises(tmp_path: Path) -> None:
    empty_human = tmp_path / "h.csv"
    empty_ai = tmp_path / "a.csv"
    empty_human.write_text("source_id,label\n", encoding="utf-8")
    empty_ai.write_text("source_id,label\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Leere Korpus-CSVs"):
        train_classifier(empty_human, empty_ai)


def test_training_metadata_set(synthetic_csvs: tuple[Path, Path]) -> None:
    human, ai = synthetic_csvs
    report = train_classifier(human, ai, model_type="logreg")
    meta = report.bundle.metadata
    assert "trained_at" in meta
    assert meta["corpus_size"]["human"] == 100
    assert meta["corpus_size"]["ai"] == 100
    assert "best_params" in meta
