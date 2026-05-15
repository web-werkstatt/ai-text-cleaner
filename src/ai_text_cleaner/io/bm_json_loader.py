"""Loader für Blog-Machine-DraftVersion.content_json.

Format (vereinfacht):
{
  "blocks": [
    {"type": "heading", "level": 1, "text": "..."},
    {"type": "paragraph", "text": "..."},
    {"type": "code", "lang": "python", "text": "..."},   # NICHT cleanen
    {"type": "list", "items": ["...", "..."]},
    {"type": "image", "alt": "...", "url": "..."},
    ...
  ]
}

`iter_text_blocks()` liefert (block_index, field_name, text) — der Aufrufer
schreibt das geänderte Text zurück über `set_block_text()`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

# Block-Typen, deren Text-Inhalt gecleaned wird.
CLEANABLE_TYPES = {"paragraph", "heading", "quote", "callout", "list", "list_item"}
# Block-Typen, die unverändert bleiben.
PROTECTED_TYPES = {"code", "image", "video", "embed", "table", "divider"}


def load_bm_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_bm_json(path: str | Path, data: dict) -> None:
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def iter_text_blocks(data: dict) -> Iterator[tuple[int, str, str]]:
    """Yieldet (block_index, field_path, text)."""
    blocks = data.get("blocks", [])
    for idx, block in enumerate(blocks):
        btype = block.get("type", "")
        if btype in PROTECTED_TYPES:
            continue
        if btype in CLEANABLE_TYPES or "text" in block:
            text = block.get("text")
            if isinstance(text, str) and text.strip():
                yield idx, "text", text
            items = block.get("items")
            if isinstance(items, list):
                for i, item in enumerate(items):
                    if isinstance(item, str) and item.strip():
                        yield idx, f"items[{i}]", item


def set_block_text(data: dict, block_index: int, field_path: str, new_text: str) -> None:
    block = data["blocks"][block_index]
    if field_path == "text":
        block["text"] = new_text
        return
    if field_path.startswith("items["):
        i = int(field_path[len("items[") : -1])
        block["items"][i] = new_text
        return
    raise ValueError(f"Unknown field path: {field_path}")
