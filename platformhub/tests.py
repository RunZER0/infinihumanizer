from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .catalog import commercial_terms, estimate_request
from .legacy_mapping import legacy_amount_band, normalize_legacy_transaction
from .models import Deliverable, ServiceRequest


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
        for name in ["platformhub:home", "platformhub:services", "platformhub:pricing", "platformhub:start", "platformhub:consultation"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

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
