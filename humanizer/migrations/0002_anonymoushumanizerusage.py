from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("humanizer", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnonymousHumanizerUsage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("day", models.DateField()),
                ("fingerprint", models.CharField(max_length=64)),
                ("words_used", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-day", "-updated_at"]},
        ),
        migrations.AddConstraint(
            model_name="anonymoushumanizerusage",
            constraint=models.UniqueConstraint(
                fields=("day", "fingerprint"),
                name="humanizer_anon_usage_day_fingerprint",
            ),
        ),
    ]
