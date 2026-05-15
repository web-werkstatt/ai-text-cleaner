"""Adversarial-Eval-Loop — iterativer Tier-2-Polish mit Klassifikator-Reward.

Die Loop ist dependency-injection-freundlich aufgebaut: ScoreProvider und
PolishProvider sind Callable-Protokolle, die in Tests durch Mocks ersetzt
werden. In Produktion liefern sie den echten Classifier-Score und den
echten Tier-2-Polish.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from .config import EvalConfig
from .prompt_strategy import build_prompt_hints, format_for_prompt
from .trajectory import improving, plot_ascii, total_improvement


class ScoreProvider(Protocol):
    """Liefert (score 0.0–1.0, top_features). Höherer Score = KI-haftiger."""

    def __call__(self, text: str) -> tuple[float, list[tuple[str, float]]]:
        ...


class PolishProvider(Protocol):
    """Polished den Text mit zusätzlichen Hinweisen. Liefert nur den Text."""

    def __call__(self, text: str, *, hints: list[str], aggressive: bool) -> str:
        ...


@dataclass
class EvalIteration:
    iteration: int
    score: float
    text: str
    hints: list[str] = field(default_factory=list)
    aggressive: bool = False
    accepted: bool = True
    stop_reason: str | None = None


@dataclass
class EvalResult:
    text: str
    initial_score: float
    final_score: float
    best_score: float
    trajectory: list[float]
    iterations: int
    stop_reason: str
    history: list[EvalIteration] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "initial_score": round(self.initial_score, 4),
            "final_score": round(self.final_score, 4),
            "best_score": round(self.best_score, 4),
            "trajectory": [round(s, 4) for s in self.trajectory],
            "iterations": self.iterations,
            "stop_reason": self.stop_reason,
            "improvement": round(total_improvement(self.trajectory), 4),
            "plot": plot_ascii(self.trajectory),
        }


def run_eval_loop(
    text: str,
    *,
    config: EvalConfig,
    score_provider: ScoreProvider,
    polish_provider: PolishProvider,
    on_iteration: Callable[[EvalIteration], None] | None = None,
) -> EvalResult:
    """Iteriere Polish + Score, bis Stop-Bedingung greift.

    Stop-Bedingungen (Reihenfolge):
    1. max_iter erreicht
    2. Score konvergiert (improving() False)
    3. Score ist bereits 0.0 (Best Case)
    """
    initial_score, current_top = score_provider(text)
    trajectory: list[float] = [initial_score]
    history: list[EvalIteration] = [
        EvalIteration(iteration=0, score=initial_score, text=text, accepted=True)
    ]
    if on_iteration is not None:
        on_iteration(history[0])

    current_text = text
    best_text = text
    best_score = initial_score
    stop_reason = "max_iter_reached"

    if initial_score <= 0.0:
        return _build_result(
            text=text,
            trajectory=trajectory,
            history=history,
            stop_reason="initial_score_zero",
            initial=initial_score,
            best=best_score,
        )

    for iteration in range(1, config.max_iter + 1):
        hints = build_prompt_hints(current_top, top_n=config.top_feature_count)
        aggressive = iteration >= config.aggressive_after

        polished = polish_provider(
            current_text,
            hints=hints,
            aggressive=aggressive,
        )
        new_score, new_top = score_provider(polished)
        trajectory.append(new_score)
        current_top = new_top

        accepted = new_score < best_score
        iter_record = EvalIteration(
            iteration=iteration,
            score=new_score,
            text=polished,
            hints=hints,
            aggressive=aggressive,
            accepted=accepted,
        )

        if accepted:
            best_text = polished
            best_score = new_score
            current_text = polished

        if on_iteration is not None:
            on_iteration(iter_record)
        history.append(iter_record)

        if new_score <= 0.0:
            stop_reason = "score_zero"
            iter_record.stop_reason = stop_reason
            break

        if not improving(trajectory, config.min_delta):
            stop_reason = "no_improvement"
            iter_record.stop_reason = stop_reason
            break

    return _build_result(
        text=best_text,
        trajectory=trajectory,
        history=history,
        stop_reason=stop_reason,
        initial=initial_score,
        best=best_score,
    )


def _build_result(
    *,
    text: str,
    trajectory: list[float],
    history: list[EvalIteration],
    stop_reason: str,
    initial: float,
    best: float,
) -> EvalResult:
    return EvalResult(
        text=text,
        initial_score=initial,
        final_score=trajectory[-1] if trajectory else initial,
        best_score=best,
        trajectory=trajectory,
        iterations=max(0, len(trajectory) - 1),
        stop_reason=stop_reason,
        history=history,
    )


def build_prompt_extension(hints: list[str]) -> str:
    """Convenience-Wrapper für Engine-Dispatch."""
    return format_for_prompt(hints)


__all__ = [
    "EvalIteration",
    "EvalResult",
    "PolishProvider",
    "ScoreProvider",
    "build_prompt_extension",
    "run_eval_loop",
]
