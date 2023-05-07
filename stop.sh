#!/usr/bin/env bash
pkill -f "gunicorn vafdb.wsgi"
pkill -f "celery -A vafdb"
echo "VAFDB stopped."
