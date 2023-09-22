# Generated by Django 4.2.1 on 2023-08-22 20:00

from django.db import migrations, models
import main.models

def update_income_received(apps, schema_editor):
    Income = apps.get_model("main", "Income")
    Receipt = apps.get_model("main", "Receipt")
    for receipt in Receipt.objects.all():
        receipt.currency = receipt.income.currency
        receipt.save()
    for income in Income.objects.all():
        income.received = {
            "英镑": float(income.received) if income.currency == 0 else 0,
            "人民币": float(income.received) if income.currency == 1 else 0,
        }
        income.save()

class Migration(migrations.Migration):
    dependencies = [
        ("main", "0005_income_receipt"),
    ]

    operations = [
        migrations.AddField(
            model_name="receipt",
            name="currency",
            field=models.IntegerField(choices=[(0, "英镑"), (1, "人民币")], default=0),
        ),
        migrations.AlterField(
            model_name="income",
            name="received",
            field=models.JSONField(default=main.models.received_json_default),
        ),
        migrations.RunPython(update_income_received),
    ]
