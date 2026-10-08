# Hermes Agent Architecture

## System structure

```mermaid
flowchart TB
  C[Client] --> API[FastAPI]
  API --> DB[(PostgreSQL / SQLite)]
  API --> Q[(Redis Streams)]
  Q --> W[Worker]
  W --> R[Router]
  R --> S[Skill Retrieval]
  S --> E[Executor]
  E --> T[Tool Policy + Sandbox]
  E --> K[Critic]
  K --> DB
  E --> L[LLM Gateway: Mock/Ollama]
  EV[Evolver] --> DB
  EV --> TESTS[Regression + Holdout]
```

## Operational workflow

```mermaid
flowchart TD
  A[Submit] --> B[Authenticate + Validate]
  B --> C[Persist task]
  C --> D[Enqueue]
  D --> E[Claim with lease]
  E --> F[Route]
  F --> G[Retrieve skills]
  G --> H[Execute within budgets]
  H --> I{Tool call?}
  I -->|Yes| J[Validate policy / sandbox / approval]
  J --> H
  I -->|No| K[Critic evaluation]
  K --> L[Persist result and trace]
  L --> M{Reusable?}
  M -->|Yes| N[Candidate skill]
  M -->|No| O[Complete]
```

## Trust boundaries

- Model output is untrusted and must not grant itself new permissions.
- HTTP content is untrusted data and must be isolated from system instructions.
- File tools are confined to `workspace/`.
- Webhooks are restricted by `WEBHOOK_ALLOW`.
- Customer-facing actions should use a human approval layer before production.

## Current implementation status

- Implemented: FastAPI, task persistence, inline execution, Redis queue adapter, worker, Mock/Ollama gateway, routing, critic schema, file/Python/HTTP/webhook tool safeguards, Docker Compose, tests.
- Planned: pgvector retrieval, reranking service, real Evolver promotion, migrations, distributed leases, full rate limiting, approval UI, metrics export, and stronger sandbox isolation.
