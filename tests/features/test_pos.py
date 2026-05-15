"""Tests für features/pos.py — laufen ohne installiertes spaCy."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ai_text_cleaner.features.pos import extract_pos
from ai_text_cleaner.features.schema import POS_FEATURES


def test_returns_zeros_when_spacy_unavailable() -> None:
    with patch("ai_text_cleaner.features.pos._load_spacy", return_value=None):
        features, available = extract_pos("Ein deutscher Satz.")
    assert available is False
    assert set(features.keys()) == set(POS_FEATURES)
    assert all(v == 0.0 for v in features.values())


def test_returns_zeros_for_empty_text_even_with_spacy() -> None:
    fake_nlp = MagicMock()
    with patch("ai_text_cleaner.features.pos._load_spacy", return_value=fake_nlp):
        features, available = extract_pos("")
    assert available is False
    assert all(v == 0.0 for v in features.values())


def test_distributes_pos_counts_correctly() -> None:
    fake_nlp = MagicMock()

    def make_token(pos: str, dep: str = "", head_idx: int = 0, idx: int = 0) -> MagicMock:
        tok = MagicMock()
        tok.pos_ = pos
        tok.dep_ = dep
        tok.i = idx
        head = MagicMock()
        head.i = head_idx
        head.head = head
        tok.head = head
        return tok

    tokens = [
        make_token("NOUN", idx=0),
        make_token("NOUN", idx=1),
        make_token("VERB", idx=2),
        make_token("ADJ", idx=3),
    ]
    fake_nlp.return_value = tokens

    with patch("ai_text_cleaner.features.pos._load_spacy", return_value=fake_nlp):
        features, available = extract_pos("Text egal — wird durch Mock ersetzt.")

    assert available is True
    assert features["pos_noun_ratio"] == 0.5
    assert features["pos_verb_ratio"] == 0.25
    assert features["pos_adj_ratio"] == 0.25
    assert features["adj_noun_ratio"] == 0.5
