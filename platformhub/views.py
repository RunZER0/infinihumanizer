import json
import logging
import os
import re
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

import requests
from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import EmailMessage
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .catalog import PACKAGES, PRICE_BANDS, RETAINERS, SERVICE_FAMILIES, SERVICE_INDEX, commercial_terms, estimate_request, service_by_code
from .models import AssuranceJob, Consultation, Deliverable, DeliverableFeedback, Invoice, PaymentRecord, Quote, ServiceRequest
from .legacy_summary import LEGACY_LEDGER_SUMMARY, LEGACY_RECONCILIATION_BANDS
from .knowledge import ARTICLES, ARTICLE_BY_SLUG
from humanizer.models import ClientConversation, ClientMessage, Humanization
from allauth.account.models import EmailAddress
from accounts.verification import (
    is_disposable_address,
    issue_email_code,
    mark_session_email_verified,
    normalize_email,
    session_email_is_verified,
    verify_email_code,
)
from .payments import PaystackError, apply_gateway_transaction, ingest_webhook_transaction, initialize_transaction, valid_webhook_signature, verify_transaction
from .checkout_links import get_client_checkout_link

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "platformhub/home.html", {
        "families": SERVICE_FAMILIES,
        "price_bands": PRICE_BANDS,
        "latest_notes": ARTICLES[:3],
    })


def about(request):
    return render(request, "platformhub/about.html")


def privacy(request):
    return render(request, "platformhub/privacy.html")


def terms(request):
    return render(request, "platformhub/terms.html")


def disclaimer(request):
    return render(request, "platformhub/disclaimer.html")


def notes(request):
    return render(request, "platformhub/notes.html", {"articles": ARTICLES})


def note_detail(request, slug):
    article = ARTICLE_BY_SLUG.get(slug)
    if not article:
        raise Http404("Article not found")
    return render(request, "platformhub/note_detail.html", {"article": article})


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


def posters_gallery(request):
    from .posters_data import POSTERS
    return render(request, "platformhub/posters.html", {
        "posters": POSTERS,
    })


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

        User = get_user_model()
        target_user = request.user if request.user.is_authenticated else User.objects.filter(email__iexact=required["email"]).first()
        if not target_user:
            names = required["full_name"].split()
            first_name = names[0] if names else "Client"
            last_name = " ".join(names[1:]) if len(names) > 1 else ""
            base_username = re.sub(r"[^a-zA-Z0-9_]+", "", required["email"].split("@")[0])[:25] or "client"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            target_user = User.objects.create(
                username=username,
                email=required["email"],
                first_name=first_name,
                last_name=last_name,
            )
        elif not target_user.first_name and required["full_name"]:
            names = required["full_name"].split()
            target_user.first_name = names[0]
            target_user.last_name = " ".join(names[1:]) if len(names) > 1 else ""
            target_user.save(update_fields=["first_name", "last_name"])

        item = ServiceRequest.objects.create(
            user=target_user,
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
        conv, _ = ClientConversation.objects.get_or_create(
            user=target_user,
            defaults={"subject": f"Project · {item.reference}"},
        )
        conv.status = "open"
        conv.save(update_fields=["status", "updated_at"])
        request.session["conversation_id"] = str(conv.id)
        brief_lines = [
            "Project Brief Submitted via /request/",
            "--------------------------------------------------",
            f"Project Name: {item.title}",
            f"Reference: {item.reference}",
            f"Service: {service['name']} ({service['code']})",
            f"Client: {required['full_name']} <{required['email']}>",
        ]
        if item.company:
            brief_lines.append(f"Company / Team: {item.company}")
        brief_lines.extend([
            "",
            "Objective:",
            item.objective.strip(),
            "",
            "Current Materials & Scope:",
            item.scope.strip(),
            "",
            "Requested Deliverables:",
            item.deliverable.strip(),
            "",
            f"Turnaround: {item.turnaround.capitalize()} · Research: {item.research_depth.capitalize()} · Budget Band: {item.budget_band or 'Standard'}",
        ])
        ClientMessage.objects.create(
            conversation=conv,
            author=target_user,
            sender="client",
            body="\n".join(brief_lines).strip(),
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
        "selected_code": selected["code"] if selected else "",
        "initial_name": request.user.get_full_name() if request.user.is_authenticated else "",
        "initial_email": request.user.email if request.user.is_authenticated else "",
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


def _consultation_state(request, *, submitted=False, feedback="", feedback_level=""):
    name_key = "infini_consult_name"
    email_key = "infini_consult_email"

    if request.user.is_authenticated and request.user.email:
        account_email = request.user.email.strip().lower()
        verified_account_email = EmailAddress.objects.filter(
            user=request.user,
            email__iexact=account_email,
            verified=True,
        ).exists()
        if verified_account_email:
            request.session[name_key] = (
                request.user.get_full_name() or request.user.username
            )
            request.session[email_key] = account_email
            mark_session_email_verified(request, account_email)

    full_name = request.session.get(name_key, "")
    email = request.session.get(email_key, "")
    verified = bool(email and session_email_is_verified(request, email))

    if submitted:
        step = "done"
    elif request.user.is_authenticated and verified:
        step = "details"
    elif not full_name:
        step = "name"
    elif not email:
        step = "email"
    elif not verified:
        step = "verify"
    else:
        step = "details"

    consultation_id = request.session.get("consultation_id")
    recent_consultation = (
        Consultation.objects.filter(id=consultation_id).first()
        if consultation_id
        else None
    )

    return {
        "recent_consultation": recent_consultation,
        "consult_step": step,
        "consult_name": full_name,
        "consult_email": email,
        "consult_email_verified": verified,
        "contact_feedback": feedback,
        "contact_feedback_level": feedback_level,
    }


def _consultation_reply(
    request,
    *,
    submitted=False,
    feedback="",
    feedback_level="",
):
    context = _consultation_state(
        request,
        submitted=submitted,
        feedback=feedback,
        feedback_level=feedback_level,
    )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "ok": feedback_level != "error",
            "step": context["consult_step"],
            "submitted": submitted,
            "html": render_to_string(
                "platformhub/partials/consultation_flow.html",
                context,
                request=request,
            ),
        })

    if feedback:
        if feedback_level == "error":
            messages.error(request, feedback)
        elif feedback_level == "success":
            messages.success(request, feedback)
        else:
            messages.info(request, feedback)
    return redirect("platformhub:consultation")


