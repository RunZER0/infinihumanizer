from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from accounts.models import Profile
from .utils import humanize_text


@login_required
def humanizer_view(request):
    try:
        user = request.user
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            return HttpResponse("<pre>POST ERROR: Profile does not exist for this user.</pre>", status=500)

        word_balance = profile.word_quota - profile.words_used

        input_text = ""
        output_text = ""
        word_count = 0

        if request.method == "POST":
            input_text = request.POST.get("text", "").strip()
            word_count = len(input_text.split())

            if word_count > word_balance:
                return render(request, "humanizer.html", {
                    "input_text": input_text,
                    "output_text": "",
                    "word_balance": word_balance,
                    "word_count": word_count,
                    "error": f"You've exceeded your word balance ({word_balance} words left).",
                })

            output_text = humanize_text(input_text)
            profile.words_used += word_count
            profile.save()

        return render(request, "humanizer.html", {
            "input_text": input_text,
            "output_text": output_text,
            "word_balance": word_balance,
            "word_count": word_count,
        })

    except Exception as e:
        return HttpResponse(f"<pre>POST ERROR: {e}</pre>", status=500)


@login_required
def pricing_view(request):
    return render(request, "pricing.html")


@login_required
def about_view(request):
    return render(request, "about.html")


@login_required
def contact_view(request):
    return render(request, "contact.html")


@login_required
def settings_view(request):
    profile = request.user.profile
    percent_used = int((profile.words_used / profile.word_quota) * 100) if profile.word_quota else 0

    return render(request, "settings.html", {
        "profile": profile,
        "percent_used": percent_used,
    })
