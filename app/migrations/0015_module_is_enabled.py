# Generated by Django 4.0.5 on 2022-07-27 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0014_remove_role_is_admin_remove_role_is_member_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="module",
            name="is_enabled",
            field=models.BooleanField(default=False),
        ),
    ]