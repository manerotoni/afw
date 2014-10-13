"""
multiclasssvm.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from PyQt4 import QtGui

from annot.gui.sidebar.models import AtMultiClassSvmItemModel


from .classifiers import Classifier

class McSvmParameterWidget(QtGui.QFrame):

    def __init__(self, parent, *args, **kw):
        super(McSvmParameterWidget, self).__init__(parent, *args, **kw)

        gbox = QtGui.QGridLayout(self)
        gbox.setContentsMargins(2, 2, 2, 2)

        self.treeview = QtGui.QTreeView(self)
        self.treeview.activated.connect(parent.onActivated)
        self.treeview.setModel(AtMultiClassSvmItemModel())
        self.treeview.setSelectionMode(self.treeview.MultiSelection)

        gbox.addWidget(self.treeview, 1, 0, 1, 0)


class MultiClassSvm(Classifier):

    def __init__(self, *args, **kw):
        super(MultiClassSvm, self).__init__(*args, **kw)
        self._pp = None

    def parameterWidget(self, parent):
        self._params = McSvmParameterWidget(parent)
        return self._params

    def saveToHdf(self, *args, **kw):
        pass

    def train(self, *args, **kw):
        pass

    def predict(self, *args, **kw):
        pass
