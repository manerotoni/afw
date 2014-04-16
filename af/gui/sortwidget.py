"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AfSortWidget', )


from os.path import splitext
import numpy as np

from scipy import stats
from matplotlib import mlab

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

    startSorting = QtCore.pyqtSignal()

    reduced_idx = [222, 223, 236]

    def __init__(self, parent=None, *args, **kw):
        super(AfSortWidget, self).__init__(parent, *args, **kw)
        # qtmethod does not return the real parent!
        self.parent = parent
        uic.loadUi(splitext(__file__)[0]+'.ui', self)

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

    def onSort(self):

        all_items = self.parent.items
        nitems = len(all_items)
        nfeatures = all_items[0].features.size
        data = np.empty((nitems, nfeatures))

        # all featurs of all items
        for i, item in enumerate(all_items):
            data[i, :] = item.features

        zs_mean = data.mean(axis=0)
        zs_std = data.std(axis=0)
        data_zs = (data - zs_mean)/zs_std

        pca = mlab.PCA(data_zs)
        data_pca = pca.project(data_zs)

        mu = self._meanFromItems(pca, zs_mean, zs_std)
        distsq = [np.power((x - mu), 2).sum() for x in data_pca]

        dist = np.sqrt(distsq)

        for d, item in zip(dist, all_items):
            item.sortkey = d

        self.startSorting.emit()

    def _meanFromItems(self, pca, zs_mean, zs_std):
        """Mean feature vector of the items in the list."""
        nitems = self.items.topLevelItemCount()
        nfeatures = self.items.topLevelItem(0).cellitem.features.size

        ftrs = np.empty((nitems, nfeatures))
        for i in xrange(nitems):
            ftrs[i, :] = \
                self.items.topLevelItem(i).cellitem.features

        ftrs = pca.project((ftrs-zs_mean)/zs_std)

        return ftrs.mean(axis=0)
