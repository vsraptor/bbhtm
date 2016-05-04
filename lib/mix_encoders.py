import numpy as np
from splice_encoders import SpliceEncoders
from scalar_encoder import ScalarEncoder
from category_encoder import CategoryEncoder
from lambda_encoder import LambdaEncoder
from uneven_lambda_encoder import UnevenLambdaEncoder
from lambdas import *

class MixEncoders(SpliceEncoders):

	def __init__(self, blueprint=[(0,5),(1,45)]):
		def mod5(x): return mod(x,5)
		self.se = ScalarEncoder(nbits=2000,width=20)
#		self.mod5 = LambdaEncoder(lam=mod5,nbits=25,ncats=5)
		self.prime = UnevenLambdaEncoder(lam=is_prime, blueprint=blueprint)
		self.fib = UnevenLambdaEncoder(lam=is_fibonacci, blueprint=blueprint)

		super(MixEncoders, self).__init__(encoders=[self.se, self.prime, self.fib])


	def encode(self,data):
		d = [data] * len(self.encoders)
		return super(MixEncoders,self).encode(d)


	def decode(self,data) :
		return NotImplementedError