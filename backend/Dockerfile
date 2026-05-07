FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry
COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction

COPY backend/ .
COPY ai/ /app/ai/      
ENV PYTHONPATH=/app    