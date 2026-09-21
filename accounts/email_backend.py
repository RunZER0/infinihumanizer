from email.utils import parseaddr

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class BrevoAPIEmailBackend(BaseEmailBackend):
    """Send Django email through Brevo's HTTPS API instead of blocked SMTP ports."""

    endpoint = "https://api.brevo.com/v3/smtp/email"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = getattr(settings, "BREVO_API_KEY", "")
        if not api_key:
            if self.fail_silently:
                return 0
            raise RuntimeError("Transactional email is not configured.")

        sent = 0
        for message in email_messages:
            try:
                sender_name, sender_email = parseaddr(
                    message.from_email or settings.DEFAULT_FROM_EMAIL
                )
                sender_email = (
                    getattr(settings, "BREVO_SENDER_EMAIL", "") or sender_email
                ).strip()
                sender_name = (
                    getattr(settings, "BREVO_SENDER_NAME", "") or sender_name or "InfiniAI"
                ).strip()
                if not sender_email:
                    raise RuntimeError("Transactional email sender is not configured.")

                html_content = ""
                for alternative in getattr(message, "alternatives", []) or []:
                    content = getattr(alternative, "content", None)
                    mimetype = getattr(alternative, "mimetype", None)
                    if content is None and isinstance(alternative, (tuple, list)):
                        content, mimetype = alternative
                    if mimetype == "text/html":
                        html_content = content
                        break

                payload = {
                    "sender": {"name": sender_name, "email": sender_email},
                    "to": [{"email": address} for address in message.to],
                    "subject": message.subject,
                    "textContent": message.body or "",
                }
                if html_content:
                    payload["htmlContent"] = html_content
                    payload.pop("textContent", None)
                if message.cc:
                    payload["cc"] = [{"email": address} for address in message.cc]
                if message.bcc:
                    payload["bcc"] = [{"email": address} for address in message.bcc]
                if message.reply_to:
                    reply_name, reply_email = parseaddr(message.reply_to[0])
                    payload["replyTo"] = {
                        "email": reply_email or message.reply_to[0],
                        "name": reply_name or reply_email or message.reply_to[0],
                    }

                response = requests.post(
                    self.endpoint,
                    headers={
                        "accept": "application/json",
                        "api-key": api_key,
                        "content-type": "application/json",
                    },
                    json=payload,
                    timeout=15,
                )
                response.raise_for_status()
                sent += 1
            except Exception:
                if not self.fail_silently:
                    raise
        return sent
