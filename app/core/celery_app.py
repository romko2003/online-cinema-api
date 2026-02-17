from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery = Celery(
    "cinema",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.cleanup_tokens",
    ],
)

celery.conf.update(
    timezone="UTC",
    enable_utc=True,
)

# Periodic tasks (celery beat)
celery.conf.beat_schedule = {
    # every 10 minutes cleanup expired tokens
    "cleanup-expired-tokens-every-10-min": {
        "task": "app.tasks.cleanup_tokens.cleanup_expired_tokens",
        "schedule": 600.0,
    },
}
