"""Whitespace-Normalisierung: NBSP, doppelte Leerzeichen, Mehrfach-Newlines."""

from __future__ import annotations

import re

NBSP = " "


def apply_whitespace(text: str) -> tuple[str, list[dict]]:
    changes: list[dict] = []
    out = text
    if NBSP in out:
        count = out.count(NBSP)
        out = out.replace(NBSP, " ")
        changes.append(
            {"rule": "whitespace", "before": f"{count}x NBSP", "after": "regular space", "reason": "nbsp"}
        )

    new_out, n = re.subn(r"[ \t]{2,}", " ", out)
    if n:
        changes.append(
            {"rule": "whitespace", "before": f"{n}x multiple spaces", "after": "single space", "reason": "multispace"}
        )
        out = new_out

    new_out, n = re.subn(r"\n{3,}", "\n\n", out)
    if n:
        changes.append(
            {"rule": "whitespace", "before": f"{n}x triple newline", "after": "double newline", "reason": "multinewline"}
        )
        out = new_out

    # Trailing-Whitespace pro Zeile
    new_out = re.sub(r"[ \t]+\n", "\n", out)
    if new_out != out:
        changes.append(
            {"rule": "whitespace", "before": "trailing ws", "after": "stripped", "reason": "trailing"}
        )
        out = new_out

    return out, changes
