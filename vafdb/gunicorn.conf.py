"""gunicorn WSGI server configuration."""

# Change these settings to suit your application!
bind = f"localhost:8000"
loglevel = "DEBUG"
workers = 10
timeout = 120
