# ai-text-cleaner

Regelbasierter + LLM-gestützter Cleaner für KI-typische Schreibmuster in **deutschen** Texten.

Erkennt und glättet z. B. Em-Dash-Overuse, Floskeln (`„In der heutigen Zeit"`, `„Darüber hinaus"`, `„Es ist wichtig zu beachten"`), generische Intros, Buzzword-Verben, generische Headlines und gleichförmige Satzlängen.

## Architektur

Zwei Stufen, optional kombinierbar:

- **Tier 1 — Rules** (stdlib + YAML, offline, gratis, deterministisch)
- **Tier 2 — LLM-Polish** (Anthropic Claude, Default `claude-haiku-4-5-20251001`, optional)

Geplant für v0.3.0: **Tier 3 — Adversarial-Eval-Loop** mit eigenem Klassifikator.

## Installation

```bash
pip install ai-text-cleaner                 # nur Rules
pip install ai-text-cleaner[llm]            # mit LLM-Polish
pip install ai-text-cleaner[llm,clipboard]  # voll
```

## CLI

```bash
ai-text-cleaner artikel.md                          # Default: Hybrid (Rules + LLM, falls Key vorhanden)
ai-text-cleaner artikel.md --rules-only             # nur Tier 1, offline
ai-text-cleaner artikel.md --llm-only               # nur Tier 2
ai-text-cleaner artikel.md -o out.md
ai-text-cleaner artikel.md --report                 # Analyse ohne Rewrite
ai-text-cleaner draft.json --format bm-json         # Blog-Machine-DraftVersion-JSON
cat artikel.md | ai-text-cleaner -                  # stdin → stdout
ai-text-cleaner --clipboard                         # liest + schreibt Clipboard
ai-text-cleaner artikel.md --rules em_dashes,floskeln
```

ENV: `ANTHROPIC_API_KEY` für die LLM-Stufe. Fehlt der Key → automatischer Rückfall auf `--rules-only` mit Warnung.

## Python-API

```python
from ai_text_cleaner import clean_text, analyze_text, Mode

result = clean_text(
    "In der heutigen Zeit revolutioniert KI die Branche — und das schnell — und tiefgreifend.",
    mode=Mode.HYBRID,
)
print(result.text)
print(result.report.markdown())
```

## Was wird erkannt?

- **Em-Dashes**: > 1 Em-Dash pro Absatz → Komma/Punkt
- **Floskeln**: `„In der heutigen Zeit"`, `„Darüber hinaus"`, `„Es ist wichtig zu beachten"`, `„Zusammenfassend lässt sich sagen"` u. a.
- **Buzzword-Verben**: `„revolutionieren"` → `„verändert"`, `„optimieren"` → `„verbessert"` (kontextabhängig)
- **Headlines**: `„Die ultimative/komplette/perfekte ..."` → neutralisiert
- **Whitespace**: NBSP, doppelte Leerzeichen, Mehrfach-Newlines
- **Satzlängen-Varianz**: Hinweis im Report (kein Auto-Rewrite in v1)

Erweiterung der Patterns via eigene YAML: `ai-text-cleaner artikel.md --patterns custom.yaml`.

## Grenzen

- **„100% KI-frei" ist technisch nicht garantierbar.** Selbst menschliche Texte werden von AI-Detectors mit ~5–15% Falsch-Positiv-Rate als „KI" klassifiziert. Das Tool senkt die Wahrscheinlichkeit deutlich, kann sie aber nicht eliminieren.
- v1 ist DE-fokussiert. EN-Patterns sind nicht im Scope.
- LLM-Stufe ist nicht-deterministisch — Output variiert bei wiederholtem Lauf.

## Tests

```bash
pip install -e ".[dev,llm,clipboard]"
pytest -v
```

## Lizenz

MIT
