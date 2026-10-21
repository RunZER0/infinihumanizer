from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("humanizer", "0002_anonymoushumanizerusage"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientmessage",
            name="attachments",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name="clientmessage",
            name="body",
            field=models.TextField(blank=True),
        ),
    ]
