"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtSortWidget', )


from os.path import dirname, join
import numpy as np

from PyQt4 import uic
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtGui import QMessageBox

from cat.sorters import Sorter
from cat.config import AtConfig
from .sidebar import NoSampleError
from .sidebar import AtSideBarWidget
from .models import  AtSorterItemModel

from .feature_tables import FeatureTables
from cat.segmentation.channelname import ChannelName as cn


class AtChannelFeatureGroupsWidget(QtGui.QWidget):

    selectionChanged = QtCore.pyqtSignal()

    def __init__(self, title, table,  *args, **kw):
        super(AtChannelFeatureGroupsWidget, self).__init__(*args, **kw)
        self.setLayout(QtGui.QVBoxLayout())
        self.gbox = QtGui.QGroupBox(self)

        self.gbox.setLayout(QtGui.QVBoxLayout())
        self.layout().addWidget(self.gbox)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.gbox.setTitle(cn.display(title))

        if table is None:
            self._table = FeatureTables.values()[0]
        else:
            self._table = FeatureTables[table]

        for group, names in self._table.iteritems():
            self.addFeatureGroup(group, names)

    def addFeatureGroup(self, group, feature_names):
        checkbox = QtGui.QCheckBox(group)
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

        self.removeBtn.clicked.connect(self.removeSelected)
        self.removeAllBtn.clicked.connect(self.removeAll)
        self.addBtn.clicked.connect(self.onAdd)
        self.sortBtn.clicked.connect(self.sort)
        self.startSorting.connect(
            lambda: self.tileview.reorder(force_update=True))

        self._channels = tuple()
        self.ftable.addItems(FeatureTables.keys())
        self.ftable.currentIndexChanged[str].connect(self.onTableChanged)

    def onTableChanged(self, table):
        self.setChannelNames(self._channels, table)

    def _iterGroups(self):
        for i in xrange(self.fbox.count()):
            yield self.fbox.itemAt(i).widget()

    def setChannelNames(self, channel_names, table=None):
        self.clearChannels()
        self._channels = channel_names
        for chn in channel_names:
            fgw = AtChannelFeatureGroupsWidget(chn, table, self)
            self.fbox.insertWidget(self.fbox.count(), fgw)
            fgw.selectionChanged.connect(self.onSelectionChanged)
            setattr(self, chn.lower(), fgw)

    def clearChannels(self):
        for i in xrange(self.fbox.count()):
            item = self.fbox.takeAt(0)
            item.widget().close()

    def onSelectionChanged(self):
        feature_names = list()
        for widget in self._iterGroups():
            feature_names.extend(widget.currentFeatureNames())
        self.selectionChanged.emit(tuple(feature_names))

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
