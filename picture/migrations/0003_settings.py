# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-11 00:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0002_auto_20161010_2322'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='picture.Picture')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
