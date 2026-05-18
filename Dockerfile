FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini ./
COPY alembic ./alembic
COPY docker/api-entrypoint.sh /app/docker/api-entrypoint.sh
COPY src ./src

RUN chmod +x /app/docker/api-entrypoint.sh

EXPOSE 8000

CMD ["/app/docker/api-entrypoint.sh"]
