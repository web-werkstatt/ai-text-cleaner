from ai_text_cleaner import Mode, clean_text
from ai_text_cleaner.rules.em_dashes import apply_em_dashes, count_em_dashes


def test_count_em_dashes():
    assert count_em_dashes("a — b — c") == 2
    assert count_em_dashes("a - b") == 0  # Hyphen ist kein Em-Dash


def test_einer_pro_absatz_erlaubt():
    text = "Das ist gut — wirklich gut."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert "—" in result.text
    em_changes = [c for c in result.changes if c["rule"] == "em_dashes"]
    assert em_changes == []


def test_uebermaessige_em_dashes_ersetzt():
    text = "Das ist gut — wirklich gut — und schnell — und billig."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert result.text.count("—") == 1
    em_changes = [c for c in result.changes if c["rule"] == "em_dashes"]
    assert len(em_changes) == 2


def test_pro_absatz_separat():
    text = "Erster Absatz — mit einem Em-Dash.\n\nZweiter Absatz — mit einem.\n\nDritter Absatz — auch okay."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert result.text.count("—") == 3


def test_apply_em_dashes_direct():
    text = "x — y — z"
    out, changes = apply_em_dashes(text, max_per_paragraph=1)
    assert out.count("—") == 1
    assert len(changes) == 1
