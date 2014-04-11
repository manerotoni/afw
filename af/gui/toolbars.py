"""
toolbars.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("NavToolBar", "ViewToolBar")


from PyQt4 import QtGui
from PyQt4 import QtCore
from af.hdfio import HdfCoord


class NavToolBar(QtGui.QToolBar):

    coordUpdated = QtCore.pyqtSignal("PyQt_PyObject")

    def __init__(self, *args, **kw):
        super(NavToolBar, self).__init__(*args, **kw)

        self.plate = QtGui.QComboBox(self)
        self.well = QtGui.QComboBox(self)
        self.site = QtGui.QComboBox(self)
        self.region = QtGui.QComboBox(self)

        policy = QtGui.QComboBox.AdjustToContents
        self.plate.setSizeAdjustPolicy(policy)
        self.well.setSizeAdjustPolicy(policy)
        self.site.setSizeAdjustPolicy(policy)
        self.region.setSizeAdjustPolicy(policy)

        self.addWidget(self.plate)
        self.addWidget(self.well)
        self.addWidget(self.site)
        self.addWidget(self.region)

        self.plate.activated.connect(self._cBoxChanged)
        self.well.activated.connect(self._cBoxChanged)
        self.site.activated.connect(self._cBoxChanged)
        self.region.activated.connect(self._cBoxChanged)

    @property
    def coordinate(self):
        return HdfCoord(self.plate.currentText(),
                        self.well.currentText(),
                        self.site.currentText(),
                        self.region.currentText())

    def _cBoxChanged(self):
        self.coordUpdated.emit(self.coordinate)

    def updateNavToolbar(self, coords):
        self.plate.clear()
        self.well.clear()
        self.site.clear()
        self.region.clear()
        self.plate.addItems(coords['plate'])
        self.well.addItems(coords['well'])
        self.site.addItems(coords['site'])
        self.region.addItems(coords['region'])

        self.coordUpdated.emit(self.coordinate)


class ViewToolBar(QtGui.QToolBar):

    def __init__(self, *args, **kw):
        super(ViewToolBar, self).__init__(*args, **kw)

        self.galSize = QtGui.QSpinBox(self)
        self.galSize.setPrefix("gallery size: ")
        self.galSize.setRange(0, 256)
        self.galSize.setValue(65)

        self.nItems = QtGui.QSpinBox(self)
        self.nItems.setPrefix("number items: ")
        self.nItems.setRange(0, 1e9)
        self.nItems.setSingleStep(50)
        self.nItems.setValue(250)

        self.reloadBtn = QtGui.QPushButton("reload", self)
        self.sortBtn = QtGui.QPushButton("sort", self)

        self.actionOpen = QtGui.QAction(
            QtGui.QIcon.fromTheme("document-open"), "open", self)
        self.addAction(self.actionOpen)
        self.addSeparator()
        self.addWidget(self.galSize)
        self.addWidget(self.nItems)
        self.addWidget(self.reloadBtn)


    @property
    def galsize(self):
        return self.galSize.value()

    @property
    def nitems(self):
        return self.nItems.value()
