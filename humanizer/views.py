from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from allauth.account.models import EmailAddress
from django.contrib import messages

from accounts.models import Profile
from .utils import humanize_text, humanize_text_with_engine
from .preprocessing import TextPreprocessor
from .validation import HumanizationValidator
import requests
import textstat
import geoip2.database
import os
import nltk
import statistics

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
    
    # --- Base Score & Feedback Log ---
    # We start with a base score and add/subtract based on heuristics.
    human_score = 75.0  # Start from a 'neutral-good' baseline
    
    # --- Tokenization ---
    try:
        sentences = nltk.sent_tokenize(text)
        words = nltk.word_tokenize(text.lower())
    except Exception as e:
        print(f"NLTK tokenization failed: {e}. Falling back to simple tokenization.")
        # Fallback to simple tokenization
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        words = text.lower().split()
    
    if len(sentences) < 3 or len(words) < 30:
        # Text too short for meaningful analysis
        flesch_score = textstat.flesch_reading_ease(text)
        read_score = max(0, min(100, flesch_score))
        return {"human_score": 50, "read_score": int(read_score)}
    
    # --- Factor 1: Burstiness (Sentence Length Std. Dev.) ---
    # High variance = human-like. Low variance = AI-like.
    # Weight: Strong (up to +/- 30 points)
    try:
        sentence_word_lengths = [len(nltk.word_tokenize(s)) for s in sentences]
        sent_len_stdev = statistics.stdev(sentence_word_lengths)
    except Exception:
        # Fallback calculation
        sentence_word_lengths = [len(s.split()) for s in sentences]
        sent_len_stdev = statistics.stdev(sentence_word_lengths) if len(sentence_word_lengths) > 1 else 0
    
    if sent_len_stdev < 7:
        human_score -= 30
    elif sent_len_stdev < 10:
        human_score -= 10
    elif sent_len_stdev > 14:
        human_score += 15
    
    # --- Factor 2: Lexical Diversity (Type-Token Ratio - TTR) ---
    # TTR = unique words / total words.
    # Weight: Medium (up to -20 points)
    ttr = len(set(words)) / len(words) if len(words) > 0 else 0
    
    if ttr < 0.35:
        human_score -= 15
    elif ttr > 0.6:
        human_score -= 20
    else:
        human_score += 5
    
    # --- Factor 3: Readability (Flesch Reading Ease) ---
    # 0-30 = Very Difficult (Academic). 60-70 = Plain English. 90-100 = Very Easy.
    # Weight: Medium (up to -25 points)
    flesch_score = textstat.flesch_reading_ease(text)
    
    if flesch_score < 30:
        human_score -= 25
    elif flesch_score > 85:
        human_score -= 10
    
    # --- Factor 4: "AI-ism" & Complexity Profile ---
    # Penalize for each "AI-ism" found.
    # Weight: Very Strong (uncapped penalty)
    ai_word_count = 0
    text_lower = text.lower()
    
    for word in COMPLEX_AI_WORDS:
        if word in text_lower:
            ai_word_count += text_lower.count(word)
    
    # Aggressive penalty: 5 points per word
    ai_penalty = ai_word_count * 5
    human_score -= ai_penalty
    
    # --- Factor 5: Personal Pronoun Usage ---
    # A small amount is a strong human signal.
    # Weight: Strong Bonus / Medium Penalty
    first_person_count = words.count('i') + words.count('my')
    pronoun_freq = first_person_count / len(words) if len(words) > 0 else 0
    
    if 0 < pronoun_freq < 0.03:  # 0% - 3%
        human_score += 25
    elif pronoun_freq >= 0.03:
        human_score -= 15
    
    # --- Final Score Calculation ---
    final_human_score = max(0, min(100, human_score))
    read_score = max(0, min(100, flesch_score))
    
    return {
        "human_score": int(final_human_score),
        "read_score": int(read_score)
    }


