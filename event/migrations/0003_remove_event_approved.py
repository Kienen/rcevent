# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-23 23:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_auto_20160423_1412'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='approved',
        ),
    ]