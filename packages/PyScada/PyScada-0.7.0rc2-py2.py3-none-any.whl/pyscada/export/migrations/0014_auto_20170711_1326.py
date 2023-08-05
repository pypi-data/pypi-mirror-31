# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-11 13:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('export', '0013_auto_20170711_0729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporttask',
            name='file_format',
            field=models.CharField(choices=[('hdf5', 'Hierarchical Data Format Version 5'), ('mat', 'Matlab\xae mat v7.3 compatible file'), ('CSV_EXCEL', 'Microsoft\xae Excel\xae compatible csv file')], default='hdf5', max_length=400),
        ),
        migrations.AlterField(
            model_name='scheduledexporttask',
            name='export_period',
            field=models.PositiveSmallIntegerField(choices=[(1, '1 Day'), (2, '2 Days (on every even Day of the year)'), (7, '7 Days (on Mondays)'), (14, '14 Days'), (30, '30 Days')], default=0),
        ),
        migrations.AlterField(
            model_name='scheduledexporttask',
            name='file_format',
            field=models.CharField(choices=[('hdf5', 'Hierarchical Data Format Version 5'), ('mat', 'Matlab\xae mat v7.3 compatible file'), ('CSV_EXCEL', 'Microsoft\xae Excel\xae compatible csv file')], default='hdf5', max_length=400),
        ),
    ]
