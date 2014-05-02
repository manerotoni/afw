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
        self.setObjectName('NavigationToolbar')

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

    valueChanged = QtCore.pyqtSignal(float)

    def __init__(self, *args, **kw):
        super(ViewToolBar, self).__init__(*args, **kw)
        self.setObjectName("ViewToolbar")
        self.setIconSize(QtCore.QSize(16, 16))

        self.galSize = QtGui.QSpinBox(self)
        self.galSize.setPrefix("gallery size: ")
        self.galSize.setRange(0, 256)
        self.galSize.setValue(65)

        self.nItems = QtGui.QSpinBox(self)
        self.nItems.setPrefix("number items: ")
        self.nItems.setRange(0, 1e9)
        self.nItems.setSingleStep(50)
        self.nItems.setValue(250)

        self.zoom =  QtGui.QComboBox(self)
        self.zoom.addItem("100%", QtCore.QVariant(1.0))
        self.zoom.addItem("75%", QtCore.QVariant(0.75))
        self.zoom.addItem("50%", QtCore.QVariant(0.50))
        self.zoom.addItem("25%", QtCore.QVariant(0.25))
        self.zoom.currentIndexChanged.connect(self.onIndexChanged)
        self.reloadBtn = QtGui.QPushButton("load", self)

        icon = QtGui.QIcon(":/hdf5-logo.png")
        self.actionOpen = QtGui.QAction(
            icon, "open", self)
        self.addAction(self.actionOpen)
        self.addWidget(self.reloadBtn)
        self.addSeparator()
        self.addWidget(self.galSize)
        self.addWidget(self.nItems)
        self.addWidget(self.zoom)

    def onIndexChanged(self, index):
        zfactor = self.zoom.itemData(index).toDouble()[0]
        self.valueChanged.emit(zfactor)

    @property
    def galsize(self):
        return self.galSize.value()

    @property
    def nitems(self):
        return self.nItems.value()
