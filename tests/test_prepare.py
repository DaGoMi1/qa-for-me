"""Prepare node sets intent and search_query in one model call."""

from ml.graph.nodes import prepare


class _Message:
    """Fixed model reply. No API call."""

    def __init__(self, content: str) -> None:
        self.content = content


class _FixedModel:
    """Return a fixed prepare reply."""

    def __init__(self, content: str) -> None:
        self._content = content

    def invoke(self, prompt: str) -> _Message:
        return _Message(self._content)


def test_prepare_bio_sets_intent_and_search_query() -> None:
    """Fake bio reply fills intent and search_query."""
    result = prepare(
        {
            "question": "어디 살아?",
            "history": [],
            "intent": "",
            "search_query": "",
            "context": [],
            "answer": "",
        },
        model=_FixedModel("intent: bio\nsearch_query: 어디 살아?"),
    )
    assert result["intent"] == "bio"
    assert result["search_query"] == "어디 살아?"


def test_prepare_projects_for_confident_project() -> None:
    """Fake projects reply routes to projects."""
    result = prepare(
        {
            "question": "자신 있는 프로젝트가 뭐야?",
            "history": [],
            "intent": "",
            "search_query": "",
            "context": [],
            "answer": "",
        },
        model=_FixedModel(
            "intent: projects\nsearch_query: 자신 있는 프로젝트가 뭐야?"
        ),
    )
    assert result["intent"] == "projects"
    assert result["search_query"] == "자신 있는 프로젝트가 뭐야?"


def test_prepare_with_history_uses_model_search_query() -> None:
    """With history, the model search_query is kept."""
    result = prepare(
        {
            "question": "그거 말고 다른 건 없어?",
            "history": [
                {"role": "user", "content": "프로젝트 뭐 있어?"},
                {"role": "assistant", "content": "why-song-serious가 있습니다."},
            ],
            "intent": "",
            "search_query": "",
            "context": [],
            "answer": "",
        },
        model=_FixedModel(
            "intent: projects\nsearch_query: 이다검이 한 다른 프로젝트 목록"
        ),
    )
    assert result["intent"] == "projects"
    assert result["search_query"] == "이다검이 한 다른 프로젝트 목록"
    assert result["question"] == "그거 말고 다른 건 없어?"


def test_prepare_falls_back_on_unparseable_reply() -> None:
    """Odd model text falls back to bio and the original question."""
    result = prepare(
        {
            "question": "강점이 뭐야?",
            "history": [],
            "intent": "",
            "search_query": "",
            "context": [],
            "answer": "",
        },
        model=_FixedModel("잘 모르겠어요."),
    )
    assert result["intent"] == "bio"
    assert result["search_query"] == "강점이 뭐야?"
