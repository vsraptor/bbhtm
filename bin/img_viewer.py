#!/usr/bin/env python
import os, sys
basedir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.abspath(os.path.join(basedir, '../lib'));
libtest = os.path.abspath(os.path.join(basedir, '../lib/test'));

sys.path.append(libdir)
sys.path.append(libtest)

import matplotlib.pylab as plt

fname = sys.argv[1]
#plt.figure()
img = plt.imread(fname)
fig, ax = plt.subplots()
im = ax.imshow(img)
plt.show()