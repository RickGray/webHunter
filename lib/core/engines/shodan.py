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


_NAME = 'Shodan'
_SITE = 'https://www.shodan.io/'
_DESC = ('Shodan Search, Shodan is the world\'s first '
         'search engine for Internet-connected devices.')


class Shodan(Engine):

    def __init__(self):
        self.maximum = 50
        self.pmax = 10

        self.sreq = requests.Session()
        self.sreq.headers['User-Agent'] = random_user_agent()

        super(Shodan, self).__init__(_NAME, _SITE, _DESC)

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

        return (int(d['page']) * int(self.pmax)) <= limit

    @staticmethod
    def _fetch_next_page(prev_link, content):
        q = urlparse.urlparse(prev_link).query
        d = query2dict(q)
        prev_page = d.get('page', '')
        if prev_page:
            match = re.search(r'<a href="(?P<next>[^">]*)".*?>Next', content)
            next_link = match.group('next') if match else ''
            next_link = patch_url(prev_link, next_link)
        else:
            next_link = ''

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

    def search(self, keyword, limit):
        self._init()

        if limit > self.maximum:
            limit = self.maximum
        d = {
            'query': keyword,
            'page': str(1),
        }
        q = dict2query(d)
        link = urlparse.urljoin(self._site, '/search?' + q)
        while self._is_over_limit(link, limit):
            print link
            content = self._fetch_page_content(link)
            link = self._fetch_next_page(link, content)
            if not link:
                break
            yield content

    def _login(self, username, password):
        i_url = 'https://account.shodan.io/login'
        post = {
            'username': username,
            'password': password,
            'grant_type': 'password',
            'continue': 'https://account.shodan.io/',
            'login_submit': 'Log in'
        }
        self.sreq.post(i_url, data=post)
