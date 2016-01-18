#!/usr/bin/env python
# coding: utf-8

import re
import urlparse

import xml.etree.ElementTree as ET

import thirdparty.requests as requests

from lib.core.engines import Engine
from lib.core.engines import EngineError
from lib.core.engines import EngineConnectionError
from lib.utils.agents import random_user_agent
from lib.utils.common import dict2query
from lib.utils.common import query2dict
from lib.utils.common import patch_url


_NAME = 'Google'
_SITE = 'https://www.google.com/'
_DESC = ('Google Search, commonly referred to as Google Web Search '
         'or Google, is a web search engine owned by Google Inc.')


class Google(Engine):

    def __init__(self):
        self.maximum = 1000
        self.pmax = 100

        self.sreq = requests.Session()
        self.sreq.headers['User-Agent'] = random_user_agent()

        super(Google, self).__init__(_NAME, _SITE, _DESC)

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

        return (int(d['start']) + int(self.pmax)) <= limit

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

    @staticmethod
    def _fetch_next_page(prev_link, content):
        pattern = r'<a class="pn" href="(?P<next>[^"]*)" id="pnnext"'
        match = re.search(pattern, content)
        next_link = match.group('next') if match else ''
        if next_link:
            next_link = patch_url(prev_link, next_link)

        return next_link

    @staticmethod
    def parse_results(content):
        pattern = (r'<div class="rc".*?<h3 class="r">'
                   r'<a href="(?P<link>[^">]*)".*?>(?P<title>[^">]*)</a></h3>')

        results = []
        for iterm in re.finditer(pattern, content):
            # link, title = iterm.group('link'), iterm.group('title')
            link = iterm.group('link')
            results.append(link)

        return results

    def search(self, keyword, limit):
        self._init()

        if limit > self.maximum:
            limit = self.maximum
        d = {
            'q': keyword,
            'num': str(self.pmax),
            'start': str(0),
        }
        q = dict2query(d)
        link = urlparse.urljoin(self._site, '/search?' + q)
        while self._is_over_limit(link, limit):
            content = self._fetch_page_content(link)
            link = self._fetch_next_page(link, content)
            if not link:
                break
            yield content
