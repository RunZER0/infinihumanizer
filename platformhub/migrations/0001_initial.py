# Generated for the InfiniAI platform foundation.
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("slug", models.SlugField(max_length=180, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="ServiceRequest",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reference", models.CharField(blank=True, max_length=32, unique=True)),
                ("full_name", models.CharField(max_length=180)),
                ("email", models.EmailField(max_length=254)),
                ("company", models.CharField(blank=True, max_length=180)),
                ("service_family", models.CharField(max_length=80)),
                ("service_code", models.CharField(max_length=100)),
                ("title", models.CharField(max_length=220)),
                ("objective", models.TextField()),
                ("audience", models.TextField(blank=True)),
                ("scope", models.TextField()),
                ("deliverable", models.TextField()),
                ("research_depth", models.CharField(choices=[("none", "No external research"), ("light", "Light research"), ("standard", "Standard research"), ("deep", "Deep research")], default="standard", max_length=20)),
                ("turnaround", models.CharField(choices=[("flexible", "Flexible"), ("standard", "Standard"), ("priority", "Priority")], default="standard", max_length=20)),
                ("budget_band", models.CharField(blank=True, max_length=80)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("estimate_low", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("estimate_high", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("status", models.CharField(choices=[("new", "New"), ("scoping", "Scoping"), ("quoted", "Quoted"), ("active", "Active"), ("review", "Client review"), ("delivered", "Delivered"), ("closed", "Closed")], default="new", max_length=20)),
                ("source", models.CharField(default="website", max_length=40)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="requests", to="platformhub.organization")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="infini_requests", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Consultation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reference", models.CharField(blank=True, max_length=32, unique=True)),
                ("full_name", models.CharField(max_length=180)),
                ("email", models.EmailField(max_length=254)),
                ("company", models.CharField(blank=True, max_length=180)),
                ("topic", models.TextField()),
                ("fee_usd", models.DecimalField(decimal_places=2, default=50, max_digits=10)),
                ("status", models.CharField(choices=[("requested", "Requested"), ("scheduled", "Scheduled"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="requested", max_length=20)),
                ("scheduled_for", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("request", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="consultations", to="platformhub.servicerequest")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Quote",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("number", models.CharField(blank=True, max_length=32, unique=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("sent", "Sent"), ("accepted", "Accepted"), ("expired", "Expired"), ("declined", "Declined")], default="draft", max_length=20)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("discount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("tax", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("notes", models.TextField(blank=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="quotes", to="platformhub.servicerequest")),
            ],
        ),
        migrations.CreateModel(
            name="QuoteItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=220)),
                ("description", models.TextField(blank=True)),
                ("quantity", models.DecimalField(decimal_places=2, default=1, max_digits=8)),
                ("unit_price", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("quote", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="platformhub.quote")),
            ],
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("number", models.CharField(blank=True, max_length=32, unique=True)),
                ("email", models.EmailField(max_length=254)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("open", "Open"), ("part_paid", "Part paid"), ("paid", "Paid"), ("void", "Void")], default="open", max_length=20)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("amount_due", models.DecimalField(decimal_places=2, max_digits=12)),
                ("amount_paid", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("due_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("quote", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="invoices", to="platformhub.quote")),
                ("request", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="invoices", to="platformhub.servicerequest")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="PaymentRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("provider", models.CharField(default="paystack", max_length=40)),
                ("reference", models.CharField(max_length=120, unique=True)),
                ("source_type", models.CharField(blank=True, max_length=50)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("currency", models.CharField(max_length=3)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed"), ("abandoned", "Abandoned"), ("refunded", "Refunded")], default="pending", max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("original_description", models.TextField(blank=True)),
                ("normalized_family", models.CharField(blank=True, max_length=80)),
                ("normalized_service_code", models.CharField(blank=True, max_length=100)),
                ("legacy", models.BooleanField(default=False)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("invoice", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payments", to="platformhub.invoice")),
                ("request", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payments", to="platformhub.servicerequest")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-paid_at", "-created_at"]},
        ),
        migrations.CreateModel(
            name="Deliverable",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=220)),
                ("kind", models.CharField(blank=True, max_length=80)),
                ("status", models.CharField(choices=[("planned", "Planned"), ("in_progress", "In progress"), ("review", "Review"), ("approved", "Approved"), ("delivered", "Delivered")], default="planned", max_length=20)),
                ("version", models.PositiveIntegerField(default=1)),
                ("external_url", models.URLField(blank=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="deliverables", to="platformhub.servicerequest")),
            ],
        ),
    ]
