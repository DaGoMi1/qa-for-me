# qa-for-me

나에 대한 질문에 답하는 개인 Q&A입니다. FastAPI가 요청을 받고, LangGraph가 `retrieve` → `generate` 순서로 프로필을 검색·답변합니다. 벡터 저장소는 Chroma이고, 화면은 Streamlit입니다.

## 폴더

- `backend/main.py` — FastAPI 앱, `/health`, 기동 시 빈 저장소만 적재
- `backend/api/routes/chat.py` — `POST /chat`이 그래프를 호출해 답변 반환
- `backend/core/config.py` — 환경 변수
- `backend/schemas/chat.py` — 요청·응답 모델
- `ml/graph/` — 상태, `retrieve`/`generate` 노드, 그래프 컴파일
- `ml/rag/` — 프로필 로드, 청크, 벡터 저장, 적재
- `data/profile/` — 답변에 쓰는 마크다운
- `data/chroma/` — 로컬 벡터 저장소 (gitignore)
- `scripts/ingest.py` — 프로필을 강제로 다시 적재할 때 사용
- `frontend/streamlit_app.py` — 질문을 `POST /chat`으로 보내는 화면
- `tests/` — pytest

## 실행

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

OpenAI API 키 등 로컬 설정을 준비한 뒤 API를 띄웁니다.

```bash
uvicorn backend.main:app --reload
```

다른 터미널에서 화면을 띄웁니다.

```bash
.venv\Scripts\activate
streamlit run frontend/streamlit_app.py
```

Streamlit이 붙는 API 주소는 `API_BASE_URL`이며, 없으면 `http://127.0.0.1:8000`입니다.

## 적재

서버가 뜰 때 `data/chroma`의 프로필 컬렉션이 비어 있으면 한 번 적재합니다. 이미 벡터가 있으면 그대로 씁니다.

`data/profile/about.md`를 고친 뒤에는 다시 넣어야 합니다.

```bash
python scripts/ingest.py
```

## 테스트

```bash
pytest
```

## 알려진 한계

최근 대화는 API로 넘기지만, 답은 검색된 프로필 조각 안에 있는 내용으로만 만듭니다. 검색이 빗나가면 이어 묻기도 부족하게 답할 수 있습니다.
