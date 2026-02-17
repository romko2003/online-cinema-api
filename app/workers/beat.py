from app.workers.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "cleanup-activation-tokens-every-hour": {
        "task": "app.workers.tasks.accounts.cleanup_expired_activation_tokens",
        "schedule": 3600.0,
    },
    "cleanup-password-reset-tokens-every-hour": {
        "task": "app.workers.tasks.accounts.cleanup_expired_password_reset_tokens",
        "schedule": 3600.0,
    },
}
