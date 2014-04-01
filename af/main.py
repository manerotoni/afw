"""
main.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from os.path import splitext, basename, expanduser

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4.QtGui import QFileDialog
# from PyQt4 import QtCore

from af.graphicsview import AfGraphicsView


class AfMainWindow(QtGui.QMainWindow):

    def __init__(self, file_=None, *args, **kw):
        super(AfMainWindow, self).__init__(*args, **kw)
        self._lastdir = expanduser("~")
        self._hdf = None

        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowTitle("AfMainWindow")

        self.tileview = AfGraphicsView(parent=self)
        self.setupToolbar()
        self.setCentralWidget(self.tileview)
        self.show()

        if file_ is not None:
            self.openFile(file_)
            self.loadItems()

        self.plate.activated.connect(self.loadItems)
        self.well.activated.connect(self.loadItems)
        self.site.activated.connect(self.loadItems)
        self.region.activated.connect(self.loadItems)

    def closeEvent(self, event):
        try:
            self._hdf.close()
        except AttributeError:
            pass

    def setupToolbar(self):
        toolbar = QtGui.QToolBar(self)
        actionOpen = QtGui.QAction(
            QtGui.QIcon.fromTheme("document-open"), "open", self)
        actionOpen.triggered.connect(self.onFileOpen)
        toolbar.addAction(actionOpen)
        toolbar.addSeparator()

        self.plate = QtGui.QComboBox(self)
        self.well = QtGui.QComboBox(self)
        self.site = QtGui.QComboBox(self)
        self.region = QtGui.QComboBox(self)

        policy = QtGui.QComboBox.AdjustToContents
        self.plate.setSizeAdjustPolicy(policy)
        self.well.setSizeAdjustPolicy(policy)
        self.site.setSizeAdjustPolicy(policy)
        self.region.setSizeAdjustPolicy(policy)

        toolbar.addWidget(self.plate)
        toolbar.addWidget(self.well)
        toolbar.addWidget(self.site)
        toolbar.addWidget(self.region)

        self.addToolBar(toolbar)

    def onFileOpen(self):

        file_ = QFileDialog.getOpenFileName(
            self, "Open hdf5 file", self._lastdir,
            "Hdf files (*.hdf5 *.ch5 *.hdf *.h5)")

        if bool(file_):
            self._lastdir = basename(file_)
            self.loadFromFile(file_)

    def openFile(self, file_):
        try:
            self.tileview.openFile(file_)
        except:
            self.statusBar().showMessage("Error loading file %s" %file_)
        else:
            self.statusBar().showMessage(file_)

    @property
    def coordinate(self):
        return {"plate": self.plate.currentText(),
                "well": self.well.currentText(),
                "site": self.site.currentText(),
                "region": self.region.currentText()}

    def loadItems(self):
        self.tileview.clear()
        self.tileview.loadItems(**self.coordinate)
