import os

os.environ.setdefault("ENV", "dev")
os.environ.setdefault("MOCK_LLM", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test-hermes.db")
os.environ.setdefault("QUEUE_MODE", "inline")
os.environ.setdefault("API_KEYS", "test-secret")
