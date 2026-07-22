"""
Thin wrapper around the official `neevai` SDK, scoped to exactly what
Srijan needs: provision an agent, drive one task on it, stream progress,
and clean up — always, even on failure.
"""
import re
import uuid
from collections.abc import Iterator
from dataclasses import dataclass

from neevai import NeevAI
from neevai.errors import APIConnectionError, APIError, APITimeoutError, NeevAIError

from src.agents.templates import AgentSpec, get_agent_spec
from src.config import settings
from src.logging import get_logger

logger = get_logger(__name__)

# Matches a GitHub PR URL anywhere in the agent's stdout, e.g.
# https://github.com/NeevCloudAI/some-repo/pull/42
_PR_URL_RE = re.compile(r"https://github\.com/[\w.\-]+/[\w.\-]+/pull/\d+")


class TransientAgentPlatformError(Exception):
    """Retryable — connection blips, 502/503/504. Caller may retry the job."""


class AgentPlatformError(Exception):
    """Non-retryable — bad request, auth failure, template not found, etc."""


def is_transient(exc: Exception) -> bool:
    if isinstance(exc, (APIConnectionError, APITimeoutError)):
        return True
    return isinstance(exc, APIError) and exc.status_code in (502, 503, 504)


@dataclass
class TaskResult:
    exit_code: int | None
    result_url: str | None      # PR link (dev) or None (debug — full log is the result)
    full_output: str


def run_agent_task(
    job_id: uuid.UUID,
    command_type: str,
    task_text: str,
    on_progress,  # Callable[[str], None] — called for each stdout chunk
) -> tuple[str, TaskResult]:
    """
    Provisions an agent, runs one task on it, streams progress via
    `on_progress`, and always deletes the agent afterwards.

    Returns (platform_agent_id, TaskResult). Raises AgentPlatformError /
    TransientAgentPlatformError on failure — caller decides how to handle
    Job/Log/Mattermost updates.
    """
    spec: AgentSpec = get_agent_spec(command_type)
    agent_name = f"srijan-{command_type}-{str(job_id)[:8]}"
    output_lines: list[str] = []

    try:
        with NeevAI(
            api_key=settings.neev_api_key,
            org_id=settings.neev_org_id,
            project_id=settings.neev_project_id,
        ) as client:
            agent = client.agents.create({
                "name": agent_name,
                "agent_template": spec.template,
                "env": [{"name": k, "value": v} for k, v in spec.env.items() if v],
                "egress": {
                    "mode": "allow_list",
                    "allow": [{"host": host} for host in spec.egress_hosts],
                },
            })

            platform_agent_id = agent.id
            logger.info(f"job {job_id}: created agent {platform_agent_id} (template={spec.template})")

            try:
                agent.wait_until_ready()
            except NeevAIError as exc:
                raise AgentPlatformError(f"agent failed to become Ready: {exc}") from exc

            on_progress("Agent is ready. Starting task…")
            sandbox = agent.sandbox()

            command = spec.build_command(task_text)
            proc = sandbox.processes.start(command)

            exit_code: int | None = None
            for event in proc.follow():
                if event["type"] == "stdout":
                    chunk = event["data"]
                    output_lines.append(chunk)
                    on_progress(chunk)
                elif event["type"] == "exit":
                    exit_code = event["exit_code"]

            full_output = "".join(output_lines)
            pr_match = _PR_URL_RE.search(full_output)
            result_url = pr_match.group(0) if pr_match else None

            return platform_agent_id, TaskResult(exit_code=exit_code, result_url=result_url, full_output=full_output)

    except NeevAIError as exc:
        if is_transient(exc):
            raise TransientAgentPlatformError(str(exc)) from exc
        raise AgentPlatformError(str(exc)) from exc


def delete_agent(platform_agent_id: str) -> None:
    """Best-effort cleanup — logs but does not raise, so a delete failure
    never masks the real outcome of a job."""
    try:
        with NeevAI(
            api_key=settings.neev_api_key,
            org_id=settings.neev_org_id,
            project_id=settings.neev_project_id,
        ) as client:
            client.agents.delete(platform_agent_id)
            logger.info(f"deleted agent {platform_agent_id}")
    except Exception:
        logger.exception(f"failed to delete agent {platform_agent_id} — may need manual cleanup")