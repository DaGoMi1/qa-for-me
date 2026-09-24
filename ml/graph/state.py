"""Shared state passed between graph nodes."""

from typing import TypedDict


class HistoryMessage(TypedDict):
    """One prior user or assistant turn."""

    role: str
    content: str


class GraphState(TypedDict):
    """Question, history, search query, retrieved snippets, and answer."""

    question: str
    history: list[HistoryMessage]
    search_query: str
    context: list[str]
    answer: str
