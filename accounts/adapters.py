from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """Use django-allauth's verification flow with the configured Django email backend."""

    pass
