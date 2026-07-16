import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Job(Base):
    """
    One row per slash command received from Mattermost.
    Populated by the webhook handler, updated by the Celery worker
    as the job moves through its lifecycle.
    """

    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("command_type IN ('dev', 'debug')", name="ck_jobs_command_type"),
        CheckConstraint(
            "status IN ('queued', 'provisioning', 'running', 'completed', 'failed', 'timed_out')",
            name="ck_jobs_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    command_type: Mapped[str] = mapped_column(String(10))
    user_id: Mapped[str] = mapped_column(String(128))
    channel_id: Mapped[str] = mapped_column(String(128))
    root_post_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    task_text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="queued")
    result_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)