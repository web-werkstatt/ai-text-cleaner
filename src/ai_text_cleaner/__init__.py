"""ai-text-cleaner — KI-Schreibmuster in deutschen Texten glätten."""

from .engine import CleanResult, Mode, analyze_text, clean_text
from .eval_loop import EvalConfig, EvalResult
from .report import CleanReport

__version__ = "0.1.0"

__all__ = [
    "CleanResult",
    "CleanReport",
    "EvalConfig",
    "EvalResult",
    "Mode",
    "analyze_text",
    "clean_text",
    "__version__",
]
