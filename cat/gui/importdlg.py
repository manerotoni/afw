"""
rudolf.hoefler@gmail.com
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


__all__ = ('ImportDialog', )


import glob
import traceback
from os.path import isfile, isdir, basename
from os.path import splitext, expanduser
from collections import OrderedDict

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox

from cat.threading import AtThread
from cat.threading import AtImporter
from cat.gui.channelbar import ChannelBar
from cat.gui.segmentationdlg import SegmentationDialog
from cat.segmentation.multicolor import LsmProcessor
from cat.imageio.filescanner import FileScanner


class ImportDialog(QtWidgets.QDialog):

    loadData = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kw):
        super(ImportDialog, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)

        self.structType.addItems(FileScanner.scanners())

        self.metadata =  None
        self._files  = None

        self.progressBar.hide()

        self.segdlg = SegmentationDialog(self)
        self.segdlg.hide()

        self.thread = AtThread(self)
        self.viewer.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                  QtWidgets.QSizePolicy.MinimumExpanding)

        self.cbar = ChannelBar(self, self.viewer)
        self.cbox.addWidget(self.cbar)
        self.cbar.newPixmap.connect(self.viewer.showPixmap,
                                    Qt.DirectConnection)
        self.cbar.newContourImage.connect(self.viewer.contourImage)

        self.dataFileBtn.clicked.connect(self.onOpenOutFile)
        self.imageDirBtn.clicked.connect(self.onOpenImageDir)
        self.startBtn.clicked.connect(self.raw2hdf)
        self.closeBtn.clicked.connect(self.close)
        self.closeBtn.clicked.connect(self.cbar.clear)
        self.segmentationBtn.clicked.connect(self.onSegmentationBtn)

        self.slider.newValue.connect(self.showObjects)

        self.slider.valueChanged.connect(self.showImage)
        self.slider.sliderReleased.connect(self.showObjects)
        self.slider.sliderPressed.connect(self.cbar.clearContours)
        self.contoursCb.stateChanged.connect(self.onContours)
        self.showBBoxes.stateChanged.connect(self.onBBoxes)
        self.showBBoxes.stateChanged.connect(self.showObjects)
        self.segdlg.paramsChanged.connect(self.showObjects)
        self.segdlg.refreshBtn.clicked.connect(self.showObjects)
        self.segdlg.imageUpdate.connect(self.showImage)
        self.segdlg.activateChannels.connect(self.cbar.activateChannels)
        self.segdlg.changeColor.connect(self.cbar.setColor)

        self.nextBtn.clicked.connect(self.onNextBtn)
        self.prevBtn.clicked.connect(self.onPrevBtn)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.showObjects()

    def closeEvent(self, event):
        super(ImportDialog, self).closeEvent(event)
        ofile = self.dataFile.text()
        if self.loadOnClose.isChecked() and isfile(ofile):
            self.loadData.emit(ofile)

    def onNextBtn(self):
        self.slider.setValue(self.slider.value()+1)
        self.showObjects()

    def onPrevBtn(self):
        self.slider.setValue(self.slider.value()-1)
        self.showObjects()

    def onContours(self, state):
        if state == Qt.Checked:
            self.showObjects()
        else:
            self.cbar.clearContours()
            self.viewer.clearPolygons()

    def onBBoxes(self, state):
        if state == Qt.Checked:
            self.showObjects()
        else:
            self.viewer.clearRects()

    def onSegmentationBtn(self):
        self.segdlg.show()
        self.segdlg.raise_()

    def onOpenOutFile(self):

        ofile = self.dataFile.text()
        if isfile(ofile):
            path = basename(ofile)
        else:
            path = expanduser("~")

        ofile = QFileDialog.getSaveFileName(self, "save to hdf file",
                                            path,
                                            "hdf (*.hdf *.h5)")[0]
        self.dataFile.setText(ofile)

    def onOpenImageDir(self):
        self.cbar.clearContours()
        self.viewer.clearRects()
        self.viewer.clearPolygons()

        idir = self.imageDir.text()
        if isdir(idir):
            path = basename(idir)
        else:
            path = expanduser("~")

        # TODO use getOpenFileNames instead
        idir = QFileDialog.getExistingDirectory(self,
                                                "Select an image directory",
                                                path)
        # cancel button
        if not idir:
            return

        self.imageDir.setText(idir)

        scanner = FileScanner(self.structType.currentText(), idir)
        self._files = scanner()

        if not self._files:
            QMessageBox.warning(self, "Error", "No files found")
            return

        self.dirinfo.setText("%d images found" %len(self._files))

        proc = LsmProcessor(self._files.keys()[0],
                            self.segdlg.segmentationParams(),
                            self.cbar.checkedChannels(),
                            treatment=self._files.values()[0])

        self.metadata = proc.metadata
        self.metadata.n_images = len(self._files)
        images = list(proc.iterQImages())
        props = list(proc.iterprops())
        self.cbar.addChannels(len(images))
        self.cbar.setImages(images, list(proc.iterprops()))
        state = self.segdlg.blockSignals(True)
        self.segdlg.setRegions(self.cbar.allChannels(), props)
        self.segdlg.setMaxZSlice(self.metadata.n_zslices-1)
        self.segdlg.blockSignals(state)
        self.slider.setRange(0, self.metadata.n_images-1)
        self.slider.setValue(0)

        self.showObjects()

    def showImage(self, index=0):
        # no image directory yet
        if self._files is None:
            return

        try:
            proc = LsmProcessor(self._files.keys()[index],
                                self.segdlg.segmentationParams(),
                                self.cbar.checkedChannels(),
                                treatment=self._files.values()[index])
        except IndexError:
            return
        self.viewer.clearPolygons()
        self.viewer.clearRects()
        images = list(proc.iterQImages())
        self.cbar.setImages(images, list(proc.iterprops()))

    def showObjects(self):

        if not (self.contoursCb.isChecked() or \
                    self.showBBoxes.isChecked()) or  \
                    self._files is None:
            return

        index = self.slider.value()
        try:
            mp = LsmProcessor(self._files.keys()[index],
                              self.segdlg.segmentationParams(),
                              self.cbar.checkedChannels(),
                              treatment=self._files.values()[index])
            # first channel for primary segementation
            mp.segmentation()
        except Exception as e:
            QMessageBox.critical(self, "Error", "%s:%s"  %(type(e), str(e)))
        finally:
            if not mp.objects:
                return

            if self.contoursCb.isChecked():
                self.cbar.setContours(mp.objects.contours)

            if self.showBBoxes.isChecked():
                self.cbar.drawRectangles(mp.objects.centers.values(),
                                         self.segdlg.galSize.value(),
                                         isize=self.metadata.size)

    def onError(self, exc):
        self.startBtn.setText("Start")
        QMessageBox.critical(self, "Error", str(exc))

    def onFinished(self):
        self.raise_()
        self.startBtn.setText("Start")
        QMessageBox.information(self, "finished", "training set saved")

    def showSlider(self):
        self.progressBar.hide()
        self.sliderframe.show()

    def hideSlider(self):
        self.progressBar.show()
        self.sliderframe.hide()

    def raw2hdf(self):

        if self.thread.isRunning():
            self.startBtn.setText("Start")
            self.thread.worker.abort()
        else:
            self.viewer.clearPolygons()
            self.viewer.clearRects()

            try:
                worker = AtImporter(self._files,
                                    self.metadata,
                                    self.dataFile.text(),
                                    self.cbar.checkedChannels(),
                                    self.cbar.colors(),
                                    self.segdlg.segmentationParams(),
                                    self.segdlg.featureGroups())
            except Exception as e:
                QMessageBox.critical(self, str(e), traceback.format_exc())
                return

            worker.connetToProgressBar(self.progressBar, Qt.QueuedConnection)
            worker.started.connect(self.hideSlider)
            worker.finished.connect(self.showSlider)
            worker.finished.connect(self.onFinished, Qt.QueuedConnection)
            worker.error.connect(self.onError, Qt.QueuedConnection)
            worker.contourImage.connect(self.cbar.contourImage,
                                        Qt.QueuedConnection)
            self.thread.start(worker)
            self.startBtn.setText("Abort")
