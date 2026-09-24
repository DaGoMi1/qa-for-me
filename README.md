# qa-for-me

나에 대한 질문에 답하는 API입니다. FastAPI가 요청을 받고, LangGraph가 검색과 답변 단계를 잇습니다. 지금은 폴더와 함수 자리만 있습니다.

## 폴더

- `backend/main.py` — FastAPI 앱과 `/health`
- `backend/api/routes/chat.py` — `POST /chat`. 그래프 호출은 다음 단계
- `backend/core/config.py` — 환경 변수
- `backend/schemas/chat.py` — 요청·응답 모델
- `ml/graph/` — 상태, `retrieve`/`generate` 노드, 그래프 조립
- `ml/rag/` — 프로필 로드, 청크, 벡터 저장, 적재
- `data/profile/` — 나에 대한 마크다운
- `scripts/ingest.py` — 프로필을 벡터 저장소에 넣는 진입점
- `frontend/streamlit_app.py` — 질문을 `POST /chat`으로 보내는 화면

## 실행

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
uvicorn backend.main:app --reload
```

다른 터미널에서 화면을 띄웁니다.

```bash
.venv\Scripts\activate
streamlit run frontend/streamlit_app.py
```

API 주소는 `API_BASE_URL`이며, 없으면 `http://127.0.0.1:8000`입니다. `GET /health`는 동작합니다. `POST /chat`은 아직 501을 반환하고, 화면은 그 문구를 보여 줍니다.

## 다음 구현 순서

1. `data/profile/about.md`에 답변에 쓸 사실을 채운다.
2. `ml/rag`에서 마크다운을 청크로 나누고 임베딩해 `data/chroma`에 저장한다.
3. `ml/graph`에서 `retrieve` 다음 `generate`로 이어지는 그래프를 `compile`한다.
4. `POST /chat`이 그 그래프를 호출하게 연결한다.
