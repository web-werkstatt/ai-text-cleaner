"""CLI: Korpus-Verzeichnis → Feature-CSV.

Beispiel:
    python scripts/extract_features.py \\
        --input corpus/raw/human --output corpus/features/human.csv \\
        --label human --use-pos
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from multiprocessing import Pool, cpu_count
from pathlib import Path

from ai_text_cleaner.features import CSV_HEADER, FeatureVector, extract_features


def _source_id(path: Path) -> str:
    return hashlib.sha1(path.name.encode("utf-8"), usedforsecurity=False).hexdigest()[:16]


def _process_one(args: tuple[Path, str, bool]) -> FeatureVector | None:
    path, label, use_pos = args
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if not text.strip():
        return None
    return extract_features(
        text,
        source_id=_source_id(path),
        label=label,
        use_pos=use_pos,
    )


def _load_existing_ids(csv_path: Path) -> set[str]:
    if not csv_path.exists():
        return set()
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return {row["source_id"] for row in reader if row.get("source_id")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extrahiere Features aus einem Text-Korpus.")
    parser.add_argument("--input", type=Path, required=True, help="Verzeichnis mit .txt-Dateien")
    parser.add_argument("--output", type=Path, required=True, help="Ziel-CSV-Pfad")
    parser.add_argument("--label", required=True, choices=["human", "ai"])
    parser.add_argument("--use-pos", action="store_true", help="spaCy-POS-Features einbeziehen")
    parser.add_argument("--workers", type=int, default=cpu_count(), help="Pool-Größe")
    parser.add_argument("--pattern", default="*.txt", help="Glob für Input-Dateien")
    args = parser.parse_args(argv)

    if not args.input.is_dir():
        print(f"Input-Verzeichnis existiert nicht: {args.input}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(args.input.glob(args.pattern))
    if not files:
        print(f"Keine Dateien in {args.input} (pattern={args.pattern})", file=sys.stderr)
        return 1

    existing_ids = _load_existing_ids(args.output)
    todo = [f for f in files if _source_id(f) not in existing_ids]
    if not todo:
        print(f"Nichts zu tun — alle {len(files)} Dateien bereits in {args.output}")
        return 0

    print(f"Verarbeite {len(todo)} Dateien (von {len(files)}) mit {args.workers} Workern …")

    new_file = not args.output.exists()
    with args.output.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(CSV_HEADER))
        if new_file:
            writer.writeheader()

        job_args = [(f, args.label, args.use_pos) for f in todo]
        with Pool(processes=max(1, args.workers)) as pool:
            done = 0
            for vec in pool.imap_unordered(_process_one, job_args, chunksize=8):
                done += 1
                if vec is None:
                    continue
                writer.writerow(vec.to_csv_row())
                if done % 50 == 0:
                    print(f"  … {done}/{len(todo)}")

    print(f"Fertig. Geschrieben nach {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
