"""Tier-3-Klassifikator (Sprint 25b).

Public-API:
- `predict(text)` → Prediction(score, top_features, confidence)
- `train_classifier(human_csv, ai_csv)` → TrainingReport
- `load_classifier()` → ClassifierBundle
- `save_classifier(bundle, path)` → None
- `Prediction`, `ClassifierBundle`, `TrainingReport`, `EvaluationReport`

Ohne `pip install .[ml]` werfen die Funktionen `MLDependencyMissingError`
mit klarer Installations-Anleitung.
"""

from __future__ import annotations

from .._sklearn_imports import MLDependencyMissingError
from .evaluation import EvaluationReport, evaluate, report_markdown
from .persistence import (
    DEFAULT_METADATA_PATH,
    DEFAULT_MODEL_PATH,
    ClassifierBundle,
    load_model,
    save_model,
)
from .predict import Prediction, predict
from .train import ModelType, TrainingReport, train_classifier

load_classifier = load_model
save_classifier = save_model

__all__ = [
    "ClassifierBundle",
    "DEFAULT_METADATA_PATH",
    "DEFAULT_MODEL_PATH",
    "EvaluationReport",
    "MLDependencyMissingError",
    "ModelType",
    "Prediction",
    "TrainingReport",
    "evaluate",
    "load_classifier",
    "load_model",
    "predict",
    "report_markdown",
    "save_classifier",
    "save_model",
    "train_classifier",
]
