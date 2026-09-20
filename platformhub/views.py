import logging
import uuid
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .catalog import PACKAGES, PRICE_BANDS, RETAINERS, SERVICE_FAMILIES, SERVICE_INDEX, commercial_terms, estimate_request, service_by_code
from .models import AssuranceJob, Consultation, Invoice, PaymentRecord, Quote, ServiceRequest

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "platformhub/home.html", {
        "families": SERVICE_FAMILIES,
        "price_bands": PRICE_BANDS,
    })


def services(request):
    return render(request, "platformhub/services.html", {"families": SERVICE_FAMILIES})


def service_detail(request, family_slug):
    family = SERVICE_FAMILIES.get(family_slug)
    if not family:
        return redirect("platformhub:services")
    return render(request, "platformhub/service_detail.html", {
        "family_slug": family_slug,
        "family": family,
    })


def pricing(request):
    return render(request, "platformhub/pricing.html", {
        "packages": PACKAGES,
        "price_bands": PRICE_BANDS,
        "retainers": RETAINERS,
    })


def start(request):
    return render(request, "platformhub/start.html", {"families": SERVICE_FAMILIES})


@require_http_methods(["GET", "POST"])
def request_service(request, service_code=None):
    selected = service_by_code(service_code) if service_code else None

    if request.method == "POST":
        code = request.POST.get("service_code", "").strip()
        service = service_by_code(code)
        if not service:
            messages.error(request, "Choose the service that best matches the work.")
            return render(request, "platformhub/request_form.html", {
                "families": SERVICE_FAMILIES,
                "service_index": SERVICE_INDEX,
                "selected": selected,
                "values": request.POST,
            })

        required = {
            "full_name": request.POST.get("full_name", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "title": request.POST.get("title", "").strip(),
            "objective": request.POST.get("objective", "").strip(),
            "scope": request.POST.get("scope", "").strip(),
            "deliverable": request.POST.get("deliverable", "").strip(),
        }
        if not all(required.values()):
            messages.error(request, "Complete the required fields so the scope can be understood.")
            return render(request, "platformhub/request_form.html", {
                "families": SERVICE_FAMILIES,
                "service_index": SERVICE_INDEX,
                "selected": service,
                "values": request.POST,
            })

        research_depth = request.POST.get("research_depth", "standard")
        turnaround = request.POST.get("turnaround", "standard")
        low, high = estimate_request(code, research_depth, turnaround)

        item = ServiceRequest.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=required["full_name"],
            email=required["email"],
            company=request.POST.get("company", "").strip(),
            service_family=service["family"],
            service_code=code,
            title=required["title"],
            objective=required["objective"],
            audience=request.POST.get("audience", "").strip(),
            scope=required["scope"],
            deliverable=required["deliverable"],
            research_depth=research_depth,
            turnaround=turnaround,
            budget_band=request.POST.get("budget_band", "").strip(),
            estimate_low=low,
            estimate_high=high,
            currency="USD",
            metadata={
                "service_name": service["name"],
                "family_name": service["family_name"],
                "preferred_contact": request.POST.get("preferred_contact", "email"),
            },
        )
        request.session.setdefault("infini_request_ids", [])
        ids = request.session["infini_request_ids"]
        ids.append(str(item.id))
        request.session["infini_request_ids"] = ids[-12:]
        request.session.modified = True
        return redirect("platformhub:request_success", request_id=item.id)

    return render(request, "platformhub/request_form.html", {
        "families": SERVICE_FAMILIES,
        "service_index": SERVICE_INDEX,
        "selected": selected,
        "values": {},
    })


def request_success(request, request_id):
    item = get_object_or_404(ServiceRequest, id=request_id)
    visible = False
    if request.user.is_authenticated and item.user_id == request.user.id:
        visible = True
    if str(item.id) in request.session.get("infini_request_ids", []):
        visible = True
    if not visible:
        return redirect("platformhub:home")
    return render(request, "platformhub/request_success.html", {"item": item})


