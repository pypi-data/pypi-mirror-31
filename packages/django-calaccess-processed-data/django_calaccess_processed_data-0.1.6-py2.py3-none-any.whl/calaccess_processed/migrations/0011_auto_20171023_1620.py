# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-23 16:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_processed', '0010_auto_20171013_1838'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fileridvalue',
            options={'verbose_name': 'Filer ID value'},
        ),
        migrations.AlterModelOptions(
            name='filingidvalue',
            options={'verbose_name': 'Filing ID value'},
        ),
        migrations.AlterModelOptions(
            name='processeddatafile',
            options={'ordering': ('-version_id', 'file_name'), 'verbose_name': 'TRACKING: CAL-ACCESS processed data file'},
        ),
    ]
