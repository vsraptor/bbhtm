import logging as log
import numpy as np
from stats import stats
import matplotlib.pylab as plt
from base import Base

class Results(Base):

	def __init__(self):
		self.metrics = {}
		self.series = {}
		self.m = {}
		self.ext = 'res'

	def calc_metrics(self,ys,yhat, begin=0, end=None):
		if end is None : end = ys.size
		self.m['rmse'] = stats.rmse(ys[begin:end], yhat[begin:end])
		self.m['mae'] = stats.mae(ys[begin:end], yhat[begin:end])
		self.m['mape'] = stats.mape(ys[begin:end], yhat[begin:end])
		self.m['nll'] = stats.nll(ys[begin:end], yhat[begin:end])
		self.m['r2'] = stats.r2(ys[begin:end], yhat[begin:end])


	def add_metric(self, name, key, val) : self.metrics[name][key] = val
	def get_metric(self, name, key) : return self.metrics[name][key]

	def add_data(self, name, ys,yhat, begin=0, end=None, forward=0):
		print "Adding data metrics with name : %s " % name
		if end is None : end = ys.size

		self.calc_metrics(ys[begin:end], yhat[begin:end], begin, end)

		if not self.metrics.has_key(name) : self.metrics[name] = { 'mae' : [], 'mape' : [], 'rmse' : [], 'nll' : [], 'r2' : [] }
		self.metrics[name]['mae'] = self.m['mae']
		self.metrics[name]['mape'] = self.m['mape']
		self.metrics[name]['rmse'] = self.m['rmse']
		self.metrics[name]['nll'] = self.m['nll']
		self.metrics[name]['r2'] = self.m['r2']


		if not self.series.has_key(name) : self.series[name] = { 'ys' : None, 'yhat' : None }
		else : print "'%s' already exists overriding metrics data ..." % name
		self.series[name]['ys'] = ys[begin:end+forward] #.copy()
		self.series[name]['yhat'] = yhat[begin:end+forward] #.copy()


	def print_metrics(self):
		for m in self.m.keys() :
			log.info( "%s: %s" % ( m.upper(), self.m[m] ) )


	def plot(self, name,series, begin=0, end=None):
		if end == None : end = self.series[name][series].size
		size = begin - end
		#plt.tight_layout()
		plt.plot(xrange(begin,end), self.series[name][series][begin:end])


	def tests_list(self):
		rv = {}
		for t in self.series.keys() :
			rv[t] = { 'size' : self.series[t]['ys'].size, 'metrics' : self.metrics[t] }
		return rv


