from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.utils.html import format_html
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount

from accounts.models import DeviceSession, EmailVerification, Profile, WhatsAppVerification
from humanizer.models import AnonymousHumanizerUsage, ClientConversation, ClientMessage, Humanization
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
    SocialPoster,
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
        return bool(
            request.user.is_authenticated
            and request.user.is_active
            and (request.user.is_superuser or self._is_owner(request.user))
        )

    def admin_view(self, view, cacheable=False):
        parent_wrapper = super().admin_view(view, cacheable=cacheable)

        def inner(request, *args, **kwargs):
            if not self.has_permission(request) and request.user.is_authenticated:
                return HttpResponseForbidden(
                    "Administrator access is restricted to the authorized Google account."
                )
            return parent_wrapper(request, *args, **kwargs)

        return inner

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
    list_display = ("user", "status", "updated_at", "open_chat")
    list_filter = ("status",)
    search_fields = ("user__email", "user__username", "subject")
    inlines = [ClientMessageInline]

    def get_urls(self):
        return [
            path(
                "<path:object_id>/chat/",
                self.admin_site.admin_view(self.chat_view),
                name="humanizer_clientconversation_chat",
            ),
        ] + super().get_urls()

    @admin.display(description="Conversation")
    def open_chat(self, obj):
        url = reverse(
            "infini_admin:humanizer_clientconversation_chat",
            args=[obj.pk],
        )
        return format_html('<a href="{}">Open chat →</a>', url)

    def chat_view(self, request, object_id):
        conversation = get_object_or_404(ClientConversation, pk=object_id)

        if request.method == "POST":
            body = request.POST.get("message", "").strip()
            if not body:
                self.message_user(request, "Write a message before sending.", level="error")
            elif len(body) > 5000:
                self.message_user(request, "Keep the message under 5,000 characters.", level="error")
            else:
                ClientMessage.objects.create(
                    conversation=conversation,
                    author=request.user,
                    sender="admin",
                    body=body,
                )
                conversation.status = "open"
                conversation.save(update_fields=["status", "updated_at"])
                self.message_user(request, "Reply sent.")
            return redirect(
                reverse(
                    "infini_admin:humanizer_clientconversation_chat",
                    args=[conversation.pk],
                )
            )

        conversation.messages.filter(
            sender="client",
            read_at__isnull=True,
        ).update(read_at=timezone.now())

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "original": conversation,
            "title": f"Chat with {conversation.user.email or conversation.user.username}",
            "conversation": conversation,
            "chat_messages": conversation.messages.select_related("author").all(),
        }
        return render(
            request,
            "admin/humanizer/clientconversation/chat.html",
            context,
        )


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


class SocialPosterAdmin(OwnerModelAdmin):
    change_list_template = "admin/platformhub/socialposter/change_list.html"
    list_display = (
        "poster_preview",
        "number",
        "tag_badge",
        "eyebrow",
        "headline_display",
        "style",
        "turnaround",
        "download_actions",
    )
    list_filter = ("style",)
    search_fields = ("number", "tag_badge", "eyebrow", "headline_pre", "headline_span", "outcome")
    readonly_fields = ("poster_large_preview", "download_actions", "created_at", "updated_at")
    actions = ["download_selected_as_zip", "download_all_as_zip"]

    def changelist_view(self, request, extra_context=None):
        if not SocialPoster.objects.exists():
            from platformhub.engaging_posters_data import sync_social_posters_db
            sync_social_posters_db()
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description="Preview")
    def poster_preview(self, obj):
        return format_html(
            '<a href="{}" target="_blank" title="Click to view full image"><img src="{}" style="height:90px; width:auto; border-radius:4px; border:1px solid #cfc9bc; box-shadow:0 1px 3px rgba(0,0,0,0.1);" /></a>',
            obj.png_url,
            obj.png_url,
        )

    @admin.display(description="Headline")
    def headline_display(self, obj):
        return format_html(
            '<strong>{}</strong> <span style="color:#c84132; font-weight:700;">{}</span> {}',
            obj.headline_pre,
            obj.headline_span,
            obj.headline_post,
        )

    @admin.display(description="Direct Downloads")
    def download_actions(self, obj):
        png_dl = reverse("platformhub:operations_download_poster", kwargs={"number": obj.number, "format_type": "png"})
        jpg_dl = reverse("platformhub:operations_download_poster", kwargs={"number": obj.number, "format_type": "jpg"})
        return format_html(
            '<div style="display:flex; gap:6px; align-items:center;">'
            '<a class="button" href="{}" download style="background:#c84132; color:#ffffff !important; padding:4px 10px; border-radius:3px; text-decoration:none; font-weight:700; font-size:11px; letter-spacing:0.04em;">PNG</a>'
            '<a class="button" href="{}" download style="background:#11110f; color:#faf8f2 !important; padding:4px 10px; border-radius:3px; text-decoration:none; font-weight:700; font-size:11px; letter-spacing:0.04em;">JPG</a>'
            '</div>',
            png_dl,
            jpg_dl,
        )

    @admin.display(description="Full Image Preview")
    def poster_large_preview(self, obj):
        return format_html(
            '<div style="margin-bottom:12px;">'
            '<a href="{}" target="_blank"><img src="{}" style="max-height:540px; width:auto; border-radius:6px; border:1px solid #cfc9bc; box-shadow:0 4px 12px rgba(0,0,0,0.15);" /></a>'
            '</div>',
            obj.png_url,
            obj.png_url,
        )

    def _build_zip_response(self, queryset, filename):
        import io, zipfile
        from pathlib import Path
        from django.http import HttpResponse

        buffer = io.BytesIO()
        candidate_dirs = [
            Path(settings.BASE_DIR) / "static" / "posters",
            Path(settings.BASE_DIR) / "staticfiles" / "posters",
            Path(settings.BASE_DIR) / "public" / "posters",
        ]
        if hasattr(settings, "STATIC_ROOT") and settings.STATIC_ROOT:
            candidate_dirs.append(Path(settings.STATIC_ROOT) / "posters")

        def locate_file(fn):
            for d in candidate_dirs:
                p = d / fn
                if p.exists():
                    return p
            return None

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for obj in queryset:
                png_fn = f"poster_{obj.number}.png"
                jpg_fn = f"poster_{obj.number}.jpg"
                png_p = locate_file(png_fn)
                jpg_p = locate_file(jpg_fn)
                if png_p:
                    zf.write(str(png_p), arcname=f"png/{png_fn}")
                if jpg_p:
                    zf.write(str(jpg_p), arcname=f"jpg/{jpg_fn}")

        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @admin.action(description="Download selected posters as ZIP bundle")
    def download_selected_as_zip(self, request, queryset):
        return self._build_zip_response(queryset, "infini_selected_posters.zip")

    @admin.action(description="Download all 20 posters as ZIP bundle")
    def download_all_as_zip(self, request, queryset):
        all_posters = SocialPoster.objects.all().order_by("number")
        return self._build_zip_response(all_posters, "infini_all_20_social_posters.zip")


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
    AnonymousHumanizerUsage,
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
admin_site.register(SocialPoster, SocialPosterAdmin)
