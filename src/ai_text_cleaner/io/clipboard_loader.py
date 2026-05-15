"""Clipboard-Loader (lazy import — optional dependency)."""

from __future__ import annotations


class ClipboardUnavailable(RuntimeError):
    """pyperclip nicht installiert oder OS bietet kein Clipboard."""


def _get_pyperclip():
    try:
        import pyperclip  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ClipboardUnavailable(
            "pyperclip nicht installiert. `pip install ai-text-cleaner[clipboard]`"
        ) from exc
    return pyperclip


def read_clipboard() -> str:
    pyperclip = _get_pyperclip()
    try:
        return pyperclip.paste()
    except Exception as exc:
        raise ClipboardUnavailable(f"Clipboard-Zugriff fehlgeschlagen: {exc}") from exc


def write_clipboard(text: str) -> None:
    pyperclip = _get_pyperclip()
    try:
        pyperclip.copy(text)
    except Exception as exc:
        raise ClipboardUnavailable(f"Clipboard-Zugriff fehlgeschlagen: {exc}") from exc
