#!/usr/bin/env python
import os, sys
import getopt
import csv
import logging as log
log.basicConfig(format='%(message)s', level=log.DEBUG)

basedir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.abspath(os.path.join(basedir, '../lib'));
libtest = os.path.abspath(os.path.join(basedir, '../lib/test'));

sys.path.append(libdir)
sys.path.append(libtest)

import matplotlib.pylab as plt
from results import *

def load(fname): return Results.load(fname)



def metrics(res):
#		res.print_all_metrics()
#	print res.metrics
	with open('metrics.csv', 'a') as f :
		w = csv.writer(f)
		i = 0
		for name, item in sorted(res.metrics.items()) :
			shape,wp = name.split('w')
			nrows,ncols = shape.split('x')
			if i == 0 :
				w.writerow(["name","nrows","ncols","winp"] + item.keys())
				i += 1
			w.writerow( [name,nrows,ncols,wp] + item.values())


def plot(res):
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

def parse_args(arguments):
	opts = {}
	try:
		for arg,opt in getopt.getopt(arguments,'f:vm')[0] : opts[arg] = opt
		return opts
	except getopt.GetoptError:
		print "wrong args"
		sys.exit(2)



opts = parse_args(sys.argv[1:])
res = load(opts['-f'])

if '-v' in opts : plot(res)
if '-m' in opts : metrics(res)

