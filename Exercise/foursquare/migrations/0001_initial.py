# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-09 11:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location_search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_text', models.CharField(default='I am looking for..', max_length=100)),
                ('location_text', models.CharField(default='Location', max_length=50)),
                ('search_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
    ]
