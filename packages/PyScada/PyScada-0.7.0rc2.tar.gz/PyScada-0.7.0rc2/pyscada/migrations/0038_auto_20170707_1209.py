# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-07 12:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0037_auto_20170418_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backgroundprocess',
            name='parent_process',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pyscada.BackgroundProcess'),
        ),
        migrations.AlterField(
            model_name='backgroundprocess',
            name='pid',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='backgroundprocess',
            name='process_class',
            field=models.CharField(blank=True, default=b'pyscada.utils.scheduler.Process', help_text=b'from pyscada.utils.scheduler import Process', max_length=400),
        ),
        migrations.AlterField(
            model_name='backgroundprocess',
            name='process_class_kwargs',
            field=models.CharField(blank=True, default=b'{}', help_text=b'arguments in json format will be passed as kwargs while the init of the process instance, example: {"keywordA":"value1", "keywordB":7}', max_length=400),
        ),
    ]
