# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-23 18:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bitkeeper', '0021_auto_20180223_1750'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pghcouncildistrict',
            name='police_department',
        ),
        migrations.AddField(
            model_name='policedepartment',
            name='pittsburgh_council_district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bitkeeper.PGHCouncilDistrict'),
        ),
    ]
