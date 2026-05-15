# Korpus — Akquise und Lizenzen

Dieses Verzeichnis enthält die Daten-Pipeline für den Tier-3-Klassifikator
(`ai-text-cleaner` v0.3.0, Sprint 25).

## Struktur

```
corpus/
├── README.md           # diese Datei
├── .gitignore          # raw/ wird nie committed
├── raw/                # Roh-Texte (lokal, nicht im Repo)
│   ├── human/
│   └── ai/
└── features/           # extrahierte Feature-CSVs (re-distributable)
    ├── human.csv
    └── ai.csv
```

## Lizenz-Note

Roh-Texte (`corpus/raw/`) werden **nicht** im öffentlichen Repo abgelegt.
Re-Distribution kommerzieller Blog-Texte ist juristisch eng. Im Repo
landen ausschließlich die extrahierten Feature-Zahlen
(`corpus/features/*.csv`), die als CC0 freigegeben werden — keine
Originaltexte, keine Substrings, keine Verlinkungen zu Volltext-Quellen.

## Quellen — menschlich

| Quelle | Lizenz | Anzahl Ziel | Akquise-Befehl |
|---|---|---|---|
| Eigene Blog-Posts vor 2022 | Owner-Recht | ~500 | manueller Export aus Blog Machine DB |
| Wikipedia DE (alte Versionen) | CC BY-SA | ~3000 | `wikiextractor` auf einem Dump-Snapshot |
| Common Crawl DE News | per Robots ok | ~1500 | `commoncrawl` Python-Bibliothek, Filter `lang=de` |

**Mindestziel:** 5000 menschliche Artikel.

## Quellen — KI

| Quelle | Modell | Anzahl Ziel | Akquise-Befehl |
|---|---|---|---|
| Blog Machine DB-Export | Claude 4.x | ~2000 | SQL-Export aus `draft_versions` mit Filter `model='claude-*'` |
| Synthetisch generiert | GPT-4 / Claude 3.5 / Gemini | ~2500 | `scripts/generate_ai_corpus.py` (kommt in 25b vor Training) |
| HuggingFace AI-Detect (DE) | gemischt | ~500 | `datasets.load_dataset('artem9k/ai-text-detection')` mit `lang=de`-Filter |

**Mindestziel:** 5000 KI-generierte Artikel.

## Feature-Extraktion

```bash
# Menschliche Texte
python scripts/extract_features.py \
  --input corpus/raw/human \
  --output corpus/features/human.csv \
  --label human \
  --use-pos

# KI-Texte
python scripts/extract_features.py \
  --input corpus/raw/ai \
  --output corpus/features/ai.csv \
  --label ai \
  --use-pos
```

Idempotent — bestehende Zeilen werden per `source_id`-Hash übersprungen.

## Stichprobe ansehen

```bash
python scripts/sample_corpus.py --input corpus/raw/human --n 20
```

## Reproduzierbarkeit

Jede Akquise-Operation muss in dieser README dokumentiert sein
(Datum, Größe, Quelle, Lizenz). So lässt sich der Korpus später
nachvollziehen, auch wenn die Roh-Daten nur lokal liegen.
