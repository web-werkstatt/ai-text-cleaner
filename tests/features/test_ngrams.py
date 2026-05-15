"""Tests für features/ngrams.py."""

from __future__ import annotations

from ai_text_cleaner.features.ngrams import extract_ngrams
from ai_text_cleaner.features.schema import NGRAM_FEATURES


def test_empty_text() -> None:
    out = extract_ngrams("")
    assert set(out.keys()) == set(NGRAM_FEATURES)
    assert all(v == 0.0 for v in out.values())


def test_single_token() -> None:
    out = extract_ngrams("Hallo")
    assert out["bigram_top10_concentration"] == 0.0
    assert out["trigram_unique_ratio"] == 0.0
    assert out["repetition_rate"] == 0.0


def test_repetition_rate_detects_repeats() -> None:
    out = extract_ngrams("foo foo foo bar")
    assert out["repetition_rate"] > 0.0
    assert out["repetition_rate"] <= 1.0


def test_trigram_ratio_high_for_diverse_text() -> None:
    out = extract_ngrams("a b c d e f g h i j")
    assert out["trigram_unique_ratio"] == 1.0


def test_bigram_concentration_bounded() -> None:
    out = extract_ngrams("a b a b a b a b")
    assert 0.0 <= out["bigram_top10_concentration"] <= 1.0
