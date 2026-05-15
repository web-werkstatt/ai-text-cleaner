"""Report-Generator: aggregierte Übersicht der gefundenen Patterns."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CleanReport:
    changes: list[dict] = field(default_factory=list)
    sentence_stats: dict | None = None
    em_dash_count_before: int = 0
    em_dash_count_after: int = 0
    llm_used: bool = False
    fallback_reason: str | None = None
    iterations: int = 0

    def by_rule(self) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for c in self.changes:
            counter[c.get("rule", "?")] += 1
        return dict(counter)

    def by_reason(self) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for c in self.changes:
            counter[c.get("reason", "?")] += 1
        return dict(counter)

    def markdown(self) -> str:
        lines: list[str] = []
        lines.append("# Cleaner-Report\n")
        lines.append(f"- Änderungen gesamt: **{len(self.changes)}**")
        lines.append(f"- Em-Dashes vorher / nachher: {self.em_dash_count_before} / {self.em_dash_count_after}")
        lines.append(f"- LLM-Stufe genutzt: {'ja' if self.llm_used else 'nein'}")
        if self.fallback_reason:
            lines.append(f"- Fallback-Grund: {self.fallback_reason}")
        if self.iterations:
            lines.append(f"- Iterationen: {self.iterations}")
        if self.sentence_stats:
            s = self.sentence_stats
            lines.append("")
            lines.append("## Satzlängen-Analyse")
            lines.append(f"- Sätze: {s['count']}")
            lines.append(f"- Mittlere Länge: {s['mean']} Wörter (σ={s['stdev']})")
            lines.append(f"- Min/Max: {s['min']} / {s['max']}")
            lines.append(f"- Varianz-Quotient: {s['variance_ratio']}")
            if s.get("warning"):
                lines.append(f"- ⚠️  {s['warning']}")
        by_rule = self.by_rule()
        if by_rule:
            lines.append("")
            lines.append("## Änderungen nach Regel")
            for rule, n in sorted(by_rule.items(), key=lambda kv: -kv[1]):
                lines.append(f"- `{rule}`: {n}")
        by_reason = self.by_reason()
        if by_reason:
            lines.append("")
            lines.append("## Änderungen nach Grund")
            for reason, n in sorted(by_reason.items(), key=lambda kv: -kv[1]):
                lines.append(f"- `{reason}`: {n}")
        if self.changes:
            lines.append("")
            lines.append("## Beispiele (max. 10)")
            for c in self.changes[:10]:
                before = (c.get("before") or "").replace("\n", " ⏎ ")[:80]
                after = (c.get("after") or "").replace("\n", " ⏎ ")[:80]
                lines.append(f"- `{c.get('rule', '?')}`: `{before}` → `{after}`")
        return "\n".join(lines) + "\n"

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_changes": len(self.changes),
            "em_dashes_before": self.em_dash_count_before,
            "em_dashes_after": self.em_dash_count_after,
            "llm_used": self.llm_used,
            "fallback_reason": self.fallback_reason,
            "iterations": self.iterations,
            "by_rule": self.by_rule(),
            "by_reason": self.by_reason(),
            "sentence_stats": self.sentence_stats,
            "changes": self.changes,
        }

    def json(self, indent: int = 2) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=indent)
