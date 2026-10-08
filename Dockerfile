FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 hermes
COPY app ./app
COPY config ./config
COPY prompts ./prompts
COPY scripts ./scripts
COPY skills ./skills
COPY web ./web
RUN mkdir -p /app/workspace /app/review && chown -R hermes:hermes /app
USER hermes
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
