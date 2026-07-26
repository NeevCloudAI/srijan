from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for Srijan.
    All values are loaded from environment variables or the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ───────────────────────────────────────────────────────────────
    app_env: str = "development"
    log_level: str = "INFO"

    # ── Mattermost ────────────────────────────────────────────────────────
    mattermost_token: str = ""
    mattermost_bot_token: str = ""
    mattermost_base_url: str = ""

    # ── Agent Platform (NeevCloud Agentic Studio, via neevai SDK) ─────────
    neev_api_key: str = ""
    neev_org_id: str = ""
    neev_project_id: str = ""
    neev_base_url: str = "https://api.ai.neevcloud.com/agent"

    dev_agent_template: str = "claude-code"
    debug_agent_template: str = "claude-code"

    # Credentials injected into agent sandboxes (never logged, never hardcoded)
    github_token: str = ""              # dev agent — write access, clones repo + opens PR
    github_token_readonly: str = ""     # debug agent — read-only
    k8s_credentials: str = ""          # debug agent — short-lived read-only cluster token
    signdz_api_key: str = ""           # debug agent — platform API, read-only
    readonly_db_url: str = ""          # debug agent — read-only application DB (NOT srijan's own DB)

    # Egress allow-lists (comma-separated hostnames)
    dev_agent_egress_hosts: str = "github.com,api.anthropic.com"
    debug_agent_egress_hosts: str = "api.anthropic.com"

    # Command templates — {task} is replaced with shlex.quote(task_text).
    # Do NOT wrap {task} in quotes here — shlex.quote already does that.
    dev_agent_command_template: str = "claude-code --print {task}"
    debug_agent_command_template: str = "claude-code --print {task}"

    # Hard ceiling on how long a single job may run (Celery task time limit)
    agent_task_time_limit_seconds: int = 900        # 15 minutes, per design doc
    agent_task_soft_time_limit_seconds: int = 870
    agent_ready_poll_interval_seconds: int = 10

    # ── PostgreSQL ────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://srijan:srijan@localhost:5432/srijan"

    # ── Redis ─────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"


# Single instance imported everywhere — loaded only once at startup
settings = Settings()