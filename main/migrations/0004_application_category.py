# Generated by Django 4.2.1 on 2023-06-04 22:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0003_approval_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="category",
            field=models.CharField(default="", max_length=10),
            preserve_default=False,
        ),
    ]
