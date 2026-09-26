"""Chat UI that posts questions to the FastAPI /chat endpoint."""

import os

import httpx
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="Q&A for Me")
st.title("Q&A for Me")

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(
        "저에 대해 궁금한 것을 물어보세요. "
        "직접 적은 프로필 문서를 기준으로 답합니다.\n\n"
        "예: `이름이 뭐야?`, `너가 한 프로젝트는 뭐 있어?`  "
        "자유롭게 물어보셔도 됩니다. 문서에 없으면 모른다고 답할 수 있어요."
    )


def ask(question: str, history: list[dict[str, str]]) -> str:
    """Send a question and prior turns to POST /chat."""
    try:
        response = httpx.post(
            f"{API_BASE_URL}/chat",
            json={"question": question, "history": history},
            timeout=30.0,
        )
    except httpx.HTTPError as exc:
        return f"API에 연결하지 못했습니다: {exc}"

    if response.status_code == 200:
        return str(response.json().get("answer", ""))

    detail: object = response.text
    try:
        detail = response.json().get("detail", detail)
    except ValueError:
        pass
    return str(detail)


def render_message(text: str) -> None:
    """Show chat text as markdown without treating ~ ranges as strikethrough."""
    st.markdown(text.replace("~", "\\~"))


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        render_message(message["content"])

with st.form("chat", clear_on_submit=True):
    question = st.text_input("질문")
    submitted = st.form_submit_button("전송")

if submitted and question.strip():
    history = list(st.session_state.messages)
    answer = ask(question.strip(), history)
    st.session_state.messages.append({"role": "user", "content": question.strip()})
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
