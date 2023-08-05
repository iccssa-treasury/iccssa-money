# Generated by Django 4.2.1 on 2023-07-01 22:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="department",
            field=models.IntegerField(
                choices=[
                    (0, "未分配"),
                    (1, "主席团"),
                    (2, "秘书处"),
                    (3, "财务处"),
                    (4, "事业部"),
                    (5, "媒体部"),
                    (6, "赞助部"),
                    (7, "文艺部"),
                    (8, "文化部"),
                    (9, "外联部"),
                    (10, "体育部"),
                ],
                default=0,
            ),
        ),
    ]