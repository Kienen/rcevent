# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-08 22:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0006_calendar_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='owner',
        ),
    ]