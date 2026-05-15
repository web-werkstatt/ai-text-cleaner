"""Modell-Persistenz via joblib. ClassifierBundle hält Estimator + Scaler + Metadata."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .._sklearn_imports import require_joblib

DEFAULT_MODEL_PATH = Path(__file__).parent / "model.pkl"
DEFAULT_METADATA_PATH = Path(__file__).parent / "model.metadata.json"


@dataclass
class ClassifierBundle:
    """Trainings-Artefakt: Estimator + Feature-Skalierer + Metadaten."""

    estimator: Any
    scaler: Any
    feature_names: list[str]
    model_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def metadata_with_paths(self, model_path: Path) -> dict[str, Any]:
        return {
            **self.metadata,
            "model_type": self.model_type,
            "feature_count": len(self.feature_names),
            "model_file": model_path.name,
        }


def save_model(
    bundle: ClassifierBundle,
    model_path: Path = DEFAULT_MODEL_PATH,
    metadata_path: Path | None = None,
) -> None:
    """Bundle nach joblib + JSON-Metadata serialisieren."""
    joblib = require_joblib()
    model_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "estimator": bundle.estimator,
            "scaler": bundle.scaler,
            "feature_names": bundle.feature_names,
            "model_type": bundle.model_type,
        },
        model_path,
        compress=3,
    )

    meta_path = metadata_path or model_path.with_suffix(".metadata.json")
    meta_path.write_text(
        json.dumps(bundle.metadata_with_paths(model_path), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_model(model_path: Path = DEFAULT_MODEL_PATH) -> ClassifierBundle:
    """Bundle aus joblib-Datei rekonstruieren."""
    joblib = require_joblib()
    if not model_path.exists():
        raise FileNotFoundError(
            f"Kein Modell unter {model_path}. Erst `python scripts/train_classifier.py` ausführen."
        )

    payload = joblib.load(model_path)
    meta_path = model_path.with_suffix(".metadata.json")
    metadata = (
        json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    )

    return ClassifierBundle(
        estimator=payload["estimator"],
        scaler=payload["scaler"],
        feature_names=list(payload["feature_names"]),
        model_type=str(payload["model_type"]),
        metadata=metadata,
    )


__all__ = [
    "ClassifierBundle",
    "DEFAULT_METADATA_PATH",
    "DEFAULT_MODEL_PATH",
    "load_model",
    "save_model",
]
