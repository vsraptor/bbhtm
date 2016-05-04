import time
import numpy as np
import matplotlib.pylab as plt

class Blah:

	def __init__(self):
		self.fig = None
		self.ax1 = None
		self.ax2 = None

	def plot(self, cmap='Greys',pause=1):

		if self.fig is None :
			self.fig = plt.figure(1,figsize=(24,5))
			self.ax1 = self.fig.add_subplot(211)
			self.ax2 = self.fig.add_subplot(212)
			plt.tight_layout()
			#plt.show()
		else :
			plt.figure(1)

		#... build numpy array... FOR EXAMPLE :
		aview = np.random.randint(0,2,(5,300))
		pview = np.random.randint(0,2,(5,300))

		self.ax1.imshow(aview, cmap=cmap, interpolation='nearest', aspect='auto')
		self.ax2.imshow(pview, cmap=cmap, interpolation='nearest', aspect='auto')
		plt.pause(pause)
		self.fig.canvas.draw()


def main() :
	x = Blah()
	for i in xrange(50) :
		print i
		x.plot()
	time.sleep(30)

if __name__ == '__main__' : main()
