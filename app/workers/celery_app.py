from celery import Celery

celery_app = Celery(
    "online_cinema",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)
