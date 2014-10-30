"""
classifier.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("Classifier", )

from collections import OrderedDict

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
        self._classes = OrderedDict()

    @property
    def actions(self):
        return self._actions

    @property
    def classes(self):
        return self._classes

    def setClasses(self, classes, parent, panel):
        """Update the dictionary of the class definition and the list of
        the context menu actions."""

        self._classes.clear()
        self._classes.update(classes)
        self.createActions(parent, panel)

    def createActions(self, parent, panel):
        """Create context menu actions according to the class definition."""

        self._actions = list()
        for name in self._classes.keys():
            self.actions.append(
                QtGui.QAction( "add to %s" %name, parent,
                    triggered=lambda: panel.addAnnotation(name)))

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

    def normalize(self, features):
        return self._pp(features)
