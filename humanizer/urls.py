from django.urls import path
from .views import (
    humanizer_view,
    pricing_view,
    about_view,
    contact_view,
    settings_view,  # ✅ add this
)

urlpatterns = [
    path('', humanizer_view, name='humanizer'),
    path('pricing/', pricing_view, name='pricing'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('settings/', settings_view, name='settings'),
]
