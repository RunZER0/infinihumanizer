from django.urls import include, path

from .admin import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("humanizer/", include("humanizer.urls")),
    path("", include("platformhub.urls")),
]
