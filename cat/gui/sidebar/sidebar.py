"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtSideBarWidget', 'NoSampleError')


from PyQt5 import QtWidgets
from PyQt5 import QtCore

class NoSampleError(Exception):
    pass


class AtSideBarWidget(QtWidgets.QWidget):

    itemCountChanged = QtCore.pyqtSignal()

    def __init__(self, parent, tileview, featuredlg=None, *args, **kw):
        super(AtSideBarWidget, self).__init__(parent, *args, **kw)
        self.tileview = tileview
        self.featuredlg = featuredlg
        self.parent = parent

    def removeSelected(self):
        model_indices =  self.itemView().selectionModel().selectedRows()
        model_indices.reverse()
        self.model.removeItems(model_indices)
        self.itemCountChanged.emit()

    def removeAll(self):
        self.model.clear()
        self.itemCountChanged.emit()

    def addItems(self, items):
        for item in items:
            self.model.addItem(item)
        self.itemCountChanged.emit()

    def onAdd(self):
        items = self.tileview.selectedItems()
        self.addItems(items)

    def onActivated(self, index):
        item = self.model.item(index.row())
        hashkey = item.data()
        self.tileview.selectByKey(hashkey)

    def itemView(self):
        raise NotImplementedError

    def filterFeatures(self, features, no_empty_table=True):
        """Filter the feature matrix by column wise. Indices of the cols are
        determined by the FeatureSelection Dialog.

        If no_empty_table is True the methode return the full feature table if
        the number of selected features is zero.
        """

        ftrs_indices = self.filter_indices

        # returns the full feature table if not features are selected
        if no_empty_table and not ftrs_indices:
            ftrs_indices = range(features.shape[1])

        if not ftrs_indices or features is None:
            raise NoSampleError("no features selected for classifier training")

        return features[:, ftrs_indices]

    @property
    def filter_indices(self):
        return self.featuredlg.indicesOfCheckedItems()
