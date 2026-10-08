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
PROFILE=lite ./scripts/pull-models.sh
```

Review licenses before commercial use or redistribution. Open weights do not automatically mean OSI-approved open source. See [docs/open-models.md](docs/open-models.md), [OWNER.md](OWNER.md), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

### Recommended internal chain

`👤 User → 🔐 API → ⚡ Router → 🧭 Planner → 📚 Skills → 🧩 Specialist → 🛠️ Tools → 🔎 Critic → 🗄️ Trace → 🔄 Evolver`

## Ollama

1. Run Ollama outside Compose or add an Ollama service to your environment.
2. Pull a profile with `scripts/pull-models.sh`.
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
docs/open-models.md  model fleet and agent handoff
docs/skills.md       external skills and approval flow
docs/architecture.md architecture diagrams
docs/index.html      responsive project landing page with inline icons
```

## 🧰 External skills from GitHub and other platforms

Import an external skill as an untrusted candidate:

```bash
python scripts/import_skill.py \
  https://raw.githubusercontent.com/OWNER/REPO/main/SKILL.md \
  --name booking-followup
```

The skill is saved under `skills/candidates/` after HTTPS validation, host allowlisting, and content hashing. It is not approved and does not receive tool permissions automatically. Read [docs/skills.md](docs/skills.md).

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

## Web interface

The `web/` directory contains the English landing page, operations dashboard, Models Management, and Tasks Management pages. When the API runs, FastAPI serves the interface from the same origin:

- `/` — professional landing page
- `/dashboard.html` — operations dashboard
- `/pages/models.html` — Models Management
- `/pages/tasks.html` — Tasks Management

The pages are intentionally dependency-free static HTML/CSS/JavaScript and can later be connected to the protected API endpoints.

## Arabic documentation

- [Security guide](docs/SECURITY_AR.md)
- [Architecture guide](docs/ARCHITECTURE_AR.md)
- [API reference](docs/API_REFERENCE_AR.md)
- [Security and DevOps audit](docs/AUDIT.md)
