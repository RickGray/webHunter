#!/usr/bin/env python
# coding: utf-8

import os
import re
import urllib
import urlparse
import HTMLParser


def dict2query(d):
    q = urllib.urlencode(d)
    return q


def query2dict(q):
    print q
    items = q.split('&')
    d = {}
    for item in items:
        try:
            k, v = item.split('=')
        except any:
            k = item
            v = ''

        k = urllib.unquote(k)
        v = urllib.unquote(v)
        d[k] = v

    return d


def patch_url(s_url, p_url):
    p_url = HTMLParser.HTMLParser().unescape(p_url)

    if p_url.startswith('//'):
        p_url = 'http:' + p_url
    elif re.search(r'^/[^/].*$', p_url):
        p_url = urlparse.urljoin(s_url, p_url)
    elif re.search(r'^[^/].*$', p_url):
        p_url = urlparse.urljoin(os.path.dirname(s_url) + '/', p_url)
    elif re.search(r'^[\.]{1,2}/[^/].*$', p_url):
        p_url = urlparse.urljoin(s_url, p_url)

    return p_url
