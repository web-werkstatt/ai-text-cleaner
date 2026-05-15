"""POS-Features via spaCy `de_core_news_sm`.

Fällt sauber auf 0.0 zurück, wenn spaCy oder das Modell nicht verfügbar sind.
Aufrufer kann am `pos_available`-Flag im FeatureVector erkennen, ob die Werte
echt extrahiert oder Fallback sind.
"""

from __future__ import annotations

from typing import Any

from .schema import POS_FEATURES

_NLP: Any = None
_LOAD_ATTEMPTED = False
_LOAD_OK = False

_POS_KEYS: dict[str, str] = {
    "NOUN": "pos_noun_ratio",
    "PROPN": "pos_noun_ratio",  # Eigennamen zählen für NOUN-Anteil
    "VERB": "pos_verb_ratio",
    "AUX": "pos_verb_ratio",
    "ADJ": "pos_adj_ratio",
    "ADV": "pos_adv_ratio",
    "PRON": "pos_pron_ratio",
    "SCONJ": "pos_conj_ratio",
    "CCONJ": "pos_conj_ratio",
}


def _zero_features() -> dict[str, float]:
    return {name: 0.0 for name in POS_FEATURES}


def _load_spacy() -> Any | None:
    global _NLP, _LOAD_ATTEMPTED, _LOAD_OK
    if _LOAD_ATTEMPTED:
        return _NLP if _LOAD_OK else None
    _LOAD_ATTEMPTED = True
    try:
        import spacy  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        _NLP = spacy.load("de_core_news_sm", disable=["ner"])
        _LOAD_OK = True
        return _NLP
    except (OSError, ValueError):
        return None


def is_available() -> bool:
    """True, wenn spaCy + de_core_news_sm geladen werden konnten."""
    return _load_spacy() is not None


def extract_pos(text: str) -> tuple[dict[str, float], bool]:
    """Liefert (features, available). available=False → alle Werte sind 0.0."""
    nlp = _load_spacy()
    if nlp is None or not text.strip():
        return _zero_features(), False

    doc = nlp(text)
    counts: dict[str, int] = dict.fromkeys(POS_FEATURES, 0)
    total = 0
    subordination_depths: list[int] = []

    for token in doc:
        key = _POS_KEYS.get(token.pos_)
        if key is not None:
            counts[key] += 1
        total += 1
        if token.dep_ in {"cp", "sb", "oc", "re"}:
            depth = 0
            head = token.head
            seen = {token.i}
            while head is not None and head.i not in seen and head.head is not head:
                depth += 1
                seen.add(head.i)
                head = head.head
                if depth > 20:
                    break
            subordination_depths.append(depth)

    features = _zero_features()
    if total > 0:
        for name in POS_FEATURES:
            if name in counts:
                features[name] = counts[name] / total

    noun = features.get("pos_noun_ratio", 0.0)
    adj = features.get("pos_adj_ratio", 0.0)
    features["adj_noun_ratio"] = adj / noun if noun > 0 else 0.0

    features["mean_subordination_depth"] = (
        sum(subordination_depths) / len(subordination_depths)
        if subordination_depths
        else 0.0
    )

    return features, True


__all__ = ["extract_pos", "is_available"]
