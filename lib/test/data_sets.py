import logging as log
import csv
import numpy as np
from pattern_lang import PatternLang
import sklearn.datasets

#data definition
dd = {
	'ny' : {
		'fname' : '../data/nyc_taxi.csv', 'count' : 17522, 'field' : 'passenger_count', 'min': 0, 'max' : 30000, 'granularity' : 10, 'scale' : 1,
		'delta_min' : 0, 'delta_max' : 7000, 'delta_granularity' : 10, 'delta_scale' : 1, 'delta_lift' : 1000
	},
	'dollar' : {
		'fname' : '../data/eurusd_1h.csv', 'count' : 65039, 'field' : 'close', 'min' : 8580, 'max' : 16040, 'granularity' : 10, 'scale' : 10000,
		'delta_min' : 0, 'delta_max' : 3200, 'delta_scale' : 10, 'delta_lift' : 0, 'delta_granularity' : 10
	 },
	'hot-gym' : {
		'fname' : '../data/rec-center-hourly.csv', 'count' : 4392, 'field' : 'kw_energy_consumption', 'min': 0, 'max' : 900, 'granularity' : 10, 'scale' : 10, 'lift' : 0,
		'delta_min' : 0, 'delta_max' : 1000, 'delta_granularity' : 10, 'delta_scale' : 1, 'delta_lift' : 10
	},

	'sine' : { 'fname' : '../data/sine.csv', 'count' : 2003, 'field' : 'data', 'min': 0, 'max' : 21050, 'granularity' : 10, 'scale' : 10000, 'lift' : 11000 }
}

class DataSet:

	def __init__(self, data_source='ny', pat=None) :
		self.ds = data_source #data source
		self.data = None
		self.data_delta = None
		self.pl = None

		if pat is not None : #pattern
			self.generate_sequence(pat)
			self.ds = 'pat'
			dd[self.ds] = { 'count' : self.data.size, 'min' : self.data.min(), 'max' : self.data.max(), 'granularity' : 10, 'scale' : 1, 'lift' :0 }
			return

		if self.ds in dd :
			self.fname = dd[self.ds]['fname']
			self.read_data(self.fname)
			return

		try : # SKLEARN
			methodCall = getattr(sklearn.datasets, data_source)
			self.dset = methodCall()
			self.data = self.dset.data
		except: raise Exception("%s data set does not exist" % self.ds)


	def read_data(self,fname):
		log.debug( "Reading %s ....." % self.fname )
		f = open(fname, 'rb')
		self.reader = csv.DictReader(f)
		self.data = np.zeros(dd[self.ds]['count'] , dtype=np.int)
		lift = dd[self.ds]['lift'] if 'lift' in dd[self.ds] else 0
		for i, row in enumerate(self.reader) :
			if i < 2 : continue
			self.data[i] = int( (float(row[ dd[self.ds]['field'] ]) * dd[self.ds]['scale'])  + lift )

		f.close()

	@property
	def delta(self,lift=None,scale=None):
		if lift is None : lift = dd[self.ds]['delta_lift']
		if scale is None : scale = dd[self.ds]['delta_scale']

		if self.data_delta is None :
			self.data_delta = scale * ( np.diff(self.data) + lift )

		return self.data_delta


	def get(self, key) :
		if self.ds in dd : return dd[self.ds][key]
		return 0

	def generate_sequence(self, pat):
		if self.pl is None : self.pl = PatternLang()
		self.data = np.array( self.pl.generate(pat), dtype=np.uint16)

	@staticmethod
	def list_datasets() : return dd.keys()

	@staticmethod
	def dataset_desc() : return dd


###---------------MOVE-------------- #!fixme


	#encode image (list of numbers 0-255) to binary numpy representation
	@staticmethod
	def encode_digit(data,bits=8):
		ary = []
		for d in data :
			ary += list( [ int(x) for x in list(np.binary_repr(d, bits)) ] )
		return np.array(ary)

