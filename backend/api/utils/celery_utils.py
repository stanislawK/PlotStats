from functools import wraps
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar

from asgiref import sync
from celery import Celery, Task, current_app as current_celery_app

from api.settings import settings

_P = ParamSpec("_P")
_R = TypeVar("_R")


def create_celery() -> Celery:
    celery_app = current_celery_app
    celery_app.config_from_object(settings, namespace="CELERY")
    return celery_app


def async_task(app: Celery, *args: Any, **kwargs: Any) -> Task:
    def _decorator(func: Callable[_P, Coroutine[Any, Any, _R]]) -> Task:
        sync_call = sync.AsyncToSync(func)

        @app.task(*args, **kwargs)  # type: ignore
        @wraps(func)
        def _decorated(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            return sync_call(*args, **kwargs)

        return _decorated

    return _decorator
