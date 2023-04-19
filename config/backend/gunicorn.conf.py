from os import environ

wsgi_app = "core.asgi:application"
bind = "0.0.0.0:" + environ.get("PORT", "8000")
workers = environ.get("WORKERS", 4)
worker_class = "uvicorn.workers.UvicornWorker"
