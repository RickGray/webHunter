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


_NAME = 'Censys'
_SITE = 'https://www.censys.io/'
_DESC = ('Censys Search, a search engine that allows computer scientists to '
         'ask questions about the devices and networks that compose the Internet.')


class Censys(Engine):

    def __init__(self):
        self.maximum = 1000
        self.pmax = 25

        self.sreq = requests.Session()
        self.sreq.headers['User-Agent'] = random_user_agent()

        super(Censys, self).__init__(_NAME, _SITE, _DESC)

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
            match = re.search(r'<a href=(?P<next>[^">]*)>' + str(int(prev_page)+1) + r'</a>', content)
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
        try:
            self._login()
        except any:
            pass

        if limit > self.maximum:
            limit = self.maximum
        d = {
            'q': keyword,
            'page': str(1),
        }
        q = dict2query(d)
        link = urlparse.urljoin(self._site, '/domain?' + q)
        while self._is_over_limit(link, limit):
            content = self._fetch_page_content(link)
            link = self._fetch_next_page(link, content)
            if not link:
                break
            yield content

    def _login(self):
        username = conf.get('censys', 'username')
        password = conf.get('censys', 'password')

        def fetch_csrf_token(login_url):
            _res = self.sreq.get(login_url)
            match = re.search(r'name="csrf_token" value="(?P<csrf_token>[^">].*)"', _res.content)
            _csrf_token = match.group('csrf_token') if match else ''
            match = re.search(r'name="came_from" value= "(?P<came_from>[^">].*)"', _res.content)
            _came_from = match.group('came_from') if match else ''

            return _csrf_token, _came_from

        i_url = 'https://www.censys.io/login'
        csrf_token, came_from = fetch_csrf_token(i_url)
        if csrf_token and came_from:
            post = {
                'csrf_token': csrf_token,
                'came_from': came_from,
                'login': username,
                'password': password
            }
            self.sreq.post(i_url, data=post)
