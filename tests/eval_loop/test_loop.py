"""Tests für eval_loop/loop.py — run_eval_loop mit Mocks."""

from __future__ import annotations

from collections.abc import Callable

from ai_text_cleaner.eval_loop.config import EvalConfig
from ai_text_cleaner.eval_loop.loop import EvalResult, run_eval_loop


def _make_score(values: list[float]) -> Callable[[str], tuple[float, list[tuple[str, float]]]]:
    """Score-Provider, der bei jedem Aufruf den nächsten Wert aus `values` zurückgibt.
    Wenn die Liste leer ist, bleibt der letzte Wert stehen."""
    iter_state = {"i": 0}

    def _score(_text: str) -> tuple[float, list[tuple[str, float]]]:
        idx = min(iter_state["i"], len(values) - 1)
        iter_state["i"] += 1
        return values[idx], [("em_dash_per_1000_words", 0.5)]

    return _score


def _noop_polish(text: str, *, hints: list[str], aggressive: bool) -> str:  # noqa: ARG001
    return text + " ."


def test_loop_respects_max_iter() -> None:
    config = EvalConfig(max_iter=3, min_delta=0.0)
    scores = [0.9, 0.8, 0.7, 0.6, 0.5]
    result = run_eval_loop(
        "Text",
        config=config,
        score_provider=_make_score(scores),
        polish_provider=_noop_polish,
    )
    assert result.iterations == 3
    assert result.stop_reason == "max_iter_reached"
    assert len(result.trajectory) == 4  # initial + 3 iterations


def test_loop_stops_on_no_improvement() -> None:
    config = EvalConfig(max_iter=10, min_delta=0.05)
    scores = [0.9, 0.85, 0.84, 0.83]
    result = run_eval_loop(
        "Text",
        config=config,
        score_provider=_make_score(scores),
        polish_provider=_noop_polish,
    )
    assert result.stop_reason == "no_improvement"
    assert result.iterations < 10


def test_loop_stops_when_score_zero() -> None:
    config = EvalConfig(max_iter=10)
    scores = [0.5, 0.0, 0.0]
    result = run_eval_loop(
        "Text",
        config=config,
        score_provider=_make_score(scores),
        polish_provider=_noop_polish,
    )
    assert result.stop_reason == "score_zero"
    assert result.best_score == 0.0


def test_loop_returns_best_text_not_last() -> None:
    config = EvalConfig(max_iter=3, min_delta=0.0)
    scores = [0.9, 0.3, 0.5, 0.4]
    result = run_eval_loop(
        "Original",
        config=config,
        score_provider=_make_score(scores),
        polish_provider=_noop_polish,
    )
    assert result.best_score == 0.3
    assert result.final_score == result.trajectory[-1]


def test_loop_initial_zero_score_short_circuits() -> None:
    config = EvalConfig(max_iter=5)
    result = run_eval_loop(
        "Schon perfekt",
        config=config,
        score_provider=_make_score([0.0]),
        polish_provider=_noop_polish,
    )
    assert result.iterations == 0
    assert result.stop_reason == "initial_score_zero"
    assert result.text == "Schon perfekt"


def test_loop_on_iteration_callback_invoked() -> None:
    config = EvalConfig(max_iter=2, min_delta=0.0)
    seen: list[int] = []

    def cb(it):
        seen.append(it.iteration)

    run_eval_loop(
        "Text",
        config=config,
        score_provider=_make_score([0.9, 0.7, 0.5]),
        polish_provider=_noop_polish,
        on_iteration=cb,
    )
    assert seen == [0, 1, 2]


def test_loop_aggressive_after_threshold() -> None:
    config = EvalConfig(max_iter=3, min_delta=0.0, aggressive_after=2)
    seen_aggressive: list[bool] = []

    def polish(text: str, *, hints: list[str], aggressive: bool) -> str:  # noqa: ARG001
        seen_aggressive.append(aggressive)
        return text + "."

    result = run_eval_loop(
        "Text",
        config=config,
        score_provider=_make_score([0.9, 0.7, 0.5, 0.3]),
        polish_provider=polish,
    )
    assert seen_aggressive == [False, True, True]
    assert isinstance(result, EvalResult)
