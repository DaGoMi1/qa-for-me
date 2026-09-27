# Python
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY pyproject.toml README.md ./
COPY backend ./backend
COPY ml ./ml
COPY frontend ./frontend
COPY data/profile ./data/profile
COPY scripts ./scripts

RUN pip install --upgrade pip && pip install .

EXPOSE 8000 8501

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
