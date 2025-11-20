from django.urls import path
from .views import (
    humanizer_view,
    humanize_ajax,
    get_modes,
    get_models,
    pricing_view,
    about_view,
    contact_view,
    settings_view,
    devices_view,
    start_payment,
    verify_payment
)

urlpatterns = [
    path('', humanizer_view, name='humanizer'),
    path('humanize/', humanize_ajax, name='humanize_ajax'),
    path('api/modes/', get_modes, name='get_modes'),
    path('api/models/', get_models, name='get_models'),
    path('pricing/', pricing_view, name='pricing'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('settings/', settings_view, name='settings'),
    path('devices/', devices_view, name='devices'),
    path('start-payment/', start_payment, name='start-payment'),
    path('verify-payment/', verify_payment, name='verify-payment'),
]
