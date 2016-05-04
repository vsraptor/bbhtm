import numpy as np
import matplotlib.pylab as plt
import matplotlib.animation as anim
import time
from bitarray import bitarray
from base import Base
from bmap2D import BMap2D
from memory import *
import datetime as dt
import time
import utils

class TemporalMemory(Base):

	def __init__(self, ncols=None, nrows=5, winp=0.021, randomize=0.01, data_size=None, loopy_cols=True):

		self.ncols = ncols if ncols else data_size
		assert self.ncols, "need to specify ncols|data_size when creatining a memory"
		self.nrows = nrows
		self.ncells = self.ncols * self.nrows

		self.loopy_cols = loopy_cols
		self.ext = 'tm'

		#winners for active and predicted, pooler is calculating it on its own
		self.winners_percent = winp # % of 1s
		self.winners_count = int(self.winners_percent * self.ncols) # Memory winc is disregarded, because TM have is own winner() method 

		#adjecent connection bitmap-matrix
		self.memory = Memory(ncols=self.ncells,nrows=self.ncells,winp=winp,randomize=randomize,data_size=data_size)

		self.active    = BMap2D(nrows=self.nrows, ncols=self.ncols)
		self.past      = BMap2D(nrows=self.nrows, ncols=self.ncols)
		self.predicted = BMap2D(nrows=self.nrows, ncols=self.ncols)

		self.xlabel = ''
		self.ylabel = ''

		self.fig = None
		self.fig2 = None

		self.train_cycle = 0

	@property
	def info(self) :
		s = "> Temporal Memory =========================================\n"
		s += "Data size | number of columns : %s\n" % self.ncols
		s += "Memory dims (rows,cols) : %s, %s\n" % (self.active.nrows, self.active.ncols)
		s += "winc : %s\n" % (self.winners_count)
		print s
		self.memory.info

	#store current active state for learning purposes (VAL)
	def backup(self):
		self.past.bmap = self.active.bmap.copy()


	def activate(self,data) :

		self.active.erase()
		self.bursted = [] #store the list of bursted columns

		#Activate whole col or specific cell in col, depending on the predicitve state
		one = bitarray(1); one[0] = 1
		data_oncols = data.search(one)
		#predicted cols
		pred_cols = self.predicted.count_ones(axis='cols')
		for c in data_oncols :
			c = int(c) # Long ;!
			if pred_cols[c] > 0 : # if predicted cols have at least one cell ON
				self.active[:,c] = self.predicted[:,c]
			else : # .. set column on fire
				self.bursted.append(c)
				self.active[:,c] = 1


	def predict(self, idxs ):
		self.predicted.erase()
		if not self.loopy_cols : self.memory.clear_loopy(self.nrows)
		for i in idxs : self.predicted[i] = 1


 	#clean bursted columns from signal, because they don't provide useful information
	def cleanup_bursted(self):
#		print "b> %s" % self.bursted
		if len(self.bursted) > 0 :
			self.active[:,self.bursted] = 0

	#very often col will have many best candidates, pick randomly one of them
	# ... otherwise the memory usage cluster to 'top-left' show_mem() i.e. lateral-SDRs mostly uses top row of the region
	def pick_rand_from_max(self, ary):
		maxx = np.max(ary) #whos the best
		midxs = np.where(ary == maxx)[0] #idx of all max elems
		return midxs[ np.random.randint(0, midxs.size) ] #pick randomly from them


	#find the best canditate in the column, by best overlap with next learned pattern i.e. past /t-1/
	def best_in_col(self, col) :
		#holds [idx, score]
		scores = np.zeros((self.active.nrows,2),dtype=np.int)
		#go over every row in the specified column
		for i,row in enumerate(xrange(self.active.nrows)) :
			cell_idx = row * self.active.ncols + col #2D => 1D
			overlap = self.memory.mem[cell_idx,:] & self.past
			scores[i,0] = row
			scores[i,1] = overlap.count_ones()
		m = self.pick_rand_from_max(scores[:,1])
		#m = np.argmax(scores[:,1]) #^interchangable
		return scores[m,0] #max overlap row-idx

	#select the best cell in bursted column, so that we learn/store only one pattern per bursted-active-column
	def pick_best_bursted(self):
		self.cleanup_bursted()
		for col in self.bursted :
			row = self.best_in_col(col)
			self.active[row,col] = 1


	###  1D => 2D => max => 1D
	def winners(self, overlap_mem):
		# count the one's in every match/line
		overlap_counts = overlap_mem.count_ones(axis='rows')

		#shape it like .predicted array
		ary2D = overlap_counts.view()
		ary2D.shape = (self.nrows, self.ncols)
		#pick max val, for every column
		max_row_idxs = np.argmax(ary2D, axis=0) #^^vertical, pos of MAX-value in the column
		# .. the topN cols of those max-values i.e. predicted SDR
		self.top_col_idxs = np.argsort(- np.max(ary2D,axis=0) )[ :self.winners_count ]
		#pick only top rows and cols, those would be the cells we want to set in predictive state
		pred_2D_coords = max_row_idxs[self.top_col_idxs], self.top_col_idxs
		#convert the top-2D coords back to the 1D coords
		win1D_coords = np.ravel_multi_index( pred_2D_coords, (self.nrows, self.ncols) )
		return win1D_coords

	#the last predicted columns, converted to SDR-bitmap
	def predicted_sdr(self): return utils.idxs2bits( self.top_col_idxs, nbits=self.ncols )

	#process data and learn based on the outcome
	def train(self,data,via=False, anim=False, show_burst=False):

		self.activate(data)
		if anim and show_burst : self.plot()

		if not via :# LEARN
			#important! dont learn for all bursted, just for the best
			self.pick_best_bursted() #In active, deselect all but the best cells in the cols
			learn_idxs = self.active.find_ones() #CM row addresses
			self.memory.learn(learn_idxs, self.past)

		#memory uses all active cells as input, instead of Data. returns winning idxs
		overlap = self.memory.process(self.active.bmap)
		win_idxs = self.winners(overlap) #do the magic

		#set the cells in predicted state
		self.predict(win_idxs) #!this could go before the LEARN phase,
			# .. just hoping that predicting after learning may produce better results
		#copy active => past
		self.backup() #!this could move to the begining too

		self.train_cycle += 1


	#dont learn just process
	def via(self,data) : return self.train(data,via=True)

	#make prediction using last prediction as input, instead of real data
	def forward(self) :
		self.via(self.predicted_sdr())
		yield self.predicted_sdr()


#----------------------------------------------------------------------------------------


	def plot(self, cmap='Greys',pause=1):

		if self.fig is None :
			self.fig = plt.figure(1,figsize=(24,5))
			self.ax1 = self.fig.add_subplot(211)
			self.ax1.set_title('active')
			self.ax2 = self.fig.add_subplot(212)
			self.ax2.set_title('predicted')
			plt.tight_layout()
			plt.show()
		else : plt.figure(1)

		aview = self.memory.bm2np(self.active)
		pview = self.memory.bm2np(self.predicted)

		self.ax1.imshow(aview, cmap=cmap, interpolation='nearest', aspect='auto')
		self.ax2.imshow(pview, cmap=cmap, interpolation='nearest', aspect='auto')
#		plt.pause(pause)
		self.fig.canvas.draw()
		#plt.show()
		del aview
		del pview




