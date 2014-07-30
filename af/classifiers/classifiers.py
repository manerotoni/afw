"""
classifier.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("Classifier", "OneClassSvm")

from sklearn import svm
from PyQt4 import QtGui

from af.pattern import Factory
from af.preprocessor import PreProcessor
from af.gui.sidebar.models import AfOneClassSvmItemModel

class Classifier(object):
    """Parent factory for all classifier classes"""

    __metaclass__ = Factory

    def __init__(self):
        super(Classifier, self).__init__()
        self._pp = None # setup preprocessor in the train method
        self.model = None

    @classmethod
    def classifiers(cls):
        return cls._classes.keys()

    def parameterWidget(self, parent):
        return QtGui.QWidget(self)

    def train(self, features):
        raise NotImplementedError



class OneClassSvm(Classifier):
    """Class for training and parameter tuning of a one class svm."""

    def __init__(self):
        self.model = AfOneClassSvmItemModel()

    def parameterWidget(self, parent):

        self._frame = QtGui.QFrame(parent)

        vbox = QtGui.QHBoxLayout(self._frame)

        self._nu = QtGui.QDoubleSpinBox(self._frame)
        self._nu.setRange(0.0, 1.0)
        self._nu.setSingleStep(0.05)
        self._nu.setValue(0.01)

        self._gamma = QtGui.QDoubleSpinBox(self._frame)
        self._gamma.setRange(0.0, 100.0)
        self._gamma.setSingleStep(0.5)
        self._gamma.setValue(0.1)

        vbox.addWidget(QtGui.QLabel("nu", self._nu))
        vbox.addWidget(self._nu)
        vbox.addWidget(QtGui.QLabel("gamma", self._gamma))
        vbox.addWidget(self._gamma)

        return self._frame

    @property
    def nu(self):
        return self._nu.value()

    @property
    def gamma(self):
        return self._gamma.value()

    def train(self, features):
        self._pp = PreProcessor(features)
        self._clf = svm.OneClassSVM(nu=self.nu, kernel="rbf", gamma=self.gamma)
        self._clf.fit(self._pp.traindata)
        print("classifier trained")
