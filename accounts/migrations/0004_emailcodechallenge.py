from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_profile_currency_profile_current_active_devices_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailCodeChallenge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("code_hash", models.CharField(blank=True, max_length=255)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("last_sent_at", models.DateTimeField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
