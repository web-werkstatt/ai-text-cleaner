"""Tests für ai_text_cleaner/corpus_utils.py."""

from __future__ import annotations

from ai_text_cleaner.corpus_utils import strip_markdown, word_count


def test_strip_code_fences() -> None:
    md = "Vor dem Code.\n\n```python\nprint('hi')\n```\n\nNach dem Code."
    plain = strip_markdown(md)
    assert "print" not in plain
    assert "Vor dem Code" in plain
    assert "Nach dem Code" in plain


def test_strip_headings_keeps_text() -> None:
    md = "# Überschrift\n\nFließtext darunter."
    plain = strip_markdown(md)
    assert plain.startswith("Überschrift")
    assert "Fließtext darunter." in plain


def test_strip_links_keeps_anchor() -> None:
    md = "Siehe [Beispiel](https://example.com) für mehr."
    plain = strip_markdown(md)
    assert "Beispiel" in plain
    assert "example.com" not in plain


def test_strip_images_removed_completely() -> None:
    md = "Bild: ![Alt-Text](image.png) — Text danach."
    plain = strip_markdown(md)
    assert "image.png" not in plain
    assert "Alt-Text" not in plain
    assert "Text danach" in plain


def test_strip_bold_italic() -> None:
    md = "**Fett** und *kursiv* und __auch fett__ und _auch kursiv_."
    plain = strip_markdown(md)
    assert plain == "Fett und kursiv und auch fett und auch kursiv."


def test_strip_lists() -> None:
    md = "- Punkt eins\n- Punkt zwei\n\n1. Erster\n2. Zweiter"
    plain = strip_markdown(md)
    assert "Punkt eins" in plain
    assert "- " not in plain
    assert "1. " not in plain


def test_strip_blockquote() -> None:
    md = "> Ein Zitat\n> über mehrere Zeilen"
    plain = strip_markdown(md)
    assert "> " not in plain
    assert "Ein Zitat" in plain


def test_strip_frontmatter() -> None:
    md = "---\ntitle: Test\nauthor: Joseph\n---\n\nHaupttext beginnt hier."
    plain = strip_markdown(md)
    assert "title:" not in plain
    assert plain.startswith("Haupttext")


def test_em_dashes_preserved() -> None:
    md = "Text — mit Em-Dash — bleibt erhalten."
    plain = strip_markdown(md)
    assert plain.count("—") == 2


def test_collapses_multiple_blank_lines() -> None:
    md = "Absatz eins.\n\n\n\n\nAbsatz zwei."
    plain = strip_markdown(md)
    assert "\n\n\n" not in plain
    assert "Absatz eins." in plain
    assert "Absatz zwei." in plain


def test_word_count_basic() -> None:
    assert word_count("Hallo Welt.") == 2
    assert word_count("") == 0
    assert word_count("eins zwei drei vier fünf") == 5
    assert word_count("Mit Umlauten: schön, größer, fünfzehn.") == 5
