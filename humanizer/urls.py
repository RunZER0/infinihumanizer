from django.urls import path

from .views import humanize_ajax, humanizer_view, save_humanization

urlpatterns = [
    path("", humanizer_view, name="humanizer"),
    path("humanize/", humanize_ajax, name="humanize_ajax"),
    path("save/", save_humanization, name="save_humanization"),
]
