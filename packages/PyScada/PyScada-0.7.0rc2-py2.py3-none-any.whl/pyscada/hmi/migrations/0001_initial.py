# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chart',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=400)),
                ('x_axis_label', models.CharField(default=b'', max_length=400, blank=True)),
                ('x_axis_ticks', models.PositiveSmallIntegerField(default=6)),
                ('y_axis_label', models.CharField(default=b'', max_length=400, blank=True)),
                ('y_axis_min', models.FloatField(default=0)),
                ('y_axis_max', models.FloatField(default=100)),
                ('variables', models.ManyToManyField(to='pyscada.Variable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChartSet',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('distribution', models.PositiveSmallIntegerField(default=0, choices=[(0, b'side by side (1/2)'), (1, b'side by side (2/3|1/3)'), (2, b'side by side (1/3|2/3)')])),
                ('chart_1', models.ForeignKey(related_name='chart_1', verbose_name=b'left Chart', blank=True, to='hmi.Chart', null=True)),
                ('chart_2', models.ForeignKey(related_name='chart_2', verbose_name=b'right Chart', blank=True, to='hmi.Chart', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.SlugField(max_length=80, verbose_name=b'variable name')),
                ('R', models.PositiveSmallIntegerField(default=0)),
                ('G', models.PositiveSmallIntegerField(default=0)),
                ('B', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ControlItem',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('label', models.CharField(default=b'', max_length=400)),
                ('position', models.PositiveSmallIntegerField(default=0)),
                ('type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'label blue'), (1, b'label light blue'), (2, b'label ok'), (3, b'label warning'), (4, b'label alarm'), (7, b'label alarm inverted'), (5, b'Control Element'), (6, b'Display Value')])),
                ('variable', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Variable', null=True)),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ControlPanel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=400)),
                ('items', models.ManyToManyField(to='hmi.ControlItem', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomHTMLPanel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=400, blank=True)),
                ('html', models.TextField()),
                ('variables', models.ManyToManyField(to='pyscada.Variable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupDisplayPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('charts', models.ManyToManyField(to='hmi.Chart', blank=True)),
                ('control_items', models.ManyToManyField(to='hmi.ControlItem', blank=True)),
                ('custom_html_panels', models.ManyToManyField(to='hmi.CustomHTMLPanel', blank=True)),
                ('hmi_group', models.OneToOneField(to='auth.Group')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HMIVariable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(default=b'', max_length=80, verbose_name=b'variable short name')),
                ('chart_line_thickness', models.PositiveSmallIntegerField(default=3, choices=[(3, b'3Px')])),
                ('chart_line_color', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='hmi.Color', null=True)),
                ('hmi_variable', models.OneToOneField(to='pyscada.Variable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=400)),
                ('link_title', models.SlugField(default=b'', max_length=80)),
                ('position', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SlidingPanelMenu',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=400)),
                ('position', models.PositiveSmallIntegerField(default=0, choices=[(0, b'Control Menu'), (1, b'left'), (2, b'right')])),
                ('visable', models.BooleanField(default=True)),
                ('control_panel', models.ForeignKey(default=None, blank=True, to='hmi.ControlPanel', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=400)),
                ('description', models.TextField(default=b'', null=True, verbose_name=b'Description')),
                ('link_title', models.SlugField(default=b'', max_length=80)),
                ('logo', models.ImageField(upload_to=b'img/', verbose_name=b'Overview Picture', blank=True)),
                ('visable', models.BooleanField(default=True)),
                ('position', models.PositiveSmallIntegerField(default=0)),
                ('pages', models.ManyToManyField(to='hmi.Page')),
                ('sliding_panel_menus', models.ManyToManyField(to='hmi.SlidingPanelMenu', blank=True)),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=400, blank=True)),
                ('row', models.PositiveSmallIntegerField(default=0, choices=[(0, b'1. row'), (1, b'2. row'), (2, b'3. row'), (3, b'4. row'), (4, b'5. row'), (5, b'6. row'), (6, b'7. row'), (7, b'8. row'), (8, b'9. row'), (9, b'10. row'), (10, b'11. row'), (11, b'12. row')])),
                ('col', models.PositiveSmallIntegerField(default=0, choices=[(0, b'1. col'), (1, b'2. col'), (2, b'3. col'), (3, b'4. col')])),
                ('size', models.PositiveSmallIntegerField(default=4, choices=[(4, b'page width'), (3, b'3/4 page width'), (2, b'1/2 page width'), (1, b'1/4 page width')])),
                ('visable', models.BooleanField(default=True)),
                ('chart', models.ForeignKey(default=None, blank=True, to='hmi.Chart', null=True)),
                ('chart_set', models.ForeignKey(default=None, blank=True, to='hmi.ChartSet', null=True)),
                ('control_panel', models.ForeignKey(default=None, blank=True, to='hmi.ControlPanel', null=True)),
                ('custom_html_panel', models.ForeignKey(default=None, blank=True, to='hmi.CustomHTMLPanel', null=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='hmi.Page', null=True)),
            ],
            options={
                'ordering': ['row', 'col'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='groupdisplaypermission',
            name='pages',
            field=models.ManyToManyField(to='hmi.Page', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupdisplaypermission',
            name='sliding_panel_menus',
            field=models.ManyToManyField(to='hmi.SlidingPanelMenu', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupdisplaypermission',
            name='views',
            field=models.ManyToManyField(to='hmi.View', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupdisplaypermission',
            name='widgets',
            field=models.ManyToManyField(to='hmi.Widget', blank=True),
            preserve_default=True,
        ),
    ]
