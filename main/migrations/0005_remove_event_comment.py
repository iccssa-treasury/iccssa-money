# Generated by Django 4.2.1 on 2023-06-26 16:02

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_event_delete_decision"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="comment",
        ),
    ]
