# Hermes Agent MVP

**Project owner:** Ahmed MO Kireldin  
**Website:** [Ahmedmokireldin.online](https://Ahmedmokireldin.online)

## 📞 Official contact

- Phone: `+201012025650`
- Phone: `+201006334062`
- Email: [Ahmedmokireldin.online@gmail.com](mailto:Ahmedmokireldin.online@gmail.com)

These contact details identify the project owner and are included at the owner's request.

Hermes Agent is a self-hosted multi-agent AI platform. It routes each task to a specialist, provides controlled tools and reusable skills, evaluates outputs with a critic, and prepares safe self-improvement workflows. It supports local Mock execution, Ollama model serving, Redis/Postgres through Docker Compose, and open-weight model profiles.

> Hermes Agent is an independent project owned by **Ahmed MO Kireldin**. Third-party model weights, names, trademarks, and licenses remain with their respective owners.

> This MVP must not be exposed directly to the public internet without a reverse proxy, TLS, authentication, rate limiting, SSRF hardening, and stronger sandbox isolation.

## Components

- FastAPI: `POST /tasks`, `GET /tasks/{id}`, `GET /health`
- Async SQLAlchemy: SQLite locally or PostgreSQL through Docker
- Redis queue: optional locally and enabled in Compose
- Router / Executor / Critic: Mock by default or Ollama-backed
- Restricted tools: workspace files, Python timeout, public-only HTTP, webhook allowlist
- Independent Worker when `QUEUE_MODE=redis`
- Model profiles: `lite`, `balanced`, and `quality`
- Documented internal agent handoff contracts and permission boundaries
- External skill importer for GitHub, GitLab, Hugging Face, and explicitly allowlisted HTTPS sources

## Quick local start

```bash
cd hermes-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.api:app --reload --port 8000
```

The default local mode executes tasks inline with `MOCK_LLM=true`, so Ollama and Redis are not required.

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"input":"Calculate the occupancy rate for 18 booked nights out of 30"}'
```

If `API_KEYS` is configured, send `X-API-Key` with requests.

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Submit a task:

```bash
curl -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"input":"Draft a customer update about this week\'s bookings", "idempotency_key":"booking-001"}'
```

The API returns a task with `queued` status. Poll `GET /tasks/{id}` until it becomes `succeeded`.

## 🧠 Open model fleet

The `config/models.open.yaml` file defines the initial profiles:

| Profile | Intended use | Main models |
|---|---|---|
| `lite` | One machine or limited memory | Qwen3 4B/8B, Qwen Coder 7B, Granite 8B |
| `balanced` | Medium GPU server | Qwen3 14B, DeepSeek-R1 Distill 14B, Mistral Small 3.1 24B |
| `quality` | Strong GPU or multiple servers | Qwen3 32B, DeepSeek-R1 Distill 32B, Qwen Coder 32B |

Pull the selected models through Ollama:

```bash
PROFILE=lite ./scripts-pull-models.sh
```

Review licenses before commercial use or redistribution. Open weights do not automatically mean OSI-approved open source. See [docs-open-models.md](docs-open-models.md), [OWNER.md](OWNER.md), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

### Recommended internal chain

`👤 User → 🔐 API → ⚡ Router → 🧭 Planner → 📚 Skills → 🧩 Specialist → 🛠️ Tools → 🔎 Critic → 🗄️ Trace → 🔄 Evolver`

## Ollama

1. Run Ollama outside Compose or add an Ollama service to your environment.
2. Pull a profile with `scripts-pull-models.sh`.
3. Set `MOCK_LLM=false` and `OLLAMA_URL`.
4. Review `config/models.open.yaml` before starting production workloads.

## Project structure

```text
app/
  api.py       FastAPI endpoints
  agent.py     route → execute → critic
  db.py        SQLAlchemy models
  llm.py       Mock/Ollama gateway with model profiles
  queue.py     Redis queue adapter
  worker.py    queue worker
  skills.py    external skill importer
  tools.py     constrained tools
  evolver.py   conservative self-improvement entry point
