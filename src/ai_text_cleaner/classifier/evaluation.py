"""Evaluations-Metriken für den Klassifikator.

Liefert AUC, F1, Precision, Recall, Confusion-Matrix, Falsch-Positiv-Rate auf
menschlichem Test-Set und Calibration-Bins. Bewusst ohne Matplotlib — die
Plot-Erzeugung kommt im Eval-Loop-Script (25d) als optionaler Render-Schritt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .._sklearn_imports import require_sklearn

AI_LABEL = "ai"
HUMAN_LABEL = "human"


@dataclass
class EvaluationReport:
    auc: float
    f1: float
    precision: float
    recall: float
    accuracy: float
    confusion_matrix: dict[str, int] = field(default_factory=dict)
    false_positive_rate_human: float = 0.0
    calibration_bins: list[dict[str, float]] = field(default_factory=list)
    threshold: float = 0.5
    n_samples: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "auc": round(self.auc, 4),
            "f1": round(self.f1, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "accuracy": round(self.accuracy, 4),
            "confusion_matrix": self.confusion_matrix,
            "false_positive_rate_human": round(self.false_positive_rate_human, 4),
            "calibration_bins": self.calibration_bins,
            "threshold": self.threshold,
            "n_samples": self.n_samples,
        }


def _confusion_matrix(y_true: list[int], y_pred: list[int]) -> dict[str, int]:
    tp = tn = fp = fn = 0
    for t, p in zip(y_true, y_pred, strict=False):
        if t == 1 and p == 1:
            tp += 1
        elif t == 0 and p == 0:
            tn += 1
        elif t == 0 and p == 1:
            fp += 1
        else:
            fn += 1
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def _calibration_bins(
    y_true: list[int], y_score: list[float], n_bins: int = 10
) -> list[dict[str, float]]:
    bins: list[dict[str, float]] = []
    for i in range(n_bins):
        lo = i / n_bins
        hi = (i + 1) / n_bins
        members = [
            (t, s) for t, s in zip(y_true, y_score, strict=False) if lo <= s < hi or (hi == 1.0 and s == 1.0)
        ]
        if not members:
            bins.append({"bin_lo": lo, "bin_hi": hi, "count": 0, "mean_score": 0.0, "frac_positive": 0.0})
            continue
        mean_score = sum(s for _, s in members) / len(members)
        frac_positive = sum(t for t, _ in members) / len(members)
        bins.append(
            {
                "bin_lo": lo,
                "bin_hi": hi,
                "count": len(members),
                "mean_score": round(mean_score, 4),
                "frac_positive": round(frac_positive, 4),
            }
        )
    return bins


def evaluate(
    y_true: list[int],
    y_score: list[float],
    threshold: float = 0.5,
) -> EvaluationReport:
    """Berechne alle Metriken. `y_true=1` heißt 'AI', `y_true=0` heißt 'human'."""
    require_sklearn()
    from sklearn.metrics import (  # type: ignore[import-not-found]
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    y_pred = [1 if s >= threshold else 0 for s in y_score]
    cm = _confusion_matrix(y_true, y_pred)

    auc = float(roc_auc_score(y_true, y_score)) if len(set(y_true)) > 1 else 0.0
    f1 = float(f1_score(y_true, y_pred, zero_division=0))  # type: ignore[arg-type]
    precision = float(precision_score(y_true, y_pred, zero_division=0))  # type: ignore[arg-type]
    recall = float(recall_score(y_true, y_pred, zero_division=0))  # type: ignore[arg-type]
    accuracy = float(accuracy_score(y_true, y_pred))

    n_human = cm["tn"] + cm["fp"]
    fpr_human = cm["fp"] / n_human if n_human > 0 else 0.0

    return EvaluationReport(
        auc=auc,
        f1=f1,
        precision=precision,
        recall=recall,
        accuracy=accuracy,
        confusion_matrix=cm,
        false_positive_rate_human=fpr_human,
        calibration_bins=_calibration_bins(y_true, y_score),
        threshold=threshold,
        n_samples=len(y_true),
    )


def report_markdown(report: EvaluationReport) -> str:
    cm = report.confusion_matrix
    return f"""# Evaluation Report

| Metrik | Wert |
|---|---|
| AUC | {report.auc:.4f} |
| F1 | {report.f1:.4f} |
| Precision | {report.precision:.4f} |
| Recall | {report.recall:.4f} |
| Accuracy | {report.accuracy:.4f} |
| Falsch-Positiv-Rate (Human) | {report.false_positive_rate_human:.4f} |
| Threshold | {report.threshold} |
| n_samples | {report.n_samples} |

## Confusion Matrix

|  | Pred Human | Pred AI |
|---|---|---|
| **True Human** | {cm.get("tn", 0)} | {cm.get("fp", 0)} |
| **True AI** | {cm.get("fn", 0)} | {cm.get("tp", 0)} |
"""


__all__ = ["EvaluationReport", "evaluate", "report_markdown"]
