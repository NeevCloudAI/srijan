"""
Per-command-type policy: which template to use, what credentials and
egress each task class gets, and how the final sandbox command is built.
Everything specific to a given agent CLI lives in src/agents/adapters/.
"""
import shlex
from dataclasses import dataclass

from src.agents.adapters import get_adapter
from src.config import settings
from src.db.constants import CommandType


@dataclass(frozen=True)
class AgentSpec:
    template: str
    env: dict[str, str]
    egress_hosts: list[str]
    command_template: str
    setup: str = ""

    def build_command(self, task_text: str) -> list[str]:
        """Returns an argv-style command list. `task_text` is shell-quoted
        via shlex.quote before substitution to prevent injection into the
        rendered `sh -c` string."""
        rendered = self.command_template.format(task=shlex.quote(task_text))
        if self.setup:
            rendered = f"{self.setup} && {rendered}"
        return ["sh", "-c", rendered]


def _split_hosts(raw: str) -> list[str]:
    return [h.strip() for h in raw.split(",") if h.strip()]


def get_agent_spec(command_type: str) -> AgentSpec:
    if command_type == CommandType.DEV:
        adapter = get_adapter(settings.dev_agent_template)
        return AgentSpec(
            template=adapter.name,
            env={
                **adapter.env(),
                "GH_TOKEN": settings.github_token,
            },
            egress_hosts=_split_hosts(settings.dev_agent_egress_hosts),
            command_template=settings.dev_agent_command_template or adapter.default_command_template,
            setup=adapter.setup(),
        )
    if command_type == CommandType.DEBUG:
        adapter = get_adapter(settings.debug_agent_template)
        return AgentSpec(
            template=adapter.name,
            env={
                **adapter.env(),
                "GH_TOKEN": settings.github_token_readonly,
                "K8S_CREDENTIALS": settings.k8s_credentials,
                "SIGNDZ_API_KEY": settings.signdz_api_key,
                "READONLY_DB_URL": settings.readonly_db_url,
            },
            egress_hosts=_split_hosts(settings.debug_agent_egress_hosts),
            command_template=settings.debug_agent_command_template or adapter.default_command_template,
            setup=adapter.setup(),
        )
    raise ValueError(f"Unknown command_type: {command_type!r}")
