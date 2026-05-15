"""Tests für features/punctuation.py."""

from __future__ import annotations

from ai_text_cleaner.features.punctuation import extract_punctuation
from ai_text_cleaner.features.schema import PUNCTUATION_FEATURES


def test_empty_text() -> None:
    out = extract_punctuation("")
    assert set(out.keys()) == set(PUNCTUATION_FEATURES)
    assert all(v == 0.0 for v in out.values())


def test_em_dash_rate() -> None:
    tokens_text = " ".join(["wort"] * 1000)
    out = extract_punctuation(f"{tokens_text} — Test")
    assert out["em_dash_per_1000_words"] > 0.0


def test_en_dash_distinct_from_em_dash() -> None:
    em = extract_punctuation("a — b")
    en = extract_punctuation("a – b")
    assert em["em_dash_per_1000_words"] > 0.0
    assert em["en_dash_per_1000_words"] == 0.0
    assert en["en_dash_per_1000_words"] > 0.0
    assert en["em_dash_per_1000_words"] == 0.0


def test_typographic_quote_ratio() -> None:
    out = extract_punctuation("„Hallo" + chr(0x201C) + " und \"Welt\"")
    assert 0.0 < out["typographic_quote_ratio"] < 1.0


def test_brackets_counted() -> None:
    out = extract_punctuation("Text (mit) Klammern (auch hier).")
    assert out["bracket_per_1000_words"] > 0.0
