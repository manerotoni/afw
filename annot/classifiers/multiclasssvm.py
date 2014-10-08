"""
multiclasssvm.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from PyQt4 import QtGui

from annot.gui.sidebar.models import AtMultiClassSvmItemModel

from .itemclass import ItemClass
from .classifiers import Classifier


class MultiClassSvm(Classifier):

    def __init__(self, *args, **kw):
        super(MultiClassSvm, self).__init__(*args, **kw)
        self.model = AtMultiClassSvmItemModel()
        self._pp = None

    def parameterWidget(self, parent):
        self._frame = QtGui.QFrame(parent)
        return self._frame

    def saveToHdf(self, *args, **kw):
        pass

    def train(self, *args, **kw):
        pass

    def predict(self, *args, **kw):
        pass