@require_http_methods(["GET", "POST"])
def consultation(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        topic = request.POST.get("topic", "").strip()
        if not full_name or not email or not topic:
            messages.error(request, "Name, email and the topic are required.")
        else:
            item = Consultation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name,
                email=email,
                company=request.POST.get("company", "").strip(),
                topic=topic,
            )
            request.session["consultation_reference"] = item.reference
            return redirect(f"{reverse('platformhub:checkout')}?package=consultation&email={email}")

    return render(request, "platformhub/consultation.html", {
        "package": PACKAGES["consultation"],
    })


def _can_view_request(request, item):
    if request.user.is_authenticated and (item.user_id == request.user.id or (request.user.email and item.email.lower() == request.user.email.lower())):
        return True
    return str(item.id) in request.session.get("infini_request_ids", [])


@login_required
def project_detail(request, request_id):
    item = get_object_or_404(ServiceRequest, id=request_id)
    if not _can_view_request(request, item):
        return redirect("platformhub:workspace")
    return render(request, "platformhub/project_detail.html", {
        "item": item,
        "quotes": item.quotes.exclude(status="draft").order_by("-created_at"),
        "invoices": item.invoices.all().order_by("-created_at"),
        "deliverables": item.deliverables.all().order_by("-updated_at"),
    })


@login_required
@require_http_methods(["GET", "POST"])
def quote_detail(request, quote_id):
    quote = get_object_or_404(Quote.objects.select_related("request"), id=quote_id)
    if not _can_view_request(request, quote.request):
        return redirect("platformhub:workspace")
    if quote.status == "draft" and not request.user.is_staff:
        messages.info(request, "This quote is still being prepared.")
        return redirect("platformhub:project_detail", request_id=quote.request_id)

    terms = commercial_terms(quote.total, quote.request.service_code)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "accept" and quote.status == "sent":
            quote.status = "accepted"
            quote.save(update_fields=["status"])
            invoice = quote.invoices.first()
            if not invoice:
                invoice = Invoice.objects.create(
                    request=quote.request,
                    quote=quote,
                    user=request.user,
                    email=quote.request.email,
                    currency=quote.currency,
                    amount_due=terms["due_now"],
                    description=f'{terms["label"]} — {quote.request.title} — accepted quote {quote.number}',
                )
            quote.request.status = "quoted"
            quote.request.save(update_fields=["status", "updated_at"])
            messages.success(request, "Quote accepted. The invoice is ready.")
            return redirect(f"{reverse('platformhub:checkout')}?invoice={invoice.id}")
        if action == "decline" and quote.status == "sent":
            quote.status = "declined"
            quote.save(update_fields=["status"])
            messages.info(request, "Quote declined. The request remains available for re-scoping.")
            return redirect("platformhub:project_detail", request_id=quote.request_id)

    return render(request, "platformhub/quote_detail.html", {"quote": quote, "terms": terms})


