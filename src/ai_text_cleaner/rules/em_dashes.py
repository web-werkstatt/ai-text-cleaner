"""Em-Dash-Overuse glätten.

Erlaubt max_per_paragraph Em-Dashes pro Absatz. Überschüssige werden ersetzt.
Em-Dash = U+2014 (—). En-Dash (–) und Hyphen-Minus (-) bleiben unangetastet.
"""

from __future__ import annotations

import re

EM_DASH = "—"
EM_DASH_PADDED = re.compile(r"\s*—\s*")


def count_em_dashes(text: str) -> int:
    return text.count(EM_DASH)


def apply_em_dashes(
    text: str,
    max_per_paragraph: int = 1,
    strategy: str = "comma",
) -> tuple[str, list[dict]]:
    """Überzählige Em-Dashes pro Absatz ersetzen.

    Strategy:
      comma  → ", "
      period → ". " (mit Großschreibung des Folgesatzes)
    """
    paragraphs = re.split(r"(\n\s*\n)", text)
    changes: list[dict] = []
    out_parts: list[str] = []

    for chunk in paragraphs:
        if re.fullmatch(r"\n\s*\n", chunk):
            out_parts.append(chunk)
            continue
        new_para, para_changes = _process_paragraph(chunk, max_per_paragraph, strategy)
        out_parts.append(new_para)
        changes.extend(para_changes)

    return "".join(out_parts), changes


def _process_paragraph(
    para: str, max_allowed: int, strategy: str
) -> tuple[str, list[dict]]:
    count = para.count(EM_DASH)
    if count <= max_allowed:
        return para, []

    changes: list[dict] = []
    to_replace = count - max_allowed
    result_chars: list[str] = []
    i = 0
    seen = 0
    replaced = 0

    while i < len(para):
        ch = para[i]
        if ch == EM_DASH:
            seen += 1
            if seen > max_allowed and replaced < to_replace:
                # Pad-Whitespace links und rechts mitkonsumieren
                left = len(result_chars)
                while result_chars and result_chars[-1] == " ":
                    result_chars.pop()
                j = i + 1
                while j < len(para) and para[j] == " ":
                    j += 1
                before_excerpt = "".join(result_chars[max(0, left - 20) : left])
                if strategy == "period":
                    result_chars.append(".")
                    result_chars.append(" ")
                    rest = para[j:]
                    if rest and rest[0].islower():
                        rest = rest[0].upper() + rest[1:]
                    result_chars.extend(rest)
                    i = len(para)
                else:  # comma
                    result_chars.append(",")
                    result_chars.append(" ")
                    i = j
                changes.append(
                    {
                        "rule": "em_dashes",
                        "before": before_excerpt + EM_DASH,
                        "after": before_excerpt + ("," if strategy != "period" else "."),
                        "reason": "em_dash_overuse",
                    }
                )
                replaced += 1
                continue
        result_chars.append(ch)
        i += 1

    return "".join(result_chars), changes
