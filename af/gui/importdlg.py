"""
rudolf.hoefler@gmail.com
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


__all__ = ('ImportDialog', )


import glob
from os.path import isfile, isdir, basename, dirname
from os.path import splitext, expanduser

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox

from af.hdfwriter import HdfWriter
from af.hdfwriter import HdfError
from af.gui.channelbar import ChannelBar
from af.segmentation.multicolor import LsmProcessor

from af.segmentation import PrimaryParams, ExpansionParams
from af.segmentation import feature_groups
from cecog import ccore

params = {"Channel 1": PrimaryParams(3, 17, 3, True, True),
          "Channel 2" : ExpansionParams(
        ccore.SrgType.KeepContours, None, 0, 5, 0)}

params["Channel 3"] = params["Channel 2"]
params["Channel 4"] = params["Channel 2"]

ftrg = {"Channel 1": feature_groups,
        "Channel 2": feature_groups,
        "Channel 3": feature_groups,
        "Channel 4": feature_groups}


class ImportDialog(QtGui.QDialog):

    progressUpdate = QtCore.pyqtSignal(int)
    progressSetRange = QtCore.pyqtSignal(int, int)
    progressFinished = QtCore.pyqtSignal()
    progressStart = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(ImportDialog, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowTitle("Import Training Data")

        self.viewer.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                  QtGui.QSizePolicy.MinimumExpanding)
        self.metadata =  None
        self.cbar = ChannelBar(self)
        self.cbox.addWidget(self.cbar)
        self.cbar.newPixmap.connect(self.viewer.showPixmap)

        pbar = self.parent().progressbar
        self.progressUpdate.connect(pbar.setValue)
        self.progressSetRange.connect(pbar.setRange)
        self.progressFinished.connect(pbar.parent().hide)
        self.progressStart.connect(pbar.parent().show)

        self.outputBtn.clicked.connect(self.onOpenOutFile)
        self.inputBtn.clicked.connect(self.onOpenInputDir)
        self.importBtn.clicked.connect(self.raw2hdf)
        self.closeBtn.clicked.connect(self.close)
        self.closeBtn.clicked.connect(self.cbar.clear)

        self.progressStart.connect(lambda: self.importBtn.setEnabled(False))
        self.progressFinished.connect(lambda: self.importBtn.setEnabled(True))

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

        idir = QFileDialog.getExistingDirectory(self,
                                                "select output directory",
                                                path)

        if isdir(idir):
            self.inputDir.setText(idir)
            pattern = self.inputDir.text() + "/*.lsm"
            self._files = glob.glob(pattern)
            self.dirinfo.setText("%d images found" %len(self._files))

        proc = LsmProcessor(self._files[0])
        self.metadata = proc.metadata
        self.metadata.n_images = len(self._files)
        images = list(proc.iterQImages())
        self.cbar.addChannels(len(images))
        self.cbar.setImages(images, list(proc.iterprops()))

    def raw2hdf(self):
        if not isdir(dirname(self.outputFile.text())):
            QMessageBox.critical(self, "Error", "path does not exist!")
            return

        writer = HdfWriter(self.outputFile.text())
        writer.setupImages(self.metadata.n_images,
                           len(self.cbar.checkedChannels()),
                           self.metadata.size, self.metadata.dtype)

        self.progressSetRange.emit(0, len(self._files))
        self.progressStart.emit()

        channels = self.cbar.checkedChannels()
        try:
            for i, file_ in enumerate(self._files):
                self.progressUpdate.emit(i+1)
                QtCore.QCoreApplication.processEvents()
                mp = LsmProcessor(file_)
                # first channel for primary segementation
                mp.segmentation(params, channels, min(channels.keys()))
                mp.calculateFeatures(ftrg)
                writer.saveData(mp.objects)
                writer.setImage(mp.image[:, :, channels.keys()], i)

                self.cbar.setImages(list(mp.iterQImages()))
            writer.close()
        except HdfError as e:
            QMessageBox.critical(self, "Error", str(e))
            writer.close(flush=False)
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            writer.close()
            return

        self.progressFinished.emit()
        QMessageBox.information(self, "finished", "all images save to hdf")
