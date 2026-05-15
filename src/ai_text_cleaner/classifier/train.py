"""Training-Pipeline: Feature-CSVs → ClassifierBundle.

Strategie:
- Stratified Split 70/15/15 (train/val/test)
- LogReg (Default, interpretierbar) oder GradientBoosting
- GridSearchCV auf Val-Set
- Test-Set wird einmal evaluiert, nicht zum Tuning genutzt
"""

from __future__ import annotations

import csv
import datetime as _dt
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .._sklearn_imports import require_sklearn
from ..features.schema import FEATURE_NAMES
from .evaluation import EvaluationReport, evaluate
from .persistence import ClassifierBundle

ModelType = Literal["logreg", "gbm"]


@dataclass
class TrainingReport:
    bundle: ClassifierBundle
    val_metrics: EvaluationReport
    test_metrics: EvaluationReport
    train_size: int
    val_size: int
    test_size: int


def _load_csv(path: Path, expected_label: str) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if row.get("label") != expected_label:
                continue
            rows.append({name: float(row.get(name, 0.0) or 0.0) for name in FEATURE_NAMES})
    return rows


def _build_estimator(model_type: ModelType):
    require_sklearn()
    if model_type == "logreg":
        from sklearn.linear_model import LogisticRegression  # type: ignore[import-not-found]
        return LogisticRegression(max_iter=2000, solver="lbfgs"), {
            "C": [0.1, 1.0, 10.0],
        }
    from sklearn.ensemble import GradientBoostingClassifier  # type: ignore[import-not-found]
    return GradientBoostingClassifier(random_state=42), {
        "n_estimators": [50, 100, 200],
        "max_depth": [2, 3, 4],
    }


def train_classifier(
    human_csv: Path,
    ai_csv: Path,
    *,
    model_type: ModelType = "logreg",
    random_state: int = 42,
) -> TrainingReport:
    require_sklearn()
    from sklearn.model_selection import GridSearchCV, train_test_split  # type: ignore[import-not-found]
    from sklearn.preprocessing import StandardScaler  # type: ignore[import-not-found]

    human_rows = _load_csv(human_csv, "human")
    ai_rows = _load_csv(ai_csv, "ai")

    if not human_rows or not ai_rows:
        raise ValueError(
            f"Leere Korpus-CSVs: human={len(human_rows)}, ai={len(ai_rows)}. "
            "Erst Sprint 25a mit echtem Korpus durchziehen."
        )

    X: list[list[float]] = []
    y: list[int] = []
    for row in human_rows:
        X.append([row[name] for name in FEATURE_NAMES])
        y.append(0)
    for row in ai_rows:
        X.append([row[name] for name in FEATURE_NAMES])
        y.append(1)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=random_state
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=random_state
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    base_estimator, param_grid = _build_estimator(model_type)
    grid = GridSearchCV(
        base_estimator,
        param_grid=param_grid,
        scoring="roc_auc",
        cv=3,
        n_jobs=-1,
    )
    grid.fit(X_train_s, y_train)
    best = grid.best_estimator_

    val_score = best.predict_proba(X_val_s)[:, 1].tolist()
    test_score = best.predict_proba(X_test_s)[:, 1].tolist()

    val_metrics = evaluate(list(y_val), val_score)
    test_metrics = evaluate(list(y_test), test_score)

    bundle = ClassifierBundle(
        estimator=best,
        scaler=scaler,
        feature_names=list(FEATURE_NAMES),
        model_type=model_type,
        metadata={
            "trained_at": _dt.datetime.now(_dt.UTC).isoformat(),
            "corpus_size": {"human": len(human_rows), "ai": len(ai_rows)},
            "best_params": grid.best_params_,
            "val_metrics": val_metrics.to_dict(),
            "test_metrics": test_metrics.to_dict(),
        },
    )

    return TrainingReport(
        bundle=bundle,
        val_metrics=val_metrics,
        test_metrics=test_metrics,
        train_size=len(X_train),
        val_size=len(X_val),
        test_size=len(X_test),
    )


__all__ = ["ModelType", "TrainingReport", "train_classifier"]
