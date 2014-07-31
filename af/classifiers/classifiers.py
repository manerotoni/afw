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
from af.classifiers.itemclass import ItemClass, UnClassified

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



class OneClassSvm(Classifier):
    """Class for training and parameter tuning of a one class svm."""

    # TODO method to set the item classes
    INLIER = ItemClass("inlier", QtGui.QColor("green"), 1)
    OUTLIER = ItemClass("outlier", QtGui.QColor("red"), -1)
    classes = {INLIER.label: INLIER,
               OUTLIER.label: OUTLIER}

    def __init__(self, *args, **kw):
        super(OneClassSvm, self).__init__(*args, **kw)
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
        self._gamma.setSingleStep(0.01)
        self._gamma.setValue(0.5)

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
        self._clf = svm.OneClassSVM(C=0.66, nu=self.nu, kernel="rbf", gamma=self.gamma)
        self._clf.fit(self._pp.traindata)
        print("classifier trained")

    def predict(self, features):
        if self._clf is None:
            return super(OneClassSvm, self).predict(features)
        else:
            predictions = self._clf.predict(self._pp(features))
            return [self.classes[pred] for pred in predictions]
