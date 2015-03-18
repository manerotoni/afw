"""
mining.py

Collection of various helper functions
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import numpy as np


def filter_nans(data, data2=None):
    """Delete columns from that contain NAN's"""

    nans = np.isnan(data)
    col_nans = np.unique(np.where(nans)[1])
    if data2 is None:
        return np.delete(data, col_nans, axis=1)
    else:
        return (np.delete(data, col_nans, axis=1),
                np.delete(data2, col_nans, axis=1))


class ZScore(object):

    def __init__(self, data, min_variance=10e-9, replace_inf=True):
        self.mean = data.mean(axis=0)
        self.std = data.std(axis=0)
        if replace_inf:
            # features with no variance should be filtered out later
            self.std[self.std <= min_variance] = np.nan

    def normalize(self, data):
        return (data - self.mean)/self.std


class PCA(object):

    def __init__(self, data, minfrac=0.0):
        self.minfrac = minfrac

        self.numrows, self.numcols = data.shape
        if not self.numrows > self.numcols:
            raise RuntimeError(('PCA requires numrows > numcols'))

        U, s, Vh = np.linalg.svd(data, full_matrices=False)

        vars = s**2/float(len(s))
        self.fracs = vars/vars.sum()
        self._mask = self.fracs > self.minfrac
        self.wt = Vh

    def iproject(self, data, minfrac=0.0):
        wt_inv = np.linalg.inv(self.wt)
        wt_inv = wt_inv[:, self._mask]

        if data.shape[1] != wt_inv.shape[1]:
            raise RuntimeError("Shapes of inversion matrices do not match")

        return np.dot(wt_inv, data.T).T

    def project(self, x, minfrac=0.):
        """Project x onto the principle axes, dropping any axes where
        fraction of variance<minfrac
        """
        x = np.asarray(x)

        ndims = len(x.shape)

        if (x.shape[-1]!=self.numcols):
            raise ValueError('Expected an array with dims[-1]==%d'%self.numcols)

        Y = np.dot(self.wt, x.T).T

        if ndims == 2:
            return Y[:, self._mask]
        else:
            return Y[self._mask]
