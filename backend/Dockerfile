FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /venv
COPY requirements.txt .
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /venv /venv
WORKDIR /app
COPY . .

ENV PATH="/venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE="musicalement.settings.prod"

EXPOSE 8000

CMD ["gunicorn", "musicalement.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
