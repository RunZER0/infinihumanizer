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
        self.assertContains(page, "Enter the code")


    @patch("platformhub.views.issue_email_code")
    def test_contact_email_step_updates_in_place(self, issue_code):
        issue_code.return_value = (object(), True)
        session = self.client.session
        session["infini_consult_name"] = "Potential client"
        session.save()

        response = self.client.post(
            reverse("platformhub:consultation"),
            {
                "action": "set_email",
                "email": "client@example.com",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["step"], "verify")
        self.assertIn("Enter the code", payload["html"])
        self.assertNotIn("We verify", payload["html"])
        self.assertNotIn("WHY VERIFY", payload["html"])

    @patch("platformhub.views.verify_email_code", return_value=(True, ""))
    def test_contact_code_verification_does_not_reload_page(self, verify_code):
        session = self.client.session
        session["infini_consult_name"] = "Potential client"
        session["infini_consult_email"] = "client@example.com"
        session.save()

        response = self.client.post(
            reverse("platformhub:consultation"),
            {
                "action": "verify_email",
                "code": "123456",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["step"], "details")
        self.assertIn("Your message", payload["html"])
        verify_code.assert_called_once_with("client@example.com", "123456")

    def test_contact_page_has_no_verification_narration(self):
        session = self.client.session
        session["infini_consult_name"] = "Potential client"
        session.save()

        response = self.client.get(reverse("platformhub:consultation"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "We verify")
        self.assertNotContains(response, "WHY VERIFY")
        self.assertNotContains(response, "Temporary and disposable")

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

    def test_two_way_chat_and_admin_invoice_workflow(self):
        from humanizer.models import ClientConversation, ClientMessage

        client_post = self.client.post(
            reverse("platformhub:client_chat"),
            {"message": "Can you issue the invoice for phase one?"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(client_post.status_code, 200)
        client_payload = client_post.json()
        self.assertTrue(client_payload["ok"])
        self.assertEqual(client_payload["message"]["sender"], "client")
        self.assertTrue(client_payload["message"]["created_at_display"])

        conv = ClientConversation.objects.get(user=self.user)

        admin_post = self.client.post(
            reverse("platformhub:operations_desk_conversation", kwargs={"conversation_id": conv.id}),
            {"action": "reply", "message": "Sending the phase one invoice now."},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(admin_post.status_code, 200)
        admin_payload = admin_post.json()
        self.assertTrue(admin_payload["ok"])
        self.assertEqual(admin_payload["message"]["sender"], "admin")
        self.assertTrue(admin_payload["message"]["created_at_display"])

        inv_post = self.client.post(
            reverse("platformhub:admin_create_invoice"),
            {
                "conversation_id": str(conv.id),
                "email": self.user.email,
                "description": "Phase one architecture brief",
                "currency": "USD",
                "amount_due": "450.00",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(inv_post.status_code, 200)
        inv_payload = inv_post.json()
        self.assertTrue(inv_payload["ok"])
        self.assertEqual(inv_payload["invoice"]["amount_due"], "450.00")
        self.assertEqual(inv_payload["invoice"]["description"], "Phase one architecture brief")

        feed_res = self.client.get(
            reverse("platformhub:client_chat_feed"),
            {"conversation": str(conv.id), "role": "client"},
        )
        self.assertEqual(feed_res.status_code, 200)
        feed_data = feed_res.json()
        self.assertEqual(len(feed_data["messages"]), 3)
        self.assertEqual(feed_data["messages"][0]["sender"], "client")
        self.assertEqual(feed_data["messages"][1]["sender"], "admin")
        self.assertEqual(len(feed_data["invoices"]), 1)

        client_page = self.client.get(reverse("platformhub:client_chat"))
        self.assertContains(client_page, "Can you issue the invoice for phase one?")
        self.assertContains(client_page, "Sending the phase one invoice now.")
        self.assertContains(client_page, "Phase one architecture brief")
        self.assertEqual(ClientMessage.objects.filter(conversation=conv).count(), 3)

    def test_client_and_admin_can_upload_chat_attachments(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from humanizer.models import ClientConversation
        from platformhub.chat_files import get_chat_files_dir

        files_dir = get_chat_files_dir()
        sample_pdf = SimpleUploadedFile(
            "vendor_notes.pdf",
            b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n" + b"A" * 12000 + b"\n%%EOF\n",
            content_type="application/pdf",
        )
        res = self.client.post(
            reverse("platformhub:client_chat"),
            {"message": "Here is the PDF.", "attachments": [sample_pdf]},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(len(payload["message"]["attachments"]), 1)
        att = payload["message"]["attachments"][0]
        self.assertEqual(att["name"], "vendor_notes.pdf")
        self.assertEqual(att["kind"], "PDF")

        dl_res = self.client.get(att["url"])
        self.assertEqual(dl_res.status_code, 200)
        dl_res.close()

        conv = ClientConversation.objects.get(user=self.user)
        sample_docx = SimpleUploadedFile(
            "deliverable_v1.docx",
            b"PK\x03\x04fake-docx-payload" + b"B" * 12000,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        admin_res = self.client.post(
            reverse("platformhub:operations_desk_conversation", kwargs={"conversation_id": conv.id}),
            {"action": "reply", "message": "Attached the clean draft.", "attachments": [sample_docx]},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(admin_res.status_code, 200)
        admin_payload = admin_res.json()
        self.assertTrue(admin_payload["ok"])
        self.assertEqual(len(admin_payload["message"]["attachments"]), 1)
        self.assertEqual(admin_payload["message"]["attachments"][0]["kind"], "DOCX")

        # Clean up uploaded test files from disk
        for p in files_dir.glob("*_vendor_notes.pdf"):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
        for p in files_dir.glob("*_deliverable_v1.docx"):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass

    def test_seed_orbit_production_populates_threads_invoices_and_ledger(self):
        from django.core.management import call_command
        from humanizer.models import ClientConversation, ClientMessage

        call_command("seed_orbit_production", reset=True)
        self.assertEqual(PaymentRecord.objects.count(), 51)
        self.assertEqual(PaymentRecord.objects.filter(status="success").count(), 51)
        self.assertEqual(PaymentRecord.objects.filter(invoice__isnull=False).count(), 51)
        self.assertEqual(Invoice.objects.count(), 40)
        self.assertEqual(ClientConversation.objects.count(), 18)




        messages_with_files = [
            m for m in ClientMessage.objects.all() if m.attachments
        ]
        self.assertGreaterEqual(len(messages_with_files), 30)

        sample_att = messages_with_files[0].attachments[0]
        dl = self.client.get(sample_att["url"])
        self.assertEqual(dl.status_code, 200)

        desk = self.client.get(reverse("platformhub:operations_desk"))
        self.assertEqual(desk.status_code, 200)
        self.assertContains(desk, "Snapchat")

        first_inv = Invoice.objects.exclude(status="void").first()
        inv_page = self.client.get(reverse("platformhub:operations_invoices"))
        self.assertEqual(inv_page.status_code, 200)
        self.assertContains(inv_page, first_inv.number)

        tx_page = self.client.get(reverse("platformhub:operations_transactions"))
        self.assertEqual(tx_page.status_code, 200)
        self.assertContains(tx_page, "T850856961040908")
        self.assertContains(tx_page, "T493259790266047")
        self.assertContains(tx_page, "QP-MOL7PPPC2N24")
        self.assertContains(tx_page, "QP-MQWYNHW6NBYG")






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


class PostersGalleryTests(TestCase):
    def test_posters_gallery_renders_20_posters_and_contact_ctas(self):
        url = reverse("platformhub:posters")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["posters"]), 20)
        self.assertContains(resp, "Contact us via www.byinfini.online/consultation/")
        self.assertContains(resp, "poster_01.png")
        self.assertContains(resp, "poster_20.png")
        self.assertContains(resp, "poster_01.jpg")
        self.assertContains(resp, "poster_20.jpg")


class AdminPostersDownloadTests(TestCase):
    def setUp(self):
        from platformhub.engaging_posters_data import sync_social_posters_db
        sync_social_posters_db()

    def test_operations_posters_page_renders_in_admin(self):
        url = reverse("platformhub:operations_posters")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["posters"]), 20)
        self.assertContains(resp, "Download All 20 Posters (.ZIP)")
        self.assertContains(resp, "Download PNG")
        self.assertContains(resp, "Download JPG")

    def test_operations_posters_style_filtering(self):
        url = reverse("platformhub:operations_posters") + "?style=photo-dark"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["posters"]), 20)

    def test_operations_individual_poster_png_download(self):
        url = reverse("platformhub:operations_download_poster", kwargs={"number": "01", "format_type": "png"})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "image/png")
        self.assertIn("attachment", resp["Content-Disposition"])
        self.assertIn("infini_story_01.png", resp["Content-Disposition"])

    def test_operations_individual_poster_jpg_download(self):
        url = reverse("platformhub:operations_download_poster", kwargs={"number": "01", "format_type": "jpg"})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "image/jpeg")
        self.assertIn("attachment", resp["Content-Disposition"])
        self.assertIn("infini_story_01.jpg", resp["Content-Disposition"])

    def test_operations_download_all_zip_bundle(self):
        url = reverse("platformhub:operations_download_all_posters")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/zip")
        self.assertIn("infini_social_story_posters_20.zip", resp["Content-Disposition"])
        self.assertGreater(len(resp.content), 500000)

    def test_social_poster_admin_model(self):
        from platformhub.models import SocialPoster

        poster = SocialPoster.objects.first()
        self.assertIsNotNone(poster)
        self.assertEqual(poster.png_url, f"/static/posters/poster_{poster.number}.png")
        self.assertEqual(poster.jpg_url, f"/static/posters/poster_{poster.number}.jpg")
        self.assertTrue(len(poster.full_headline) > 0)

    def test_django_admin_changelist_view_renders_with_download_controls(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user = User.objects.create_superuser(username="admin_poster_test", email="admin@example.com", password="password123")
        self.client.force_login(admin_user)

        resp = self.client.get("/admin/platformhub/socialposter/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Download All 20 Posters (.ZIP)")
        self.assertContains(resp, "Visual Studio Gallery")
        self.assertContains(resp, "Direct Downloads")
        self.assertContains(resp, "operations/posters/download/01/png/")
        self.assertContains(resp, "operations/posters/download/01/jpg/")

    def test_django_admin_action_download_selected_zip(self):
        from django.contrib.auth import get_user_model
        from platformhub.models import SocialPoster
        User = get_user_model()
        admin_user = User.objects.create_superuser(username="admin_action_test", email="admin_action@example.com", password="password123")
        self.client.force_login(admin_user)

        posters = list(SocialPoster.objects.filter(number__in=["01", "02"]))
        post_data = {
            "action": "download_selected_as_zip",
            "_selected_action": [str(p.pk) for p in posters],
        }
        resp = self.client.post("/admin/platformhub/socialposter/", post_data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/zip")
        self.assertIn("infini_selected_posters.zip", resp["Content-Disposition"])
        self.assertGreater(len(resp.content), 100000)

    def test_django_admin_action_download_all_zip(self):
        from django.contrib.auth import get_user_model
        from platformhub.models import SocialPoster
        User = get_user_model()
        admin_user = User.objects.create_superuser(username="admin_all_test", email="admin_all@example.com", password="password123")
        self.client.force_login(admin_user)

        first_poster = SocialPoster.objects.first()
        post_data = {
            "action": "download_all_as_zip",
            "_selected_action": [str(first_poster.pk)],
        }
        resp = self.client.post("/admin/platformhub/socialposter/", post_data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/zip")
        self.assertIn("infini_all_20_social_posters.zip", resp["Content-Disposition"])
        self.assertGreater(len(resp.content), 500000)


class AudioChatAndIntakeEndToEndTests(TestCase):
    def test_consultation_intake_creates_conversation_and_surfaces_in_admin_desk(self):
        from django.contrib.auth import get_user_model
        from humanizer.models import ClientConversation, ClientMessage
        from platformhub.models import Consultation
        from accounts.verification import SESSION_VERIFIED_EMAIL

        User = get_user_model()
        client_email = "marcus.vance@executivebrief.com"

        session = self.client.session
        session["infini_consult_name"] = "Dr. Marcus Vance"
        session["infini_consult_email"] = client_email
        session[SESSION_VERIFIED_EMAIL] = client_email
        session.save()

        post_res = self.client.post(
            reverse("platformhub:consultation"),
            {
                "action": "submit_note",
                "topic": "We require an executive communication audit and technical reports restructuring.",
                "company": "Vance BioAnalytics",
            },
        )
        self.assertEqual(post_res.status_code, 302)

        consultation = Consultation.objects.filter(email=client_email).first()
        self.assertIsNotNone(consultation)
        self.assertEqual(consultation.full_name, "Dr. Marcus Vance")
        self.assertEqual(consultation.company, "Vance BioAnalytics")

        user = User.objects.filter(email__iexact=client_email).first()
        self.assertIsNotNone(user)
        self.assertEqual(consultation.user, user)

        conversation = ClientConversation.objects.filter(user=user).first()
        self.assertIsNotNone(conversation)
        self.assertEqual(conversation.status, "open")

        initial_msg = ClientMessage.objects.filter(conversation=conversation, sender="client").first()
        self.assertIsNotNone(initial_msg)
        self.assertIn(consultation.reference, initial_msg.body)
        self.assertIn("Vance BioAnalytics", initial_msg.body)
        self.assertIn("executive communication audit", initial_msg.body)

        desk_res = self.client.get(reverse("platformhub:operations_desk"))
        self.assertEqual(desk_res.status_code, 200)
        self.assertContains(desk_res, "Dr. Marcus Vance")
        self.assertContains(desk_res, client_email)

    def test_admin_and_client_audio_exchange_flow(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.contrib.auth import get_user_model
        from humanizer.models import ClientConversation, ClientMessage

        User = get_user_model()
        client_user = User.objects.create_user(
            username="clara_client",
            email="clara@soundstudio.io",
            first_name="Clara",
            last_name="Oswald",
        )
        conversation = ClientConversation.objects.create(
            user=client_user,
            subject="Studio Voice & Language Direction",
            status="open",
        )

        from platformhub.chat_files import get_chat_files_dir

        files_dir = get_chat_files_dir()
        admin_audio = SimpleUploadedFile(
            "studio_briefing.mp3",
            b"\xff\xfb\x90\x44" * 3000,
            content_type="audio/mpeg",
        )
        admin_post = self.client.post(
            reverse("platformhub:operations_desk_conversation", kwargs={"conversation_id": conversation.id}),
            {
                "action": "reply",
                "message": "Here is the audio voice overview for the brief.",
                "attachments": [admin_audio],
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(admin_post.status_code, 200)
        admin_data = admin_post.json()
        self.assertTrue(admin_data["ok"])
        self.assertEqual(admin_data["message"]["sender"], "admin")
        self.assertEqual(len(admin_data["message"]["attachments"]), 1)
        att = admin_data["message"]["attachments"][0]
        self.assertTrue(att["is_audio"])
        self.assertEqual(att["kind"], "AUDIO")
        self.assertEqual(att["mime"], "audio/mpeg")
        self.assertIn("studio_briefing", att["filename"])

        audio_res = self.client.get(att["url"])
        self.assertEqual(audio_res.status_code, 200)
        self.assertEqual(audio_res["Content-Type"], "audio/mpeg")
        audio_res.close()

        feed_res = self.client.get(
            reverse("platformhub:client_chat_feed"),
            {"conversation": str(conversation.id), "role": "client"},
        )
        self.assertEqual(feed_res.status_code, 200)
        feed_data = feed_res.json()
        self.assertEqual(len(feed_data["messages"]), 1)
        self.assertTrue(feed_data["messages"][0]["attachments"][0]["is_audio"])

        client_voice = SimpleUploadedFile(
            "voice_note_feedback.webm",
            b"\x1a\x45\xdf\xa3" * 3000,
            content_type="audio/webm",
        )
        self.client.force_login(client_user)
        client_post = self.client.post(
            reverse("platformhub:client_chat"),
            {
                "conversation_id": str(conversation.id),
                "message": "Recorded voice feedback on pacing.",
                "attachments": [client_voice],
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(client_post.status_code, 200)
        client_data = client_post.json()
        self.assertTrue(client_data["ok"])
        self.assertEqual(client_data["message"]["sender"], "client")
        self.assertEqual(len(client_data["message"]["attachments"]), 1)
        client_att = client_data["message"]["attachments"][0]
        self.assertTrue(client_att["is_audio"])
        self.assertEqual(client_att["kind"], "AUDIO")
        self.assertEqual(client_att["mime"], "audio/webm")

        client_audio_res = self.client.get(client_att["url"])
        self.assertEqual(client_audio_res.status_code, 200)
        self.assertEqual(client_audio_res["Content-Type"], "audio/webm")
        client_audio_res.close()

        # Clean up created audio files from disk
        for p in files_dir.glob("*_studio_briefing.mp3"):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
        for p in files_dir.glob("*_voice_note_feedback.webm"):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass

        admin_feed_res = self.client.get(
            reverse("platformhub:client_chat_feed"),
            {"conversation": str(conversation.id), "role": "admin"},
        )
        self.assertEqual(admin_feed_res.status_code, 200)
        admin_feed_data = admin_feed_res.json()
        self.assertEqual(len(admin_feed_data["messages"]), 2)
        self.assertEqual(admin_feed_data["messages"][1]["sender"], "client")
        self.assertTrue(admin_feed_data["messages"][1]["attachments"][0]["is_audio"])

    def test_django_admin_displays_consultation_and_conversations(self):
        from django.contrib.auth import get_user_model
        from humanizer.models import ClientConversation
        from platformhub.models import Consultation

        User = get_user_model()
        superuser = User.objects.create_superuser(
            username="admin_consult_test",
            email="admin_consult@example.com",
            password="adminpassword123",
        )
        self.client.force_login(superuser)

        consult = Consultation.objects.create(
            full_name="Lady Violet",
            email="violet@crawley.estate",
            company="Downton",
            topic="Need writing polished for royal correspondence.",
        )
        ClientConversation.objects.create(
            user=superuser,
            subject="Admin oversight thread",
        )

        resp_consult = self.client.get("/admin/platformhub/consultation/")
        self.assertEqual(resp_consult.status_code, 200)
        self.assertContains(resp_consult, "Lady Violet")
        self.assertContains(resp_consult, consult.reference)

        resp_conv = self.client.get("/admin/humanizer/clientconversation/")
        self.assertEqual(resp_conv.status_code, 200)
        self.assertContains(resp_conv, "Admin oversight thread")


class InvoicePdfAndVerificationTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            username="jose_cruz",
            email="josecruz.creative@gmail.com",
            first_name="Jose",
            last_name="Cruz",
        )
        self.invoice = Invoice.objects.create(
            number="INV-261018-JC01",
            user=self.user,
            email=self.user.email,
            currency="USD",
            amount_due=Decimal("120.00"),
            amount_paid=Decimal("120.00"),
            description="Brand voice guidelines and story restructuring",
            status="paid",
        )

    def test_privacy_masking_helpers(self):
        from .invoice_pdf import mask_email, mask_name
        self.assertEqual(mask_email("josecruz.creative@gmail.com"), "j***e@gmail.com")
        self.assertEqual(mask_email("audreymbrown2007@gmail.com"), "a***7@gmail.com")
        self.assertEqual(mask_name("Jose Cruz"), "Jose C. [Protected]")
        self.assertEqual(mask_name("Audrey Brown"), "Audrey B. [Protected]")

    def test_invoice_pdf_download_by_uuid_and_number(self):
        res_uuid = self.client.get(reverse("platformhub:invoice_pdf_download", kwargs={"invoice_id": self.invoice.id}))
        self.assertEqual(res_uuid.status_code, 200)
        self.assertEqual(res_uuid["Content-Type"], "application/pdf")
        self.assertIn("INV-261018-JC01.pdf", res_uuid["Content-Disposition"])
        self.assertTrue(len(res_uuid.content) > 1000)

        res_num = self.client.get(reverse("platformhub:invoice_pdf_download", kwargs={"invoice_id": self.invoice.number}))
        self.assertEqual(res_num.status_code, 200)
        self.assertEqual(res_num["Content-Type"], "application/pdf")

    def test_invoice_verification_redacts_private_details(self):
        res = self.client.get(reverse("platformhub:invoice_verify", kwargs={"invoice_id": self.invoice.id}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "INV-261018-JC01")
        self.assertContains(res, "120.00")
        self.assertContains(res, "Settled &amp; Paid")
        self.assertContains(res, "Brand voice guidelines")

        self.assertContains(res, "Jose C. [Protected]")
        self.assertContains(res, "j***e@gmail.com")
        self.assertNotContains(res, "josecruz.creative@gmail.com")
        self.assertNotContains(res, "Jose Cruz")

    def test_audrey_brown_showcase_page(self):
        res = self.client.get(reverse("platformhub:showcase_studio_brown"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Studio Brown")
        self.assertContains(res, "audreybrown-studio/studio-brown-portfolio")
        self.assertContains(res, "East Austin")
        self.assertContains(res, "Essential Session")
        self.assertContains(res, "$450")
        self.assertContains(res, "$950")
        self.assertContains(res, "$2,200")

    def test_dockstream_showcase_page(self):
        res = self.client.get(reverse("platformhub:showcase_dockstream"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "DockStream")
        self.assertContains(res, "Interactive Cross-Dock Terminal")
        self.assertContains(res, "detention savings")
        # Direct route
        res_direct = self.client.get(reverse("platformhub:dockstream_direct"))
        self.assertEqual(res_direct.status_code, 200)

    def test_orozco_roofing_showcase_page(self):
        res = self.client.get(reverse("platformhub:showcase_orozco"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Orozco")
        self.assertContains(res, "Commercial Roof Bid Calculator")
        self.assertContains(res, "60-mil")
        self.assertContains(res, "Carlisle")
        # Direct route
        res_direct = self.client.get(reverse("platformhub:orozco_direct"))
        self.assertEqual(res_direct.status_code, 200)

    def test_apexdesk_showcase_page(self):
        res = self.client.get(reverse("platformhub:showcase_apexdesk"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "ApexDesk")
        self.assertContains(res, "Configure Your Desk Ecosystem")
        self.assertContains(res, "Qi2")
        self.assertContains(res, "MagSafe")
        # Direct route
        res_direct = self.client.get(reverse("platformhub:apexdesk_direct"))
        self.assertEqual(res_direct.status_code, 200)




