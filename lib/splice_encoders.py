import numpy as np
import math
from encoder import Encoder

#Concatenate encoded results
class SpliceEncoders(Encoder):

	def __init__(self,encoders):
		self.encoders = encoders
		self.nbits = 0
		for enc in self.encoders : self.nbits += enc.nbits

	@property
	def info(self):
		s = "=====================================\n"
		for e in self.encoders :
			e.info()
			s += "-----------------------------------\n"
		s += "Total number of bits : %s\n" % self.nbits
		print s

	#one data item per encoder
	def encode(self, data):
		assert len(data) == len(self.encoders), "Data <=> Encoder size mistmatch"
		catenated = []
		for i, enc in enumerate(self.encoders) :
			catenated.append( enc.encode(data[i]) )
		return np.hstack(catenated)

	def batch_encode(self, data):
		rv = np.zeros((len(data),self.nbits))
		for i in np.arange(len(data)) :
			rv[i] = self.encode(data[i])
		return rv


	def decode(self,data):
		return NotImplementedError

	def batch_decode(self,data) :
		return NotImplementedError



