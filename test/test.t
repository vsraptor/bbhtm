#!/usr/bin/env python
import os, sys
basedir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.abspath(os.path.join(basedir, '../lib'));
sys.path.append(libdir)

import TAP.Simple
from bitarray import bitarray
from bmap2D import BMap2D

b = BMap2D(nrows=10,ncols=10)
b.set(b.rand_bmap)

ok = TAP.Builder.create(15).ok

zeros = b.mk_item()
ones = b.mk_item()
ones.setall(1)
b[0,:] = zeros
b[1,:] = ones
print b
print "zeros : %s" % zeros
print "ones : %s" % ones

ok(1)
print
print "Equality checks ...."

ok(b[0,:].bmap == zeros, "b[0,:].bmap == zeros")
ok(b[1,:].bmap == ones, "b[1,:].bmap == ones")
ok(b[0,:] == zeros, "b[0,:] == zeros ...")
ok(b[1,:] == ones, "b[1,:] == ones ...")

ok(b[0,:] != ones, "b[0,:] != ones ...")
ok(b[1,:] != zeros, "b[1,:] != zeros ...")

ok(b[2] == b[2], "b[2] == b[2]")
ok(b[2,:].bmap == b[2,:].bmap, "b[2,:].bmap == b[2,:].bmap")

ok(b[2,:] == b[2,:], "b[2,:] == b[2,:]")
ok(b[:,2] == b[:,2], "b[:,2] == b[:,2]")

ok(b[2,:][3] == b[23], "b[2,:][23] == b[23]")

ok(b[3,:] == b.bmap[30:30+b.ncols], "rows: b[3,:] == b.bmap[30:40]")
ok(b[3,:] == b[30:30+b.ncols], "rows: b[3,:] == b[30:40]")
ok(b[:,0] == b.bmap[0:b.len:b.ncols], "cols:  b[:,0] == b.bmap[0:b.len:b.ncols]")
ok(b[:,0] == b[0:b.len:b.ncols], "cols:  b[:,0] == b[0,:b.len:b.ncols]")

print
print "bit operations ..."
ok( (b[0,:] & zeros) == zeros, "(b[0,:] & zeros) == zeros")
ok( (b[0,:] & ones) == zeros, "(b[0,:] & zeros) == ones")
ok( (b[0,:] | zeros) == zeros, "(b[0,:] | zeros) == zeros")
ok( (b[0,:] | ones) == ones, "(b[0,:] | zeros) == ones")
ok( (b[1,:] & ones) == ones, "(b[1,:] | ones) == ones")

print
print "list indecies ..."
ok(b[[1]] == [ b.bmap[1] ], "b[[1]] == [ b.bmap[1] ]")
ok(b[[1,5]] == [ b.bmap[1], b.bmap[5] ], "b[[1,5]] == [ b.bmap[1], b.bmap[5] ]")
ok(b[5,[5]] == bitarray( b.bmap[25] ) , "!!!")


ok(b[[1]] == [ b[1] ], "b[[1]] == [ b[1] ]")
ok(b[[1,5]] == [ b[1], b[5] ], "b[[1,5]] == [ b[1], b[5] ]")
ok(b[5,[5]] == b[25], "x!!!")
ok(b[[5],[5]] == b[25], "!!!")
#ok(b[[0,1],[5]] == b[[

print b[[5],[5]]
print bitarray( b.bmap[25] )


print
print "slice indecies ..."


print
print "assignments ..."

#assign single_value/bitarray/bmap to row's/col's

##RETURN COLS instead of ROWS when x[:, ...]
