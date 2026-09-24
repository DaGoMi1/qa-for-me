"""Graph nodes. Generation stays empty until the answer step exists."""

from langchain_chroma import Chroma

from ml.graph.state import GraphState
from ml.rag.vectorstore import get_vector_store


def retrieve(state: GraphState, vector_store: Chroma | None = None) -> GraphState:
    """Load profile chunks relevant to the question."""
    store = vector_store or get_vector_store()
    documents = store.similarity_search(state["question"], k=4)
    return {
        "question": state["question"],
        "context": [document.page_content for document in documents],
        "answer": "",
    }


def generate(state: GraphState) -> GraphState:
    """Draft an answer from the retrieved context."""
    ...
