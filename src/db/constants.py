from enum import StrEnum


class CommandType(StrEnum):
    """Slash command types."""
    DEV = "dev"
    DEBUG = "debug"


class JobStatus(StrEnum):
    """Job lifecycle states."""
    QUEUED = "queued"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"