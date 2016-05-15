from bitarray import bitarray
import numpy as np

#Implements 1D bit-binary functionality using 1D continious bitarray

class BMap1D(bitarray):

	ONE = bitarray("1")
	ZERO = bitarray("0")

	def __lshift__(self, cnt):
		return self[cnt:] + type(self)('0') * cnt

	def __rshift__(self, cnt):
		return type(self)('0') * cnt + self[:-cnt]

	def one_idxs(self):
		idxs = self.search(bitarray("1"))
		return np.array(idxs,dtype=np.uint16)

	def zero_idxs(self):
		idxs = self.search(bitarray("0"))
		return np.array(idxs,dtype=np.uint16)

