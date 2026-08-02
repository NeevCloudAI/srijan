"""
Adapter interface: everything that is specific to one agent CLI
(claude-code, opencode, …) lives behind this, so command-type policy
(credentials, egress, time limits) stays agnostic of which agent runs.
"""
from abc import ABC, abstractmethod


class AgentConfigError(Exception):
    """Raised when an adapter is used without the settings it requires."""


class AgentAdapter(ABC):
    """How to configure and drive one agent CLI inside its sandbox."""

    # Catalogue template name this adapter serves (e.g. "opencode").
    name: str

    # Command run in the sandbox for one task; {task} is substituted
    # (shell-quoted) by AgentSpec.build_command. Settings may override
    # this per command type.
    default_command_template: str

    @abstractmethod
    def env(self) -> dict[str, str]:
        """Environment variables the agent CLI needs (model/provider wiring)."""

    def setup(self) -> str:
        """Optional shell snippet run before the task command (e.g. writing
        a config file). Empty string means no setup step."""
        return ""
