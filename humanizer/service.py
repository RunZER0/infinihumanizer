"""Sentence-local text rewriting service for InfiniAI."""

from __future__ import annotations

from django.conf import settings

from .sentence_runtime import DEFAULT_MODEL, DEFAULT_STRENGTH, RewriteRuntime, plan_document, reassemble

MAX_INPUT_WORDS = 3000
MAX_INPUT_CHARS = 48000


def rewrite_text(
    text: str,
    strength: int = DEFAULT_STRENGTH,
    temperature: float | None = None,
) -> tuple[str, str]:
    """Rewrite prose sentence by sentence while preserving document structure."""
    text = (text or "").strip()
    if not text:
        raise ValueError("Add text to rewrite.")
    if len(text) > MAX_INPUT_CHARS:
        raise ValueError(f"Text exceeds the {MAX_INPUT_CHARS:,}-character limit.")
    word_count = len(text.split())
    if word_count > MAX_INPUT_WORDS:
        raise ValueError(f"Text exceeds the {MAX_INPUT_WORDS:,}-word limit.")

    if temperature is not None and strength == DEFAULT_STRENGTH:
        try:
            strength = int(round(float(temperature) * 10))
        except (TypeError, ValueError):
            strength = DEFAULT_STRENGTH
    strength = max(1, min(10, int(strength)))

    plans, paragraph_separators, tasks = plan_document(text)
    if not tasks:
        model = getattr(settings, "HUMANIZER_MODEL_ID", DEFAULT_MODEL) or DEFAULT_MODEL
        return text, str(model)

    runtime = RewriteRuntime(strength)
    try:
        rewritten, model_used = runtime.run(tasks)
    finally:
        runtime.close()

    output = reassemble(plans, paragraph_separators, rewritten)
    if not output:
        raise RuntimeError("The humanizer returned an empty response.")
    return output, model_used
