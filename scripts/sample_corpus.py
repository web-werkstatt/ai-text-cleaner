"""Hilfs-Script: Stichprobe ziehen und Korpus-Statistiken ausgeben."""

from __future__ import annotations

import argparse
import random
import statistics
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stichprobe ziehen + Längen-Statistik.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--n", type=int, default=20, help="Stichprobengröße")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--pattern", default="*.txt")
    args = parser.parse_args(argv)

    if not args.input.is_dir():
        print(f"Verzeichnis fehlt: {args.input}", file=sys.stderr)
        return 2

    files = sorted(args.input.glob(args.pattern))
    if not files:
        print(f"Keine Dateien in {args.input}", file=sys.stderr)
        return 1

    rng = random.Random(args.seed)
    sample = rng.sample(files, min(args.n, len(files)))

    lengths: list[int] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lengths.append(len(text.split()))

    print(f"Korpus:       {args.input}")
    print(f"Dateien:      {len(files)}")
    if lengths:
        print(f"Wörter total: {sum(lengths)}")
        print(f"  ø          {statistics.fmean(lengths):.0f}")
        print(f"  median     {statistics.median(lengths):.0f}")
        print(f"  min/max    {min(lengths)} / {max(lengths)}")

    print()
    print(f"Stichprobe ({len(sample)}):")
    for path in sample:
        print(f"  {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
