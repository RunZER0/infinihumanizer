import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("platformhub", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AssuranceJob",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reference", models.CharField(blank=True, max_length=32, unique=True)),
                ("title", models.CharField(max_length=220)),
                ("content", models.TextField()),
                ("instructions", models.TextField(blank=True)),
                ("level", models.CharField(default="quick", max_length=30)),
                ("status", models.CharField(choices=[("awaiting_payment", "Awaiting payment"), ("queued", "Queued"), ("reviewing", "Reviewing"), ("ready", "Ready"), ("cancelled", "Cancelled")], default="awaiting_payment", max_length=30)),
                ("originality_score", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("result_summary", models.TextField(blank=True)),
                ("result_report", models.TextField(blank=True)),
                ("payment_reference", models.CharField(blank=True, max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assurance_jobs", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
