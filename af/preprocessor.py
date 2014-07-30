"""
preprocessor.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import numpy as np
from af.mining import ZScore


class PreProcessor(object):
    """PreProcessor is used to normalize the data and remove columns that
    contain NaN's and have zero variance.
    """

    def __init__(self, data):

        # to remove columns that contaim nan's and have zero variance
        self._mask = np.invert(np.isnan(data.sum(axis=0)))* \
            (data.std(axis=0) > 0.0)

        data = self.filter(data)
        self._zs = ZScore(data)
        self.traindata = self.normalize(data)

    def normalize(self, data):
        return self._zs.normalize(data)

    def filter(self, data):
        return data[:, self._mask]

    def __call__(self, data):
        return self.normalize(self.filter(data))
