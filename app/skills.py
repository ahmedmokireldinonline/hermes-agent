import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse
import httpx
from .config import get_settings, ROOT

settings = get_settings()
CANDIDATE_DIR = ROOT / "skills" / "candidates"
APPROVED_DIR = ROOT / "skills" / "approved"
AUDIT_LOG = ROOT / "skills" / "audit.log"


class SkillImportError(Exception):
    pass


_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")


def _allowed(url: str) -> bool:
    parsed = urlparse(url)
    return (
        parsed.scheme == "https"
        and bool(parsed.hostname)
        and parsed.hostname.lower() in settings.allowed_skill_hosts
    )


async def import_external_skill(url: str, name: str | None = None) -> dict:
    if not _allowed(url):
        raise SkillImportError("Skill URL host is not allowlisted")
    safe_name = name or "external-skill"
    if not _NAME_RE.fullmatch(safe_name):
        raise SkillImportError("Skill name must match ^[a-z0-9][a-z0-9_-]{1,63}$")
    parsed = urlparse(url)
    if parsed.hostname in {
        "raw.githubusercontent.com",
        "github.com",
        "gitlab.com",
    } and not re.search(r"@[0-9a-fA-F]{40}", url):
        raise SkillImportError("GitHub/GitLab sources require a pinned commit SHA")
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(20), follow_redirects=False, trust_env=False
    ) as client:
        response = await client.get(url)
        if response.is_redirect:
            raise SkillImportError("Redirects are not allowed")
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").lower()
        if content_type and not any(
            x in content_type
            for x in ("text/", "markdown", "json", "yaml", "octet-stream")
        ):
            raise SkillImportError("Unsupported skill content type")
        chunks = []
        size = 0
        async for chunk in response.aiter_bytes(16_384):
            size += len(chunk)
            if size > settings.max_skill_bytes:
                raise SkillImportError("Skill exceeds MAX_SKILL_BYTES")
            chunks.append(chunk)
    content = b"".join(chunks)
    digest = hashlib.sha256(content).hexdigest()
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    path = CANDIDATE_DIR / f"{safe_name}-{digest[:16]}.md"
    path.write_bytes(content)
    return {
        "status": "candidate",
        "path": str(path),
        "sha256": digest,
        "source_url": url,
        "trusted": False,
    }


def approve_skill(candidate: str, approver: str) -> dict:
    path = Path(candidate).resolve()
    if not path.is_relative_to(CANDIDATE_DIR.resolve()) or not path.is_file():
        raise SkillImportError("Invalid candidate path")
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    destination = APPROVED_DIR / path.name
    destination.write_bytes(path.read_bytes())
    with AUDIT_LOG.open("a", encoding="utf-8") as log:
        log.write(f"approved\t{approver}\t{path.name}\n")
    return {"status": "approved", "path": str(destination), "approver": approver}
