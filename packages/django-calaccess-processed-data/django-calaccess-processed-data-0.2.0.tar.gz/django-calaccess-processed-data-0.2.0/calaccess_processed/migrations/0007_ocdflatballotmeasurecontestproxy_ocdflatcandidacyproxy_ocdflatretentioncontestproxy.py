# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-23 15:00
from __future__ import unicode_literals

import calaccess_processed.models.proxies.opencivicdata.base
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0002_auto_20170731_2047'),
        ('calaccess_processed', '0006_ocdpersonidentifierproxy'),
    ]

    operations = [
        migrations.CreateModel(
            name='OCDFlatBallotMeasureContestProxy',
            fields=[
            ],
            options={
                # 'indexes': [],
                'proxy': True,
            },
            bases=('elections.ballotmeasurecontest', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDFlatCandidacyProxy',
            fields=[
            ],
            options={
                # 'indexes': [],
                'proxy': True,
            },
            bases=('elections.candidacy', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDFlatRetentionContestProxy',
            fields=[
            ],
            options={
                # 'indexes': [],
                'proxy': True,
            },
            bases=('elections.retentioncontest', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
    ]
