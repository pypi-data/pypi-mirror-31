# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-24 12:49
from __future__ import unicode_literals
from pyscada.phant import PROTOCOL_ID

from django.db import migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    DeviceProtocol = apps.get_model("pyscada", "DeviceProtocol")
    db_alias = schema_editor.connection.alias
    if not DeviceProtocol.objects.using(db_alias).filter(pk=PROTOCOL_ID):
        DeviceProtocol.objects.using(db_alias).bulk_create([
            DeviceProtocol(pk=PROTOCOL_ID,
                           protocol='phant',
                           description='Phant Webservice Device',
                           app_name='pyscada.phant',
                           device_class='None',
                           daq_daemon=False,
                           single_thread=True),
        ])


def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    DeviceProtocol = apps.get_model("pyscada", "DeviceProtocol")
    db_alias = schema_editor.connection.alias
    DeviceProtocol.objects.using(db_alias).filter(pk=PROTOCOL_ID).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('phant', '0002_auto_20161013_1239'),
        ('pyscada', '0036_auto_20170224_1245'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
