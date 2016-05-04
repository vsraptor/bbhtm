import numpy as np
import matplotlib.pylab as plt
import matplotlib.animation as anim
import time
from bitarray import bitarray
from bmap2D import BMap2D
import datetime as dt
import time
import utils
from base import Base

class Memory(Base):

	def __init__(self, ncols=100, nrows=100, winp=0.021, randomize=0.1, data_size=None):

		self.ncols = ncols if ncols else data_size
		assert self.ncols, "need to specify ncols|data_size when creatining a pooler"
		self.nrows = nrows
		self.len = self.nrows * self.ncols
		self.ext = 'memory'

		self.winners_percent = winp # % of 1s
		self.winners_count = int(self.winners_percent * self.ncols)

		self.mem = BMap2D(nrows=self.nrows, nbits=self.ncols, randomize=randomize)

		self.forget_thresh = 0.6
		self.forget_count = 10
		self.forget_thresh_count = int(self.forget_thresh * self.mem.len)
		self.forget_cycles = 100

		self.train_cycle = 0

	@property
	def info(self) :
		s = "> Memory =========================================\n"
		s += "Data size : %s\n" % self.ncols
		s += "rows,cols : %s, %s\n" % (self.nrows, self.ncols)
		s += "win count : %s\n" % (self.winners_count)
		print s
		self.mem.info

#========== Basic ops =================================================

	#duplicate the pattern to match the dimention of the binary-map
	def overlap(self, data): #Dup ... AND
		signal = self.mem.repeat( data, self.nrows )
		#AND them together, to find where they match
		o = (self.mem.bmap & signal) #expensive?? too much mem
		return o

	#for specfied indecies apply the pattern
	def union(self, idxs, pat): #OR the pattern
		for i in idxs :
			self.mem[int(i),:] |= pat #!fixme : np.uint16 &&  list-as-bmap || pat

#========== Processes =================================================

	def process(self, data, cb_winners=None):
		res = self.overlap(data)
		olap = BMap2D(self.mem.nrows, self.mem.ncols, res)
		return olap

	def winners(self, overlap_mem) :
		# count the one's in every match and pick the winners
		win_idxs = np.argsort( - overlap_mem.count_ones(axis='rows') )[:self.winners_count]
		#print "win> %s" % win_idxs
		return win_idxs

	def learn(self,idxs,pat):
		#print "learned pats> %s" % idxs.size
		self.union(idxs,pat)

	def forget(self):
		raise NotImplementedError

	def via(self,data): #pass trough
		olap = self.process(data)
		idxs = self.winners(olap)
		return utils.idxs2bits(idxs, nbits=self.ncols)

	#process data and learn based on the outcome
	def train(self,data):
		olap = self.process(data)
		idxs = self.winners(olap)
		self.learn(idxs,data)
		self.train_cycle += 1

	#clear all connections of the cell with itself and closest neigboors(col)
	def clear_loopy(self,step):
		for r in xrange(0,self.ncols, step) :
			c = r + step
			#clean up rectangle
			self.mem[r:c, r:c] = 0


#========== Graphing ==================================================


	def bm2np(self,data=None,nr=None,nc=None):
		ncols = nc if nc else data.ncols
		nrows = nr if nr else data.nrows
		d = utils.bits2np(data.bmap)
		dview = d.view()
		dview.shape = (nrows, ncols)
		return dview

	def show_mem(self,data=None):
		if data is None : data = self.mem
		plt.figure()
		plt.imshow(self.bm2np(data), cmap='Greys', interpolation='nearest', aspect='auto')






