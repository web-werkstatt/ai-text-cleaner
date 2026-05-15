"""CLI: Feature-CSVs → trainiertes Modell.

Beispiel:
    python scripts/train_classifier.py \\
        --human corpus/features/human.csv \\
        --ai corpus/features/ai.csv \\
        --model-type logreg \\
        --output src/ai_text_cleaner/classifier/model.pkl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from ai_text_cleaner.classifier import save_classifier, train_classifier
from ai_text_cleaner.classifier.persistence import DEFAULT_MODEL_PATH


def _corpus_hash(*paths: Path) -> str:
    hasher = hashlib.sha256()
    for path in paths:
        if not path.exists():
            continue
        hasher.update(path.name.encode("utf-8"))
        hasher.update(str(path.stat().st_size).encode("utf-8"))
        hasher.update(str(int(path.stat().st_mtime)).encode("utf-8"))
    return hasher.hexdigest()[:16]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Trainiere Tier-3-Klassifikator.")
    parser.add_argument("--human", type=Path, required=True)
    parser.add_argument("--ai", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--model-type", choices=["logreg", "gbm"], default="logreg")
    parser.add_argument("--force", action="store_true", help="Re-Train auch bei identischem Korpus")
    args = parser.parse_args(argv)

    if not args.human.exists() or not args.ai.exists():
        print(f"CSVs fehlen: human={args.human}, ai={args.ai}", file=sys.stderr)
        return 2

    new_hash = _corpus_hash(args.human, args.ai)
    meta_path = args.output.with_suffix(".metadata.json")
    if not args.force and meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
            if existing.get("corpus_hash") == new_hash:
                print(f"Korpus unverändert (hash={new_hash}) — kein Re-Train. --force zum Erzwingen.")
                return 0
        except (OSError, json.JSONDecodeError):
            pass

    print(f"Training: model={args.model_type}, human={args.human.name}, ai={args.ai.name}")
    report = train_classifier(
        args.human, args.ai, model_type=args.model_type
    )
    report.bundle.metadata["corpus_hash"] = new_hash

    save_classifier(report.bundle, args.output)
    print(f"Modell gespeichert: {args.output}")
    print(f"Val-AUC: {report.val_metrics.auc:.4f}")
    print(f"Test-AUC: {report.test_metrics.auc:.4f}")
    print(f"Test-FPR (Human): {report.test_metrics.false_positive_rate_human:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
