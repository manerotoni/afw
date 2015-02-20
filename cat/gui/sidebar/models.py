"""
models.py

Implementation of ItemModels for the sidebar

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ =("AtOneClassSvmItemModel", "AtSorterItemModel" )


from collections import OrderedDict
import numpy as np
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from .sidebar import NoSampleError

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

    def hashkey(self):
        raise NotImplementedError

    def clear(self):
        for i in range(self.rowCount()):
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
            raise NoSampleError

        nfeatures = self.items[0].features.size
        features = np.empty((nitems, nfeatures))

        for i, item in enumerate(self.iterItems()):
            features[i, :] = item.features
        return features

    @property
    def sample_info(self):
        """Return a ndarray of hdf group names ind indices to trace back
        single samples to the feature table in the original data set (hdf file).
        """
        nitems = self.rowCount()
        dt = [("index", np.uint32), ("name", "S256")]

        sample_info = np.empty((nitems, ), dtype=dt)

        for i, item in enumerate(self.iterItems()):
            sample_info[i] = np.array((item.index, item.path), dtype=dt)

        return sample_info


    def prepareRowItems(self, item):
        items = [QtGui.QStandardItem(QtGui.QIcon(item.pixmap), str(item.index)),
                 QtGui.QStandardItem(str(item.frame)),
                 QtGui.QStandardItem(str(item.objid))]

        items[0].setData(QtCore.QVariant(item.hash))

        for item in items:
            item.setEditable(False)
            item.setDragEnabled(False)
            item.setDropEnabled(False)
        return items

    def removeItems(self, indices):
        for index in indices:
            self.removeRow(index.row())


class AtSorterItemModel(AtStandardItemModel):

    def __init__(self, *args, **kw):
        super(AtSorterItemModel, self).__init__(*args, **kw)

    def removeRow(self, row):
        key = self.item(row, 0).data()
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
        key = self.item(row, 0).data()
        self._items[key].clear()
        del self._items[key]
        super(AtOneClassSvmItemModel, self).removeRow(row)

    def hashkey(self, index):
        item = self.item(index.row(), 0)
        return item.data()
