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


class _RecordingModel:
    """Capture the prompt text. No API call."""

    def __init__(self) -> None:
        self.last_prompt = ""

    def invoke(self, prompt: str) -> _Message:
        self.last_prompt = prompt
        return _Message("다른 프로젝트도 있습니다.")


def test_generate_keeps_question_and_fills_answer() -> None:
    """The fake reply becomes answer. Question and context stay as given."""
    state = {
        "question": "어디서 살아?",
        "history": [],
        "context": ["이다검은 부산에서 살고 있습니다."],
        "answer": "",
    }

    result = generate(state, model=_FixedModel())

    assert result["answer"] == "부산에서 살고 있습니다."
    assert result["question"] == state["question"]
    assert result["context"] == state["context"]


def test_generate_includes_history_in_prompt() -> None:
    """Prior turns appear in the model prompt."""
    model = _RecordingModel()
    state = {
        "question": "그거 밖에 없어?",
        "history": [
            {"role": "user", "content": "프로젝트 뭐 있어?"},
            {"role": "assistant", "content": "why-song-serious가 있습니다."},
        ],
        "context": ["프로젝트: why-song-serious, movie-recommendation"],
        "answer": "",
    }

    generate(state, model=model)

    assert "프로젝트 뭐 있어?" in model.last_prompt
    assert "그거 밖에 없어?" in model.last_prompt
