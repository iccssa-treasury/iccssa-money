# Generated by Django 4.2.1 on 2023-09-22 20:02

from django.db import migrations, models

def update_integer_amounts(apps, schema_editor):
    Application = apps.get_model("main", "Application")
    Income = apps.get_model("main", "Income")
    Receipt = apps.get_model("main", "Receipt")
    for application in Application.objects.all():
        application.amount = int(round(application.amount * 100))
        application.save()
    for income in Income.objects.all():
        income.amount = int(round(income.amount * 100))
        income.received = {label: int(amount * 100) for label, amount in income.received.items()}
        income.save()
    for receipt in Receipt.objects.all():
        receipt.amount = int(round(receipt.amount * 100))
        receipt.save()

class Migration(migrations.Migration):
    dependencies = [
        ("main", "0006_receipt_currency_alter_income_received"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="amount",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="income",
            name="amount",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="receipt",
            name="amount",
            field=models.IntegerField(),
        ),
        migrations.RunPython(update_integer_amounts),
    ]
