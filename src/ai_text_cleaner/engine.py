"""Orchestrierung: Tier 1 (Rules) + Tier 2 (LLM-Polish)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from .llm.polish import DEFAULT_MODEL, LLMUnavailable, polish_with_llm
from .report import CleanReport
from .rules import (
    analyze_sentence_lengths,
    apply_buzzwords,
    apply_em_dashes,
    apply_floskeln,
    apply_headlines,
    apply_whitespace,
    count_em_dashes,
)

log = logging.getLogger(__name__)

DEFAULT_PATTERNS = Path(__file__).parent / "patterns.de.yaml"


class Mode(str, Enum):
    RULES_ONLY = "rules_only"
    HYBRID = "hybrid"
    LLM_ONLY = "llm_only"


@dataclass
class CleanResult:
    text: str
    report: CleanReport = field(default_factory=CleanReport)
    changes: list[dict] = field(default_factory=list)
    llm_used: bool = False
    fallback_reason: str | None = None


def _load_patterns(path: str | Path | None = None) -> dict:
    p = Path(path) if path else DEFAULT_PATTERNS
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def _run_rules(
    text: str,
    patterns: dict,
    enabled_rules: set[str] | None,
) -> tuple[str, list[dict]]:
    changes: list[dict] = []
    out = text

    def _enabled(name: str) -> bool:
        return enabled_rules is None or name in enabled_rules

    if _enabled("whitespace"):
        out, c = apply_whitespace(out)
        changes.extend(c)

    if _enabled("headlines"):
        out, c = apply_headlines(out, patterns.get("headline_softeners", []))
        changes.extend(c)

    if _enabled("floskeln"):
        merged = patterns.get("generic_intros", []) + patterns.get("connector_phrases", [])
        out, c = apply_floskeln(out, merged)
        changes.extend(c)

    if _enabled("buzzwords"):
        out, c = apply_buzzwords(out, patterns.get("buzzword_verbs", []))
        changes.extend(c)

    if _enabled("em_dashes"):
        em_cfg = patterns.get("em_dashes", {})
        out, c = apply_em_dashes(
            out,
            max_per_paragraph=em_cfg.get("max_per_paragraph", 1),
            strategy=em_cfg.get("replacement_strategy", "comma"),
        )
        changes.extend(c)

    return out, changes


def clean_text(
    text: str,
    *,
    mode: Mode = Mode.HYBRID,
    aggressive: bool = False,
    enabled_rules: list[str] | None = None,
    llm_model: str = DEFAULT_MODEL,
    llm_api_key: str | None = None,
    patterns_path: str | Path | None = None,
    llm_client: Any | None = None,
) -> CleanResult:
    """Reinigt einen Text. Tier 1 → Tier 2 abhängig von `mode`.

    Bei fehlendem API-Key oder fehlendem `anthropic`-Paket wird der LLM-Schritt
    übersprungen und das Ergebnis von Tier 1 zurückgegeben (mit `fallback_reason`).
    """
    patterns = _load_patterns(patterns_path)
    rules_set = set(enabled_rules) if enabled_rules else None
    em_before = count_em_dashes(text)

    rules_changes: list[dict] = []
    intermediate = text

    if mode in (Mode.RULES_ONLY, Mode.HYBRID):
        intermediate, rules_changes = _run_rules(text, patterns, rules_set)

    llm_used = False
    fallback_reason: str | None = None
    llm_changes: list[dict] = []
    final_text = intermediate

    if mode in (Mode.HYBRID, Mode.LLM_ONLY):
        source_for_llm = intermediate if mode == Mode.HYBRID else text
        try:
            response = polish_with_llm(
                source_for_llm,
                model=llm_model,
                api_key=llm_api_key,
                aggressive=aggressive,
                client=llm_client,
            )
            final_text = response.cleaned_text
            llm_changes = [c.model_dump() for c in response.changes]
            for c in llm_changes:
                c.setdefault("rule", "llm")
                c.setdefault("reason", "llm_rewrite")
            llm_used = True
        except LLMUnavailable as exc:
            fallback_reason = str(exc)
            log.warning("LLM-Polish übersprungen: %s", exc)
            if mode == Mode.LLM_ONLY:
                final_text = text

    em_after = count_em_dashes(final_text)
    all_changes = rules_changes + llm_changes
    sentence_stats = analyze_sentence_lengths(final_text)

    report = CleanReport(
        changes=all_changes,
        sentence_stats=sentence_stats,
        em_dash_count_before=em_before,
        em_dash_count_after=em_after,
        llm_used=llm_used,
        fallback_reason=fallback_reason,
        iterations=1,
    )

    return CleanResult(
        text=final_text,
        report=report,
        changes=all_changes,
        llm_used=llm_used,
        fallback_reason=fallback_reason,
    )


def analyze_text(
    text: str,
    *,
    patterns_path: str | Path | None = None,
) -> CleanReport:
    """Reine Analyse: Tier 1 trocken anwenden, keine Änderung am Originaltext."""
    patterns = _load_patterns(patterns_path)
    _, changes = _run_rules(text, patterns, enabled_rules=None)
    em_before = count_em_dashes(text)
    sentence_stats = analyze_sentence_lengths(text)
    return CleanReport(
        changes=changes,
        sentence_stats=sentence_stats,
        em_dash_count_before=em_before,
        em_dash_count_after=em_before,
        llm_used=False,
        fallback_reason=None,
        iterations=0,
    )
