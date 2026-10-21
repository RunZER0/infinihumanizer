from django.contrib import admin
from .models import ClientConversation, ClientMessage, Humanization


class ClientMessageInline(admin.TabularInline):
    model = ClientMessage
    extra = 0
    readonly_fields = ("created_at", "read_at")
    fields = ("sender", "author", "body", "attachments", "created_at", "read_at")


@admin.register(ClientConversation)
class ClientConversationAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "subject")
    inlines = [ClientMessageInline]


@admin.register(ClientMessage)
class ClientMessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "author", "created_at", "read_at")
    list_filter = ("sender", "created_at")
    search_fields = ("body", "conversation__user__email", "conversation__user__username")


@admin.register(Humanization)
class HumanizationAdmin(admin.ModelAdmin):
    list_display = ("user", "model_name", "input_words", "output_words", "created_at")
    search_fields = ("user__username", "user__email")