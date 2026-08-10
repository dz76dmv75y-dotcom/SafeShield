"""Sync Profile model with OTP tracking fields.

Adds missing otp tracking fields and adjusts otp_code length.
Removes the obsolete `otp` field added by a prior migration.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_profile_otp_alter_profile_user_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='otp_code',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='profile',
            name='otp_attempts',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='otp_last_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='otp_resend_count',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='otp_resend_window_started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='profile',
            name='otp',
        ),
    ]
