# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-07 20:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0005_auto_20160407_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendar',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]