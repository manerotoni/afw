"""
classifier.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("Classifier", )


from PyQt4 import QtGui

from af.pattern import Factory
from af.classifiers.itemclass import  UnClassified

# TODO need design pattern QFactory
class Classifier(object):
    """Parent factory for all classifier classes."""

    __metaclass__ = Factory

    def __init__(self, *args, **kw):
        super(Classifier, self).__init__(*args, **kw)
        self._pp = None # setup preprocessor in the train method
        self.model = None
        self._clf = None

    @classmethod
    def classifiers(cls):
        return cls._classes.keys()

    def parameterWidget(self, parent):
        return QtGui.QWidget(self)

    def train(self, features):
        raise NotImplementedError

    def predict(self, features):
        return [UnClassified]*features.shape[0]

    def saveToHdf(self, file_, feature_names):
        raise NotImplementedError
