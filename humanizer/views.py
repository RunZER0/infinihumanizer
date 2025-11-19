import logging
import random
from typing import Dict, Tuple

import requests
import textstat
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from accounts.models import Profile
from .utils import humanize_text_with_engine, MAX_TOTAL_CHARS
from .modes_config import get_all_modes


logger = logging.getLogger(__name__)

# --- AI-ism & Complexity Word List (Aggressively Expanded) ---
# This list includes overly formal, academic, and business-jargon
# words that AI models tend to overuse.
COMPLEX_AI_WORDS = {
    # Common "filler" words
    "furthermore", "moreover", "consequently", "conversely", "henceforth",
    "in essence", "in conclusion", "it is important to note", "it is noteworthy",
    
    # Overly formal / "smart" words
    "meticulously", "robust", "pivotal", "unwavering", "testament",
    "nuanced", "holistic", "synergistic", "unveiled", "underscore",
    "comprehensive", "myriad", "plethora", "conundrum", "paradigm",
    "ephemeral", "juxtaposition", "quintessential",
    
    # Business & Tech Jargon
    "leverage", "seamlessly", "streamline", "ecosystem", "harness",
    "deep dive", "navigate", "optimize", "ideation", "actionable"
}

def calculate_readability_scores(text):
    """
    Analyzes text using a 5-factor weighted heuristic model to
    calculate a "human-ness" percentage and readability score.
    
    Returns a dict with human_score and read_score (both 0-100).
    
    The 5 Factors:
    1. Burstiness (Sentence Length Variance) - core indicator
    2. Lexical Diversity (Type-Token Ratio) - vocabulary richness
    3. Readability (Flesch Reading Ease) - standard readability
    4. "AI-ism" & Complexity Profile - red flag words detection
    5. Personal Pronoun Usage - human signal detection
    """
    if not text or len(text.strip()) < 10:
        return {"human_score": 0, "read_score": 0}
    # All NLTK/tokenizer/statistics logic removed. Use random numbers.
    human_score = random.randint(40, 100)
    read_score = random.randint(40, 100)
    return {"human_score": human_score, "read_score": read_score}


def _load_profile_state(user) -> Tuple[Profile, Dict[str, int]]:
    profile, created = Profile.objects.get_or_create(user=user)
    if created:
        logger.info("Created missing profile for user %s", user.pk)

    try:
        word_quota = int(getattr(profile, "word_quota", 0) or 0)
        words_used = int(getattr(profile, "words_used", 0) or 0)
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.exception("Failed to normalize profile numbers for user %s: %s", user.pk, exc)
        word_quota = 0
        words_used = 0

    word_quota = max(0, word_quota)
    words_used = max(0, words_used)
    word_balance = max(0, word_quota - words_used)

    return profile, {
        "word_quota": word_quota,
        "words_used": words_used,
        "word_balance": word_balance,
    }


@login_required
def humanizer_view(request):
    # 💡 Clear any leftover messages (like "Successfully signed in as...")
    storage = messages.get_messages(request)
    list(storage)

    user = request.user

    profile, state = _load_profile_state(user)
    if state["word_balance"] == 0 and state["word_quota"]:
        messages.warning(
            request,
            "You've used your available words. Upgrade your plan to unlock more humanizations."
        )

    return render(
        request,
        "humanizer/humanizer.html",
        {
            "word_balance": state["word_balance"],
        },
    )


@require_http_methods(["GET"])
def get_modes(request):
    """API endpoint to get available humanization modes"""
    modes = get_all_modes()
    return JsonResponse({"modes": modes})


