FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry==2.3.3
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction

COPY . .