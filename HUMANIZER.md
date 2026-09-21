# Humanizer

The Humanizer uses a sentence-local OpenRouter runtime. The browser sends source text and a 1-10 rewrite strength. The server segments prose into sentences, protects literals, rewrites independent sentence batches concurrently, validates the returned structure, and restores the original paragraph order.

## Active files

- `humanizer/service.py` - validates the request and invokes the runtime.
- `humanizer/sentence_runtime.py` - segmentation, protected literals, few-shot prompting, concurrent OpenRouter calls, retry/rate-limit handling, validation and reassembly.
- `humanizer/views.py` - account/anonymous quotas and the POST endpoint.
- `humanizer/templates/humanizer/humanizer.html` - the writing interface.
- `humanizer/tests.py` - endpoint and runtime tests.

## Runtime

Default model:

```
mistralai/ministral-3b-2512
```

The model sees independent sentence items rather than the whole document. Batches run concurrently and are reassembled in source order. Quotations, citation-like parentheticals, numeric citations, URLs, DOIs and numbers are replaced with protected tokens before inference and restored afterward.

Rewrite strength is separate from model sampling temperature:

- 1-3: close
- 4-6: balanced
- 7-10: maximum
- default: 8

Few-shot examples differ by profile. Higher strength requests structural reconstruction while the internal sampling temperature remains bounded.

## Configuration

Required:

- `OPENROUTER_API_KEY`

Defaults:

- `HUMANIZER_BACKEND=openrouter`
- `HUMANIZER_MODEL_ID=mistralai/ministral-3b-2512`
- `HUMANIZER_SENTENCE_BATCH_SIZE=8`
- `HUMANIZER_MAX_CONCURRENCY=6`
- `HUMANIZER_REQUEST_TIMEOUT=30`
- `HUMANIZER_MAX_RETRIES=2`
- `HUMANIZER_PROVIDER_SORT=throughput`
- `HUMANIZER_DEFAULT_STRENGTH=8`

`HUMANIZER_FALLBACK_MODELS` can contain comma-separated model fallbacks. Provider fallback remains enabled independently so OpenRouter can route around a failing or rate-limited endpoint.

## Reliability

A 429 applies a shared cooldown to the current document runtime and honors `Retry-After` when present. Retries happen per sentence batch. Invalid structured output receives one repair pass. The runtime never logs source or rewritten text.

## Limits

- 3,000 input words
- 18,000 input characters
