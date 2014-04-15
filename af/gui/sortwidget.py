"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AfSortWidget', )


from os.path import splitext
import numpy as np

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore


class AfTreeWidgetItem(QtGui.QTreeWidgetItem):

    def __init__(self, item, *args, **kw):
        super(AfTreeWidgetItem, self).__init__(*args, **kw)
        self.cellitem = item
        self.setIcon(0, QtGui.QIcon(item.pixmap))
        self.setData(1, QtCore.Qt.DisplayRole, str(item.frame))
        self.setData(2, QtCore.Qt.DisplayRole, str(item.objid))


class AfSideBarWidget(QtGui.QWidget):

    def __init__(self, *args, **kw):
        super(AfSideBarWidget, self).__init__(*args, **kw)

    def addItems(self, items):
        for item in items:
            self.items.addTopLevelItem(AfTreeWidgetItem(item))

    def onRemoveAll(self):
        self.items.clear()

    def onRemove(self):
        for item in self.items.selectedItems():
            index = self.items.indexOfTopLevelItem(item)
            self.items.takeTopLevelItem(index)


class AfSortWidget(AfSideBarWidget):

    def __init__(self, parent=None, *args, **kw):
        super(AfSortWidget, self).__init__(parent, *args, **kw)
        # qtmethod does not return the real parent!
        self.parent = parent
        uic.loadUi(splitext(__file__)[0]+'.ui', self)

        self.removeBtn.clicked.connect(self.onRemove)
        self.removeAllBtn.clicked.connect(self.onRemoveAll)
        self.addBtn.clicked.connect(self.onAdd)
        self.sortBtn.clicked.connect(self.onSort)

        for i in xrange(self.items.columnCount()):
            self.items.setColumnWidth(i, 50)

    def onAdd(self):
        items = self.parent.selectedItems()
        self.addItems(items)

    def onSort(self):
        center = self._meanFromItems()

        all_items = sorted(self.parent().items(), lambda p: p.sortkey)

        from PyQt4.QtCore import pyqtRemoveInputHook; pyqtRemoveInputHook()
        import pdb; pdb.set_trace()

        print center

    def _meanFromItems(self):
        """Mean feature vector of the items in the list."""
        nitems = self.items.topLevelItemCount()
        nfeatures = self.items.topLevelItem(0).cellitem.features.size

        ftrs = np.empty((nitems, nfeatures))
        for i in xrange(nitems):
            ftrs[i, :] = self.items.topLevelItem(i).cellitem.features

        return ftrs.mean(axis=0)
