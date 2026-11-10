from django.contrib import admin
from .models import ClientConversation, ClientMessage, Humanization


class ClientMessageInline(admin.TabularInline):
    model = ClientMessage
    extra = 0
    fields = ("sender", "author", "body", "attachments", "created_at", "read_at")


@admin.register(ClientConversation)
class ClientConversationAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "subject", "status", "category", "created_at", "updated_at")
    list_filter = ("status", "category", "created_at", "updated_at")
    search_fields = ("reference", "user__username", "user__email", "user__first_name", "user__last_name", "subject")
    inlines = [ClientMessageInline]


@admin.register(ClientMessage)
class ClientMessageAdmin(admin.ModelAdmin):
    list_display = ("conversation_ref", "sender", "author", "short_body", "created_at", "read_at")
    list_filter = ("sender", "created_at")
    search_fields = ("body", "conversation__reference", "conversation__user__email", "conversation__user__username")

    def conversation_ref(self, obj):
        return obj.conversation.reference or str(obj.conversation)
    conversation_ref.short_description = "Conversation"

    def short_body(self, obj):
        if not obj.body:
            return "(No text)"
        return obj.body[:80] + ("..." if len(obj.body) > 80 else "")
    short_body.short_description = "Message"


@admin.register(Humanization)
class HumanizationAdmin(admin.ModelAdmin):
    list_display = ("user", "model_name", "input_words", "output_words", "created_at")
    search_fields = ("user__username", "user__email")