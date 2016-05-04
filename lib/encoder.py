import numpy as np
import math
from base import Base

class Encoder(Base):

	def __init__(self, num_bits):
		self.nbits = num_bits

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
