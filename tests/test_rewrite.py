"""Rewrite node builds a standalone search query."""

from ml.graph.nodes import rewrite


class _Message:
    """Fixed model reply. No API call."""

    def __init__(self, content: str) -> None:
        self.content = content


class _FixedModel:
    """Return a fixed rewritten search query."""

    def invoke(self, prompt: str) -> _Message:
        return _Message("이다검이 한 다른 프로젝트 목록")


def test_rewrite_without_history_uses_question() -> None:
    """No history means search_query is the question and the model is unused."""
    result = rewrite(
        {
            "question": "어디서 살아?",
            "history": [],
            "search_query": "",
            "context": [],
            "answer": "",
        }
    )

    assert result["search_query"] == "어디서 살아?"


def test_rewrite_with_history_uses_model() -> None:
    """With history, the fake model reply becomes search_query."""
    result = rewrite(
        {
            "question": "그거 말고 다른 건 없어?",
            "history": [
                {"role": "user", "content": "프로젝트 뭐 있어?"},
                {"role": "assistant", "content": "why-song-serious가 있습니다."},
            ],
            "search_query": "",
            "context": [],
            "answer": "",
        },
        model=_FixedModel(),
    )

    assert result["search_query"] == "이다검이 한 다른 프로젝트 목록"
    assert result["question"] == "그거 말고 다른 건 없어?"
