# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-13 05:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0004_auto_20161011_0329'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, max_length=255)),
                ('url', models.TextField(blank=True, max_length=255)),
                ('type', models.IntegerField()),
                ('number', models.IntegerField()),
            ],
        ),
    ]
