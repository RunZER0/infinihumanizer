# Render deployment

Production runs as the Render web service `infiniai`.

## Build

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
```

## Start

`start.sh` runs database migrations and starts Gunicorn.

## Required environment

- `DJANGO_SECRET_KEY`
- `DATABASE_URL`
- `OPENAI_API_KEY`
- `DEBUG=False`
- `OFFLINE_MODE=False`

Add payment and email credentials when those features are enabled:

- `PAYSTACK_PUBLIC_KEY`
- `PAYSTACK_SECRET_KEY`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

The Humanizer can optionally use `HUMANIZER_MODEL_ID` to override its default fine-tuned model.

## Verification after deployment

Check:

- `/`
- `/about/`
- `/humanizer/` while signed in
- `/health/`

Render logs should show migrations completing before Gunicorn starts.
