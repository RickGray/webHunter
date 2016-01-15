#!/usr/bin/env python
# coding: utf-8

import re
import urlparse

import thirdparty.requests as requests

from lib.core.engines import Engine
from lib.core.engines import EngineError
from lib.core.engines import EngineConnectionError
from lib.utils.agents import random_user_agent
from lib.utils.common import dict2query
from lib.utils.common import query2dict
from lib.utils.common import patch_url
from lib.parse.confparse import conf


_NAME = 'ZoomEye'
_SITE = 'https://www.zoomeye.org/'
_DESC = ('ZoomEye Search, a search engine for cyberspace, powered by Knownsec. '
         'It helps you explore devices and websites in cyberspace.')


class ZoomEye(Engine):

    def __init__(self):
        self.maximum = 1000
        self.pmax = 10

        self.sreq = requests.Session()
        self.sreq.headers['User-Agent'] = random_user_agent()

        super(ZoomEye, self).__init__(_NAME, _SITE, _DESC)

    def _init(self):
        try:
            self.sreq.get(self._site)
        except Exception, ex:
            err = 'Failed to connect "%s", ' % self._site
            err += str(ex)
            raise EngineConnectionError(err)

    def _is_over_limit(self, link, limit):
        q = urlparse.urlparse(link).query
        d = query2dict(q)

        return (int(d['p']) * int(self.pmax)) <= limit

    @staticmethod
    def _fetch_next_page(prev_link, content):
        match = re.search(r'<a href="(?P<next>[^">]*)">(?:下一页|Next)', content)
        next_link = match.group('next') if match else ''
        if next_link:
            next_link = patch_url(prev_link, next_link)

        return next_link

    def _fetch_page_content(self, link):
        try:
            content = self.sreq.get(link).content
        except any:
            content = ''
            # err = str(ex)

        return content

    def _process_redirection(self, res):
        # TODO
        pass

    def search(self, keyword, limit, search_type=''):
        self._init()

        if limit > self.maximum:
            limit = self.maximum
        d = {
            'q': keyword,
            'p': str(1),
            't': search_type if search_type in ['web', 'host'] else 'web',
        }

        q = dict2query(d)
        link = urlparse.urljoin(self._site, '/search?' + q)
        while self._is_over_limit(link, limit):
            content = self._fetch_page_content(link)
            link = self._fetch_next_page(link, content)
            if not link:
                break
            yield content
