#!/usr/bin/env python
#import os, sys
#basedir = os.path.abspath(os.path.dirname(__file__))
#libdir = os.path.abspath(os.path.join(basedir, '../lib'));
#libtest = os.path.abspath(os.path.join(basedir, '../lib/test'));

#sys.path.append(libdir)
#sys.path.append(libtest)
import logging as log
log.basicConfig(format='%(message)s', level=log.DEBUG)

from data_sets import *
from results import Results
from atest import ATest
import time

class DataTest:

	def __init__(self,data_set='ny' ):
		if data_set[0] == '.' :
			self.data = DataSet(pat=data_set[1:])
		else :
			self.data = DataSet(data_set)

		self.results = Results()
		self.tests = {}
		self.end = 0
		self.first = None

	def new_test(self,name,**args):
		winp = args['winp'] if 'winp' in args else 'def'
		log.debug("Creating test : %s, wp:%s" % (name,winp))
		self.tests[name] = ATest(name, data=self.data,results=self.results, **args)
		if not self.first : self.first = self.tests[name]


	def make_tests(self,nrows_lst=[5],ncols_lst=[300],winp_lst=[0.02],delta=False):
		rv = []
		for ncols in ncols_lst:
			for nrows in nrows_lst :
				for winp in winp_lst :
					name = str(nrows) + 'x' + str(ncols) + 'w' + str(int(100 * winp))
					rv = self.new_test(name,data_size=ncols,nrows=nrows, winp=winp, delta=delta)
				self.test = rv

	def run_test(self,name, begin=0,end=10,anim=False,forward=0, delta=False):
		self.end = end
		if name in self.tests :
			log.debug("> Runing test : %s ..." % name)
		 	self.tests[name].run(begin=begin,end=end,anim=anim,forward=forward,delta=delta)
		else:
			log.debug("Test with name : %s does not exists" % name)


	def run_tests(self,begin=0,end=10,anim=False,forward=0,delta=False):
		self.end = end
		for name, test in self.tests.items() :
			log.debug( "> Runing test : %s ..." % name)
			test.run(begin=begin,end=end,anim=anim,forward=forward, delta=delta)


	def save(self, save_at='../../tmp/dt'):
		log.debug( "Saving data sets ..." )
		tstamp = time.strftime('%d%H%M') + '-' + str(self.end)
		for name, test in self.tests.items() : 
			test.save(save_at + '/' + tstamp + '_' + name)
			test.save_plot(name,save_at)
			test.save_plot(name,save_at,ext='png')

		self.results.save(save_at + '/' + tstamp + '_results')


def main():
	dt = DataTest(data_set='dollar')
#	dt.new_test('x')
#	dt.make_tests(yrange=xrange(500,1001,500), nrows=8)
	dt.make_tests(yrange=xrange(2000,2001,1), nrows=5)

#	dt.make_tests(nrows=8)
	dt.run_tests(begin=5000, end=9000)
	dt.save()

#if __name__ == '__main__' : main()


