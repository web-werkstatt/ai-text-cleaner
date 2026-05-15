"""Plain-Text- und Markdown-Loader."""

from __future__ import annotations

from pathlib import Path


def load_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def save_text(path: str | Path, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")
