# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-19 13:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0041_update_protocol_id'),
        ('phant', '0003_auto_20170225_0908'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtendedPhantDevice',
            fields=[
            ],
            options={
                'verbose_name': 'Phant Device',
                'proxy': True,
                'verbose_name_plural': 'Phant Devices',
                'indexes': [],
            },
            bases=('pyscada.device',),
        ),
        migrations.CreateModel(
            name='ExtendedPhantVariable',
            fields=[
            ],
            options={
                'verbose_name': 'Phant Variable',
                'proxy': True,
                'verbose_name_plural': 'Phant Variables',
                'indexes': [],
            },
            bases=('pyscada.variable',),
        ),
    ]
