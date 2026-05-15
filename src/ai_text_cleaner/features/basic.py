"""Basic-Features — stdlib only, kein spaCy, kein numpy."""

from __future__ import annotations

import re
import statistics
from typing import Final

from .schema import BASIC_FEATURES

_SENTENCE_SPLIT: Final = re.compile(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ])")
_TOKEN_PATTERN: Final = re.compile(r"\b[\wäöüÄÖÜß]+\b", re.UNICODE)
_PARAGRAPH_SPLIT: Final = re.compile(r"\n\s*\n")


def _split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    parts = _SENTENCE_SPLIT.split(text)
    return [p.strip() for p in parts if p.strip()]


def _split_paragraphs(text: str) -> list[str]:
    parts = _PARAGRAPH_SPLIT.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def _tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _TOKEN_PATTERN.finditer(text)]


def extract_basic(text: str) -> dict[str, float]:
    """Extrahiere stdlib-Features. Liefert für alle BASIC_FEATURES einen Wert."""
    sentences = _split_sentences(text)
    paragraphs = _split_paragraphs(text)
    tokens = _tokenize(text)

    sentence_lengths = [len(_tokenize(s)) for s in sentences]
    paragraph_lengths = [len(_tokenize(p)) for p in paragraphs]

    sentence_count = len(sentences)
    token_count = len(tokens)
    unique_token_count = len(set(tokens))
    paragraph_count = len(paragraphs)

    if sentence_lengths:
        mean_sentence_length = statistics.fmean(sentence_lengths)
        stdev_sentence_length = (
            statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0.0
        )
    else:
        mean_sentence_length = 0.0
        stdev_sentence_length = 0.0

    variance_ratio = (
        stdev_sentence_length / mean_sentence_length if mean_sentence_length > 0 else 0.0
    )

    mean_paragraph_length = (
        statistics.fmean(paragraph_lengths) if paragraph_lengths else 0.0
    )

    type_token_ratio = unique_token_count / token_count if token_count > 0 else 0.0
    avg_word_length = (
        sum(len(t) for t in tokens) / token_count if token_count > 0 else 0.0
    )

    em_dash_count = text.count("—")
    em_dash_per_paragraph = em_dash_count / paragraph_count if paragraph_count > 0 else 0.0

    features = {
        "avg_word_length": avg_word_length,
        "em_dash_count": float(em_dash_count),
        "em_dash_per_paragraph": em_dash_per_paragraph,
        "mean_paragraph_length": mean_paragraph_length,
        "mean_sentence_length": mean_sentence_length,
        "paragraph_count": float(paragraph_count),
        "sentence_count": float(sentence_count),
        "stdev_sentence_length": stdev_sentence_length,
        "token_count": float(token_count),
        "type_token_ratio": type_token_ratio,
        "unique_token_count": float(unique_token_count),
        "variance_ratio": variance_ratio,
    }

    assert set(features.keys()) == set(BASIC_FEATURES), "Feature-Set drift in basic.py"
    return features


__all__ = ["extract_basic"]
