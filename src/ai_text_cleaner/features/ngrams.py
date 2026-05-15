"""N-Gram-Features — Bigram-Konzentration, Trigram-Diversität, Wiederholungsrate."""

from __future__ import annotations

import re
from collections import Counter
from typing import Final

from .schema import NGRAM_FEATURES

_TOKEN_PATTERN: Final = re.compile(r"\b[\wäöüÄÖÜß]+\b", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return [m.group(0).lower() for m in _TOKEN_PATTERN.finditer(text)]


def _ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    if len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def extract_ngrams(text: str) -> dict[str, float]:
    """Extrahiere N-Gram-Features. Liefert für alle NGRAM_FEATURES einen Wert."""
    tokens = _tokens(text)
    token_count = len(tokens)

    bigrams = _ngrams(tokens, 2)
    trigrams = _ngrams(tokens, 3)

    if bigrams:
        bigram_counter = Counter(bigrams)
        top10_sum = sum(c for _, c in bigram_counter.most_common(10))
        bigram_top10_concentration = top10_sum / len(bigrams)
    else:
        bigram_top10_concentration = 0.0

    if trigrams:
        trigram_unique_ratio = len(set(trigrams)) / len(trigrams)
    else:
        trigram_unique_ratio = 0.0

    if token_count > 0:
        token_counter = Counter(tokens)
        repeated = sum(c - 1 for c in token_counter.values() if c > 1)
        repetition_rate = repeated / token_count
    else:
        repetition_rate = 0.0

    features = {
        "bigram_top10_concentration": bigram_top10_concentration,
        "repetition_rate": repetition_rate,
        "trigram_unique_ratio": trigram_unique_ratio,
    }

    assert set(features.keys()) == set(NGRAM_FEATURES), "Feature-Set drift in ngrams.py"
    return features


__all__ = ["extract_ngrams"]
