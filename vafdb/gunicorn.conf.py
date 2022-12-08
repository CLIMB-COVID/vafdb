"""gunicorn WSGI server configuration."""

import os

bind = f"{os.environ['VAFDB_HOST']}:{os.environ['VAFDB_PORT']}"
loglevel = os.environ["VAFDB_GUNICORN_LOG_LEVEL"]
workers = os.environ["VAFDB_GUNICORN_WORKER_COUNT"]
timeout = os.environ["VAFDB_GUNICORN_WORKER_TIMEOUT"]
