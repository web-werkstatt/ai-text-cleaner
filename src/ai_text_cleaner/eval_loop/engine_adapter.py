"""Engine ↔ Eval-Loop-Adapter.

Hält die ML-Imports raus aus `engine.py`. `engine.py` ruft nur
`run_hybrid_ml(...)` als Dispatch — alle Classifier-/LLM-Wiring liegt hier.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from ..llm.polish import LLMUnavailable, polish_with_llm
from ..report import CleanReport
from ..rules import count_em_dashes
from .config import EvalConfig
from .loop import PolishProvider, ScoreProvider, run_eval_loop

if TYPE_CHECKING:
    from ..engine import CleanResult

log = logging.getLogger(__name__)


def run_hybrid_ml(
    text: str,
    *,
    aggressive: bool,
    enabled_rules: list[str] | None,
    llm_model: str,
    llm_api_key: str | None,
    patterns_path: str | Path | None,
    llm_client: Any | None,
    eval_config: Any | None,
    score_provider: Any | None,
    polish_provider: Any | None,
) -> CleanResult:
    """Tier-1 Rules + Tier-3 iterativer Polish-Loop mit Classifier-Reward."""
    from ..engine import CleanResult, Mode, clean_text

    config = eval_config if eval_config is not None else EvalConfig()

    if score_provider is None:
        score_provider = _default_score_provider(config)
    if polish_provider is None:
        polish_provider = _default_polish_provider(
            llm_model=llm_model,
            llm_api_key=llm_api_key,
            llm_client=llm_client,
            base_aggressive=aggressive,
        )

    base = clean_text(
        text,
        mode=Mode.RULES_ONLY,
        enabled_rules=enabled_rules,
        patterns_path=patterns_path,
    )

    eval_result = run_eval_loop(
        base.text,
        config=config,
        score_provider=cast(ScoreProvider, score_provider),
        polish_provider=cast(PolishProvider, polish_provider),
    )

    report = CleanReport(
        changes=base.changes,
        sentence_stats=base.report.sentence_stats,
        em_dash_count_before=base.report.em_dash_count_before,
        em_dash_count_after=count_em_dashes(eval_result.text),
        llm_used=eval_result.iterations > 0,
        fallback_reason=None,
        iterations=eval_result.iterations,
        trajectory=eval_result.trajectory,
        stop_reason=eval_result.stop_reason,
    )

    return CleanResult(
        text=eval_result.text,
        report=report,
        changes=base.changes,
        llm_used=eval_result.iterations > 0,
        fallback_reason=None,
        trajectory=eval_result.trajectory,
        iterations=eval_result.iterations,
        stop_reason=eval_result.stop_reason,
    )


def _default_score_provider(config: EvalConfig) -> Any:
    """Lädt den Klassifikator aus dem Paket. Bei fehlendem [ml]-Extra
    wirft load_classifier MLDependencyMissingError mit Install-Anleitung."""
    from ..classifier import load_classifier, predict

    bundle = (
        load_classifier(config.classifier_path)
        if config.classifier_path
        else load_classifier()
    )

    def _score(text: str) -> tuple[float, list[tuple[str, float]]]:
        prediction = predict(text, bundle=bundle, use_pos=config.use_pos_features)
        return prediction.score, prediction.top_features

    return _score


def _default_polish_provider(
    *,
    llm_model: str,
    llm_api_key: str | None,
    llm_client: Any | None,
    base_aggressive: bool,
) -> Any:
    """Hints werden in EvalIteration geloggt, aber noch nicht an den LLM-Prompt
    durchgereicht — das kommt in 25d (CLI/Release), wenn polish_with_llm einen
    extra_hints-Parameter bekommt. Bis dahin steuert `aggressive`."""

    def _polish(text: str, *, hints: list[str], aggressive: bool) -> str:
        del hints
        try:
            response = polish_with_llm(
                text,
                model=llm_model,
                api_key=llm_api_key,
                aggressive=base_aggressive or aggressive,
                client=llm_client,
            )
            return response.cleaned_text
        except LLMUnavailable as exc:
            log.warning("LLM-Polish im Eval-Loop übersprungen: %s", exc)
            return text

    return _polish


__all__ = ["run_hybrid_ml"]
