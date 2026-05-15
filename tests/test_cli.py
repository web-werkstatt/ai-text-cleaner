import json
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def _run(args, input_text: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "ai_text_cleaner.cli", *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_rules_only_stdin():
    res = _run(["-", "--rules-only"], input_text="In der heutigen Zeit revolutioniert KI alles.")
    assert res.returncode == 0
    assert "In der heutigen Zeit" not in res.stdout
    assert "revolutioniert" not in res.stdout


def test_cli_report_markdown(tmp_path):
    src = tmp_path / "x.md"
    src.write_text("In der heutigen Zeit revolutioniert KI alles.", encoding="utf-8")
    res = _run([str(src), "--report"])
    assert res.returncode == 0
    assert "Cleaner-Report" in res.stdout
    assert "floskeln" in res.stdout or "buzzword" in res.stdout


def test_cli_report_json(tmp_path):
    src = tmp_path / "x.md"
    src.write_text("In der heutigen Zeit revolutioniert KI alles.", encoding="utf-8")
    res = _run([str(src), "--report", "--json-report"])
    assert res.returncode == 0
    payload = json.loads(res.stdout)
    assert payload["total_changes"] > 0
    assert "by_rule" in payload


def test_cli_file_rewrite(tmp_path):
    src = tmp_path / "artikel.md"
    src.write_text("In der heutigen Zeit revolutioniert KI alles.", encoding="utf-8")
    out = tmp_path / "out.md"
    res = _run([str(src), "--rules-only", "-o", str(out)])
    assert res.returncode == 0, res.stderr
    cleaned = out.read_text(encoding="utf-8")
    assert "In der heutigen Zeit" not in cleaned


def test_cli_bm_json(tmp_path):
    src = FIXTURES / "example_bm_draft.json"
    out = tmp_path / "out.json"
    res = _run([str(src), "--rules-only", "--format", "bm-json", "-o", str(out)])
    assert res.returncode == 0, res.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    # Code-Block bleibt
    code = next(b for b in data["blocks"] if b["type"] == "code")
    assert "revolutioniere" in code["text"]
    # Paragraph hat Floskel entfernt
    para = data["blocks"][1]["text"]
    assert "In der heutigen Zeit" not in para
