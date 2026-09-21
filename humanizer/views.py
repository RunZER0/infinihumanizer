import hashlib
import logging
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.models import Profile
from .models import AnonymousHumanizerUsage, Humanization
from .service import MAX_INPUT_CHARS, MAX_INPUT_WORDS, rewrite_text

logger = logging.getLogger(__name__)


def _engine_configured():
    backend = getattr(settings, "HUMANIZER_BACKEND", "openrouter").lower()
    if backend == "openrouter":
        return bool(getattr(settings, "OPENROUTER_API_KEY", ""))
    if backend == "openai":
        return bool(getattr(settings, "OPENAI_API_KEY", ""))
    return False


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


def _anonymous_fingerprint(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = forwarded.split(",")[0].strip() if forwarded else ""
    if not ip_address:
        ip_address = request.META.get("REMOTE_ADDR", "")
    user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
    raw = f"{settings.SECRET_KEY}|{ip_address}|{user_agent}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _anonymous_state(request, create=False):
    limit = max(0, int(getattr(settings, "HUMANIZER_ANON_DAILY_WORDS", 300)))
    lookup = {
        "day": timezone.localdate(),
        "fingerprint": _anonymous_fingerprint(request),
    }
    usage = AnonymousHumanizerUsage.objects.filter(**lookup).first()
    if usage is None and create:
        usage, _ = AnonymousHumanizerUsage.objects.get_or_create(**lookup)
    used = max(0, int(usage.words_used or 0)) if usage else 0
    return {
        "limit": limit,
        "used": used,
        "remaining": max(0, limit - used),
        "usage_id": usage.pk if usage else None,
    }


def _reserve_anonymous_words(request, word_count):
    state = _anonymous_state(request, create=True)
    if word_count > state["remaining"]:
        return state, False
    updated = AnonymousHumanizerUsage.objects.filter(
        pk=state["usage_id"],
        words_used__lte=state["limit"] - word_count,
    ).update(words_used=F("words_used") + word_count)
    if not updated:
        return _anonymous_state(request), False
    return _anonymous_state(request), True


def _release_anonymous_words(usage_id, word_count):
    with transaction.atomic():
        usage = AnonymousHumanizerUsage.objects.select_for_update().filter(pk=usage_id).first()
        if usage:
            usage.words_used = max(0, int(usage.words_used or 0) - word_count)
            usage.save(update_fields=["words_used", "updated_at"])


def _auth_urls():
    humanizer_url = reverse("humanizer")
    return {
        "login_url": f'{reverse("account_login")}?next={humanizer_url}',
        "signup_url": f'{reverse("account_signup")}?next={humanizer_url}',
    }


def humanizer_view(request):
    public_base = str(getattr(settings, "PUBLIC_BASE_URL", "") or "").rstrip("/")
    if not settings.DEBUG and request.get_host().lower().startswith("www.") and public_base:
        return redirect(f"{public_base}{request.get_full_path()}")

    storage = messages.get_messages(request)
    list(storage)

    recent = []
    initial_humanization = None
    if request.user.is_authenticated:
        profile, state = _profile_state(request.user)
        if not state["unlimited"] and state["remaining"] == 0:
            messages.warning(request, "Your word balance is empty.")
        balance_label = "Unlimited" if state["unlimited"] else f'{state["remaining"]:,}'
        recent = Humanization.objects.filter(user=request.user)[:8]
        saved_id = request.GET.get("saved", "").strip()
        if saved_id:
            try:
                saved_uuid = uuid.UUID(saved_id)
            except (TypeError, ValueError):
                saved_uuid = None
            if saved_uuid:
                initial_humanization = Humanization.objects.filter(
                    user=request.user,
                    id=saved_uuid,
                ).first()
        anonymous_remaining = None
    else:
        anon = _anonymous_state(request)
        balance_label = f'{anon["remaining"]:,} free today'
        anonymous_remaining = anon["remaining"]

    return render(request, "humanizer/humanizer.html", {
        "balance_label": balance_label,
        "engine_configured": _engine_configured(),
        "max_words": MAX_INPUT_WORDS,
        "max_chars": MAX_INPUT_CHARS,
        "anonymous_daily_limit": int(getattr(settings, "HUMANIZER_ANON_DAILY_WORDS", 300)),
        "anonymous_remaining": anonymous_remaining,
        "recent_humanizations": recent,
        "initial_humanization": initial_humanization,
        **_auth_urls(),
    })


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

    profile = None
    state = None
    anon = None
    anonymous_reserved = False
    if request.user.is_authenticated:
        profile, state = _profile_state(request.user)
        if not state["unlimited"] and word_count > state["remaining"]:
            return JsonResponse({
                "error": f'Your balance has {state["remaining"]:,} words remaining.',
                "quota_reached": state["remaining"] == 0,
            }, status=400)
    else:
        anon, anonymous_reserved = _reserve_anonymous_words(request, word_count)
        if not anonymous_reserved:
            urls = _auth_urls()
            return JsonResponse({
                "error": "Your free daily rewrite limit has been reached. Sign in to rewrite more and save your work.",
                "limit_reached": True,
                "auth_required": True,
                "anonymous_remaining": anon["remaining"],
                **urls,
            }, status=429)

    try:
        output_text, model_used = rewrite_text(input_text, temperature=temperature)
    except ValueError as exc:
        if anonymous_reserved:
            _release_anonymous_words(anon["usage_id"], word_count)
        return JsonResponse({"error": str(exc)}, status=400)
    except RuntimeError as exc:
        if anonymous_reserved:
            _release_anonymous_words(anon["usage_id"], word_count)
        logger.warning("Humanizer configuration/request error: %s", exc)
        return JsonResponse({"error": str(exc)}, status=503)
    except Exception:
        if anonymous_reserved:
            _release_anonymous_words(anon["usage_id"], word_count)
        logger.exception(
            "Humanizer API request failed for %s",
            request.user.pk if request.user.is_authenticated else "anonymous",
        )
        return JsonResponse({"error": "The humanizer could not process this text. Try again in a moment."}, status=503)

    humanization = None
    if request.user.is_authenticated:
        profile.words_used = state["used"] + word_count
        profile.save(update_fields=["words_used"])
        humanization = Humanization.objects.create(
            user=request.user,
            source_text=input_text,
            output_text=output_text,
            variation=temperature,
            model_name=model_used,
            input_words=word_count,
            output_words=len(output_text.split()),
        )
        remaining = None if state["unlimited"] else max(0, state["quota"] - profile.words_used)
        word_balance = "Unlimited" if remaining is None else remaining
        anonymous_remaining = None
    else:
        anon = _anonymous_state(request)
        anonymous_remaining = anon["remaining"]
        word_balance = f"{anonymous_remaining:,} free today"

    return JsonResponse({
        "success": True,
        "output_text": output_text,
        "humanization_id": str(humanization.id) if humanization else "",
        "saved": bool(humanization),
        "words_used": word_count,
        "output_words": len(output_text.split()),
        "word_balance": word_balance,
        "anonymous_remaining": anonymous_remaining,
        "login_prompt": not request.user.is_authenticated,
        **(_auth_urls() if not request.user.is_authenticated else {}),
    })


@login_required
@require_http_methods(["POST"])
def save_humanization(request):
    source_text = request.POST.get("source_text", "").strip()
    output_text = request.POST.get("output_text", "").strip()
    humanization_id = request.POST.get("humanization_id", "").strip()

    if not output_text:
        return JsonResponse({"error": "There is no rewritten text to save."}, status=400)
    if len(source_text) > MAX_INPUT_CHARS or len(output_text) > MAX_INPUT_CHARS * 2:
        return JsonResponse({"error": "This rewrite is too large to save."}, status=413)

    try:
        variation = float(request.POST.get("temperature", 0.65))
    except (TypeError, ValueError):
        variation = 0.65
    variation = max(0.1, min(1.0, variation))

    if humanization_id:
        item = get_object_or_404(Humanization, id=humanization_id, user=request.user)
        item.source_text = source_text or item.source_text
        item.output_text = output_text
        item.variation = variation
        item.output_words = len(output_text.split())
        item.save(update_fields=["source_text", "output_text", "variation", "output_words", "updated_at"])
    else:
        item = Humanization.objects.create(
            user=request.user,
            source_text=source_text,
            output_text=output_text,
            variation=variation,
            input_words=len(source_text.split()),
            output_words=len(output_text.split()),
        )

    return JsonResponse({
        "success": True,
        "humanization_id": str(item.id),
        "saved_at": item.updated_at.isoformat(),
    })
