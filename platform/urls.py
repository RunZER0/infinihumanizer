from django.urls import path

from . import views

app_name = "platform"

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("pricing/", views.pricing, name="pricing"),
    path("originality/", views.originality, name="originality"),
    path("enterprise/", views.enterprise, name="enterprise"),
    path("start/", views.start_project, name="start"),
    path("scope/<str:project_id>/", views.scope, name="scope"),
    path("checkout/<str:project_id>/", views.checkout, name="checkout"),
    path("payment/verify/<str:project_id>/", views.verify_payment, name="verify_payment"),
    path("projects/", views.projects, name="projects"),
    path("projects/<str:project_id>/", views.project_detail, name="project_detail"),
    path("consultation/", views.consultation, name="consultation"),
    path("operations/reconciliation/", views.reconciliation, name="reconciliation"),
]
