from django.urls import path

from .views import humanize_ajax, humanizer_view

urlpatterns = [
    path("", humanizer_view, name="humanizer"),
    path("humanize/", humanize_ajax, name="humanize_ajax"),
]
