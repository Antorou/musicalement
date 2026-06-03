FROM python:3.12-slim AS builder

WORKDIR /app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim

ENV PATH="/venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=musicalement.settings.prod

WORKDIR /app

COPY --from=builder /venv /venv
COPY . .

CMD ["gunicorn", "musicalement.wsgi:application", "--bind", "0.0.0.0:8000"]
