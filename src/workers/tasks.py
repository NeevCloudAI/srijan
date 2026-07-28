from amqp import basic_message
import uuid

from celery.exceptions import SoftTimeLimitExceeded



from src.agents.client import (
    AgentPlatformError,
    TransientAgentPlatformError,
    delete_agent,
    run_agent_task,
)
from src.agents.templates import get_agent_spec
from src.chat.client import MattermostClient
from src.config import settings
from src.db.constants import AgentStatus, JobStatus
from src.db.models import Agent, Job, Log, _utcnow
from src.db.models import Agent, Job, Log, _utcnow
from src.db.sync_session import get_sync_db
from src.logging import get_logger
from src.workers.celery_app import celery_app

logger = get_logger(__name__)

# Batch progress updates so we don't spam Mattermost with one message per
# stdout line — flush every N characters or on exit, whichever comes first.
_PROGRESS_FLUSH_THRESHOLD = 400


@celery_app.task(
    name="workers.process_job",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(TransientAgentPlatformError,),  # only retry network blips —
    # business-logic failures (bad template, auth) are handled explicitly below
    # and must NOT be blindly retried, or we'd spawn duplicate agents.
    time_limit=settings.agent_task_time_limit_seconds,
    soft_time_limit=settings.agent_task_soft_time_limit_seconds,
)
def process_job(self, job_id: str) -> None:
    """Drives a single job end-to-end: provisions an agent, streams its
    output to the originating Mattermost thread, records the outcome in
    the database, and always cleans up the agent afterwards."""
    with get_sync_db() as db:
        job = db.get(Job, uuid.UUID(job_id))
        if job is None:
            logger.error(f"process_job: job {job_id} not found")
            return

        mm = MattermostClient()
        platform_agent_id: str | None = None
        buffer: list[str] = []
        buffer_len = 0

        def log_and_stream(message: str, source: str = "system") -> None:
            """Persist a log line to the `logs` table for this job."""
            db.add(Log(job_id=job.id, message=message, source=source))
            db.commit()

        def flush_progress(force: bool = False) -> None:
            """Post buffered agent output to Mattermost once the threshold is hit
            (or immediately if `force=True`), then clear the buffer."""
            nonlocal buffer, buffer_len
            if not buffer or (buffer_len < _PROGRESS_FLUSH_THRESHOLD and not force):
                return
            chunk = "".join(buffer)
            buffer, buffer_len = [], 0
            mm.post_message(job.channel_id, chunk, root_id=job.root_post_id)
            log_and_stream(chunk, source="agent")

        def on_progress(text: str) -> None:
            """Callback passed to run_agent_task — buffers streamed stdout chunks
            and triggers a flush once enough output has accumulated."""
            nonlocal buffer, buffer_len
            buffer.append(text)
            buffer_len += len(text)
            flush_progress()

        try:
            logger.info(f"Picked up job {job.id} ({job.command_type}): {job.task_text!r}")
            job.status = JobStatus.PROVISIONING
            db.commit()
            log_and_stream("Provisioning agent…")

            platform_agent_id, resolved_template, result = run_agent_task(
                job_id=job.id,
                command_type=job.command_type,
                task_text=job.task_text,
                on_progress=on_progress,
            )

            # Fix: store the actual template used, not the command type string
            actual_template = get_agent_spec(job.command_type).template
            db.add(Agent(
                job_id=job.id,
                platform_agent_id=platform_agent_id,
                template_name=resolved_template,
                status=AgentStatus.READY,
            ))
            job.status = JobStatus.RUNNING
            db.commit()

            flush_progress(force=True)

            if result.exit_code == 0:
                job.status = JobStatus.COMPLETED
                job.result_url = result.result_url
                final_message = (
                    f"Done! Here's your PR: {result.result_url}"
                    if job.command_type == "dev" and result.result_url
                    else "Task completed. See the thread above for the full output."
                )
            else:
                job.status = JobStatus.FAILED
                job.error_message = f"Task exited with code {result.exit_code}"
                final_message = f"Task failed (exit code {result.exit_code}). See the thread above for details."

            mm.post_message(job.channel_id, final_message, root_id=job.root_post_id)
            log_and_stream(final_message)

        except SoftTimeLimitExceeded:
            job.status = JobStatus.TIMED_OUT
            job.error_message = f"Exceeded {settings.agent_task_time_limit_seconds}s time limit"
            mm.post_message(job.channel_id, "⏱️ This task took too long and was stopped.", root_id=job.root_post_id)
            log_and_stream("Task timed out.")

        except TransientAgentPlatformError:
            # Re-raise so Celery's autoretry_for wrapper can retry the task.
            # Do NOT mark the job FAILED here — a fresh attempt is coming.
            raise

        except AgentPlatformError as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            mm.post_message(job.channel_id, f"Something went wrong provisioning the agent: {exc}", root_id=job.root_post_id)
            log_and_stream(f"Agent platform error: {exc}")

        except Exception as exc:
            # Catch-all: any unexpected bug must still mark the job failed
            # and clean up — never leave it stuck in provisioning/running.
            logger.exception(f"job {job.id}: unexpected error in process_job")
            job.status = JobStatus.FAILED
            job.error_message = f"Unexpected error: {exc}"
            mm.post_message(job.channel_id, "Something unexpected went wrong. The team has been notified.", root_id=job.root_post_id)
            log_and_stream(f"Unexpected error: {exc}")

        finally:
            if platform_agent_id:
                delete_agent(platform_agent_id)
                # Fix: stamp deleted_at so the column is never left NULL
                db.query(Agent).filter(Agent.platform_agent_id == platform_agent_id).update(
                    {"status": AgentStatus.DELETED, "deleted_at": _utcnow()}
                )
            db.commit()