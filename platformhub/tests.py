from unittest.mock import patch
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .catalog import SERVICE_INDEX, commercial_terms, estimate_request
from .legacy_mapping import legacy_amount_band, normalize_legacy_transaction
from .knowledge import ARTICLES
from .models import Consultation, Deliverable, ServiceRequest


class CommercialArchitectureTests(TestCase):
    def test_scope_estimate_scales_with_research_and_priority(self):
        base = estimate_request("studio-report", "none", "flexible")
        deep = estimate_request("studio-report", "deep", "priority")
        self.assertGreater(deep[1], base[1])

    def test_payment_structure_is_proportional(self):
        self.assertEqual(commercial_terms(Decimal("350"), "studio-review")["percent"], Decimal("100"))
        self.assertEqual(commercial_terms(Decimal("2000"), "studio-report")["percent"], Decimal("50"))
        self.assertEqual(commercial_terms(Decimal("10000"), "systems-finetune")["percent"], Decimal("30"))
        self.assertEqual(commercial_terms(Decimal("10000"), "studio-retainer")["percent"], Decimal("100"))

    def test_ambiguous_legacy_quick_pay_is_not_invented(self):
        family, code = normalize_legacy_transaction({
            "Payment Type": "quick_pay",
            "Description": "",
            "Reference": "QP-UNKNOWN",
        })
        self.assertEqual((family, code), ("unclassified", "legacy-unclassified"))

    def test_legacy_amount_band_does_not_assign_service(self):
        self.assertEqual(
            legacy_amount_band({"Amount Paid": "500", "Currency": "USD"}),
            "legacy_project_payment",
        )


class PublicJourneyTests(TestCase):
    def test_public_pages_render(self):
        for name in ["platformhub:home", "platformhub:about", "platformhub:privacy", "platformhub:terms", "platformhub:disclaimer", "platformhub:notes", "platformhub:services", "platformhub:pricing", "platformhub:start", "platformhub:consultation"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_every_service_request_page_renders(self):
        for code in SERVICE_INDEX:
            response = self.client.get(reverse("platformhub:request_service_code", kwargs={"service_code": code}))
            self.assertEqual(response.status_code, 200, code)

    def test_knowledge_archive_has_ten_monthly_articles(self):
        self.assertEqual(len(ARTICLES), 10)
        months = [(article["date"].year, article["date"].month) for article in ARTICLES]
        self.assertEqual(len(months), len(set(months)))
        for article in ARTICLES:
            response = self.client.get(reverse("platformhub:note_detail", kwargs={"slug": article["slug"]}))
            self.assertEqual(response.status_code, 200, article["slug"])

    def test_talking_to_us_does_not_create_a_payment(self):
        response = self.client.post(reverse("platformhub:consultation"), {
            "full_name": "Potential client",
            "email": "client@example.com",
            "topic": "We need help deciding how to structure product language.",
        })
        self.assertEqual(response.status_code, 302)
        item = Consultation.objects.get(email="client@example.com")
        self.assertEqual(item.payments.count(), 0)

    def test_brief_creates_request_not_invoice(self):
        response = self.client.post(reverse("platformhub:request_service"), {
            "service_code": "studio-report",
            "full_name": "Test Buyer",
            "email": "buyer@example.com",
            "title": "Market decision brief",
            "objective": "Decide whether to enter a new market.",
            "scope": "Internal notes exist; external research is required.",
            "deliverable": "Board-ready report",
            "research_depth": "standard",
            "turnaround": "standard",
        })
        self.assertEqual(response.status_code, 302)
        item = ServiceRequest.objects.get(email="buyer@example.com")
        self.assertEqual(item.invoices.count(), 0)
        self.assertGreater(item.estimate_high, item.estimate_low)

    def test_client_can_request_revision_and_approve(self):
        user = User.objects.create_user(username="buyer", email="buyer@example.com", password="pw-strong-123")
        item = ServiceRequest.objects.create(
            user=user,
            full_name="Buyer",
            email=user.email,
            service_family="studio",
            service_code="studio-report",
            title="Report",
            objective="Decision support",
            scope="Research and production",
            deliverable="Final report",
        )
        deliverable = Deliverable.objects.create(request=item, title="Report v1", status="review")
        self.client.force_login(user)
        revision = self.client.post(reverse("platformhub:project_detail", kwargs={"request_id": item.id}), {
            "deliverable_id": deliverable.id,
            "action": "revision",
            "message": "Clarify the market-size assumptions.",
        })
        self.assertEqual(revision.status_code, 302)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, "in_progress")
        deliverable.status = "review"
        deliverable.save()
        approval = self.client.post(reverse("platformhub:project_detail", kwargs={"request_id": item.id}), {
            "deliverable_id": deliverable.id,
            "action": "approve",
            "message": "",
        })
        self.assertEqual(approval.status_code, 302)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, "approved")


    def test_oauth_homepage_has_privacy_link(self):
        response = self.client.get(reverse("platformhub:about"))
        self.assertContains(response, reverse("platformhub:privacy"))
        self.assertContains(response, "Google sign-in")


class QuickPayTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="paying-user",
            email="payer@example.com",
            password="strong-password-123",
        )
        self.client.force_login(self.user)

    def test_quickpay_requires_account(self):
        self.client.logout()
        response = self.client.get(reverse("platformhub:quickpay"))
        self.assertEqual(response.status_code, 302)

    def test_quickpay_creates_account_invoice(self):
        response = self.client.post(reverse("platformhub:quickpay"), {
            "purpose": "Website copy revision",
            "currency": "USD",
            "amount": "75.00",
            "confirm": "yes",
        })
        self.assertEqual(response.status_code, 302)
        invoice = self.user.invoice_set.get()
        self.assertEqual(invoice.email, self.user.email)
        self.assertEqual(invoice.amount_due, Decimal("75.00"))
        self.assertTrue(invoice.description.startswith("QuickPay"))

    def test_workspace_shows_email_matched_legacy_payment(self):
        from .models import PaymentRecord
        PaymentRecord.objects.create(
            reference="HP-LEGACY-1",
            amount=Decimal("50"),
            currency="USD",
            status="success",
            email=self.user.email,
            legacy=True,
            original_description="Legacy payment",
        )
        response = self.client.get(reverse("platformhub:workspace"))
        self.assertContains(response, "HP-LEGACY-1")
        self.assertContains(response, "Legacy payment")

    @patch("platformhub.views.initialize_transaction")
    def test_quickpay_checkout_creates_payment_record(self, initialize):
        initialize.return_value = {
            "authorization_url": "https://checkout.paystack.test/example",
            "reference": "INF-TEST",
        }
        invoice = self.user.invoice_set.create(
            email=self.user.email,
            currency="USD",
            amount_due=Decimal("40"),
            description="QuickPay — Copy edit",
        )
        with self.settings(PAYSTACK_SECRET_KEY="test-secret"):
            response = self.client.post(reverse("platformhub:start_checkout"), {
                "invoice_id": str(invoice.id),
                "email": self.user.email,
                "currency": "USD",
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["authorization_url"], "https://checkout.paystack.test/example")
        payment = invoice.payments.get()
        self.assertEqual(payment.source_type, "quickpay")
        self.assertEqual(payment.normalized_service_code, "quickpay")
