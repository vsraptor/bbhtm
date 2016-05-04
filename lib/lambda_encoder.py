import numpy as np
from inspect import isfunction
from category_encoder import CategoryEncoder

class LambdaEncoder(CategoryEncoder):

	def __init__(self, lam, **args):
		assert isfunction(lam), "Expecting lambda function to categorize the data-values"
		self.lam = lam
		super(LambdaEncoder, self).__init__(**args)


	def encode(self,data):
		category = self.lam(data)
		return super(LambdaEncoder,self).encode(category)


	def decode(self,data):
		return NotImplementedError

