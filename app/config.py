from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    env: str = "prod"
    app_name: str = "Hermes Agent"
    database_url: str = "sqlite+aiosqlite:///./hermes.db"
    redis_url: str = "redis://localhost:6379/0"
    ollama_url: str = "http://localhost:11434"
    mock_llm: bool = True
    model_profile: str = "lite"
    api_keys: str = ""
    rate_limit_per_min: int = 60
    max_steps: int = 6
    max_task_seconds: int = 120
    max_task_tokens: int = 4096
    max_retries: int = 3
    max_input_chars: int = 100_000
    max_file_bytes: int = 100_000
    max_file_count: int = 100
    webhook_allow: str = ""
    skill_source_allow: str = (
        "raw.githubusercontent.com,github.com,gitlab.com,huggingface.co"
    )
    skill_repo_allow: str = ""
    max_skill_bytes: int = 200_000
    workspace_dir: str = str(ROOT / "workspace")
    review_dir: str = str(ROOT / "review")
    worker_poll_seconds: float = 1.0
    queue_mode: str = "inline"
    redis_queue_name: str = "hermes:tasks"
    request_max_bytes: int = 200_000

    @property
    def allowed_api_keys(self) -> set[str]:
        return {x.strip() for x in self.api_keys.split(",") if x.strip()}

    @property
    def allowed_webhooks(self) -> set[str]:
        return {x.strip() for x in self.webhook_allow.split(",") if x.strip()}

    @property
    def allowed_skill_hosts(self) -> set[str]:
        return {
            x.strip().lower() for x in self.skill_source_allow.split(",") if x.strip()
        }

    @property
    def allowed_skill_repos(self) -> set[str]:
        return {
            x.strip().lower() for x in self.skill_repo_allow.split(",") if x.strip()
        }

    @property
    def auth_required(self) -> bool:
        return self.env != "dev"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.auth_required and (
        not settings.allowed_api_keys or "change-me" in settings.allowed_api_keys
    ):
        raise RuntimeError(
            "API_KEYS must be configured with non-placeholder values when ENV is not dev"
        )
    return settings
