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
from af.classifiers import Classifier

from af.gui.sidebar.models import AfOneClassSvmItemModel, AfSorterItemModel


class AfSideBarWidget(QtGui.QWidget):

    def __init__(self, parent, tileview, *args, **kw):
        super(AfSideBarWidget, self).__init__(parent, *args, **kw)
        self.tileview = tileview
        self.parent = parent
        self._items = list()

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

    def _featureTable(self):
        """Yields a feature matrix from the items in the Sidebar. One feature
        vector per row."""
        nitems = self.model.rowCount()
        nfeatures = self.model.items[0].features.size
        ftrs = np.empty((nitems, nfeatures))

        for i, item in enumerate(self.model.iterItems()):
            ftrs[i, :] = item.features
        return ftrs


class AfSortWidget(AfSideBarWidget):

    startSorting = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(AfSortWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)

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
        nitems = len(all_items)
        nfeatures = all_items[0].features.size
        data = np.empty((nitems, nfeatures))

        # all featurs of all items
        for i, item in enumerate(all_items):
            data[i, :] = item.features

        sorter = Sorter(self.sortAlgorithm.currentText(), data)

        if self.model.rowCount() == 0 and sorter.needs_treedata:
            QMessageBox.warning(self, 'no items added',
                                'You need to add items to the sidebar')
            return

        elif sorter.needs_treedata:
            sorter.treedata = self._featureTable()

        dist = sorter()

        for d, item in zip(dist, all_items):
            item.sortkey = d

        self.startSorting.emit()


class AfAnnotationWidget(AfSideBarWidget):

    def __init__(self, *args, **kw):
        super(AfAnnotationWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)

        self.saveBtn.clicked.connect(self.onSave)
        self.classifiers.addItems(Classifier.classifiers())

        self.model = AfOneClassSvmItemModel(self)
        self.treeview.setModel(self.model)

        self.removeBtn.clicked.connect(self.onRemove)
        self.removeAllBtn.clicked.connect(self.onRemoveAll)
        self.addBtn.clicked.connect(self.onAdd)

    def onSave(self):

        fname = QFileDialog.getSaveFileName(self, "save Feature Table",
                                            expanduser("~"))
        if not fname:
            return

        ftrnames = self.parent.loader.featureNames
        ftrs = self._featureTable()
        np.savetxt(fname, ftrs, delimiter=",", header=",".join(ftrnames))
        QMessageBox.information(self, "information", "data successfully saved")
