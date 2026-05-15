"""Tests für classifier/persistence.py — save/load Roundtrip."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_text_cleaner.classifier.persistence import load_model, save_model
from ai_text_cleaner.classifier.predict import predict
from ai_text_cleaner.classifier.train import train_classifier


def test_save_load_roundtrip(synthetic_csvs: tuple[Path, Path], tmp_path: Path) -> None:
    human, ai = synthetic_csvs
    report = train_classifier(human, ai, model_type="logreg")

    model_path = tmp_path / "model.pkl"
    save_model(report.bundle, model_path)
    assert model_path.exists()
    assert model_path.with_suffix(".metadata.json").exists()

    loaded = load_model(model_path)
    assert loaded.model_type == "logreg"
    assert loaded.feature_names == report.bundle.feature_names


def test_load_missing_model_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Kein Modell"):
        load_model(tmp_path / "does-not-exist.pkl")


def test_predict_after_save_load_is_identical(
    synthetic_csvs: tuple[Path, Path], tmp_path: Path
) -> None:
    human, ai = synthetic_csvs
    report = train_classifier(human, ai, model_type="logreg")
    model_path = tmp_path / "m.pkl"
    save_model(report.bundle, model_path)

    text = "Ein konsistenter Test-Text — mit Gedankenstrich."
    before = predict(text, bundle=report.bundle, use_pos=False).score
    after = predict(text, bundle=load_model(model_path), use_pos=False).score
    assert abs(before - after) < 1e-6


def test_metadata_includes_corpus_size(
    synthetic_csvs: tuple[Path, Path], tmp_path: Path
) -> None:
    human, ai = synthetic_csvs
    report = train_classifier(human, ai, model_type="logreg")
    model_path = tmp_path / "m.pkl"
    save_model(report.bundle, model_path)

    loaded = load_model(model_path)
    assert loaded.metadata["corpus_size"]["human"] == 100
    assert loaded.metadata["corpus_size"]["ai"] == 100
