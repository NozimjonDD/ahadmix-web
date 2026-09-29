FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash ahadmix

COPY requirements/production.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=ahadmix:ahadmix . .

USER ahadmix

CMD ["gunicorn", \
     "--config", "deploy/gunicorn/gunicorn.conf.py", \
     "project_backend.wsgi:application"]
