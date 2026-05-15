"""CLI: gespeichertes Modell + Test-CSV → Markdown-Report."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from ai_text_cleaner.classifier import evaluate, load_classifier, report_markdown
from ai_text_cleaner.classifier.persistence import DEFAULT_MODEL_PATH
from ai_text_cleaner.features.schema import FEATURE_NAMES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluiere Klassifikator auf Test-CSV.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--test-set", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args(argv)

    if not args.test_set.exists():
        print(f"Test-Set fehlt: {args.test_set}", file=sys.stderr)
        return 2

    bundle = load_classifier(args.model)

    y_true: list[int] = []
    X_rows: list[list[float]] = []
    with args.test_set.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            label = row.get("label", "")
            if label not in {"human", "ai"}:
                continue
            y_true.append(1 if label == "ai" else 0)
            X_rows.append([float(row.get(name, 0.0) or 0.0) for name in FEATURE_NAMES])

    if not X_rows:
        print(f"Keine human/ai-Zeilen in {args.test_set}", file=sys.stderr)
        return 1

    scaled = bundle.scaler.transform(X_rows)
    y_score = [float(p) for p in bundle.estimator.predict_proba(scaled)[:, 1]]

    report = evaluate(y_true, y_score, threshold=args.threshold)
    markdown = report_markdown(report)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Report geschrieben: {args.output}")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
