# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-24 03:41
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.postgres.operations import CreateExtension

class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_processed', '0007_ocdflatballotmeasurecontestproxy_ocdflatcandidacyproxy_ocdflatretentioncontestproxy'),
    ]

    operations = [
        CreateExtension('intarray')
    ]
