from bitarray import bitarray
import numpy as np
import itertools
import operator as op
import os
from base import Base
import utils


def lshift(self, cnt):
	return self[cnt:] + type(self)('0') * cnt
def rshift(self, cnt):
	return type(self)('0') * cnt + self[:-cnt]

bitarray.__lshift__ = lshift
bitarray.__rshift__ = rshift


#Implements 2D bit-binary functionality using 1D continious bitarray

class BMap2D(Base):

	def __init__(self, nrows, nbits=None, val=None, randomize=0, ncols=None):
		self.nrows = nrows
		self.ncols = ncols if ncols else nbits
		assert self.ncols , "When creating BMap2D, please provide ncols|nbits"
		self.len = self.nrows * self.ncols
		self.ext = 'bmap'
		self.bmap = bitarray(self.len)
		self.index = 0
		self.erase()
		if randomize :#should we generate random noise
			many = int(self.len * randomize)
			idxs = np.random.randint(0,self.len,many)
			for i in np.nditer(idxs) : self.bmap[i] = 1

		self.set(val)


	@property
	def fill(self): return self.bmap.count() / float(self.len)
	@property
	def avg_item_fill(self): return np.average(self.count_ones() / float(self.ncols))
	@property
	def max_item_fill(self): return np.max(self.count_ones() / float(self.ncols))

	@property
	def info(self):
		s = "> 2D Bitmap -----\n"
		s += "Dims in bits : %s,%s\n" % (self.nrows, self.ncols)
		s += "Mem use : %0.2fMb\n" % self.mbytes

		s += "Fill %%: %0.2f%%\n" % self.fill
		s += "Avg item %% fill: %0.2f%%\n" % self.avg_item_fill
		s += "Max item %% fill: %0.2f%%\n" % self.max_item_fill
		print s


	def set(self,val): #elsif is evil
		if val is None : return

		if isinstance(val, BMap2D) :
			assert len(self.bmap) == len(val.den), "SDRD: assignment size mistmatch"
			self.bmap = val.bmap
			return
		if isinstance(val, np.ndarray) :
			assert self.nrows * self.ncols == val.size, "numpy: assignment size mistmatch"
			self.bmap = utils.np2bits(val)
			return

		#default case : hope it is bitarray!
		assert self.nrows * self.ncols == len(val), "bitarray: assignment size mistmatch"
		self.bmap = val

	@staticmethod
	def from_np(ary):
		nrows, ncols = ary.shape
		return BMap2D(nrows=nrows,ncols=ncols, val=ary)


	def mk_item(self) :
		val = bitarray(self.ncols)
		val.setall(0)
		return val

	@property
	def rand_item(self):
		return bitarray(list(np.random.randint(0,2,self.ncols)))

	@property
	def rand_bmap(self):
		return bitarray(list(np.random.randint(0,2,( self.nrows * self.ncols) )))

	@property
	def shape(self): return (self.nrows,self.ncols)

	def length(self): return self.len
	def count(self): return self.bmap.count()
	def zeros(self): self.bmap.setall(0)
	def ones(self) : self.bmap.setall(1)

	def find_ones(self):
		one = bitarray(1); one[0] = 1
		idxs = self.bmap.search(one)
		return np.array(idxs,dtype=np.uint16)


	def repeat(self,val,times=None):
		if times is None : times = self.nrows
		return val * times

	def count_ones(self,axis='rows'):
		if axis == 'rows' :
			rv = np.zeros(self.nrows,dtype=np.int)
			for i in xrange(self.nrows):
				rv[i] = self.get_row(i).count()
		else :
			rv = np.zeros(self.ncols,dtype=np.int)
			for i in xrange(self.ncols):
				rv[i] = self.get_col(i).count()

		return rv

	def erase(self): self.bmap.setall(0)

	def rotate(self,deg=90):
		tmp = bitarray(self.len)
		for r in xrange(self.ncols) :
			pos = r * self.nrows
			tmp[pos : pos + self.nrows ] = self.bmap[ r : self.len : self.ncols ]
		self.bmap = tmp
		cols = self.ncols
		self.ncols = self.nrows
		self.nrows = cols


	def __lshift__(self, cnt): self.bmap <<= ( cnt * self.ncols )
	def __rshift__(self, cnt): self.bmap >>= ( cnt * self.ncols )

	def __and__   (self,b):
		bmap = b.bmap if isinstance(b, BMap2D) else b
		return BMap2D( self.nrows, self.ncols, self.bmap & bmap )
	def __or__    (self,b):
		bmap = b.bmap if isinstance(b, BMap2D) else b
		return BMap2D( self.nrows, self.ncols, self.bmap | bmap )
	def __xor__   (self,b):
		bmap = b.bmap if isinstance(b, BMap2D) else b
		return BMap2D( self.nrows, self.ncols, self.bmap ^ bmap )
	def __invert__(self)  :
		bmap = b.bmap if isinstance(b, BMap2D) else b
		return BMap2D( self.nrows, self.ncols, ~ bmap )

	def __eq__(self, right) :
		if isinstance(right, BMap2D): return self.bmap == right.bmap
		if isinstance(right, bitarray): return self.bmap == right
		return NotImplemented

	def __ne__(self, right) :
		if isinstance(right, BMap2D): return self.bmap != right.bmap
		if isinstance(right, bitarray): return self.bmap != right
		return NotImplemented

	def __iter__(self): return self

	def next(self):
		if self.index >= self.nrows:
			self.index = 0
			raise StopIteration
		else:
			rv = self.get_row(self.index)
			self.index += 1
			return rv

	# bm[int,:]
	def get_row(self,row) :
		if row < 0 : row = self.nrows - abs(row)
		assert row >= 0 and row < self.nrows, "row idx out of range : %s" % row
		pos = row * self.ncols
		return self.bmap[pos: pos + self.ncols]

	#bm[:,int]
	def get_col(self,col) :
		if col < 0 : col = self.ncols - abs(col)
		assert col >= 0 and col < self.ncols, "column idx out of range : %s" % col
		return self.bmap[col : self.len : self.ncols]

	#bm[int,:] = val
	def set_row(self,row, val) :
		if not isinstance(val,int) :
			assert val.length() == self.ncols, "the size of the value differ from the number of cols"
		if row < 0 : row = self.nrows - abs(row)
		assert row >= 0 and row < self.nrows, "row idx out of range : %s" % row
		pos = row * self.ncols
		if isinstance(val, BMap2D) :
			self.bmap[pos: pos + self.ncols] = val.bmap
		else :
			self.bmap[pos: pos + self.ncols] = val

	#bm[:,int] = val
	def set_col(self,col,val) :
		if not isinstance(val,int) :
			assert val.length() == self.nrows, "the size of the value differ from the number of rows"
		if col < 0 : col = self.ncols - abs(col)
		assert col >= 0 and col < self.ncols, "column idx out of range : %s" % col
		if isinstance(val, BMap2D) :
			self.bmap[col : self.len : self.ncols] = val.bmap
		else :
			self.bmap[col : self.len : self.ncols] = val

	#bm[int,int]  and bm[int,int] = val
	def row_col(self,row,col,val=None):
		assert row >= 0 and row < self.nrows, "row idx out of range : %s" % row
		assert col >= 0 and col < self.ncols, "column idx out of range : %s" % col
		if row < 0 : row = self.nrows - abs(row)
		if col < 0 : col = self.ncols - abs(col)

		pos = row * self.ncols + col
		if val is None : return self.bmap[pos : pos+1]
		self.bmap[ pos : pos+1 ] = val


	#bm[int,:], bm[[1,2,3],:] , bm[1:10:2, :]
	def get_rows(self, lst, ret='bmap'): #works with numpy array as list

		if isinstance(lst,int) :
			if ret == 'ba' : return self.get_row(lst)
			else : lst = [lst]

		lst_len = len(lst)
		bm = BMap2D(nrows=lst_len,ncols=self.ncols)
		for i, row in enumerate(lst) :
			bm.set_row(i, self.get_row(row))
		return bm

	#bm[:,int], bm[:,[1,2,3]] , bm[:, 1:10:2]
	def get_cols(self, lst, ret='bmap'): #works with numpy array as list

		if isinstance(lst,int) :
			if ret == 'ba' : return self.get_col(lst)
			else : lst = [lst]

		lst_len = len(lst)
		bm = BMap2D(nrows=lst_len,ncols=self.nrows)
		for i, col in enumerate(lst) :
			bm.set_row(i, self.get_col(col))
		return bm

	def set_rows(self, lst, vals):
		if isinstance(lst,int) :
			self.set_row(lst,vals)
			return

		if isinstance(vals, int) :
			lst_len = len(lst)
			for i, row in enumerate(lst): self.set_row(row,vals)
		else :
			assert isinstance(vals, (bitarray,BMap2D)), "expecting bitarray or BMap2D"
			if isinstance(vals,bitarray) : vals = BMap2D(nrows=1, ncols=self.ncols, val=vals) #!fixme, uneeded
			lst_len = len(lst)
			assert vals.nrows == 1 or vals.nrows == lst_len, "The number of idxs differ from the number of values"
			for i, row in enumerate(lst):
				if vals.nrows == 1 : self.set_row(row, vals.bmap)
				else: self.set_row(row, vals.get_row(i-1))


	def set_cols(self, lst, vals):
		if isinstance(lst,int) :
			self.set_col(lst,vals)
			return

		if isinstance(vals, int) :
			lst_len = len(lst)
			for i, col in enumerate(lst): self.set_col(col,vals)
		else :
			assert isinstance(vals, (bitarray,BMap2D)), "expecting bitarray or BMap2D"
			if isinstance(vals,bitarray) : vals = BMap2D(nrows=1, ncols=self.ncols, val=vals) #!fixme, uneeded
			lst_len = len(lst)
	 		assert vals.nrows == 1 or vals.nrows == lst_len, "The number of idxs differ from the number of values"
			for i, col in enumerate(lst):
				if vals.nrows == 1 : self.set_col(col, vals.bmap)
				else: self.set_col(col, vals.get_col(i-1))


	@staticmethod
	def slice2range(idxs, max_val) :
		if isinstance(idxs,slice) :
			start = 0 if idxs.start is None else idxs.start
			stop  = max_val if idxs.stop is None or idxs.stop > max_val - 1 else idxs.stop + 1
			step  = 1 if idxs.step is None else idxs.step
			return xrange(start,stop,step)
		return idxs

	@staticmethod
	def is_empty_slice(s): return isinstance(s,slice) and s == slice(None,None,None)

	#bm[r2D,c2D] vs bm[1D]
	def get_byidxs(self,idxs):
		#print ">>> %s" % (idxs,)
		#In case 2D indecies are specified
		if isinstance(idxs,tuple) :
			rows, cols = idxs

			if BMap2D.is_empty_slice(rows) : #cols only case
				return self.get_cols( BMap2D.slice2range(cols, self.ncols) )
			else : rows = self.slice2range(rows, self.nrows)

			if BMap2D.is_empty_slice(cols) : #rows only case
				return self.get_rows( BMap2D.slice2range(rows, self.nrows) )
			else : cols = self.slice2range(cols, self.ncols)

			#they are no longer slices but ranges
			bm = self.get_rows(rows)
			rv = bm.get_cols(cols)
			rv.rotate()
			return rv

		else: #1D index

			if isinstance(idxs,(list,np.ndarray)) :
				rv = []
				for i in idxs : rv.append( self.bmap[i] )
				return rv
			else : return bitarray( self.bmap[idxs] )


	def set_byidxs(self, idxs, vals):
		#print ">>> %s" % (idxs,)

		#In case 2D indecies are specified
		if isinstance(idxs,tuple) :
			rows, cols = idxs

			if BMap2D.is_empty_slice(rows) : #cols only case
				return self.set_cols( BMap2D.slice2range(cols, self.ncols), vals )
			else : rows = self.slice2range(rows, self.nrows)

			if BMap2D.is_empty_slice(cols) : #rows only case
				return self.set_rows( BMap2D.slice2range(rows, self.nrows), vals )
			else : cols = self.slice2range(cols, self.ncols)

			#they no longer slices but ranges or ints
			if isinstance(rows,int) : rows = [rows]
			if isinstance(cols,int) : cols = [cols]

			#!fixme : there are faster but more complex ways
			if isinstance(vals,int) :
				for r,c in itertools.product(rows,cols) : self.row_col(r,c,vals)
			else :
				assert (len(rows),len(cols)) == vals.shape, "Mismatch in sizes"
				for i,r in enumerate(rows) :
					for j,c in enumerate(cols): #self.bmap[r,c] = vals[i,j]
						self.row_col(r,c, vals.row_col(i,j) )

		else: #1D index

			if isinstance(idxs,(list,np.ndarray)) :
				for i in idxs : self.bmap[i] = vals
			else : self.bmap[idxs] = vals

	"""
		Given list of 1D coordinates, returns list-of-tuples with 2D coordinates
	"""
	def coords2D(self, idxs):
		rv = []
		for i in idxs :
			row = int( i / self.nrows )
			col = int( i % self.ncols )
			rv.append( (row,col) )
		return rv

	def coords1D(self,idxs) :
		rv = []
		for r,c in idxs :
			rv.append( r * self.nrows + c )
		return rv


	def reduce(self, lam, axis='rows'):
		if axis == 'rows' :
			rv = np.zeros(self.nrows, dtype=np.int)
			for r in xrange(self.nrows):
				pass

	def __getitem__(self,idxs):
		return self.get_byidxs(idxs)


	def __setitem__(self,idxs,val):
		self.set_byidxs(idxs,val)

	def __repr__(self):
		astr = ''
		try : #jupyter does not have terminal
			height, width = os.popen('stty size', 'r').read().split()
		except ValueError :
			height, width = 20, 80

		width = int(width) - 12
		step = 1 if self.nrows < 30 else self.nrows/30
		for i in xrange(0,self.nrows,step) :
			display = ''

			if (self.ncols > width) :
				val = self.get_row(i)
				display = val[0:width/2].to01() + ' ... ' + val[-width/2:].to01()
			else :
				display  = self.get_row(i).to01()

			astr += str(i) + "| " + display + "\n"
		return astr

#	def __repr__(self): return self.__str__()

	@property
	def nbytes(self): return len(self.bmap) / 8.
	@property
	def kbytes(self): return self.nbytes / 1024.
	@property
	def mbytes(self): return self.kbytes / 1024.

