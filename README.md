# Q&A for Me

나에 대한 질문에, 직접 적은 프로필 문서만 근거로 답하는 개인 Q&A입니다.

FastAPI가 `POST /chat`을 받고, LangGraph가 `prepare` → `retrieve`(bio|projects) → `generate` 순으로 검색·생성합니다. 벡터 저장소는 Chroma, 화면은 Streamlit입니다.

**Demo:** [http://13.125.245.206:8501](http://13.125.245.206:8501)  
(EC2 퍼블릭 IP는 인스턴스 재시작 시 바뀔 수 있습니다.)

## 구성

| 경로 | 역할 |
|------|------|
| `backend/` | FastAPI (`/health`, `/chat`) |
| `ml/graph/` | LangGraph 노드·컴파일 |
| `ml/rag/` | 프로필 로드·청크·Chroma |
| `data/profile/` | `bio.md`, `projects.md` |
| `frontend/` | Streamlit UI |
| `scripts/` | 적재·eval |
| `tests/` | pytest · gold eval |

배포는 `Dockerfile` / `docker-compose.yml`로 API와 Streamlit을 로컬과 AWS EC2에 동일하게 띄웁니다. GitHub Actions로 `pytest`(CI)와 `main` 푸시 시 EC2에 SSH로 Compose 재배포(CD)를 돌립니다.

## 실행

`.env`에 `OPENAI_API_KEY`가 필요합니다. (`.env.example` 참고)

**Docker**

```bash
docker compose up --build
```

→ `http://localhost:8501`  
Compose에서 Streamlit은 `http://api:8000`으로 API에 연결합니다.

**로컬 (venv)**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
uvicorn backend.main:app --reload
```

다른 터미널:

```bash
streamlit run frontend/streamlit_app.py
```

`API_BASE_URL` 기본값은 `http://127.0.0.1:8000`입니다.

## 동작 요약

- **prepare**: intent(`bio`|`projects`)와 검색용 `search_query`를 한 번에 만듦
- **retrieve**: source 필터로 해당 프로필 청크만 검색 (k=4)
- **generate**: 검색된 사실만으로 1인칭 한국어 답변 (없으면 모른다고)
- 기동 시 Chroma가 비어 있으면 프로필을 적재하고, 문서 변경 후에는 `python scripts/ingest.py`
- `POST /chat`마다 `uvicorn.error`에 intent·source·latency 등 관측 로그

## 테스트 · eval

```bash
pytest
```

단위 테스트는 가짜 모델·임베딩을 쓰며 OpenAI를 호출하지 않습니다.

`scripts/eval_chat.py`는 실 API로 gold set을 채점합니다. `bio.md`+`projects.md` 해시가 `tests/eval/profile_hash.txt`와 같아야 하며, intent / abstain / followup 게이트를 통과해야 합니다.

## 한계

대화 history는 요청마다 넘기지만, 답은 검색된 프로필 조각 안의 내용으로만 만듭니다. 도메인·HTTPS는 없고, 데모는 EC2 퍼블릭 IP의 8501 포트로 접속합니다.
