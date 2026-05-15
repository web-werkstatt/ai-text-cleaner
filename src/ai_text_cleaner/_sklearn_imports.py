"""Zentraler Ort für Lazy-Imports der optionalen `[ml]`-Dependencies.

Hier wird sichergestellt, dass v0.1.0-Nutzer ohne `pip install .[ml]` einen
klaren Fehler sehen statt eines kryptischen ImportError tief im Code.
"""

from __future__ import annotations

from typing import Any

_INSTALL_HINT = (
    "Das Tier-3-Modul (Classifier/Features) benötigt die optionale "
    "ML-Dependency. Installiere sie mit:\n"
    "    pip install 'ai-text-cleaner[ml]'\n"
    "und optional für POS-Features:\n"
    "    python -m spacy download de_core_news_sm"
)


class MLDependencyMissingError(ImportError):
    """ImportError mit Hinweis auf das `[ml]`-Extra."""

    def __init__(self, missing_module: str) -> None:
        super().__init__(
            f"{missing_module} ist nicht installiert.\n{_INSTALL_HINT}"
        )


def require_joblib() -> Any:
    try:
        import joblib  # type: ignore[import-not-found]
    except ImportError as exc:
        raise MLDependencyMissingError("joblib") from exc
    return joblib


def require_sklearn() -> Any:
    try:
        import sklearn  # type: ignore[import-not-found]
    except ImportError as exc:
        raise MLDependencyMissingError("scikit-learn") from exc
    return sklearn


__all__ = [
    "MLDependencyMissingError",
    "require_joblib",
    "require_sklearn",
]
