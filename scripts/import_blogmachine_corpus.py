"""Korpus-Akquise aus Blog-Machine-DB.

Extrahiert pro Draft-Session zwei Texte:
- `version=1` mit `source_provider IN (claude, anthropic, openai, gpt-*)` → label=ai
- höchste Version (oder `status='published'`) → label=human

Voraussetzung:
    pip install 'ai-text-cleaner[corpus]'

Beispiel:
    python scripts/import_blogmachine_corpus.py \\
        --db-url postgresql://user:pass@localhost:5434/blogmachine \\
        --output corpus/raw \\
        --min-words 200

Filter:
- Skip wenn nur 1 Version existiert (kein Edit-Signal)
- Skip wenn v1 und vN inhaltlich identisch sind (User hat nichts geändert)
- Skip wenn Text unter `--min-words` Wörter hat nach Markdown-Stripping
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai_text_cleaner.corpus_utils import strip_markdown, word_count

AI_PROVIDERS = {"claude", "anthropic", "openai", "gpt", "gemini"}


@dataclass
class DraftPair:
    session_id: str
    ai_text: str
    human_text: str
    ai_provider: str
    ai_version: int
    human_version: int


def _is_ai_provider(provider: str | None) -> bool:
    if not provider:
        return False
    p = provider.lower()
    return any(p.startswith(prefix) for prefix in AI_PROVIDERS)


def fetch_pairs(db_url: str, min_words: int) -> list[DraftPair]:
    """Holt Draft-Paare aus der DB. Erfordert psycopg ([corpus]-Extra)."""
    try:
        import psycopg  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit(
            "psycopg fehlt. Installiere: pip install 'ai-text-cleaner[corpus]'"
        ) from exc

    query = """
        SELECT
            session_id::text,
            version_number,
            status,
            source_provider,
            markdown
        FROM draft_version
        WHERE session_id IS NOT NULL
          AND markdown IS NOT NULL
          AND length(markdown) > 0
        ORDER BY session_id, version_number ASC
    """

    pairs: list[DraftPair] = []
    grouped: dict[str, list[dict[str, Any]]] = {}

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            for row in cur:
                session_id, version, status, provider, markdown = row
                grouped.setdefault(session_id, []).append(
                    {
                        "version": version,
                        "status": status,
                        "provider": provider,
                        "markdown": markdown,
                    }
                )

    for session_id, versions in grouped.items():
        if len(versions) < 2:
            continue

        ai_candidates = [
            v for v in versions
            if v["version"] == 1 and _is_ai_provider(v["provider"])
        ]
        if not ai_candidates:
            continue
        ai_v = ai_candidates[0]

        human_candidates = [v for v in versions if v["status"] == "published"]
        if not human_candidates:
            human_v = max(versions, key=lambda v: v["version"])
        else:
            human_v = max(human_candidates, key=lambda v: v["version"])

        if human_v["version"] == ai_v["version"]:
            continue

        ai_plain = strip_markdown(ai_v["markdown"])
        human_plain = strip_markdown(human_v["markdown"])

        if ai_plain == human_plain:
            continue
        if word_count(ai_plain) < min_words or word_count(human_plain) < min_words:
            continue

        pairs.append(
            DraftPair(
                session_id=session_id,
                ai_text=ai_plain,
                human_text=human_plain,
                ai_provider=str(ai_v["provider"] or "unknown"),
                ai_version=int(ai_v["version"]),
                human_version=int(human_v["version"]),
            )
        )

    return pairs


def write_pairs(pairs: list[DraftPair], output_dir: Path, *, dry_run: bool = False) -> None:
    ai_dir = output_dir / "ai"
    human_dir = output_dir / "human"

    if not dry_run:
        ai_dir.mkdir(parents=True, exist_ok=True)
        human_dir.mkdir(parents=True, exist_ok=True)

    for pair in pairs:
        short_id = hashlib.sha1(
            pair.session_id.encode("utf-8"), usedforsecurity=False
        ).hexdigest()[:10]
        ai_file = ai_dir / f"bm-{short_id}-v{pair.ai_version}.txt"
        human_file = human_dir / f"bm-{short_id}-v{pair.human_version}.txt"

        if dry_run:
            print(f"[dry-run] {ai_file.name} ({word_count(pair.ai_text)} W)")
            print(f"[dry-run] {human_file.name} ({word_count(pair.human_text)} W)")
            continue

        ai_file.write_text(pair.ai_text, encoding="utf-8")
        human_file.write_text(pair.human_text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--db-url",
        required=True,
        help="z. B. postgresql://user:pass@localhost:5434/blogmachine",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("corpus/raw"),
        help="Zielverzeichnis (Default: corpus/raw)",
    )
    parser.add_argument(
        "--min-words",
        type=int,
        default=200,
        help="Texte unter dieser Wörter-Anzahl werden übersprungen",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Zeige nur, was geschrieben würde, ohne Dateien anzulegen",
    )
    args = parser.parse_args(argv)

    print(f"Lade Draft-Paare aus {args.db_url} …")
    pairs = fetch_pairs(args.db_url, min_words=args.min_words)

    if not pairs:
        print("Keine geeigneten Draft-Paare gefunden.", file=sys.stderr)
        print("Erwartet wird mindestens eine Session mit AI-Version 1 + späterer Edit.", file=sys.stderr)
        return 1

    print(f"Gefundene Paare: {len(pairs)}")
    providers = sorted({p.ai_provider for p in pairs})
    print(f"AI-Provider:     {', '.join(providers)}")

    write_pairs(pairs, args.output, dry_run=args.dry_run)

    if args.dry_run:
        print("(dry-run — keine Dateien geschrieben)")
    else:
        print(f"Geschrieben nach: {args.output}/ai/  und  {args.output}/human/")
        print(f"Texte pro Klasse: {len(pairs)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
