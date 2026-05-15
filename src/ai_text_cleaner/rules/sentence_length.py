"""Satzlängen-Analyse — Hinweis im Report, kein Auto-Rewrite in v1."""

from __future__ import annotations

import re
import statistics

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> list[str]:
    plain = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    plain = re.sub(r"`[^`]*`", "", plain)
    plain = re.sub(r"^#{1,6}\s.*$", "", plain, flags=re.MULTILINE)
    sentences = [s.strip() for s in SENT_SPLIT.split(plain) if s.strip()]
    return sentences


def analyze_sentence_lengths(text: str) -> dict:
    sentences = _split_sentences(text)
    if len(sentences) < 3:
        return {
            "count": len(sentences),
            "mean": 0.0,
            "stdev": 0.0,
            "min": 0,
            "max": 0,
            "variance_ratio": 0.0,
            "warning": None,
        }
    lengths = [len(s.split()) for s in sentences]
    mean = statistics.mean(lengths)
    stdev = statistics.stdev(lengths) if len(lengths) > 1 else 0.0
    variance_ratio = (stdev / mean) if mean else 0.0
    warning: str | None = None
    if variance_ratio < 0.25 and len(lengths) >= 5:
        warning = (
            f"Geringe Satzlängen-Varianz ({variance_ratio:.2f}). "
            "Menschliche Texte schwanken stärker — erwäge kurze Sätze einzustreuen."
        )
    return {
        "count": len(sentences),
        "mean": round(mean, 1),
        "stdev": round(stdev, 1),
        "min": min(lengths),
        "max": max(lengths),
        "variance_ratio": round(variance_ratio, 3),
        "warning": warning,
    }
