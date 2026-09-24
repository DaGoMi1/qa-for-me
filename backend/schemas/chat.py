"""Chat request and response models."""

from pydantic import BaseModel, Field


class HistoryMessage(BaseModel):
    """One prior turn from the chat UI."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """A question about the profile, with optional prior turns."""

    question: str
    history: list[HistoryMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """An answer grounded in retrieved profile context."""

    answer: str
