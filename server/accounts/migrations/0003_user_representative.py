# Generated by Django 4.2.1 on 2023-08-08 19:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_user_department"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="representative",
            field=models.BooleanField(default=False),
        ),
    ]