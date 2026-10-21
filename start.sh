#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
PYTHON_BIN="$(command -v python3 || command -v python)"

echo "Running database migrations..."
"$PYTHON_BIN" manage.py migrate --noinput
"$PYTHON_BIN" manage.py seed_orbit_production
"$PYTHON_BIN" manage.py check
"$PYTHON_BIN" manage.py import_homeworkpal_payments --if-configured
"$PYTHON_BIN" manage.py smoke_service_requests
"$PYTHON_BIN" manage.py smoke_humanizer_platform
"$PYTHON_BIN" manage.py smoke_google_oauth
"$PYTHON_BIN" manage.py smoke_identity_email
"$PYTHON_BIN" manage.py shell -c "from django.conf import settings; from pathlib import Path; print('Payment config: secret=%s public=%s apple_domain=%s' % ('yes' if settings.PAYSTACK_SECRET_KEY else 'no', 'yes' if settings.PAYSTACK_PUBLIC_KEY else 'no', 'yes' if (settings.BASE_DIR / 'static' / 'apple-developer-merchantid-domain-association').exists() else 'no'))"
"$PYTHON_BIN" manage.py shell -c "from django.conf import settings; print('Google OAuth config: client_id=%s client_secret=%s' % ('yes' if settings.GOOGLE_CLIENT_ID else 'no', 'yes' if settings.GOOGLE_CLIENT_SECRET else 'no'))"
"$PYTHON_BIN" manage.py shell -c "from django.conf import settings; backend=settings.HUMANIZER_BACKEND; key_ready=bool(settings.OPENROUTER_API_KEY) if backend == 'openrouter' else bool(settings.OPENAI_API_KEY) if backend == 'openai' else False; print('Humanizer config: backend=%s key=%s model=%s batch=%s concurrency=%s provider_sort=%s strength=%s anon_daily_words=%s' % (backend, 'yes' if key_ready else 'no', settings.HUMANIZER_MODEL_ID, settings.HUMANIZER_SENTENCE_BATCH_SIZE, settings.HUMANIZER_MAX_CONCURRENCY, settings.HUMANIZER_PROVIDER_SORT, settings.HUMANIZER_DEFAULT_STRENGTH, settings.HUMANIZER_ANON_DAILY_WORDS))"
"$PYTHON_BIN" manage.py shell -c "from django.conf import settings; print('Email config: recipient=%s brevo_api=%s sender=%s' % (settings.SUPPORT_EMAIL, 'yes' if settings.BREVO_API_KEY else 'no', settings.BREVO_SENDER_EMAIL or 'unset'))"

echo "Starting Gunicorn..."
exec gunicorn core.wsgi:application \
  --bind 0.0.0.0:${DEFAULT_APP_PORT:-${PORT:-3000}} \
  --workers ${GUNICORN_WORKERS:-2} \
  --timeout ${GUNICORN_TIMEOUT:-300} \
  --log-level ${GUNICORN_LOG_LEVEL:-info} \
  --access-logfile - \
  --error-logfile -
