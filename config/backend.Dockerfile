FROM python:3.11

ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH "${PYTHONPATH}:/backend/"

COPY ./backend/requirements.txt /backend/
WORKDIR /backend
RUN pip install --no-deps --no-cache-dir -r requirements.txt

COPY ./config/scripts/wait-for-it.sh /scripts/wait-for-it.sh
COPY ./config/backend/run.sh /scripts/run.sh

COPY ./config/backend /config

COPY ./backend /backend

CMD /scripts/run.sh
