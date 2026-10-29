import uuid

from django.conf import settings
from django.db import models


class Humanization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="humanizations",
    )
    source_text = models.TextField()
    output_text = models.TextField()
    variation = models.FloatField(default=0.65)
    model_name = models.CharField(max_length=120, blank=True)
    input_words = models.PositiveIntegerField(default=0)
    output_words = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user_id} · {self.created_at:%Y-%m-%d %H:%M}"


class ClientConversation(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]
    CATEGORY_CHOICES = [
        ("job", "Job"),
        ("support", "Support"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_conversations",
    )
    reference = models.CharField(max_length=24, blank=True, db_index=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="job")
    subject = models.CharField(max_length=220, default="Workspace chat")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        ref = f"[{self.reference}] " if self.reference else ""
        return f"{ref}{self.user.email or self.user.username} · {self.get_status_display()}"

    def compute_reference(self):
        user = self.user
        initials = ""
        if user:
            fn = (user.first_name or "").strip()
            ln = (user.last_name or "").strip()
            if fn and ln:
                initials = f"{fn[0]}{ln[0]}".upper()
            elif fn:
                initials = fn[:2].upper()
            elif user.username:
                initials = user.username[:2].upper()
            elif user.email:
                initials = user.email.split("@")[0][:2].upper()
        initials = (initials or "CL")[:2].upper()
        if len(initials) == 1:
            initials = f"{initials}X"
        existing_refs = list(
            ClientConversation.objects.filter(user_id=self.user_id)
            .exclude(pk=self.pk)
            .values_list("reference", flat=True)
        )
        max_num = 0
        for r in existing_refs:
            if r and r.startswith(initials):
                suffix = r[len(initials):]
                if suffix.isdigit():
                    max_num = max(max_num, int(suffix))
        next_num = max(max_num + 1, len(existing_refs) + 1)
        return f"{initials}{next_num:02d}"

    def save(self, *args, **kwargs):
        if not self.reference and self.user_id:
            self.reference = self.compute_reference()
        super().save(*args, **kwargs)


class ClientMessage(models.Model):
    SENDER_CHOICES = [
        ("client", "Client"),
        ("admin", "InfiniAI"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        ClientConversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="infini_chat_messages",
    )
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    body = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_sender_display()} · {self.created_at:%Y-%m-%d %H:%M}"



class AnonymousHumanizerUsage(models.Model):
    day = models.DateField()
    fingerprint = models.CharField(max_length=64)
    words_used = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["day", "fingerprint"],
                name="humanizer_anon_usage_day_fingerprint",
            ),
        ]
        ordering = ["-day", "-updated_at"]

    def __str__(self):
        return f"{self.day} · {self.words_used} words"


from django.contrib.auth import get_user_model

def _user_client_conversation(self):
    return self.client_conversations.order_by("-updated_at").first()

try:
    get_user_model().client_conversation = property(_user_client_conversation)
except Exception:
    pass
