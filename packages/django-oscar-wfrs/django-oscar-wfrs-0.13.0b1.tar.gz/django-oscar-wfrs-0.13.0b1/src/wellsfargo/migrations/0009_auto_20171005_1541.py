# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-05 19:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wellsfargo', '0008_fraudscreenresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fraudscreenresult',
            name='decision',
            field=models.CharField(choices=[('REJECT', 'Transaction was rejected'), ('ACCEPT', 'Transaction was accepted'), ('ERROR', 'Error occurred while running fraud screen'), ('REVIEW', 'Transaction was flagged for manual review')], max_length=25, verbose_name='Decision'),
        ),
        migrations.AlterField(
            model_name='fraudscreenresult',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wfrs_fraud_screen_results', to='order.Order'),
        ),
    ]
