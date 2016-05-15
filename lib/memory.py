import numpy as np
import matplotlib.pylab as plt
import matplotlib.animation as anim
import time
from bmap1D import BMap1D
from bmap2D import BMap2D
import datetime as dt
import time
import utils
from base import Base

class Memory(Base):

	#Enums...
	OVERLAP, DISTANCE = range(2)
	UNION, NUDGE = range(2)

	def __init__(self, ncols=100, nrows=100, winp=0.021, randomize=0.1, data_size=None, fade=None, nudge=5 ):

		self.ncols = ncols if ncols else data_size
		assert self.ncols, "need to specify ncols|data_size when creatining a pooler"
		self.nrows = nrows
		self.len = self.nrows * self.ncols
		self.ext = 'memory'

		self.winners_percent = winp # % of 1s
		self.winners_count = int(self.winners_percent * self.ncols)

		self.mem = BMap2D(nrows=self.nrows, nbits=self.ncols, randomize=randomize)

		#self.forget_thresh = 0.6
		#self.forget_count = 10
		#self.forget_thresh_count = int(self.forget_thresh * self.mem.len)
		#self.forget_cycles = 100

		self.fade = fade #for SP
		self.nudge_step = nudge
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
		#AND them together, to find where they match on ONE's
		o = (self.mem.bmap & signal) #expensive?? too much mem
		return o

	#Hamming distance
	def distance(self, data): #Dup ... XOR
		signal = self.mem.repeat( data, self.nrows )
		#XOR them together, to find where they differ
		o = (self.mem.bmap ^ signal) #expensive?? too much mem
		return o

	#LEARN: for specfied indecies apply the pattern
	def union(self, idxs, pat): #OR the pattern
		for i in idxs :
			self.mem[int(i),:] |= pat #!fixme : np.uint16 &&  list-as-bmap || pat

	#LEARN: for specfied indecies flip bits in the pattern to get closer
	def nudge(self, idxs, pat):
		for i,row in enumerate(idxs) : #idxs are sorted by closness
			# ? nudge fade as it go further from best match or not
			dist = int(self.nudge_step * self.fade(i) ) if self.fade else self.nudge_step
			#print "i,dist> %s, %s" % (i, dist)
			diff = self.mem[int(row),:] ^ pat #where do they differ
			cnt = diff.bmap.count()
			if cnt == 0 : continue # no diffs, skip it
			flip_cnt = dist if dist <= cnt else cnt #how many bits to flip
			diff_idxs = diff.bmap.one_idxs()
			#pick random bits where the two patterns differ
			flip_idxs = np.random.choice(diff_idxs,flip_cnt,replace=False)
			# .. and flip them ...nudging patterns closer
			for i in flip_idxs :	self.mem[int(row),int(i)] ^= BMap1D.ONE


#========== Processes =================================================

	def process(self, data, op=OVERLAP):
		if op == Memory.OVERLAP : res = self.overlap(data)
		else: res = self.distance(data)
		od = BMap2D(self.mem.nrows, self.mem.ncols, res)
		return od

	#DEFAULT WTA method, most propably you should provide your own, this is just template
	def winners(self, overlap_mem) :
		# count the one's in every match and pick the winners
		win_idxs = np.argsort( - overlap_mem.count_ones(axis='rows') )[:self.winners_count]
		return win_idxs

	def learn(self, idxs, pat, op=UNION):
		if op == Memory.UNION : self.union(idxs,pat)
		else : self.nudge(idxs, pat)

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






