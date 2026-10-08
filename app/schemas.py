from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    input: str = Field(min_length=1, max_length=100_000)
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")
    idempotency_key: str | None = Field(
        default=None, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
    )


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    input: str
    status: str
    role: str | None = None
    result: str | None = None
    score: float | None = None
    critique: str | None = None
    reusable: bool = False
    steps: list[Any] = Field(default_factory=list)
    retries: int = 0
    failure_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    llm: str
