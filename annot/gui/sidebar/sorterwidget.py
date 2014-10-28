"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtSortWidget', )


from os.path import dirname, join

from PyQt4 import uic
from PyQt4 import QtCore
from PyQt4.QtGui import QMessageBox

from annot.sorters import Sorter
from annot.config import AtConfig
from .sidebar import AtSideBarWidget
from .models import  AtSorterItemModel


class AtSortWidget(AtSideBarWidget):

    startSorting = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(AtSortWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)

        self.treeview.activated.connect(self.onActivated)

        self.sortAlgorithm.addItems(Sorter.sorters())

        self.model = AtSorterItemModel(self)
        self.treeview.setModel(self.model)

        self.removeBtn.clicked.connect(self.removeSelected)
        self.removeAllBtn.clicked.connect(self.removeAll)
        self.addBtn.clicked.connect(self.onAdd)
        self.sortBtn.clicked.connect(self.sort)
        self.startSorting.connect(
            lambda: self.tileview.reorder(force_update=True))

    def itemView(self):
        return self.treeview

    def defaultSortAlgorithm(self):
        return AtConfig().default_sorter

    def applyDefaultSortAlgorithm(self):
        index = self.sortAlgorithm.findText(self.defaultSortAlgorithm())
        self.sortAlgorithm.setCurrentIndex(index)

    def sort(self):

        all_items = self.tileview.items

        # nothing to sort
        if not all_items:
            return

        sorter = Sorter(self.sortAlgorithm.currentText(), all_items)
        sorter.treedata = self.model.features

        try:
            dist = sorter()
        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e))
            return

        if dist is not None:
            for d, item in zip(dist, all_items):
                item.sortkey = d
            self.startSorting.emit()
