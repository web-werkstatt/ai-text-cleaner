"""Adversarial-Eval-Loop (Sprint 25c).

Public-API:
- `run_eval_loop(text, config, score_provider, polish_provider)` → EvalResult
- `EvalConfig` — Steuerparameter
- `EvalResult`, `EvalIteration` — Ergebnis + Verlauf
- `ScoreProvider`, `PolishProvider` — Callable-Protocols für DI
- `build_prompt_hints` — Feature → Hint-Mapping (öffentlich für Engine + Tests)
"""

from __future__ import annotations

from .config import EvalConfig
from .loop import (
    EvalIteration,
    EvalResult,
    PolishProvider,
    ScoreProvider,
    build_prompt_extension,
    run_eval_loop,
)
from .prompt_strategy import FEATURE_HINTS, build_prompt_hints, format_for_prompt
from .trajectory import improving, plot_ascii, total_improvement

__all__ = [
    "EvalConfig",
    "EvalIteration",
    "EvalResult",
    "FEATURE_HINTS",
    "PolishProvider",
    "ScoreProvider",
    "build_prompt_extension",
    "build_prompt_hints",
    "format_for_prompt",
    "improving",
    "plot_ascii",
    "run_eval_loop",
    "total_improvement",
]
