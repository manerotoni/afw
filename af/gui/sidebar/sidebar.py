"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AfSortWidget', 'AfAnnotationWidget')


from os.path import dirname, join, expanduser
import numpy as np


from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QFileDialog

from af.sorters import Sorter
from af.classifiers.classifiers import Classifier
from .models import  AfSorterItemModel


class AfSideBarWidget(QtGui.QWidget):

    def __init__(self, parent, tileview, *args, **kw):
        super(AfSideBarWidget, self).__init__(parent, *args, **kw)
        self.tileview = tileview
        self.parent = parent

    def onRemove(self):
        model_indices =  self.treeview.selectionModel().selectedRows()
        model_indices.reverse()

        for mi in model_indices:
            self.model.removeRow(mi.row())

    def onRemoveAll(self):
        self.model.clear()

    def addItems(self, items):
        for item in items:
            self.model.addItem(item)

    def onAdd(self):
        items = self.tileview.selectedItems()
        self.addItems(items)

    def onActivated(self, index):
        item = self.model.item(index.row())
        self.tileview.selectByIndex(int(item.text()))


class AfSortWidget(AfSideBarWidget):

    startSorting = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(AfSortWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)
        self.treeview.activated.connect(self.onActivated)

        self.sortAlgorithm.addItems(Sorter.sorters())

        self.model = AfSorterItemModel(self)
        self.treeview.setModel(self.model)

        self.removeBtn.clicked.connect(self.onRemove)
        self.removeAllBtn.clicked.connect(self.onRemoveAll)
        self.addBtn.clicked.connect(self.onAdd)
        self.sortBtn.clicked.connect(self.onSort)
        self.startSorting.connect(
            lambda: self.tileview.reorder(force_update=True))

    def onSort(self):

        all_items = self.tileview.items
        sorter = Sorter(self.sortAlgorithm.currentText(), all_items)


        sorter.treedata = self.model.features

        try:
            dist = sorter()
        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e))
            return

        if dist is not None:
            for d, item in zip(dist, all_items):
                item.sortkey = d
            self.startSorting.emit()



class AfAnnotationWidget(AfSideBarWidget):


    def __init__(self, *args, **kw):
        super(AfAnnotationWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)
        self.treeview.activated.connect(self.onActivated)

        self.stack = QtGui.QStackedWidget(self)
        self.stack.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Maximum)
            )

        self.sbox.addWidget(self.stack)
        self.saveBtn.clicked.connect(self.onSave)

        self._setupClassifiers()
        self.classifiers.currentIndexChanged.connect(
            self.stack.setCurrentIndex)

        self.treeview.setModel(self.model)

        self.removeBtn.clicked.connect(self.onRemove)
        self.removeAllBtn.clicked.connect(self.onRemoveAll)
        self.predictBtn.clicked.connect(self.onPredict)
        self.addBtn.clicked.connect(self.onAdd)

    def _setupClassifiers(self):
        for name in Classifier.classifiers():
            clf = Classifier(name)
            self.classifiers.addItem(name)
            self.stack.addWidget(clf.parameterWidget(self))
            setattr(self, name, clf)

    def currentClassifier(self):
        return getattr(self, self.classifiers.currentText())

    @property
    def model(self):
        return self.currentClassifier().model

    def onSave(self):

        fname = QFileDialog.getSaveFileName(self, "save Feature Table",
                                            expanduser("~"))
        if not fname:
            return

        ftrnames = self.parent.loader.featureNames
        np.savetxt(fname, self.model.features,
                   delimiter=",", header=",".join(ftrnames))
        QMessageBox.information(self, "information", "data successfully saved")

    def onRemoveAll(self):
        super(AfAnnotationWidget, self).onRemoveAll()
        for item in self.tileview.items:
            item.clearClass()

    def onRemove(self):
        super(AfAnnotationWidget, self).onRemove()
        self.classify(self.tileview.items)

    def addItems(self, items):
        super(AfAnnotationWidget, self).addItems(items)
        self.train()
        self.classify(self.tileview.items)

    def onPredict(self):
        self.classify(self.tileview.items)

    def train(self):
        clf = self.currentClassifier()
        clf.train(self.model.features)

    def classify(self, items):
        clf = self.currentClassifier()
        for item in items:
            prediction = clf.predict(item.features.reshape((1, -1)))
            item.setClass(prediction[0])
