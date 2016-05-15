from __future__ import division
import numpy as np
from bmap1D import BMap1D
from math import factorial
import operator as op

def limit(x) : return np.fmax(0, np.fmin(1,x))
def binary(x) : return x.astype(int)
#p : permanence, x : data vector

#threshold hard limit : [0 ..|.. 1] =>  {0,1}
def thardlim(p,x=1,thresh=0.5): return  binary( (1 + np.sign( p*x - thresh ))/2 )
#threshold hard limit symetrical [0 ..|.. 1] => {-1, +1 }
def thardlim_sim(p,x=1,thresh=0.5): return binary( np.sign( p*x - (thresh+0.001)) )

# 0,0 => -, 1,0 => 0, 1,0 => 0, 1,1 => 1
def match(x,y): return (x + y) - 1

def backward_delta(p,x,rate=0.1) : return (x - thardlim(p)) * rate

def forward_delta(p,x,rate=0.1):
	return match( thardlim(p), x) * rate
	#return sgnlin(p,x) * rate

def compare(p,x) : return "bin    > %s <=> %s" % (thardlim(p), x)

def train(p,x,rate=0.1) :
	print "before > %s" % p
	p += forward_delta(p,x)
	print "forward> %s" % p
	p += backward_delta(p,x)
	print "back   > %s" % p
	print compare(p,x)
	return p

def delta(p,x): return x - p

def test(perm,val,percent, steps) :
	tmp = perm
	rv = [tmp]
	for i in range(steps):
		tmp = tmp + delta(tmp,val) * percent
		rv.append(tmp)
	return rv

def rolling_window(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def sigmoid(x): return 1/(1+np.exp(-x))

def scurve(x,a=0.7,epsilon=0.0001):
	#this Logistic Sigmoid has been normalized.

	min_param_a = 0.0 + epsilon
	max_param_a = 1.0 - epsilon
	a = max(min_param_a, min(max_param_a, a))
	a = (1/(1-a) - 1)

	A = 1.0 / (1.0 + np.exp(0 -((x-0.5)*a*2.0)))
	B = 1.0 / (1.0 + np.exp(a))
	C = 1.0 / (1.0 + np.exp(0-a))
	y = (A-B)/(C-B)

	return y

def flatten(LoL): return [item for sublst in LoL for item in sublst ]

def randbin(shape) : return np.random.randint(0,2,shape)

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def num(x) :
	try :	return int(x)
	except ValueError : return float(x)

def nCr(n,r):
	print "n,r: %s, %s" % (n,r)
	assert n >= r, "nCr : n < r !"
	r = min(r,n-r)
	if r == 0 : return 1
	numerator = reduce(op.mul, xrange(n,n-r,-1))
	denominator = reduce(op.mul, xrange(1, r+1) )
	return numerator//denominator

#count of vectors with w-bits ON that have b-bits overlap
def overlap_set(n,w,b): #nCr(n,w) are all possible combinations
	return nCr(w,b) * nCr(n-w , w-b)

#inexact match : false positive overlap set
# probability of random vector to be false positive
def fp_oset(n,w,b): return overlap_set(n,w,b) / nCr(n,w)

#exact mathch : probability of bit being 0 (zero) after M additions
def fp_union_p0(n,w,M) :
	p0 = ( 1 - (w/float(n)) )**M
	print "p1> %s" % (1 - p0)
	return p0

#inexact match: M number of stored patterns
def fp_union(n,w,b,M):
	wx = n * (1 - fp_union_p0(n,w,M))
	print "wx> %s" % wx
#	wx = w
	return fp_oset(n, int(wx), b)


#=============== SP/TP utils =======================================

def np2bits(ary):
	b = BMap1D()
	b.pack(ary.astype(np.bool).tostring())
	return b
	#return BMap1D(list(ary))

def bits2np(bits):
	 return np.fromstring(bits.unpack(), dtype=np.uint8)

#convert idxs to bit array
def idxs2bits(idxs, nbits):
	bit_ary = BMap1D(nbits)
	bit_ary.setall(0)
	for i in idxs: bit_ary[i] = 1
	return bit_ary

#hamming distance
def hd(item1, item2): return (item1 ^ item2).count()
#overlap distance
def od(item1, item2): return (item1 & item2).count()

#nudge bitstring in the direction of target
def nudge(source, target, dist):
	diff = source ^ target #where do they differ
	cnt = diff.count()
	if cnt == 0 : return # no diffs
	flip_cnt = dist if dist <= cnt else cnt #how many to flip
	diff_idxs = diff.one_idxs()
	#pick random bits where the two patterns differ
	flip_idxs = np.random.choice(diff_idxs,flip_cnt,replace=False)
	# .. and flip them ...nudging patterns closer
	for i in flip_idxs :	source[int(i)] ^= 1


#flip random bits
def flip_rand(data,cnt=0):
	if cnt == 0 : return
	flip_idxs = np.random.randint(0, len(data), cnt )
	for i in flip_idxs :	data[int(i)] ^= 1

def fade(val,lam=0.05): return np.exp(-val * lam)
