"""
featuredlg.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

from os.path import splitext
from collections import OrderedDict

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


from cat.config import AtConfig
from .sidebar import AtChannelFeatureGroupsWidget
from cat.gui.loadui import loadUI

class AtFeatureModel(QtGui.QStandardItemModel):

    NAME = 0
    CHANNEL = 1
    INDEX = 2

    def __init__(self, *args, **kw):
        super(AtFeatureModel, self).__init__(*args, **kw)
        self._setupHeader()

    def _setupHeader(self):
        self.insertColumns(0, 3)
        self.setHeaderData(self.NAME, QtCore.Qt.Horizontal, "Name")
        self.setHeaderData(self.CHANNEL, QtCore.Qt.Horizontal, "Channel")
        self.setHeaderData(self.INDEX, QtCore.Qt.Horizontal, "Index")

    def clear(self):
        super(AtFeatureModel, self).clear()
        self._setupHeader()


class AtSortFilterProxyModel(QtCore.QSortFilterProxyModel):

    def __init__(self, *args, **kw):
        super(AtSortFilterProxyModel, self).__init__(*args, **kw)
        self._state_filter = Qt.Unchecked

    def setStateFilter(self, state):
        self._state_filter = state
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent):

        m_index = self.sourceModel().index(sourceRow, 0, sourceParent)
        item = self.sourceModel().item(m_index.row(), 0)

        if item.checkState() == Qt.Unchecked and self._state_filter == Qt.Checked:
            return False
        else:
            return super(AtSortFilterProxyModel, self).filterAcceptsRow(sourceRow, sourceParent)


class AtContextTreeView(QtWidgets.QTreeView):

    def __init__(self, *args, **kw):
        super(AtContextTreeView, self).__init__(*args, **kw)
        self.createActions()
        self.createContextMenu()

    def createActions(self):
        self.actionCheckSelected= QtWidgets.QAction(
            "&check selection", self,
            triggered=lambda: self.toggleItems(True))
        self.actionUnCheckSelected = QtWidgets.QAction(
            "&uncheck selection", self,
            triggered=lambda: self.toggleItems(False))

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def createContextMenu(self):
        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.addAction(self.actionCheckSelected)
        self.context_menu.addAction(self.actionUnCheckSelected)

    def toggleItems(self, state):

        model = self.model().sourceModel()
        model_indices =  self.selectionModel().selectedRows()

        for mi_ in model_indices:
            mi = self.model().mapToSource(mi_)

            item = model.item(mi.row(), 0)
            if state:
                item.setCheckState(Qt.Checked)
            else:

                item.setCheckState(Qt.Unchecked)


class AtFeatureSelectionDlg(QtWidgets.QWidget):

    selectionChanged = QtCore.pyqtSignal(tuple)

    def __init__(self, *args, **kw):
        super(AtFeatureSelectionDlg, self).__init__(*args, **kw)
        uifile = splitext(__file__)[0] + ".ui"
        loadUI(uifile, self)

        self.setWindowFlags(Qt.Window)

        self.regexLbl.setBuddy(self.regex)
        self.regex.textChanged.connect(self.filterChanged)

        self.proxyModel = AtSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(False)
        self.view.setModel(self.proxyModel)
        self.model = AtFeatureModel(self)
        self.setSourceModel(self.model)
        self.selectAll.stateChanged.connect(self.toggleAll)
        self.selectedOnly.stateChanged.connect(self.view.model().setStateFilter)
        self.selectionChanged.connect(self.setSelectionByName)

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

    def _iterGroups(self):
        for i in xrange(self.fbox.count()):
            yield self.fbox.itemAt(i).widget()

    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)

    def toggleAll(self, state):
        for row in xrange(self.model.rowCount()):
            self.model.item(row, 0).setCheckState(state)
        self.filterChanged()

    def filterChanged(self):
        regExp = QtCore.QRegExp(self.regex.text())
        self.proxyModel.setFilterRegExp(regExp)

    def indicesOfCheckedItems(self):
        indices = list()
        for i in xrange(self.model.rowCount()):
            idx_item = self.model.item(i, self.model.INDEX)
            name_item = self.model.item(i, self.model.NAME)
            if name_item.checkState() == Qt.Checked:
                indices.append(int(idx_item.text()))
        return tuple(indices)

    def setSelectionByName(self, names):

        for i in xrange(self.model.rowCount()):
            name_item = self.model.item(i, self.model.NAME)
            channel_item = self.model.item(i, self.model.CHANNEL)

            ftrname = "%s-%s" %(channel_item.text(), name_item.text())
            if ftrname in names:
                name_item.setCheckState(Qt.Checked)
            else:
                name_item.setCheckState(Qt.Unchecked)
        self.filterChanged()

    def checkedItems(self):
        odict = OrderedDict()

        for i in xrange(self.model.rowCount()):
            idx_item = self.model.item(i, self.model.INDEX)
            ch_item = self.model.item(i, self.model.CHANNEL)
            name_item = self.model.item(i, self.model.NAME)
            if name_item.checkState() == Qt.Checked:
                odict[int(idx_item.text())] = \
                    "%s-%s" %(ch_item.text(), name_item.text())

        return odict

    def clear(self):
        self.model.clear()
        self.clearFeatureGroups()

    def addFeatureList(self, feature_names):

        self.selectAll.setChecked(Qt.Checked)
        self.model.clear()

        for i, feature_name in enumerate(feature_names):
            channel, name = feature_name.split("-")
            name_item = QtGui.QStandardItem(name)
            name_item.setCheckable(True)
            name_item.setCheckState(Qt.Checked)

            items = [name_item,
                     QtGui.QStandardItem(channel),
                     QtGui.QStandardItem(str(i))]

            for item in items:
                item.setEditable(False)

            self.model.appendRow(items)

        for i in xrange(self.proxyModel.columnCount()):
            self.view.resizeColumnToContents(i)
