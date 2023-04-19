#!/bin/bash

/scripts/wait-for-it.sh -t 15 $DB_HOST:$DB_PORT

if [ $DEBUG == True ]; then
    uvicorn api.app:create_app --host 0.0.0.0 --port 8000 --reload
else
    gunicorn -c /config/gunicorn.conf.py
fi