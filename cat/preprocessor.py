"""
preprocessor.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import numpy as np
from cat.mining import ZScore
from cat.mining import PCA


class PreProcessor(object):
    """PreProcessor is used to normalize the data and remove columns that
    contain NaN's and have zero variance. If index is None all features are
    taken into account otherwise only those specified with index. Index can
    be an integer or a list of integers.
    """

    def __init__(self, data, index=None, pca=False):

        self.data = data
        self._pca = None

        # to remove columns that contaim nan's and have zero variance
        mask_nan = np.invert(np.isnan(data.sum(axis=0)))* \
                   (data.std(axis=0) > 0.0)
        self._mask = np.ones(mask_nan.shape).astype(bool)

        if index is not None:
            self._mask[:] = False
            self._mask[index] = True

        self._mask*=mask_nan
        data = self.filter(data)
        self._zs = ZScore(data)

        if pca:
            data1 = self.normalize(data)
            self._pca = PCA(data1, minfrac=0.05)
            self.traindata = self._pca.project(data1)
        else:
            self.traindata = self.normalize(data)

    @property
    def std(self):
        return self.data.std(axis=0)

    @property
    def mean(self):
        return self.data.mean(axis=0)

    @property
    def mask(self):
        return self._mask

    @property
    def nfeatures(self):
        return self.traindata.shape[1]

    @property
    def nsamples(self):
        return self.data.shape[0]

    def normalize(self, data):
        return self._zs.normalize(data)

    def filter(self, data):
        return data[:, self._mask]

    def __call__(self, data):
        data1 = self.normalize(self.filter(data))
        if self._pca is None:
            return data1
        else:
            return self._pca.project(data1)
