"""Tier 1 — regelbasierter Cleaner."""

from .em_dashes import apply_em_dashes, count_em_dashes
from .floskeln import apply_floskeln
from .buzzwords import apply_buzzwords
from .headlines import apply_headlines
from .whitespace import apply_whitespace
from .sentence_length import analyze_sentence_lengths

__all__ = [
    "apply_em_dashes",
    "count_em_dashes",
    "apply_floskeln",
    "apply_buzzwords",
    "apply_headlines",
    "apply_whitespace",
    "analyze_sentence_lengths",
]
