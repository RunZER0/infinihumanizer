# Local testing

Create a virtual environment, install the current dependencies and provide the environment variables needed for the feature you are testing.

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

For the Humanizer, set `OPENAI_API_KEY`. `HUMANIZER_MODEL_ID` is optional.

The Humanizer does not have an offline rewriting engine. Tests mock the API boundary instead:

```bash
python manage.py test humanizer
```

For platform tests:

```bash
python manage.py test platformhub
```

When testing production-like database behaviour locally, set `DATABASE_URL` and keep `OFFLINE_MODE=False`.
