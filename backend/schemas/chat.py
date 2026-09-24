"""Chat request and response models."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """A question about the profile."""

    question: str


class ChatResponse(BaseModel):
    """An answer grounded in retrieved profile context."""

    answer: str
