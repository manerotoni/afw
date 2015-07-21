"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtSortWidget', 'AtChannelFeatureGroupsWidget')


from os.path import dirname, join
import numpy as np

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QMessageBox

from cat.sorters import Sorter, SortingError
from cat.config import AtConfig
from .sidebar import NoSampleError
from .sidebar import AtSideBarWidget
from .models import  AtSorterItemModel


from cat.segmentation.channelname import ChannelName as cn


class AtChannelFeatureGroupsWidget(QtWidgets.QWidget):

    selectionChanged = QtCore.pyqtSignal()

    def __init__(self, title, table, *args, **kw):
        super(AtChannelFeatureGroupsWidget, self).__init__(*args, **kw)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.gbox = QtWidgets.QGroupBox(self)

        self.gbox.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.gbox)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(1)

        self.gbox.layout().setContentsMargins(1, 1, 1, 1)
        self.gbox.layout().setSpacing(1)

        self.gbox.setTitle(cn.display(title))

        self._table = table

        for group, names in self._table.iteritems():
            self.addFeatureGroup(group, names)

    def addFeatureGroup(self, group, feature_names):
        checkbox = QtWidgets.QCheckBox(group)
        checkbox.setCheckState(QtCore.Qt.Checked)
        checkbox.stateChanged.connect(self.onStateChanged)
        self.gbox.layout().addWidget(checkbox)

    def currentFeatureNames(self):
        features = list()
        prefix = cn.abreviate(self.gbox.title())
        layout = self.gbox.layout()
        for i in xrange(layout.count()):
            cb = layout.itemAt(i).widget()
            if cb.isChecked():
                ftrs = ("%s-%s" %(prefix, f) for f in self._table[cb.text()])
                features.extend(ftrs)
        return features

    def onStateChanged(self, dummy=None):
        self.selectionChanged.emit()


class AtSortWidget(AtSideBarWidget):

    startSorting = QtCore.pyqtSignal()
    selectionChanged = QtCore.pyqtSignal(tuple)

    def __init__(self, *args, **kw):
        super(AtSortWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)

        self.treeview.activated.connect(self.onActivated)

        self.sortAlgorithm.addItems(Sorter.sorters())

        self.model = AtSorterItemModel(self)
        self.treeview.setModel(self.model)
        self.setupToolBar()

        self.startSorting.connect(
            lambda: self.tileview.reorder(force_update=True))

        self._channels = tuple()

    def setupToolBar(self):

        toolbar =  QtWidgets.QToolBar(self)
        toolbar.setIconSize(QtCore.QSize(16, 16))
        self.vbox.addWidget(toolbar)

        self.addBtn = QtWidgets.QToolButton()
        self.addBtn.setToolTip("Add items")
        self.addBtn.setIcon(QtGui.QIcon(":/oxygen/list-add.png"))
        self.addBtn.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.addBtn.pressed.connect(self.onAdd)

        self.removeBtn = QtWidgets.QToolButton()
        self.removeBtn.setToolTip("Remove selected Items")
        self.removeBtn.setIcon(QtGui.QIcon(":/oxygen/list-remove.png"))
        self.removeBtn.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.removeBtn.pressed.connect(self.removeSelected)


        self.removeAllBtn = QtWidgets.QToolButton()
        self.removeAllBtn.setToolTip("Clear Items")
        self.removeAllBtn.setIcon(QtGui.QIcon(":/oxygen/edit-clear.png"))
        self.removeAllBtn.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.removeAllBtn.pressed.connect(self.removeAll)

        self.sortAscendingBtn = QtWidgets.QToolButton()
        self.sortAscendingBtn.setToolTip("Sort ascending")
        self.sortAscendingBtn.setIcon(
            QtGui.QIcon(":/oxygen/sort-ascending.png"))
        self.sortAscendingBtn.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.sortAscendingBtn.pressed.connect(self.sortAscending)

        self.sortDescendingBtn = QtWidgets.QToolButton()
        self.sortDescendingBtn.setToolTip("Sort descending")
        self.sortDescendingBtn.setIcon(
            QtGui.QIcon(":/oxygen/sort-descending.png"))
        self.sortDescendingBtn.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.sortDescendingBtn.pressed.connect(self.sortDescending)

        toolbar.addWidget(self.addBtn)
        toolbar.addWidget(self.removeBtn)
        toolbar.addWidget(self.removeAllBtn)
        toolbar.addWidget(self.sortAscendingBtn)
        toolbar.addWidget(self.sortDescendingBtn)

    def clear(self):
        self.clearFeatureGroups()

    def _iterGroups(self):
        for i in xrange(self.fbox.count()):
            yield self.fbox.itemAt(i).widget()

    def setFeatureGroups(self, feature_groups):
        self.clearFeatureGroups()
        self._channels = feature_groups.keys()
        for chn, tables in feature_groups.iteritems():
            table = tables[AtConfig().default_feature_group]
            fgw = AtChannelFeatureGroupsWidget(chn, table, self)
            self.fbox.insertWidget(self.fbox.count(), fgw)
            fgw.selectionChanged.connect(self.onSelectionChanged)
            setattr(self, chn.lower(), fgw)

    def clearFeatureGroups(self):
        for i in xrange(self.fbox.count()):
            item = self.fbox.takeAt(0)
            item.widget().close()
        self._channels = None

    def onSelectionChanged(self):
        self.selectionChanged.emit(self.currentFeatureNames())

    def currentFeatureNames(self):
        feature_names = list()
        for widget in self._iterGroups():
            feature_names.extend(widget.currentFeatureNames())
        return tuple(feature_names)

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


    def sort(self, reversed_=False):
        all_items = self.tileview.items
        try:
            if not all_items:
                raise NoSampleError
            sorter = Sorter(self.sortAlgorithm.currentText(), all_items,
                            self.sort_filter_indices)
            if sorter.requiresTreeData():
                sorter.treedata = self.sortFilterFeatures(self.model.features)
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

    def sortFilterFeatures(self, features):
        ftrs_indices = self.sort_filter_indices

        if not ftrs_indices or features is None:
            raise NoSampleError("no features selected for classifier training")

        return features[:, ftrs_indices]

    @property
    def sort_filter_indices(self):

        old_names = self.featuredlg.checkedItems().values()
        sorter_features = self.currentFeatureNames()

        # intersection of both lists, don't want use already excluded features
        # for sorting
        sorter_features = tuple(set(sorter_features).intersection(old_names))

        self.featuredlg.setSelectionByName(sorter_features)
        fidx = self.featuredlg.indicesOfCheckedItems()
        self.featuredlg.setSelectionByName(old_names)

        return fidx
