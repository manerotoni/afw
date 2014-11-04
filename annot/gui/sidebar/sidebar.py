"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtSideBarWidget', )


from PyQt4 import QtGui


class NoSampleError(Exception):
    pass


class AtSideBarWidget(QtGui.QWidget):

    def __init__(self, parent, tileview, *args, **kw):
        super(AtSideBarWidget, self).__init__(parent, *args, **kw)
        self.tileview = tileview
        self.parent = parent

    def removeSelected(self):
        model_indices =  self.itemView().selectionModel().selectedRows()
        model_indices.reverse()
        self.model.removeItems(model_indices)

    def removeAll(self):
        self.model.clear()

    def addItems(self, items):
        for item in items:
            self.model.addItem(item)

    def onAdd(self):
        items = self.tileview.selectedItems()
        self.addItems(items)

    def onActivated(self, index):
        item = self.model.item(index.row())
        hashkey = item.data().toPyObject()
        self.tileview.selectByKey(hashkey)

    def itemView(self):
        raise NotImplementedError