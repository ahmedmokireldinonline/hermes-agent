import json
from pathlib import Path
import httpx
import yaml
from .config import get_settings, ROOT

settings = get_settings()
CONFIG_PATH = ROOT / 'config' / 'models.open.yaml'

def _load_config() -> dict:
    if CONFIG_PATH.exists():
        return yaml.safe_load(CONFIG_PATH.read_text(encoding='utf-8')) or {}
    return {}

class LLMClient:
    def __init__(self) -> None:
        self.config = _load_config()
        self.profile = self.config.get('profiles', {}).get(settings.model_profile, self.config.get('profiles', {}).get('lite', {}))

    def model_for(self, role: str) -> str:
        return self.profile.get(role) or role

    async def chat(self, role: str, prompt: str) -> str:
        if settings.mock_llm:
            return self._mock(role, prompt)
        payload = {'model': self.model_for(role), 'prompt': prompt, 'stream': False}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f'{settings.ollama_url}/api/generate', json=payload)
            response.raise_for_status()
            return response.json().get('response', '')

    def _mock(self, role: str, prompt: str) -> str:
        if role == 'fast':
            text = prompt.lower()
            selected = 'coder' if any(x in text for x in ['code', 'python', 'برمج', 'كود']) else ('arabic' if any(x in text for x in ['arabic', 'عربي', 'رسالة']) else 'planner')
            return json.dumps({'role': selected, 'confidence': 0.8})
        if role == 'critic':
            return json.dumps({'accuracy': 8, 'completeness': 8, 'language_quality': 8, 'instruction_following': 8, 'safety': 9, 'overall': 8.2, 'critique': 'Mock evaluation; replace with a real critic model.', 'reusable': False})
        return f'[{role} / {self.model_for(role)}] Mock response. Configure MOCK_LLM=false and Ollama for real model execution.\n\nRequest: {prompt[:2000]}'

llm = LLMClient()
