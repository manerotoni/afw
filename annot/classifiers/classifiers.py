"""
classifier.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("Classifier", )


from PyQt4 import QtGui

from annot.pattern import Factory
from annot.classifiers.itemclass import UnClassified

# TODO need design pattern QFactory
class Classifier(object):
    """Parent factory for all classifier classes."""

    __metaclass__ = Factory

    def __init__(self):
        super(Classifier, self).__init__()
        self._pp = None # setup preprocessor in the train method
        self.model = None
        self._clf = None
        self._actions = list()

    @property
    def actions(self):
        return self._actions

    def createActions(self, parent, panel):
        pass

    def addToClassActions(self):
        raise NotImplementedError

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
