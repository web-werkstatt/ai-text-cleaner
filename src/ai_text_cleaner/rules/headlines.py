"""Markdown-Headlines glätten (z. B. „Die ultimative Anleitung")."""

from __future__ import annotations

from .floskeln import apply_floskeln


def apply_headlines(text: str, patterns: list[dict]) -> tuple[str, list[dict]]:
    return apply_floskeln(text, patterns)
