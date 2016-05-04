import sys
import os
import getopt
import logging as log
import utils
from data_test import DataTest
from data_sets import *

class TestSuite:

	def __init__(self):
		self.opts = {}
		self.args = { 'nrows_lst' : [], 'ncols_lst' : [], 'winp_lst' : [] }
		self.begin = 0
		self.end = 10
		self.data_set = None

		self.parse_args(sys.argv[1:])
		if '-h' in self.opts : self.print_help(); exit()

		for o in [ '-r', '-c', '-w', '-b', '-e' ]  :
			if o not in self.opts : raise Exception("Missing cmd line option : %s" % o)

		if '-d' in self.opts : self.data_set = self.opts['-d']
		else : raise Exception( "Data set must be specified : %s" % DataSet.list_datasets() )

		for opt, arg in zip(['-r', '-c', '-w' ],['nrows_lst', 'ncols_lst', 'winp_lst']) :
			if opt in self.opts :
				self.args[arg] = [ utils.num(x) for x in self.opts[opt].split(',') ]

		self.begin = int(self.opts['-b']) if '-b' in self.opts else  0
		self.end   = int(self.opts['-e'])   if '-e' in self.opts else 10

		#print self.args

		self.dt = DataTest(data_set=self.data_set)
		self.dt.make_tests(**self.args)


	def run(self):
		self.dt.run_tests(begin=self.begin, end=self.end)

	def save(self,save_at=None): 
		if save_at is None : save_at = '../tmp/dt/' + self.data_set
		if not os.path.exists(save_at): os.makedirs(save_at)
		self.dt.save(save_at)

	def parse_args(self,arguments):
		opts = {}
		try:
			for arg,opt in getopt.getopt(arguments,'hr:c:w:f:d:b:e:')[0] : self.opts[arg] = opt
		except getopt.GetoptError:
			print "wrong args"
			sys.exit(2)

		print self.opts


	def print_help(self):
		print """
Example :
	python run_test_suite.py -d ny -r 5 -c 100,200 -w 0.02 -s 0 -e 100
Test suite params :
	-d : data set : ny, dollar, hot-gym, sine
	-r : number of rows - a list
	-c : number of cols - a list
	-w : winners percent, controls sparsity - a list
	-b : in data set what position to start
	-e : in data set what position to end
		"""