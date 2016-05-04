import cPickle as pickle

class Base(object):

	def save(self, file_name):
		if self.ext : file_name += '.' + self.ext
		with open(file_name,'wb') as f : pickle.dump(self,f)

	@staticmethod
	def load(file_name):
		with open(file_name,'rb') as f : return pickle.load(f)

