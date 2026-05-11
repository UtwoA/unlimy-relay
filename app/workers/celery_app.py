from celery import Celery

from app.core.config import settings

celery_app = Celery("unlimy_relay", broker=settings.celery_broker_url, backend=settings.celery_result_backend)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "health-checks-every-30s": {
            "task": "app.workers.tasks.run_health_checks",
            "schedule": 30.0,
        },
        "auto-rotation-every-5m": {
            "task": "app.workers.tasks.run_auto_rotation",
            "schedule": 300.0,
        },
    },
)
