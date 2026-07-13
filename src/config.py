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

    # ── Agent Platform ────────────────────────────────────────────────────
    agent_platform_base_url: str = ""
    agent_platform_api_key: str = ""
    agent_platform_org_id: str = ""
    agent_platform_project_id: str = ""

    # ── PostgreSQL ────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://srijan:srijan@localhost:5432/srijan"

    # ── Redis ─────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"


# Single instance imported everywhere — loaded only once at startup
settings = Settings()