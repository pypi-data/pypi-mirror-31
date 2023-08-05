#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Proxy models for augmenting our source data tables with methods useful for processing.
"""
from __future__ import unicode_literals
from ..base import OCDProxyModelMixin
from opencivicdata.core.models import Organization
from calaccess_processed.managers import OCDPartyManager


class OCDPartyProxy(Organization, OCDProxyModelMixin):
    """
    A proxy on the OCD Organization model with helper methods for interacting with political parties.
    """
    objects = OCDPartyManager()

    class Meta:
        """
        Make this a proxy model.
        """
        proxy = True

    def is_unknown(self):
        """
        Returns whether or not the provided party is unknown.
        """
        return self.name == 'UNKNOWN'
