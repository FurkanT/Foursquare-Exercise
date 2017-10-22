# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-19 15:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foursquare', '0006_auto_20171012_1142'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationsearch',
            name='offset',
            field=models.CharField(default=0, max_length=5),
        ),
        migrations.AlterField(
            model_name='locationsearch',
            name='food',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='locationsearch',
            name='location',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='locationsearch',
            name='search_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]