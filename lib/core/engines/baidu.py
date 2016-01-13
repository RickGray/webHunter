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


_NAME = 'Baidu'
_SITE = 'https://www.baidu.com/'
_DESC = ('Baidu Search, is a Chinese language-search '
         'engine for websites, audio files and images.')


class Baidu(Engine):

    def __init__(self):
        self.maximum = 1000
        self.pmax = 50

        self.sreq = requests.Session()
        self.sreq.headers['User-Agent'] = random_user_agent()

        super(Baidu, self).__init__(_NAME, _SITE, _DESC)

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

        return (int(d['pn']) + int(self.pmax)) <= limit

    @staticmethod
    def _fetch_next_page(prev_link, content):
        match = re.search(r'<a href="(?P<next>[^"]*)" class="n">下一页', content)
        next_link = match.group('next') if match else ''
        next_link = patch_url(prev_link, next_link)

        return next_link

    def _fetch_page_content(self, link):
        try:
            content = self.sreq.get(link).content
        except any:
            content = ''
            # err = str(ex)

        return content

    def search(self, keyword, limit):
        self._init()

        if limit > self.maximum:
            limit = self.maximum
        d = {
            'wd': keyword,
            'rn': str(self.pmax),
            'pn': str(0),
        }
        q = dict2query(d)
        link = urlparse.urljoin(self._site, '/s?' + q)
        while self._is_over_limit(link, limit):
            content = self._fetch_page_content(link)
            link = self._fetch_next_page(link, content)
            if not link:
                break
            yield content