@login_required
def humanizer_view(request):
    # 💡 Clear any leftover messages (like "Successfully signed in as...")
    storage = messages.get_messages(request)
    list(storage)

    input_text = ""
    output_text = ""
    word_count = 0
    error = ""
    word_balance = None

    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return HttpResponse("<pre>Profile does not exist for this user.</pre>", status=500)

    word_balance = profile.word_quota - profile.words_used

    # Just render the page for GET requests
    return render(request, "humanizer/humanizer.html", {
        "word_balance": word_balance,
    })


@login_required
@require_http_methods(["POST"])
def humanize_ajax(request):
    """AJAX endpoint for humanization with preprocessing and validation"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return JsonResponse({"error": "Profile does not exist"}, status=500)

    word_balance = profile.word_quota - profile.words_used
    
    input_text = request.POST.get("text", "").strip()
    selected_engine = (request.POST.get("engine") or "claude").lower()  # Default to Claude (OXO)
    word_count = len(input_text.split())
    
    print(f"\n{'='*60}")
    print(f"🚀 AJAX HUMANIZATION REQUEST")
    print(f"   Engine: {selected_engine}")
    print(f"   Word count: {word_count}")
    print(f"   Word balance: {word_balance}")
    print(f"{'='*60}")

    if word_count > word_balance:
        error = f"You've exceeded your word balance ({word_balance} words left)."
        print(f"❌ Word limit exceeded!")
        return JsonResponse({"error": error}, status=400)
    
    # Valid engines: DeepSeek (Loly), Claude (OXO), OpenAI (Smurk)
    if selected_engine not in ("deepseek", "claude", "openai"):
        return JsonResponse({"error": "Invalid engine selection"}, status=400)
    
    try:
        # =============================================================================
        # 3-STAGE PIPELINE - ALWAYS ACTIVE, CANNOT BE BYPASSED
        # =============================================================================
        
        # STAGE 1: PREPROCESSING - Analyze text before humanization (MANDATORY)
        print(f"🔍 Stage 1: PREPROCESSING & ANALYSIS (MANDATORY)...")
        preprocessor = TextPreprocessor()
        analysis = preprocessor.preprocess_text(input_text)
        
        print(f"   ✅ Analysis complete:")
        print(f"      - AI patterns detected: {len(analysis['ai_patterns'])} categories")
        print(f"      - Elements to preserve: {sum(len(v) for v in analysis['preservation_map'].values())}")
        print(f"      - Safe variation zones: {len(analysis['safe_variation_zones'])}")
        
        # STAGE 2: HUMANIZATION - Process with selected engine (MANDATORY)
        print(f"⏳ Stage 2: HUMANIZATION with {selected_engine.upper()} (MANDATORY)...")
        output_text = humanize_text_with_engine(input_text, selected_engine)
        print(f"   ✅ Humanization complete! Output length: {len(output_text)} chars")
        
        # STAGE 3: VALIDATION - Quality control and fixing (MANDATORY)
        print(f"🔬 Stage 3: QUALITY VALIDATION & AUTO-FIX (MANDATORY)...")
        validator = HumanizationValidator()
        validation_report = validator.validate_humanization(
            original=input_text,
            humanized=output_text,
            preservation_map=analysis['preservation_map']
        )
        
        print(f"   ✅ Validation complete:")
        print(f"      - Overall score: {validation_report['overall_score']}/100")
        print(f"      - Passed: {validation_report['passed_validation']}")
        print(f"      - Issues detected: {len(validation_report['detected_issues'])}")
        print(f"      - AI Detection Risk: {validation_report['risk_assessment']['risk_level']}")
        
        # Use the validated/fixed text (ALWAYS VALIDATED)
        final_text = validation_report['final_text']
        
        # =============================================================================
        # END OF 3-STAGE PIPELINE
        # =============================================================================
        
        # Calculate readability scores for the output
        scores = calculate_readability_scores(final_text)
        print(f"📊 Final Scores - Human: {scores['human_score']}%, Read: {scores['read_score']}%")
        
        # Update word usage
        profile.words_used += word_count
        profile.save()
        
        new_balance = profile.word_quota - profile.words_used
        
        print(f"✅ HUMANIZATION COMPLETE - ALL 3 STAGES EXECUTED")
        print(f"{'='*60}\n")
        
        return JsonResponse({
            "success": True,
            "output_text": final_text,
            "word_balance": new_balance,
            "words_used": word_count,
            "human_score": scores["human_score"],
            "read_score": scores["read_score"],
            "validation": {
                "score": validation_report['overall_score'],
                "passed": validation_report['passed_validation'],
                "risk_level": validation_report['risk_assessment']['risk_level'],
                "issues_count": len(validation_report['detected_issues'])
            }
        })
        
    except Exception as e:
        error = f"Humanization error: {str(e)}"
        print(f"❌ ERROR in humanize_ajax: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": error}, status=500)


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
        # You would use a GeoIP database here in production
        # For now, using a simple IP geolocation API
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=2)
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
    
    # Set pricing based on location
    if is_africa:
        # Kenya/Africa pricing in KES
        pricing = {
            'currency': 'KES',
            'currency_symbol': 'KSh',
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
    try:
        profile = request.user.profile
        percent_used = int((profile.words_used / profile.word_quota) * 100) if profile.word_quota else 0

        return render(request, "settings.html", {
            "profile": profile,
            "percent_used": percent_used,
        })

    except Exception as e:
        return HttpResponse(f"<pre>SETTINGS VIEW ERROR:\n{e}</pre>", status=500)


PLAN_WORD_QUOTAS = {
    30: 100_000,
    75: 250_000,
    150: 600_000,
}

PLAN_TIERS = {
    30: 'STANDARD',
    75: 'PRO',
    150: 'ENTERPRISE'
}


@csrf_exempt
def start_payment(request):
    if request.method == 'GET':
        # Show payment form
        plan = request.GET.get('plan', 'Standard')
        amount = request.GET.get('amount', '1500')
        return render(request, 'payment.html', {
            'plan': plan,
            'amount': amount,
            'user_email': request.user.email if request.user.is_authenticated else ''
        })
    
    if request.method == 'POST':
        email = request.POST.get('email')
        usd_amount = int(request.POST.get('amount'))
        currency = request.POST.get('currency', 'USD')

        kes_amount = usd_amount * 135 * 100

        # Offline mode: return a mocked init response
        if getattr(settings, 'OFFLINE_MODE', False):
            return JsonResponse({
                'status': True,
                'message': 'Authorization URL created',
                'data': {
                    'authorization_url': f"http://localhost:8000/humanizer/verify-payment/?reference=OFFLINE_REF&amount={usd_amount}",
                    'access_code': 'OFFLINE_ACCESS',
                    'reference': 'OFFLINE_REF'
                },
                'amount': int(kes_amount),
            })

        data = {
            "email": email,
            "amount": int(kes_amount),
            "currency": "KES",
            "callback_url": f"http://localhost:8000/humanizer/verify-payment/?amount={usd_amount}"
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

    # Offline mode: assume success and apply plan
    if getattr(settings, 'OFFLINE_MODE', False):
        profile = request.user.profile
        profile.word_quota = PLAN_WORD_QUOTAS.get(amount, 0)
        profile.words_used = 0
        profile.is_paid = True
        profile.account_type = PLAN_TIERS.get(amount, 'FREE')
        profile.save()
        return redirect('humanizer')

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data['status'] and res_data['data']['status'] == 'success':
        profile = request.user.profile
        profile.word_quota = PLAN_WORD_QUOTAS.get(amount, 0)
        profile.words_used = 0
        profile.is_paid = True
        profile.account_type = PLAN_TIERS.get(amount, 'FREE')
        profile.save()
        return redirect('humanizer')

    return redirect('pricing')
