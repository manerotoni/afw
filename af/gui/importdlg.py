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

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox

from af.threading import AfThread
from af.threading import AfImporter
from af.gui.channelbar import ChannelBar
from af.gui.segmentationdlg import SegmentationDialog
from af.segmentation.multicolor import LsmProcessor


class ImportDialog(QtGui.QDialog):

    def __init__(self, *args, **kw):
        super(ImportDialog, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.metadata =  None
        self._files  = None

        self.setWindowTitle("Import Training Data")
        self.progressBar.hide()

        self.segdlg = SegmentationDialog(self)
        self.segdlg.hide()

        self.thread = AfThread(self)
        self.viewer.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                  QtGui.QSizePolicy.MinimumExpanding)

        self.cbar = ChannelBar(self, self.viewer)
        self.cbox.addWidget(self.cbar)
        self.cbar.newPixmap.connect(self.viewer.showPixmap,
                                    Qt.DirectConnection)
        self.cbar.newContourImage.connect(self.viewer.contourImage)

        self.outputBtn.clicked.connect(self.onOpenOutFile)
        self.inputBtn.clicked.connect(self.onOpenInputDir)
        self.startBtn.clicked.connect(self.raw2hdf)
        self.closeBtn.clicked.connect(self.close)
        self.closeBtn.clicked.connect(self.cbar.clear)
        self.segmentationBtn.clicked.connect(self.onSegmentationBtn)

        self.slider.valueChanged.connect(self.showImage)
        self.slider.sliderReleased.connect(self.showObjects)
        self.slider.sliderPressed.connect(self.cbar.clearContours)
        self.contoursCb.stateChanged.connect(self.onContours)
        self.showBBoxes.stateChanged.connect(self.onBBoxes)
        self.showBBoxes.stateChanged.connect(self.showObjects)
        self.segdlg.refreshBtn.clicked.connect(self.showObjects)

        self.nextBtn.clicked.connect(self.onNextBtn)
        self.prevBtn.clicked.connect(self.onPrevBtn)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.showObjects()

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

    def onOpenOutFile(self):

        ofile = self.outputFile.text()
        if isfile(ofile):
            path = basename(ofile)
        else:
            path = expanduser("~")

        ofile = QFileDialog.getSaveFileName(self, "save to hdf file",
                                            path,
                                            "hdf (*.hdf *.h5)")
        self.outputFile.setText(ofile)

    def onOpenInputDir(self):
        self.cbar.clearContours()
        self.viewer.clearRects()
        self.viewer.clearPolygons()

        idir = self.inputDir.text()
        if isdir(idir):
            path = basename(idir)
        else:
            path = expanduser("~")

        # TODO use getOpenFileNames instead
        idir = QFileDialog.getExistingDirectory(self,
                                                "select output directory",
                                                path)
        # cancel button
        if not idir:
            return

        self.inputDir.setText(idir)
        pattern = self.inputDir.text() + "/*.lsm"
        self._files = glob.glob(pattern)

        if not self._files:
            QMessageBox.warning(self, "Error", "No files found")
            return

        self._files.sort()
        self.dirinfo.setText("%d images found" %len(self._files))

        proc = LsmProcessor(self._files[0])
        self.metadata = proc.metadata
        self.metadata.n_images = len(self._files)
        images = list(proc.iterQImages())
        self.cbar.addChannels(len(images))
        self.cbar.setImages(images, list(proc.iterprops()))

        self.segdlg.setRegions(self.cbar.allChannels())
        self.slider.setRange(0, self.metadata.n_images-1)
        self.showObjects()

    def showImage(self, index=0):
        self.viewer.clearPolygons()
        self.viewer.clearRects()
        proc = LsmProcessor(self._files[index])
        images = list(proc.iterQImages())
        self.cbar.setImages(images, list(proc.iterprops()))

    def showObjects(self):
        if not (self.contoursCb.isChecked() or self.showBBoxes.isChecked()):
            return

        index = self.slider.value()
        try:
            mp = LsmProcessor(self._files[index])
            # first channel for primary segementation
            mp.segmentation(self.segdlg.segmentationParams(),
                        self.cbar.checkedChannels())
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            if self.contoursCb.isChecked():
                self.cbar.setContours(mp.objects.contours)

            if self.showBBoxes.isChecked():
                self.cbar.drawRectangles(mp.objects.centers.values(),
                                         self.segdlg.galSize.value())

    def onError(self, exc):
        self.startBtn.setText("start")
        QMessageBox.critical(self, "Error", str(exc))

    def onFinished(self):
        self.raise_()
        self.startBtn.setText("start")
        QMessageBox.information(self, "finished", "training set saved")

    def raw2hdf(self):

        if self.thread.isRunning():
            self.startBtn.setText("start")
            self.thread.worker.abort()
        else:
            self.viewer.clearPolygons()
            self.viewer.clearRects()

            try:
                worker = AfImporter(self._files,
                                    self.metadata,
                                    self.outputFile.text(),
                                    self.cbar.checkedChannels(),
                                    self.cbar.colors(),
                                    self.segdlg.segmentationParams(),
                                    self.segdlg.featureGroups())
            except Exception as e:
                QMessageBox.critical(self, str(e), traceback.format_exc())
                return

            worker.connetToProgressBar(self.progressBar, Qt.QueuedConnection)
            worker.finished.connect(self.onFinished, Qt.QueuedConnection)
            worker.error.connect(self.onError, Qt.QueuedConnection)
            worker.contourImage.connect(self.cbar.contourImage,
                                        Qt.QueuedConnection)
            self.thread.start(worker)
            self.startBtn.setText("abort")
