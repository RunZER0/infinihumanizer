from django.contrib import admin
from .models import (
    Organization, ServiceRequest, Consultation, Quote, QuoteItem,
    Invoice, PaymentRecord, Deliverable, AssuranceJob,
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
admin.site.register(Consultation)
admin.site.register(Deliverable)

admin.site.register(AssuranceJob)
