import hashlib
import hmac
import json
from decimal import Decimal

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import PaymentRecord


class PaystackError(RuntimeError):
    pass


def _secret():
    secret = getattr(settings, "PAYSTACK_SECRET_KEY", None)
    if not secret:
        raise PaystackError("Paystack is not configured.")
    return secret


def initialize_transaction(*, email, amount, currency, reference, callback_url, metadata):
    payload = {
        "email": email,
        "amount": int((Decimal(str(amount)) * 100).quantize(Decimal("1"))),
        "currency": currency,
        "reference": reference,
        "callback_url": callback_url,
        "metadata": metadata,
    }
    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=payload,
        headers={"Authorization": f"Bearer {_secret()}", "Content-Type": "application/json"},
        timeout=20,
    )
    data = response.json()
    if not response.ok or not data.get("status"):
        raise PaystackError(data.get("message") or "Payment initialization failed.")
    return data["data"]


def verify_transaction(reference):
    response = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers={"Authorization": f"Bearer {_secret()}"},
        timeout=20,
    )
    data = response.json()
    if not response.ok or not data.get("status"):
        raise PaystackError(data.get("message") or "Payment verification failed.")
    return data.get("data") or {}


def valid_webhook_signature(raw_body, signature):
    if not signature:
        return False
    digest = hmac.new(_secret().encode(), raw_body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(digest, signature)


def _apply_entitlement(payment):
    package_slug = (payment.metadata or {}).get("package_slug", "")
    if not package_slug or not payment.user_id:
        return
    from accounts.models import Profile
    profile, _ = Profile.objects.get_or_create(user_id=payment.user_id)
    if package_slug == "humanizer-individual":
        profile.account_type = "STANDARD"
        profile.is_paid = True
        profile.word_quota = max(profile.word_quota, 100000)
    elif package_slug == "humanizer-pro":
        profile.account_type = "PRO"
        profile.is_paid = True
        profile.word_quota = max(profile.word_quota, 250000)
    elif package_slug == "humanizer-team":
        profile.account_type = "ENTERPRISE"
        profile.is_paid = True
        profile.word_quota = max(profile.word_quota, 600000)
        profile.max_concurrent_devices = max(profile.max_concurrent_devices, 5)
    else:
        return
    profile.save()


@transaction.atomic
def apply_gateway_transaction(payment_id, tx):
    payment = (
        PaymentRecord.objects.select_for_update()
        .select_related("invoice", "request", "assurance_job", "consultation", "user")
        .get(id=payment_id)
    )
    gateway_status = str(tx.get("status") or "").lower()
    was_success = payment.status == "success"

    gateway = {
        "id": tx.get("id"),
        "channel": tx.get("channel"),
        "gateway_response": tx.get("gateway_response"),
        "fees": tx.get("fees"),
        "paid_at": tx.get("paid_at"),
    }
    payment.metadata = {**(payment.metadata or {}), "gateway": gateway}

    if gateway_status == "success":
        paid_amount = Decimal(str(tx.get("amount") or 0)) / Decimal("100")
        tx_currency = str(tx.get("currency") or payment.currency).upper()
        if tx_currency != payment.currency.upper():
            raise PaystackError("Payment currency does not match the checkout.")
        if not was_success:
            payment.amount = paid_amount
            payment.status = "success"
            payment.paid_at = timezone.now()
        payment.save(update_fields=["amount", "status", "paid_at", "metadata"])

        if not was_success and payment.invoice_id:
            invoice = payment.invoice
            invoice.amount_paid = min(invoice.amount_due, invoice.amount_paid + paid_amount)
            invoice.save()
            if invoice.status == "paid" and invoice.request_id:
                project = invoice.request
                project.status = "active"
                project.save(update_fields=["status", "updated_at"])

        if not was_success and payment.assurance_job_id:
            job = payment.assurance_job
            job.status = "queued"
            job.payment_reference = payment.reference
            job.save(update_fields=["status", "payment_reference", "updated_at"])

        if not was_success:
            _apply_entitlement(payment)
    elif not was_success:
        if gateway_status in {"failed", "abandoned", "reversed"}:
            payment.status = "abandoned" if gateway_status == "abandoned" else "failed"
            payment.save(update_fields=["status", "metadata"])
        else:
            payment.save(update_fields=["metadata"])

    return payment


def ingest_webhook_transaction(tx):
    reference = str(tx.get("reference") or "").strip()
    if not reference:
        return None
    customer = tx.get("customer") or {}
    email = customer.get("email") or (tx.get("metadata") or {}).get("email") or ""
    amount = Decimal(str(tx.get("amount") or 0)) / Decimal("100")
    currency = str(tx.get("currency") or "USD").upper()
    payment, _ = PaymentRecord.objects.get_or_create(
        reference=reference,
        defaults={
            "provider": "paystack",
            "source_type": "paystack_webhook",
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "email": email,
            "metadata": {"gateway_event": True},
        },
    )
    return apply_gateway_transaction(payment.id, tx)
