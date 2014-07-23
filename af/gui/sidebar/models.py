"""
models.py

Implementation of ItemModels for the sidebar

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ =("AfOneClassSvmItemModel", )


from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt


class AfStandardItemModel(QtGui.QStandardItemModel):

    def __init__(self, *args, **kw):
        super(AfStandardItemModel, self).__init__(*args, **kw)
        self._items = dict()
        self.insertColumns(0, 3)
        # default columns
        self.setHeaderData(0, Qt.Horizontal, QtCore.QVariant("item"))
        self.setHeaderData(1, Qt.Horizontal, QtCore.QVariant("frame"))
        self.setHeaderData(2, Qt.Horizontal, QtCore.QVariant("objed-id"))

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


class AfSorterItemModel(AfStandardItemModel):

    def __init__(self, *args, **kw):
        super(AfSorterItemModel, self).__init__(*args, **kw)

    def prepareRowItems(self, item):
        return [QtGui.QStandardItem(QtGui.QIcon(item.pixmap), str(item.index)),
                QtGui.QStandardItem(str(item.frame)),
                QtGui.QStandardItem(str(item.objid))]


class AfOneClassSvmItemModel(AfStandardItemModel):

    def __init__(self, *args, **kw):
        super(AfOneClassSvmItemModel, self).__init__(*args, **kw)

    def prepareRowItems(self, item):
        return [QtGui.QStandardItem(QtGui.QIcon(item.pixmap), str(item.index)),
                QtGui.QStandardItem(str(item.frame)),
                QtGui.QStandardItem(str(item.objid))]
