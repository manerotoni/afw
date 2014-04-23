"""
sorters.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import numpy as np
from af.mining import filter_nans
from af.mining import ZScore, PCA


class SortFactory(type):
    """Meta class to implement the factory design pattern"""

    def __init__(cls, name, bases, dct):

        if len(cls.__mro__)  >= 3:
            bases[0]._sorters[name] = cls
            setattr(bases[0], name, name) # perhaps an int?
        return type.__init__(cls, name, bases, dct)

    def __call__(cls, sorter=None, *args, **kw):

        if sorter in cls._sorters.keys():
            return cls._sorters[sorter](*args, **kw)
        elif sorter is None:
            return type.__call__(cls, *args, **kw)
        elif cls in cls._sorters.values():
            allargs = (sorter, ) + args
            return type.__call__(cls, *allargs, **kw)


class Sorter(object):
    """Class to implement the factory desing pattern. The __init__ method of
    this class returns the requestest child-instance. Arguments of the child
    classes are delegated transparently to the child class's __init__() methods.

    >>>pcasorter = Sorter(Sorter.PcaSorter, 1, 3)
    >>><__main__.PcaSorter object at 0x1004a7190>
    """

    __metaclass__ = SortFactory
    _sorters = dict()

    @classmethod
    def sorters(cls):
        return cls._sorters.keys()


class ZScoreSorter(Sorter):
    """Sorting data by using the Euclidic distance of the z-scored data as
    similarity measurement. Sorting is not performed, the __call__() method
    computes only the distance measure."""


    def __init__(self, data, treedata):

        self.data = data
        self.treedata = treedata

    def __call__(self):
        # z-scoring
        zs = ZScore(self.data)
        data_zs = zs.normalize(self.data)

        # z-scored mean value of pca procjected treedata
        mu = zs.normalize(self.treedata)
        data_zs, mu = filter_nans(data_zs, mu)

        mu = mu.mean(axis=0)
        distsq = [np.power((x - mu), 2).sum() for x in data_zs]

        return np.sqrt(distsq)


class PcaSorter(Sorter):
    """Sorting data by performing a PCA and using the Euclidic distance as
    similarity measurement. Sorting is not performed, the __call__() method
    computes only the distance measure."""

    def __init__(self, data, treedata):

        self.data = data
        self.treedata = treedata

    def __call__(self):

        # PCA does the z scoring automatically
        # zscored mean value of pca procjected treedata

        zs = ZScore(self.data)
        data_zs = zs.normalize(self.data)
        mu = zs.normalize(self.treedata)
        data_zs, mu_zs = filter_nans(data_zs, mu)

        pca = PCA(data_zs, minfrac=0.01)
        data_pca = pca.project(data_zs)
        mu_pca = pca.project(mu_zs)

        # inverse projection of the data
        data_pca_ = pca.iproject(data_pca)
        mu_ = pca.iproject(mu_pca)

        from PyQt4.QtCore import pyqtRemoveInputHook; pyqtRemoveInputHook()
        import pdb; pdb.set_trace()


        distsq = [np.power((x - mu), 2).sum() for x in data_pca]

        return np.sqrt(distsq)
