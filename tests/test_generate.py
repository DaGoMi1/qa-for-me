"""Generate node fills the answer from a supplied model."""

from ml.graph.nodes import generate


class _Message:
    """Fixed model reply. No API call."""

    def __init__(self, content: str) -> None:
        self.content = content


class _FixedModel:
    """Return the same sentence for every prompt."""

    def invoke(self, prompt: str) -> _Message:
        return _Message("부산에서 살고 있습니다.")


def test_generate_keeps_question_and_fills_answer() -> None:
    """The fake reply becomes answer. Question and context stay as given."""
    state = {
        "question": "어디서 살아?",
        "context": ["이다검은 부산에서 살고 있습니다."],
        "answer": "",
    }

    result = generate(state, model=_FixedModel())

    assert result["answer"] == "부산에서 살고 있습니다."
    assert result["question"] == state["question"]
    assert result["context"] == state["context"]
