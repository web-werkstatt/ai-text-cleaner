"""Feature → Prompt-Hint-Mapping für verschärften Tier-2-Polish.

Top-Features aus dem Klassifikator werden in natürlich-sprachige Anweisungen
an das LLM übersetzt. Mapping kann erweitert werden, sobald 25b mit echtem
Korpus läuft und klar ist, welche Features in der Praxis dominieren.
"""

from __future__ import annotations

FEATURE_HINTS: dict[str, str] = {
    # Satz-/Wort-Statistik
    "stdev_sentence_length": "Erhöhe die Varianz der Satzlängen drastisch: mische 3–6-Wort-Sätze mit Sätzen von 18+ Wörtern.",
    "variance_ratio": "Variiere Satzlängen stärker — gleichförmige Längen sind ein KI-Signal.",
    "mean_sentence_length": "Bring die mittlere Satzlänge in einen menschlicheren Bereich (12–18 Wörter).",
    "type_token_ratio": "Erhöhe die lexikalische Vielfalt — vermeide Wort-Wiederholungen, nutze Synonyme.",
    "repetition_rate": "Reduziere wiederkehrende Wörter, ersetze sie durch Synonyme oder paraphrasiere.",
    "trigram_unique_ratio": "Vermeide phraseologische Wiederholungen — verschiedene Trigrame statt Formelhaftigkeit.",
    "bigram_top10_concentration": "Mische Formulierungen stärker — vermeide, dass wenige Phrasen den Text dominieren.",
    "avg_word_length": "Variiere die Wortlängen — wechsle bewusst zwischen kurzen und langen Wörtern.",
    # Interpunktion
    "em_dash_per_1000_words": "Entferne alle Em-Dashes (—) und ersetze sie durch Komma oder Punkt.",
    "em_dash_count": "Reduziere Em-Dashes deutlich — bei Bedarf Komma oder Punkt.",
    "em_dash_per_paragraph": "Maximal ein Em-Dash pro Absatz, besser keiner.",
    "en_dash_per_1000_words": "Reduziere En-Dashes auf Zahlenbereiche; in Fließtext eher Komma.",
    "colon_per_1000_words": "Reduziere Doppelpunkte — gleichmäßiger Einsatz wirkt KI-haft.",
    "typographic_quote_ratio": "Mische Anführungszeichen-Stile menschlicher — nicht systematisch typografisch.",
    "bracket_per_1000_words": "Reduziere Klammern — viele Einschübe wirken KI-strukturiert.",
    # POS / Syntax
    "pos_noun_ratio": "Reduziere Substantiv-Häufigkeit zugunsten konkreter Verben.",
    "pos_verb_ratio": "Nutze aktive, konkrete Verben statt blasser Hilfsverb-Konstruktionen.",
    "pos_adj_ratio": "Reduziere Adjektive — KI-Texte sind oft adjektiv-überladen.",
    "adj_noun_ratio": "Weniger Adjektive vor Substantiven — knappere Nominalphrasen.",
    "pos_adv_ratio": "Reduziere Adverbien wie 'wirklich', 'wahrlich', 'durchaus'.",
    "pos_pron_ratio": "Variiere Pronomen-Einsatz — nicht jeder Satz mit 'es' oder 'das' beginnen.",
    "pos_conj_ratio": "Weniger Konjunktionen — kurze, eigenständige Sätze statt Schachtelung.",
    "mean_subordination_depth": "Brich tiefe Schachtelsätze in zwei oder drei kurze Sätze auf.",
    # Struktur
    "paragraph_count": "Variiere die Absatzstruktur — nicht alle Absätze gleich lang.",
    "mean_paragraph_length": "Variiere die Absatzlänge stärker — kurze und lange Absätze mischen.",
}

DEFAULT_HINT = "Reduziere KI-typische Muster im Text."


def build_prompt_hints(
    top_features: list[tuple[str, float]],
    *,
    top_n: int = 3,
) -> list[str]:
    """Aus Top-Features konkrete LLM-Anweisungen ableiten.

    Liefert maximal `top_n` Hinweise, Dubletten werden entfernt.
    Unbekannte Features führen zu keinem Hinweis (kein Default-Spam).
    """
    hints: list[str] = []
    seen: set[str] = set()
    for name, _ in top_features:
        hint = FEATURE_HINTS.get(name)
        if hint is None or hint in seen:
            continue
        hints.append(hint)
        seen.add(hint)
        if len(hints) >= top_n:
            break
    return hints


def format_for_prompt(hints: list[str]) -> str:
    """Renderbare System-Prompt-Erweiterung. Leerer Hint-List → leerer String."""
    if not hints:
        return ""
    lines = ["Zusätzliche Hinweise aus der Stilanalyse (priorisiert):"]
    for i, hint in enumerate(hints, 1):
        lines.append(f"{i}. {hint}")
    return "\n".join(lines)


__all__ = ["DEFAULT_HINT", "FEATURE_HINTS", "build_prompt_hints", "format_for_prompt"]
