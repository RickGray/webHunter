#!/usr/bin/env python
# coding: utf-8

import os
import ConfigParser


conf = ConfigParser.ConfigParser()

pconf = os.path.join(os.path.dirname(__file__), '../../config.ini')
try:
    conf.read(pconf)
except any:
    pass
