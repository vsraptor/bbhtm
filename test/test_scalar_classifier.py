#!/usr/bin/env python
import os, sys
basedir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.abspath(os.path.join(basedir, '../lib'));
sys.path.append(libdir)

from scalar_encoder import *
from scalar_classifier import *
from stats import stats
import getopt

class SCTest:

	def __init__(self,n=None,x=None,b=None,s=None,w=None):
		self.opts = {}
		self.n = n
		self.x = x
		self.b = b
		self.s = s
		self.w = w
		self.h = None

		if sys.argv[0] :
			self.parse_args(sys.argv[1:])
			if self.h is not None : self.print_help(); exit()

			for o in [ 'n', 'x', 'b', 's', 'w' ]  :
				if getattr(self,o) is None : raise Exception("Missing cmd line option : %s" % o)

		self.init(mn=self.n, mx=self.x,nbits=self.b,step=self.s)

	def init(self, mn=0, mx=1000, nbits=100, step=10):
		self.se = ScalarEncoder(minimum=mn,maximum=mx, nbits=nbits,width=self.w)
		self.sc = ScalarClassifier(encoder=self.se)
		self.sc.build_cmap(start=mn,end=mx,step=step)


	def parse_args(self,arguments):
		try:
			for arg,opt in getopt.getopt(arguments,'h:n:x:b:s:w:')[0] :
				setattr(self, arg[1:], int(opt))
		except getopt.GetoptError:
			print "wrong args"
			sys.exit(2)

	def test(self):
		self.ys = np.zeros(self.x - self.n)
		self.yhat = np.zeros(self.x - self.n)

		for i in xrange(self.n,self.x):
			self.ys[i - self.n] = i
			self.yhat[i - self.n] = self.sc.best_match(i)

		self.mape = stats.mape(self.ys,self.yhat)
		self.mae = stats.mae(self.ys,self.yhat)
		self.rmse = stats.rmse(self.ys,self.yhat)
		self.nll =  stats.nll(self.ys,self.yhat)

		self.sc.info
		print
		print "MAPE: %s" % self.mape
		print "MAE: %s" % self.mae
		print "RMSE: %s" % self.rmse
		print "NLL: %s" % self.nll


	def print_help(self):
		print """
Example :
./test_scalar_classifier.py -b 100 -n 0 -x 1000 -s 10 -w 5

Help :
	-n minimum
	-x maximum
	-s step
	-b number of bits
	-w SE bit width
		"""

def main():
	sct = SCTest()
	sct.test()

if __name__ == '__main__' : main()
