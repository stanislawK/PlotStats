#!/bin/bash

# Run both celery and celery beat in one container

# Start Celery worker in the background
celery -A api.asgi.celery worker --concurrency=1 -l INFO &

# Start Celery beat in the foreground
celery -A api.asgi.celery beat -S redbeat.RedBeatScheduler --max-interval 30 -l INFO
