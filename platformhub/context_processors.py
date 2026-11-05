from .views import is_admin_user


def admin_context(request):
    """Expose is_admin flag to all templates for role-aware UI navigation."""
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        return {"is_admin": is_admin_user(user)}
    return {"is_admin": False}
