from ai_text_cleaner.llm.protection import mask_protected, restore_protected


def test_code_block_maskiert():
    text = "Text vorher\n```python\ndef foo(): return 42\n```\nText nachher"
    masked, originals = mask_protected(text)
    assert "def foo" not in masked
    assert "__PROTECTED_" in masked
    restored = restore_protected(masked, originals)
    assert "def foo(): return 42" in restored


def test_inline_code_maskiert():
    text = "Nutze `clean_text()` für den Cleanup."
    masked, originals = mask_protected(text)
    assert "clean_text" not in masked
    assert restore_protected(masked, originals) == text


def test_urls_maskiert():
    text = "Siehe https://example.com/path?q=1 für Details."
    masked, originals = mask_protected(text)
    assert "https://example.com" not in masked
    assert "https://example.com/path?q=1" in restore_protected(masked, originals)


def test_zitate_maskiert():
    text = "Vorher\n> Das ist ein Zitat.\nNachher"
    masked, originals = mask_protected(text)
    assert "Das ist ein Zitat" not in masked
    restored = restore_protected(masked, originals)
    assert "Das ist ein Zitat" in restored


def test_zahlen_maskiert():
    text = "Wir haben 42 Kunden und 1337 Anfragen."
    masked, originals = mask_protected(text)
    assert "1337" not in masked
    restored = restore_protected(masked, originals)
    assert "42" in restored
    assert "1337" in restored


def test_restore_tolerant_bei_fehlenden_tokens():
    text = "Nur ein Wort"
    masked, originals = mask_protected(text)
    assert restore_protected(masked, originals) == text
