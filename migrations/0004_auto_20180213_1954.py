# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-13 19:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bitkeeper', '0003_auto_20180213_1858'),
    ]

    operations = [
        migrations.CreateModel(
            name='CouncilMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='FireDepartment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('street_address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('municipality', models.CharField(max_length=100, unique=True)),
                ('cog', models.CharField(max_length=100)),
                ('congressional_district', models.SmallIntegerField()),
                ('municipal_web_site', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PoliceDepartment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('police_station', models.CharField(max_length=100, unique=True)),
                ('street_address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('chief_name', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=50)),
                ('chief_email', models.CharField(max_length=90)),
            ],
        ),
        migrations.DeleteModel(
            name='fire_department',
        ),
        migrations.AddField(
            model_name='councilmember',
            name='municipality',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bitkeeper.Municipality'),
        ),
    ]
