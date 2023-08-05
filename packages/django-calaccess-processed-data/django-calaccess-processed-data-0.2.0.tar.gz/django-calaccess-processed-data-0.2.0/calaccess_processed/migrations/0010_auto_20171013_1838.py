# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-13 18:38
from __future__ import unicode_literals

import calaccess_processed
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_processed', '0009_auto_20171003_0124'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessedDataZip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zip_archive', models.FileField(help_text='An archived zip of processed files', max_length=255, upload_to=calaccess_processed.archive_directory_path, verbose_name='zip archive')),
                ('zip_size', models.BigIntegerField(default=0, help_text='The expected size (in bytes) of the zip ', verbose_name='size of zip (in bytes)')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, help_text='Date and time when zip was created', verbose_name='date and time zip created')),
            ],
            options={
                'verbose_name': 'TRACKING: CAL-ACCESS processed data zip',
                'ordering': ('-version', 'zip_archive'),
            },
        ),
        migrations.RemoveField(
            model_name='processeddataversion',
            name='zip_archive',
        ),
        migrations.RemoveField(
            model_name='processeddataversion',
            name='zip_size',
        ),
        migrations.AddField(
            model_name='processeddatazip',
            name='version',
            field=models.ForeignKey(help_text='Foreign key referencing the processed version of CAL-ACCESS', on_delete=django.db.models.deletion.CASCADE, related_name='zips', to='calaccess_processed.ProcessedDataVersion', verbose_name='processed data version'),
        ),
        migrations.AlterUniqueTogether(
            name='processeddatazip',
            unique_together=set([('version', 'zip_archive')]),
        ),
    ]
