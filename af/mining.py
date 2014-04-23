"""
mining.py

Collection of various helper functions
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

from matplotlib import mlab
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

    def __init__(self, data):
        self.mean = data.mean(axis=0)
        self.std = data.std(axis=0)

    def normalize(self, data):
        return (data - self.mean)/self.std


class PCA(mlab.PCA):

    def __init__(self, data, minfrac=0.0):
        self.minfrac = minfrac
        mlab.PCA.__init__(self, data)

    def center(self, data):
        """Overwrite this method to not perform a zscoring."""
        return data

    def iproject(self, data, minfrac=0.0):

        mask = self.fracs >= minfrac
        wt_inv = np.linalg.inv(self.Wt)
        wt_inv = wt_inv[:, mask]

        from PyQt4.QtCore import pyqtRemoveInputHook; pyqtRemoveInputHook()
        import pdb; pdb.set_trace()

        return np.dot(wt_inv, data.T).T

    def project(self, x, minfrac=0.):
        """Project x onto the principle axes, dropping any axes where
        fraction of variance<minfrac
        """
        x = np.asarray(x)

        ndims = len(x.shape)

        if (x.shape[-1]!=self.numcols):
            raise ValueError('Expected an array with dims[-1]==%d'%self.numcols)

        Y = np.dot(self.Wt, x.T).T
        mask = self.fracs>=minfrac

        if ndims==2:
            Yreduced = Y[:,mask]
        else:
            Yreduced = Y[mask]
        return Yreduced
