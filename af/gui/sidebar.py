"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AfSortWidget', )


from os.path import dirname, join
import numpy as np


from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QMessageBox

from af.sorters import Sorter

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
        self._items = list()

    def addItems(self, items):
        for item in items:
            if item not in self._items:
                self.items.addTopLevelItem(AfTreeWidgetItem(item))
                self._items.append(item)

    def onRemoveAll(self):
        self.items.clear()
        self._items = list()

    def onRemove(self):
        for item in self.items.selectedItems():
            index = self.items.indexOfTopLevelItem(item)
            topitem = self.items.takeTopLevelItem(index)
            self._items.remove(topitem.cellitem)

class AfAnnotationWidget(AfSideBarWidget):

    def __init__(self, parent, *args, **kw):
        super(AfAnnotationWidget, self).__init__(parent, *args, **kw)
        # qtmethod does not return the real parent!
        self.parent = parent
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)


class AfSortWidget(AfSideBarWidget):

    startSorting = QtCore.pyqtSignal()

    def __init__(self, parent=None, *args, **kw):
        super(AfSortWidget, self).__init__(parent, *args, **kw)
        # qtmethod does not return the real parent!
        self.parent = parent
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)

        self.sortAlgorithm.addItems(Sorter.sorters())

        self.removeBtn.clicked.connect(self.onRemove)
        self.removeAllBtn.clicked.connect(self.onRemoveAll)
        self.addBtn.clicked.connect(self.onAdd)
        self.sortBtn.clicked.connect(self.onSort)

        self.startSorting.connect(lambda: parent.reorder(force_update=True))

        for i in xrange(self.items.columnCount()):
            self.items.setColumnWidth(i, 50)

    def onAdd(self):
        items = self.parent.selectedItems()
        self.addItems(items)

    def _featuresFromSidebar(self):
        """Yields a feature matrix from the items in the Sidebar. One feature
        vector per row."""
        nitems = self.items.topLevelItemCount()
        nfeatures = self.items.topLevelItem(0).cellitem.features.size
        ftrs = np.empty((nitems, nfeatures))

        for i in xrange(nitems):
            ftrs[i, :] = \
                self.items.topLevelItem(i).cellitem.features
        return ftrs

    def onSort(self):

        all_items = self.parent.items
        nitems = len(all_items)
        nfeatures = all_items[0].features.size
        data = np.empty((nitems, nfeatures))

        # all featurs of all items
        for i, item in enumerate(all_items):
            data[i, :] = item.features

        sorter = Sorter(self.sortAlgorithm.currentText(), data)

        if self.items.topLevelItemCount() == 0 and sorter.needs_treedata:
            QMessageBox.warning(self, 'no items added',
                                'You need to add items to the sidebar')
            return

        elif sorter.needs_treedata:
            sorter.treedata = self._featuresFromSidebar()

        dist = sorter()

        for d, item in zip(dist, all_items):
            item.sortkey = d

        self.startSorting.emit()
