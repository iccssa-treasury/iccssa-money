# Generated by Django 4.2.1 on 2023-07-01 22:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
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
        migrations.AlterField(
            model_name="application",
            name="level",
            field=models.IntegerField(
                choices=[
                    (-1, "已取消"),
                    (0, "已完成"),
                    (1, "待付款"),
                    (2, "待财务审批"),
                    (3, "待主席审批"),
                    (4, "待部门审批"),
                    (5, "待成员审批"),
                ],
                default=5,
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="action",
            field=models.IntegerField(
                choices=[
                    (0, "评论"),
                    (1, "批准"),
                    (2, "驳回"),
                    (3, "创建"),
                    (4, "撤销"),
                    (5, "完成"),
                ],
                default=0,
            ),
        ),
    ]