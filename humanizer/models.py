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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_conversation",
    )
    subject = models.CharField(max_length=220, default="Workspace chat")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.email or self.user.username} · {self.get_status_display()}"


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
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_sender_display()} · {self.created_at:%Y-%m-%d %H:%M}"
