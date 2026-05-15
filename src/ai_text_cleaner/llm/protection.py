"""Schützt Code-Blöcke, Inline-Code, URLs, Zitate und Zahlen vor LLM-Rewrites.

Vor dem LLM-Call werden geschützte Bereiche durch Tokens ersetzt (z. B.
`__PROTECTED_0__`). Nach der Antwort werden die Tokens zurückersetzt.
"""

from __future__ import annotations

import re

_PROTECT_PATTERNS = [
    re.compile(r"```.*?```", re.DOTALL),     # Fenced Code
    re.compile(r"`[^`\n]+`"),                # Inline Code
    re.compile(r"https?://\S+"),             # URLs
    re.compile(r"^>\s.*$", re.MULTILINE),    # Markdown-Zitate
    re.compile(r"\b\d[\d.,]*\s*(?:%|€|\$|EUR|USD|km|kg|g|h|min|s|MB|GB|TB)?\b"),
]


def mask_protected(text: str) -> tuple[str, list[str]]:
    """Ersetzt geschützte Spans durch Tokens. Liefert (maskierter Text, originals)."""
    originals: list[str] = []
    masked = text
    for pattern in _PROTECT_PATTERNS:
        def _sub(m: re.Match[str]) -> str:
            token = f"__PROTECTED_{len(originals)}__"
            originals.append(m.group(0))
            return token
        masked = pattern.sub(_sub, masked)
    return masked, originals


def restore_protected(text: str, originals: list[str]) -> str:
    """Setzt Tokens zurück in die Originalwerte. Tolerant gegen fehlende Tokens."""
    out = text
    for i, original in enumerate(originals):
        token = f"__PROTECTED_{i}__"
        out = out.replace(token, original)
    return out
