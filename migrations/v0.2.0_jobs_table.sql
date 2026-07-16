-- Phase 2: Mattermost Integration
-- Adds the `jobs` table — one row per slash command received.
-- (agents / logs tables land in Phase 3 / Phase 4 when they're first used.)

CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- for gen_random_uuid()

CREATE TABLE IF NOT EXISTS jobs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    command_type  VARCHAR(10)  NOT NULL CONSTRAINT ck_jobs_command_type CHECK (command_type IN ('dev', 'debug')),
    user_id       VARCHAR(128) NOT NULL,
    channel_id    VARCHAR(128) NOT NULL,
    root_post_id  VARCHAR(128),
    task_text     TEXT NOT NULL,
    status        VARCHAR(20)  NOT NULL DEFAULT 'queued'
                  CONSTRAINT ck_jobs_status CHECK (status IN ('queued', 'provisioning', 'running', 'completed', 'failed', 'timed_out')),
    result_url    TEXT,
    error_message TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_jobs_status ON jobs (status);