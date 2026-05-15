"""Feature-Schema — stabile Schnittstelle zwischen 25a (Extraktion) und 25b (Training)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

BASIC_FEATURES: tuple[str, ...] = (
    "avg_word_length",
    "em_dash_count",
    "em_dash_per_paragraph",
    "mean_paragraph_length",
    "mean_sentence_length",
    "paragraph_count",
    "sentence_count",
    "stdev_sentence_length",
    "token_count",
    "type_token_ratio",
    "unique_token_count",
    "variance_ratio",
)

NGRAM_FEATURES: tuple[str, ...] = (
    "bigram_top10_concentration",
    "repetition_rate",
    "trigram_unique_ratio",
)

POS_FEATURES: tuple[str, ...] = (
    "adj_noun_ratio",
    "mean_subordination_depth",
    "pos_adj_ratio",
    "pos_adv_ratio",
    "pos_conj_ratio",
    "pos_noun_ratio",
    "pos_pron_ratio",
    "pos_verb_ratio",
)

PUNCTUATION_FEATURES: tuple[str, ...] = (
    "bracket_per_1000_words",
    "colon_per_1000_words",
    "em_dash_per_1000_words",
    "en_dash_per_1000_words",
    "typographic_quote_ratio",
)

FEATURE_NAMES: tuple[str, ...] = tuple(
    sorted(BASIC_FEATURES + NGRAM_FEATURES + POS_FEATURES + PUNCTUATION_FEATURES)
)

METADATA_COLUMNS: tuple[str, ...] = ("source_id", "label", "pos_available")

CSV_HEADER: tuple[str, ...] = METADATA_COLUMNS + FEATURE_NAMES


class FeatureVector(BaseModel):
    """Ein extrahierter Feature-Vektor für einen Text.

    `pos_available=False` signalisiert, dass spaCy nicht verfügbar war und
    POS-Features auf 0.0 zurückgefallen sind.
    """

    source_id: str = Field(..., description="Stabile ID des Texts (Hash oder Datei-Name).")
    label: str = Field(..., description="'human' oder 'ai' — kommt aus der Akquise-Pipeline.")
    pos_available: bool = Field(default=True)
    features: dict[str, float] = Field(default_factory=dict)

    def to_csv_row(self) -> dict[str, Any]:
        row: dict[str, Any] = {
            "source_id": self.source_id,
            "label": self.label,
            "pos_available": int(self.pos_available),
        }
        for name in FEATURE_NAMES:
            row[name] = float(self.features.get(name, 0.0))
        return row

    @classmethod
    def from_csv_row(cls, row: dict[str, Any]) -> FeatureVector:
        features = {name: float(row.get(name, 0.0) or 0.0) for name in FEATURE_NAMES}
        return cls(
            source_id=str(row["source_id"]),
            label=str(row["label"]),
            pos_available=bool(int(row.get("pos_available", 1))),
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
]
