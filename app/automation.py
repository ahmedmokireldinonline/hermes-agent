import asyncio
import ipaddress
import json
import socket
import time
from pathlib import Path
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from .config import get_settings
from .tracking import increment

settings = get_settings()


class AutomationError(Exception):
    pass


def _public_host(host: str) -> bool:
    try:
        for info in socket.getaddrinfo(host, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
        return True
    except Exception:
        return False


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname:
        raise AutomationError('Only HTTP(S) URLs are allowed')
    host = parsed.hostname.lower()
    allowed = settings.allowed_browser_domains
    if allowed and not any(host == d or host.endswith('.' + d) for d in allowed):
        raise AutomationError('Domain is not in BROWSER_ALLOWED_DOMAINS')
    if not allowed and not _public_host(host):
        raise AutomationError('Private, local, and reserved destinations are blocked')
    return url


async def scrape(request: dict) -> dict:
    url = validate_url(request['url'])
    increment('scrape_requests_total')
    if request.get('use_browser'):
        return await browser_run([{'type': 'navigate', 'url': url}, {'type': 'extract_text', 'selector': request.get('selector', 'body')}])
    async with httpx.AsyncClient(timeout=20, follow_redirects=False, headers={'User-Agent': 'HermesAgent/0.2 (+self-hosted)'}) as client:
        response = await client.get(url)
        response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    nodes = soup.select(request.get('selector', 'body'))
    if request.get('extract') == 'html':
        value = ''.join(str(n) for n in nodes)[:200_000]
    elif request.get('extract') == 'links':
        value = [{'text': n.get_text(' ', strip=True), 'href': n.get('href')} for n in soup.select(request.get('selector', 'a'))][:5_000]
    else:
        value = '\n'.join(n.get_text(' ', strip=True) for n in nodes)[:200_000]
    return {'url': url, 'status_code': response.status_code, 'data': value, 'content_type': response.headers.get('content-type', '')}


async def browser_run(steps: list[dict], variables: dict | None = None) -> dict:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise AutomationError('Playwright is not installed. Install requirements and run: playwright install chromium') from exc
    variables = variables or {}
    artifacts = Path(settings.artifacts_dir)
    artifacts.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    outputs: dict = {'steps': []}
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=settings.browser_headless)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        try:
            if len(context.pages) > settings.browser_max_pages:
                raise AutomationError('Browser page limit exceeded')
            for index, raw in enumerate(steps):
                step = dict(raw)
                timeout = int(step.get('timeout_ms') or settings.browser_timeout_ms)
                action = step.get('type')
                increment('browser_actions_total')
                value = step.get('value')
                if isinstance(value, str):
                    for key, replacement in variables.items():
                        value = value.replace('{{' + key + '}}', str(replacement))
                if action == 'navigate':
                    await page.goto(validate_url(step['url']), wait_until='domcontentloaded', timeout=timeout)
                elif action == 'back': await page.go_back(timeout=timeout)
                elif action == 'forward': await page.go_forward(timeout=timeout)
                elif action == 'reload': await page.reload(timeout=timeout)
                elif action == 'click': await page.locator(step['selector']).click(timeout=timeout)
                elif action in {'fill', 'type'}:
                    if action == 'fill': await page.locator(step['selector']).fill(value or '', timeout=timeout)
                    else: await page.locator(step['selector']).type(value or '', timeout=timeout)
                elif action == 'press': await page.locator(step['selector']).press(value or 'Enter', timeout=timeout)
                elif action == 'select': await page.locator(step['selector']).select_option(value or '', timeout=timeout)
                elif action == 'check': await page.locator(step['selector']).check(timeout=timeout)
                elif action == 'uncheck': await page.locator(step['selector']).uncheck(timeout=timeout)
                elif action == 'hover': await page.locator(step['selector']).hover(timeout=timeout)
                elif action == 'scroll': await page.mouse.wheel(0, int(value or 800))
                elif action == 'wait': await asyncio.sleep(float(value or 1))
                elif action == 'wait_for_selector': await page.locator(step['selector']).wait_for(timeout=timeout)
                elif action == 'extract_text': outputs[f'step_{index}'] = await page.locator(step.get('selector', 'body')).all_text_contents()
                elif action == 'extract_attribute': outputs[f'step_{index}'] = await page.locator(step['selector']).get_attribute(step.get('attribute', 'href'), timeout=timeout)
                elif action == 'screenshot':
                    target = artifacts / f'workflow-{int(time.time())}-{index}.png'
                    await page.screenshot(path=str(target), full_page=True)
                    outputs[f'step_{index}'] = str(target)
                elif action == 'download_file':
                    outputs[f'step_{index}'] = 'downloads are supported through Playwright download events in custom workflows'
                else:
                    raise AutomationError(f'Unsupported browser action: {action}')
                outputs['steps'].append({'index': index, 'action': action, 'status': 'succeeded'})
        except Exception as exc:
            outputs['error'] = str(exc)
            raise
        finally:
            await context.close()
            await browser.close()
    outputs['duration_ms'] = int((time.monotonic() - started) * 1000)
    return outputs


async def run_workflow(steps: list[dict], variables: dict | None = None) -> dict:
    return await browser_run(steps, variables)
