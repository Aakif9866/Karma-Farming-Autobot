from celery import Celery

from app.core.settings import get_settings

celery_app = Celery("kfa", broker=get_settings().redis_url)
celery_app.conf.update(
    timezone="Asia/Kolkata",  # ADR-011: schedules in IST
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={},  # periodic jobs arrive in Phase 2
)


@celery_app.task(name="system.ping")  # type: ignore[untyped-decorator]  # celery is untyped
def ping() -> str:
    return "pong"
