# Humanizer

The Humanizer is a small Django surface around one API-backed rewriting service.

## Active files

- `humanizer/service.py` — validates input and calls the configured OpenAI model.
- `humanizer/views.py` — serves the page, enforces account word balance, and exposes the POST endpoint.
- `humanizer/urls.py` — `/humanizer/` and `/humanizer/humanize/`.
- `humanizer/templates/humanizer/humanizer.html` — the writing interface.
- `humanizer/tests.py` — page, API, and quota tests.

## Configuration

Required:

- `OPENAI_API_KEY`

Optional:

- `HUMANIZER_MODEL_ID` — overrides the default fine-tuned model ID.

The browser does not choose an engine or model. It submits text and a bounded variation value. The server owns the model selection and prompt.

## Limits

- 3,000 input words
- 18,000 input characters

The rewrite prompt preserves meaning, facts, quotations, citations, names, and technical detail while removing repetitive or formulaic writing patterns.
