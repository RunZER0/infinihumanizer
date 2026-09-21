from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount

from accounts.models import DeviceSession, EmailVerification, Profile, WhatsAppVerification
from humanizer.models import ClientConversation, ClientMessage, Humanization
from platformhub.models import (
    AssuranceJob,
    Consultation,
    Deliverable,
    DeliverableFeedback,
    Invoice,
    Organization,
    PaymentRecord,
    Quote,
    QuoteItem,
    ServiceRequest,
)


class OwnerAdminSite(admin.AdminSite):
    site_header = "InfiniAI administration"
    site_title = "InfiniAI Admin"
    index_title = "Operations"

    def _is_owner(self, user):
        if not user.is_authenticated or not user.is_active:
            return False
        if (user.email or "").strip().lower() != settings.INFINIAI_ADMIN_EMAIL:
            return False
        return SocialAccount.objects.filter(user=user, provider="google").exists()

    def has_permission(self, request):
        return self._is_owner(request.user)

    def login(self, request, extra_context=None):
        if not request.user.is_authenticated:
            return redirect(f'{reverse("account_login")}?next={request.path}')
        if not self._is_owner(request.user):
            return HttpResponseForbidden(
                "Administrator access is restricted to the authorized Google account."
            )
        return redirect("infini_admin:index")


admin_site = OwnerAdminSite(name="infini_admin")


class OwnerPermissionMixin:
    def has_module_permission(self, request):
        return self.admin_site.has_permission(request)

    def has_view_permission(self, request, obj=None):
        return self.admin_site.has_permission(request)

    def has_add_permission(self, request):
        return self.admin_site.has_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.admin_site.has_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.admin_site.has_permission(request)


class OwnerModelAdmin(OwnerPermissionMixin, admin.ModelAdmin):
    list_per_page = 50


class OwnerUserAdmin(OwnerPermissionMixin, UserAdmin):
    pass


class OwnerGroupAdmin(OwnerPermissionMixin, GroupAdmin):
    pass


class ClientMessageInline(admin.TabularInline):
    model = ClientMessage
    extra = 1
    fields = ("sender", "body", "author", "created_at", "read_at")
    readonly_fields = ("created_at",)

    def has_view_permission(self, request, obj=None):
        return self.admin_site.has_permission(request)

    def has_add_permission(self, request, obj=None):
        return self.admin_site.has_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.admin_site.has_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.admin_site.has_permission(request)


class ClientConversationAdmin(OwnerModelAdmin):
    list_display = ("user", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__email", "user__username", "subject")
    inlines = [ClientMessageInline]


class ClientMessageAdmin(OwnerModelAdmin):
    list_display = ("conversation", "sender", "author", "created_at", "read_at")
    list_filter = ("sender",)
    search_fields = ("conversation__user__email", "body")


class HumanizationAdmin(OwnerModelAdmin):
    list_display = ("user", "input_words", "output_words", "model_name", "updated_at")
    search_fields = ("user__email", "source_text", "output_text")
    readonly_fields = ("created_at", "updated_at")


class ServiceRequestAdmin(OwnerModelAdmin):
    list_display = ("reference", "title", "email", "service_family", "status", "created_at")
    list_filter = ("status", "service_family")
    search_fields = ("reference", "title", "email", "full_name", "company")


class PaymentRecordAdmin(OwnerModelAdmin):
    list_display = ("reference", "email", "amount", "currency", "status", "source_type", "created_at")
    list_filter = ("status", "currency", "source_type")
    search_fields = ("reference", "email", "original_description")


class InvoiceAdmin(OwnerModelAdmin):
    list_display = ("number", "email", "amount_due", "amount_paid", "currency", "status", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("number", "email", "description")


class QuoteAdmin(OwnerModelAdmin):
    list_display = ("number", "request", "total", "currency", "status", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("number", "request__reference", "request__email")


class AssuranceJobAdmin(OwnerModelAdmin):
    list_display = ("reference", "user", "title", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("reference", "user__email", "title")


for model in [
    Organization,
    Consultation,
    QuoteItem,
    Deliverable,
    DeliverableFeedback,
    Profile,
    DeviceSession,
    EmailVerification,
    WhatsAppVerification,
    EmailAddress,
    SocialAccount,
]:
    admin_site.register(model, OwnerModelAdmin)

admin_site.register(User, OwnerUserAdmin)
admin_site.register(Group, OwnerGroupAdmin)
admin_site.register(ServiceRequest, ServiceRequestAdmin)
admin_site.register(Quote, QuoteAdmin)
admin_site.register(Invoice, InvoiceAdmin)
admin_site.register(PaymentRecord, PaymentRecordAdmin)
admin_site.register(AssuranceJob, AssuranceJobAdmin)
admin_site.register(Humanization, HumanizationAdmin)
admin_site.register(ClientConversation, ClientConversationAdmin)
admin_site.register(ClientMessage, ClientMessageAdmin)
