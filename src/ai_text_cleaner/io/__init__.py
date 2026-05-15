"""Input/Output-Loader für verschiedene Formate."""

from .text_loader import load_text, save_text
from .bm_json_loader import load_bm_json, save_bm_json, iter_text_blocks
from .stdin_loader import read_stdin
from .clipboard_loader import read_clipboard, write_clipboard

__all__ = [
    "load_text",
    "save_text",
    "load_bm_json",
    "save_bm_json",
    "iter_text_blocks",
    "read_stdin",
    "read_clipboard",
    "write_clipboard",
]
