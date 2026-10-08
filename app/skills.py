import hashlib
from pathlib import Path
from urllib.parse import urlparse
import httpx
from .config import get_settings, ROOT

settings = get_settings()
CANDIDATE_DIR = ROOT / 'skills' / 'candidates'

class SkillImportError(Exception):
    pass

def _allowed(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == 'https' and bool(parsed.hostname) and parsed.hostname.lower() in settings.allowed_skill_hosts

async def import_external_skill(url: str, name: str | None = None) -> dict:
    if not _allowed(url):
        raise SkillImportError('Skill URL host is not allowlisted')
    async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
        response = await client.get(url)
        response.raise_for_status()
        content = response.content
    if len(content) > settings.max_skill_bytes:
        raise SkillImportError('Skill is larger than MAX_SKILL_BYTES')
    digest = hashlib.sha256(content).hexdigest()[:16]
    safe_name = ''.join(c if c.isalnum() or c in '-_' else '-' for c in (name or 'external-skill'))[:60]
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    path = CANDIDATE_DIR / f'{safe_name}-{digest}.md'
    path.write_bytes(content)
    return {'status': 'candidate', 'path': str(path), 'sha256_prefix': digest, 'source_url': url, 'trusted': False}
