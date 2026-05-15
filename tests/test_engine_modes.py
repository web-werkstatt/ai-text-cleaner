from types import SimpleNamespace

from ai_text_cleaner import Mode, analyze_text, clean_text


class MockMessages:
    def __init__(self, response_text: str):
        self.response_text = response_text
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(text=self.response_text)]
        )


class MockClient:
    def __init__(self, response_text: str):
        self.messages = MockMessages(response_text)


def test_rules_only_funktioniert_ohne_anthropic():
    text = "In der heutigen Zeit revolutioniert KI alles."
    result = clean_text(text, mode=Mode.RULES_ONLY)
    assert result.llm_used is False
    assert result.fallback_reason is None
    assert "In der heutigen Zeit" not in result.text


def test_hybrid_fallback_ohne_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    text = "In der heutigen Zeit revolutioniert KI alles."
    result = clean_text(text, mode=Mode.HYBRID)
    assert result.llm_used is False
    assert result.fallback_reason is not None
    # Rules wurden trotzdem angewendet
    assert "In der heutigen Zeit" not in result.text


def test_hybrid_mit_mock_client_nutzt_llm():
    response = '{"cleaned_text": "Heute prägt KI die Wirtschaft stark.", "changes": [{"before": "alles", "after": "die Wirtschaft", "reason": "präziser"}]}'
    client = MockClient(response)
    result = clean_text(
        "In der heutigen Zeit revolutioniert KI alles.",
        mode=Mode.HYBRID,
        llm_client=client,
    )
    assert result.llm_used is True
    assert result.fallback_reason is None
    assert result.text == "Heute prägt KI die Wirtschaft stark."
    assert len(client.messages.calls) == 1


def test_llm_only_uebersrpingt_rules():
    response = '{"cleaned_text": "Direkt vom LLM.", "changes": []}'
    client = MockClient(response)
    result = clean_text(
        "In der heutigen Zeit blabla.",
        mode=Mode.LLM_ONLY,
        llm_client=client,
    )
    assert result.text == "Direkt vom LLM."
    # In LLM_ONLY werden keine Rules-Changes erwartet
    rule_changes = [c for c in result.changes if c.get("rule") != "llm"]
    assert rule_changes == []


def test_llm_protection_zahlen_bleiben():
    response_text = '{"cleaned_text": "__PROTECTED_0__ Kunden in __PROTECTED_1__ Ländern.", "changes": []}'
    client = MockClient(response_text)
    result = clean_text(
        "1337 Kunden in 42 Ländern.",
        mode=Mode.LLM_ONLY,
        llm_client=client,
    )
    assert "1337" in result.text
    assert "42" in result.text


def test_analyze_text_aendert_nichts():
    text = "In der heutigen Zeit revolutioniert KI alles."
    report = analyze_text(text)
    assert report.iterations == 0
    assert len(report.changes) > 0
    # Originaltext bleibt unangetastet — analyze gibt nur Report zurück, nicht modifizierten Text
