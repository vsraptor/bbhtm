import os, sys
import logging as log
#log.basicConfig(format='%(message)s', level=log.DEBUG)

from stats import *
from data_sets import *
from results import Results
from scalar_encoder import *
from spatial_pooler import *
from the_test import *


class SPoolerTest(TheTest):

	def __init__(self, name, data, results,  isize, osize, segment_size=1, winp=0.02, delta=False, nudge=5, fade=None, randomize=0.01):

		self.data = data
		self.results = results
		self.test_name = name
		self.tame_taken = 0

		self.sp = SpatialPooler(input_size=isize, output_size=osize, segment_size=segment_size, winp=winp, nudge=nudge, fade=fade, randomize=randomize)

		if self.data.ds in DataSet.list_datasets() : #!fixme
			log.debug("> Setting encoder ...")
			vmin = self.data.get('delta_min') if delta else self.data.get('min')
			vmax = self.data.get('delta_max') if delta else self.data.get('max')
			granularity = self.data.get('delta_granularity') if delta else self.data.get('granularity')

			self.se = ScalarEncoder(minimum=vmin, maximum=vmax,nbits=isize,width=self.sp.in_wc)


	def run(self,begin=0,end=100,via=False):
		self.ys = np.zeros(end-begin, dtype=np.int)
		self.yhat = np.zeros(end-begin, dtype=np.int)

		ts = dt.datetime.now()

		for i, d in enumerate( self.data.data[begin:end] ) :
#			value = utils.np2bits( DataSet.encode_digit(d) )
			value = self.se.encode(d)
#			self.ys[i] = d #store the original data
			if i % 100 == 0 : log.debug("%s>" % i)

			if via : self.sp.via(value)
			else :  self.sp.train(value)

		te = dt.datetime.now()
		self.time_taken = te - ts
		log.debug("Time taken : %s" % self.time_taken)


	def predict(self, value) :
		if isinstance(value, int) : value = self.se.encode(value)
		return self.sp.predict(value)

	def via(self, value) :
		if isinstance(value, int) : value = self.se.encode(value)
		return self.sp.via(value)
