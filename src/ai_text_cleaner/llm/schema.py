"""Pydantic-Schemata für LLM-Antworten."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LLMChange(BaseModel):
    before: str = Field(description="Originaler Textausschnitt")
    after: str = Field(description="Umgeschriebener Ausschnitt")
    reason: str = Field(description="Begründung der Änderung")


class CleanResponse(BaseModel):
    cleaned_text: str
    changes: list[LLMChange] = Field(default_factory=list)
