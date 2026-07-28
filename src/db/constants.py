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

class AgentStatus(StrEnum):
    """Mirrors the NeevCloud Agent Platform's AgentStatus enum exactly."""
    PROVISIONING = "Provisioning"
    READY = "Ready"
    PAUSED = "Paused"
    FAILED = "Failed"
    DELETING = "Deleting"
    DELETED = "Deleted"  # local-only terminal state