#!/usr/bin/env python
# coding: utf-8

from lib.core.engines import Google
from lib.core.engines import Baidu
from lib.core.engines import Censys
from lib.core.engines import Shodan
from lib.core.engines import ZoomEye

from lib.utils.proxy import init_proxy


if __name__ == '__main__':
    import sys
    init_proxy('socks5://127.0.0.1:1080')

    if len(sys.argv) < 4:
        print 'Usage: python %s [engine] [keyword] [limit]' % sys.argv[0]
        sys.exit()

    engine = sys.argv[1]
    keyword = sys.argv[2]
    limit = int(sys.argv[3])

    if engine == 'Google':
        engine = Google()
    elif engine == 'Baidu':
        engine = Baidu()
    else:
        print 'Invalid engine'
        sys.exit()

    for content in engine.search(keyword=keyword, limit=limit):
        results = engine.parse_results(content)
        for link in results:
            print link
