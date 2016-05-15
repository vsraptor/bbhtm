import numpy as np
import math
from base import Base
import utils

class Encoder(Base):

	def __init__(self, num_bits):
		self.nbits = num_bits


	def encode(self, data): raise NotImplementedError
	def decode(self, data): raise NotImplementedError

	#override this method if you can, better provide directly BMap1D output
	def np_encode(self, data): return utils.bits2np( self.encode(data) )
	def np_decode(self, data): return utils.bits2np( self.decode(data) )

	def batch_encode(self, data):
		if isinstance(data,list) : data = np.array(data)
		rv = np.zeros((data.size,self.nbits))
		for i in np.arange(data.size) :
			rv[i] = self.encode(data[i])
		return rv

	def batch_decode(self, data):
		if isinstance(data,list) : data = np.array(data)
		rv = np.zeros((data.size,self.nbits))
		for i in np.arange(data.size) :
			rv[i] = self.decode(data[i])
		return rv
