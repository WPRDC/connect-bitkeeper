# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-13 18:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bitkeeper', '0002_auto_20180213_1856'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fire_department',
            old_name='address_city',
            new_name='city',
        ),
    ]
