"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtSortWidget', )


from os.path import dirname, join
import numpy as np

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtGui import QMessageBox

from cat.sorters import Sorter
from cat.config import AtConfig
from .sidebar import NoSampleError
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

    def sortAscending(self):
        self.sort()

    def sortDescending(self):
        self.sort(reversed_=True)

    def _data_from_items(self, items):
        nitems = len(items)
        nfeatures = items[0].features.size
        data = np.empty((nitems, nfeatures))
        for i, item in enumerate(items):
            data[i, :] = item.features
        return data

    def sort(self, reversed_=False):
        all_items = self.tileview.items
        try:
            sorter = Sorter(self.sortAlgorithm.currentText(), all_items,
                            self.filter_indices)
            sorter.treedata = self.filterFeatures(self.model.features)
        except NoSampleError:
            return

        try:
            dist = sorter()
        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e))
            return

        if reversed_:
            dist = -1*dist

        if dist is not None:
            for d, item in zip(dist, all_items):
                item.sortkey = d
            self.startSorting.emit()
