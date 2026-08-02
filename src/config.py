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

    # OpenAI-compatible inference endpoint used by opencode agents.
    # No defaults on purpose: the opencode adapter refuses to build a spec
    # until all three are explicitly configured.
    inference_api_key: str = ""
    inference_base_url: str = ""
    inference_model: str = ""

    # Credentials injected into agent sandboxes (never logged, never hardcoded)
    github_token: str = ""              # dev agent — write access, clones repo + opens PR
    github_token_readonly: str = ""     # debug agent — read-only
    k8s_credentials: str = ""          # debug agent — short-lived read-only cluster token
    signdz_api_key: str = ""           # debug agent — platform API, read-only
    readonly_db_url: str = ""          # debug agent — read-only application DB (NOT srijan's own DB)

    # Egress allow-lists (comma-separated hostnames). Empty means "don't
    # override": the platform applies the template's default_egress
    # allow-list, which already covers model providers and toolchain hosts.
    dev_agent_egress_hosts: str = ""
    debug_agent_egress_hosts: str = ""

    # Command template run inside the agent sandbox. {task} is replaced with
    # the user's task text. Empty means "use the agent adapter's default"
    # (see src/agents/adapters/); set only to override per command type.
    dev_agent_command_template: str = ""
    debug_agent_command_template: str = ""

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