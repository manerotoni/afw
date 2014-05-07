"""
rudolf.hoefler@gmail.com
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


__all__ = ('ImportDialog', )

import glob
from os.path import isfile, isdir, basename, dirname

from os.path import splitext, expanduser
from pylsm import lsmreader

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox

from af.hdfwriter import HdfWriter
from af.imageio import LsmImage


class ImportDialog(QtGui.QDialog):

    progressUpdate = QtCore.pyqtSignal(int)
    progressSetRange = QtCore.pyqtSignal(int, int)
    progressFinished = QtCore.pyqtSignal()
    progressStart = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(ImportDialog, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)

        pbar= self.parent().progressbar
        self.progressUpdate.connect(pbar.setValue)
        self.progressSetRange.connect(pbar.setRange)
        self.progressFinished.connect(pbar.parent().hide)
        self.progressStart.connect(pbar.parent().show)

        self.outputBtn.clicked.connect(self.onOpenOutFile)
        self.inputBtn.clicked.connect(self.onOpenInputDir)
        self.importBtn.clicked.connect(self.raw2hdf)

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
            pattern = self.inputDir.text() + "/*.*"
            self._files = glob.glob(pattern)
            self.dirinfo.setText("%d images found" %len(self._files))

    def raw2hdf(self):
        if not isdir(dirname(self.outputFile.text())):
            QMessageBox.critical(self, "Error", "path does not exist!")
            return

        lsm = LsmImage(self._files[0])
        lsm.open()

        writer = HdfWriter(self.outputFile.text())
        writer.setupImages(len(self._files), lsm.channels, lsm.size, lsm.dtype)

        self.progressSetRange.emit(0, len(self._files))
        self.progressStart.emit()
        for i, file_ in enumerate(self._files):
            self.progressUpdate.emit(i+1)
            QtCore.QCoreApplication.processEvents()
            lsm = LsmImage(file_)
            lsm.open()
            for ci in xrange(lsm.channels):
                writer.setImage(lsm.get_image(stack=0, channel=ci), i, ci)

        writer.close()
        self.progressFinished.emit()
        QMessageBox.information(self, "finished", "all images save to hdf")
