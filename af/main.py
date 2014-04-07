"""
main.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from os.path import splitext, basename, expanduser

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4.QtGui import QFileDialog

from af.graphicsview import AfGraphicsView


class AfMainWindow(QtGui.QMainWindow):

    def __init__(self, file_=None, *args, **kw):
        super(AfMainWindow, self).__init__(*args, **kw)
        self._lastdir = expanduser("~")
        self._hdf = None

        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowTitle("AfMainWindow")

        self.galSize = QtGui.QSpinBox(self)
        self.galSize.setPrefix("gallery size: ")
        self.galSize.setRange(0, 256)
        self.galSize.setValue(75)

        self.nItems = QtGui.QSpinBox(self)
        self.nItems.setPrefix("number items: ")
        self.nItems.setRange(0, 1e9)
        self.nItems.setSingleStep(50)
        self.nItems.setValue(1000)

        self.reloadBtn = QtGui.QPushButton("reload", self)
        self.reloadBtn.clicked.connect(self.loadItems)
        self.tileview = AfGraphicsView(parent=self, gsize=self.galSize.value())

        self.setupToolbar()
        self.setCentralWidget(self.tileview)
        self.setupProgressBar()

        self.tileview.itemLoaded.connect(self.progressbar.setValue)
        self.show()

        if file_ is not None:
            self.openFile(file_)
            self.loadItems()

        self.galSize.valueChanged.connect(self.tileview.updateRaster)
        self.plate.activated.connect(self.loadItems)
        self.well.activated.connect(self.loadItems)
        self.site.activated.connect(self.loadItems)
        self.region.activated.connect(self.loadItems)

    def closeEvent(self, event):
        try:
            self._hdf.close()
        except AttributeError:
            pass

    def setupProgressBar(self):
        self.progressbar = QtGui.QProgressBar(self)
        frame = QtGui.QFrame(self)
        vbox = QtGui.QVBoxLayout(frame)
        vbox.addWidget(self.progressbar)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.statusBar().addPermanentWidget(frame)

    def setupToolbar(self):
        actionOpen = QtGui.QAction(
            QtGui.QIcon.fromTheme("document-open"), "open", self)
        actionOpen.triggered.connect(self.onFileOpen)
        self.toolBar.addAction(actionOpen)
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.galSize)
        self.toolBar.addWidget(self.nItems)
        self.toolBar.addWidget(self.reloadBtn)

        self.plate = QtGui.QComboBox(self)
        self.well = QtGui.QComboBox(self)
        self.site = QtGui.QComboBox(self)
        self.region = QtGui.QComboBox(self)

        policy = QtGui.QComboBox.AdjustToContents
        self.plate.setSizeAdjustPolicy(policy)
        self.well.setSizeAdjustPolicy(policy)
        self.site.setSizeAdjustPolicy(policy)
        self.region.setSizeAdjustPolicy(policy)

        self.navToolBar.addWidget(self.plate)
        self.navToolBar.addWidget(self.well)
        self.navToolBar.addWidget(self.site)
        self.navToolBar.addWidget(self.region)

    def onFileOpen(self):

        file_ = QFileDialog.getOpenFileName(
            self, "Open hdf5 file", self._lastdir,
            "Hdf files (*.hdf5 *.ch5 *.hdf *.h5)")

        if bool(file_):
            self._lastdir = basename(file_)
            self.openFile(file_)

    def openFile(self, file_):
        try:
            self.tileview.openFile(file_)
        except:
            self.statusBar().showMessage("Error loading file %s" %file_)
        else:
            self.statusBar().showMessage(basename(file_))

    @property
    def coordinate(self):
        return {"plate": self.plate.currentText(),
                "well": self.well.currentText(),
                "site": self.site.currentText(),
                "region": self.region.currentText()}

    def loadItems(self):

        self.progressbar.setRange(0, self.nItems.value())
        self.tileview.clear()
        self.tileview.loadItems(size=self.galSize.value(),
                                nitems=self.nItems.value(),
                                **self.coordinate)
