import logging as log
import csv
import numpy as np
from pattern_lang import PatternLang
#data definition
dd = {
	'ny' : {
		'fname' : '../data/nyc_taxi.csv', 'count' : 17522, 'field' : 'passenger_count', 'min': 0, 'max' : 40000, 'granularity' : 50, 'scale' : 1,
		'delta_min' : 0, 'delta_max' : 20000, 'delta_granularity' : 10, 'delta_scale' : 1, 'delta_lift' : 10000
	},
	'dollar' : {
		'fname' : '../data/eurusd_1h.csv', 'count' : 65040, 'field' : 'close', 'min' : 8500, 'max' : 16100, 'granularity' : 10, 'scale' : 10000,
		'delta_min' : 0, 'delta_max' : 610, 'delta_scale' : 1, 'delta_lift' : 300, 'delta_granularity' : 2
	 },
	'hot-gym' : {
		'fname' : '../data/rec-center-hourly.csv', 'count' : 4392, 'field' : 'kw_energy_consumption', 'min': 0, 'max' : 90, 'granularity' : 1, 'scale' : 1, 'lift' : 0,
		'delta_min' : 0, 'delta_max' : 100, 'delta_granularity' : 1, 'delta_scale' : 1, 'delta_lift' : 10
	},

	'sine' : { 'fname' : '../data/sine.csv', 'count' : 2003, 'field' : 'data', 'min': 0, 'max' : 21050, 'granularity' : 10, 'scale' : 10000, 'lift' : 11000 }
}

class DataSet:

	def __init__(self, data_source='ny', pat=None) :
		self.ds = data_source #data source
		self.data = None
		self.data_delta = None
		self.pl = None
		if pat is not None :
			self.generate_sequence(pat)
			self.ds = 'pat'
			dd[self.ds] = { 'count' : self.data.size, 'min' : self.data.min(), 'max' : self.data.max(), 'granularity' : 10, 'scale' : 1, 'lift' :0 }
		else :
			if self.ds in dd :
				self.fname = dd[self.ds]['fname']
				self.read_data(self.fname)
			else : raise Exception("%s data set does not exist" % self.ds)


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
		return dd[self.ds][key]

	def generate_sequence(self, pat):
		if self.pl is None : self.pl = PatternLang()
		self.data = np.array( self.pl.generate(pat), dtype=np.uint16)

	@staticmethod
	def list_datasets() : return dd.keys()

	@staticmethod
	def dataset_desc() : return dd

