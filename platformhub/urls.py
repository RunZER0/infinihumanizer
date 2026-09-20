from django.urls import path
from . import views

app_name = "platformhub"

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("services/<slug:family_slug>/", views.service_detail, name="service_detail"),
    path("pricing/", views.pricing, name="pricing"),
    path("start/", views.start, name="start"),
    path("request/", views.request_service, name="request_service"),
    path("request/<str:service_code>/", views.request_service, name="request_service_code"),
    path("request/success/<uuid:request_id>/", views.request_success, name="request_success"),
    path("consultation/", views.consultation, name="consultation"),
    path("workspace/", views.workspace, name="workspace"),
    path("billing/checkout/", views.checkout, name="checkout"),
    path("billing/start/", views.start_checkout, name="start_checkout"),
    path("billing/verify/", views.verify_checkout, name="verify_checkout"),
    path("health/", views.health, name="health"),
]
