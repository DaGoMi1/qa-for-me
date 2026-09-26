"""그래프 노드 정의: prepare, retrieve, generate"""

from typing import Protocol

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

from backend.core.config import get_settings
from ml.graph.state import GraphState, HistoryMessage
from ml.rag.loader import PROFILE_DIR
from ml.rag.vectorstore import get_vector_store

_HISTORY_TURNS = 4


class _ChatMessage(Protocol):
    """모델 응답: 텍스트만 사용"""

    content: str


class _ChatModel(Protocol):
    """프롬프트를 메시지로 변환하는 모든 객체"""

    def invoke(self, prompt: str) -> _ChatMessage: ...


def _recent_history(history: list[HistoryMessage]) -> list[HistoryMessage]:
    """마지막 몇 턴만 유지하여 프롬프트가 짧게 유지되도록 함"""
    return history[-_HISTORY_TURNS:]


def _format_history(history: list[HistoryMessage]) -> str:
    """프롬프트에 사용될 대화 라인을 포맷팅"""
    lines: list[str] = []
    for message in _recent_history(history):
        lines.append(f"{message['role']}: {message['content']}")
    return "\n".join(lines)


def _pass_through(state: GraphState, **updates: object) -> GraphState:
    """공유 필드를 유지하고 로컬 업데이트를 적용"""
    return {
        "question": state["question"],
        "history": state.get("history", []),
        "intent": state.get("intent", ""),
        "search_query": state.get("search_query", ""),
        "context": state.get("context", []),
        "answer": state.get("answer", ""),
        **updates,  # type: ignore[misc]
    }


def _parse_prepare(text: str, question: str) -> tuple[str, str]:
    """intent와 search_query를 파싱"""
    intent = "bio"
    search_query = question
    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith("intent:"):
            value = stripped.split(":", 1)[1].strip().lower()
            intent = "projects" if "projects" in value else "bio"
        elif lower.startswith("search_query:"):
            value = stripped.split(":", 1)[1].strip()
            if value:
                search_query = value
    return intent, search_query


def prepare(state: GraphState, model: _ChatModel | None = None) -> GraphState:
    """bio|projects를 선택하고 독립적인 검색 쿼리를 하나의 모델 호출로 처리"""
    chat = model or _default_chat_model()
    history = state.get("history", [])
    history_text = _format_history(history)
    history_block = (
        f"이전 대화:\n{history_text}\n\n" if history_text else ""
    )
    prompt = (
        "질문을 보고 아래 두 줄만 출력하세요. 설명이나 따옴표는 쓰지 마세요.\n"
        "intent: bio 또는 projects\n"
        "search_query: 프로필 문서 검색용 한국어 질문 한 문장 "
        "(이전 대화가 있으면 이어 묻기를 반영하고, 없으면 질문과 같게)\n\n"
        "규칙: 소개·학교·거주지·관심·강점은 bio, "
        "프로젝트 목록·특정 프로젝트·자신 있는 프로젝트는 projects.\n\n"
        f"{history_block}"
        f"질문: {state['question']}"
        "출력 예시 1: intent: bio\nsearch_query: 너는 어디서 살아?"
        "출력 예시 2: intent: projects\nsearch_query: 너는 어떤 프로젝트를 했어?"
    )
    response = chat.invoke(prompt)
    intent, search_query = _parse_prepare(response.content, state["question"])
    return _pass_through(
        state,
        intent=intent,
        search_query=search_query,
        context=[],
        answer="",
    )


def retrieve(
    state: GraphState,
    vector_store: Chroma | None = None,
    source_name: str | None = None,
) -> GraphState:
    """프로필 청크를 검색 쿼리에 맞게 불러오고, 옵션으로 파일 필터링"""
    store = vector_store or get_vector_store()
    query = state.get("search_query") or state["question"]
    search_filter = None
    if source_name is not None:
        search_filter = {"source": str(PROFILE_DIR / source_name)}
    documents = store.similarity_search(query, k=4, filter=search_filter)
    return _pass_through(
        state,
        context=[document.page_content for document in documents],
        answer="",
    )


def generate(state: GraphState, model: _ChatModel | None = None) -> GraphState:
    """검색된 컨텍스트와 최근 대화 기반으로 답변 작성"""
    chat = model or _default_chat_model()
    context = "\n".join(state["context"])
    history_text = _format_history(state.get("history", []))
    history_block = (
        f"이전 대화:\n{history_text}\n\n" if history_text else ""
    )
    prompt = (
        "당신은 이다검입니다. 아래 사실만 근거로 질문에 한국어로 답하세요. "
        "나/저는으로 직접 말하세요. "
        "프로필, 문서, 검색 결과 같은 말은 쓰지 마세요. "
        "이전 대화가 있으면 이어 묻기를 반영하세요. "
        "사실에 없으면 짧게 모른다고만 하세요. "
        "근거 문장의 시제와 시점을 바꾸지 마세요. "
        "예를 들어 취득했다를 취득할 예정으로 바꾸지 마세요. "
        "근거에 없는 구현 단계, 수치, 도구 이름을 지어내지 마세요. "
        "근거에 없으면 추측으로 채우지 마세요.\n\n"
        f"내가 알아도 되는 사실:\n{context}\n\n"
        f"{history_block}"
        f"질문: {state['question']}"
    )
    response = chat.invoke(prompt)
    return _pass_through(state, answer=response.content)


def _default_chat_model() -> ChatOpenAI:
    """설정된 채팅 모델을 열고, 테스트 시 자체 모델을 사용"""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
    )
