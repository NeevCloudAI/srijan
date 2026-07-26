# Srijan

An AI-powered engineering assistant for chat platforms.

Srijan lets engineers delegate routine coding and debugging tasks to autonomous AI agents via simple slash commands — without leaving their chat window. Type a command, get an acknowledgment in under 3 seconds, and receive the result (a PR link or diagnosis report) directly in the thread.

---

## How it works

```
Engineer types /neevai-dev fix the login 404 bug
        ↓
Srijan acknowledges instantly ("Working on it!")       ← Phase 2
        ↓
Background worker provisions a sandboxed AI agent      ← Phase 3
        ↓
Agent executes the task, Srijan streams progress       ← Phase 4 (upcoming)
        ↓
Engineer receives a PR link or diagnosis in the thread ← Phase 4 (upcoming)
        ↓
Agent is safely destroyed                              ← Phase 3
```

---

## Commands

| Command | Purpose | Output |
|---|---|---|
| `/neevai-dev <task>` | Coding tasks — bug fixes, small features, documentation | GitHub Pull Request link |
| `/neevai-debug <issue>` | Debugging — root cause analysis, log inspection, API diagnosis | Structured diagnosis report |

---

## Architecture

Srijan is composed of five components:

| Component | Technology | Role | Status |
|---|---|---|---|
| Webhook Server | FastAPI | Receives slash commands, validates token, returns instant ACK | ✅ Done (Phase 2) |
| Task Queue | Redis | Broker between webhook server and background workers | ✅ Done (Phase 2) |
| Background Worker | Celery | Provisions agents, polls status, manages full lifecycle | ✅ Done (Phase 3) |
| Database | PostgreSQL | Audit log of every job, agent, and progress message | ✅ Done (Phase 2 & 3) |
| Chat Bot | httpx (Mattermost API) | Posts acknowledgments, progress, and results back to thread | 🔜 Phase 4 |

---

## Implementation Progress

| Phase | Name | Status | Key Deliverable |
|---|---|---|---|
| 1 | Foundation | ✅ Complete | Repo setup, FastAPI skeleton, health endpoint, Docker Compose |
| 2 | Mattermost Integration | ✅ Complete | Slash command endpoints, token validation, instant ACK, job persistence, Celery enqueue |
| 3 | Agent Platform Integration | ✅ Complete | Agent create → poll → connect → delete lifecycle, DB updated at each state |
| 4 | Streaming & Result Delivery | 🔜 Upcoming | Real-time progress streamed to thread, PR link / diagnosis posted |
| 5 | Hardening & Deployment | 🔜 Upcoming | Error handling, retries, timeouts, tests, Dockerfile, K8s manifests |

---

## Project Structure

```
srijan/
├── migrations/
│   └── v0.1.0_initial_schema.sql       # jobs, agents, logs tables
│
├── src/
│   ├── config.py                        # pydantic-settings — loaded once at startup
│   ├── logging.py                       # structured logging setup
│   ├── main.py                          # FastAPI app entrypoint
│   │
│   ├── api/routes/
│   │   ├── health.py                    # GET /health
│   │   └── webhooks.py                  # POST /webhook/dev, POST /webhook/debug
│   │
│   ├── agents/                          # Agent Platform integration (Phase 3)
│   │   ├── client.py                    # httpx client — create/poll/connect/delete agents
│   │   └── lifecycle.py                 # Full agent lifecycle orchestration
│   │
│   ├── chat/                            # Mattermost integration (Phase 2)
│   │   ├── client.py                    # Bot client — posts messages to threads
│   │   └── security.py                  # Token validation
│   │
│   ├── db/                              # PostgreSQL layer
│   │   ├── constants.py                 # CommandType, JobStatus enums
│   │   ├── models.py                    # SQLAlchemy Job, Agent, Log models
│   │   ├── session.py                   # Async engine (FastAPI)
│   │   └── sync_session.py              # Sync engine (Celery workers)
│   │
│   └── workers/
│       ├── celery_app.py                # Celery app definition
│       └── tasks.py                     # process_job task — drives agent lifecycle
│
├── docs/rfcs/
│   ├── 001_initial_design.md            # Full system design
│   └── 002_code_organization.md         # Directory layout decisions
│
├── .env.example                         # Environment variable template
├── docker-compose.yml                   # PostgreSQL + Redis for local dev
├── QUICKSTART.md                        # Step-by-step local setup guide
└── pyproject.toml                       # Dependencies
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `MATTERMOST_TOKEN` | Slash command verification token from Mattermost |
| `MATTERMOST_BOT_TOKEN` | Bot account token for posting outbound messages |
| `MATTERMOST_BASE_URL` | Your Mattermost instance URL |
| `DATABASE_URL` | PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `REDIS_URL` | Redis connection string (`redis://...`) |
| `AGENT_PLATFORM_BASE_URL` | Agent Platform API base URL |
| `AGENT_PLATFORM_API_KEY` | Agent Platform API key |
| `AGENT_PLATFORM_ORG_ID` | Agent Platform organisation ID |
| `AGENT_PLATFORM_PROJECT_ID` | Agent Platform project ID |
| `APP_ENV` | `development` or `production` |
| `LOG_LEVEL` | `INFO`, `DEBUG`, etc. |

See `.env.example` for the full template.

---

## Local Development

See [QUICKSTART.md](QUICKSTART.md) for step-by-step setup instructions.

---

## Documentation

- [Initial Design RFC](docs/rfcs/001_initial_design.md) — problem statement, goals, architecture, API contracts, database schema
- [Code Organization RFC](docs/rfcs/002_code_organization.md) — directory layout and naming decisions