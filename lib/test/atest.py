import numpy as np
import matplotlib.pylab as plt
from temporal_memory import *
from pattern_lang import PatternLang
from scalar_encoder import *
from scalar_classifier import *
from stats import stats
import utils
from data_sets import *
import logging as log
import datetime as dt
from the_test import *
from spatial_pooler import *

class ATest(TheTest):

	def __init__(self, name, data, results, ttype=None,
		 data_size=100, enc_data_size=None, nrows=5, winp=0.02, randomize=0.01, delta=False, loopy_cols=True,
		 isize=100, osize=200, segment_size=1, nudge=5, fade=None
	) :

		self.data = data
		self.results = results
		self.test_name = name
		self.tame_taken = 0

		self.sp = None
		self.pre_train_sp = False #do we use SP
		self.ttype = ttype

		vmin = self.data.get('delta_min') if delta else self.data.get('min')
		vmax = self.data.get('delta_max') if delta else self.data.get('max')
		granularity = self.data.get('delta_granularity') if delta else self.data.get('granularity')

		#we can have different data size, the SP will compensate
		self.enc_data_size = enc_data_size if enc_data_size else data_size

		self.tm = TemporalMemory(data_size=data_size, nrows=nrows, winp=winp, randomize=randomize, loopy_cols=loopy_cols)
		self.se = ScalarEncoder(minimum=vmin, maximum=vmax,nbits=self.enc_data_size,width=self.tm.winners_count)

		if self.ttype == 'enc_sp' :
			log.debug('> Creating Spatial pooler ...')
			self.sp = SpatialPooler(input_size=self.enc_data_size, output_size=data_size, segment_size=1, winp=winp, nudge=nudge, fade=fade, randomize=randomize)
			self.train_spooler(end=1000)
			self.pre_train_sp = False
		else : assert self.enc_data_size is None

		self.sc = ScalarClassifier(encoder=self.se, spooler=self.sp)
		#data for measuring performance
		self.ys = []
		self.yhat = []
		#init
		self.sc.build_cmap(start=vmin, end=vmax, step=granularity)


	def train_spooler(self,begin=0,end=100):
		log.debug("> Training Spatial pooler ...")
		ts = dt.datetime.now()

		for i, d in enumerate( self.data.data[begin:end] ) :
			value = self.se.encode(d)
			if i % 100 == 0 : log.debug("%s>" % i)
			self.sp.train(value)

		te = dt.datetime.now()
		time_taken = te - ts
		log.debug("Time taken : %s" % time_taken)
		#turn it off, for the next runs
		self.pre_train_sp = False


	def run(self, name=None, begin=0,end=100,anim=False,run_metrics=True,via=False,forward=0,delta=False):
		self.end = end
		if name is not None : self.test_name = name
		self.ys = np.zeros(end-begin + forward, dtype=np.int)
		self.yhat = np.zeros(end-begin + forward, dtype=np.int)

		if self.pre_train_sp :
			self.train_spooler(begin,end)

		pred = self.se.encode(0)
	  	ds = self.data.data[begin:end]
		if delta :
			ds = self.data.delta[begin:end]

		ts = dt.datetime.now()

		for i, d in enumerate( ds ) :

			value = self.se.encode(d)
			if self.ttype == 'enc_sp' : value = self.sp.predict(value)

			self.ys[i] = d #store the original data
			log.debug("%s> %s <=> %s : %s" % (i, d, self.yhat[i], self.yhat[i] - d) )

			if via : self.tm.via(value)
			else :  self.tm.train(value,anim=anim)

			#fetch last prediction
			pred = self.tm.predicted_sdr()
			if i < self.yhat.size - 1 :
				bm = self.sc.best_match(pred)
				self.yhat[i+1] = bm #save prediction one step forward

			if anim : self.tm.plot(pause=0.01,cmap='Greys')

		if forward > 0 :#predict more steps in the future
			for f in xrange(1,forward):
				tmp = next(self.tm.forward())
				self.yhat[end+f] = self.sc.best_match( tmp )
				log.debug( "fwd:%s> %s" % (f, self.yhat[end+f]) )

		te = dt.datetime.now()
		self.time_taken = te - ts
		log.debug("Time taken : %s" % self.time_taken)

		if run_metrics : self.metrics(forward=forward)


	def metrics(self, name=None, begin=0, end=None, forward=0):
		if name is None : name = self.test_name
		if end is None : end = self.ys.size
		self.results.add_data(name, self.ys, self.yhat, begin,end,forward)
		self.results.add_metric(name, 'fill', self.tm.memory.mem.fill)
		self.results.add_metric(name, 'avg_fill', self.tm.memory.mem.avg_item_fill)
		self.results.add_metric(name, 'max_fill', self.tm.memory.mem.max_item_fill)
		self.results.add_metric(name, 'time_taken', self.time_taken)

		self.results.print_metrics()


#==========================================================================================

	@staticmethod
	def rolling_metric(ys,yhat,fun=stats.mape,begin=10,step=10):
		assert ys is not None, "No data ....."
		size = ys.size
		return [ fun(ys[0:n],yhat[0:n]) for n in range(begin,size,step) ]


	@staticmethod
	def plot_metric(results=None, name=None, fun=stats.mape, begin=10, step=10, ys=None, yhat=None):
		if (results is not None) and (name is not None) :
			ys = results.series[name]['ys']
			yhat = results.series[name]['yhat']

		assert ys is not None, "No data ....."
		size = ys.size
		plt.plot(xrange(begin,size,step), ATest.rolling_metric(ys,yhat,fun,begin,step))


