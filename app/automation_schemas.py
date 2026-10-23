from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict, HttpUrl

ActionType = Literal['navigate', 'back', 'forward', 'reload', 'click', 'fill', 'type', 'press', 'select', 'check', 'uncheck', 'hover', 'scroll', 'wait', 'wait_for_selector', 'extract_text', 'extract_attribute', 'screenshot', 'upload_file', 'download_file']


class WorkflowStep(BaseModel):
    type: ActionType
    url: str | None = None
    selector: str | None = None
    value: str | None = None
    attribute: str | None = None
    path: str | None = None
    timeout_ms: int | None = Field(default=None, ge=100, le=120_000)
    optional: bool = False


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    steps: list[WorkflowStep] = Field(min_length=1, max_length=50)


class WorkflowResponse(WorkflowCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: str
    created_at: datetime
    updated_at: datetime


class WorkflowRunCreate(BaseModel):
    variables: dict[str, Any] = Field(default_factory=dict)


class WorkflowRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workflow_id: str
    status: str
    outputs: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: int = 0
    created_at: datetime


class ScrapeRequest(BaseModel):
    url: str
    selector: str = Field(default='body', max_length=500)
    extract: Literal['text', 'html', 'links'] = 'text'
    use_browser: bool = False


class MetricsResponse(BaseModel):
    workflows_total: int
    workflow_runs_total: int
    workflow_runs_succeeded: int
    workflow_runs_failed: int
    browser_actions_total: int
    scrape_requests_total: int
    uptime_seconds: float
