# Quickstart

Get Srijan running locally end-to-end — from slash command to a provisioned AI agent — in under 15 minutes.

> **Current state (Phase 3 complete):** Slash commands are received, acknowledged instantly, persisted to the database, and handed off to a Celery worker that drives the full Agent Platform lifecycle (create → poll → connect → delete). Progress streaming and result delivery to Mattermost come in Phase 4.

---

## Prerequisites

- Python 3.11+
- Docker + Docker Compose
- A Mattermost instance with admin access (to register slash commands)
- Agent Platform credentials (base URL, API key, org ID, project ID)

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/NeevCloudAI/srijan.git
cd srijan
```

---

## Step 2 — Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in all values:

```env
# Mattermost — get token from slash command settings (Step 9)
MATTERMOST_TOKEN=your_verification_token
MATTERMOST_BOT_TOKEN=your_bot_token
MATTERMOST_BASE_URL=https://your-mattermost-instance.com

# Agent Platform
AGENT_PLATFORM_BASE_URL=https://api.your-agent-platform.com
AGENT_PLATFORM_API_KEY=your_api_key
AGENT_PLATFORM_ORG_ID=your_org_id
AGENT_PLATFORM_PROJECT_ID=your_project_id

# Leave as-is for local dev (matches docker-compose.yml)
DATABASE_URL=postgresql+asyncpg://srijan:srijan@localhost:5432/srijan
REDIS_URL=redis://localhost:6379/0

APP_ENV=development
LOG_LEVEL=INFO
```

---

## Step 3 — Start PostgreSQL and Redis

```bash
docker compose up -d
```

Verify both are running:

```bash
docker compose ps
```

---

## Step 4 — Apply the database migration

```bash
PGPASSWORD=srijan psql -h localhost -U srijan -d srijan -f migrations/v0.1.0_initial_schema.sql
```

Expected output:
```
CREATE EXTENSION
CREATE TABLE   ← jobs
CREATE TABLE   ← agents
CREATE TABLE   ← logs
CREATE INDEX
```

---

## Step 5 — Install dependencies

```bash
pip install -e .
```

---

## Step 6 — Start the webhook server

```bash
uvicorn src.main:app --reload --port 8000
```

Verify it's up:

```bash
curl http://localhost:8000/health
# {"status": "ok", "service": "srijan"}
```

---

## Step 7 — Start the Celery worker

Open a second terminal in the same directory:

```bash
celery -A src.workers.celery_app worker -Q dev-queue,debug-queue --loglevel=info
```

You should see:
```
[tasks]
  . workers.process_job

[celery@hostname ready.]
```

---

## Step 8 — Expose your local server to Mattermost

Mattermost needs a public URL to POST webhook requests to. Use [ngrok](https://ngrok.com):

```bash
ngrok http 8000
```

Copy the HTTPS forwarding URL (e.g. `https://abc123.ngrok.io`) — you need it in the next step.

---

## Step 9 — Register slash commands in Mattermost

Go to **Main Menu → Integrations → Slash Commands → Add Slash Command** and create two commands:

**Command 1 — Dev:**

| Field | Value |
|---|---|
| Command Trigger Word | `neevai-dev` |
| Request URL | `https://abc123.ngrok.io/webhook/dev` |
| Request Method | `POST` |
| Response Username | `srijan-bot` |

**Command 2 — Debug:**

| Field | Value |
|---|---|
| Command Trigger Word | `neevai-debug` |
| Request URL | `https://abc123.ngrok.io/webhook/debug` |
| Request Method | `POST` |
| Response Username | `srijan-bot` |

After saving each command, Mattermost shows a **Verification Token**. Copy it and set it as `MATTERMOST_TOKEN` in your `.env`, then restart the webhook server.

---

## Step 10 — Test it

In any Mattermost channel, type:

```
/neevai-dev fix the login 404 bug
```

**You should see in Mattermost (immediate, < 3 seconds):**
```
Working on it! I'll update this thread shortly.
```

**You should see in the webhook server terminal:**
```
INFO: POST /webhook/dev → 200
```

**You should see in the Celery worker terminal:**
```
Picked up job <uuid> (dev): 'fix the login 404 bug'
INFO: Provisioning agent for job <uuid>
INFO: Agent <platform_agent_id> status: Provisioning
INFO: Agent <platform_agent_id> status: Ready
INFO: Agent connected — task running
INFO: Agent deleted after completion
```

---

## Step 11 — Verify the database

```bash
PGPASSWORD=srijan psql -h localhost -U srijan -d srijan \
  -c "SELECT command_type, status, created_at FROM jobs ORDER BY created_at DESC LIMIT 5;"
```

```bash
PGPASSWORD=srijan psql -h localhost -U srijan -d srijan \
  -c "SELECT job_id, platform_agent_id, status FROM agents ORDER BY created_at DESC LIMIT 5;"
```

---

## What's working now (Phase 3 complete)

| Step | What happens |
|---|---|
| Slash command received | Token validated, `401` returned on mismatch |
| Instant ACK | "Working on it!" returned within 3 seconds — always |
| Job persisted | Row created in `jobs` table with `status=queued` |
| Task enqueued | `process_job` task sent to `dev-queue` or `debug-queue` |
| Agent provisioned | Worker calls Agent Platform to create a sandboxed agent |
| Agent polled | Worker polls every 10 seconds until agent is `Ready` or times out |
| Agent connected | Worker mints a connection token and connects to the agent |
| Agent destroyed | Worker calls Agent Platform to delete the agent after task |
| DB updated | `jobs` and `agents` tables updated at every state transition |

---

## What's coming next (Phase 4)

- Real-time progress streamed from the agent back to the Mattermost thread
- PR link posted to thread on `/neevai-dev` completion
- Diagnosis report posted to thread on `/neevai-debug` completion

---

## Troubleshooting

**`401 Invalid verification token`**
The `MATTERMOST_TOKEN` in `.env` doesn't match what Mattermost sends. Copy the token from the slash command settings page and restart the server.

**Celery worker not picking up tasks**
Check Redis is running (`docker compose ps`) and the worker is subscribed to both queues (`-Q dev-queue,debug-queue`).

**Agent Platform connection error**
Verify `AGENT_PLATFORM_BASE_URL`, `AGENT_PLATFORM_API_KEY`, `AGENT_PLATFORM_ORG_ID`, and `AGENT_PLATFORM_PROJECT_ID` are all set correctly in `.env`.

**Agent stuck in `Provisioning`**
The Agent Platform may be slow or rate-limiting. The worker polls every 10 seconds with a 15-minute hard timeout — check the Celery worker logs for polling status.

**`asyncpg` connection error**
Ensure PostgreSQL is running (`docker compose ps`) and `DATABASE_URL` matches the credentials in `docker-compose.yml` (`srijan`/`srijan`).

**Port 8000 already in use**
Change the port: `uvicorn src.main:app --reload --port 8001` and update your ngrok tunnel.