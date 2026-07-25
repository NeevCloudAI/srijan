# Quickstart

Get Srijan running locally and receive your first "Working on it!" reply in Mattermost in under 10 minutes.

---

## Prerequisites

- Python 3.11+
- Docker + Docker Compose
- A Mattermost instance with admin access (to register slash commands)

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

Open `.env` and fill in your values:

```env
# Get this from Mattermost when you register the slash command (Step 5)
MATTERMOST_TOKEN=your_verification_token

# Get this from Mattermost bot account settings (Step 4)
MATTERMOST_BOT_TOKEN=your_bot_token
MATTERMOST_BASE_URL=https://your-mattermost-instance.com

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

Mattermost needs a public URL to send webhook requests to. Use [ngrok](https://ngrok.com) or any tunneling tool:

```bash
ngrok http 8000
```

Copy the HTTPS forwarding URL (e.g. `https://abc123.ngrok.io`) — you'll need it in the next step.

---

## Step 9 — Register slash commands in Mattermost

In your Mattermost instance, go to **Main Menu → Integrations → Slash Commands → Add Slash Command** and create two commands:

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
/neevai-dev hello world
```

You should see:

```
Working on it! I'll update this thread shortly.
```

And in your Celery worker terminal:

```
Picked up job <uuid> (dev): 'hello world'
```

That's it — the full Phase 2 flow is working end-to-end.

---

## Verify the database

```bash
PGPASSWORD=srijan psql -h localhost -U srijan -d srijan \
  -c "SELECT command_type, user_id, status, created_at FROM jobs ORDER BY created_at DESC LIMIT 5;"
```

---

## Troubleshooting

**`401 Invalid verification token`**
The `MATTERMOST_TOKEN` in your `.env` doesn't match what Mattermost is sending. Copy the token from the slash command settings page and restart the server.

**Celery worker not picking up tasks**
Make sure Redis is running (`docker compose ps`) and the worker is subscribed to the right queues (`-Q dev-queue,debug-queue`).

**`asyncpg` connection error**
Ensure PostgreSQL is running (`docker compose ps`) and `DATABASE_URL` in `.env` matches the credentials in `docker-compose.yml` (`srijan`/`srijan`).

**Port 8000 already in use**
Change the port: `uvicorn src.main:app --reload --port 8001` and update your ngrok tunnel accordingly.
