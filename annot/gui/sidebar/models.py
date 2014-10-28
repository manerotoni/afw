"""
models.py

Implementation of ItemModels for the sidebar

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ =("AtOneClassSvmItemModel", )


from collections import OrderedDict
import numpy as np
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt


class AtStandardItemModel(QtGui.QStandardItemModel):

    def __init__(self, *args, **kw):
        super(AtStandardItemModel, self).__init__(*args, **kw)
        self._items = OrderedDict()
        self.insertColumns(0, 3)
        self._setHeader()

    def _setHeader(self):
        # default columns
        self.setHeaderData(0, Qt.Horizontal, QtCore.QVariant("item"))
        self.setHeaderData(1, Qt.Horizontal, QtCore.QVariant("frame"))
        self.setHeaderData(2, Qt.Horizontal, QtCore.QVariant("label"))

    def prepareRowItems(self, *args, **kw):
        raise NotImplementedError

    def clear(self):
        for i in range(len(self._items)):
            self.removeRow(0)
        self._items.clear()

    @property
    def items(self):
        return self._items.values()

    def iterItems(self):
        """Iterator over all items ordered from top to bottom."""
        for key, value in self._items.iteritems():
            yield value

    @property
    def labels(self):
        return None

    @property
    def features(self):
        """Yields a feature matrix from the items in the Sidebar. One feature
        vector per row."""
        nitems = self.rowCount()
        if not nitems:
            return
        nfeatures = self.items[0].features.size
        features = np.empty((nitems, nfeatures))

        for i, item in enumerate(self.iterItems()):
            features[i, :] = item.features
        return features

    def prepareRowItems(self, item):
        items = [QtGui.QStandardItem(QtGui.QIcon(item.pixmap), str(item.index)),
                 QtGui.QStandardItem(str(item.frame)),
                 QtGui.QStandardItem(str(item.objid))]

        items[0].setData(QtCore.QVariant(item.hash))

        for item in items:
            item.setEditable(False)
        return items

    def removeItems(self, indices):
        for index in indices:
            self.removeRow(index.row())


class AtSorterItemModel(AtStandardItemModel):

    def __init__(self, *args, **kw):
        super(AtSorterItemModel, self).__init__(*args, **kw)

    def removeRow(self, row):
        key = self.item(row, 0).data().toPyObject()
        self._items[key].clear()
        del self._items[key]
        super(AtSorterItemModel, self).removeRow(row)

    def addItem(self, item):
        if not self._items.has_key(item.hash):
            self._items[item.hash] = item
            root = self.invisibleRootItem()
            root.appendRow(self.prepareRowItems(item))


class AtOneClassSvmItemModel(AtStandardItemModel):

    def __init__(self, *args, **kw):
        super(AtOneClassSvmItemModel, self).__init__(*args, **kw)

    def addAnnotation(self, item, class_name=None):
        # No class_names in the one class support vector machine..

        if not self._items.has_key(item.hash):
            self._items[item.hash] = item
            root = self.invisibleRootItem()
            root.appendRow(self.prepareRowItems(item))

    def removeRow(self, row):
        key = self.item(row, 0).data().toPyObject()
        self._items[key].clear()
        del self._items[key]
        super(AtOneClassSvmItemModel, self).removeRow(row)
