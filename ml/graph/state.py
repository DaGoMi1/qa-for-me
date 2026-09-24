"""Shared state passed between graph nodes."""

from typing import TypedDict


class HistoryMessage(TypedDict):
    """One prior user or assistant turn."""

    role: str
    content: str


class GraphState(TypedDict):
    """Question, history, retrieved snippets, and the drafted answer."""

    question: str
    history: list[HistoryMessage]
    context: list[str]
    answer: str
