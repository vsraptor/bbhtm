# bbhtm
bare bone Hierarchial Temporal Memory

## What is this ?

This is description and implementation of Hierarchial Temporal Memory (HTM).
HTM is a theory of the neuro-cortex part of the brain tailored toward software implementation.

### How to install ?

```
> pip install numpy
> pip install matplotlib
> pip install bitarray
> git clone git@github.com:vsraptor/bbhtm.git bbhtm
```

### How to test ?

> cd bbhtm/lib

ipython --pylab

sys.path.append('test')

from data_test import *

dt = DataTest(data_set='ny')

dt.new_test(name='5x300', nrows=5, data_size=300)

dt.run_test(name='5x300', end=1000)

dt.first.plot_data()



