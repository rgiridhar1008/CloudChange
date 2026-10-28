FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip "setuptools>=80.0.0" "wheel>=0.48.0" "jaraco.context>=6.1.2" "urllib3>=2.8.0" "msgpack>=1.2.3"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

# Run as a non-root user (also satisfies Trivy's Dockerfile checks)
RUN useradd --create-home --uid 10001 appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
