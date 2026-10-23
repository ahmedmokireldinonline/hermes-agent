FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
COPY requirements.txt .
COPY requirements-automation.txt .
RUN pip install --no-cache-dir -r requirements.txt -r requirements-automation.txt
RUN playwright install --with-deps chromium
COPY app ./app
COPY config ./config
COPY prompts ./prompts
COPY workspace ./workspace
COPY dashboard ./dashboard
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
