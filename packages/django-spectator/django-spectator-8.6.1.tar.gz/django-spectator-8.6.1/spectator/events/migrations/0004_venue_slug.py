# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-01 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spectator_events', '0003_auto_20171101_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='slug',
            field=models.SlugField(blank=True, default='a', max_length=10),
            preserve_default=False,
        ),
    ]
