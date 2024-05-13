FROM python:3.12

ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH "${PYTHONPATH}:/backend/"

EXPOSE 8000

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

COPY ./backend/requirements.txt /backend/
WORKDIR /backend
RUN /root/.cargo/bin/uv pip install --system --no-cache -r requirements.txt

COPY ./config/scripts/wait-for-it.sh /scripts/wait-for-it.sh
COPY ./config/backend/run.sh /scripts/run.sh

COPY ./config/backend /config

COPY ./backend /backend

CMD /scripts/run.sh
