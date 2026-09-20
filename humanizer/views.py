import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from accounts.models import Profile
from .service import MAX_INPUT_CHARS, MAX_INPUT_WORDS, rewrite_text

logger = logging.getLogger(__name__)


def _profile_state(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    quota = max(0, int(profile.word_quota or 0))
    used = max(0, int(profile.words_used or 0))
    unlimited = bool(profile.is_kenya_plan() and profile.has_quota(1))
    remaining = None if unlimited else max(0, quota - used)
    return profile, {
        "quota": quota,
        "used": used,
        "remaining": remaining,
        "unlimited": unlimited,
    }


@login_required
def humanizer_view(request):
    storage = messages.get_messages(request)
    list(storage)

    profile, state = _profile_state(request.user)
    if not state["unlimited"] and state["remaining"] == 0:
        messages.warning(request, "Your word balance is empty.")

    return render(request, "humanizer/humanizer.html", {
        "balance_label": "Unlimited" if state["unlimited"] else f'{state["remaining"]:,}',
        "engine_configured": bool(getattr(settings, "OPENAI_API_KEY", "")),
        "max_words": MAX_INPUT_WORDS,
        "max_chars": MAX_INPUT_CHARS,
    })


@login_required
@require_http_methods(["POST"])
def humanize_ajax(request):
    input_text = request.POST.get("text", "").strip()
    word_count = len(input_text.split())

    try:
        temperature = float(request.POST.get("temperature", 0.65))
    except (TypeError, ValueError):
        temperature = 0.65
    temperature = max(0.1, min(1.0, temperature))

    if not input_text:
        return JsonResponse({"error": "Add text to rewrite."}, status=400)
    if len(input_text) > MAX_INPUT_CHARS:
        return JsonResponse({"error": f"Text exceeds the {MAX_INPUT_CHARS:,}-character limit."}, status=413)
    if word_count > MAX_INPUT_WORDS:
        return JsonResponse({"error": f"Text exceeds the {MAX_INPUT_WORDS:,}-word limit."}, status=413)

    profile, state = _profile_state(request.user)
    if not state["unlimited"] and word_count > state["remaining"]:
        return JsonResponse({
            "error": f'Your balance has {state["remaining"]:,} words remaining.'
        }, status=400)

    try:
        output_text = rewrite_text(input_text, temperature=temperature)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except Exception:
        logger.exception("Humanizer API request failed for user %s", request.user.pk)
        return JsonResponse({"error": "The humanizer could not process this text. Try again in a moment."}, status=503)

    profile.words_used = state["used"] + word_count
    profile.save(update_fields=["words_used"])

    remaining = None if state["unlimited"] else max(0, state["quota"] - profile.words_used)
    return JsonResponse({
        "success": True,
        "output_text": output_text,
        "words_used": word_count,
        "output_words": len(output_text.split()),
        "word_balance": "Unlimited" if remaining is None else remaining,
    })
