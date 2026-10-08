from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    app_name: str = 'Hermes Agent'
    database_url: str = 'sqlite+aiosqlite:///./hermes.db'
    redis_url: str = 'redis://localhost:6379/0'
    ollama_url: str = 'http://localhost:11434'
    mock_llm: bool = True
    model_profile: str = 'lite'
    api_keys: str = ''
    rate_limit_per_min: int = 60
    max_steps: int = 6
    max_task_seconds: int = 120
    max_task_tokens: int = 4096
    max_retries: int = 3
    webhook_allow: str = ''
    skill_source_allow: str = 'raw.githubusercontent.com,github.com,gitlab.com,huggingface.co'
    max_skill_bytes: int = 200_000
    workspace_dir: str = str(ROOT / 'workspace')
    worker_poll_seconds: float = 1.0
    queue_mode: str = 'inline'
    redis_queue_name: str = 'hermes:tasks'

    @property
    def allowed_api_keys(self) -> set[str]:
        return {x.strip() for x in self.api_keys.split(',') if x.strip()}

    @property
    def allowed_webhooks(self) -> set[str]:
        return {x.strip() for x in self.webhook_allow.split(',') if x.strip()}

    @property
    def allowed_skill_hosts(self) -> set[str]:
        return {x.strip().lower() for x in self.skill_source_allow.split(',') if x.strip()}

@lru_cache
def get_settings() -> Settings:
    return Settings()
