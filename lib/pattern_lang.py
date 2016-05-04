import sys
from lepl import *
import numpy as np

#Flatten list of list of list .... LoL
def flatten(lst):
	for el in lst :
		if isinstance(el, basestring) : yield el
		else :
			try: #if elem is list, process is recursively
				for e in flatten(el): yield e
			except TypeError : #if is not list return it
				yield el

class PatternLang:

	def __init__(self):
		self.grammar = []
		self.build_grammar()

	def node(self,val):
		return val

	def random_num(self,val):

		return np.random.randint(int(val[1:]))

	def fun(self, val):
		#print val[2:]
		if val[:2] == '&R' : return self.random_num(val[2:])
		return 0


	def calc(self,lst):
		if len(lst) >= 3:
			if lst[1] == '*' : return [ lst[0] ] * lst[2]
			if lst[1] == ':' :
				#extract only the numbers
				args = filter(lambda n: isinstance(n,int), lst)
				return range( *args )
		return lst

	def process(self,lst):
		for i in range(len(lst)): #go over the list

			if isinstance(lst[i],list): #if list process it
				lst[i] = self.process(lst[i]) #recursivly
		#it is operation, do it
		return self.calc(lst)

	def build_grammar(self):
		#definition of tokens
		fun = Token('&[A-Za-z0-9\.]+') >> self.fun
		rand_num = Token('R[0-9]+') >> self.random_num
		num = Token('[\+\-]?[0-9]+') >> int
		comma = Token(',')
		spaces = Token('[ \t]+')[:]
		dcol = Token(':')
		mult = Token('\*')
		left_bracket = Token('\(')
		right_bracket = Token('\)')


		with Separator(~spaces):
			nums = num | rand_num
			repeat = nums & mult & nums > self.node
			#greeder first
			ranges = nums & dcol & ( (nums & dcol & nums) | nums ) > self.node
			ops = repeat | ranges | nums | fun #operations
			op_list = ops[1:,~comma] #more than one ops separated by comma
			group = Delayed() #there will something encased in brackets
			group_repeat = group & mult & nums > self.node #like a repeat but for block
			group_list = (group_repeat | group | op_list | ops)[1:,~comma] #block-list
			group += ~left_bracket & group_list & ~right_bracket > self.node #finally define the block
			atom = group_repeat | group | ops #group or standalone op
			self.grammar = atom[1:,~comma] > self.node

	def parse(self,txt):
		return self.grammar.parse(txt)

	def generate(self,pattern):
		return list( flatten( self.process( self.parse(pattern) ) ))


def test():
	arg = ''
	if len(sys.argv) > 1 : arg = sys.argv[1] 
	pat = arg if arg else '3*4,(2*4,1:5)*2,(5*2,3*3)'
	print pat
	p = PatternLang()
	lst = p.parse(pat)[0]
	print lst
	res = p.process(lst)
	print res
	print list(flatten(res))


if __name__ == '__main__' : pass
