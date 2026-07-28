-- Phase 3: Agent Platform Integration
-- Adds `agents` (one row per provisioned agent, linked to its job) and
-- `logs` (streamed progress history) — deferred from Phase 2 per the
-- original schema comment.

CREATE TABLE IF NOT EXISTS agents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id              UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    platform_agent_id   VARCHAR(256) NOT NULL,
    template_name       VARCHAR(128) NOT NULL,
    status              VARCHAR(20)  NOT NULL DEFAULT 'Provisioning'
                        CONSTRAINT ck_agents_status CHECK (status IN ('Provisioning', 'Ready', 'Paused', 'Failed', 'Deleting', 'Deleted')),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_agents_job_id ON agents (job_id);

CREATE TABLE IF NOT EXISTS logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id      UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    message     TEXT NOT NULL,
    source      VARCHAR(20) NOT NULL DEFAULT 'system'
               CONSTRAINT ck_logs_source CHECK (source IN ('agent', 'system')),
    logged_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_logs_job_id ON logs (job_id);