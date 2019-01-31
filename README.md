##### Documentation : check ![docs](https://github.com/vsraptor/bbhtm/tree/master/docs) directory OR [igrok.site](http://igrok.site/bbHTM.html)

---

# bbhtm
bare bone Hierarchial Temporal Memory ([bbHTM](http://www.igrok.site/bbHTM.html))

## What is this ?

This is description and implementation of Hierarchial Temporal Memory ([HTM](http://numenta.org/)).
HTM is a theory of the neuro-cortex part of the brain tailored toward software implementation.

### How to install ?

```
# apt-get install python-numpy
# apt-get install python-matplotlib
# apt-get install python-scikits-learn
# pip install bitarray
# 

# git clone git@github.com:vsraptor/bbhtm.git bbhtm
```

### How to test ?

```
#cd bbhtm/lib
#ipython --pylab

> sys.path.append('test')
> from data_test import *
> dt = DataTest(data_set='ny')
> dt.new_test(name='5x300', nrows=5, data_size=300)
> dt.first.run(end=1000)
> dt.first.plot_data()
```

##### Documentation : check ![docs](https://github.com/vsraptor/bbhtm/tree/master/docs) directory OR [igrok.site](http://www.igrok.site/bbHTM.html)

