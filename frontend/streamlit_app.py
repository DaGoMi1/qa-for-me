"""Chat UI that posts questions to the FastAPI /chat endpoint."""

import os

import httpx
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="qa-for-me")
st.title("qa-for-me")

if "messages" not in st.session_state:
    st.session_state.messages = []


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


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.form("chat", clear_on_submit=True):
    question = st.text_input("질문")
    submitted = st.form_submit_button("전송")

if submitted and question.strip():
    history = list(st.session_state.messages)
    answer = ask(question.strip(), history)
    st.session_state.messages.append({"role": "user", "content": question.strip()})
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
