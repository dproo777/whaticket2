# Generated by Django 4.0.5 on 2022-07-21 07:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_rename_hourly_limit_per_month_compensation_expected_hours_per_week_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='organization',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.organization'),
        ),
    ]
