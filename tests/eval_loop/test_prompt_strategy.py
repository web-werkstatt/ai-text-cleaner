"""Tests für eval_loop/prompt_strategy.py."""

from __future__ import annotations

from ai_text_cleaner.eval_loop.prompt_strategy import (
    FEATURE_HINTS,
    build_prompt_hints,
    format_for_prompt,
)


def test_returns_known_hints() -> None:
    features = [
        ("em_dash_per_1000_words", 0.4),
        ("variance_ratio", 0.3),
        ("type_token_ratio", 0.2),
    ]
    hints = build_prompt_hints(features)
    assert len(hints) == 3
    assert all(h in FEATURE_HINTS.values() for h in hints)


def test_caps_at_top_n() -> None:
    features = [(name, 0.1) for name in list(FEATURE_HINTS.keys())]
    hints = build_prompt_hints(features, top_n=2)
    assert len(hints) == 2


def test_unknown_features_skipped_silently() -> None:
    features = [("unknown_x", 0.5), ("em_dash_per_1000_words", 0.3)]
    hints = build_prompt_hints(features)
    assert len(hints) == 1
    assert hints[0] == FEATURE_HINTS["em_dash_per_1000_words"]


def test_deduplicates_hints() -> None:
    features = [("em_dash_per_1000_words", 0.5), ("em_dash_per_1000_words", 0.4)]
    hints = build_prompt_hints(features, top_n=5)
    assert len(hints) == 1


def test_format_for_prompt_empty() -> None:
    assert format_for_prompt([]) == ""


def test_format_for_prompt_numbered() -> None:
    rendered = format_for_prompt(["foo", "bar"])
    assert "1. foo" in rendered
    assert "2. bar" in rendered
    assert "Stilanalyse" in rendered
