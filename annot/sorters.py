"""
sorters.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import numpy as np

from annot.pattern import Factory
from annot.mining import filter_nans
from annot.mining import ZScore, PCA


class SortingError(Exception):
    pass


class Sorter(object):
    """Class to implement the factory desing pattern. The __init__ method of
    this class returns the requestest child-instance. Arguments of the child
    classes are delegated transparently to the child class's __init__() methods.

    >>>pcasorter = Sorter(Sorter.PcaSorter, 1, 3)
    >>><__main__.PcaSorter object at 0x1004a7190>
    """

    __metaclass__ = Factory

    @classmethod
    def sorters(cls):
        return cls._classes.keys()


    def _data_from_items(self, items):

        nitems = len(items)
        nfeatures = items[0].features.size
        data = np.empty((nitems, nfeatures))

        for i, item in enumerate(items):
            data[i, :] = item.features

        return data


# class PcaBackProjectedDistance(Sorter):
#     """Sorting data by performing a PCA, taking only 99% of the variance,
#     back projecting the the reduced feature set and sort after the difference
#     to the original features."""

#     def __init__(self, items, *args, **kw):
#         super(PcaBackProjectedDistance, self).__init__(*args, **kw)
#         self.data = self._data_from_items(items)

#     def __call__(self):

#         # PCA does the z scoring automatically
#         # zscored mean value of pca procjected treedata
#         zs = ZScore(self.data)
#         data_zs = zs.normalize(self.data)
#         data_zs = filter_nans(data_zs)

#         pca = PCA(data_zs, minfrac=0.01)
#         data_pca = pca.project(data_zs)

#         # inverse projection of the data
#         data2 = pca.iproject(data_pca)
#         delta = data_zs - data2
#         distsq = [np.power(d, 2).sum() for d in delta]

#         return -1.*np.sqrt(distsq)



class CosineSimilarity(Sorter):
    """Sorting data by using the Euclidic distance of the z-scored data as
    similarity measurement."""


    def __init__(self, items, *args, **kw):
        super(CosineSimilarity, self).__init__(*args, **kw)
        self.data = self._data_from_items(items)
        self.treedata = None

    def __call__(self):
        # z-scoring

        if self.treedata is None:
            raise SortingError("No examples for similarity measure available!")

        zs = ZScore(self.data)
        data_zs = zs.normalize(self.data)

        # z-scored mean value of pca procjected treedata
        mu = zs.normalize(self.treedata)
        data_zs, mu = filter_nans(data_zs, mu)

        mu = mu.mean(axis=0)
        denom = np.sqrt((mu**2).sum())*np.sqrt((data_zs**2).sum(axis=1))
        s_cos = np.sum(mu*data_zs, axis=1)/denom
        return -1.0*s_cos


class ClassLabel(Sorter):
    """Sorts items by class label."""

    def __init__(self, items, *args, **kw):
        super(ClassLabel, self).__init__(*args, **kw)
        self.class_labels = [i.class_.label for i in items]
        self.annotations = [i.isTrainingSample() for i in items]


    def __call__(self):
        try:
            return -1*(np.array(self.class_labels)*10 + \
                       np.array(self.annotations, dtype=bool))

        except TypeError:
            raise SortingError("No class labels available yet!")


class EucledianDistance(Sorter):
    """Sorting data by using the cosine similarity metric of the z-scored data.
    """

    def __init__(self, items, *args, **kw):
        super(EucledianDistance, self).__init__(*args, **kw)
        self.data = self._data_from_items(items)
        self.treedata = None

    def __call__(self):
        # z-scoring

        if self.treedata is None:
            raise SortingError("No examples for similarity measure available!")

        zs = ZScore(self.data)
        data_zs = zs.normalize(self.data)

        # z-scored mean value of pca procjected treedata
        mu = zs.normalize(self.treedata)
        data_zs, mu = filter_nans(data_zs, mu)

        mu = mu.mean(axis=0)
        distsq = [np.power((x - mu), 2).sum() for x in data_zs]
        return np.sqrt(distsq)