config/        model roles and open-weight profiles
prompts/       role guidance
tests/         automated and regression tests
workspace/     confined file workspace
skills/        imported candidate skills
docs-open-models.md  model fleet and agent handoff
docs-skills.md       external skills and approval flow
docs-architecture.md architecture diagrams
docs/index.html      responsive project landing page with inline icons
```

## 🧰 External skills from GitHub and other platforms

Import an external skill as an untrusted candidate:

```bash
python scripts/import_skill.py \
  https://raw.githubusercontent.com/OWNER/REPO/main/SKILL.md \
  --name booking-followup
```

The skill is saved under `skills/candidates/` after HTTPS validation, host allowlisting, and content hashing. It is not approved and does not receive tool permissions automatically. Read [docs-skills.md](docs-skills.md).

## MVP scope and planned work

The current version provides the core path but does not yet include real pgvector retrieval, a reranker service, audio/vision service integration, full Evolver promotion, Alembic migrations, distributed leases, full rate limiting, a human approval UI, metrics export, or Firecracker isolation. Add these components after validating usage and expanding integration tests.

## Security requirements

- Never place secrets in prompts or traces.
- Never expose the API directly to the public internet.
- Use a reverse proxy, TLS, authentication, and rate limiting.
- Keep `WEBHOOK_ALLOW` empty until intended endpoints are explicitly reviewed.
- Treat all HTTP content as untrusted data.
- Use a stronger sandbox than a subprocess for untrusted code.
- Review the exact license of every model before commercial use.

## Superpower Automation Layer

Hermes now includes an integrated automation layer instead of treating scraping, browser control, and tracking as separate products:

- **Browser Automation:** Playwright/Chromium sessions with `navigate`, `click`, `fill`, `type`, `press`, `select`, `check`, `hover`, `scroll`, `wait`, `wait_for_selector`, `extract_text`, `extract_attribute`, and `screenshot` actions.
- **Open-source Scraping:** `POST /scrape` supports HTTP parsing with BeautifulSoup or browser-backed extraction for JavaScript pages. SSRF protection, public-destination checks, domain allowlists, request timeouts, and bounded output are enabled by default.
- **Workflow Engine:** Save reusable JSON workflows, pass variables such as `{{email}}`, run them through isolated browser contexts, and inspect per-step outputs and artifacts.
- **Tracking:** Every workflow run and scrape is recorded as an audit event. `GET /metrics` exposes run, action, scrape, success, and failure counters.

### Automation API examples

Create a browser workflow:

```bash
curl -X POST http://localhost:8000/workflows \
  -H 'Content-Type: application/json' \
  -d '{"name":"Public page capture","steps":[
    {"type":"navigate","url":"https://example.com"},
    {"type":"extract_text","selector":"h1"},
    {"type":"screenshot"}
  ]}'
```

Run it with variables:

```bash
curl -X POST http://localhost:8000/workflows/<WORKFLOW_ID>/runs \
  -H 'Content-Type: application/json' \
  -d '{"variables":{"email":"user@example.com"}}'
