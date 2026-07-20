from celery import Celery

from src.config import settings

celery_app = Celery(
    "srijan",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.workers.tasks"],
)

celery_app.conf.update(
    # dev-queue / debug-queue are chosen per-call via apply_async in webhooks.py
    task_default_queue="dev-queue",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)