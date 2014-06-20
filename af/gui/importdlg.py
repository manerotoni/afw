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

# XXX TODO implement dialog for segementation parmeters
from af.segmentation import PrimaryParams, ExpansionParams
from af.segmentation import feature_groups
from cecog import ccore

params = {"Channel 1": PrimaryParams(3, 42, 6, True, True),
          "Channel 2" : ExpansionParams(
        ccore.SrgType.KeepContours, None, 0, 5, 0)}

params["Channel 3"] = params["Channel 2"]
params["Channel 4"] = params["Channel 2"]

ftrg = {"Channel 1": feature_groups,
        "Channel 2": feature_groups,
        "Channel 3": feature_groups,
        "Channel 4": feature_groups}


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

        self.outputBtn.clicked.connect(self.onOpenOutFile)
        self.inputBtn.clicked.connect(self.onOpenInputDir)
        self.startBtn.clicked.connect(self.raw2hdf)
        self.closeBtn.clicked.connect(self.close)
        self.closeBtn.clicked.connect(self.cbar.clear)
        self.segmentationBtn.clicked.connect(self.onSegmentationBtn)

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

        # no lsm files in directory
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
            try:
                worker = AfImporter(self._files,
                                    self.metadata,
                                    self.outputFile.text(),
                                    self.cbar.checkedChannels(),
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
