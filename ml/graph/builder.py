"""prepare, retrieve, generate 그래프 빌더"""

from langchain_chroma import Chroma
from langgraph.graph import END, START, StateGraph

from ml.graph.nodes import _ChatModel, generate, prepare, retrieve
from ml.graph.state import GraphState


def build_graph(vector_store: Chroma | None = None, model: _ChatModel | None = None):
    """prepare → bio|projects retrieve → generate 그래프 컴파일"""

    def prepare_node(state: GraphState) -> GraphState:
        """prepare 노드: 의도와 검색 쿼리 결정"""
        return prepare(state, model=model)

    def retrieve_bio_node(state: GraphState) -> GraphState:
        """retrieve_bio 노드: bio.md 소스에서 검색"""
        return retrieve(state, vector_store=vector_store, source_name="bio.md")

    def retrieve_projects_node(state: GraphState) -> GraphState:
        """retrieve_projects 노드: projects.md 소스에서 검색"""
        return retrieve(state, vector_store=vector_store, source_name="projects.md")

    def generate_node(state: GraphState) -> GraphState:
        """generate 노드: 컨텍스트와 대화 기반 답변 생성"""
        return generate(state, model=model)

    def route_by_intent(state: GraphState) -> str:
        """의도에 따라 분기: bio 또는 projects"""
        if state.get("intent") == "projects":
            return "retrieve_projects"
        return "retrieve_bio"

    graph = StateGraph(GraphState)
    graph.add_node("prepare", prepare_node)
    graph.add_node("retrieve_bio", retrieve_bio_node)
    graph.add_node("retrieve_projects", retrieve_projects_node)
    graph.add_node("generate", generate_node)
    graph.add_edge(START, "prepare")
    graph.add_conditional_edges(
        "prepare",
        route_by_intent,
        {
            "retrieve_bio": "retrieve_bio",
            "retrieve_projects": "retrieve_projects",
        },
    )
    graph.add_edge("retrieve_bio", "generate")
    graph.add_edge("retrieve_projects", "generate")
    graph.add_edge("generate", END)
    return graph.compile()
