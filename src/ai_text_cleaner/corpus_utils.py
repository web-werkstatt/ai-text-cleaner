"""Hilfsfunktionen für Korpus-Akquise.

Aktuell: Markdown → Plaintext-Stripping für `import_blogmachine_corpus.py`.
stdlib-only, kein markdown-it / mistune nötig — wir sind tolerant gegenüber
imperfektem Output, weil die Feature-Extraktion danach robust ist.
"""

from __future__ import annotations

import re
from typing import Final

_CODE_FENCE: Final = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE: Final = re.compile(r"`[^`\n]+`")
_HEADING: Final = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_BOLD_ITALIC: Final = re.compile(r"(\*\*|__|\*|_)(.+?)\1")
_LINK: Final = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_IMAGE: Final = re.compile(r"!\[[^\]]*\]\([^)]+\)")
_HTML_TAG: Final = re.compile(r"<[^>]+>")
_LIST_BULLET: Final = re.compile(r"^[\s]*[-*+]\s+", re.MULTILINE)
_LIST_NUMBER: Final = re.compile(r"^[\s]*\d+\.\s+", re.MULTILINE)
_BLOCKQUOTE: Final = re.compile(r"^>\s?", re.MULTILINE)
_HORIZONTAL: Final = re.compile(r"^[-*_]{3,}\s*$", re.MULTILINE)
_MULTI_NEWLINE: Final = re.compile(r"\n{3,}")
_FRONTMATTER: Final = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def strip_markdown(text: str) -> str:
    """Reduziert Markdown auf Plaintext für Feature-Extraktion.

    Behält: Absatz-Struktur, Em-Dashes, Anführungszeichen.
    Entfernt: Code-Blöcke (komplett), Inline-Code, Headings, Listen-Marker,
              Links (Text bleibt), Bilder, HTML-Tags, Frontmatter.
    """
    text = _FRONTMATTER.sub("", text)
    text = _CODE_FENCE.sub("", text)
    text = _IMAGE.sub("", text)
    text = _LINK.sub(r"\1", text)
    text = _INLINE_CODE.sub("", text)
    text = _HEADING.sub("", text)
    text = _BOLD_ITALIC.sub(r"\2", text)
    text = _HTML_TAG.sub("", text)
    text = _LIST_BULLET.sub("", text)
    text = _LIST_NUMBER.sub("", text)
    text = _BLOCKQUOTE.sub("", text)
    text = _HORIZONTAL.sub("", text)
    text = _MULTI_NEWLINE.sub("\n\n", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\wäöüÄÖÜß]+\b", text))


__all__ = ["strip_markdown", "word_count"]
