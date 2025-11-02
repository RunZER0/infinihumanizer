import logging
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.account.utils import user_email
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.urls import reverse

logger = logging.getLogger(__name__)

class CustomAccountAdapter(DefaultAccountAdapter):
    def login(self, request, user):
        """
        TEMPORARILY DISABLED - Email verification handled in VerifiedEmailLoginView
        """
        print("⚠️  CustomAccountAdapter.login() called - SKIPPING to let view handle it")
        # Just call parent login directly
        return super().login(request, user)

    def send_mail(self, template_prefix, email_template, context, from_email=None, to_email=None):
        """
        Sends an email using custom HTML + TXT templates located in templates/account/email/
        Handles allauth flows where only an email string (not a user) is passed.
        """
        subject = context.get("email_subject", f"{settings.SITE_NAME} Notification").strip()

        html_template_path = f"{template_prefix}_message.html"
        text_template_path = f"{template_prefix}_message.txt"

        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        # ✅ Resolve recipient email address safely across all flows
        if to_email is None:
            # Try context['email']
            to_email = context.get("email")

            # Try fallback: 'email_template' param might be the raw email string
            if not to_email and isinstance(email_template, str) and "@" in email_template:
                to_email = email_template

            # Try context['user']
            if not to_email:
                user = context.get("user")
                if user:
                    try:
                        to_email = user_email(user)
                    except Exception as e:
                        logger.warning(f"User email fetch failed: {e}")

            # If nothing works, raise helpful error
            if not to_email:
                logger.error(f"❌ Cannot resolve 'to_email'. Context keys: {list(context.keys())}")
                raise ValueError("Cannot send email: 'to_email' could not be determined.")

        logger.info(f"📤 Preparing to send email to {to_email} using template '{template_prefix}'")

        # Load HTML email body
        try:
            html_body = render_to_string(html_template_path, context)
            logger.info(f"✅ Loaded HTML template: {html_template_path}")
        except TemplateDoesNotExist:
            html_body = None
            logger.warning(f"⚠️ HTML template not found: {html_template_path}")
        except Exception as e:
            html_body = None
            logger.error(f"❌ Error rendering HTML template: {e}")

        # Load TXT fallback
        try:
            text_body = render_to_string(text_template_path, context)
            logger.info(f"✅ Loaded text template: {text_template_path}")
        except TemplateDoesNotExist:
            text_body = "This is a notification from Infiniai Assistant."
            logger.warning(f"⚠️ Text template not found: {text_template_path}")
        except Exception as e:
            text_body = "This is a notification from Infiniai Assistant."
            logger.error(f"❌ Error rendering text template: {e}")

        # Construct and send email
        try:
            msg = EmailMultiAlternatives(subject, text_body, from_email=from_email, to=[to_email])
            if html_body:
                msg.attach_alternative(html_body, "text/html")
            msg.send()
            logger.info(f"✅ Email successfully sent to {to_email}")
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            raise
