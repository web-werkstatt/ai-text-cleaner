"""Tests für classifier/predict.py."""

from __future__ import annotations

from pathlib import Path

from ai_text_cleaner.classifier.predict import predict
from ai_text_cleaner.classifier.train import train_classifier


def test_predict_returns_score_in_unit_interval(synthetic_csvs: tuple[Path, Path]) -> None:
    human, ai = synthetic_csvs
    report = train_classifier(human, ai, model_type="logreg")
    result = predict("Ein deutscher Beispieltext. Mit zwei Sätzen.", bundle=report.bundle, use_pos=False)
    assert 0.0 <= result.score <= 1.0


def test_top_features_capped_at_ten(synthetic_csvs: tuple[Path, Path]) -> None:
    human, ai = synthetic_csvs
    report = train_classifier(human, ai, model_type="logreg")
    result = predict("Test.", bundle=report.bundle, use_pos=False)
    assert len(result.top_features) <= 10
    assert all(isinstance(name, str) for name, _ in result.top_features)


def test_confidence_categories(synthetic_csvs: tuple[Path, Path]) -> None:
    human, ai = synthetic_csvs
    report = train_classifier(human, ai, model_type="logreg")
    extreme_ai = "Text — mit — vielen — Em-Dashes — überall — drin — wirklich — viele — davon — siehe — selbst."
    extreme = predict(extreme_ai, bundle=report.bundle, use_pos=False)
    assert extreme.confidence in {"low", "medium", "high"}


def test_gbm_predict_uses_global_importances(synthetic_csvs: tuple[Path, Path]) -> None:
    human, ai = synthetic_csvs
    report = train_classifier(human, ai, model_type="gbm")
    result = predict("Beispiel.", bundle=report.bundle, use_pos=False)
    assert len(result.top_features) <= 10
    assert all(v >= 0 for _, v in result.top_features)
