"""
main.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from os.path import splitext, basename, expanduser

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QFileDialog

from af import version
from af.gui.graphicsview import AfGraphicsView
from af.gui.toolbars import NavToolBar, ViewToolBar
from af.gui.sidebar import AfSortWidget
from af.gui.sidebar import AfAnnotationWidget
from af.loader import AfLoader, AfLoaderThread

# import resources
from af import af_rc

class AfMainWindow(QtGui.QMainWindow):

    coordUpdated = QtCore.pyqtSignal("PyQt_PyObject")
    abort = QtCore.pyqtSignal()

    def __init__(self, file_=None, *args, **kw):
        super(AfMainWindow, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowTitle("AfMainWindow")
        self.sorting.adjustSize()

        self.loaderThread = AfLoaderThread(self)
        self.loader = AfLoader()
        self._lastdir = expanduser("~")

        self.setupToolbar()
        self.tileview = AfGraphicsView(parent=self, gsize=self.toolBar.galsize)
        self.toolBar.valueChanged.connect(self.tileview.zoom)
        self.setCentralWidget(self.tileview)
        self.setupDock()
        self.setupProgressBar()

        self.loader.progressUpdate.connect(self.progressbar.setValue)
        self.loader.fileOpened.connect(self.navToolBar.updateNavToolbar)
        self.loader.itemLoaded.connect(self.tileview.addItem)
        self.abort.connect(self.loader.abort)
        self.actionOpen.triggered.connect(self.onFileOpen)

        self._restoreSettings()
        self.show()
        if file_ is not None:
            self.openFile(file_)
            self.loadItems()

    def _saveSettings(self):
        settings = QtCore.QSettings(version.organisation, version.appname)
        settings.beginGroup('Gui')
        settings.setValue('state', self.saveState())
        settings.setValue('geometry', self.saveGeometry())
        settings.endGroup()

    def _restoreSettings(self):
        settings = QtCore.QSettings(version.organisation, version.appname)
        settings.beginGroup('Gui')

        geometry = settings.value('geometry')
        if geometry is not None:
            self.restoreGeometry(geometry.toByteArray())
        state = settings.value('state')
        if state is not None:
            self.restoreState(state.toByteArray())
        settings.endGroup()

    def onAbort(self):
        self.abort.emit()

    def closeEvent(self, event):
        self._saveSettings()
        try:
            self.abort.emit()
            self.loaderThread.wait()
            self.loader.close()
        except AttributeError:
            pass

    def setupDock(self):
        self.sorting = AfSortWidget(self.tileview)
        self.annotation = AfAnnotationWidget(self.tileview)

        self.toolBox.addItem(self.sorting, "sorting")
        self.toolBox.addItem(self.annotation, "annotation")

    def setupProgressBar(self):
        self.progressbar = QtGui.QProgressBar(self)
        self.progressbar.setMaximumHeight(15)
        self.abortBtn = QtGui.QPushButton('abort', self)
        self.abortBtn.clicked.connect(self.onAbort)
        self.abortBtn.setMaximumHeight(20)
        frame = QtGui.QFrame(self)
        hbox = QtGui.QHBoxLayout(frame)
        hbox.addWidget(self.progressbar)
        hbox.addWidget(self.abortBtn)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.loaderThread.started.connect(frame.show)
        self.loaderThread.finished.connect(frame.hide)
        frame.hide()
        self.statusBar().addPermanentWidget(frame)

    def setupToolbar(self):
        self.toolBar = ViewToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar.actionOpen.triggered.connect(self.onFileOpen)
        self.toolBar.reloadBtn.clicked.connect(self.loadItems)

        self.navToolBar = NavToolBar(self)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.navToolBar)
        self.navToolBar.coordUpdated.connect(self.loader.setCoordinate)

    def onFileOpen(self):

        file_ = QFileDialog.getOpenFileName(
            self, "Open hdf5 file", self._lastdir,
            "Hdf files (*.hdf5 *.ch5 *.hdf *.h5)")

        if bool(file_):
            self._lastdir = basename(file_)
            self.openFile(file_)

    def openFile(self, file_):

        try:
            self.loader.openFile(file_)
        except Exception as e:
            self.statusBar().showMessage(str(e))
        else:
            self.statusBar().showMessage(basename(file_))

    def addToToolbox(self):
        cw = self.toolBox.currentWidget()
        cw.addItems(self.tileview.selectedItems())

    def loadItems(self):

        self.abort.emit()
        self.loaderThread.wait()

        self.tileview.clear()
        self.tileview.updateRaster(self.toolBar.galsize)
        self.tileview.updateNColumns(self.tileview.size().width())

        self.progressbar.setRange(0, self.toolBar.nitems)
        self.loader.setNumberItems(self.toolBar.nitems)
        self.loader.setGallerySize(self.toolBar.galsize)
        self.loaderThread.start(self.loader)
