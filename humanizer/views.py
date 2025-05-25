from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from allauth.account.models import EmailAddress
from django.contrib import messages

from accounts.models import Profile
from .utils import humanize_text
import requests

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

    if request.method == "POST":
        input_text = request.POST.get("text", "").strip()
        word_count = len(input_text.split())

        if word_count > word_balance:
            error = f"You've exceeded your word balance ({word_balance} words left)."
        else:
            output_text = humanize_text(input_text)
            profile.words_used += word_count
            profile.save()

    return render(request, "humanizer.html", {
        "input_text": input_text,
        "output_text": output_text,
        "word_count": word_count,
        "word_balance": word_balance,
        "error": error,
    })


@login_required
def pricing_view(request):
    return render(request, "pricing.html", {
        "PAYSTACK_PUBLIC_KEY": settings.PAYSTACK_PUBLIC_KEY
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
    if request.method == 'POST':
        email = request.POST.get('email')
        usd_amount = int(request.POST.get('amount'))
        currency = request.POST.get('currency', 'USD')

        kes_amount = usd_amount * 135 * 100

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