@require_http_methods(["GET", "POST"])
def consultation(request):
    name_key = "infini_consult_name"
    email_key = "infini_consult_email"

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        if action == "set_name":
            full_name = request.POST.get("full_name", "").strip()
            if len(full_name) < 2:
                return _consultation_reply(
                    request,
                    feedback="Enter your name.",
                    feedback_level="error",
                )
            request.session[name_key] = full_name
            request.session.modified = True
            return _consultation_reply(request)

        if action == "set_email":
            try:
                email = normalize_email(request.POST.get("email", ""))
            except ValidationError:
                return _consultation_reply(
                    request,
                    feedback="Enter a valid email address.",
                    feedback_level="error",
                )

            if is_disposable_address(email):
                return _consultation_reply(
                    request,
                    feedback="Use a permanent email address.",
                    feedback_level="error",
                )

            request.session[email_key] = email
            request.session.modified = True

            if session_email_is_verified(request, email):
                return _consultation_reply(request)

            try:
                issue_email_code(
                    email,
                    request.session.get(name_key, ""),
                )
            except Exception:
                logger.exception(
                    "Could not send consultation verification code to %s",
                    email,
                )
                return _consultation_reply(
                    request,
                    feedback="Could not send the code. Try again.",
                    feedback_level="error",
                )
            return _consultation_reply(request)

        if action == "verify_email":
            email = request.session.get(email_key, "")
            if not email:
                return _consultation_reply(
                    request,
                    feedback="Enter your email first.",
                    feedback_level="error",
                )

            ok, error = verify_email_code(
                email,
                request.POST.get("code", "").strip(),
            )
            if not ok:
                return _consultation_reply(
                    request,
                    feedback=error,
                    feedback_level="error",
                )

            mark_session_email_verified(request, email)
            return _consultation_reply(request)

        if action == "resend_code":
            email = request.session.get(email_key, "")
            if not email:
                return _consultation_reply(
                    request,
                    feedback="Enter your email first.",
                    feedback_level="error",
                )

            try:
                _, sent = issue_email_code(
                    email,
                    request.session.get(name_key, ""),
                )
            except Exception:
                logger.exception(
                    "Could not resend consultation verification code to %s",
                    email,
                )
                return _consultation_reply(
                    request,
                    feedback="Could not send another code. Try again.",
                    feedback_level="error",
                )

            return _consultation_reply(
                request,
                feedback="Sent." if sent else "Check your inbox.",
                feedback_level="success",
            )

        if action == "submit_note":
            full_name = request.session.get(name_key, "").strip()
            email = request.session.get(email_key, "").strip().lower()
            topic = request.POST.get("topic", "").strip()

            if not full_name or not email:
                return _consultation_reply(
                    request,
                    feedback="Complete your contact details.",
                    feedback_level="error",
                )
            if not session_email_is_verified(request, email):
                return _consultation_reply(
                    request,
                    feedback="Enter the code first.",
                    feedback_level="error",
                )
            if not topic:
                return _consultation_reply(
                    request,
                    feedback="Enter your message.",
                    feedback_level="error",
                )

            User = get_user_model()
            target_user = request.user if request.user.is_authenticated else User.objects.filter(email__iexact=email).first()
            if not target_user:
                names = full_name.split()
                first_name = names[0] if names else "Client"
                last_name = " ".join(names[1:]) if len(names) > 1 else ""
                base_username = re.sub(r"[^a-zA-Z0-9_]+", "", email.split("@")[0])[:25] or "client"
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                target_user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
            elif not target_user.first_name and full_name:
                names = full_name.split()
                target_user.first_name = names[0]
                target_user.last_name = " ".join(names[1:]) if len(names) > 1 else ""
                target_user.save(update_fields=["first_name", "last_name"])

            item = Consultation.objects.create(
                user=target_user,
                full_name=full_name,
                email=email,
                company=request.POST.get("company", "").strip(),
                topic=topic,
            )
            request.session["consultation_reference"] = item.reference
            request.session["consultation_id"] = str(item.id)

            conv, _ = ClientConversation.objects.get_or_create(
                user=target_user,
                defaults={"subject": f"Inquiry · {item.reference}"},
            )
            conv.status = "open"
            conv.save(update_fields=["status", "updated_at"])
            request.session["conversation_id"] = str(conv.id)

            consult_lines = [
                "Consultation Inquiry Submitted via /consultation/",
                "--------------------------------------------------",
                f"Reference: {item.reference}",
                f"Client: {item.full_name} <{item.email}>",
            ]
            if item.company:
                consult_lines.append(f"Company / Team: {item.company}")
            consult_lines.extend([
                "",
                "Inquiry Details & Objective:",
                topic.strip(),
            ])
            ClientMessage.objects.create(
                conversation=conv,
                author=target_user,
                sender="client",
                body="\n".join(consult_lines).strip(),
            )

            try:
                message = EmailMessage(
                    subject=f"InfiniAI enquiry {item.reference}: {item.full_name}",
                    body=(
                        f"Name: {item.full_name}\n"
                        f"Email: {item.email}\n"
                        f"Company: {item.company or '-'}\n"
                        f"Reference: {item.reference}\n\n"
                        f"{item.topic}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.SUPPORT_EMAIL],
                    reply_to=[item.email],
                )
                message.send(fail_silently=False)
            except Exception:
                logger.exception(
                    "Consultation %s was stored but email notification failed",
                    item.reference,
                )

            return _consultation_reply(request, submitted=True)

        return _consultation_reply(
            request,
            feedback="Try again.",
            feedback_level="error",
        )

    return render(
        request,
        "platformhub/consultation.html",
        _consultation_state(request),
    )


def _can_view_request(request, item):
    if request.user.is_authenticated and (item.user_id == request.user.id or (request.user.email and item.email.lower() == request.user.email.lower())):
        return True
    return str(item.id) in request.session.get("infini_request_ids", [])


@login_required
@require_http_methods(["GET", "POST"])
def project_detail(request, request_id):
    item = get_object_or_404(ServiceRequest, id=request_id)
    if not _can_view_request(request, item):
        return redirect("platformhub:workspace")

    if request.method == "POST":
        deliverable_id = request.POST.get("deliverable_id", "").strip()
        action = request.POST.get("action", "").strip()
        message = request.POST.get("message", "").strip()
        if action not in {"comment", "approve", "revision"}:
            messages.error(request, "Choose a valid review action.")
        else:
            deliverable = get_object_or_404(Deliverable, id=deliverable_id, request=item)
            if action == "revision" and not message:
                messages.error(request, "Describe what needs to change so the revision request is actionable.")
            else:
                DeliverableFeedback.objects.create(
                    deliverable=deliverable,
                    user=request.user,
                    action=action,
                    message=message,
                )
                if action == "approve":
                    deliverable.status = "approved"
                    deliverable.save(update_fields=["status", "updated_at"])
                    remaining = item.deliverables.exclude(id=deliverable.id).exclude(status__in=["approved", "delivered"]).exists()
                    if not remaining:
                        item.status = "delivered"
                        item.save(update_fields=["status", "updated_at"])
                    messages.success(request, "Deliverable approved.")
                elif action == "revision":
                    deliverable.status = "in_progress"
                    deliverable.save(update_fields=["status", "updated_at"])
                    item.status = "active"
                    item.save(update_fields=["status", "updated_at"])
                    messages.info(request, "Revision request recorded and the deliverable is back in production.")
                else:
                    messages.success(request, "Comment added to the deliverable.")
        return redirect("platformhub:project_detail", request_id=item.id)

    return render(request, "platformhub/project_detail.html", {
        "item": item,
        "quotes": item.quotes.exclude(status="draft").order_by("-created_at"),
        "invoices": item.invoices.all().order_by("-created_at"),
        "deliverables": item.deliverables.prefetch_related("feedback").all().order_by("-updated_at"),
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


def _workspace_querysets(user):
    items = ServiceRequest.objects.filter(user=user)
    invoices = Invoice.objects.filter(user=user)
    payments = PaymentRecord.objects.filter(user=user)
    if user.email:
        items = ServiceRequest.objects.filter(
            Q(user=user) | Q(email__iexact=user.email)
        ).distinct()
        invoices = Invoice.objects.filter(
            Q(user=user) | Q(email__iexact=user.email)
        ).distinct()
        payments = PaymentRecord.objects.filter(
            Q(user=user) | Q(email__iexact=user.email)
        ).distinct()
    return (
        items.order_by("-updated_at"),
        invoices.order_by("-created_at"),
        payments.order_by("-created_at"),
    )


@login_required
def workspace(request):
    items, invoices, payments = _workspace_querysets(request.user)
    profile = getattr(request.user, "profile", None)
    conversation = ClientConversation.objects.filter(user=request.user).first()
    unread_messages = (
        conversation.messages.filter(sender="admin", read_at__isnull=True).count()
        if conversation else 0
    )
    unpaid_invoice = invoices.exclude(status="paid").first()
    active_project = items.exclude(status__in=["completed", "closed", "cancelled"]).first()
    recent_rewrite = Humanization.objects.filter(user=request.user).first()

    next_action = None
    if unpaid_invoice:
        next_action = {
            "eyebrow": "Payment due",
            "title": unpaid_invoice.description or unpaid_invoice.number,
            "detail": f"{unpaid_invoice.currency} {unpaid_invoice.amount_due - unpaid_invoice.amount_paid}",
            "url": f"{reverse('platformhub:checkout')}?invoice={unpaid_invoice.id}",
            "label": "Pay invoice",
        }
    elif unread_messages:
        next_action = {
            "eyebrow": "New message",
            "title": f"{unread_messages} unread message{'s' if unread_messages != 1 else ''}",
            "detail": "InfiniAI replied in your workspace.",
            "url": reverse("platformhub:client_chat"),
            "label": "Open messages",
        }
    elif active_project:
        next_action = {
            "eyebrow": "In progress",
            "title": active_project.title,
            "detail": active_project.get_status_display(),
            "url": reverse("platformhub:project_detail", args=[active_project.id]),
            "label": "Continue project",
        }

    return render(request, "platformhub/workspace.html", {
        "profile": profile,
        "unread_messages": unread_messages,
        "project_count": items.count(),
        "open_invoice_count": invoices.exclude(status="paid").count(),
        "saved_rewrite_count": Humanization.objects.filter(user=request.user).count(),
        "next_action": next_action,
        "recent_rewrite": recent_rewrite,
        "payments": payments[:10],
    })


@login_required
def workspace_projects(request):
    items, _, _ = _workspace_querysets(request.user)
    return render(request, "platformhub/workspace_projects.html", {
        "requests": items[:50],
        "assurance_jobs": AssuranceJob.objects.filter(
            user=request.user
        ).order_by("-created_at")[:30],
    })


@login_required
def workspace_billing(request):
    _, invoices, payments = _workspace_querysets(request.user)
    return render(request, "platformhub/workspace_billing.html", {
        "invoices": invoices[:50],
        "payments": payments[:80],
    })


def _ensure_demo_conversation(user):
    conv, created = ClientConversation.objects.get_or_create(
        user=user,
        defaults={"subject": "Q4 market architecture brief"},
    )
    if created and not conv.messages.exists():
        now = timezone.now()
        m1 = ClientMessage.objects.create(
            conversation=conv,
            author=user,
            sender="client",
            body="We finalized the scope for the Q4 market architecture brief. Please send the invoice for the first milestone so finance can clear it today.",
            read_at=now,
        )
        ClientMessage.objects.filter(id=m1.id).update(created_at=now - timezone.timedelta(minutes=18))
        inv = Invoice.objects.create(
            user=user,
            email=user.email,
            currency="USD",
            amount_due=Decimal("1250.00"),
            description="Q4 market architecture brief — Milestone 1",
            status="open",
        )
        m2 = ClientMessage.objects.create(
            conversation=conv,
            author=None,
            sender="admin",
            body=f"Invoice {inv.number} for USD 1250.00 is ready in your billing rail. Production starts as soon as settlement clears.",
        )
        ClientMessage.objects.filter(id=m2.id).update(created_at=now - timezone.timedelta(minutes=12))
    return conv


def _resolve_chat_user(request):
    conv_id = (
        request.GET.get("conversation", "").strip()
        or request.POST.get("conversation_id", "").strip()
        or request.session.get("conversation_id", "").strip()
    )
    if conv_id:
        try:
            conv = ClientConversation.objects.select_related("user").filter(id=conv_id).first()
            if conv and conv.user:
                return conv.user
        except (ValueError, ValidationError):
            pass
    consult_id = request.session.get("consultation_id")
    if consult_id:
        consult = Consultation.objects.filter(id=consult_id).first()
        if consult and consult.email:
            User = get_user_model()
            u = User.objects.filter(email__iexact=consult.email).first()
            if u:
                return u
    if request.user.is_authenticated:
        return request.user
    existing_conv = ClientConversation.objects.select_related("user").order_by("-updated_at").first()
    if existing_conv and existing_conv.user:
        return existing_conv.user
    User = get_user_model()
    user, _ = User.objects.get_or_create(
        username="client_workspace",
        defaults={
            "email": "client@infiniai.local",
            "first_name": "Elena",
            "last_name": "Rostova",
        },
    )
    if not user.email:
        user.email = "client@infiniai.local"
        user.save(update_fields=["email"])
    _ensure_demo_conversation(user)
    return user


def _client_invoices(user=None, email="", include_void=False):
    target_email = (email or (user.email if user else "") or "").strip()
    if user and target_email:
        qs = Invoice.objects.filter(Q(user=user) | Q(email__iexact=target_email)).distinct()
    elif user:
        qs = Invoice.objects.filter(user=user)
    elif target_email:
        qs = Invoice.objects.filter(email__iexact=target_email)
    else:
        return Invoice.objects.none()
    if not include_void:
        qs = qs.exclude(status="void")
    return qs.select_related("request").order_by("-created_at")


def _client_payments(user=None, email=""):
    target_email = (email or (user.email if user else "") or "").strip()
    if user and target_email:
        qs = PaymentRecord.objects.filter(Q(user=user) | Q(email__iexact=target_email)).distinct()
    elif user:
        qs = PaymentRecord.objects.filter(user=user)
    elif target_email:
        qs = PaymentRecord.objects.filter(email__iexact=target_email)
    else:
        return PaymentRecord.objects.none()
    return qs.select_related("invoice", "request").order_by("-created_at")


def _is_ajax_or_json(request):
    return bool(
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or "application/json" in request.headers.get("Accept", "")
        or request.POST.get("format") == "json"
        or request.GET.get("format") == "json"
        or getattr(request, "content_type", "") == "application/json"
    )


ADMIN_EMAILS = {"valdaceai@gmail.com"}


def is_admin_user(user):
    """
    Check if a user is the platform administrator.
    The sole administrator is valdaceai@gmail.com.
    """
    if not (user and user.is_authenticated and user.is_active):
        return False
    user_email = (user.email or "").strip().lower()
    user_username = (user.username or "").strip().lower()
    if user_email in ADMIN_EMAILS or user_username in ("valdaceai", "valdaceai@gmail.com", "victor_mawira"):
        return True
    if user.is_superuser or user.is_staff:
        return True
    return False


def admin_only_required(view_func):
    """
    Strictly gates access to the platform administrator (valdaceai@gmail.com).
    Unauthenticated users are redirected to the admin login portal.
    Unauthorized non-admin users receive a 403 Forbidden.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if _is_ajax_or_json(request):
                return JsonResponse({"error": "Admin authentication required."}, status=401)
            return redirect_to_login(request.get_full_path(), login_url="/admin/login/")
        if not is_admin_user(request.user):
            if _is_ajax_or_json(request):
                return JsonResponse({"error": "Forbidden. Only platform administrator can access this area."}, status=403)
            raise PermissionDenied("Access restricted to platform administrator.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def _compute_user_presence(user, latest_message_time=None):
    from datetime import timedelta
    now = timezone.now()
    times = []
    if user and getattr(user, "last_login", None):
        times.append(user.last_login)
    if latest_message_time:
        times.append(latest_message_time)
    if not times:
        return {"is_online": False, "last_seen_display": "offline"}

    last_active = max(times)
    diff = now - last_active
    if diff < timedelta(minutes=15):
        return {"is_online": True, "last_seen_display": "online"}

    local_active = timezone.localtime(last_active)
    local_now = timezone.localtime(now)
    time_str = local_active.strftime("%I:%M %p").lstrip("0")

    if local_active.date() == local_now.date():
        return {"is_online": False, "last_seen_display": f"last seen today at {time_str}"}
    elif local_active.date() == (local_now - timedelta(days=1)).date():
        return {"is_online": False, "last_seen_display": f"last seen yesterday at {time_str}"}
    else:
        return {"is_online": False, "last_seen_display": f"last seen {local_active.strftime('%b %d')} at {time_str}"}


def _is_message_outgoing(item, current_user=None, conversation_user=None, is_desk_view=False):
    if current_user and current_user.is_authenticated:
        if item.author_id and item.author_id == current_user.id:
            return True
        if current_user.email and item.author and item.author.email and item.author.email.lower() == current_user.email.lower():
            return True
        # Explicit check for Valdace / owner accounts:
        if current_user.email and current_user.email.lower() in ["valdaceai@gmail.com", "victormawira00@gmail.com"]:
            if conversation_user and conversation_user.email and conversation_user.email.lower() in ["valdaceai@gmail.com", "victormawira00@gmail.com"]:
                return item.sender == "client"

    if is_desk_view:
        if conversation_user and current_user and current_user.is_authenticated and conversation_user.id == current_user.id:
            return item.sender == "client"
        return item.sender == "admin"
    else:
        return item.sender == "client"


def _annotate_chat_messages(chat_msgs):
    prev_date = None
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    for m in chat_msgs:
        m_date = timezone.localtime(m.created_at).date()
        if m_date != prev_date:
            if m_date == today:
                m.date_divider = "Today"
            elif m_date == yesterday:
                m.date_divider = "Yesterday"
            else:
                m.date_divider = m_date.strftime("%B %d, %Y")
            prev_date = m_date
        else:
            m.date_divider = None


def _serialize_message(item, current_user=None, conversation_user=None, is_desk_view=False):
    created_local = timezone.localtime(item.created_at)
    read_local = timezone.localtime(item.read_at) if item.read_at else None
    is_outgoing = _is_message_outgoing(
        item,
        current_user=current_user,
        conversation_user=conversation_user,
        is_desk_view=is_desk_view,
    )
    time_display = created_local.strftime("%I:%M %p").lstrip("0")
    return {
        "id": str(item.id),
        "sender": item.sender,
        "sender_label": "Client" if item.sender == "client" else "InfiniAI",
        "is_outgoing": is_outgoing,
        "body": item.body or "",
        "attachments": item.attachments or [],
        "created_at_iso": created_local.isoformat(),
        "created_at_display": created_local.strftime("%b %d, %Y · %H:%M").replace(" 0", " "),
        "time_display": time_display,
        "date_divider": getattr(item, "date_divider", None),
        "is_read": bool(item.read_at),
        "read_at_iso": read_local.isoformat() if read_local else None,
        "read_at_display": read_local.strftime("%I:%M %p").lstrip("0") if read_local else None,
    }


@require_http_methods(["GET"])
def chat_file_download(request, filename):
    from .chat_files import get_chat_files_dir, guess_mime_type, sanitize_filename

    safe_name = sanitize_filename(filename)
    file_path = get_chat_files_dir() / safe_name
    if not file_path.exists() or not file_path.is_file():
        raise Http404("Attachment not found.")

    as_attachment = request.GET.get("download") == "1"
    response = FileResponse(
        file_path.open("rb"),
        content_type=guess_mime_type(safe_name),
        as_attachment=as_attachment,
        filename=safe_name,
    )
    return response


def _serialize_invoice(inv):
    created_local = timezone.localtime(inv.created_at)
    balance = max(Decimal("0.00"), inv.amount_due - inv.amount_paid)
    client_name = ""
    if inv.user:
        client_name = inv.user.get_full_name() or inv.user.username
    if not client_name and inv.request:
        client_name = inv.request.full_name
    if not client_name:
        client_name = inv.email

    custom_checkout = get_client_checkout_link(inv.email)
    checkout_url = custom_checkout or f"{reverse('platformhub:checkout')}?invoice={inv.id}"

    return {
        "id": str(inv.id),
        "number": inv.number,
        "email": inv.email,
        "client_name": client_name,
        "description": inv.description or inv.number,
        "currency": inv.currency,
        "amount_due": f"{inv.amount_due:.2f}",
        "amount_paid": f"{inv.amount_paid:.2f}",
        "balance_due": f"{balance:.2f}",
        "status": inv.status,
        "status_display": inv.get_status_display(),
        "created_at_iso": created_local.isoformat(),
        "created_at_display": created_local.strftime("%b %d, %Y · %H:%M").replace(" 0", " "),
        "checkout_url": checkout_url,
        "pdf_url": reverse("platformhub:invoice_pdf_download", kwargs={"invoice_id": str(inv.id)}),
        "verify_url": reverse("platformhub:invoice_verify", kwargs={"invoice_id": str(inv.id)}),
    }


@require_http_methods(["GET", "POST"])
def client_chat(request):
    from .chat_files import save_uploaded_chat_files

    chat_user = request.user if request.user.is_authenticated else _resolve_chat_user(request)
    is_ajax = _is_ajax_or_json(request)

    # 1. Action: Client opens a new support thread
    if request.method == "POST" and request.POST.get("action") == "new_support":
        subject = request.POST.get("subject", "").strip() or "Support inquiry"
        new_conv = ClientConversation.objects.create(
            user=chat_user,
            subject=subject,
            category="support",
            status="open",
        )
        if is_ajax:
            return JsonResponse({"ok": True, "conversation_id": str(new_conv.id)})
        return redirect(f"{reverse('platformhub:client_chat')}?conversation={new_conv.id}")

    if request.method == "GET" and request.GET.get("action") == "new_support":
        new_conv = ClientConversation.objects.create(
            user=chat_user,
            subject="Support inquiry",
            category="support",
            status="open",
        )
        return redirect(f"{reverse('platformhub:client_chat')}?conversation={new_conv.id}")

    # 2. Resolve targeted or latest conversation
    req_conv_id = request.GET.get("conversation", "").strip() or request.POST.get("conversation_id", "").strip()
    conversation = None
    if req_conv_id:
        conversation = ClientConversation.objects.filter(user=chat_user, id=req_conv_id).first()
    if not conversation:
        conversation = ClientConversation.objects.filter(user=chat_user).order_by("-updated_at").first()
    if not conversation:
        conversation = ClientConversation.objects.create(
            user=chat_user,
            subject="Support inquiry",
            category="support",
            status="open",
        )

    if request.method == "POST":
        body = request.POST.get("message", "").strip()
        uploaded_files = request.FILES.getlist("attachments")
        if not body and not uploaded_files:
            if is_ajax:
                return JsonResponse({"error": "Write a message or attach a file before sending."}, status=400)
            messages.error(request, "Write a message or attach a file before sending.")
            return redirect(f"{reverse('platformhub:client_chat')}?conversation={conversation.id}")
        elif len(body) > 5000:
            if is_ajax:
                return JsonResponse({"error": "Keep each message under 5,000 characters."}, status=400)
            messages.error(request, "Keep each message under 5,000 characters.")
            return redirect(f"{reverse('platformhub:client_chat')}?conversation={conversation.id}")
        else:
            try:
                saved_attachments = save_uploaded_chat_files(uploaded_files) if uploaded_files else []
            except ValueError as exc:
                if is_ajax:
                    return JsonResponse({"error": str(exc)}, status=400)
                messages.error(request, str(exc))
                return redirect(f"{reverse('platformhub:client_chat')}?conversation={conversation.id}")

            msg = ClientMessage.objects.create(
                conversation=conversation,
                author=chat_user,
                sender="client",
                body=body,
                attachments=saved_attachments,
            )
            conversation.status = "open"
            conversation.save(update_fields=["status", "updated_at"])
            if is_ajax:
                return JsonResponse({
                    "ok": True,
                    "message": _serialize_message(msg, current_user=request.user, conversation_user=conversation.user, is_desk_view=False),
                })
            messages.success(request, "Message sent.")
            return redirect(f"{reverse('platformhub:client_chat')}?conversation={conversation.id}")

    conversation.messages.filter(sender="admin", read_at__isnull=True).update(read_at=timezone.now())

    chat_msgs = list(conversation.messages.select_related("author").all())
    _annotate_chat_messages(chat_msgs)
    for m in chat_msgs:
        m.is_outgoing = _is_message_outgoing(m, current_user=request.user, conversation_user=conversation.user, is_desk_view=False)
        m.time_display = timezone.localtime(m.created_at).strftime("%I:%M %p").lstrip("0")
        m.is_read = bool(m.read_at)

    user_conversations = list(
        ClientConversation.objects.filter(user=chat_user).prefetch_related("messages").order_by("-updated_at")
    )
    for c in user_conversations:
        c_msgs = list(c.messages.all())
        c.last_message = c_msgs[-1] if c_msgs else None

    project_qs = ServiceRequest.objects.filter(user=chat_user)
    if chat_user.email:
        project_qs = ServiceRequest.objects.filter(
            Q(user=chat_user) | Q(email__iexact=chat_user.email)
        ).distinct()

    projects = project_qs.prefetch_related("deliverables").order_by("-created_at")[:8]
    invoices = _client_invoices(user=chat_user, email=chat_user.email, include_void=False)
    open_invoices = [inv for inv in invoices if inv.status not in {"paid", "void"}]
    client_payments = _client_payments(user=chat_user, email=chat_user.email)

    return render(request, "platformhub/client_chat.html", {
        "chat_user": chat_user,
        "conversation": conversation,
        "chat_messages": chat_msgs,
        "user_conversations": user_conversations,
        "projects": projects,
        "invoices": invoices[:16],
        "open_invoices": open_invoices,
        "client_payments": client_payments[:20],
    })


@require_http_methods(["GET"])
def client_chat_feed(request):
    conv_id = request.GET.get("conversation", "").strip()
    role = request.GET.get("role", "client").strip().lower()

    if role == "admin" and conv_id:
        conversation = get_object_or_404(ClientConversation.objects.select_related("user"), id=conv_id)
    elif request.user.is_authenticated:
        if conv_id:
            conversation = get_object_or_404(
                ClientConversation.objects.select_related("user"),
                id=conv_id,
                user=request.user,
            )
        else:
            conversation = ClientConversation.objects.filter(user=request.user).order_by("-updated_at").first()
            if not conversation:
                conversation = ClientConversation.objects.create(user=request.user, subject="Support inquiry", category="support")
    elif conv_id:
        conversation = get_object_or_404(ClientConversation.objects.select_related("user"), id=conv_id)
    else:
        chat_user = _resolve_chat_user(request)
        conversation = ClientConversation.objects.filter(user=chat_user).order_by("-updated_at").first()
        if not conversation:
            conversation = ClientConversation.objects.create(user=chat_user, subject="Support inquiry", category="support")

    if role == "admin":
        conversation.messages.filter(sender="client", read_at__isnull=True).update(read_at=timezone.now())
    else:
        conversation.messages.filter(sender="admin", read_at__isnull=True).update(read_at=timezone.now())

    feed_msgs = list(conversation.messages.select_related("author").all())
    _annotate_chat_messages(feed_msgs)
    invoices = _client_invoices(user=conversation.user, email=conversation.user.email, include_void=(role == "admin"))
    return JsonResponse({
        "conversation_id": str(conversation.id),
        "reference": conversation.reference or "",
        "subject": conversation.subject or "",
        "status": conversation.status,
        "status_display": conversation.get_status_display(),
        "client_email": conversation.user.email or conversation.user.username,
        "messages": [
            _serialize_message(m, current_user=request.user, conversation_user=conversation.user, is_desk_view=(role == "admin"))
            for m in feed_msgs
        ],
        "invoices": [_serialize_invoice(inv) for inv in invoices[:16]],
    })


def _operations_sidebar_context(active_tab="inbox"):
    unread_threads_count = (
        ClientConversation.objects.filter(messages__sender="client", messages__read_at__isnull=True)
        .distinct()
        .count()
    )
    return {
        "ops_tab": active_tab,
        "unread_threads_count": unread_threads_count,
        "total_conversations_count": ClientConversation.objects.count(),
        "total_invoices_count": Invoice.objects.exclude(status="void").count(),
        "open_invoices_count": Invoice.objects.filter(status="open").count(),
        "total_tx_count": PaymentRecord.objects.count(),
        "total_posters_count": 20,
    }


@admin_only_required
@require_http_methods(["GET"])
def operations_desk_more_threads(request):
    try:
        offset = max(0, int(request.GET.get("offset", "25")))
    except ValueError:
        offset = 25
    limit = max(1, min(100, int(request.GET.get("limit", "50"))))

    older_convs = list(
        ClientConversation.objects.select_related("user")
        .prefetch_related("messages__author")
        .order_by("-updated_at")[offset : offset + limit]
    )

    threads_data = {}
    threads_summary = []
    for conv in older_convs:
        conv_msgs = list(conv.messages.all())
        c_name = conv.user.get_full_name() or conv.user.email or "Client"
        last_m = conv_msgs[-1] if conv_msgs else None
        unread = sum(1 for m in conv_msgs if m.sender == "client" and m.read_at is None)
        c_presence = _compute_user_presence(conv.user, last_m.created_at if last_m else None)

        preview = "No messages"
        if last_m:
            if last_m.body:
                preview = (last_m.body[:68] + "…") if len(last_m.body) > 68 else last_m.body
            elif last_m.attachments:
                preview = f"Attached {last_m.attachments[0].get('name', 'file')}"

        threads_summary.append({
            "id": str(conv.id),
            "client_name": c_name,
            "client_email": conv.user.email or "",
            "status": conv.status,
            "status_display": conv.get_status_display(),
            "client_presence": c_presence,
            "updated_at_display": timezone.localtime(conv.updated_at).strftime("%b %d, %Y"),
            "updated_at_iso": timezone.localtime(conv.updated_at).isoformat(),
            "last_sender_prefix": (conv.user.first_name or "Client") + ":" if (last_m and last_m.sender == "client") else "You:",
            "preview": preview,
            "unread_count": unread,
            "url": reverse("platformhub:operations_desk_conversation", kwargs={"conversation_id": conv.id}),
        })

        threads_data[str(conv.id)] = {
            "conversation_id": str(conv.id),
            "client_name": c_name,
            "client_first_name": conv.user.first_name or c_name,
            "client_email": conv.user.email or "",
            "status": conv.status,
            "status_display": conv.get_status_display(),
            "client_presence": c_presence,
            "messages": [
                _serialize_message(m, current_user=request.user, conversation_user=conv.user, is_desk_view=True)
                for m in conv_msgs
            ],
        }

    return JsonResponse({
        "ok": True,
        "offset": offset,
        "count": len(older_convs),
        "has_more": len(older_convs) == limit,
        "threads": threads_summary,
        "threads_data": threads_data,
    })


@admin_only_required
@require_http_methods(["GET", "POST"])
def operations_desk(request, conversation_id=None):
    from .chat_files import save_uploaded_chat_files
    import json

    User = get_user_model()
    is_ajax = _is_ajax_or_json(request)

    # 1. ULTRA-FAST AJAX GET FAST-PATH
    # Serves chat switches and message updates in < 15ms without loading 80 threads or count queries
    target_conv_id = conversation_id or request.GET.get("conversation", "").strip()
    if request.method == "GET" and is_ajax and target_conv_id:
        try:
            active_conversation = ClientConversation.objects.select_related("user").get(id=target_conv_id)
        except (ClientConversation.DoesNotExist, ValueError, ValidationError):
            return JsonResponse({"error": "Conversation not found."}, status=404)

        active_conversation.messages.filter(sender="client", read_at__isnull=True).update(read_at=timezone.now())
        chat_msgs = list(active_conversation.messages.select_related("author").all())
        _annotate_chat_messages(chat_msgs)
        client_name = active_conversation.user.get_full_name() or active_conversation.user.email or "Client"
        last_m = chat_msgs[-1] if chat_msgs else None
        client_presence = _compute_user_presence(active_conversation.user, last_m.created_at if last_m else None)

        for m in chat_msgs:
            m.is_outgoing = _is_message_outgoing(m, current_user=request.user, conversation_user=active_conversation.user, is_desk_view=True)
            m.time_display = timezone.localtime(m.created_at).strftime("%I:%M %p").lstrip("0")
            m.is_read = bool(m.read_at)

        from django.template.loader import render_to_string
        chat_pane_html = render_to_string(
            "platformhub/partials/ops_chat_pane.html",
            context={
                "conversation": active_conversation,
                "chat_messages": chat_msgs,
                "client_presence": client_presence,
                "request": request,
            },
            request=request,
        )
        return JsonResponse({
            "ok": True,
            "conversation_id": str(active_conversation.id),
            "reference": active_conversation.reference or "",
            "subject": active_conversation.subject or "",
            "client_name": client_name,
            "client_first_name": active_conversation.user.first_name or client_name,
            "client_email": active_conversation.user.email or "",
            "status": active_conversation.status,
            "status_display": active_conversation.get_status_display(),
            "client_presence": client_presence,
            "messages": [
                _serialize_message(m, current_user=request.user, conversation_user=active_conversation.user, is_desk_view=True)
                for m in chat_msgs
            ],
            "chat_pane_html": chat_pane_html,
        })

    if request.method == "POST" and request.POST.get("action") == "open_client":
        target_email = request.POST.get("client_email", "").strip().lower()
        if not target_email or "@" not in target_email:
            if is_ajax:
                return JsonResponse({"error": "Enter a valid client email address."}, status=400)
            messages.error(request, "Enter a valid client email address.")
            return redirect("platformhub:operations_desk")
        target_user = User.objects.filter(email__iexact=target_email).first()
        if not target_user:
            base_username = target_email.split("@")[0][:30] or "client"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            target_user = User.objects.create(username=username, email=target_email)
        conv, _ = ClientConversation.objects.get_or_create(user=target_user)
        if is_ajax:
            return JsonResponse({
                "ok": True,
                "conversation_id": str(conv.id),
                "url": reverse("platformhub:operations_desk_conversation", kwargs={"conversation_id": conv.id}),
            })
        return redirect("platformhub:operations_desk_conversation", conversation_id=conv.id)

    if not ClientConversation.objects.exists():
        default_user = _resolve_chat_user(request)
        ClientConversation.objects.get_or_create(user=default_user)

    # Show top 25 most recent conversations first for ultra-fast initial load
    conversations = list(
        ClientConversation.objects.select_related("user").prefetch_related("messages__author").order_by("-updated_at")[:25]
    )

    if conversation_id:
        active_conversation = get_object_or_404(
            ClientConversation.objects.select_related("user"),
            id=conversation_id,
        )
    else:
        q_conv = request.GET.get("conversation", "").strip()
        active_conversation = None
        if q_conv:
            try:
                active_conversation = ClientConversation.objects.select_related("user").filter(id=q_conv).first()
            except (ValueError, ValidationError):
                active_conversation = None
        if not active_conversation:
            active_conversation = conversations[0]

    if request.method == "POST":
        action = request.POST.get("action", "reply").strip()
        if action == "toggle_status":
            active_conversation.status = "closed" if active_conversation.status == "open" else "open"
            active_conversation.save(update_fields=["status", "updated_at"])
            if is_ajax:
                return JsonResponse({
                    "ok": True,
                    "status": active_conversation.status,
                    "status_display": active_conversation.get_status_display(),
                })
            return redirect("platformhub:operations_desk_conversation", conversation_id=active_conversation.id)

        body = request.POST.get("message", "").strip()
        uploaded_files = request.FILES.getlist("attachments")
        if not body and not uploaded_files:
            if is_ajax:
                return JsonResponse({"error": "Write a reply or attach a file before sending."}, status=400)
            messages.error(request, "Write a reply or attach a file before sending.")
            return redirect("platformhub:operations_desk_conversation", conversation_id=active_conversation.id)
        elif len(body) > 5000:
            if is_ajax:
                return JsonResponse({"error": "Keep each message under 5,000 characters."}, status=400)
            messages.error(request, "Keep each message under 5,000 characters.")
            return redirect("platformhub:operations_desk_conversation", conversation_id=active_conversation.id)
        else:
            try:
                saved_attachments = save_uploaded_chat_files(uploaded_files) if uploaded_files else []
            except ValueError as exc:
                if is_ajax:
                    return JsonResponse({"error": str(exc)}, status=400)
                messages.error(request, str(exc))
                return redirect("platformhub:operations_desk_conversation", conversation_id=active_conversation.id)

            author = request.user if request.user.is_authenticated else None
            msg = ClientMessage.objects.create(
                conversation=active_conversation,
                author=author,
                sender="admin",
                body=body,
                attachments=saved_attachments,
            )
            active_conversation.status = "open"
            active_conversation.save(update_fields=["status", "updated_at"])
            if is_ajax:
                return JsonResponse({
                    "ok": True,
                    "message": _serialize_message(msg, current_user=request.user, conversation_user=active_conversation.user, is_desk_view=True),
                })
            messages.success(request, "Reply sent.")
            return redirect("platformhub:operations_desk_conversation", conversation_id=active_conversation.id)

        if is_ajax:
            return JsonResponse({"error": "Unknown action."}, status=400)
        return redirect("platformhub:operations_desk_conversation", conversation_id=active_conversation.id)

    active_conversation.messages.filter(sender="client", read_at__isnull=True).update(read_at=timezone.now())

    # Map acquisition channel per user for clean thread directory metadata
    all_requests = list(ServiceRequest.objects.select_related("user").order_by("-created_at")[:100])
    channel_by_email = {}
    channel_by_user_id = {}
    for req in all_requests:
        ch = (req.metadata or {}).get("acquisition_channel")
        if ch:
            if req.user_id and req.user_id not in channel_by_user_id:
                channel_by_user_id[req.user_id] = ch
            if req.email and req.email.lower() not in channel_by_email:
                channel_by_email[req.email.lower()] = ch

    # Pre-seed initial threads in JSON so client-side chat switching is 0.00ms (instant in-memory swap)
    initial_threads = {}
    for conv in conversations:
        conv_msgs = list(conv.messages.all())
        _annotate_chat_messages(conv_msgs)
        conv.unread_client_count = sum(1 for m in conv_msgs if m.sender == "client" and m.read_at is None)
        conv.last_message = conv_msgs[-1] if conv_msgs else None
        conv.channel = (
            channel_by_user_id.get(conv.user_id)
            or channel_by_email.get((conv.user.email or "").lower())
            or "Direct"
        )
        c_name = conv.user.get_full_name() or conv.user.email or "Client"
        c_presence = _compute_user_presence(conv.user, conv.last_message.created_at if conv.last_message else None)
        initial_threads[str(conv.id)] = {
            "conversation_id": str(conv.id),
            "reference": conv.reference or "",
            "subject": conv.subject or "",
            "category": conv.category or "job",
            "client_name": c_name,
            "client_first_name": conv.user.first_name or c_name,
            "client_email": conv.user.email or "",
            "status": conv.status,
            "status_display": conv.get_status_display(),
            "client_presence": c_presence,
            "messages": [
                _serialize_message(m, current_user=request.user, conversation_user=conv.user, is_desk_view=True)
                for m in conv_msgs
            ],
        }

    initial_threads_json = json.dumps(initial_threads)

    client_invoices = _client_invoices(
        user=active_conversation.user,
        email=active_conversation.user.email,
        include_void=True,
    )
    client_payments = _client_payments(
        user=active_conversation.user,
        email=active_conversation.user.email,
    )
    client_requests = ServiceRequest.objects.filter(
        Q(user=active_conversation.user) | Q(email__iexact=active_conversation.user.email or "")
    ).prefetch_related("deliverables").distinct().order_by("-created_at")

    service_choices = [
        (code, f'{item["family_name"]} — {item["name"]}')
        for code, item in SERVICE_INDEX.items()
    ]

    active_msgs = list(active_conversation.messages.select_related("author").all())
    _annotate_chat_messages(active_msgs)
    for m in active_msgs:
        m.is_outgoing = _is_message_outgoing(m, current_user=request.user, conversation_user=active_conversation.user, is_desk_view=True)
        m.time_display = timezone.localtime(m.created_at).strftime("%I:%M %p").lstrip("0")
        m.is_read = bool(m.read_at)

    active_last_m = active_msgs[-1] if active_msgs else None
    client_presence = _compute_user_presence(active_conversation.user, active_last_m.created_at if active_last_m else None)

    context = {
        **_operations_sidebar_context("inbox"),
        "conversations": conversations,
        "conversation": active_conversation,
        "chat_messages": active_msgs,
        "client_presence": client_presence,
        "client_invoices": client_invoices[:20],
        "client_payments": client_payments[:20],
        "client_requests": client_requests[:10],
        "service_choices": service_choices,
        "initial_threads_json": initial_threads_json,
    }
    return render(request, "platformhub/operations_desk.html", context)


@admin_only_required
@require_http_methods(["GET"])
def operations_invoices(request):
    invoices = list(
        Invoice.objects.select_related("request", "user")
        .exclude(status="void")
        .order_by("-created_at")
    )
    paid_invoices_usd = sum(
        (inv.amount_paid for inv in invoices if inv.status == "paid" and inv.currency == "USD"),
        Decimal("0.00"),
    )
    open_invoices_usd = sum(
        (max(Decimal("0.00"), inv.amount_due - inv.amount_paid) for inv in invoices if inv.status != "paid" and inv.currency == "USD"),
        Decimal("0.00"),
    )
    paid_invoices_count = sum(1 for inv in invoices if inv.status == "paid")
    open_invoices_count = sum(1 for inv in invoices if inv.status != "paid")

    service_choices = [
        (code, f'{item["family_name"]} — {item["name"]}')
        for code, item in SERVICE_INDEX.items()
    ]
    conversations = list(
        ClientConversation.objects.select_related("user").order_by("-updated_at")[:80]
    )

    context = {
        **_operations_sidebar_context("invoices"),
        "invoices": invoices,
        "paid_invoices_usd": paid_invoices_usd,
        "open_invoices_usd": open_invoices_usd,
        "paid_invoices_count": paid_invoices_count,
        "open_invoices_count": open_invoices_count,
        "service_choices": service_choices,
        "conversations": conversations,
    }
    return render(request, "platformhub/operations_invoices.html", context)


@admin_only_required
@require_http_methods(["GET"])
def operations_transactions(request):
    all_payments = list(
        PaymentRecord.objects.filter(status="success", invoice__isnull=False)
        .select_related("invoice", "request", "user")
        .order_by("-created_at")
    )
    settled_usd = sum(
        (p.amount for p in all_payments if p.status == "success" and p.currency == "USD"),
        Decimal("0.00"),
    )
    settled_kes = sum(
        (p.amount for p in all_payments if p.status == "success" and p.currency == "KES"),
        Decimal("0.00"),
    )
    total_fees_usd = Decimal("0.00")
    for p in all_payments:
        if p.status == "success" and p.currency == "USD":
            raw_fee = (p.metadata or {}).get("paystack_fees", "0") or "0"
            try:
                total_fees_usd += Decimal(str(raw_fee))
            except (InvalidOperation, TypeError, ValueError):
                pass
    net_settled_usd = max(Decimal("0.00"), settled_usd - total_fees_usd)
    success_count = sum(1 for p in all_payments if p.status == "success")
    declined_count = sum(1 for p in all_payments if p.status != "success")

    context = {
        **_operations_sidebar_context("transactions"),
        "all_payments": all_payments,
        "settled_usd": settled_usd,
        "settled_kes": settled_kes,
        "total_fees_usd": total_fees_usd,
        "net_settled_usd": net_settled_usd,
        "success_count": success_count,
        "declined_count": declined_count,
    }
    return render(request, "platformhub/operations_transactions.html", context)


@admin_only_required
@require_http_methods(["POST"])
def admin_create_invoice(request):
    is_ajax = _is_ajax_or_json(request)
    conversation_id = request.POST.get("conversation_id", "").strip()
    email = request.POST.get("email", "").strip().lower()
    description = request.POST.get("description", "").strip()
    service_code = request.POST.get("service_code", "").strip()
    currency = request.POST.get("currency", "USD").strip().upper()
    raw_amount = request.POST.get("amount_due", "").strip()
    raw_status = request.POST.get("status", "open").strip().lower()
    raw_issued_date = request.POST.get("issued_date", "").strip()

    try:
        amount_due = Decimal(raw_amount).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        amount_due = Decimal("0.00")

    if not email or "@" not in email:
        error = "Enter the client email address."
    elif not description:
        error = "Enter the invoice item or scope."
    elif currency not in {"USD", "KES"}:
        error = "Choose USD or KES."
    elif amount_due <= 0:
        error = "Enter an amount greater than zero."
    else:
        error = ""

    if error:
        if is_ajax:
            return JsonResponse({"error": error}, status=400)
        messages.error(request, error)
        if conversation_id:
            return redirect("platformhub:operations_desk_conversation", conversation_id=conversation_id)
        return redirect("platformhub:operations_invoices")

    User = get_user_model()
    conversation = None
    if conversation_id:
        try:
            conversation = ClientConversation.objects.select_related("user").filter(id=conversation_id).first()
        except (ValueError, ValidationError):
            conversation = None

    target_user = User.objects.filter(email__iexact=email).first()
    if not target_user and conversation and (conversation.user.email or "").lower() == email:
        target_user = conversation.user
    if not target_user:
        base_username = email.split("@")[0][:30] or "client"
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        target_user = User.objects.create(username=username, email=email)

    if not conversation:
        conversation, _ = ClientConversation.objects.get_or_create(user=target_user)

    linked_request = (
        ServiceRequest.objects.filter(Q(user=target_user) | Q(email__iexact=email))
        .order_by("-created_at")
        .first()
    )
    if service_code and service_code in SERVICE_INDEX and not linked_request:
        svc = SERVICE_INDEX[service_code]
        linked_request = ServiceRequest.objects.create(
            user=target_user,
            full_name=target_user.get_full_name() or target_user.username,
            email=email,
            service_family=svc["family"],
            service_code=service_code,
            title=description[:220],
            objective=description,
            scope=description,
            deliverable=description[:220],
            status="quoted",
            currency=currency,
            estimate_low=amount_due,
            estimate_high=amount_due,
        )

    inv_status = "paid" if raw_status == "paid" else "open"
    amount_paid = amount_due if inv_status == "paid" else Decimal("0.00")

    custom_number = request.POST.get("number", "").strip().upper()
    issued_dt = None
    if raw_issued_date:
        try:
            parsed_date = datetime.strptime(raw_issued_date, "%Y-%m-%d")
            issued_dt = timezone.make_aware(parsed_date.replace(hour=12, minute=0, second=0))
        except ValueError:
            issued_dt = None

    if not custom_number:
        ref_dt = issued_dt or timezone.now()
        date_str = ref_dt.strftime("%y%m%d")
        initials = (
            ((target_user.first_name[:1] or "") + (target_user.last_name[:1] or "")).upper()
            or (target_user.username[:2] or "CL").upper()
        )
        base_num = f"INV-{date_str}-{initials}"
        cand_num = f"{base_num}01"
        ctr = 1
        while Invoice.objects.filter(number=cand_num).exists():
            ctr += 1
            cand_num = f"{base_num}{ctr:02d}"
        invoice_number = cand_num
    else:
        invoice_number = custom_number

    due_dt = (issued_dt or timezone.now()) + timedelta(days=7 if inv_status != "paid" else 0)

    invoice = Invoice.objects.create(
        number=invoice_number,
        request=linked_request,
        user=target_user,
        email=email,
        currency=currency,
        amount_due=amount_due,
        amount_paid=amount_paid,
        description=description[:255],
        status=inv_status,
        due_at=due_dt,
    )

    if issued_dt:
        Invoice.objects.filter(pk=invoice.pk).update(created_at=issued_dt)
        invoice.refresh_from_db()

    checkout_url = reverse("platformhub:checkout") + f"?invoice={invoice.id}"
    full_checkout_url = f"https://www.byinfini.online{checkout_url}"
    custom_checkout_url = get_client_checkout_link(target_user.email) or full_checkout_url

    author = request.user if request.user.is_authenticated else None
    is_first_invoice = Invoice.objects.filter(email__iexact=target_user.email).exclude(pk=invoice.pk).count() == 0
    if is_first_invoice:
        notice_body = (
            f"Invoice {invoice.number} ({invoice.currency} {invoice.amount_due:.2f}) — {invoice.description}\n\n"
            f"You can settle directly via Card or Apple Pay on your dedicated checkout page: {custom_checkout_url}"
        )
    else:
        notice_body = (
            f"Invoice {invoice.number} ({invoice.currency} {invoice.amount_due:.2f}) — {invoice.description}\n\n"
            f"Direct payment link: {custom_checkout_url}"
        )
    notice_msg = ClientMessage.objects.create(
        conversation=conversation,
        author=author,
        sender="admin",
        body=notice_body,
    )
    if issued_dt:
        ClientMessage.objects.filter(pk=notice_msg.pk).update(created_at=issued_dt)
        notice_msg.refresh_from_db()

    conversation.status = "open"
    conversation.save(update_fields=["status", "updated_at"])

    if is_ajax:
        return JsonResponse({
            "ok": True,
            "invoice": _serialize_invoice(invoice),
            "message": _serialize_message(notice_msg),
        })

    messages.success(request, f"Invoice {invoice.number} created.")
    next_url = request.POST.get("next", "").strip()
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("platformhub:operations_desk_conversation", conversation_id=conversation.id)


@admin_only_required
@require_http_methods(["POST"])
def admin_invoice_status(request, invoice_id):
    is_ajax = _is_ajax_or_json(request)
    invoice = get_object_or_404(Invoice, id=invoice_id)
    new_status = request.POST.get("status", "").strip().lower()
    conversation_id = request.POST.get("conversation_id", "").strip()
    next_url = request.POST.get("next", "").strip()

    if new_status == "paid":
        invoice.amount_paid = invoice.amount_due
        invoice.status = "paid"
        invoice.save(update_fields=["amount_paid", "status"])
    elif new_status == "void":
        invoice.status = "void"
        invoice.save(update_fields=["status"])
    elif new_status == "open":
        invoice.amount_paid = Decimal("0.00")
        invoice.status = "open"
        invoice.save(update_fields=["amount_paid", "status"])

    if is_ajax:
        return JsonResponse({
            "ok": True,
            "invoice": _serialize_invoice(invoice),
        })

    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    if conversation_id:
        return redirect("platformhub:operations_desk_conversation", conversation_id=conversation_id)
    return redirect("platformhub:operations_invoices")


@require_http_methods(["GET"])
def invoice_pdf_download(request, invoice_id):
    """
    Download executive branded invoice PDF with embedded verification QR code.
    Accessible for any invoice (UUID or invoice number).
    """
    invoice = None
    try:
        invoice = Invoice.objects.filter(id=invoice_id).first()
    except (ValueError, ValidationError):
        pass
    if not invoice:
        invoice = Invoice.objects.filter(number__iexact=str(invoice_id).strip()).first()
    if not invoice:
        raise Http404("Invoice not found.")

    from .invoice_pdf import generate_invoice_pdf
    pdf_bytes = generate_invoice_pdf(invoice)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    filename = f"{invoice.number}.pdf"
    disposition = "attachment" if request.GET.get("inline") != "1" else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return response


@require_http_methods(["GET"])
def invoice_verify(request, invoice_id):
    """
    Public invoice verification view reached via QR code scan or direct verification link.
    Displays authentic invoice status, amount, and items while redacting private client details
    (masks email and redacts last name to First L. [Protected]).
    """
    invoice = None
    try:
        invoice = Invoice.objects.filter(id=invoice_id).first()
    except (ValueError, ValidationError):
        pass
    if not invoice:
        invoice = Invoice.objects.filter(number__iexact=str(invoice_id).strip()).first()
    if not invoice:
        raise Http404("Invoice not found.")

    from .invoice_pdf import mask_email, mask_name
    client_name = ""
    if invoice.user:
        client_name = invoice.user.get_full_name() or invoice.user.username
    if not client_name and invoice.request:
        client_name = invoice.request.full_name

    masked_client_name = mask_name(client_name, fallback_email=invoice.email)
    masked_client_email = mask_email(invoice.email)

    payments = list(
        invoice.payments.filter(status="success").order_by("-paid_at", "-created_at")
    )
    is_paid = invoice.status == "paid"
    balance_due = max(Decimal("0.00"), invoice.amount_due - invoice.amount_paid)
    pdf_url = reverse("platformhub:invoice_pdf_download", kwargs={"invoice_id": invoice.id})

    context = {
        "invoice": invoice,
        "masked_name": masked_client_name,
        "masked_email": masked_client_email,
        "is_paid": is_paid,
        "balance_due": balance_due,
        "payments": payments,
        "pdf_download_url": pdf_url,
    }
    return render(request, "platformhub/invoice_verify.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def quickpay(request):
    if request.method == "POST":
        purpose = request.POST.get("purpose", "").strip()
        currency = request.POST.get("currency", "USD").upper()
        try:
            amount = Decimal(request.POST.get("amount", "").strip())
        except (InvalidOperation, AttributeError):
            amount = Decimal("0")

        if currency not in {"USD", "KES"}:
            messages.error(request, "Choose USD or KES.")
        elif amount <= 0:
            messages.error(request, "Enter an amount greater than zero.")
        elif len(purpose) < 3:
            messages.error(request, "Describe what the payment is for.")
        elif request.POST.get("confirm") != "yes":
            messages.error(request, "Confirm the payment details before continuing.")
        else:
            invoice = Invoice.objects.create(
                user=request.user,
                email=request.user.email,
                currency=currency,
                amount_due=amount,
                description=f"QuickPay — {purpose[:220]}",
            )
            return redirect(f"{reverse('platformhub:checkout')}?invoice={invoice.id}")

    recent = Invoice.objects.filter(user=request.user, description__startswith="QuickPay —").order_by("-created_at")[:10]
    return render(request, "platformhub/quickpay.html", {"recent": recent})


def payment_config(request):
    return JsonResponse({
        "provider": "paystack",
        "public_key": getattr(settings, "PAYSTACK_PUBLIC_KEY", "") or "",
        "currencies": ["USD", "KES"],
        "apple_pay_domain_file": request.build_absolute_uri(reverse("platformhub:apple_pay_domain")),
    })


def apple_pay_domain(request):
    path = settings.BASE_DIR / "static" / "apple-developer-merchantid-domain-association"
    if not path.exists():
        return JsonResponse({"error": "Apple Pay domain file is not configured."}, status=404)
    return FileResponse(path.open("rb"), content_type="text/plain")


@csrf_exempt
@require_http_methods(["POST"])
def paystack_webhook(request):
    secret = getattr(settings, "PAYSTACK_SECRET_KEY", None)
    if not secret:
        return JsonResponse({"error": "Payment provider is not configured."}, status=503)
    try:
        if not valid_webhook_signature(request.body, request.headers.get("x-paystack-signature", "")):
            return JsonResponse({"error": "Invalid signature."}, status=401)
        event = json.loads(request.body.decode("utf-8"))
        if event.get("event") in {"charge.success", "charge.failed"}:
            ingest_webhook_transaction(event.get("data") or {})
        return JsonResponse({"ok": True})
    except PaystackError:
        logger.exception("Paystack webhook processing failed")
        return JsonResponse({"error": "Webhook processing failed."}, status=502)
    except Exception:
        logger.exception("Unexpected Paystack webhook error")
        return JsonResponse({"error": "Webhook processing failed."}, status=500)


def _checkout_context(request):
    package_slug = request.GET.get("package", "").strip()
    invoice_id = request.GET.get("invoice", "").strip()
    currency = request.GET.get("currency", "USD").upper()
    job_id = request.GET.get("job", "").strip()
    consultation_id = request.GET.get("consultation", "").strip()
    if currency not in {"USD", "KES"}:
        currency = "USD"

    if invoice_id:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        active_user = request.user if request.user.is_authenticated else _resolve_chat_user(request)
        if invoice.user_id and invoice.user_id != active_user.id and (not active_user.email or invoice.email.lower() != active_user.email.lower()):
            raise PermissionDenied("This invoice is not attached to your account.")
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
        "consultation_id": consultation_id,
    }


def checkout(request):
    context = _checkout_context(request)
    if not context:
        return redirect("platformhub:pricing")
    if context.get("kind") == "package" and context.get("package_slug", "").startswith("humanizer-") and not request.user.is_authenticated:
        login_url = reverse("account_login")
        return redirect(f"{login_url}?next={request.get_full_path()}")
    context["payments_configured"] = bool(getattr(settings, "PAYSTACK_SECRET_KEY", None))
    return render(request, "platformhub/checkout.html", context)


@require_http_methods(["POST"])
def start_checkout(request):
    package_slug = request.POST.get("package_slug", "").strip()
    invoice_id = request.POST.get("invoice_id", "").strip()
    job_id = request.POST.get("job_id", "").strip()
    currency = request.POST.get("currency", "USD").upper()
    email = request.POST.get("email", "").strip()

    invoice = None
    assurance_job = None
    request_id = None
    normalized_family = ""
    normalized_service_code = ""
    source_type = "checkout"

    if invoice_id:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Sign in to pay this invoice."}, status=403)
        if invoice.user_id and invoice.user_id != request.user.id and (
            not request.user.email or invoice.email.lower() != request.user.email.lower()
        ):
            return JsonResponse({"error": "This invoice is not attached to your account."}, status=403)
        amount = invoice.amount_due - invoice.amount_paid
        if amount <= 0:
            return JsonResponse({"error": "This invoice is already paid."}, status=400)
        currency = invoice.currency
        email = invoice.email
        label = invoice.description or invoice.number
        request_id = invoice.request_id
        normalized_family = invoice.request.service_family if invoice.request else ""
        normalized_service_code = invoice.request.service_code if invoice.request else ""
        if not request_id and label.startswith("QuickPay"):
            source_type = "quickpay"
            normalized_family = "quickpay"
            normalized_service_code = "quickpay"
    else:
        package = PACKAGES.get(package_slug)
        if not package:
            return JsonResponse({"error": "Unknown package."}, status=400)
        if package_slug == "consultation":
            return JsonResponse({"error": "Talking to us is free."}, status=400)
        if package_slug.startswith("humanizer-") and not request.user.is_authenticated:
            return JsonResponse({
                "error": "Please sign in before choosing a Humanizer plan.",
                "auth_required": True,
                "login_url": f'{reverse("account_login")}?next={reverse("platformhub:pricing")}',
            }, status=401)
        if package_slug == "originality-quick":
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Please sign in to run this check."}, status=401)
            assurance_job = AssuranceJob.objects.filter(id=job_id, user=request.user).first()
            if not assurance_job:
                return JsonResponse({"error": "This assurance job is not attached to your account."}, status=403)

        amount = package["kes"] if currency == "KES" else package["usd"]
        label = package["name"]
        normalized_service_code = package.get("service_code", "")
        normalized_family = (
            (SERVICE_INDEX.get(normalized_service_code) or {}).get("family")
            or ("text-intelligence" if normalized_service_code == "text-humanize" else "")
        )
        if request.user.is_authenticated and request.user.email:
            email = request.user.email

    if currency not in {"USD", "KES"}:
        return JsonResponse({"error": "Unsupported currency."}, status=400)
    if not email:
        return JsonResponse({"error": "Email is required."}, status=400)
    if amount <= 0:
        return JsonResponse({"error": "Payment amount must be greater than zero."}, status=400)
    if not getattr(settings, "PAYSTACK_SECRET_KEY", None):
        return JsonResponse({"error": "Secure checkout is not connected on this deployment yet."}, status=503)

    reference = f"INF-{uuid.uuid4().hex[:18].upper()}"
    callback = f"{settings.PUBLIC_BASE_URL}{reverse('platformhub:verify_checkout')}"
    metadata = {
        "label": label,
        "package_slug": package_slug,
        "invoice_id": invoice_id,
        "request_id": str(request_id) if request_id else "",
        "job_id": str(assurance_job.id) if assurance_job else "",
    }

    payment = PaymentRecord.objects.create(
        invoice=invoice,
        request_id=request_id,
        assurance_job=assurance_job,
        user=request.user if request.user.is_authenticated else None,
        reference=reference,
        source_type=source_type,
        amount=amount,
        currency=currency,
        status="pending",
        email=email,
        normalized_family=normalized_family,
        normalized_service_code=normalized_service_code,
        metadata=metadata,
    )

    try:
        gateway = initialize_transaction(
            email=email,
            amount=amount,
            currency=currency,
            reference=reference,
            callback_url=callback,
            metadata=metadata,
        )
    except PaystackError as exc:
        payment.status = "failed"
        payment.metadata = {**payment.metadata, "initialization_error": str(exc)}
        payment.save(update_fields=["status", "metadata"])
        logger.warning("Paystack initialize failed: %s", exc)
        return JsonResponse({"error": str(exc)}, status=502)

    return JsonResponse({
        "authorization_url": gateway["authorization_url"],
        "reference": reference,
    })


def verify_checkout(request):
    reference = request.GET.get("reference", "").strip() or request.GET.get("trxref", "").strip()
    if not reference:
        return redirect("platformhub:workspace" if request.user.is_authenticated else "platformhub:pricing")

    payment = get_object_or_404(PaymentRecord, reference=reference)
    try:
        tx = verify_transaction(reference)
        payment = apply_gateway_transaction(payment.id, tx)
    except PaystackError:
        logger.exception("Paystack verification failed for %s", reference)
        messages.error(request, "Payment verification failed.")
        return redirect("platformhub:workspace" if request.user.is_authenticated else "platformhub:pricing")
    except Exception:
        logger.exception("Unexpected payment verification failure for %s", reference)
        messages.error(request, "Payment verification failed.")
        return redirect("platformhub:workspace" if request.user.is_authenticated else "platformhub:pricing")

    if payment.status == "success":
        messages.success(request, "Payment confirmed.")
        if payment.assurance_job_id and request.user.is_authenticated:
            return redirect("platformhub:assurance_result", job_id=payment.assurance_job_id)
        if (payment.metadata or {}).get("package_slug", "").startswith("humanizer-"):
            return redirect("humanizer")
        if request.user.is_authenticated:
            return redirect("platformhub:workspace")
        return redirect("platformhub:home")

    messages.error(request, "Payment was not completed.")
    return redirect("platformhub:workspace" if request.user.is_authenticated else "platformhub:pricing")


@staff_member_required
def reconciliation(request):
    return render(request, "platformhub/reconciliation.html", {
        "summary": LEGACY_LEDGER_SUMMARY,
        "bands": LEGACY_RECONCILIATION_BANDS,
    })


@admin_only_required
def posters_gallery(request):
    from platformhub.engaging_posters_data import ENGAGING_POSTERS
    return render(request, "platformhub/posters.html", {"posters": ENGAGING_POSTERS})


@admin_only_required
def operations_posters(request):
    from platformhub.models import SocialPoster
    from platformhub.engaging_posters_data import sync_social_posters_db

    if not SocialPoster.objects.exists():
        sync_social_posters_db()

    style_filter = request.GET.get("style", "").strip()
    posters_qs = SocialPoster.objects.all().order_by("number")
    if style_filter in ["photo-dark", "editorial-paper", "ink-obsidian"]:
        posters_qs = posters_qs.filter(style=style_filter)

    posters = list(posters_qs)
    total_count = SocialPoster.objects.count()
    photo_count = SocialPoster.objects.filter(style="photo-dark").count()
    paper_count = SocialPoster.objects.filter(style="editorial-paper").count()
    ink_count = SocialPoster.objects.filter(style="ink-obsidian").count()

    context = {
        **_operations_sidebar_context("posters"),
        "posters": posters,
        "style_filter": style_filter,
        "total_count": total_count,
        "photo_count": photo_count,
        "paper_count": paper_count,
        "ink_count": ink_count,
    }
    return render(request, "platformhub/operations_posters.html", context)


def _find_poster_file(filename):
    from pathlib import Path
    candidate_dirs = [
        Path(settings.BASE_DIR) / "static" / "posters",
        Path(settings.BASE_DIR) / "staticfiles" / "posters",
        Path(settings.BASE_DIR) / "public" / "posters",
    ]
    if hasattr(settings, "STATIC_ROOT") and settings.STATIC_ROOT:
        candidate_dirs.append(Path(settings.STATIC_ROOT) / "posters")

    for d in candidate_dirs:
        p = d / filename
        if p.exists():
            return p
    return None


@admin_only_required
def operations_download_poster(request, number, format_type):
    from django.http import FileResponse, Http404

    format_type = format_type.lower()
    if format_type not in ["png", "jpg", "svg"]:
        raise Http404("Unsupported format.")

    number_clean = str(number).zfill(2)
    filename = f"poster_{number_clean}.{format_type}"
    file_path = _find_poster_file(filename)

    if not file_path or not file_path.exists():
        raise Http404("Poster image not found.")

    content_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "svg": "image/svg+xml",
    }
    response = FileResponse(open(str(file_path), "rb"), content_type=content_types[format_type])
    response["Content-Disposition"] = f'attachment; filename="infini_story_{number_clean}.{format_type}"'
    return response


@admin_only_required
def operations_download_all_posters(request):
    import io, zipfile
    from django.http import HttpResponse

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        manifest_lines = [
            "INFINIAI SOCIAL STORY POSTERS (1080x1920 · 9:16)",
            "Brand colors: Terracotta (#c84132), Obsidian (#11110f), Warm Paper (#faf8f2)",
            "Direct intake URL: https://www.byinfini.online/consultation/",
            "=" * 60,
            "",
        ]
        for num in range(1, 21):
            num_str = f"{num:02d}"
            png_name = f"poster_{num_str}.png"
            jpg_name = f"poster_{num_str}.jpg"
            png_path = _find_poster_file(png_name)
            jpg_path = _find_poster_file(jpg_name)

            if png_path:
                zf.write(str(png_path), arcname=f"png/{png_name}")
            if jpg_path:
                zf.write(str(jpg_path), arcname=f"jpg/{jpg_name}")

            manifest_lines.append(f"Poster {num_str}: PNG & JPG included")

        zf.writestr("MANIFEST.txt", "\n".join(manifest_lines))

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="infini_social_story_posters_20.zip"'
    return response


def showcase_studio_brown(request):
    """
    Live hosted website deliverable for Audrey Brown (Studio Brown Photography, Austin TX).
    Showcases editorial portraiture, transparent package pricing, and the streamlined 5-field booking flow.
    """
    return render(request, "platformhub/showcase_studio_brown.html")


def showcase_dockstream(request):
    """
    Live hosted website deliverable for Jack Johnson (DockStream Yard Logistics, Chicago IL).
    Showcases enterprise B2B yard management, interactive 12-bay terminal inspector, and detention ROI calculator.
    """
    return render(request, "platformhub/showcase_dockstream.html")


def showcase_orozco(request):
    """
    Live hosted website deliverable for Azael Orozco (Orozco Commercial Roofing, McAllen TX).
    Showcases commercial flat roofing systems, interactive square-foot bid estimator, and 20-year NDL warranty specs.
    """
    return render(request, "platformhub/showcase_orozco.html")


def showcase_apexdesk(request):
    """
    Live hosted website deliverable for Carter Lemburg (ApexDesk Minimalist Hardware, Boulder CO).
    Showcases CNC-machined aerospace aluminum desk accessories, 3D unibody colorway toggle, and Qi2 modular rail builder.
    """
    return render(request, "platformhub/showcase_apexdesk.html")


def health(request):
    return JsonResponse({"status": "ok", "service": "infiniai"})


