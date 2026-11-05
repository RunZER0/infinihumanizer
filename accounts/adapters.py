from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from platformhub.views import is_admin_user


class CustomAccountAdapter(DefaultAccountAdapter):
    """Use django-allauth's verification flow with role-aware redirection."""

    def get_login_redirect_url(self, request):
        if request.user.is_authenticated and is_admin_user(request.user):
            return reverse("platformhub:operations_desk")
        return reverse("platformhub:workspace")

    def post_login(self, request, user, **kwargs):
        if is_admin_user(user):
            kwargs["redirect_url"] = reverse("platformhub:operations_desk")
        return super().post_login(request, user, **kwargs)
