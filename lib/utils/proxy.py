#!/usr/bin/env python
# coding: utf-8

import socket
import urlparse

import thirdparty.socks.socks as socks


def init_proxy(proxy):
    res = urlparse.urlparse(proxy)

    use_proxy = True
    if res.scheme == 'socks4':
        mode = socks.SOCKS4
    elif res.scheme == 'socks5':
        mode = socks.SOCKS5
    elif res.scheme == 'http':
        mode = socks.HTTP
    else:
        mode = None
        use_proxy = False

    if use_proxy:
        socks.set_default_proxy(mode, res.netloc.split(':')[0], int(res.netloc.split(':')[1]))
        socket.socket = socks.socksocket
