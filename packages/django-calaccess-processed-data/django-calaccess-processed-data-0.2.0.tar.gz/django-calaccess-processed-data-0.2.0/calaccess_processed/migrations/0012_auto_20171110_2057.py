# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-10 20:57
from __future__ import unicode_literals

import calaccess_processed.models.proxies.opencivicdata.base
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20171005_2028'),
        ('campaign_finance', '0001_initial'),
        ('calaccess_processed', '0011_auto_20171023_1620'),
    ]

    operations = [
        migrations.CreateModel(
            name='OCDCommitteeIdentifierProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.committeeidentifier', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDCommitteeNameProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.committeename', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDCommitteeProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.committee', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDCommitteeSourceProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.committeesource', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDCommitteeTypeProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.committeetype', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDFilingActionProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.filingaction', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDFilingActionSummaryAmountProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.filingactionsummaryamount', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDFilingIdentifierProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.filingidentifier', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDFilingProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.filing', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDFilingSourceProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.filingsource', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDJurisdictionProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.jurisdiction', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDTransactionIdentifierProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.transactionidentifier', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.CreateModel(
            name='OCDTransactionProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('campaign_finance.transaction', calaccess_processed.models.proxies.opencivicdata.base.OCDProxyModelMixin),
        ),
        migrations.AddField(
            model_name='form460filing',
            name='statement_type',
            field=models.CharField(default='', help_text='Type of statement, e.g., "Quarterly", "Semi-Annual", Pre-Election (from CVR_CAMPAIGN_DISCLOSURE.STMT_TYPE)', max_length=50, verbose_name='statement type'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='form460filingversion',
            name='statement_type',
            field=models.CharField(default='', help_text='Type of statement, e.g., "Quarterly", "Semi-Annual", Pre-Election (from CVR_CAMPAIGN_DISCLOSURE.STMT_TYPE)', max_length=50, verbose_name='statement type'),
            preserve_default=False,
        ),
    ]
