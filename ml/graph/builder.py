"""Assemble the rewrite-then-retrieve-then-generate graph."""

from langchain_chroma import Chroma
from langgraph.graph import END, START, StateGraph

from ml.graph.nodes import _ChatModel, generate, retrieve, rewrite
from ml.graph.state import GraphState


def build_graph(vector_store: Chroma | None = None, model: _ChatModel | None = None):
    """Compile rewrite, then retrieve, then generate."""

    def rewrite_node(state: GraphState) -> GraphState:
        return rewrite(state, model=model)

    def retrieve_node(state: GraphState) -> GraphState:
        return retrieve(state, vector_store=vector_store)

    def generate_node(state: GraphState) -> GraphState:
        return generate(state, model=model)

    graph = StateGraph(GraphState)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_edge(START, "rewrite")
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()
