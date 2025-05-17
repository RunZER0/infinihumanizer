from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import SignUpForm


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("humanizer")  # Redirect to the humanizer view
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def humanizer_view(request):
    input_text = ''
    output_text = ''
    word_count = 0
    word_balance = 10000

    if request.method == "POST":
        try:
            input_text = request.POST.get("text", "")
            word_count = len(input_text.split())
            word_balance = 10000 - word_count
            output_text = input_text  # Replace with your AI logic if needed
        except Exception as e:
            return HttpResponse(f"<pre>POST ERROR: {e}</pre>", status=500)

    context = {
        "input_text": input_text,
        "output_text": output_text,
        "word_count": word_count,
        "word_balance": word_balance,
    }

    return render(request, "humanizer/humanizer.html", context)
