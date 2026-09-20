import json
import os
from datetime import timezone as dt_timezone
from decimal import Decimal

import psycopg2
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from platformhub.models import PaymentRecord


STATUS_MAP = {
    "paid": "success",
    "success": "success",
    "successful": "success",
    "completed": "success",
    "complete": "success",
    "failed": "failed",
    "failure": "failed",
    "abandoned": "abandoned",
    "cancelled": "abandoned",
    "canceled": "abandoned",
    "refunded": "refunded",
    "refund": "refunded",
}


def normalize_status(value):
    return STATUS_MAP.get(str(value or "").strip().lower(), "pending")


def normalize_currency(value, fallback="USD"):
    value = str(value or fallback).strip().upper()
    return value[:3] if value else fallback


def as_decimal(value):
    try:
        return Decimal(str(value or 0))
    except Exception:
        return Decimal("0")


def dt(value):
    if not value:
        return None
    if hasattr(value, "tzinfo"):
        if timezone.is_naive(value):
            return timezone.make_aware(value, dt_timezone.utc)
        return value
    parsed = parse_datetime(str(value))
    if parsed and timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, dt_timezone.utc)
    return parsed


class Command(BaseCommand):
    help = "Import HomeworkPal payment records into the InfiniAI payment ledger."

    def add_arguments(self, parser):
        parser.add_argument("--if-configured", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        source_url = os.getenv("HOMEWORKPAL_DATABASE_URL", "").strip()
        if not source_url:
            if options["if_configured"]:
                self.stdout.write("HomeworkPal payment import skipped: HOMEWORKPAL_DATABASE_URL is not configured.")
                return
            raise CommandError("HOMEWORKPAL_DATABASE_URL is required.")

        conn = psycopg2.connect(source_url, sslmode="require")
        conn.autocommit = True
        self.user_model = get_user_model()
        self.dry_run = options["dry_run"]
        self.created = 0
        self.updated = 0
        self.skipped = 0

        try:
            with conn.cursor() as cursor:
                tables = self._tables(cursor)
                if "payment_transactions" in tables:
                    self._payment_transactions(cursor)
                if "quickpay_invoices" in tables:
                    self._quickpay(cursor)
                if "writenix_reports" in tables:
                    self._writenix(cursor, tables)
                if "slot_purchases" in tables:
                    self._slots(cursor, tables)
                if "client_orders" in tables:
                    self._orders(cursor, tables)
                if "payments" in tables:
                    self._writer_payments(cursor, tables)
                if "payouts" in tables:
                    self._payouts(cursor, tables)
        finally:
            conn.close()

        self.stdout.write(self.style.SUCCESS(
            f"HomeworkPal ledger import complete: {self.created} created, {self.updated} enriched, {self.skipped} skipped."
        ))

    def _tables(self, cursor):
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        return {row[0] for row in cursor.fetchall()}

    def _rows(self, cursor, sql):
        cursor.execute(sql)
        names = [desc[0] for desc in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

    def _user_for_email(self, email):
        if not email:
            return None
        return self.user_model.objects.filter(email__iexact=email).first()

    def _upsert(self, *, source_table, source_id, gateway_reference=None, email="", amount=0,
                currency="USD", status="pending", description="", paid_at=None, created_at=None,
                family="", service_code="", metadata=None, direction="inflow"):
        gateway_reference = str(gateway_reference or "").strip()
        synthetic = f"HP-{source_table.upper()[:16]}-{source_id}"
        reference = gateway_reference or synthetic
        metadata = dict(metadata or {})
        source_marker = {"table": source_table, "id": str(source_id)}
        metadata["homeworkpal_source"] = source_marker
        metadata["direction"] = direction
        if gateway_reference:
            metadata["original_gateway_reference"] = gateway_reference

        existing = PaymentRecord.objects.filter(reference=reference).first()
        if existing:
            merged = dict(existing.metadata or {})
            sources = merged.get("homeworkpal_sources") or []
            if source_marker not in sources:
                sources.append(source_marker)
            merged["homeworkpal_sources"] = sources
            for key, value in metadata.items():
                if key not in {"homeworkpal_source"} and value not in (None, "", [], {}):
                    merged.setdefault(key, value)
            changed = []
            if existing.legacy and description and not existing.original_description:
                existing.original_description = description
                changed.append("original_description")
            if not existing.user_id:
                user = self._user_for_email(email)
                if user:
                    existing.user = user
                    changed.append("user")
            existing.metadata = merged
            changed.append("metadata")
            if not self.dry_run:
                existing.save(update_fields=changed)
            self.updated += 1
            return

        if self.dry_run:
            self.created += 1
            return

        user = self._user_for_email(email)
        record = PaymentRecord.objects.create(
            provider="paystack" if gateway_reference else "homeworkpal",
            reference=reference,
            source_type=f"homeworkpal_{source_table}",
            amount=as_decimal(amount),
            currency=normalize_currency(currency),
            status=normalize_status(status),
            email=email or "",
            user=user,
            original_description=description or "",
            normalized_family=family,
            normalized_service_code=service_code,
            legacy=True,
            metadata=metadata,
            paid_at=dt(paid_at),
        )
        if created_at:
            parsed = dt(created_at)
            if parsed:
                PaymentRecord.objects.filter(pk=record.pk).update(created_at=parsed)
        self.created += 1

    def _payment_transactions(self, cursor):
        rows = self._rows(cursor, """
            SELECT id, reference, email, amount, currency, status, channel,
                   gateway_response, metadata, paid_at, verified_at, created_at
            FROM payment_transactions ORDER BY id
        """)
        for row in rows:
            self._upsert(
                source_table="payment_transactions",
                source_id=row["id"],
                gateway_reference=row["reference"],
                email=row["email"],
                amount=row["amount"],
                currency=row["currency"],
                status=row["status"],
                description=((row.get("metadata") or {}).get("description") if isinstance(row.get("metadata"), dict) else "") or "HomeworkPal payment",
                paid_at=row["paid_at"],
                created_at=row["created_at"],
                family="legacy-payment",
                service_code="legacy-paystack",
                metadata={
                    "channel": row.get("channel"),
                    "gateway_response": row.get("gateway_response"),
                    "homeworkpal_metadata": row.get("metadata") or {},
                    "verified_at": str(row.get("verified_at") or ""),
                },
            )

    def _quickpay(self, cursor):
        rows = self._rows(cursor, """
            SELECT id, invoice_number, client_code, client_name, client_email,
                   work_paid_for, amount, currency, payment_status,
                   paystack_reference, paid_at, created_at
            FROM quickpay_invoices ORDER BY id
        """)
        for row in rows:
            self._upsert(
                source_table="quickpay_invoices",
                source_id=row["id"],
                gateway_reference=row.get("paystack_reference"),
                email=row.get("client_email") or "",
                amount=row["amount"],
                currency=row["currency"],
                status=row["payment_status"],
                description=row.get("work_paid_for") or "QuickPay",
                paid_at=row.get("paid_at"),
                created_at=row.get("created_at"),
                family="quickpay",
                service_code="quickpay",
                metadata={
                    "invoice_number": row.get("invoice_number"),
                    "client_code": row.get("client_code"),
                    "client_name": row.get("client_name"),
                },
            )

    def _writenix(self, cursor, tables):
        email_join = "LEFT JOIN client_members cm ON cm.id = wr.member_id" if "client_members" in tables else ""
        email_col = "cm.email AS email" if "client_members" in tables else "NULL::text AS email"
        rows = self._rows(cursor, f"""
            SELECT wr.id, wr.original_filename, wr.status, wr.amount_charged, wr.currency,
                   wr.paystack_reference, wr.used_wallet_credit, wr.created_at, wr.completed_at,
                   {email_col}
            FROM writenix_reports wr
            {email_join}
            ORDER BY wr.id
        """)
        for row in rows:
            if row.get("used_wallet_credit") and not row.get("paystack_reference"):
                self.skipped += 1
                continue
            self._upsert(
                source_table="writenix_reports",
                source_id=row["id"],
                gateway_reference=row.get("paystack_reference"),
                email=row.get("email") or "",
                amount=row.get("amount_charged"),
                currency=row.get("currency"),
                status="success" if row.get("paystack_reference") else row.get("status"),
                description=f"Content assurance — {row.get('original_filename') or 'report'}",
                paid_at=row.get("completed_at"),
                created_at=row.get("created_at"),
                family="assurance",
                service_code="assurance-originality",
                metadata={"used_wallet_credit": bool(row.get("used_wallet_credit"))},
            )

    def _slots(self, cursor, tables):
        email_join = "LEFT JOIN client_members cm ON cm.id = sp.member_id" if "client_members" in tables else ""
        email_col = "cm.email AS email" if "client_members" in tables else "NULL::text AS email"
        rows = self._rows(cursor, f"""
            SELECT sp.id, sp.slot_count, sp.amount, sp.currency, sp.paystack_reference,
                   sp.created_at, {email_col}
            FROM slot_purchases sp
            {email_join}
            ORDER BY sp.id
        """)
        for row in rows:
            self._upsert(
                source_table="slot_purchases",
                source_id=row["id"],
                gateway_reference=row.get("paystack_reference"),
                email=row.get("email") or "",
                amount=row.get("amount"),
                currency=row.get("currency"),
                status="success",
                description=f"Report slots — {row.get('slot_count') or 0}",
                paid_at=row.get("created_at"),
                created_at=row.get("created_at"),
                family="assurance",
                service_code="assurance-slots",
                metadata={"slot_count": row.get("slot_count")},
            )

    def _orders(self, cursor, tables):
        email_join = "LEFT JOIN client_members cm ON cm.id = co.member_id" if "client_members" in tables else ""
        email_col = "COALESCE(cm.email, co.guest_email) AS email" if "client_members" in tables else "co.guest_email AS email"
        rows = self._rows(cursor, f"""
            SELECT co.id, co.order_number, co.final_price, co.payment_status, co.payment_method,
                   co.payment_reference, co.paid_at, co.created_at, co.package_type,
                   {email_col}
            FROM client_orders co
            {email_join}
            ORDER BY co.id
        """)
        for row in rows:
            self._upsert(
                source_table="client_orders",
                source_id=row["id"],
                gateway_reference=row.get("payment_reference"),
                email=row.get("email") or "",
                amount=row.get("final_price"),
                currency="USD",
                status=row.get("payment_status"),
                description=f"HomeworkPal order {row.get('order_number') or row['id']}",
                paid_at=row.get("paid_at"),
                created_at=row.get("created_at"),
                family="legacy-production",
                service_code="legacy-managed-production",
                metadata={
                    "order_number": row.get("order_number"),
                    "package_type": row.get("package_type"),
                    "payment_method": row.get("payment_method"),
                    "currency_inferred": True,
                },
            )

    def _writer_payments(self, cursor, tables):
        email_join = "LEFT JOIN users u ON u.id = p.writer_id" if "users" in tables else ""
        email_col = "u.email AS email" if "users" in tables else "NULL::text AS email"
        rows = self._rows(cursor, f"""
            SELECT p.id, p.amount, p.payment_date, p.method, p.reference, p.notes,
                   p.created_at, {email_col}
            FROM payments p
            {email_join}
            ORDER BY p.id
        """)
        for row in rows:
            self._upsert(
                source_table="writer_payments",
                source_id=row["id"],
                gateway_reference=row.get("reference"),
                email=row.get("email") or "",
                amount=row.get("amount"),
                currency="USD",
                status="success",
                description=row.get("notes") or "Writer payment",
                paid_at=row.get("payment_date"),
                created_at=row.get("created_at"),
                family="legacy-payout",
                service_code="legacy-writer-payment",
                metadata={"method": row.get("method"), "currency_inferred": True},
                direction="outflow",
            )

    def _payouts(self, cursor, tables):
        email_join = "LEFT JOIN users u ON u.id = p.user_id" if "users" in tables else ""
        email_col = "u.email AS email" if "users" in tables else "NULL::text AS email"
        rows = self._rows(cursor, f"""
            SELECT p.id, p.reference, p.transfer_code, p.amount, p.currency, p.status,
                   p.reason, p.created_at, p.completed_at, {email_col}
            FROM payouts p
            {email_join}
            ORDER BY p.id
        """)
        for row in rows:
            self._upsert(
                source_table="payouts",
                source_id=row["id"],
                gateway_reference=row.get("reference") or row.get("transfer_code"),
                email=row.get("email") or "",
                amount=row.get("amount"),
                currency=row.get("currency"),
                status=row.get("status"),
                description=row.get("reason") or "Writer payout",
                paid_at=row.get("completed_at"),
                created_at=row.get("created_at"),
                family="legacy-payout",
                service_code="legacy-paystack-payout",
                metadata={"transfer_code": row.get("transfer_code")},
                direction="outflow",
            )
