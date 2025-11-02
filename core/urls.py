from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import VerifiedEmailLoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Accounts app URLs FIRST (includes custom login)
    path('accounts/', include('accounts.urls')),

    # ✅ Allauth URLs (but our custom login overrides it)
    path('accounts/', include('allauth.urls')),

    # ✅ Humanizer app
    path('humanizer/', include('humanizer.urls')),

    # ✅ Root redirect
    path('', lambda request: redirect('humanizer')),
]

# ✅ Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
