import numpy as np
import math
from encoder import Encoder

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

	def encode(self, value):
		i = math.floor(self.buckets * ((value - self.vmin)/float(self.vrange)) )
		rv = np.zeros(self.nbits,dtype='uint8')
		rv[i : i + self.width ] = 1
		return rv

	def decode(self, data):
		tmp = np.where(data == 1)[0]
		i = 0 if len(tmp) == 0 else tmp[0]
		value = ( (i * self.vrange) / float(self.buckets) ) + self.vmin
		return math.floor(value)

