#!/usr/bin/env python
# coding: utf-8


class Engine(object):

    def __init__(self, i_name, i_site, i_desc):
        self._name = i_name
        self._site = i_site
        self._desc = i_desc

    def __unicode__(self):
        return u'name=%s, site=%s' % (self._name, self._site)


class EngineError(Exception):
    pass


class EngineConnectionError(EngineError):
    pass


from .google import Google
from .baidu import Baidu
from .censys import Censys
