from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import VerifiedEmailLoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Custom login view
    path('accounts/login/', VerifiedEmailLoginView.as_view(), name='account_login'),

    # ✅ Accounts app URLs (signup, resend_verification, etc.)
    path('accounts/', include('accounts.urls')),

    # ✅ Allauth and Auth URLs
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # ✅ Add this line

    # ✅ Humanizer app
    path('humanizer/', include('humanizer.urls')),

    # ✅ Root redirect
    path('', lambda request: redirect('humanizer')),
]

# ✅ Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
