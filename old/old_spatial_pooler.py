import numpy as np
import matplotlib.pylab as plt
import random


def unique_count(a):
    unique, inverse = np.unique(a, return_inverse=True)
    count = np.zeros(len(unique), np.int)
    np.add.at(count, inverse, 1)
    return np.vstack(( unique, count)).T

class SpatialPooler:

#  Basic internal structure is two 2D arrays of permanence and segments.
#  Permanence is the strength of a connection to data bit.
#  Segment (bunch of synapses) tells which permanence is connected to which data bit.
#  Multiplying data[segments] * perms =generates=> signal, which is used to decide
#   the winning bits of the final SDR-1s and eventualy to learn (i.e. modify permanences)

# *** Algorithm diagram :
# train
#   +--==> winners => process
#   +----> learn
#   +----> boost

	def __init__(
		self, data_size,
		perm_thresh=0.2,
		overlap=0.5, segments_count=1024,
		learn_rate=0.02, forget_rate=0.01, learnit=True,
		winners_percent=0.02,
		boost=0.001, boost_thresh=0.2, boostit=True,
		activity_syn_thresh=0.1, avoid_trivial=True,
		win_steep_thresh=False, #winner pick
		learn_by_data=False, #learn_by_win
		activation_fun=None
	):

		self.data_size = data_size
		#in a sense the count of bits of the output
		self.segments_count = segments_count
		#the size-% of the sample from the data for every segment
		self.overlap = overlap
		#overlap in bits
		self.segment_size = int(data_size * overlap)
		# % of 1s in a training cycle
		self.winners_percent = winners_percent
		self.winners_count = int(self.winners_percent * self.segments_count)
		self.learnit = learnit
		self.learn_rate = learn_rate
		self.forget_rate = forget_rate
		# only learn from "potential connctions" segments <-> data i.e. when both are 1  (learn is diff than train!!)
		self.learn_by_data = learn_by_data
		# threshold above which permanence value is treated as ON|1
		self.perm_thresh = perm_thresh
		self.win_steep_thresh = win_steep_thresh
		#should I boost non-winning permanences
		self.boostit = boostit
		self.boost = boost # ... by how much
		self.boost_thresh = boost_thresh
		self.activity_syn_thresh = activity_syn_thresh
		self.activation_fun = activation_fun

		#if True only segments who have number of active synapses pass a threshold will be used as "signal" eg. for training
		self.avoid_trivial = avoid_trivial
		self.trivial_count = int(self.segment_size * self.activity_syn_thresh)

		self.cycles = 0 #how many train cycle we have ran

		#keep track of activity i.e. how often a segment was used, low-activity ==> boosting
		self.activity = np.zeros(self.segments_count)

		#set random permanence values
		self.perm = np.fmax(0, np.fmin(1, np.random.normal(perm_thresh,perm_thresh,(self.segments_count, self.segment_size)) ))
		#!!! self.perm = np.zeros((self.segments_count, self.segment_size)) + self.perm_thresh

		#connect every segment-synapse with data-bits in a random manner : @[segment_idx , synapses_idx ]
		self.segments = np.zeros((self.segments_count, self.segment_size), dtype='uint16')
		#!fixme: make sure it connects to every bit of the data in at least one segment
		for idx in xrange(self.segments_count) : #non repeated per segment
		 	self.segments[idx,:] = np.array( random.sample(xrange(data_size), self.segment_size) )
		#.. it seems potential connections are uniformly distributed, as seen by ploting a self.data_coverage_hist() of connection count to every data bit !! 

		self.info()


	def info(self):
		print "Data size : %s" % self.data_size
		print "Segments shape : %s" % (self.segments.shape,)
		print "Overlap : %s" % self.overlap
		print "Win: %s%% : %s bits" % (self.winners_percent, self.winners_count)
		if self.avoid_trivial : print "Trivial> %s%% : %s" % (self.activity_syn_thresh, self.trivial_count)


	#update permanance values in the winning segments
	def learn(self,seg_idxs):
		#create inc/dec template, which is used to update permanences afterwards
		if self.learn_by_data : tmp = self.data[self.segments].copy()
		else : tmp = self.signal.copy()

		#.. permanence of synapses who guessed correctly are incremented, otherwise decremented
		tmp[ tmp == 0  ] = - self.forget_rate
		tmp[ tmp > 0 ] = self.learn_rate

		#only the winnig segments are impacted
		for idx in seg_idxs: #keep within [0,1] range
			self.perm[idx] = np.fmax(0, np.fmin(1, self.perm[idx] + tmp[idx] ))

	def boosting(self):
		#update the activity counts of the winning segments
		self.activity[ self.top_idxs ] += 1
		#how many of segments to boost
		cnt = int(self.segment_size * self.boost_thresh)
		#which segments exactly to boost
		boost_idxs = np.argsort(self.activity)[0:cnt]
		#... boost them
		self.perm[ boost_idxs, :] += self.boost

	#winners take all i.e. which bits are treated as 1
	def winners(self, data):
		self.process(data) #first pass data trought "permanances"
		#signal strength produced by every segment
		if self.win_steep_thresh : self.scores = np.sum(self.signal > 0, axis=1) # 0 <> 1
		else :
			if self.activation_fun == None : self.scores = np.sum(self.signal, axis=1)
			else : self.scores = np.sum(self.scurve(self.signal), axis=1)
		#get the winner segments
		self.top_idxs = np.argsort( -self.scores )[0 : self.winners_count]
		return self.top_idxs


	def train(self,data):
		idxs = self.winners(data) #output SDR-1s
		if self.learnit : self.learn(idxs)
		if self.boostit : self.boosting()

	#pass data trough all the segments : data => [segments] => signal
	#.. signal is 2D ary : data -via-> every segment
	def process(self,data):
		if self.learn_by_data : self.data = data #!fixme ugly, copying data

		#signal is the result of processing the data trought the spooler
		self.signal = data[self.segments] * self.perm
		#clean up all permanences below the threshold i.e. set to 0s
		self.signal[ self.signal <= self.perm_thresh ] = 0

		#avoid trivial patterns : cleanup segments which does not have thresh-number of active synapses
		if self.avoid_trivial :
			#everything > perm_thresh is treated as 1, so we can count the number of active synapses
			self.scores = np.sum(self.signal > self.perm_thresh, axis=1)
			#... pick only segments which have enough active synapases
			rows = np.argwhere(self.scores < self.trivial_count).T
			#print "rows> %s : max:%s" % (rows.size, np.max(self.scores))
			self.signal[rows] = 0 #np.zeros(self.segment_size)

		return self.signal


	def train_loop(self,ary):
		for data in ary : self.train(data)


	def data_coverage_hist(self):
		plt.hist( self.segments.flatten(), bins=self.segment_size, linewidth=0 )

	def output(self):
		tmp = np.zeros(self.segments_count)
		tmp[ self.top_idxs ] = 1
		return tmp


	#convert from index-SDR to 0|1-SDR
	def idx2bin(self, idxs):
		tmp = np.zeros(self.data_size)
		tmp[idxs] = 1
		return tmp

	#given input binary give the output SDR
	def encode(self, data):
		return self.idx2bin( self.winners(data) )










