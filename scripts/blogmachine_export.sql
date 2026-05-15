-- Korpus-Export aus Blog-Machine-DB ohne Python.
--
-- Verwendung:
--   psql postgresql://user:pass@localhost:5434/blogmachine \
--        -f scripts/blogmachine_export.sql \
--        -o /tmp/draft_pairs.tsv
--
-- Format: TSV (tab-separated) mit Spalten
--   session_id  ai_version  human_version  ai_provider  ai_markdown  human_markdown
--
-- Danach kann ein einfacher Python-Einzeiler die Texte in Dateien aufteilen, ohne
-- dass psycopg installiert sein muss. Beispiel siehe corpus/README.md.

\set ON_ERROR_STOP on
\pset format unaligned
\pset fieldsep '\t'
\pset tuples_only on
\pset pager off

WITH ai_versions AS (
    SELECT DISTINCT ON (session_id)
        session_id,
        version_number AS ai_version,
        source_provider AS ai_provider,
        markdown AS ai_markdown
    FROM draft_version
    WHERE version_number = 1
      AND source_provider IS NOT NULL
      AND lower(source_provider) ~ '^(claude|anthropic|openai|gpt|gemini)'
      AND session_id IS NOT NULL
    ORDER BY session_id, version_number ASC
),
human_versions AS (
    SELECT DISTINCT ON (session_id)
        session_id,
        version_number AS human_version,
        markdown AS human_markdown
    FROM draft_version
    WHERE session_id IS NOT NULL
      AND version_number > 1
    ORDER BY session_id,
        CASE WHEN status = 'published' THEN 0 ELSE 1 END,
        version_number DESC
)
SELECT
    a.session_id::text,
    a.ai_version,
    h.human_version,
    a.ai_provider,
    replace(replace(a.ai_markdown, E'\t', ' '), E'\n', E'\\n'),
    replace(replace(h.human_markdown, E'\t', ' '), E'\n', E'\\n')
FROM ai_versions a
JOIN human_versions h ON a.session_id = h.session_id
WHERE length(a.ai_markdown) > 800
  AND length(h.human_markdown) > 800
  AND a.ai_markdown != h.human_markdown;
