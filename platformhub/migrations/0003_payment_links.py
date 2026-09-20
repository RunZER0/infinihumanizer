from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("platformhub", "0002_assurancejob"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentrecord",
            name="consultation",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payments", to="platformhub.consultation"),
        ),
        migrations.AddField(
            model_name="paymentrecord",
            name="assurance_job",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payments", to="platformhub.assurancejob"),
        ),
    ]
