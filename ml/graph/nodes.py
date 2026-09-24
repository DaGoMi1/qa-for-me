"""Graph node signatures. Bodies stay empty until retrieval and generation exist."""

from ml.graph.state import GraphState


def retrieve(state: GraphState) -> GraphState:
    """Load profile chunks relevant to the question."""
    ...


def generate(state: GraphState) -> GraphState:
    """Draft an answer from the retrieved context."""
    ...
