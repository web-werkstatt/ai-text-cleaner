"""System-Prompt und Few-Shot-Beispiele für den LLM-Polish."""

from __future__ import annotations

SYSTEM_PROMPT = """\
Du bekommst einen deutschen Text, der nach regelbasiertem Cleanup noch typische
KI-Schreibmuster zeigt. Glätte ihn, sodass er natürlicher und weniger
maschinell wirkt.

STRIKTE REGELN:
- Fakten, Zahlen, Namen, Daten, Eigennamen, Zitate und Code-Blöcke bleiben 1:1 erhalten.
- Tokens der Form __PROTECTED_N__ NIEMALS verändern, übersetzen oder entfernen.
- Variiere ausschließlich Stil, Satzbau und Wortwahl.
- Erhöhe Satzlängen-Varianz: mische kurze (3–6 Wörter) und längere Sätze.
- Maximal 1 Em-Dash (—) pro Absatz.
- Vermeide diese Floskeln: „In der heutigen Zeit", „Darüber hinaus", „Es ist
  wichtig zu beachten", „Zusammenfassend lässt sich sagen", „revolutionieren",
  „optimieren" (außer fachlich gemeint), „transformieren", generische
  Drei-Listen, „nicht nur X, sondern auch Y".
- Behalte die Markdown-Struktur (Überschriften, Listen, Absätze) bei.
- Behalte die ungefähre Textlänge bei (±15%).

OUTPUT-FORMAT (strikt JSON, sonst nichts):
{
  "cleaned_text": "<vollständiger umgeschriebener Text>",
  "changes": [
    {"before": "<originalfragment>", "after": "<neues fragment>", "reason": "<kurz>"},
    ...
  ]
}

Liefere maximal 10 wichtige changes-Einträge — nicht jeden Wortwechsel.
"""


AGGRESSIVE_SUFFIX = """\

AGGRESSIVER MODUS:
- Bauernregeln, Sprichwörter, persönliche Wendungen sind erlaubt.
- Stilistische Brüche sind erwünscht.
- Mehr kurze Hauptsätze.
"""


def build_user_prompt(masked_text: str, aggressive: bool = False) -> str:
    suffix = AGGRESSIVE_SUFFIX if aggressive else ""
    return f"{suffix}\nHier der Text:\n\n{masked_text}"
