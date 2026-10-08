import asyncio
import ipaddress
import json
import socket
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import httpx
from .config import get_settings

settings = get_settings()

class ToolError(Exception):
    pass

def _safe_path(path: str) -> Path:
    root = Path(settings.workspace_dir).resolve()
    target = (root / path).resolve()
    if target != root and root not in target.parents:
        raise ToolError('Path is outside the workspace')
    return target

async def read_file(path: str) -> str:
    return _safe_path(path).read_text(encoding='utf-8')[:100_000]

async def write_file(path: str, content: str) -> str:
    target = _safe_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content[:100_000], encoding='utf-8')
    return f'Wrote {len(content)} characters to {target.name}'

async def run_python(code: str) -> str:
    proc = await asyncio.create_subprocess_exec('python', '-I', '-c', code[:20_000], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=settings.workspace_dir, env={})
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=30)
    except asyncio.TimeoutError:
        proc.kill()
        raise ToolError('Python execution timed out')
    return (out + err).decode(errors='replace')[:20_000]

def _public_ip(host: str) -> bool:
    try:
        infos = socket.getaddrinfo(host, None)
        for info in infos:
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
        return True
    except Exception:
        return False

async def http_get(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname or not _public_ip(parsed.hostname):
        raise ToolError('Blocked URL: only public HTTP(S) destinations are allowed')
    async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text[:6000]

async def webhook(url: str, payload: dict) -> str:
    if url not in settings.allowed_webhooks:
        raise ToolError('Webhook URL is not allowlisted')
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return f'Webhook delivered with status {response.status_code}'
