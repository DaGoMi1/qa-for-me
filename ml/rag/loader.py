"""Load profile markdown into LangChain documents."""

from pathlib import Path

from langchain_core.documents import Document

PROFILE_DIR = Path(__file__).resolve().parents[2] / "data" / "profile"


def load_profile_documents() -> list[Document]:
    """Read markdown files from data/profile."""
    documents: list[Document] = []
    for path in sorted(PROFILE_DIR.glob("*.md")):
        documents.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": str(path)},
            )
        )
    return documents
