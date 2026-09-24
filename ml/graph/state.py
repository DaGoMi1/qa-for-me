"""Shared state passed between graph nodes."""

from typing import TypedDict


class GraphState(TypedDict):
    """Question, retrieved profile snippets, and the drafted answer."""

    question: str
    context: list[str]
    answer: str
