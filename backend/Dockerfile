# backend/Dockerfile
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (if you don't need build tools, you can remove this)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# CHANGE "soil:app" to your actual module:app path
CMD ["uvicorn", "soil:app", "--host", "0.0.0.0", "--port", "8000"]
