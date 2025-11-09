#!/usr/bin/env bash
# Render start script - runs after build.sh completes

set -o errexit

echo "🔄 Waiting for database connection..."
python manage.py wait_for_db

echo "🗃️ Running database migrations..."
python manage.py migrate --noinput

echo "📧 Creating missing EmailAddress records..."
python manage.py create_missing_emailaddress

echo "� Activating verified users..."
python manage.py fix_inactive_users

echo "�🚀 Starting Gunicorn server..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers ${GUNICORN_WORKERS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-300} \
    --log-level ${GUNICORN_LOG_LEVEL:-info} \
    --access-logfile - \
    --error-logfile -
