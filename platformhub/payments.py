import hashlib
import hmac
import json
from decimal import Decimal

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .catalog import PACKAGES
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
    package = PACKAGES.get(package_slug) or {}
    credits = int(package.get("word_credits") or 0)
    if not credits or not payment.user_id:
        return

    from accounts.models import Profile

    profile, _ = Profile.objects.get_or_create(user_id=payment.user_id)
    profile.account_type = package.get("account_type") or profile.account_type
    profile.is_paid = True
    profile.word_quota = max(0, int(profile.word_quota or 0)) + credits
    profile.max_concurrent_devices = max(
        int(profile.max_concurrent_devices or 1),
        int(package.get("max_devices") or 1),
    )
    profile.save(
        update_fields=[
            "account_type",
            "is_paid",
            "word_quota",
            "max_concurrent_devices",
        ]
    )

    payment.metadata = {
        **(payment.metadata or {}),
        "fulfillment": {
            "type": "humanizer_words",
            "package_slug": package_slug,
            "word_credits_added": credits,
            "word_quota_after": profile.word_quota,
            "account_type": profile.account_type,
            "max_devices": profile.max_concurrent_devices,
        },
    }
    payment.save(update_fields=["metadata"])


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
        tx_reference = str(tx.get("reference") or "").strip()
        if tx_reference and tx_reference != payment.reference:
            raise PaystackError("Payment reference does not match the checkout.")

        paid_amount = (Decimal(str(tx.get("amount") or 0)) / Decimal("100")).quantize(Decimal("0.01"))
        expected_amount = Decimal(payment.amount).quantize(Decimal("0.01"))
        tx_currency = str(tx.get("currency") or payment.currency).upper()

        if tx_currency != payment.currency.upper():
            raise PaystackError("Payment currency does not match the checkout.")
        if paid_amount != expected_amount:
            raise PaystackError("Payment amount does not match the checkout.")

        if not was_success:
            payment.status = "success"
            payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at", "metadata"])

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
