"""
toolbars.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("NavToolBar", "ViewToolBar", "SortToolBar")


from PyQt5 import QtGui
from PyQt5 import QtCore

from cat.sorters import Sorter
from cat.hdfio.cellh5reader import Ch5Coord


class AtToolBar(QtGui.QToolBar):

    def __init__(self, *args, **kw):
        super(AtToolBar, self).__init__(*args, **kw)
        self.setObjectName(self.__class__.__name__)
        self.setWindowTitle(self.__class__.__name__)
        self.setIconSize(QtCore.QSize(24, 24))


class NavToolBar(AtToolBar):

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


class ViewToolBar(AtToolBar):

    valueChanged = QtCore.pyqtSignal(float)

    def __init__(self, *args, **kw):
        super(ViewToolBar, self).__init__(*args, **kw)
        self.setObjectName("ViewToolbar")

        self.galSize = QtGui.QSpinBox(self)
        self.galSize.setRange(0, 256)
        self.galSize.setValue(65)

        self.nItems = QtGui.QSpinBox(self)
        self.nItems.setRange(0, 1e9)
        self.nItems.setSingleStep(50)
        self.nItems.setValue(250)

        self.classification = QtGui.QCheckBox("Classifcation", self)
        self.masking = QtGui.QCheckBox("Mask", self)

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

        icon = QtGui.QIcon(":/oxygen/document-open-folder.png")
        self.actionOpen = QtGui.QAction(
            icon, "open", self)
        self.addAction(self.actionOpen)
        self.addWidget(self.reloadBtn)
        self.addSeparator()
        self.addWidget(QtGui.QLabel("gallery size:", self))
        self.addWidget(self.galSize)
        self.addWidget(QtGui.QLabel("number items:", self))
        self.addWidget(self.nItems)
        self.addSeparator()
        self.addWidget(self.zoom)
        self.addWidget(self.classification)
        self.addWidget(self.masking)

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


class SortToolBar(AtToolBar):

    def __init__(self, *args, **kw):
        super(SortToolBar, self).__init__(*args, **kw)

        self.sortAscendingBtn = QtGui.QToolButton(self)
        self.sortAscendingBtn.setToolTip("Sort ascending")
        self.sortAscendingBtn.setIcon(
            QtGui.QIcon(":/oxygen/sort-ascending.png"))
        self.sortDescendingBtn = QtGui.QToolButton(self)
        self.sortDescendingBtn.setToolTip("Sort descending")
        self.sortDescendingBtn.setIcon(
            QtGui.QIcon(":/oxygen/sort-descending.png"))

        self.sortAlgorithm = QtGui.QComboBox(self)
        self.sortAlgorithm.setToolTip(
            ("Similarity measure used for sorting"))
        self.sortAlgorithm.addItems(Sorter.sorters())

        self.addWidget(self.sortAscendingBtn)
        self.addWidget(self.sortDescendingBtn)
        self.addWidget(self.sortAlgorithm)
