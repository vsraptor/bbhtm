import numpy as np
import math
from encoder import Encoder

class UnevenCategoryEncoder(Encoder) :

	#list of pairs : (cat_num,nbits)
	def __init__(self, blueprint):
		assert isinstance(blueprint, list), "expecting list of pairs (cat_num, nbits)"
		self.ncats = len(blueprint)
		self.blueprint = blueprint
		#sum the bits to get total len
		self.nbits = reduce(lambda a,b : (0, a[1] + b[1]), self.blueprint)[1]
		self.cats = map(lambda a: a[0], self.blueprint)

		self.info()

	def info(self):
		print "> Uneven Category encoder -----"
		print "Num of categories : %s" % self.ncats
		print "Num of bits : %s" % self.nbits
		print "Blueprint : %s" % self.blueprint

	def encode(self, value):
		assert value in self.cats, "Value does not match any category : %s" % value
		rv = np.zeros(self.nbits, dtype='uint8')
		pos = 0
		for cat, nbits in self.blueprint :
			if value == cat : rv[ pos : pos + nbits ] = 1
			pos += nbits
		return rv

	def decode(self, data):
		raise NotImplementedError
