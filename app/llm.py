import json
import re
import httpx
import yaml
from .config import get_settings, ROOT

settings = get_settings()
CONFIG_PATH = ROOT / "config" / "models.open.yaml"
_MODEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    return {}


class LLMClient:
    def __init__(self) -> None:
        self.config = _load_config()
        profiles = self.config.get("profiles", {})
        self.profile = profiles.get(settings.model_profile, profiles.get("lite", {}))

    def model_for(self, role: str) -> str:
        model = self.profile.get(role) or role
        if not _MODEL_RE.fullmatch(model):
            raise RuntimeError("Invalid model name in configuration")
        return model

    async def chat(self, role: str, prompt: str) -> str:
        if settings.mock_llm:
            return self._mock(role, prompt)
        model = self.model_for(role)
        payload = {"model": model, "prompt": prompt, "stream": False}
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(60), trust_env=False
        ) as client:
            response = await client.post(
                f"{settings.ollama_url.rstrip('/')}/api/generate", json=payload
            )
            if response.status_code == 404:
                raise RuntimeError(f"Ollama model is not pulled: {model}")
            response.raise_for_status()
            return response.json().get("response", "")

    def _mock(self, role: str, prompt: str) -> str:
        if role == "fast":
            text = prompt.lower()
            selected = (
                "coder"
                if any(x in text for x in ["code", "python", "program", "debug"])
                else (
                    "arabic"
                    if any(
                        x in text for x in ["arabic", "egyptian", "customer message"]
                    )
                    else "planner"
                )
            )
            return json.dumps({"role": selected, "confidence": 0.8})
        if role == "critic":
            return json.dumps(
                {
                    "accuracy": 8,
                    "completeness": 8,
                    "language_quality": 8,
                    "instruction_following": 8,
                    "safety": 9,
                    "overall": 8.2,
                    "critique": "Mock evaluation; replace with a real critic model.",
                    "reusable": False,
                }
            )
        return f"[{role} / {self.model_for(role)}] Mock response. Configure MOCK_LLM=false and Ollama for real model execution.\n\nRequest: {prompt[:2000]}"


llm = LLMClient()
