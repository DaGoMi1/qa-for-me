"""그래프 노드 간 공유 상태 정의"""

from typing import TypedDict


class HistoryMessage(TypedDict):
    """이전 사용자 또는 어시스턴트 턴"""

    role: str
    content: str


class GraphState(TypedDict):
    """질문, 대화 기록, 의도, 검색 쿼리, 검색된 청크, 답변"""

    question: str
    history: list[HistoryMessage]
    intent: str
    search_query: str
    context: list[str]
    answer: str
