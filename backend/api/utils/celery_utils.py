from celery import Celery, current_app as current_celery_app

from api.settings import settings


def create_celery() -> Celery:
    celery_app = current_celery_app
    celery_app.config_from_object(settings, namespace="CELERY")

    return celery_app
