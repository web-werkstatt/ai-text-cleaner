"""ai-text-cleaner — KI-Schreibmuster in deutschen Texten glätten."""

from .engine import CleanResult, Mode, analyze_text, clean_text
from .report import CleanReport

__version__ = "0.1.0"

__all__ = [
    "CleanResult",
    "CleanReport",
    "Mode",
    "analyze_text",
    "clean_text",
    "__version__",
]
