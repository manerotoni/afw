"""
toolbars.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("NavToolBar", "ViewToolBar")


from PyQt4 import QtGui
from PyQt4 import QtCore
from af.hdfio import Ch5Coord


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
        return Ch5Coord(self.plate.currentText(),
                        self.well.currentText(),
                        self.site.currentText(),
                        self.region.currentText())

    def _cBoxChanged(self):
        self.coordUpdated.emit(self.coordinate)

    def updateToolbar(self, coordspace):
        self.plate.clear()
        self.well.clear()
        self.site.clear()
        self.region.clear()

        self.plate.addItems(coordspace['plate'])
        self.well.addItems(coordspace['well'])
        self.site.addItems(coordspace['site'])
        self.region.addItems(coordspace['region'])

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
        self.zoom.addItem("125%", QtCore.QVariant(1.25))
        self.zoom.addItem("150%", QtCore.QVariant(1.5))
        self.zoom.addItem("200%", QtCore.QVariant(2.0))
        self.zoom.addItem("400%", QtCore.QVariant(4.0))
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

    def updateToolbar(self, props):

        self.nItems.setEnabled(props.gal_settings_mutable)
        self.galSize.setEnabled(props.gal_settings_mutable)
        self.nItems.setValue(props.n_items)
        self.galSize.setValue(props.gallery_size)

    def onIndexChanged(self, index):
        zfactor = self.zoom.itemData(index).toDouble()[0]
        self.valueChanged.emit(zfactor)

    @property
    def galsize(self):
        return self.galSize.value()

    @property
    def nitems(self):
        return self.nItems.value()