```

Scrape a public page:

```bash
curl -X POST http://localhost:8000/scrape \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","selector":"h1","extract":"text"}'
```

Read tracking data:

```bash
curl http://localhost:8000/metrics
curl 'http://localhost:8000/audit-events?limit=50'
```

For Docker, Chromium is installed automatically. For local development, install the browser once with `playwright install chromium`. Set `BROWSER_ALLOWED_DOMAINS=example.com,another-site.test` to restrict browser and scraper targets; keep `API_KEYS` enabled before exposing the API.

### Delivery roadmap

1. **Foundation:** API authentication, database migrations, structured logs, Redis queue, and worker health.
2. **Browser MVP:** Playwright sessions, action registry, artifacts, retries, approvals for sensitive actions, and live run state.
3. **Scraping scale:** Crawlee integration, pagination, deduplication, rate limits, robots policy, JSON/CSV exports, and object storage.
4. **Workflow power:** conditions, loops, branching, schedules, webhooks, versioning, templates, and n8n connector.
5. **Observability:** OpenTelemetry traces, Prometheus exporter, Grafana dashboard, alerting, retention jobs, and Sentry-compatible errors.
6. **Production hardening:** RBAC, encrypted secrets, per-project domain allowlists, SSRF regression suite, stronger sandbox isolation, load tests, and deployment documentation.

The current release is the secure, runnable foundation for this roadmap. It intentionally does not bypass CAPTCHAs, authentication controls, robots policies, or site security; use it only on systems and data you are authorized to automate.

### Recent hardening notes

- Browser workflows enforce `MAX_STEPS` before launching Chromium and validate every HTTP(S) request, including redirects and subresources, against the SSRF/domain policy.
- HTTP scraping validates each redirect, caps redirect depth at five hops, and rejects responses larger than 2 MB.
- Collection endpoints support bounded `limit` and `offset` query parameters to prevent unbounded reads: `/workflows`, `/workflows/{id}/runs`, `/schedules`, and `/audit-events`.

## Distributed Scheduler and Crawlee

The roadmap's distributed execution layer is now included as an optional Compose deployment:

- **Redis Sorted Set scheduler:** schedules are stored in `hermes:schedules` with the next execution timestamp. Workers claim due schedules using expiring Redis leases, so multiple scheduler replicas do not execute the same schedule concurrently.
- **Interval schedules:** create a workflow schedule with a minimum interval of 10 seconds. The scheduler catches up safely after downtime and records each run in the existing workflow/audit tables.
- **Crawlee worker:** the `crawler/` service uses `PlaywrightCrawler`, bounded concurrency, same-domain link discovery, max-request limits, Redis queueing, and 24-hour result retention.

Create an interval schedule:

```bash
curl -X POST http://localhost:8000/schedules \
  -H 'Content-Type: application/json' \
  -d '{"workflow_id":"<WORKFLOW_ID>","interval_seconds":3600,"variables":{"source":"hourly"}}'
```

Start a Crawlee crawl:

```bash
curl -X POST http://localhost:8000/crawl \
  -H 'Content-Type: application/json' \
  -d '{"start_urls":["https://example.com"],"selector":"main","max_requests":50}'
# Poll the returned id
curl http://localhost:8000/crawl/<CRAWL_JOB_ID>
```

Run the distributed stack:

```bash
cp .env.example .env
docker compose up --build
```

For production, scale the scheduler and crawler independently, keep `BROWSER_ALLOWED_DOMAINS` explicit, add PostgreSQL migrations before schema evolution, and place the API behind TLS, authentication, rate limiting, and an approval layer for sensitive workflows.

## Frontend Dashboard

Hermes now ships a lightweight responsive control center at `GET /dashboard/`. It is served directly by FastAPI, so it requires no separate frontend build or Node runtime for the UI.

The dashboard provides:

- Live metrics for workflow runs, browser actions, scraping requests, and uptime.
- Workflow creation from JSON action steps and one-click manual execution.
- Schedule creation with workflow selection, interval, variables, and stop controls.
- Crawlee job creation with start URLs, CSS selector, max requests, and status refresh.
- Audit activity stream with automatic refresh every 15 seconds.
- Optional API-key field persisted locally in the browser.
- Responsive dark Hermes visual system for desktop and mobile screens.

Open it after starting Hermes:

```text
http://localhost:8000/dashboard/
```

The UI uses the same API and security controls as the backend. Set `API_KEYS` before exposing it outside a trusted local network.

## Vercel deployment

Vercel can serve the Hermes FastAPI entrypoint and Dashboard for a lightweight demo. The repository now includes `vercel.json` and `api/index.py` so Vercel detects the ASGI application explicitly. Playwright is kept in `requirements-automation.txt` for Docker/local browser workers and is not installed in the Vercel Serverless build.

For a demo deployment, configure these Vercel environment variables:

```text
DATABASE_URL=postgresql+asyncpg://...
API_KEYS=your-secure-key
REDIS_URL=redis://...
QUEUE_MODE=inline
```

Use a managed PostgreSQL and Redis provider for persistent Workflows, Schedules, and Crawlee queues. Vercel's `/tmp` SQLite fallback is only a smoke-test fallback and is not durable or shared between serverless instances. The long-running `scheduler` and `crawler` services must continue to run through Docker/VM or a worker platform.
