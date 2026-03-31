FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY models ./models
COPY docs ./docs

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "-m", "src.serving.app"]
