"""
preprocessor.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import sys
sys.path.append("../")

import numpy as np
from af.mining import ZScore


class PreProcessor(object):

    def __init__(self, traindata, testdata):

        # traindata = np.loadtxt(training_data, delimiter=",")
        # testdata = np.loadtxt(test_data, delimiter=",")

        traindata = np.recfromcsv(traindata)
        testdata = np.recfromcsv(testdata)

        self.feature_names = [n[2:] for n in traindata.dtype.names]
        nftrs = len(self.feature_names)
        traindata = traindata.view(float).reshape((-1, nftrs))
        testdata = testdata.view(float).reshape((-1, nftrs))

        # to remove columns that contaim nan's and have zero variance
        self._mask = np.invert(np.isnan(traindata.sum(axis=0)))* \
            (traindata.std(axis=0) > 0.0)

        traindata = traindata[:, self._mask]
        mask = np.invert(np.isnan(testdata.sum(axis=1)))
        testdata = testdata[:, self._mask][mask, :]

        self._zs = ZScore(traindata)
        self.traindata = self.normalize(traindata)
        self.testdata = self.normalize(testdata)

    def index(self, items):
        if not isinstance(items, (list, tuple)):
            items = (items, )
        return [self.feature_names.index(item) for item in items]

    def normalize(self, data):
        return self._zs.normalize(data)

    def filter(self, data):
        return data[:, self._mask]

    @property
    def ranges(self):
        return np.array([(self.testdata[:, 0].min(), self.testdata[:, 0].max()),
                         (self.testdata[:, 1].min(), self.testdata[:, 1].max())])

    def __call__(self, data):
        return self.normalize(self.filter(data))
