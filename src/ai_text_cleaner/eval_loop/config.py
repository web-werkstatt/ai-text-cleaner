"""EvalConfig — Steuerung des Adversarial-Eval-Loops."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class EvalConfig(BaseModel):
    """Parameter für `run_eval_loop`.

    `min_delta`: Stopp, wenn der neue Score weniger als min_delta unter dem
    bisher besten liegt. Default 0.01 — kleine Schwankungen sind kein Fortschritt.

    `aggressive_after`: Ab Iteration N wird `aggressive=True` an Tier-2-Polish
    gereicht, damit die Verschärfung beim LLM auch greift, wenn der konservative
    Modus stagniert.
    """

    max_iter: int = Field(default=3, ge=1, le=20)
    min_delta: float = Field(default=0.01, ge=0.0, le=1.0)
    classifier_path: Path | None = Field(default=None)
    aggressive_after: int = Field(default=2, ge=0)
    use_pos_features: bool = Field(default=True)
    top_feature_count: int = Field(default=3, ge=1, le=10)


__all__ = ["EvalConfig"]
