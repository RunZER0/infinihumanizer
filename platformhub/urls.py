from django.urls import path
from . import views

app_name = "platformhub"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
    path("notes/", views.notes, name="notes"),
    path("notes/<slug:slug>/", views.note_detail, name="note_detail"),
    path("services/", views.services, name="services"),
    path("services/<slug:family_slug>/", views.service_detail, name="service_detail"),
    path("pricing/", views.pricing, name="pricing"),
    path("start/", views.start, name="start"),
    path("request/", views.request_service, name="request_service"),
    path("request/<str:service_code>/", views.request_service, name="request_service_code"),
    path("request/success/<uuid:request_id>/", views.request_success, name="request_success"),
    path("consultation/", views.consultation, name="consultation"),
    path("workspace/", views.workspace, name="workspace"),
    path("workspace/projects/", views.workspace_projects, name="workspace_projects"),
    path("workspace/billing/", views.workspace_billing, name="workspace_billing"),
    path("workspace/chat/", views.client_chat, name="client_chat"),
    path("quickpay/", views.quickpay, name="quickpay"),
    path("assurance/check/", views.assurance_check, name="assurance_check"),
    path("assurance/check/<uuid:job_id>/", views.assurance_result, name="assurance_result"),
    path("workspace/project/<uuid:request_id>/", views.project_detail, name="project_detail"),
    path("quote/<uuid:quote_id>/", views.quote_detail, name="quote_detail"),
    path("billing/checkout/", views.checkout, name="checkout"),
    path("billing/start/", views.start_checkout, name="start_checkout"),
    path("billing/verify/", views.verify_checkout, name="verify_checkout"),
    path("billing/webhook/", views.paystack_webhook, name="paystack_webhook"),
    path("billing/config/", views.payment_config, name="payment_config"),
    path(".well-known/apple-developer-merchantid-domain-association", views.apple_pay_domain, name="apple_pay_domain"),
    path("operations/reconciliation/", views.reconciliation, name="reconciliation"),
    path("health/", views.health, name="health"),
]
