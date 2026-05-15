"""Buzzword-Verben durch neutralere Synonyme ersetzen."""

from __future__ import annotations

from .floskeln import apply_floskeln


def apply_buzzwords(text: str, patterns: list[dict]) -> tuple[str, list[dict]]:
    """Wendet Buzzword-Patterns an (gleicher Mechanismus wie Floskeln)."""
    return apply_floskeln(text, patterns)
