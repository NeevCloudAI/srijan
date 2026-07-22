"""
Per-command-type configuration: which template to use, what environment
variables and egress hosts to inject, and how to build the shell command
that actually drives the agent.
"""
from dataclasses import dataclass

from src.config import settings
from src.db.constants import CommandType


@dataclass(frozen=True)
class AgentSpec:
    template: str
    env: dict[str, str]
    egress_hosts: list[str]
    command_template: str

    def build_command(self, task_text: str) -> list[str]:
        """Returns an argv-style command list, safe from shell injection —
        the task text is passed as a single argument, never interpolated
        into a shell string."""
        rendered = self.command_template.format(task=task_text)
        return ["sh", "-c", rendered]


def get_agent_spec(command_type: str) -> AgentSpec:
    if command_type == CommandType.DEV:
        return AgentSpec(
            template=settings.dev_agent_template,
            env={
                "ANTHROPIC_API_KEY": settings.neev_api_key,
                "GH_TOKEN": settings.github_token,
            },
            egress_hosts=[h.strip() for h in settings.dev_agent_egress_hosts.split(",") if h.strip()],
            command_template=settings.dev_agent_command_template,
        )
    if command_type == CommandType.DEBUG:
        return AgentSpec(
            template=settings.debug_agent_template,
            env={
                "ANTHROPIC_API_KEY": settings.neev_api_key,
                "GH_TOKEN": settings.github_token_readonly,
                "K8S_CREDENTIALS": settings.k8s_credentials,
                "SIGNDZ_API_KEY": settings.signdz_api_key,
                "READONLY_DB_URL": settings.readonly_db_url,
            },
            egress_hosts=[h.strip() for h in settings.debug_agent_egress_hosts.split(",") if h.strip()],
            command_template=settings.debug_agent_command_template,
        )
    raise ValueError(f"Unknown command_type: {command_type!r}")