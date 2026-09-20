import uuid
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .catalog import (
    AI_OFFERS,
    COMMUNICATION_OFFERS,
    LEGACY_PAYMENT_BANDS,
    RETAINER_PLANS,
    SELF_SERVE_PLANS,
    SERVICE_BY_SLUG,
    SERVICE_FAMILIES,
    STUDIO_OFFERS,
    estimate_project,
    payment_structure,
)


def _projects(request):
    return request.session.get("infini_projects", {})


def _save_projects(request, projects):
    request.session["infini_projects"] = projects
    request.session.modified = True


def _get_project(request, project_id):
    return _projects(request).get(str(project_id))


def _project_id():
    return uuid.uuid4().hex[:12].upper()


def _common(page, **kwargs):
    return {
        "page": page,
        "services": SERVICE_FAMILIES,
        "self_serve_plans": SELF_SERVE_PLANS,
        "studio_offers": STUDIO_OFFERS,
        "retainer_plans": RETAINER_PLANS,
        "communication_offers": COMMUNICATION_OFFERS,
        "ai_offers": AI_OFFERS,
        **kwargs,
    }


def home(request):
    return render(request, "platform/site.html", _common("home"))


def services(request):
    return render(request, "platform/site.html", _common("services"))


def service_detail(request, slug):
    service = SERVICE_BY_SLUG.get(slug)
    if not service:
        return redirect("platform:services")
    return render(request, "platform/site.html", _common("service_detail", service=service))


def pricing(request):
    return render(request, "platform/site.html", _common("pricing"))


def originality(request):
    return render(
        request,
        "platform/site.html",
        _common("originality", service=SERVICE_BY_SLUG["content-assurance"]),
    )


def enterprise(request):
    return render(request, "platform/site.html", _common("enterprise"))


@require_http_methods(["GET", "POST"])
def start_project(request):
    initial_slug = request.GET.get("service", "research-production")
    if initial_slug not in SERVICE_BY_SLUG:
        initial_slug = "research-production"

    if request.method == "POST":
        service_slug = request.POST.get("service", initial_slug)
        if service_slug not in SERVICE_BY_SLUG:
            service_slug = "research-production"

        research_depth = request.POST.get("research_depth", "standard")
        complexity = request.POST.get("complexity", "standard")
        urgency = request.POST.get("urgency", "standard")
        low, high = estimate_project(service_slug, research_depth, complexity, urgency)
        project_id = _project_id()
        payment = payment_structure(high)

        project = {
            "id": project_id,
            "service": service_slug,
            "service_name": SERVICE_BY_SLUG[service_slug]["name"],
            "objective": request.POST.get("objective", "").strip(),
            "deliverable": request.POST.get("deliverable", "").strip(),
            "audience": request.POST.get("audience", "").strip(),
            "source_state": request.POST.get("source_state", "").strip(),
            "research_depth": research_depth,
            "complexity": complexity,
            "urgency": urgency,
            "deadline": request.POST.get("deadline", "").strip(),
            "budget": request.POST.get("budget", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "estimate_low": low,
            "estimate_high": high,
            "payment": payment,
            "status": "scope_ready",
            "invoice_status": "not_requested",
            "payment_status": "not_started",
            "timeline": [
                {"state": "Request received", "done": True},
                {"state": "Scope ready", "done": True},
                {"state": "Quote approval", "done": False},
                {"state": "Production", "done": False},
                {"state": "Review", "done": False},
                {"state": "Delivery", "done": False},
            ],
        }
        projects = _projects(request)
        projects[project_id] = project
        _save_projects(request, projects)
        return redirect("platform:scope", project_id=project_id)

    return render(
        request,
        "platform/site.html",
        _common("start", initial_service=SERVICE_BY_SLUG[initial_slug]),
    )


def scope(request, project_id):
    project = _get_project(request, project_id)
    if not project:
        messages.error(request, "That project is not available in this session.")
        return redirect("platform:start")
    return render(request, "platform/site.html", _common("scope", project=project))


@require_http_methods(["GET", "POST"])
def checkout(request, project_id):
    project = _get_project(request, project_id)
    if not project:
        messages.error(request, "That project is not available in this session.")
        return redirect("platform:start")

    due = round(project["estimate_high"] * project["payment"]["percent"] / 100, 2)
    project["amount_due"] = due

    if request.method == "POST":
        action = request.POST.get("action")
        projects = _projects(request)

        if action == "invoice":
            project["invoice_status"] = "requested"
            project["status"] = "awaiting_invoice"
            projects[project_id] = project
            _save_projects(request, projects)
            messages.success(
                request,
                "Invoice request recorded. The project remains unconfirmed until payment terms are accepted.",
            )
            return redirect("platform:project_detail", project_id=project_id)

        if action == "paystack":
            if not settings.PAYSTACK_SECRET_KEY:
                messages.warning(
                    request,
                    "Online checkout is not connected on this deployment yet. Request an invoice instead.",
                )
                return redirect("platform:checkout", project_id=project_id)

            email = project.get("email") or (
                request.user.email if request.user.is_authenticated else ""
            )
            if not email:
                messages.error(request, "Add an email address before starting online payment.")
                return redirect("platform:checkout", project_id=project_id)

            usd_kes_rate = Decimal(str(getattr(settings, "USD_KES_RATE", 135)))
            kes_amount = int(Decimal(str(due)) * usd_kes_rate * 100)
            callback = request.build_absolute_uri(
                reverse("platform:verify_payment", kwargs={"project_id": project_id})
            )
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "email": email,
                "amount": kes_amount,
                "currency": "KES",
                "callback_url": callback,
                "metadata": {
                    "project_id": project_id,
                    "service": project["service"],
                    "quoted_currency": "USD",
                    "quoted_amount": due,
                },
            }
            try:
                response = requests.post(
                    "https://api.paystack.co/transaction/initialize",
                    json=payload,
                    headers=headers,
                    timeout=20,
                )
                data = response.json()
                if data.get("status") and data.get("data", {}).get("authorization_url"):
                    project["payment_status"] = "checkout_started"
                    projects[project_id] = project
                    _save_projects(request, projects)
                    return redirect(data["data"]["authorization_url"])
            except Exception:
                pass
            messages.error(request, "Payment checkout could not be started. Request an invoice instead.")

    return render(
        request,
        "platform/site.html",
        _common(
            "checkout",
            project=project,
            amount_due=due,
            paystack_ready=bool(settings.PAYSTACK_SECRET_KEY),
        ),
    )


