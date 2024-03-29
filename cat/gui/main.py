"""
main.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import sys
from os.path import splitext, basename, expanduser, abspath

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QKeySequence


from cat import version
from cat.config import AtConfig
from cat.gui.loadui import loadUI
from cat.gui.graphicsview import AtGraphicsView
from cat.gui.toolbars import NavToolBar, ViewToolBar, SortToolBar
from cat.gui.sidebar import AtSortWidget
from cat.gui.sidebar import AtAnnotationWidget
from cat.gui.sidebar import AtContrastWidget
from cat.gui.importdlg import ImportDialog
from cat.gui.aboutdialog import AtAboutDialog
from cat.gui.featuredlg import AtFeatureSelectionDlg
from cat.gui.helpbrowser import AtAssistant
from cat.gui.helpbrowser import MANUAL
from cat.gui.prefdialog import AtPreferencesDialog
from cat.threading import AtThread
from cat.threading import AtLoader
from cat.export import CsvExporter, StatsExporter

from cat import cat_rc


def fix_path(path):
    "Windows sucks!"
    if sys.platform.startswith("win"):
        return path.strip("/")
    else:
        return path


class AtMainWindow(QtWidgets.QMainWindow):

    coordUpdated = QtCore.pyqtSignal("PyQt_PyObject")
    abort = QtCore.pyqtSignal()

    def __init__(self, file_=None, *args, **kw):
        super(AtMainWindow, self).__init__(*args, **kw)
        loadUI(splitext(__file__)[0]+'.ui', self)

        self.setWindowTitle(version.appstr)
        self.setAcceptDrops(True)

        self.featuredlg = AtFeatureSelectionDlg(self)
        self.featuredlg.hide()

        self.loaderThread = AtThread(self)
        self.loader = AtLoader()
        self._lastdir = expanduser("~")

        try:
            self.assistant = AtAssistant(MANUAL)
            self.assistant.hide()
        except IOError:
            QMessageBox.information(self, "Information",
                                    "Sorry help files are not installed")

        self.setupToolbar()
        self.tileview = AtGraphicsView(
            parent=self,
            gsize=self.navToolBar.galsize)
        self.toolBar.valueChanged.connect(self.tileview.zoom)
        self.toolBar.classification.stateChanged.connect(
            self.tileview.toggleClassIndicators, Qt.QueuedConnection)
        self.toolBar.masking.stateChanged.connect(
            self.tileview.toggleMasks, Qt.QueuedConnection)
        self.toolBar.outline.stateChanged.connect(
            self.tileview.toggleOutlines, Qt.QueuedConnection)
        self.toolBar.description.stateChanged.connect(
            self.tileview.toggleDescription, Qt.QueuedConnection)

        self.setCentralWidget(self.tileview)
        self.setupDock()
        self.setupProgressBar()

        self.loader.fileOpened.connect(self.updateToolbars)
        self.loader.progressUpdate.connect(self.updateProgressBar)
        self.loader.itemLoaded.connect(self.tileview.addItem)
        self.abort.connect(self.loader.abort)
        self.actionNewFile.triggered.connect(self.newDataFile)
        self.actionOpenHdf.triggered.connect(self.onFileOpen)
        self.actionCloseHdf.triggered.connect(self.onFileClose)
        self.actionPreferences.triggered.connect(self.onPreferences)
        self.actionExportViewPanel.triggered.connect(self.saveImage)
        self.actionSaveData2Csv.triggered.connect(self.saveData2Csv)
        self.actionSaveCountingStats.triggered.connect(self.saveCountingStats)
        self.actionAboutQt.triggered.connect(self.onAboutQt)
        self.actionAboutAnnotationTool.triggered.connect(self.onAbout)
        self.actionFeatureSelection.triggered.connect(
            self.showFeatureDlg)
        self.actionHelpManual.triggered.connect(self.onHelpManual)
        self.actionShortcuts.triggered.connect(self.onHelpShortcuts)

        self.actionRefresh.triggered.connect(self.refresh)
        self.actionSelectAll.triggered.connect(
            self.tileview.actionSelectAll.trigger)
        self.actionInvertSelection.triggered.connect(
            self.tileview.actionInvertSelection.trigger)

        self.tileview.zoomChanged.connect(self.updateZoomFactor)

        self.featuredlg.selectionChanged.connect(
            self.annotation.predictionInvalid)

        self.loader.started.connect(self.onLoadingStarted)

        self.zoom = QtWidgets.QLabel('100%')
        self.statusbar.insertPermanentWidget(0, self.zoom)
        self.statusbar.insertPermanentWidget(1,
            QtWidgets.QLabel('Number of items:'))
        self.nitems = QtWidgets.QLabel('0')
        self.statusbar.insertPermanentWidget(2, self.nitems)

        self._restoreSettings()
        self.navToolBar.hide()
        self.show()
        if file_ is not None:
            self.loader.openFile(file_)
            self.loadItems()

    def updateProgressBar(self, value):

        if value < 0:
            self.progressbar.setRange(0, 0)

        self.progressbar.setValue(value)

    def updateZoomFactor(self, factor):
        self.zoom.setText("%d%s" %(round(100*factor, 0), "%"))

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            if len(mimeData.urls()) == 1:
                self.abort.emit()
                self.loaderThread.wait()
                self.loader.close()
                self.onDropEvent(fix_path(mimeData.urls()[0].path()))
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        event.accept()

    def onHelpManual(self):
        self.assistant.show()
        self.assistant.raise_()

    def onHelpShortcuts(self):
        self.onHelpManual()
        self.assistant.openKeyword("Shortcuts")

    def refresh(self):
        self.tileview.actionRefresh.trigger()
        self.contrast.enhanceContrast()

    def showFeatureDlg(self):
        self.featuredlg.show()
        self.featuredlg.raise_()

    def onPreferences(self):
        dlg = AtPreferencesDialog(self)
        dlg.exec_()

    def onAboutQt(self):
        QMessageBox.aboutQt(self, "about Qt")

    def onAbout(self):
        dlg = AtAboutDialog(self)
        dlg.exec_()

    def _saveSettings(self):
        settings = QtCore.QSettings(version.organisation, version.appname)
        settings.beginGroup('Gui')
        settings.setValue('state', self.saveState())
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('classifier',
                          self.annotation.classifiers.currentText())
        settings.endGroup()

        AtConfig().saveSettings()


    def _restoreSettings(self):
        settings = QtCore.QSettings(version.organisation, version.appname)
        settings.beginGroup('Gui')

        if settings.contains('geometry'):
            geometry = settings.value('geometry')
            self.restoreGeometry(geometry)

        if settings.contains('state'):
            state = settings.value('state')
            self.restoreState(state)

        if settings.contains('classifier'):
            clfname = settings.value("classifier")
            self.annotation.setCurrentClassifier(clfname)

        AtConfig().restoreSettings()
        settings.endGroup()

    def closeEvent(self, event):
        self.assistant.close()
        self._saveSettings()
        try:
            self.abort.emit()
            self.loaderThread.wait()
            self.loader.close()

            if self.assistant is not None:
                self.assistant.close()

        except AttributeError:
            pass

    def setupDock(self):
        self.contrast = AtContrastWidget(self, self.tileview)
        self.sorting = AtSortWidget(self, self.tileview, self.featuredlg)
        self.annotation = AtAnnotationWidget(
            self, self.tileview, self.featuredlg)

        self.contrastdock = QtWidgets.QDockWidget("Contrast", self)
        self.contrastdock.setWidget(self.contrast)
        self.contrastdock.setObjectName("contrast")
        self.addDockWidget(Qt.LeftDockWidgetArea, self.contrastdock)

        self.sortdock = QtWidgets.QDockWidget("Sorting", self)
        self.sortdock.setWidget(self.sorting)
        self.sortdock.setObjectName("sorting")
        self.addDockWidget(Qt.RightDockWidgetArea, self.sortdock)

        self.annodock = QtWidgets.QDockWidget("Annotation", self)
        self.annodock.setWidget(self.annotation)
        self.annodock.setObjectName("annotation")
        self.addDockWidget(Qt.RightDockWidgetArea, self.annodock)

        self.tabifyDockWidget(self.sortdock, self.annodock)

        # add action to the view menu
        sort_action = self.sortdock.toggleViewAction()
        sort_action.setShortcuts(QKeySequence(Qt.ALT +  Qt.SHIFT + Qt.Key_S))
        self.menuView.addAction(sort_action)

        anno_action = self.annodock.toggleViewAction()
        anno_action.setShortcuts(QKeySequence(Qt.ALT +  Qt.SHIFT + Qt.Key_A))
        self.menuView.addAction(anno_action)

        contrast_action = self.contrastdock.toggleViewAction()
        contrast_action.setShortcuts(
            QKeySequence(Qt.ALT +  Qt.SHIFT + Qt.Key_C))
        self.menuView.addAction(contrast_action)

        # crosslink sorter dock and sorter toolbar
        self.sortToolBar.sortAlgorithm.currentIndexChanged.connect(
            self.sorting.sortAlgorithm.setCurrentIndex)
        self.sorting.sortAlgorithm.currentIndexChanged.connect(
            self.sortToolBar.sortAlgorithm.setCurrentIndex)

        self.sortToolBar.sortAscendingBtn.clicked.connect(
            self.sorting.sortAscending)
        self.sortToolBar.sortDescendingBtn.clicked.connect(
            self.sorting.sortDescending)

    def setupProgressBar(self):
        frame = QtWidgets.QFrame(self)
        self.progressbar = QtWidgets.QProgressBar(frame)
        self.progressbar.setMaximumHeight(15)
        self.abortBtn = QtWidgets.QPushButton('abort', self)
        self.abortBtn.clicked.connect(self.abort.emit)
        self.abortBtn.setMaximumHeight(20)
        hbox = QtWidgets.QHBoxLayout(frame)
        hbox.addWidget(self.progressbar)
        hbox.addWidget(self.abortBtn)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.loaderThread.started.connect(frame.show)
        self.loaderThread.finished.connect(frame.hide)
        frame.hide()
        self.statusBar().addPermanentWidget(frame)

    def saveImage(self):
        filename = QFileDialog.getSaveFileName(
            self, "Save image as ...",
            self._lastdir.replace('.hdf', '.png'),
            "png - Image (*.png)")[0]


        if filename:
            scene = self.tileview.scene()
            size = scene.sceneRect().size().toSize()
            image = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
            painter = QtGui.QPainter(image)

            image.fill(QtCore.Qt.white)
            scene.render(painter)
            painter.end()
            image.save(filename)
            self.statusBar().showMessage("Image saved to %s" %filename)

    def saveData2Csv(self):

        filename = QFileDialog.getSaveFileName(
            self, "Save csv-file as ...",
            self._lastdir.replace(".hdf", ".csv"),
            "Comma separated values (*.csv)")[0]

        if filename:
            features = self.featuredlg.checkedItems()
            exporter = CsvExporter(filename, self.tileview.items,
                                   features)
            exporter.save()
            self.statusBar().showMessage("Image saved to %s" %filename)

    def saveCountingStats(self):

        filename = QFileDialog.getSaveFileName(
            self, "Save csv-file as ...",
            self._lastdir.replace(".hdf", "_statistics.csv"),
            "Comma separated values (*.csv)")[0]

        if filename:
            features = self.featuredlg.checkedItems()
            exporter = StatsExporter(filename, self.tileview.items,
                                     features)
            exporter.save()
            self.statusBar().showMessage("Image saved to %s" %filename)

    def updateToolbars(self, props):
        # in case of cellh5 file
        if props.gal_settings_mutable:
            self.navToolBar.show()

        self.navToolBar.updateToolbar(props)
        self.contrast.setChannelNames(props.channel_names, props.colors)
        self.nitems.setText(str(props.n_items))

    def setupToolbar(self):
        self.toolBar = ViewToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar.actionOpen.triggered.connect(self.onFileOpen)
        self.toolBar.actionNew.triggered.connect(self.newDataFile)
        self.actionReloadFile.triggered.connect(self.loadItems)

        self.navToolBar = NavToolBar(self)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.navToolBar)
        self.navToolBar.coordUpdated.connect(self.loader.setCoordinate)

        self.sortToolBar = SortToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.sortToolBar)

    def newDataFile(self):
        dlg = ImportDialog(self,
                           Qt.WindowMinMaxButtonsHint|Qt.WindowCloseButtonHint)
        dlg.loadData.connect(self._openAndLoad)
        dlg.exec_()

    def onThrowAnchor(self):
        self.sorting.removeAll()
        self.sorting.addItems(self.tileview.selectedItems())
        self.sorting.applyDefaultSortAlgorithm()
        self.sorting.sortAscending()

    def addToSortPanel(self):
        self.sorting.addItems(self.tileview.selectedItems())

    def onFileClose(self):
        self.loader.close()
        self.tileview.clear()
        self.featuredlg.clear()
        self.sorting.clear()

    def onFileOpen(self):

        file_ = QFileDialog.getOpenFileName(
            self, "Open hdf5 file", self._lastdir,
            "Hdf files (*.hdf5 *.ch5 *.hdf *.h5)")[0]

        if bool(file_):
            self._fileOpen(file_)
            self.loadItems()

    def _fileOpen(self, file_):
        self._lastdir = abspath(file_)
        try:
            self.loader.openFile(file_)
        except Exception as e:
            self.statusBar().showMessage(str(e))
            msg = "Could not open file\n %s" %str(e)
            QMessageBox.critical(self, "Error", msg)
        else:
            self.statusBar().showMessage(basename(file_))

    def _openAndLoad(self, file_):
        self.onFileClose()
        self._fileOpen(file_)
        self.loadItems()

    def onLoadingStarted(self):
        self.annotation.setFeatureNames(self.loader.featureNames)
        try:
            self.featuredlg.setFeatureGroups(self.loader.featureGroups)
            self.sorting.setFeatureGroups(self.loader.featureGroups)
        except RuntimeError as e:
            pass

    def onDropEvent(self, path):
        self._fileOpen(path)
        self.loadItems()

    def loadItems(self):

        self.abort.emit()
        self.loaderThread.wait()
        self.tileview.setViewFlags(self.toolBar.viewFlags())

        self.tileview.clear()
        self.tileview.updateRaster(self.navToolBar.galsize)
        self.tileview.updateNColumns(self.tileview.size().width())

        self.progressbar.setRange(0, self.navToolBar.nitems)
        self.loader.setNumberItems(self.navToolBar.nitems)
        self.loader.setGallerySize(self.navToolBar.galsize)
        self.loaderThread.start(self.loader)
