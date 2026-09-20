import csv
import re
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from platformhub.legacy_mapping import legacy_amount_band, normalize_legacy_transaction
from platformhub.models import PaymentRecord


def parse_legacy_date(value):
    if not value:
        return None
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", value)
    for fmt in ("%b %d, %Y %I:%M:%S %p", "%B %d, %Y %I:%M:%S %p"):
        try:
            from datetime import datetime
            dt = datetime.strptime(cleaned, fmt)
            return timezone.make_aware(dt)
        except ValueError:
            continue
    return None


class Command(BaseCommand):
    help = "Import historical transaction CSV while preserving the original memo and adding a normalized InfiniAI service classification."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")

    def handle(self, *args, **options):
        created = 0
        updated = 0
        skipped = 0
        with open(options["csv_path"], "r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                reference = (row.get("Reference") or "").strip()
                if not reference:
                    skipped += 1
                    continue
                status = (row.get("Status") or "").strip().lower()
                if status not in {"success", "successful", "failed", "abandoned"}:
                    status = "pending"
                try:
                    amount = Decimal(str(row.get("Amount Paid") or "0"))
                except InvalidOperation:
                    amount = Decimal("0")

                family, service_code = normalize_legacy_transaction(row)
                defaults = {
                    "provider": "paystack",
                    "source_type": (row.get("Payment Type") or row.get("Source") or "legacy").strip(),
                    "amount": amount,
                    "currency": (row.get("Currency") or "KES").strip().upper(),
                    "status": "success" if status in {"success", "successful"} else status,
                    "email": (row.get("Customer (email)") or "").strip(),
                    "original_description": (row.get("Description") or "").strip(),
                    "normalized_family": family,
                    "normalized_service_code": service_code,
                    "legacy": True,
                    "paid_at": parse_legacy_date(row.get("Transaction Date")),
                    "metadata": {
                        "gateway_response": row.get("Gateway Response"),
                        "channel": row.get("Channel"),
                        "payment_type": row.get("Payment Type"),
                        "plan": row.get("Plan"),
                        "invoice": row.get("Invoice"),
                        "original_client_name": row.get("Client Name"),
                        "commercial_band": legacy_amount_band(row),
                    },
                }
                _, was_created = PaymentRecord.objects.update_or_create(reference=reference, defaults=defaults)
                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f"Imported: {created} new, {updated} updated, {skipped} skipped."))
