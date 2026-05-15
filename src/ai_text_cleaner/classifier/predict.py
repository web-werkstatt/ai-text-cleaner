"""Inferenz-API: Text → Score + Top-Features.

Top-Features sind die Feature-Beiträge, die den Score am stärksten Richtung
"AI" treiben. Für LogReg ist das `(feature_value - mean) / stdev * coefficient`.
Für GBM kommt die globale `feature_importances_` zum Einsatz, weil
sample-spezifische Beiträge ohne SHAP teuer wären.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .._sklearn_imports import require_sklearn
from ..features import extract_features
from .persistence import ClassifierBundle, load_model

Confidence = Literal["low", "medium", "high"]


@dataclass
class Prediction:
    score: float
    top_features: list[tuple[str, float]]
    confidence: Confidence
    pos_available: bool

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 4),
            "top_features": [(n, round(v, 4)) for n, v in self.top_features],
            "confidence": self.confidence,
            "pos_available": self.pos_available,
        }


def _confidence_for(score: float) -> Confidence:
    distance = abs(score - 0.5)
    if distance < 0.10:
        return "low"
    if distance < 0.25:
        return "medium"
    return "high"


def _top_features_logreg(
    estimator,
    scaler,
    feature_names: list[str],
    raw_values: list[float],
    k: int = 10,
) -> list[tuple[str, float]]:
    coefs = list(estimator.coef_[0])
    means = list(scaler.mean_)
    scales = list(scaler.scale_)
    contributions: list[tuple[str, float]] = []
    for name, value, coef, mean, scale in zip(
        feature_names, raw_values, coefs, means, scales, strict=True
    ):
        if scale == 0:
            continue
        scaled = (value - mean) / scale
        contributions.append((name, scaled * coef))
    contributions.sort(key=lambda x: x[1], reverse=True)
    return contributions[:k]


def _top_features_gbm(estimator, feature_names: list[str], k: int = 10) -> list[tuple[str, float]]:
    importances = list(estimator.feature_importances_)
    pairs = list(zip(feature_names, importances, strict=True))
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs[:k]


def predict(
    text: str,
    bundle: ClassifierBundle | None = None,
    *,
    use_pos: bool = True,
) -> Prediction:
    """Liefert Score 0.0-1.0 (1.0 = sehr KI-haft) + Top-Features + Confidence."""
    require_sklearn()
    if bundle is None:
        bundle = load_model()

    vector = extract_features(text, source_id="inference", label="unknown", use_pos=use_pos)
    raw_values = [vector.features.get(name, 0.0) for name in bundle.feature_names]
    scaled = bundle.scaler.transform([raw_values])
    score = float(bundle.estimator.predict_proba(scaled)[0][1])

    if bundle.model_type == "logreg":
        top = _top_features_logreg(
            bundle.estimator, bundle.scaler, bundle.feature_names, raw_values
        )
    else:
        top = _top_features_gbm(bundle.estimator, bundle.feature_names)

    return Prediction(
        score=score,
        top_features=top,
        confidence=_confidence_for(score),
        pos_available=vector.pos_available,
    )


__all__ = ["Confidence", "Prediction", "predict"]
