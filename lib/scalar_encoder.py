import numpy as np
import math
from encoder import Encoder
from bmap1D import BMap1D

class ScalarEncoder(Encoder):

	def __init__(self, minimum=0,maximum=100,buckets=100,width=5,nbits=None):
		self.vmin = minimum
		self.vmax = maximum
		self.vrange = self.vmax - self.vmin
		self.width = width
		self.ext = 'se'
		if (nbits is None) :
			self.buckets = buckets
			self.nbits = buckets + width + 1
		else :
			self.nbits = nbits
			self.buckets = nbits - width + 1

	@property
	def info(self):
		s = "> Scalar encoder -----\n"
		s += "min-max/range : %s-%s/%s\n" % (self.vmin,self.vmax,self.vrange)
		s += "buckets,width,n : %s,%s,%s\n" % (self.buckets,self.width,self.nbits)
		print s

	def np_encode(self, value):
		i = int( math.floor(self.buckets * ((value - self.vmin)/float(self.vrange)) ) )
		rv = np.zeros(self.nbits,dtype='uint8')
		rv[i : i + self.width ] = 1
		return rv

	def np_decode(self, data):
		tmp = np.where(data == 1)[0]
		i = 0 if len(tmp) == 0 else tmp[0]
		value = ( (i * self.vrange) / float(self.buckets) ) + self.vmin
		return math.floor(value)

	def encode(self, value):
		i = int( math.floor(self.buckets * ((value - self.vmin)/float(self.vrange)) ) )
		rv = BMap1D(self.nbits)
		rv.setall(0)
		end = i + self.width
		rv[i : end] = 1
		return rv

	def decode(self, data):
		tmp = data.one_idxs()
		i = 0 if len(tmp) == 0 else tmp[0]
		value = ( (i * self.vrange) / float(self.buckets) ) + self.vmin
		return math.floor(value)

