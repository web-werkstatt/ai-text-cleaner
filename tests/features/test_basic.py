"""Tests für features/basic.py."""

from __future__ import annotations

from ai_text_cleaner.features.basic import extract_basic
from ai_text_cleaner.features.schema import BASIC_FEATURES


def test_empty_text_returns_zeros() -> None:
    out = extract_basic("")
    assert set(out.keys()) == set(BASIC_FEATURES)
    assert all(v == 0.0 for v in out.values())


def test_single_sentence() -> None:
    out = extract_basic("Hallo Welt.")
    assert out["sentence_count"] == 1.0
    assert out["token_count"] == 2.0
    assert out["unique_token_count"] == 2.0
    assert out["type_token_ratio"] == 1.0
    assert out["paragraph_count"] == 1.0
    assert out["em_dash_count"] == 0.0
    assert out["stdev_sentence_length"] == 0.0


def test_multiple_paragraphs_and_em_dashes() -> None:
    text = (
        "Das ist Satz eins. Das ist Satz zwei.\n\n"
        "Ein zweiter Absatz — mit Gedankenstrich. Und noch einer."
    )
    out = extract_basic(text)
    assert out["paragraph_count"] == 2.0
    assert out["sentence_count"] >= 3.0
    assert out["em_dash_count"] == 1.0
    assert out["em_dash_per_paragraph"] == 0.5


def test_type_token_ratio_with_repeats() -> None:
    out = extract_basic("Wort Wort Wort.")
    assert out["token_count"] == 3.0
    assert out["unique_token_count"] == 1.0
    assert out["type_token_ratio"] < 0.5


def test_variance_ratio_finite() -> None:
    text = "Kurz. Etwas länger als der erste Satz."
    out = extract_basic(text)
    assert out["mean_sentence_length"] > 0.0
    assert out["variance_ratio"] >= 0.0
