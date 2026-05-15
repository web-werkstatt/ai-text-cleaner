"""End-to-End: clean_text(mode=HYBRID_ML) mit injizierten Mock-Providern.

Testet, dass der HYBRID_ML-Dispatch in engine.py den Eval-Loop korrekt
ausführt, ohne `[ml]`-Extra oder echtes Anthropic-Setup zu brauchen.
"""

from __future__ import annotations

from ai_text_cleaner import Mode, clean_text
from ai_text_cleaner.eval_loop import EvalConfig


def _score_descending() -> tuple[list[float], object]:
    state = {"i": 0}
    seq = [0.9, 0.7, 0.5, 0.3]

    def _score(_text: str) -> tuple[float, list[tuple[str, float]]]:
        i = min(state["i"], len(seq) - 1)
        state["i"] += 1
        return seq[i], [("em_dash_per_1000_words", 0.5)]

    return seq, _score


def _polish_append(text: str, *, hints: list[str], aggressive: bool) -> str:  # noqa: ARG001
    return text + " (geglättet)"


def test_hybrid_ml_returns_trajectory() -> None:
    _, score_provider = _score_descending()
    result = clean_text(
        "Test-Text — mit Em-Dash.",
        mode=Mode.HYBRID_ML,
        eval_config=EvalConfig(max_iter=2, min_delta=0.0),
        score_provider=score_provider,
        polish_provider=_polish_append,
    )
    assert result.trajectory is not None
    assert len(result.trajectory) >= 2
    assert result.iterations >= 1
    assert result.stop_reason is not None


def test_hybrid_ml_runs_tier1_rules_first() -> None:
    _, score_provider = _score_descending()
    result = clean_text(
        "Text — mit Em-Dash — und noch einem.",
        mode=Mode.HYBRID_ML,
        eval_config=EvalConfig(max_iter=1, min_delta=0.0),
        score_provider=score_provider,
        polish_provider=_polish_append,
    )
    assert "geglättet" in result.text
    rule_names = {c.get("rule") for c in result.changes}
    assert "em_dashes" in rule_names


def test_hybrid_ml_report_contains_trajectory_block() -> None:
    _, score_provider = _score_descending()
    result = clean_text(
        "Test.",
        mode=Mode.HYBRID_ML,
        eval_config=EvalConfig(max_iter=2, min_delta=0.0),
        score_provider=score_provider,
        polish_provider=_polish_append,
    )
    md = result.report.markdown()
    assert "Score-Verlauf" in md
    assert "Stop-Grund" in md
