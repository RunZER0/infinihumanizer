from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages

from .forms import SignUpForm

from allauth.account.views import LoginView
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.urls import reverse


class VerifiedEmailLoginView(LoginView):
    def form_valid(self, form):
        user = form.user_cache
        verified = EmailAddress.objects.filter(user=user, verified=True).exists()

        # ✅ Debug output to confirm this custom view is active
        print("✅ USING CUSTOM VerifiedEmailLoginView")

        if not verified:
            self.request.session['resend_email'] = user.email
            messages.error(
                self.request,
                "⚠️ Your email is not verified. Please check your inbox or resend the link."
            )

            # ✅ Render the login form again with session available immediately
            context = self.get_context_data(form=form)
            return render(self.request, self.template_name, context)

        return super().form_valid(form)


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


def resend_verification(request):
    """
    View to resend the verification email if the user logs in but is not verified.
    Triggered only when 'resend_email' is set in session by VerifiedEmailLoginView.
    """
    email = request.session.get('resend_email')
    if email:
        email_address = EmailAddress.objects.filter(email=email).first()
        if email_address and not email_address.verified:
            send_email_confirmation(request, email_address.user, email=email)
            messages.success(request, "✅ A new verification email has been sent.")
        else:
            messages.warning(request, "⚠️ This email is already verified or doesn't exist.")
        request.session.pop('resend_email', None)  # Clean up
    else:
        messages.error(request, "❌ Could not resend verification email — no email in session.")
    return redirect(reverse('account_login'))
