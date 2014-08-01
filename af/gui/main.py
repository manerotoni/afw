"""
main.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from os.path import splitext, basename, expanduser

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFileDialog

from af import version
from af.gui.graphicsview import AfGraphicsView
from af.gui.toolbars import NavToolBar, ViewToolBar
from af.gui.sidebar import AfSortWidget
from af.gui.sidebar import AfAnnotationWidget
from af.gui.importdlg import ImportDialog
from af.threading import AfThread
from af.threading import AfLoader

from af import at_rc

class AtMainWindow(QtGui.QMainWindow):

    coordUpdated = QtCore.pyqtSignal("PyQt_PyObject")
    abort = QtCore.pyqtSignal()

    def __init__(self, file_=None, *args, **kw):
        super(AtMainWindow, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowTitle(version.appstr)
        self.sorting.adjustSize()

        self.loaderThread = AfThread(self)
        self.loader = AfLoader()
        self._lastdir = expanduser("~")

        self.setupToolbar()
        self.tileview = AfGraphicsView(
            parent=self,
            gsize=self.toolBar.galsize,
            show_classes=self.toolBar.classification.isChecked())
        self.toolBar.valueChanged.connect(self.tileview.zoom)
        self.toolBar.classification.stateChanged.connect(
            self.tileview.toggleClassIndicators, Qt.QueuedConnection)

        self.setCentralWidget(self.tileview)
        self.setupDock()
        self.setupProgressBar()

        self.loader.fileOpened.connect(self.updateToolbars)
        self.loader.progressUpdate.connect(self.progressbar.setValue)
        self.loader.itemLoaded.connect(self.tileview.addItem)
        self.abort.connect(self.loader.abort)
        self.actionOpenHdf.triggered.connect(self.onFileOpen)
        self.actionCloseHdf.triggered.connect(self.onFileClose)
        self.actionProcessTrainingSet.triggered.connect(self.openImporter)

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

    def closeEvent(self, event):
        self._saveSettings()
        try:
            self.abort.emit()
            self.loaderThread.wait()
            self.loader.close()
        except AttributeError:
            pass

    def setupDock(self):
        self.sorting = AfSortWidget(self, self.tileview)
        self.annotation = AfAnnotationWidget(self, self.tileview)

        self.toolBox.addItem(self.sorting, "sorting")
        self.toolBox.addItem(self.annotation, "annotation")

    def setupProgressBar(self):
        frame = QtGui.QFrame(self)
        self.progressbar = QtGui.QProgressBar(frame)
        self.progressbar.setMaximumHeight(15)
        self.abortBtn = QtGui.QPushButton('abort', self)
        self.abortBtn.clicked.connect(self.abort.emit)
        self.abortBtn.setMaximumHeight(20)
        hbox = QtGui.QHBoxLayout(frame)
        hbox.addWidget(self.progressbar)
        hbox.addWidget(self.abortBtn)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.loaderThread.started.connect(frame.show)
        self.loaderThread.finished.connect(frame.hide)
        frame.hide()
        self.statusBar().addPermanentWidget(frame)

    def updateToolbars(self, props):
        self.navToolBar.updateToolbar(props.coordspace)
        self.toolBar.updateToolbar(props)

    def setupToolbar(self):
        self.toolBar = ViewToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar.actionOpen.triggered.connect(self.onFileOpen)
        self.toolBar.reloadBtn.clicked.connect(self.loadItems)

        self.navToolBar = NavToolBar(self)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.navToolBar)
        self.navToolBar.coordUpdated.connect(self.loader.setCoordinate)

    def openImporter(self):
        dlg = ImportDialog(self)
        dlg.exec_()

    def addToToolbox(self):
        cw = self.toolBox.currentWidget()
        cw.addItems(self.tileview.selectedItems())

    def onFileClose(self):
        self.loader.close()
        self.tileview.clear()

    def onFileOpen(self):

        file_ = QFileDialog.getOpenFileName(
            self, "Open hdf5 file", self._lastdir,
            "Hdf files (*.hdf5 *.ch5 *.hdf *.h5)")

        if bool(file_):
            self._lastdir = basename(file_)
            try:
                self.loader.openFile(file_)
            except Exception as e:
                self.statusBar().showMessage(str(e))
            else:
                self.statusBar().showMessage(basename(file_))

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
