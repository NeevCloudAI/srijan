# Srijan

An AI-powered engineering assistant for chat platforms.

Srijan lets engineers delegate routine coding and debugging tasks to autonomous AI agents via simple slash commands — without leaving their chat window. Type a command, get an acknowledgment in under 3 seconds, and receive the result (a PR link or diagnosis report) directly in the thread.

---

## How it works

```
Engineer types /neevai-dev fix the login 404 bug
        ↓
Srijan acknowledges instantly ("Working on it!")
        ↓
Background worker provisions a sandboxed AI agent
        ↓
Agent executes the task, Srijan streams progress to the thread
        ↓
Engineer receives a PR link or diagnosis report in the thread
        ↓
Agent is safely destroyed
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

| Component | Technology | Role |
|---|---|---|
| Webhook Server | FastAPI | Receives slash commands, validates token, returns instant ACK |
| Task Queue | Redis | Broker between webhook server and background workers |
| Background Worker | Celery | Provisions agents, streams progress, delivers results |
| Database | PostgreSQL | Audit log of every job, agent, and progress message |
| Chat Bot | httpx (Mattermost API) | Posts acknowledgments, progress, and results back to thread |

---

## Project Structure

```
srijan/
├── migrations/                         # SQL migrations (run in order)
│   └── v0.1.0_initial_schema.sql
│
├── src/
│   ├── config.py                       # pydantic-settings — loaded once at startup
│   ├── logging.py                      # structured logging setup
│   ├── main.py                         # FastAPI app entrypoint
│   │
│   ├── api/routes/                     # Webhook endpoints
│   │   ├── health.py                   # GET /health
│   │   └── webhooks.py                 # POST /webhook/dev, POST /webhook/debug
│   │
│   ├── chat/                           # Mattermost integration
│   │   ├── client.py                   # Bot client — posts messages to threads
│   │   └── security.py                 # Token validation
│   │
│   ├── db/                             # PostgreSQL layer
│   │   ├── constants.py                # CommandType, JobStatus enums
│   │   ├── models.py                   # SQLAlchemy Job model
│   │   ├── session.py                  # Async engine (FastAPI)
│   │   └── sync_session.py             # Sync engine (Celery workers)
│   │
│   └── workers/                        # Background processing
│       ├── celery_app.py               # Celery app definition
│       └── tasks.py                    # process_job task
│
├── docs/rfcs/
│   ├── 001_initial_design.md           # Full system design
│   └── 002_code_organization.md        # Directory layout decisions
│
├── .env.example                        # Environment variable template
├── docker-compose.yml                  # PostgreSQL + Redis for local dev
└── pyproject.toml                      # Dependencies
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
| `APP_ENV` | `development` or `production` |
| `LOG_LEVEL` | `INFO`, `DEBUG`, etc. |

See `.env.example` for a full template.

---

## Local Development

See [QUICKSTART.md](QUICKSTART.md) for step-by-step setup instructions.

---

## Documentation

- [Initial Design RFC](docs/rfcs/001_initial_design.md) — problem statement, goals, architecture, API contracts
- [Code Organization RFC](docs/rfcs/002_code_organization.md) — directory layout and naming decisions
