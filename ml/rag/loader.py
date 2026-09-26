"""프로필 마크다운을 LangChain 문서로 불러오기"""

from pathlib import Path

from langchain_core.documents import Document

PROFILE_DIR = Path(__file__).resolve().parents[2] / "data" / "profile"


def load_profile_documents() -> list[Document]:
    """data/profile 디렉토리에서 마크다운 파일을 읽어 LangChain 문서로 변환"""
    documents: list[Document] = []
    for path in sorted(PROFILE_DIR.glob("*.md")):
        documents.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": str(path)},
            )
        )
    return documents
