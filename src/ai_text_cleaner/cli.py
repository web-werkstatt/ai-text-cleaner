"""CLI-Entry-Point: `ai-text-cleaner`."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .engine import DEFAULT_MODEL, Mode, analyze_text, clean_text
from .io import (
    iter_text_blocks,
    load_bm_json,
    load_text,
    read_clipboard,
    read_stdin,
    save_bm_json,
    save_text,
    write_clipboard,
)
from .io.bm_json_loader import set_block_text
from .io.clipboard_loader import ClipboardUnavailable

log = logging.getLogger("ai_text_cleaner.cli")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ai-text-cleaner",
        description="Glättet KI-typische Schreibmuster in deutschen Texten.",
    )
    p.add_argument(
        "input",
        nargs="?",
        help="Pfad zur Datei. '-' liest stdin. Weglassen + --clipboard nutzt Zwischenablage.",
    )
    p.add_argument("-o", "--output", help="Ausgabepfad. Default: <input>.cleaned.<ext>")
    p.add_argument(
        "--format",
        choices=["auto", "text", "bm-json"],
        default="auto",
        help="Eingabe-Format. 'auto' rät anhand der Endung.",
    )

    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--rules-only", action="store_true", help="Nur Tier 1 (Rules).")
    mode.add_argument("--llm-only", action="store_true", help="Nur Tier 2 (LLM).")

    p.add_argument("--llm-model", default=DEFAULT_MODEL, help="Anthropic-Modell-ID.")
    p.add_argument("--aggressive", action="store_true", help="Aggressiverer LLM-Polish.")
    p.add_argument("--report", action="store_true", help="Nur Analyse, kein Rewrite.")
    p.add_argument("--json-report", action="store_true", help="Report als JSON statt Markdown.")
    p.add_argument("--rules", help="Komma-getrennte Rule-Whitelist (z. B. em_dashes,floskeln).")
    p.add_argument("--patterns", help="Eigene patterns.yaml laden.")
    p.add_argument("--clipboard", action="store_true", help="Liest+schreibt Clipboard.")
    p.add_argument("-q", "--quiet", action="store_true", help="Nur Output, keine Logs.")
    p.add_argument("-v", "--verbose", action="store_true", help="Mehr Logs.")
    return p


def _detect_mode(args: argparse.Namespace) -> Mode:
    if args.rules_only:
        return Mode.RULES_ONLY
    if args.llm_only:
        return Mode.LLM_ONLY
    return Mode.HYBRID


def _detect_format(path: str | None, override: str) -> str:
    if override != "auto":
        return override
    if not path or path == "-":
        return "text"
    suffix = Path(path).suffix.lower()
    if suffix in {".json", ".jsonb"}:
        return "bm-json"
    return "text"


def _default_output(input_path: str) -> str:
    p = Path(input_path)
    return str(p.with_suffix(f".cleaned{p.suffix}"))


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    level = logging.WARNING
    if args.verbose:
        level = logging.INFO
    if args.quiet:
        level = logging.ERROR
    logging.basicConfig(level=level, format="%(message)s")

    mode = _detect_mode(args)
    enabled_rules = [r.strip() for r in args.rules.split(",")] if args.rules else None

    # Input lesen
    source_text: str | None = None
    source_json: dict | None = None
    fmt = _detect_format(args.input, args.format)

    if args.clipboard:
        try:
            source_text = read_clipboard()
        except ClipboardUnavailable as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            return 2
    elif args.input == "-" or args.input is None:
        if args.input is None and not args.clipboard:
            parser.error("Bitte Input-Datei, '-' für stdin oder --clipboard angeben.")
        source_text = read_stdin()
        fmt = "text"
    else:
        if fmt == "bm-json":
            source_json = load_bm_json(args.input)
        else:
            source_text = load_text(args.input)

    # Report-Modus
    if args.report:
        if source_json is not None:
            combined = "\n\n".join(t for _, _, t in iter_text_blocks(source_json))
            report = analyze_text(combined, patterns_path=args.patterns)
        else:
            assert source_text is not None
            report = analyze_text(source_text, patterns_path=args.patterns)
        out = report.json() if args.json_report else report.markdown()
        print(out)
        return 0

    # Cleaning
    if source_json is not None:
        for idx, field_path, text in list(iter_text_blocks(source_json)):
            result = clean_text(
                text,
                mode=mode,
                aggressive=args.aggressive,
                enabled_rules=enabled_rules,
                llm_model=args.llm_model,
                patterns_path=args.patterns,
            )
            set_block_text(source_json, idx, field_path, result.text)

        out_path = args.output or _default_output(args.input)
        save_bm_json(out_path, source_json)
        log.info("BM-JSON gespeichert: %s", out_path)
        if not args.quiet:
            print(out_path)
        return 0

    assert source_text is not None
    result = clean_text(
        source_text,
        mode=mode,
        aggressive=args.aggressive,
        enabled_rules=enabled_rules,
        llm_model=args.llm_model,
        patterns_path=args.patterns,
    )

    if result.fallback_reason:
        log.warning("Hinweis: LLM-Stufe übersprungen — %s", result.fallback_reason)

    if args.clipboard:
        try:
            write_clipboard(result.text)
        except ClipboardUnavailable as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            return 2
        log.info("Clipboard aktualisiert (%d Änderungen).", len(result.changes))
        return 0

    if args.input == "-":
        sys.stdout.write(result.text)
        return 0

    out_path = args.output or _default_output(args.input)
    save_text(out_path, result.text)
    log.info("Gespeichert: %s (%d Änderungen)", out_path, len(result.changes))
    if not args.quiet:
        print(out_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
