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

Open `.env` and fill in the values (see `.env.example` for the full list):

```env
# Mattermost — get token from slash command settings (Step 6)
MATTERMOST_TOKEN=your_verification_token
MATTERMOST_BOT_TOKEN=your_bot_token
MATTERMOST_BASE_URL=https://your-mattermost-instance.com

# Agent Platform — NEEV_API_KEY must be a project API key created with the
# "aiagent" resource type. PATs and inference-scoped keys are rejected by
# the sandbox data plane.
NEEV_API_KEY=your_neev_api_key
NEEV_ORG_ID=your_org_id
NEEV_PROJECT_ID=your_project_id

# Which agent template each command uses (claude-code or opencode)
DEV_AGENT_TEMPLATE=opencode
DEBUG_AGENT_TEMPLATE=opencode

# Required when using the opencode template — no code defaults
INFERENCE_API_KEY=your_inference_api_key
INFERENCE_BASE_URL=https://inference.ai.neevcloud.com/v1
INFERENCE_MODEL=minimax-m3
```

`DATABASE_URL` and `REDIS_URL` can be left unset — docker compose points the
app containers at the bundled Postgres and Redis.

---

## Step 3 — Start the full stack

```bash
docker compose up -d --build
```

This builds the app image and starts four containers: PostgreSQL (with the
SQL files in `migrations/` applied automatically on first boot), Redis, the
webhook server on port 8000, and the Celery worker.

If a host port is already taken, override it, e.g.:

```bash
SRIJAN_POSTGRES_HOST_PORT=5434 docker compose up -d --build
```

> Migrations only run when the Postgres data volume is created. After pulling
> new migration files, apply them manually with psql or reset with
> `docker compose down -v`.

---

## Step 4 — Verify everything is up

```bash
docker compose ps
```

All four containers should be `Up` (postgres and redis `healthy`). Then:

```bash
curl http://localhost:8000/health
# {"status": "ok", "service": "srijan"}
```

```bash
docker compose logs worker | grep ready
# celery@<container> ready.
```

---

## Step 5 — Expose your local server to Mattermost

Mattermost needs a public URL to POST webhook requests to. Use [ngrok](https://ngrok.com):

```bash
ngrok http 8000
```

Copy the HTTPS forwarding URL (e.g. `https://abc123.ngrok.io`) — you need it in the next step.

---

## Step 6 — Register slash commands in Mattermost

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

## Step 7 — Test it

In any Mattermost channel, type:

```
/neevai-dev fix the login 404 bug
```

**You should see in Mattermost (immediate, < 3 seconds):**
```
Working on it! I'll update this thread shortly.
```

**You should see in the webhook server logs (`docker compose logs webhook-server`):**
```
INFO: POST /webhook/dev → 200
```

**You should see in the Celery worker logs (`docker compose logs worker`):**
```
Picked up job <uuid> (dev): 'fix the login 404 bug'
INFO: Provisioning agent for job <uuid>
INFO: Agent <platform_agent_id> status: Provisioning
INFO: Agent <platform_agent_id> status: Ready
INFO: Agent connected — task running
INFO: Agent deleted after completion
```

---

## Step 8 — Verify the database

```bash
docker exec srijan_postgres psql -U srijan -d srijan \
  -c "SELECT command_type, status, created_at FROM jobs ORDER BY created_at DESC LIMIT 5;"
```

```bash
docker exec srijan_postgres psql -U srijan -d srijan \
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
Verify `NEEV_API_KEY`, `NEEV_ORG_ID`, and `NEEV_PROJECT_ID` are all set correctly in `.env`. A `401` on the sandbox data plane means the key isn't an `aiagent`-scoped project API key.

**Agent stuck in `Provisioning`**
The Agent Platform may be slow or rate-limiting. The worker polls every 10 seconds with a 15-minute hard timeout — check the Celery worker logs for polling status.

**`asyncpg` connection error**
Ensure PostgreSQL is running (`docker compose ps`) and `DATABASE_URL` matches the credentials in `docker-compose.yml` (`srijan`/`srijan`).

**Host port already in use**
Override the published port(s): `SRIJAN_API_HOST_PORT=8001 docker compose up -d`
(also available: `SRIJAN_POSTGRES_HOST_PORT`, `SRIJAN_REDIS_HOST_PORT`). Update
your ngrok tunnel if you changed the API port.