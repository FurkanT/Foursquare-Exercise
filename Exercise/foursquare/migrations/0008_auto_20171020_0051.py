# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-19 21:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foursquare', '0007_auto_20171019_1829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationsearch',
            name='offset',
            field=models.CharField(default=1, max_length=5),
        ),
    ]