from django.contrib import admin
from .models import (
    Organization, ServiceRequest, Consultation, Quote, QuoteItem,
    Invoice, PaymentRecord, Deliverable, DeliverableFeedback, AssuranceJob,
    SocialPoster,
)


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "service_family", "email", "status", "estimate_low", "estimate_high", "created_at")
    list_filter = ("service_family", "status", "research_depth", "turnaround")
    search_fields = ("reference", "title", "email", "company")
    readonly_fields = ("reference", "created_at", "updated_at")


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("number", "request", "status", "currency", "total", "created_at")
    list_filter = ("status", "currency")
    inlines = [QuoteItemInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "email", "status", "currency", "amount_due", "amount_paid", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("number", "email", "description")


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("reference", "email", "amount", "currency", "status", "normalized_family", "legacy", "paid_at")
    list_filter = ("status", "currency", "normalized_family", "legacy")
    search_fields = ("reference", "email", "original_description")


admin.site.register(Organization)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("reference", "full_name", "email", "company", "created_at")
    list_filter = ("created_at",)
    search_fields = ("reference", "full_name", "email", "company", "topic")
admin.site.register(Deliverable)
admin.site.register(DeliverableFeedback)
admin.site.register(AssuranceJob)


@admin.register(SocialPoster)
class PlatformhubSocialPosterAdmin(admin.ModelAdmin):
    list_display = ("number", "tag_badge", "eyebrow", "style", "turnaround", "created_at")
    list_filter = ("style",)
    search_fields = ("number", "tag_badge", "eyebrow", "headline_pre", "headline_span", "outcome")