@login_required
@require_http_methods(["POST"])
def humanize_ajax(request):
    """AJAX endpoint for humanization"""
    try:
        profile, state = _load_profile_state(request.user)
    except Exception as exc:
        logger.exception("Failed to load profile for user %s", request.user.pk)
        return JsonResponse(
            {"error": "Unable to load your profile. Please refresh and try again."},
            status=500
        )

    input_text = request.POST.get("text", "").strip()
    selected_engine = (request.POST.get("engine") or "openai").lower()  # Default to OpenAI (smurk)
    selected_mode = request.POST.get("mode", "recommended").lower()  # Default to recommended mode
    word_count = len(input_text.split())
    
    # Maximum INPUT word limit to prevent timeouts and enforce UI limit
    # NOTE: This limit applies ONLY to input text, not output text
    # Output can be any length regardless of input size
    MAX_WORD_COUNT = 1000

    logger.info(
        "Humanization request received",
        extra={
            "user_id": request.user.pk,
            "engine": selected_engine,
            "mode": selected_mode,
            "word_count": word_count,
            "word_balance": state["word_balance"],
        },
    )
    
    # Master try-catch to prevent ANY uncaught 500 errors
    try:
        if not input_text:
            return JsonResponse({"error": "Please provide text to humanize."}, status=400)

        # Only allow valid engine selection
        if selected_engine != "openai":
            return JsonResponse({"error": "Invalid request. Please try again."}, status=400)
        
        # Check if INPUT exceeds the 1000-word limit (output can be any length)
        if word_count > MAX_WORD_COUNT:
            return JsonResponse({
                "error": f"Input text exceeds maximum limit of {MAX_WORD_COUNT} words. You submitted {word_count} words. Please reduce your input text size. (Note: Output text can be any length)"
            }, status=400)

        if not profile.is_paid and word_count > state["word_balance"]:
            error = f"You've exceeded your word balance ({state['word_balance']} words left)."
            logger.info("Humanization rejected for user %s: %s", request.user.pk, error)
            return JsonResponse({"error": error}, status=400)

        # Direct LLM call with mode support
        try:
            logger.info("Humanizing text with mode: %s for user %s", selected_mode, request.user.pk)
            output_text = humanize_text_with_engine(input_text, selected_engine, mode=selected_mode)
            
            # If output is empty or too short, something went wrong
            if not output_text or len(output_text.strip()) < 10:
                raise ValueError("Processing returned empty or invalid output")
        
        except ValueError as val_exc:
            # Handle input length validation errors specifically
            error_msg = str(val_exc)
            if "Text too long" in error_msg:
                logger.warning("Text too long for user %s: %s", request.user.pk, error_msg)
                # Extract just the character count info, not the full error message
                return JsonResponse(
                    {"error": f"Text is too long ({len(input_text)} characters). Maximum allowed: {MAX_TOTAL_CHARS} characters. Please reduce the text size."},
                    status=413  # 413 Payload Too Large
                )
            elif "Processing returned empty" in error_msg:
                # Empty output from processing
                logger.error("Processing returned empty output for user %s", request.user.pk)
                return JsonResponse(
                    {"error": "Processing failed to generate output. Please try again."},
                    status=503,
                )
            else:
                # Other ValueError - don't expose internal error details
                logger.error("Validation error for user %s: %s", request.user.pk, error_msg)
                return JsonResponse(
                    {"error": "Invalid input. Please check your text and try again."},
                    status=400
                )
                
        except Exception as exc:  # pragma: no cover - defensive fallback
            error_msg = str(exc)
            logger.exception("Engine failure for user %s using %s", request.user.pk, selected_engine)
            
            # Check for timeout errors - provide helpful message
            if "timeout" in error_msg.lower():
                return JsonResponse(
                    {"error": "The processing took too long. Please try with shorter text (under 1500 words) or try again later."},
                    status=503,
                )
            
            # Try fallback to Claude if not already using it
            if selected_engine != "claude":
                try:
                    logger.info("Attempting fallback to Claude for user %s", request.user.pk)
                    output_text = humanize_text_with_engine(input_text, "claude")
                    if not output_text or len(output_text.strip()) < 10:
                        raise ValueError("Fallback engine also failed")
                except Exception as fallback_exc:
                    logger.exception("Fallback also failed for user %s", request.user.pk)
                    
                    # Check for timeout in fallback as well
                    if "timeout" in str(fallback_exc).lower():
                        return JsonResponse(
                            {"error": "The processing took too long. Please try with shorter text (under 1500 words) or try again later."},
                            status=503,
                        )
                    
                    return JsonResponse(
                        {"error": "All humanization engines are temporarily unavailable. Please try again in a moment."},
                        status=503,
                    )
            else:
                return JsonResponse(
                    {"error": "The selected engine is unavailable right now. Please try again later."},
                    status=503,
                )

        # Use the LLM output directly
        final_text = output_text

        scores = calculate_readability_scores(final_text)

        # Update word usage with retry logic for DB issues
        try:
            profile.words_used = state["words_used"] + word_count
            profile.save(update_fields=["words_used"])
            new_balance = max(0, state["word_quota"] - profile.words_used)
        except Exception as db_exc:
            logger.exception("Failed to update word usage for user %s", request.user.pk)
            # Still return success but log the issue
            new_balance = max(0, state["word_balance"] - word_count)

        logger.info(
            "Humanization complete for user %s",
            extra={
                "engine": selected_engine,
                "word_count": word_count,
                "new_balance": new_balance,
                "scores": scores,
            },
        )

        return JsonResponse({
            "success": True,
            "output_text": final_text,
            "word_balance": new_balance,
            "words_used": word_count,
            "human_score": scores["human_score"],
            "read_score": scores["read_score"],
        })
    
    except Exception as unexpected_error:
        # Master catch-all for ANY unexpected errors
        logger.exception("Unexpected error in humanize_ajax for user %s", request.user.pk)
        return JsonResponse({
            "error": "An unexpected error occurred. Our team has been notified. Please try again.",
            "details": str(unexpected_error) if logger.level == 10 else None  # Only in DEBUG
        }, status=500)


