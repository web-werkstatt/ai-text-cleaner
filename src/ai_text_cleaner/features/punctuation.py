"""Interpunktions-Features — Dash-Raten, Doppelpunkte, Anführungszeichen-Stil."""

from __future__ import annotations

import re
from typing import Final

from .schema import PUNCTUATION_FEATURES

_TOKEN_PATTERN: Final = re.compile(r"\b[\wäöüÄÖÜß]+\b", re.UNICODE)
_TYPOGRAPHIC_QUOTES: Final = ("„", "“", "”", "«", "»", "‚", "‘", "’")
_ASCII_QUOTES: Final = ('"', "'")


def _per_1000(count: int, token_count: int) -> float:
    if token_count == 0:
        return 0.0
    return (count / token_count) * 1000.0


def extract_punctuation(text: str) -> dict[str, float]:
    """Extrahiere Punctuation-Features. Liefert für alle PUNCTUATION_FEATURES einen Wert."""
    tokens = _TOKEN_PATTERN.findall(text)
    token_count = len(tokens)

    em_dash = text.count("—")
    en_dash = text.count("–")
    colon = text.count(":")
    bracket_open = text.count("(")
    bracket_close = text.count(")")
    bracket_count = bracket_open + bracket_close

    typo_quote_count = sum(text.count(q) for q in _TYPOGRAPHIC_QUOTES)
    ascii_quote_count = sum(text.count(q) for q in _ASCII_QUOTES)
    total_quotes = typo_quote_count + ascii_quote_count
    typographic_quote_ratio = (
        typo_quote_count / total_quotes if total_quotes > 0 else 0.0
    )

    features = {
        "bracket_per_1000_words": _per_1000(bracket_count, token_count),
        "colon_per_1000_words": _per_1000(colon, token_count),
        "em_dash_per_1000_words": _per_1000(em_dash, token_count),
        "en_dash_per_1000_words": _per_1000(en_dash, token_count),
        "typographic_quote_ratio": typographic_quote_ratio,
    }

    assert set(features.keys()) == set(PUNCTUATION_FEATURES), (
        "Feature-Set drift in punctuation.py"
    )
    return features


__all__ = ["extract_punctuation"]
