"""Tests für classifier/evaluation.py — Metriken-Berechnung auf bekannten Vorhersagen."""

from __future__ import annotations

from ai_text_cleaner.classifier.evaluation import evaluate, report_markdown


def test_perfect_predictions() -> None:
    y_true = [0, 0, 0, 1, 1, 1]
    y_score = [0.05, 0.10, 0.20, 0.80, 0.90, 0.95]
    report = evaluate(y_true, y_score)
    assert report.auc == 1.0
    assert report.f1 == 1.0
    assert report.precision == 1.0
    assert report.recall == 1.0
    assert report.confusion_matrix == {"tp": 3, "tn": 3, "fp": 0, "fn": 0}
    assert report.false_positive_rate_human == 0.0


def test_worst_predictions() -> None:
    y_true = [0, 0, 1, 1]
    y_score = [0.9, 0.9, 0.1, 0.1]
    report = evaluate(y_true, y_score)
    assert report.auc == 0.0
    assert report.confusion_matrix == {"tp": 0, "tn": 0, "fp": 2, "fn": 2}
    assert report.false_positive_rate_human == 1.0


def test_threshold_affects_predictions() -> None:
    y_true = [0, 0, 1, 1]
    y_score = [0.3, 0.6, 0.4, 0.7]
    low = evaluate(y_true, y_score, threshold=0.35)
    high = evaluate(y_true, y_score, threshold=0.65)
    assert low.confusion_matrix["fp"] >= high.confusion_matrix["fp"]


def test_calibration_bins_sum_to_n() -> None:
    y_true = [0, 1, 0, 1, 0, 1]
    y_score = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]
    report = evaluate(y_true, y_score)
    total = sum(bin_["count"] for bin_ in report.calibration_bins)
    assert total == len(y_true)


def test_report_markdown_contains_key_metrics() -> None:
    report = evaluate([0, 1, 0, 1], [0.2, 0.8, 0.3, 0.7])
    md = report_markdown(report)
    assert "AUC" in md
    assert "Confusion Matrix" in md
    assert "Falsch-Positiv-Rate" in md
