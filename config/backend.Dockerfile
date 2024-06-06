FROM python:3.12 AS base

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/backend/"
ENV VIRTUAL_ENV=/opt/venv
RUN pip install uv
RUN uv venv $VIRTUAL_ENV
ENV PATH="/opt/venv/bin:$PATH"

# Builder stage to install dependencies
# This stage is separate so if the requirements.txt file hasn't changed, it will be cached
FROM base AS builder

# RUN apt-get update \
#     && apt-get install -y curl

# ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
# RUN /install.sh && rm /install.sh

COPY ./backend/requirements.txt /backend/
WORKDIR /backend
RUN uv pip install --no-cache -r requirements.txt

# Final stage to create the runnable image with minimal size
FROM python:3.12-slim-bookworm AS final

COPY --from=builder /opt/venv /opt/venv

COPY ./config/scripts/wait-for-it.sh /scripts/wait-for-it.sh
COPY ./config/backend/run.sh /scripts/run.sh

COPY ./config/backend /config

COPY ./backend /backend

RUN useradd -ms /bin/bash app
WORKDIR /backend
RUN chown -R app:app /backend
RUN chmod 755 /backend

USER app

EXPOSE 8000

# Activate the virtualenv in the container
# See here for more information:
# https://pythonspeed.com/articles/multi-stage-docker-python/
ENV PATH="/opt/venv/bin:$PATH"

CMD /scripts/run.sh