def verify_payment(request, project_id):
    project = _get_project(request, project_id)
    if not project:
        return redirect("platform:projects")
    reference = request.GET.get("reference")
    if not reference or not settings.PAYSTACK_SECRET_KEY:
        messages.error(request, "Payment verification is unavailable.")
        return redirect("platform:project_detail", project_id=project_id)

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    try:
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers,
            timeout=20,
        )
        data = response.json()
        if data.get("status") and data.get("data", {}).get("status") == "success":
            projects = _projects(request)
            project["payment_status"] = "paid"
            project["status"] = "confirmed"
            project["payment_reference"] = reference
            project["timeline"][2]["done"] = True
            projects[project_id] = project
            _save_projects(request, projects)
            messages.success(request, "Payment verified. The engagement is confirmed.")
        else:
            messages.error(request, "Payment was not verified.")
    except Exception:
        messages.error(request, "Payment verification could not be completed.")
    return redirect("platform:project_detail", project_id=project_id)


def projects(request):
    items = list(_projects(request).values())
    items.reverse()
    return render(request, "platform/site.html", _common("projects", projects=items))


def project_detail(request, project_id):
    project = _get_project(request, project_id)
    if not project:
        messages.error(request, "That project is not available in this session.")
        return redirect("platform:projects")
    return render(request, "platform/site.html", _common("project_detail", project=project))


@require_http_methods(["GET", "POST"])
def consultation(request):
    if request.method == "POST":
        project_id = _project_id()
        project = {
            "id": project_id,
            "service": "consultation",
            "service_name": "Consultation",
            "objective": request.POST.get("question", "").strip(),
            "deliverable": "50-minute working session + written next-step summary",
            "audience": request.POST.get("company", "").strip(),
            "source_state": request.POST.get("context", "").strip(),
            "research_depth": "light",
            "complexity": "focused",
            "urgency": "standard",
            "deadline": request.POST.get("preferred_time", "").strip(),
            "budget": "$50",
            "email": request.POST.get("email", "").strip(),
            "estimate_low": 50,
            "estimate_high": 50,
            "payment": {
                "label": "Full payment",
                "percent": 100,
                "explanation": "Consultations are confirmed when the $50 session fee is paid.",
            },
            "status": "scope_ready",
            "invoice_status": "not_requested",
            "payment_status": "not_started",
            "timeline": [
                {"state": "Request received", "done": True},
                {"state": "Session scope ready", "done": True},
                {"state": "Payment / confirmation", "done": False},
                {"state": "Consultation", "done": False},
                {"state": "Written next steps", "done": False},
            ],
        }
        projects = _projects(request)
        projects[project_id] = project
        _save_projects(request, projects)
        return redirect("platform:scope", project_id=project_id)
    return render(request, "platform/site.html", _common("consultation"))


@staff_member_required
def reconciliation(request):
    return render(
        request,
        "platform/site.html",
        _common(
            "reconciliation",
            legacy_bands=LEGACY_PAYMENT_BANDS,
            legacy_summary={
                "rows": 169,
                "successful": 68,
                "abandoned": 77,
                "failed": 24,
                "currencies": "KES and USD",
                "successful_ranges": "USD $1–$500; KES KSh 20–KSh 2,000",
            },
        ),
    )
