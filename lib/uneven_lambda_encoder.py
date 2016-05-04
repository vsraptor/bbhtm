import numpy as np
from inspect import isfunction
from uneven_category_encoder import UnevenCategoryEncoder

class UnevenLambdaEncoder(UnevenCategoryEncoder):

	def __init__(self, lam, **args):
		assert isfunction(lam), "Expecting lambda function to categorize the data-values"
		self.lam = lam
		super(UnevenLambdaEncoder, self).__init__(**args)


	def encode(self,data):
		category = self.lam(data)
		return super(UnevenLambdaEncoder,self).encode(category)


	def decode(self,data):
		return NotImplementedError

