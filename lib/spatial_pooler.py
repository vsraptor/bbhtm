import numpy as np
from bmap2D import BMap2D
from memory import *
import datetime as dt
import time
import utils


class SpatialPooler(Base):

	def __init__(self, input_size, output_size, segment_size=1, winp=0.021, randomize=0.01, nudge=5, fade=None):

		self.nudge_step = nudge
		self.segment_size = segment_size
		self.ncols = input_size
		self.isize = input_size
		self.osize = output_size
		self.nrows = self.osize * self.segment_size
		self.ext = 'sp'

		self.fade = fade
		self.nudge_step = nudge

		#winners for active and predicted, pooler is calculating it on its own
		self.winners_percent = winp # % of 1s
		self.in_wc = int(self.winners_percent * self.isize) #input win count
		self.out_wc = int(self.winners_percent * self.osize) #output win count

		#adjecent connection bitmap-matrix
		self.memory = Memory(ncols=self.ncols, nrows=self.nrows, winp=winp, randomize=randomize, fade=fade, nudge=nudge)

		self.train_cycle = 0

	@property
	def info(self) :
		print "> Spatial pooler ========================================="
		print "I => O size : %s => %s" % (self.isize, self.osize)
		print "Rows, Cols : %s, %s" % (self.nrows, self.ncols)
		print "segment-size, in winc, out winc : %s, %s, %s" % (self.segment_size, self.in_wc, self.out_wc)
		print "nudge : %s" % self.nudge_step
		self.memory.info

	def winners(self, mem) :
		# count the one's in every match and pick the winners
		win_idxs = np.argsort( mem.count_ones(axis='rows') )[:self.out_wc] #smaller the better !no-minus
		return win_idxs

	def train(self, data, via=False) :
		od = self.memory.process(data, op=Memory.DISTANCE)
		idxs = self.winners(od)
		if not via : self.memory.learn(idxs,data, op=Memory.NUDGE)
		self.train_cycle += 1
		return idxs

	def predict(self, data):
		idxs = self.via(data)
		return utils.idxs2bits(idxs, self.osize)

	def via(self, data):
		return self.train(data,via=True)

