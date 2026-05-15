"""Feature-Extraktion für Tier-3 (Sprint 25a).

Public-API:
- `extract_features(text, source_id, label, use_pos=True) -> FeatureVector`
- `FEATURE_NAMES` — alphabetisch sortierte Spaltennamen (stabil für CSVs)
- `FeatureVector` — Pydantic-Modell mit CSV-Roundtrip
"""

from __future__ import annotations

from .basic import extract_basic
from .ngrams import extract_ngrams
from .pos import extract_pos, is_available as pos_available
from .punctuation import extract_punctuation
from .schema import (
    BASIC_FEATURES,
    CSV_HEADER,
    FEATURE_NAMES,
    FeatureVector,
    METADATA_COLUMNS,
    NGRAM_FEATURES,
    POS_FEATURES,
    PUNCTUATION_FEATURES,
)


def extract_features(
    text: str,
    *,
    source_id: str,
    label: str,
    use_pos: bool = True,
) -> FeatureVector:
    """Extrahiere alle Features für einen Text. Stabile Reihenfolge via FEATURE_NAMES.

    `use_pos=False` überspringt spaCy auch wenn verfügbar (für reproduzierbare
    Stdlib-only-Läufe).
    """
    features: dict[str, float] = {}
    features.update(extract_basic(text))
    features.update(extract_ngrams(text))
    features.update(extract_punctuation(text))

    available = False
    if use_pos:
        pos_features, available = extract_pos(text)
        features.update(pos_features)
    else:
        from .schema import POS_FEATURES as _POS_FEATURES
        features.update({name: 0.0 for name in _POS_FEATURES})

    return FeatureVector(
        source_id=source_id,
        label=label,
        pos_available=available,
        features=features,
    )


__all__ = [
    "BASIC_FEATURES",
    "CSV_HEADER",
    "FEATURE_NAMES",
    "FeatureVector",
    "METADATA_COLUMNS",
    "NGRAM_FEATURES",
    "POS_FEATURES",
    "PUNCTUATION_FEATURES",
    "extract_features",
    "pos_available",
]
