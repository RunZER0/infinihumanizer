from unittest.mock import patch
from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .catalog import SERVICE_INDEX, commercial_terms, estimate_request
from .legacy_mapping import legacy_amount_band, normalize_legacy_transaction
from .knowledge import ARTICLES
from .models import AssuranceJob, Consultation, Deliverable, Invoice, PaymentRecord, ServiceRequest
from accounts.verification import SESSION_VERIFIED_EMAIL
from .payments import PaystackError, apply_gateway_transaction


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

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        SUPPORT_EMAIL="valdaceai@gmail.com",
        DEFAULT_FROM_EMAIL="InfiniAI <valdaceai@gmail.com>",
    )
    def test_talking_to_us_requires_verified_email_then_persists_and_notifies(self):
        session = self.client.session
        session["infini_consult_name"] = "Potential client"
        session["infini_consult_email"] = "client@example.com"
        session[SESSION_VERIFIED_EMAIL] = "client@example.com"
        session.save()

        response = self.client.post(reverse("platformhub:consultation"), {
            "action": "submit_note",
            "topic": "We need help deciding how to structure product language.",
        })
        self.assertEqual(response.status_code, 302)
        item = Consultation.objects.get(email="client@example.com")
        self.assertEqual(item.payments.count(), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["valdaceai@gmail.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["client@example.com"])

    @patch("platformhub.views.issue_email_code")
    def test_first_contact_progresses_from_name_to_email_verification(self, issue_code):
        issue_code.return_value = (object(), True)
        first = self.client.post(reverse("platformhub:consultation"), {
            "action": "set_name",
            "full_name": "Potential client",
        })
        self.assertEqual(first.status_code, 302)

        second = self.client.post(reverse("platformhub:consultation"), {
            "action": "set_email",
            "email": "client@example.com",
        })
        self.assertEqual(second.status_code, 302)
        issue_code.assert_called_once_with("client@example.com", "Potential client")

        page = self.client.get(reverse("platformhub:consultation"))
        self.assertContains(page, "Check your inbox.")

    def test_first_contact_rejects_disposable_email(self):
        session = self.client.session
        session["infini_consult_name"] = "Potential client"
        session.save()

        response = self.client.post(reverse("platformhub:consultation"), {
            "action": "set_email",
            "email": "someone@mailinator.com",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Consultation.objects.filter(email="someone@mailinator.com").exists())
        self.assertContains(response, "Use a permanent email address.")

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


class PaymentCompletionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="payments-user",
            email="payments@example.com",
            password="strong-password-123",
        )
        self.client.force_login(self.user)

    @patch("platformhub.views.initialize_transaction")
    def test_invoice_checkout_uses_public_callback(self, initialize):
        initialize.return_value = {"authorization_url": "https://checkout.paystack.test/tx"}
        invoice = Invoice.objects.create(
            user=self.user,
            email=self.user.email,
            currency="USD",
            amount_due=Decimal("40.00"),
            description="QuickPay — Copy edit",
        )
        with self.settings(PAYSTACK_SECRET_KEY="test-secret", PUBLIC_BASE_URL="https://byinfini.online"):
            response = self.client.post(reverse("platformhub:start_checkout"), {
                "invoice_id": str(invoice.id),
                "email": self.user.email,
                "currency": "USD",
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            initialize.call_args.kwargs["callback_url"],
            "https://byinfini.online" + reverse("platformhub:verify_checkout"),
        )
        payment = invoice.payments.get()
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.source_type, "quickpay")

    @patch("platformhub.views.verify_transaction")
    def test_invoice_success_closes_transaction_and_invoice(self, verify):
        invoice = Invoice.objects.create(
            user=self.user,
            email=self.user.email,
            currency="USD",
            amount_due=Decimal("40.00"),
            description="QuickPay — Copy edit",
        )
        payment = PaymentRecord.objects.create(
            invoice=invoice,
            user=self.user,
            reference="INF-INVOICE-SUCCESS",
            source_type="quickpay",
            amount=Decimal("40.00"),
            currency="USD",
            status="pending",
            email=self.user.email,
        )
        verify.return_value = {
            "reference": payment.reference,
            "status": "success",
            "amount": 4000,
            "currency": "USD",
            "channel": "card",
        }
        response = self.client.get(reverse("platformhub:verify_checkout"), {"reference": payment.reference})
        self.assertRedirects(response, reverse("platformhub:workspace"), fetch_redirect_response=False)
        payment.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(payment.status, "success")
        self.assertEqual(invoice.status, "paid")
        self.assertEqual(invoice.amount_paid, Decimal("40.00"))

    @patch("platformhub.views.initialize_transaction")
    @patch("platformhub.views.verify_transaction")
    def test_humanizer_package_fulfills_entitlement_and_returns_to_tool(self, verify, initialize):
        initialize.return_value = {"authorization_url": "https://checkout.paystack.test/humanizer"}
        with self.settings(PAYSTACK_SECRET_KEY="test-secret", PUBLIC_BASE_URL="https://byinfini.online"):
            start = self.client.post(reverse("platformhub:start_checkout"), {
                "package_slug": "humanizer-pro",
                "currency": "USD",
                "email": self.user.email,
            })
        self.assertEqual(start.status_code, 200)
        reference = start.json()["reference"]
        verify.return_value = {
            "reference": reference,
            "status": "success",
            "amount": 2500,
            "currency": "USD",
            "channel": "card",
        }
        done = self.client.get(reverse("platformhub:verify_checkout"), {"reference": reference})
        self.assertRedirects(done, reverse("humanizer"), fetch_redirect_response=False)
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.is_paid)
        self.assertGreaterEqual(self.user.profile.word_quota, 250000)

    @patch("platformhub.views.initialize_transaction")
    @patch("platformhub.views.verify_transaction")
    def test_assurance_payment_queues_job_and_returns_to_report(self, verify, initialize):
        job = AssuranceJob.objects.create(
            user=self.user,
            title="Draft review",
            content="This is enough source content for the assurance job to exist in the test.",
        )
        initialize.return_value = {"authorization_url": "https://checkout.paystack.test/assurance"}
        with self.settings(PAYSTACK_SECRET_KEY="test-secret", PUBLIC_BASE_URL="https://byinfini.online"):
            start = self.client.post(reverse("platformhub:start_checkout"), {
                "package_slug": "originality-quick",
                "job_id": str(job.id),
                "currency": "USD",
                "email": self.user.email,
            })
        self.assertEqual(start.status_code, 200)
        reference = start.json()["reference"]
        verify.return_value = {
            "reference": reference,
            "status": "success",
            "amount": 200,
            "currency": "USD",
            "channel": "card",
        }
        done = self.client.get(reverse("platformhub:verify_checkout"), {"reference": reference})
        self.assertRedirects(
            done,
            reverse("platformhub:assurance_result", kwargs={"job_id": job.id}),
            fetch_redirect_response=False,
        )
        job.refresh_from_db()
        self.assertEqual(job.status, "queued")
        self.assertEqual(job.payment_reference, reference)

    def test_gateway_amount_mismatch_never_fulfills_payment(self):
        invoice = Invoice.objects.create(
            user=self.user,
            email=self.user.email,
            currency="USD",
            amount_due=Decimal("40.00"),
            description="Invoice",
        )
        payment = PaymentRecord.objects.create(
            invoice=invoice,
            user=self.user,
            reference="INF-AMOUNT-CHECK",
            amount=Decimal("40.00"),
            currency="USD",
            status="pending",
            email=self.user.email,
        )
        with self.assertRaises(PaystackError):
            apply_gateway_transaction(payment.id, {
                "reference": payment.reference,
                "status": "success",
                "amount": 100,
                "currency": "USD",
            })
        payment.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(payment.status, "pending")
        self.assertEqual(invoice.amount_paid, Decimal("0.00"))



class WorkspaceChatTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="chat-user",
            email="chat@example.com",
            password="strong-password-123",
        )
        self.client.force_login(self.user)

    def test_client_can_send_workspace_message(self):
        from humanizer.models import ClientMessage

        response = self.client.post(reverse("platformhub:client_chat"), {
            "message": "Please confirm the current delivery status.",
        })
        self.assertRedirects(
            response,
            reverse("platformhub:client_chat"),
            fetch_redirect_response=False,
        )
        message = ClientMessage.objects.get(conversation__user=self.user)
        self.assertEqual(message.sender, "client")
        self.assertEqual(message.body, "Please confirm the current delivery status.")

    def test_workspace_links_to_messages(self):
        response = self.client.get(reverse("platformhub:workspace"))
        self.assertContains(response, reverse("platformhub:client_chat"))


class HumanizerEntitlementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="credit-user",
            email="credits@example.com",
            password="strong-password-123",
        )

    def _fulfill(self, reference):
        payment = PaymentRecord.objects.create(
            user=self.user,
            reference=reference,
            amount=Decimal("25.00"),
            currency="USD",
            status="pending",
            email=self.user.email,
            metadata={"package_slug": "humanizer-pro"},
        )
        apply_gateway_transaction(payment.id, {
            "reference": reference,
            "status": "success",
            "amount": 2500,
            "currency": "USD",
            "channel": "card",
        })
        payment.refresh_from_db()
        return payment

    def test_repeat_tool_purchases_add_credits_and_record_fulfillment(self):
        starting_quota = self.user.profile.word_quota
        first = self._fulfill("INF-CREDITS-1")
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.word_quota, starting_quota + 250000)
        self.assertEqual(first.metadata["fulfillment"]["word_credits_added"], 250000)

        second = self._fulfill("INF-CREDITS-2")
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.word_quota, starting_quota + 500000)
        self.assertEqual(second.metadata["fulfillment"]["account_type"], "PRO")
