#!/usr/bin/env python
import os, sys
basedir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.abspath(os.path.join(basedir, '../lib'));
libtest = os.path.abspath(os.path.join(basedir, '../lib/test'));

sys.path.append(libdir)
sys.path.append(libtest)

import matplotlib.pylab as plt
from results import *

fname = sys.argv[1]

res = Results.load(fname)
for name in res.series.keys() :
	fig = plt.figure()
	ax = fig.add_subplot(111)
	plt.plot( res.series[name]['ys'] )
	plt.plot( res.series[name]['yhat'] )
	plt.suptitle(name)
	y = 0.998
	for m in ['mape','nll', 'mae', 'rmse', 'r2'] :
		metric = "%s: %.3f" % (str(m).upper(), res.metrics[name][m])
		plt.text(0.998,y, metric, horizontalalignment='right',  verticalalignment='top', transform=ax.transAxes)
		y -= 0.03
	plt.tight_layout()


plt.show()

