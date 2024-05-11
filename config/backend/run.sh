#!/bin/bash

/scripts/wait-for-it.sh -t 15 $DB_HOST:$DB_PORT
alembic upgrade head || exit 1

if [ $DEBUG == True ]; then
    uvicorn api.asgi:app --host 0.0.0.0 --port 8000 --reload
else
    gunicorn api.asgi:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
fi
