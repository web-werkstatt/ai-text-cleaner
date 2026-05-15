"""Anthropic-Client-Wrapper für Tier 2.

Fehlt das `anthropic`-Paket oder der API-Key, wird LLMUnavailable geworfen —
der Engine-Aufrufer entscheidet dann, ob auf Rules-only zurückgefallen wird.
"""

from __future__ import annotations

import json
import logging
import os
import re

from .prompts import SYSTEM_PROMPT, build_user_prompt
from .protection import mask_protected, restore_protected
from .schema import CleanResponse

log = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 8192


class LLMUnavailable(RuntimeError):
    """LLM-Stufe nicht verfügbar (kein Paket, kein Key, oder API-Fehler)."""


def polish_with_llm(
    text: str,
    *,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    aggressive: bool = False,
    client: object | None = None,
) -> CleanResponse:
    """Sendet Text an Anthropic Claude, schützt Code/Zahlen/URLs.

    `client` kann für Tests ein Mock-Objekt sein (muss `.messages.create()` haben).
    """
    if client is None:
        client = _build_client(api_key)

    masked_text, originals = mask_protected(text)
    user_prompt = build_user_prompt(masked_text, aggressive=aggressive)

    try:
        response = client.messages.create(  # type: ignore[attr-defined]
            model=model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as exc:  # pragma: no cover — Live-Fehler werden gemapped
        raise LLMUnavailable(f"Anthropic API call failed: {exc}") from exc

    raw = _extract_text(response)
    payload = _parse_json(raw)

    cleaned = payload.get("cleaned_text", "")
    if not cleaned:
        raise LLMUnavailable("LLM returned empty cleaned_text")

    cleaned = restore_protected(cleaned, originals)

    return CleanResponse(
        cleaned_text=cleaned,
        changes=[
            {
                "before": restore_protected(c.get("before", ""), originals),
                "after": restore_protected(c.get("after", ""), originals),
                "reason": c.get("reason", ""),
            }
            for c in payload.get("changes", [])[:50]
        ],
    )


def _build_client(api_key: str | None):
    try:
        import anthropic  # type: ignore[import-not-found]
    except ImportError as exc:
        raise LLMUnavailable(
            "anthropic-Paket nicht installiert. `pip install ai-text-cleaner[llm]`"
        ) from exc

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise LLMUnavailable("Kein ANTHROPIC_API_KEY gesetzt.")
    return anthropic.Anthropic(api_key=key)


def _extract_text(response: object) -> str:
    """Extrahiert Text aus Anthropic-Response (kompatibel mit aktuellem SDK)."""
    content = getattr(response, "content", None)
    if content is None and isinstance(response, dict):
        content = response.get("content")
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            text = getattr(block, "text", None)
            if text is None and isinstance(block, dict):
                text = block.get("text")
            if text:
                parts.append(text)
        return "".join(parts)
    if isinstance(content, str):
        return content
    return str(response)


def _parse_json(raw: str) -> dict:
    """Findet das erste JSON-Objekt im Output."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise LLMUnavailable(f"LLM-Antwort war kein JSON: {raw[:200]!r}") from None
        return json.loads(match.group(0))
