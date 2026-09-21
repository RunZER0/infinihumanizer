# InfiniAI

InfiniAI is a Django platform for language work, research, content review, project delivery and AI systems.

The production service currently runs on Render and uses PostgreSQL through `DATABASE_URL`.

## Main applications

- `platformhub/` — public site, services, project requests, quotes, invoices, assurance work and client workspace.
- `humanizer/` — the text-rewriting tool.
- `accounts/` — authentication and account data.
- `core/` — Django settings and project URLs.

## Humanizer

The Humanizer now has one active processing path:

```
Browser
  -> POST /humanizer/humanize/
  -> humanizer.views.humanize_ajax
  -> humanizer.service.rewrite_text
  -> sentence-local concurrent runtime
  -> OpenRouter
  -> rewritten text
```

There are no browser-selectable engines, legacy chunkers, detector scores or alternate LLM stacks.

See [HUMANIZER.md](HUMANIZER.md) for the current implementation.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

On Windows, activate with:

```powershell
.venv\Scripts\activate
```

## Required environment

```bash
DJANGO_SECRET_KEY=...
DATABASE_URL=...
OPENROUTER_API_KEY=...
HUMANIZER_BACKEND=openrouter
HUMANIZER_MODEL_ID=mistralai/ministral-3b-2512
```

Common production settings:

```bash
DEBUG=False
OFFLINE_MODE=False
PAYSTACK_PUBLIC_KEY=...
PAYSTACK_SECRET_KEY=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

Humanizer runtime tuning is optional. Defaults are documented in `HUMANIZER.md`.

## Tests

```bash
python manage.py test humanizer platformhub
```

## Deployment

Render installs `requirements.txt`, runs `collectstatic`, then starts the service with `start.sh`. Database migrations run at startup.

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for the current production notes.
