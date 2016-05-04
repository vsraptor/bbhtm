#!/usr/bin/env python
import os, sys
basedir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.abspath(os.path.join(basedir, '../lib'));
libtest = os.path.abspath(os.path.join(basedir, '../lib/test'));

sys.path.append(libdir)
sys.path.append(libtest)
import logging as log
log.basicConfig(format='%(message)s', level=log.DEBUG)
from test_suite import TestSuite

ts = TestSuite()
ts.run()
ts.save()