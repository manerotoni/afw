"""
featuredlg.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

from os.path import splitext

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4 import uic


class AtFeatureModel(QtGui.QStandardItemModel):

    NAME = 0
    CHANNEL = 1
    INDEX = 2

    def __init__(self, *args, **kw):
        super(AtFeatureModel, self).__init__(*args, **kw)
        self.insertColumns(0, 3)
        self.setHeaderData(self.NAME, QtCore.Qt.Horizontal, "Name")
        self.setHeaderData(self.CHANNEL, QtCore.Qt.Horizontal, "Channel")
        self.setHeaderData(self.INDEX, QtCore.Qt.Horizontal, "Index")

class AtContextTreeView(QtGui.QTreeView):

    def __init__(self, *args, **kw):
        super(AtContextTreeView, self).__init__(*args, **kw)
        self.createActions()
        self.createContextMenu()


    def createActions(self):
        self.actionCheckSelected= QtGui.QAction(
            "&check selection", self,
            triggered=lambda: self.toggleItems(True))
        self.actionUnCheckSelected = QtGui.QAction(
            "&uncheck selection", self,
            triggered=lambda: self.toggleItems(False))

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def createContextMenu(self):
        self.context_menu = QtGui.QMenu(self)
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


class AtFeatureSelectionDlg(QtGui.QWidget):

    def __init__(self, *args, **kw):
        super(AtFeatureSelectionDlg, self).__init__(*args, **kw)
        uifile = splitext(__file__)[0] + ".ui"
        uic.loadUi(uifile, self)

        self.setWindowFlags(Qt.Window)

        self.regexLbl.setBuddy(self.regex)
        self.regex.textChanged.connect(self.filterChanged)

        self.proxyModel = QtGui.QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(False)
        self.view.setModel(self.proxyModel)
        self.model = AtFeatureModel(self)
        self.setSourceModel(self.model)
        self.selectAll.stateChanged.connect(self.toggleAll)

    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)

    def toggleAll(self, state):
        for row in xrange(self.model.rowCount()):
            self.model.item(row, 0).setCheckState(state)

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

    def addFeatureList(self, feature_names):

        self.selectAll.setChecked(Qt.Checked)
        self.model.clear()

        for i, feature_name in enumerate(feature_names):
            try:
                channel, name = feature_name.split("-")
            except ValueError:
                channel = "--"
                name = feature_name

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
