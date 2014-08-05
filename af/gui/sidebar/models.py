"""
models.py

Implementation of ItemModels for the sidebar

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ =("AfOneClassSvmItemModel", )


import numpy as np
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt


class AfStandardItemModel(QtGui.QStandardItemModel):

    def __init__(self, *args, **kw):
        super(AfStandardItemModel, self).__init__(*args, **kw)
        self._items = dict()
        self.insertColumns(0, 3)
        self._setHeader()

    def _setHeader(self):
        # default columns
        self.setHeaderData(0, Qt.Horizontal, QtCore.QVariant("item"))
        self.setHeaderData(1, Qt.Horizontal, QtCore.QVariant("frame"))
        self.setHeaderData(2, Qt.Horizontal, QtCore.QVariant("label"))

    def prepareRowItems(self, *args, **kw):
        raise NotImplementedError

    def addItem(self, item):

        if not self._items.has_key(item.index):
            self._items[item.index] = item
            root = self.invisibleRootItem()
            root.appendRow(self.prepareRowItems(item))

    def removeRow(self, row):
        del self._items[int(self.item(row).text())]
        super(AfStandardItemModel, self).removeRow(row)

    def clear(self):
        for i in range(len(self._items)):
            self.removeRow(0)
        self._items.clear()

    @property
    def items(self):
        return self._items.values()

    def iterItems(self):
        """Iterator over all items ordered from top to bottom."""
        for i in xrange(self.rowCount()):
            yield self._items[int(self.item(i).text())]

    @property
    def features(self):
        """Yields a feature matrix from the items in the Sidebar. One feature
        vector per row."""
        nitems = self.rowCount()
        nfeatures = self.items[0].features.size
        features = np.empty((nitems, nfeatures))

        for i, item in enumerate(self.iterItems()):
            features[i, :] = item.features
        return features


class AfSorterItemModel(AfStandardItemModel):

    def __init__(self, *args, **kw):
        super(AfSorterItemModel, self).__init__(*args, **kw)

    def prepareRowItems(self, item):
        items = [QtGui.QStandardItem(QtGui.QIcon(item.pixmap), str(item.index)),
                 QtGui.QStandardItem(str(item.frame)),
                 QtGui.QStandardItem(str(item.objid))]
        for item in items:
            item.setEditable(False)
        return items

class AfOneClassSvmItemModel(AfStandardItemModel):

    def __init__(self, *args, **kw):
        super(AfOneClassSvmItemModel, self).__init__(*args, **kw)

    def prepareRowItems(self, item):
        items = [QtGui.QStandardItem(QtGui.QIcon(item.pixmap), str(item.index)),
                 QtGui.QStandardItem(str(item.frame)),
                 QtGui.QStandardItem(str(item.objid))]
        for item in items:
            item.setEditable(False)
        return items
