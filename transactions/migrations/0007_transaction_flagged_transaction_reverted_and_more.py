# Generated by Django 5.1.2 on 2024-10-23 13:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_notification'),
        ('transactions', '0006_alter_transaction_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='flagged',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='transaction',
            name='reverted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='transaction',
            name='sender_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_transactions', to='accounts.userbankaccount'),
        ),
    ]
