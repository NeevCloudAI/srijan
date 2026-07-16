import uuid

from src.db.models import Job
from src.db.sync_session import get_sync_db
from src.logging import get_logger
from src.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="workers.process_job", bind=True, max_retries=3, default_retry_delay=5, autoretry_for=(Exception,))
def process_job(self, job_id: str) -> None:
    """
    Entry point for background processing of a queued job.

    Phase 2: just prove the queue → worker → DB path works end-to-end.
    Phase 3 will replace the body with real Agent Platform provisioning.
    """
    with get_sync_db() as db:
        job = db.get(Job, uuid.UUID(job_id))
        if job is None:
            logger.error(f"process_job: job {job_id} not found")
            return

        logger.info(f"Picked up job {job.id} ({job.command_type}): {job.task_text!r}")
        job.status = "provisioning"
        db.commit()