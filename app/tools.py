import asyncio
import ipaddress
import os
import resource
import signal
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
    if (
        not isinstance(path, str)
        or not path
        or "\x00" in path
        or path.startswith(("~", "/", "\\"))
        or "\\" in path
    ):
        raise ToolError("Invalid workspace path")
    root = Path(settings.workspace_dir).resolve()
    target = (root / path).resolve()
    if target != root and not target.is_relative_to(root):
        raise ToolError("Path is outside the workspace")
    if target.exists() and target.is_symlink():
        raise ToolError("Symlinks are not allowed")
    return target


async def read_file(path: str) -> str:
    target = _safe_path(path)
    if not target.is_file() or target.stat().st_size > settings.max_file_bytes:
        raise ToolError("File is missing or too large")
    return target.read_text(encoding="utf-8")


async def write_file(path: str, content: str) -> str:
    target = _safe_path(path)
    if len(content.encode("utf-8")) > settings.max_file_bytes:
        raise ToolError("File is too large")
    root = Path(settings.workspace_dir).resolve()
    if (
        sum(1 for p in root.rglob("*") if p.is_file()) >= settings.max_file_count
        and not target.exists()
    ):
        raise ToolError("Workspace file limit reached")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} characters to {target.name}"


def _limit_process() -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))
    resource.setrlimit(
        resource.RLIMIT_FSIZE, (settings.max_file_bytes, settings.max_file_bytes)
    )
    os.setsid()


async def run_python(code: str) -> str:
    if len(code.encode()) > 20_000:
        raise ToolError("Python source is too large")
    proc = await asyncio.create_subprocess_exec(
        "python",
        "-I",
        "-c",
        code,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=settings.workspace_dir,
        env={},
        preexec_fn=_limit_process,
        start_new_session=False,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=30)
    except asyncio.TimeoutError:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        raise ToolError("Python execution timed out")
    return (out[:20_000] + err[:20_000]).decode(errors="replace")


def _resolved_public_ips(host: str) -> list[ipaddress._BaseAddress]:
    if host.lower() in {
        "localhost",
        "metadata.google.internal",
        "instance-data.ec2.internal",
    }:
        raise ToolError("Blocked metadata hostname")
    try:
        direct = ipaddress.ip_address(host)
        infos = [direct]
    except ValueError:
        try:
            infos = [
                ipaddress.ip_address(info[4][0])
                for info in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
            ]
        except socket.gaierror as exc:
            raise ToolError("Host resolution failed") from exc
    for ip in infos:
        check = (
            ip.ipv4_mapped
            if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped
            else ip
        )
        if (
            check.is_private
            or check.is_loopback
            or check.is_link_local
            or check.is_reserved
            or check.is_multicast
            or check.is_unspecified
        ):
            raise ToolError("Private or reserved destination blocked")
    return infos


def _validate_url(url: str, allowed: set[str] | None = None) -> str:
    parsed = urlparse(url)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.username
        or parsed.password
        or not parsed.hostname
    ):
        raise ToolError("Only credential-free HTTP(S) URLs are allowed")
    if parsed.port not in {None, 80, 443}:
        raise ToolError("Only ports 80 and 443 are allowed")
    _resolved_public_ips(parsed.hostname)
    if allowed is not None and url not in allowed:
        raise ToolError("URL is not allowlisted")
    return url


async def http_get(url: str) -> str:
    _validate_url(url)
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(15), follow_redirects=False, trust_env=False
    ) as client:
        response = await client.get(url, headers={})
        if response.is_redirect:
            raise ToolError("Redirects are disabled for public HTTP tool")
        response.raise_for_status()
        if len(response.content) > 6_000_000:
            raise ToolError("HTTP response is too large")
        return response.text[:6000]


async def webhook(url: str, payload: dict) -> str:
    _validate_url(url, settings.allowed_webhooks)
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(15), follow_redirects=False, trust_env=False
    ) as client:
        response = await client.post(url, json=payload, headers={})
        if response.is_redirect:
            raise ToolError("Webhook redirects are disabled")
        response.raise_for_status()
        return f"Webhook delivered with status {response.status_code}"
