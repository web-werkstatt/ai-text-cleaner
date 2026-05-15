import json
from pathlib import Path

from ai_text_cleaner import Mode, clean_text
from ai_text_cleaner.io.bm_json_loader import (
    iter_text_blocks,
    load_bm_json,
    save_bm_json,
    set_block_text,
)

FIXTURE = Path(__file__).parent / "fixtures" / "example_bm_draft.json"


def test_iter_text_blocks_skipt_code_und_image():
    data = load_bm_json(FIXTURE)
    blocks = list(iter_text_blocks(data))
    texts = [t for _, _, t in blocks]
    # code-Block bleibt geschützt, image-Block bleibt geschützt (alt enthält Floskel, wird ignoriert)
    assert all("def revolutioniere" not in t for t in texts)
    assert all(not t.startswith("https://") for t in texts)


def test_bm_json_roundtrip_struktur_bleibt(tmp_path):
    data = load_bm_json(FIXTURE)
    block_count = len(data["blocks"])
    block_types = [b["type"] for b in data["blocks"]]

    for idx, field_path, text in list(iter_text_blocks(data)):
        result = clean_text(text, mode=Mode.RULES_ONLY)
        set_block_text(data, idx, field_path, result.text)

    out = tmp_path / "out.json"
    save_bm_json(out, data)
    reloaded = json.loads(out.read_text(encoding="utf-8"))

    assert len(reloaded["blocks"]) == block_count
    assert [b["type"] for b in reloaded["blocks"]] == block_types
    # Code-Block ist unverändert
    code_block = next(b for b in reloaded["blocks"] if b["type"] == "code")
    assert "revolutioniere" in code_block["text"]
    # Image-URL bleibt
    image_block = next(b for b in reloaded["blocks"] if b["type"] == "image")
    assert image_block["url"] == "https://example.com/a.png"


def test_bm_json_floskeln_entfernt():
    data = load_bm_json(FIXTURE)
    for idx, field_path, text in list(iter_text_blocks(data)):
        result = clean_text(text, mode=Mode.RULES_ONLY)
        set_block_text(data, idx, field_path, result.text)
    para = data["blocks"][1]["text"]
    assert "In der heutigen Zeit" not in para
    assert "Darüber hinaus" not in para
