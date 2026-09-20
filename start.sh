#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1

echo "Running database migrations..."
python manage.py migrate --noinput
python manage.py import_homeworkpal_payments --if-configured

echo "Starting Gunicorn..."
exec gunicorn core.wsgi:application   --bind 0.0.0.0:${PORT:-10000}   --workers ${GUNICORN_WORKERS:-2}   --timeout ${GUNICORN_TIMEOUT:-300}   --log-level ${GUNICORN_LOG_LEVEL:-info}   --access-logfile -   --error-logfile -
