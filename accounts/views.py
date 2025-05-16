

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("humanizer")  # 🔁 updated
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
        input_text = request.POST.get("text", "")
        word_count = len(input_text.split())
        word_balance = 10000 - word_count
        output_text = input_text  # (placeholder for your AI logic)

    context = {
        "input_text": input_text,
        "output_text": output_text,
        "word_count": word_count,
        "word_balance": word_balance,
    }

    return render(request, "humanizer.html", context)