@login_required
@require_http_methods(["GET", "POST"])
def assurance_check(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content_text = request.POST.get("content", "").strip()
        if not title or len(content_text) < 40:
            messages.error(request, "Add a title and enough text to run a meaningful check.")
        else:
            job = AssuranceJob.objects.create(
                user=request.user,
                title=title,
                content=content_text,
                instructions=request.POST.get("instructions", "").strip(),
            )
            return redirect(f"{reverse('platformhub:checkout')}?package=originality-quick&job={job.id}&email={request.user.email}")
    return render(request, "platformhub/assurance_check.html")


@login_required
def assurance_result(request, job_id):
    job = get_object_or_404(AssuranceJob, id=job_id, user=request.user)
    return render(request, "platformhub/assurance_result.html", {"job": job})


@login_required
def workspace(request):
    items = ServiceRequest.objects.filter(user=request.user)
    if request.user.email:
        items = ServiceRequest.objects.filter(Q(user=request.user) | Q(email__iexact=request.user.email)).distinct()
    invoices = Invoice.objects.filter(user=request.user)
    if request.user.email:
        invoices = Invoice.objects.filter(Q(user=request.user) | Q(email__iexact=request.user.email)).distinct()

    return render(request, "platformhub/workspace.html", {
        "requests": items[:20],
        "invoices": invoices[:20],
        "assurance_jobs": AssuranceJob.objects.filter(user=request.user).order_by("-created_at")[:20],
    })


def _checkout_context(request):
    package_slug = request.GET.get("package", "").strip()
    invoice_id = request.GET.get("invoice", "").strip()
    currency = request.GET.get("currency", "USD").upper()
    job_id = request.GET.get("job", "").strip()
    if currency not in {"USD", "KES"}:
        currency = "USD"

    if invoice_id:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        return {
            "kind": "invoice",
            "invoice": invoice,
            "label": invoice.description or f"Invoice {invoice.number}",
            "amount": invoice.amount_due - invoice.amount_paid,
            "currency": invoice.currency,
            "email": invoice.email,
            "reference_seed": invoice.number,
        }

    package = PACKAGES.get(package_slug)
    if not package:
        return None
    amount = package["kes"] if currency == "KES" else package["usd"]
    return {
        "kind": "package",
        "package_slug": package_slug,
        "package": package,
        "label": package["name"],
        "amount": amount,
        "currency": currency,
        "email": request.GET.get("email", request.user.email if request.user.is_authenticated else ""),
        "reference_seed": package_slug,
        "job_id": job_id,
    }


def checkout(request):
    context = _checkout_context(request)
    if not context:
        return redirect("platformhub:pricing")
    context["payments_configured"] = bool(getattr(settings, "PAYSTACK_SECRET_KEY", None))
    return render(request, "platformhub/checkout.html", context)


@require_http_methods(["POST"])
def start_checkout(request):
    package_slug = request.POST.get("package_slug", "").strip()
    invoice_id = request.POST.get("invoice_id", "").strip()
    job_id = request.POST.get("job_id", "").strip()
    currency = request.POST.get("currency", "USD").upper()
    email = request.POST.get("email", "").strip()

    if invoice_id:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        amount = invoice.amount_due - invoice.amount_paid
        currency = invoice.currency
        label = invoice.description or invoice.number
        request_id = invoice.request_id
        normalized_family = invoice.request.service_family if invoice.request else ""
        normalized_service_code = invoice.request.service_code if invoice.request else ""
    else:
        package = PACKAGES.get(package_slug)
        if not package:
            return JsonResponse({"error": "Unknown package."}, status=400)
        amount = package["kes"] if currency == "KES" else package["usd"]
        label = package["name"]
        request_id = None
        normalized_service_code = package.get("service_code", "")
        normalized_family = (SERVICE_INDEX.get(normalized_service_code) or {}).get("family", "text-intelligence" if normalized_service_code == "text-humanize" else "")

    if not email:
        return JsonResponse({"error": "Email is required."}, status=400)

    secret = getattr(settings, "PAYSTACK_SECRET_KEY", None)
    if not secret:
        return JsonResponse({"error": "Secure checkout is not connected on this deployment yet."}, status=503)

    reference = f"INF-{uuid.uuid4().hex[:18].upper()}"
    callback = request.build_absolute_uri(reverse("platformhub:verify_checkout"))
    minor_units = int((Decimal(amount) * 100).quantize(Decimal("1")))

    payload = {
        "email": email,
        "amount": minor_units,
        "currency": currency,
        "reference": reference,
        "callback_url": callback,
        "metadata": {
            "label": label,
            "package_slug": package_slug,
            "invoice_id": invoice_id,
            "request_id": str(request_id) if request_id else "",
            "job_id": job_id,
        },
    }
    headers = {"Authorization": f"Bearer {secret}", "Content-Type": "application/json"}

    try:
        response = requests.post("https://api.paystack.co/transaction/initialize", json=payload, headers=headers, timeout=20)
        data = response.json()
    except Exception:
        logger.exception("Paystack initialize failed")
        return JsonResponse({"error": "Payment initialization failed."}, status=502)

    if not data.get("status"):
        return JsonResponse({"error": data.get("message", "Payment initialization failed.")}, status=400)

    PaymentRecord.objects.create(
        invoice_id=invoice_id or None,
        request_id=request_id,
        user=request.user if request.user.is_authenticated else None,
        reference=reference,
        source_type="checkout",
        amount=amount,
        currency=currency,
        status="pending",
        email=email,
        normalized_family=normalized_family,
        normalized_service_code=normalized_service_code,
        metadata=payload["metadata"],
    )
    return JsonResponse({"authorization_url": data["data"]["authorization_url"]})


def verify_checkout(request):
    reference = request.GET.get("reference", "").strip()
    if not reference:
        return redirect("platformhub:pricing")

    payment = get_object_or_404(PaymentRecord, reference=reference)
    secret = getattr(settings, "PAYSTACK_SECRET_KEY", None)
    if not secret:
        messages.error(request, "Payment verification is not connected.")
        return redirect("platformhub:pricing")

    headers = {"Authorization": f"Bearer {secret}"}
    try:
        response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers, timeout=20)
        data = response.json()
    except Exception:
        logger.exception("Paystack verification failed")
        messages.error(request, "Payment verification failed.")
        return redirect("platformhub:pricing")

    tx = data.get("data") or {}
    if data.get("status") and tx.get("status") == "success":
        paid_amount = Decimal(str(tx.get("amount", 0))) / Decimal("100")
        payment.status = "success"
        payment.amount = paid_amount
        payment.paid_at = timezone.now()
        payment.metadata = {**payment.metadata, "gateway": {"channel": tx.get("channel"), "id": tx.get("id")}}
        payment.save(update_fields=["status", "amount", "paid_at", "metadata"])

        if payment.invoice:
            invoice = payment.invoice
            invoice.amount_paid = min(invoice.amount_due, invoice.amount_paid + paid_amount)
            invoice.save()
            if invoice.status == "paid" and invoice.request:
                project = invoice.request
                project.status = "active"
                project.save(update_fields=["status", "updated_at"])

        job_id = payment.metadata.get("job_id", "")
        if job_id:
            try:
                job = AssuranceJob.objects.get(id=job_id)
                job.status = "queued"
                job.payment_reference = payment.reference
                job.save(update_fields=["status", "payment_reference", "updated_at"])
            except AssuranceJob.DoesNotExist:
                logger.warning("Assurance job missing for payment %s", payment.reference)

        package_slug = payment.metadata.get("package_slug", "")
        if package_slug and request.user.is_authenticated:
            try:
                from accounts.models import Profile
                profile, _ = Profile.objects.get_or_create(user=request.user)
                if package_slug == "humanizer-individual":
                    profile.account_type = "STANDARD"; profile.is_paid = True; profile.word_quota = max(profile.word_quota, 100000)
                elif package_slug == "humanizer-pro":
                    profile.account_type = "PRO"; profile.is_paid = True; profile.word_quota = max(profile.word_quota, 250000)
                elif package_slug == "humanizer-team":
                    profile.account_type = "ENTERPRISE"; profile.is_paid = True; profile.word_quota = max(profile.word_quota, 600000); profile.max_concurrent_devices = max(profile.max_concurrent_devices, 5)
                profile.save()
            except Exception:
                logger.exception("Could not apply self-service entitlement for %s", package_slug)
        messages.success(request, "Payment confirmed.")
        if job_id and request.user.is_authenticated:
            return redirect("platformhub:assurance_result", job_id=job_id)
        if request.user.is_authenticated:
            return redirect("platformhub:workspace")
        return redirect("platformhub:home")

    payment.status = tx.get("status", "failed") if tx else "failed"
    payment.save(update_fields=["status"])
    messages.error(request, "Payment was not completed.")
    return redirect("platformhub:pricing")


def health(request):
    return JsonResponse({"status": "ok", "service": "infiniai"})
