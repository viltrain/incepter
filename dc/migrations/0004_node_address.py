# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-13 13:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dc', '0003_auto_20160512_0829'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='address',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]
