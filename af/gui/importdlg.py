"""
rudolf.hoefler@gmail.com
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


__all__ = ('ImportDialog', )

import glob
from os.path import isfile, isdir, basename, dirname
from os.path import splitext, expanduser

import numpy as np

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox

from af.hdfwriter import HdfWriter
from af.gui.imagewidget import ImageWidget
from af.gui.channelbar import ChannelBar
from af.imageio import LsmImage



class ImportDialog(QtGui.QDialog):

    progressUpdate = QtCore.pyqtSignal(int)
    progressSetRange = QtCore.pyqtSignal(int, int)
    progressFinished = QtCore.pyqtSignal()
    progressStart = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(ImportDialog, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowTitle("Import Training Data")

        self.viewer = ImageWidget(self)
        self.viewer.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                  QtGui.QSizePolicy.MinimumExpanding)
        self.imagebox.addWidget(self.viewer)
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

        lsm = LsmImage(self._files[0])
        lsm.open()

        self.metadata = lsm.metadata
        self.metadata.n_images = len(self._files)

        images = list(lsm.iterQImages())
        self.cbar.addChannels(len(images))
        self.cbar.setImages(images, list(lsm.iterprops()))
        lsm.close()

    def raw2hdf(self):
        if not isdir(dirname(self.outputFile.text())):
            QMessageBox.critical(self, "Error", "path does not exist!")
            return

        writer = HdfWriter(self.outputFile.text())
        writer.setupImages(self.metadata.n_images, self.metadata.n_channels,
                           self.metadata.size, self.metadata.dtype)

        self.progressSetRange.emit(0, len(self._files))
        self.progressStart.emit()
        channels = self.cbar.checkedChannels()

        image = np.zeros(self.metadata.image_dimension,
                         dtype=self.metadata.dtype)
        for i, file_ in enumerate(self._files):
            self.progressUpdate.emit(i+1)
            QtCore.QCoreApplication.processEvents()
            lsm = LsmImage(file_)
            lsm.open()
            try:
                for i, ci in enumerate(channels):
                    image[:, :, i] = lsm.get_image(stack=0, channel=ci)
                    writer.setImage(image, i)
            except Exception as e:
                QMessageBox.critical(self,
                                     "Error",
                                     "%s (%s)" %(e, file_))

            self.cbar.setImages(list(lsm.iterQImages()))
            lsm.close()

        writer.close()
        self.progressFinished.emit()
        QMessageBox.information(self, "finished", "all images save to hdf")
