from ai_text_cleaner import Mode, clean_text


def test_generische_intros_entfernt():
    text = "In der heutigen Zeit ist Python beliebt. Es ist allgemein bekannt, dass die Sprache 1991 entstand."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert "In der heutigen Zeit" not in result.text
    assert "Es ist allgemein bekannt" not in result.text


def test_connector_phrases():
    text = "Darüber hinaus testen wir. Es ist wichtig zu beachten, dass Tests grün sein müssen."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert "Darüber hinaus" not in result.text
    assert "Es ist wichtig zu beachten" not in result.text


def test_buzzword_verben():
    text = "Wir revolutionieren die Branche und optimieren Prozesse."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert "revolutionieren" not in result.text
    assert "optimieren" not in result.text


def test_headlines_geglaettet():
    text = "# Die ultimative Anleitung zu Python\n\nLos geht's."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert "ultimative" not in result.text
    assert result.text.startswith("# Anleitung zu Python") or result.text.startswith("# Anleitung")


def test_changes_tracked():
    text = "In der heutigen Zeit revolutioniert KI alles."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert len(result.changes) >= 2
    rules = {c["rule"] for c in result.changes}
    assert "floskeln" in rules


def test_capitalize_sentence_starts():
    text = "Es ist allgemein bekannt, dass python toll ist. wir mögen das."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert result.text[0].isupper() or result.text.lstrip()[0].isupper()
