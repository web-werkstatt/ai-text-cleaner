from ai_text_cleaner import Mode, clean_text


def test_doppelte_leerzeichen_entfernt():
    text = "Das  ist   ein  Test."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert "  " not in result.text


def test_nbsp_normalisiert():
    text = "Das ist ein Test."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert " " not in result.text


def test_dreifach_newline_zu_doppelt():
    text = "A\n\n\n\nB"
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert "\n\n\n" not in result.text


def test_trailing_whitespace_entfernt():
    text = "Zeile eins    \nZeile zwei"
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert "   \n" not in result.text