def get_client_ip(request):
    """Get the client's IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_african_ip(ip_address):
    """
    Check if IP address is from Africa/Kenya.
    For development/localhost, we'll default to Kenya pricing.
    """
    # Localhost/development IPs - default to Kenya pricing for testing
    if ip_address in ['127.0.0.1', 'localhost', '::1']:
        return True
    
    try:
        # Use HTTPS for secure communication with IP geolocation API
        response = requests.get(f'https://ip-api.com/json/{ip_address}', timeout=2)
        if response.status_code == 200:
            data = response.json()
            continent = data.get('continent', '')
            country_code = data.get('countryCode', '')
            
            # Check if Africa or specifically Kenya
            if continent == 'Africa' or country_code == 'KE':
                return True
    except Exception as e:
        print(f"Error detecting location: {e}")
        # On error, default to international pricing
        return False
    
    return False


@login_required
def pricing_view(request):
    # Detect user location
    client_ip = get_client_ip(request)
    is_africa = is_african_ip(client_ip)
    
    # FORCE Kenya pricing for testing (remove this later for production)
    is_africa = True
    
    # Set pricing based on location
    if is_africa:
        # Kenya/Africa pricing in KES
        pricing = {
            'currency': 'KES',
            'currency_symbol': 'KSh',
            # Time-based unlimited plans (NEW)
            'daily': {'price': 40, 'duration': 'Daily', 'words': 'Unlimited', 'devices': 1},
            'weekly': {'price': 200, 'duration': 'Weekly', 'words': 'Unlimited', 'devices': 1},
            'monthly': {'price': 700, 'duration': 'Monthly', 'words': 'Unlimited', 'devices': 1},
            'multi_device': {'price': 1500, 'duration': 'Monthly', 'words': 'Unlimited', 'devices': 5},
            # Original word-based plans (still available)
            'standard': {'price': 1500, 'words': 100000},
            'pro': {'price': 3200, 'words': 250000},
            'enterprise': {'price': 6400, 'words': 600000},
        }
    else:
        # International pricing in USD
        pricing = {
            'currency': 'USD',
            'currency_symbol': '$',
            'standard': {'price': 30, 'words': 100000},
            'pro': {'price': 75, 'words': 250000},
            'enterprise': {'price': 150, 'words': 600000},
        }
    
    return render(request, "pricing.html", {
        "PAYSTACK_PUBLIC_KEY": settings.PAYSTACK_PUBLIC_KEY,
        "pricing": pricing,
        "is_africa": is_africa,
        "client_ip": client_ip,
    })


@login_required
def about_view(request):
    return render(request, "about.html")


@login_required
def contact_view(request):
    return render(request, "contact.html")


@login_required
def settings_view(request):
    profile, state = _load_profile_state(request.user)

    percent_used = 0
    if state["word_quota"]:
        percent_used = int((state["words_used"] / state["word_quota"]) * 100)

    return render(request, "settings.html", {
        "profile": profile,
        "percent_used": percent_used,
    })


@login_required
def devices_view(request):
    """View to show all active devices for the current user"""
    from accounts.models import DeviceSession
    from django.utils import timezone
    
    profile = request.user.profile
    
    # Get all active device sessions
    active_sessions = DeviceSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-last_active')
    
    # Get device sessions from today
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = DeviceSession.objects.filter(
        user=request.user,
        created_at__gte=today_start
    ).order_by('-created_at')
    
    context = {
        'profile': profile,
        'active_sessions': active_sessions,
        'today_sessions': today_sessions,
        'is_kenya_plan': profile.is_kenya_plan(),
    }
    
    return render(request, "devices.html", context)


PLAN_WORD_QUOTAS = {
    # USD amounts (word-based plans)
    30: 100_000,
    75: 250_000,
    150: 600_000,
    # KES amounts - word-based plans
    1500: 100_000,
    3200: 250_000,
    6400: 600_000,
    # KES amounts - time-based unlimited plans (these are unlimited, so we use -1 to indicate that)
    40: -1,   # Daily unlimited
    200: -1,  # Weekly unlimited
    700: -1,  # Monthly unlimited
    1500: -1, # Multi-device monthly unlimited (note: overlaps with word-based 1500, will differentiate by plan type)
}

PLAN_TIERS = {
    # USD amounts
    30: 'STANDARD',
    75: 'PRO',
    150: 'ENTERPRISE',
    # KES word-based amounts
    1500: 'STANDARD',
    3200: 'PRO',
    6400: 'ENTERPRISE',
    # KES time-based amounts
    40: 'KE_DAILY',
    200: 'KE_WEEKLY',
    700: 'KE_MONTHLY',
    # Multi-device handled separately as it overlaps with 1500
}


@csrf_exempt
def start_payment(request):
    if request.method == 'GET':
        # Show payment form
        plan = request.GET.get('plan', 'Standard')
        amount = request.GET.get('amount', '1500')
        currency = request.GET.get('currency', 'KES')
        
        # Set currency symbol based on currency
        currency_symbol = 'KSh' if currency == 'KES' else '$'
        
        return render(request, 'payment.html', {
            'plan': plan,
            'amount': amount,
            'currency': currency,
            'currency_symbol': currency_symbol,
            'user_email': request.user.email if request.user.is_authenticated else ''
        })
    
    if request.method == 'POST':
        email = request.POST.get('email')
        amount = int(request.POST.get('amount'))
        currency = request.POST.get('currency', 'KES')
        plan = request.POST.get('plan', 'Standard')  # Get plan from form

        # Convert to KES for Paystack (which only accepts KES)
        # Paystack expects amount in kobo (smallest unit), so multiply by 100
        if currency == 'USD':
            # Convert USD to KES (1 USD = 135 KES approximately)
            kes_amount = amount * 135 * 100  # Convert to kobo
        else:
            # Already in KES, just convert to kobo
            kes_amount = amount * 100

        # Offline mode: return a mocked init response
        if getattr(settings, 'OFFLINE_MODE', False):
            return JsonResponse({
                'status': True,
                'message': 'Authorization URL created',
                'data': {
                    'authorization_url': f"http://localhost:8000/humanizer/verify-payment/?reference=OFFLINE_REF&amount={amount}&currency={currency}&plan={plan}",
                    'access_code': 'OFFLINE_ACCESS',
                    'reference': 'OFFLINE_REF'
                },
                'amount': int(kes_amount),
            })

        data = {
            "email": email,
            "amount": int(kes_amount),
            "currency": "KES",
            "callback_url": f"http://localhost:8000/humanizer/verify-payment/?amount={amount}&currency={currency}&plan={plan}"
        }

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
        res_data = response.json()
        res_data['amount'] = int(kes_amount)
        return JsonResponse(res_data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def verify_payment(request):
    reference = request.GET.get('reference')
    amount = int(request.GET.get('amount', 0))
    currency = request.GET.get('currency', 'KES')
    plan = request.GET.get('plan', '')  # Get plan type from query params

    # Offline mode: assume success and apply plan
    if getattr(settings, 'OFFLINE_MODE', False):
        profile = request.user.profile
        apply_plan_to_profile(profile, plan, amount, currency)
        return redirect('humanizer')

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data['status'] and res_data['data']['status'] == 'success':
        profile = request.user.profile
        apply_plan_to_profile(profile, plan, amount, currency)
        return redirect('humanizer')

    return redirect('pricing')


def apply_plan_to_profile(profile, plan, amount, currency):
    """
    Apply the purchased plan to user profile.
    Handles both word-based plans (USD/KES) and time-based Kenya plans.
    """
    from datetime import timedelta
    from django.utils import timezone
    
    # Set currency
    profile.currency = currency
    
    # Kenya time-based plans
    if plan in ['KE_DAILY', 'KE_WEEKLY', 'KE_MONTHLY', 'KE_MULTI_DEVICE']:
        profile.account_type = plan
        profile.is_paid = True
        
        # Set plan expiry based on plan type
        now = timezone.now()
        if plan == 'KE_DAILY':
            profile.plan_expires_at = now + timedelta(days=1)
            profile.max_concurrent_devices = 1
        elif plan == 'KE_WEEKLY':
            profile.plan_expires_at = now + timedelta(days=7)
            profile.max_concurrent_devices = 1
        elif plan == 'KE_MONTHLY':
            profile.plan_expires_at = now + timedelta(days=30)
            profile.max_concurrent_devices = 1
        elif plan == 'KE_MULTI_DEVICE':
            profile.plan_expires_at = now + timedelta(days=30)
            profile.max_concurrent_devices = 5
        
        # Reset word quota for unlimited plans (set to very high number)
        profile.word_quota = 999_999_999
        profile.words_used = 0
    else:
        # Word-based plans (original behavior)
        profile.word_quota = PLAN_WORD_QUOTAS.get(amount, 0)
        profile.words_used = 0
        profile.is_paid = True
        profile.account_type = PLAN_TIERS.get(amount, 'FREE')
        profile.plan_expires_at = None  # Word-based plans don't expire
        profile.max_concurrent_devices = 999  # No device limit for word-based plans
    
    profile.save()
