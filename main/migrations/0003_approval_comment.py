# Generated by Django 4.2.1 on 2023-06-04 22:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_alter_payee_account_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="approval",
            name="comment",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]