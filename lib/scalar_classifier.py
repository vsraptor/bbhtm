import numpy as np
from bmap2D import BMap2D
from scalar_encoder import ScalarEncoder
import utils
from base import Base
import matplotlib.pylab as plt
import logging as log

class ScalarClassifier(Base):

	def __init__(self, encoder, spooler=None):
		self.se = encoder
		self.sp = spooler
		self.cmap = None #classification map
		self.cmap_keys = {}
		self.start = 0
		self.end = 0
		self.end = 0
		self.step = 0
		self.ext = 'sclf'

	@property
	def info(self) :
		s = "> Scalar Classifier ==============================\n"
		s += "range,step: %s - %s , %s\n" % (self.start, self.end, self.step)
		print s
		self.se.info
		self.cmap.info

	def build_cmap(self,start=0,end=10,step=1):
		log.debug( "sc> building classification map ..." )
		self.start = start
		self.end = end
		self.step = step
		nrows = int( ( end - start ) / step ) # + 1
		#if we are having SP in the chain
		cols = self.sp.osize if self.sp else self.se.nbits
		self.cmap = BMap2D(nrows=nrows, ncols=cols)

		for i, v in enumerate(xrange(start,end,step)):
			value = self.se.encode(v)
			#one more step if SP is used
			if self.sp : value = self.sp.predict(value)
			self.cmap[i,:] = value
			self.cmap_keys[i] = v

	#given bit-binary OR numerical value, get back the closest matching value
	def best_match(self,val):
		if isinstance(val,int) : val = self.se.encode(val)
		if isinstance(val,np.ndarray) : val = utils.np2bits(val)

		val2D = self.cmap.repeat(val, self.cmap.nrows)
		bmap = BMap2D(self.cmap.nrows, self.cmap.ncols, self.cmap.bmap & val2D)
		match_idx = np.argmax( bmap.count_ones(axis='rows') )
		return self.cmap_keys[match_idx]


	def test_plot(self,step=10) :#plot real-values and best-match side by side, so that we can see how well they match
		the_range = xrange(self.start,self.end, step)
		plt.plot(the_range, [ i for i in the_range ] )
		plt.plot(the_range, [ self.best_match( self.se.encode(i) )  for i in the_range ] )

