"""Assemble the retrieve-then-generate graph."""

from langchain_chroma import Chroma
from langgraph.graph import END, START, StateGraph

from ml.graph.nodes import _ChatModel, generate, retrieve
from ml.graph.state import GraphState


def build_graph(vector_store: Chroma | None = None, model: _ChatModel | None = None):
    """Compile retrieve, then generate."""

    def retrieve_node(state: GraphState) -> GraphState:
        return retrieve(state, vector_store=vector_store)

    def generate_node(state: GraphState) -> GraphState:
        return generate(state, model=model)

    graph = StateGraph(GraphState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()
