import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


def _short(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


class Organization(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("scoping", "Scoping"),
        ("quoted", "Quoted"),
        ("active", "Active"),
        ("review", "Client review"),
        ("delivered", "Delivered"),
        ("closed", "Closed"),
    ]
    RESEARCH_CHOICES = [
        ("none", "No external research"),
        ("light", "Light research"),
        ("standard", "Standard research"),
        ("deep", "Deep research"),
    ]
    TURNAROUND_CHOICES = [
        ("flexible", "Flexible"),
        ("standard", "Standard"),
        ("priority", "Priority"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=32, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="infini_requests")
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name="requests")
    full_name = models.CharField(max_length=180)
    email = models.EmailField()
    company = models.CharField(max_length=180, blank=True)
    service_family = models.CharField(max_length=80)
    service_code = models.CharField(max_length=100)
    title = models.CharField(max_length=220)
    objective = models.TextField()
    audience = models.TextField(blank=True)
    scope = models.TextField()
    deliverable = models.TextField()
    research_depth = models.CharField(max_length=20, choices=RESEARCH_CHOICES, default="standard")
    turnaround = models.CharField(max_length=20, choices=TURNAROUND_CHOICES, default="standard")
    budget_band = models.CharField(max_length=80, blank=True)
    currency = models.CharField(max_length=3, default="USD")
    estimate_low = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimate_high = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    source = models.CharField(max_length=40, default="website")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = _short("INF")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} — {self.title}"


class Consultation(models.Model):
    STATUS_CHOICES = [("requested", "Requested"), ("scheduled", "Scheduled"), ("completed", "Completed"), ("cancelled", "Cancelled")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=32, unique=True, blank=True)
    request = models.ForeignKey(ServiceRequest, null=True, blank=True, on_delete=models.SET_NULL, related_name="consultations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    full_name = models.CharField(max_length=180)
    email = models.EmailField()
    company = models.CharField(max_length=180, blank=True)
    topic = models.TextField()
    fee_usd = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    scheduled_for = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = _short("CON")
        super().save(*args, **kwargs)


class Quote(models.Model):
    STATUS_CHOICES = [("draft", "Draft"), ("sent", "Sent"), ("accepted", "Accepted"), ("expired", "Expired"), ("declined", "Declined")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=32, unique=True, blank=True)
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="quotes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    currency = models.CharField(max_length=3, default="USD")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = _short("Q")
        super().save(*args, **kwargs)


class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="items")
    label = models.CharField(max_length=220)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class Invoice(models.Model):
    STATUS_CHOICES = [("draft", "Draft"), ("open", "Open"), ("part_paid", "Part paid"), ("paid", "Paid"), ("void", "Void")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=32, unique=True, blank=True)
    request = models.ForeignKey(ServiceRequest, null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices")
    quote = models.ForeignKey(Quote, null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    currency = models.CharField(max_length=3, default="USD")
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = _short("INV")
        if self.amount_paid >= self.amount_due:
            self.status = "paid"
        elif self.amount_paid > 0:
            self.status = "part_paid"
        super().save(*args, **kwargs)


class PaymentRecord(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("success", "Success"), ("failed", "Failed"), ("abandoned", "Abandoned"), ("refunded", "Refunded")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    request = models.ForeignKey(ServiceRequest, null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    provider = models.CharField(max_length=40, default="paystack")
    reference = models.CharField(max_length=120, unique=True)
    source_type = models.CharField(max_length=50, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    email = models.EmailField(blank=True)
    original_description = models.TextField(blank=True)
    normalized_family = models.CharField(max_length=80, blank=True)
    normalized_service_code = models.CharField(max_length=100, blank=True)
    legacy = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_at", "-created_at"]


class Deliverable(models.Model):
    STATUS_CHOICES = [("planned", "Planned"), ("in_progress", "In progress"), ("review", "Review"), ("approved", "Approved"), ("delivered", "Delivered")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="deliverables")
    title = models.CharField(max_length=220)
    kind = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")
    version = models.PositiveIntegerField(default=1)
    external_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AssuranceJob(models.Model):
    STATUS_CHOICES = [
        ("awaiting_payment", "Awaiting payment"),
        ("queued", "Queued"),
        ("reviewing", "Reviewing"),
        ("ready", "Ready"),
        ("cancelled", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=32, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assurance_jobs")
    title = models.CharField(max_length=220)
    content = models.TextField()
    instructions = models.TextField(blank=True)
    level = models.CharField(max_length=30, default="quick")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="awaiting_payment")
    originality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    result_summary = models.TextField(blank=True)
    result_report = models.TextField(blank=True)
    payment_reference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = _short("CHK")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} — {self.title}"
