from typing import Any

from celery import current_app as celery_app
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry


def setup_scan_periodic_task(
    url: str, schedule_input: dict[str, Any], search_id: int
) -> None:
    entry = RedBeatSchedulerEntry(
        name=url,
        task="api.periodic_tasks.run_periodic_scan",
        schedule=crontab(**schedule_input),
        args=[url, search_id],
        kwargs={"schedule_name": url},
        app=celery_app,
    )
    entry.save()


def remove_scan_periodic_task(url: str) -> None:
    entry = None
    try:
        entry = RedBeatSchedulerEntry.from_key(f"redbeat:{url}", app=celery_app)
    except KeyError:
        pass
    if entry:
        entry.delete()
