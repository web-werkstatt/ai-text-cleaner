"""YAML-getriebene Floskel-Replacements (Intros + Connectors)."""

from __future__ import annotations

import re


def apply_floskeln(text: str, patterns: list[dict]) -> tuple[str, list[dict]]:
    """Wendet eine Pattern-Liste aus YAML an.

    Pattern-Format: { pattern: regex, replacement: str, reason: str, multiline?: bool }
    Wenn eine Floskel komplett entfernt wird und am Satzanfang stand, wird
    das nachfolgende Wort kapitalisiert.
    """
    changes: list[dict] = []
    out = text
    for entry in patterns:
        flags = re.IGNORECASE
        if entry.get("multiline"):
            flags |= re.MULTILINE
        compiled = re.compile(entry["pattern"], flags)
        replacement = entry.get("replacement", "")
        reason = entry.get("reason", "floskel")

        def _sub(m: re.Match[str], _repl: str = replacement, _reason: str = reason) -> str:
            before = m.group(0)
            try:
                after = m.expand(_repl)
            except (re.error, IndexError):
                after = _repl
            changes.append(
                {
                    "rule": "floskeln",
                    "before": before,
                    "after": after,
                    "reason": _reason,
                }
            )
            return after

        out = compiled.sub(_sub, out)

    # Wenn Floskel-Removal Satzanfang in Kleinbuchstaben hinterlässt → kapitalisieren.
    out = _capitalize_sentence_starts(out)
    return out, changes


_SENTENCE_START = re.compile(r"(^|[.!?]\s+)([a-zäöü])")


def _capitalize_sentence_starts(text: str) -> str:
    return _SENTENCE_START.sub(lambda m: m.group(1) + m.group(2).upper(), text)
