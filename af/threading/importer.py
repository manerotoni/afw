"""
importer.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AfImporter', 'AbortQWorker')

from os.path import isdir, dirname
from collections import OrderedDict
import traceback

from PyQt4 import QtCore
from PyQt4.QtCore import Qt

from af.hdfwriter import HdfWriter
from af.hdfwriter import HdfError
from af.segmentation.multicolor import LsmProcessor


class AbortQWorker(Exception):
    pass


class AfImporter(QtCore.QObject):

    PYDELAY = 50 # ms

    progressUpdate = QtCore.pyqtSignal(int)
    progressSetRange = QtCore.pyqtSignal(int, int)
    finished = QtCore.pyqtSignal()
    started = QtCore.pyqtSignal()
    imageReady = QtCore.pyqtSignal(tuple)
    contourImage = QtCore.pyqtSignal(tuple, dict)
    error = QtCore.pyqtSignal("PyQt_PyObject")

    def __init__(self, files, metadata, outfile, channels,
                 seg_params, feature_groups):
        super(AfImporter, self).__init__()
        self._abort = False

        if not isdir(dirname(outfile)):
            raise IOError(self, "Error", "path does not exist!")

        self.files = files
        self.channels = channels
        self.metadata = metadata
        self.outfile = outfile
        self.seg_params = seg_params
        self.feature_groups = feature_groups

    def abort(self):
        self._abort = True

    def interruption_point(self):
        if self._abort:
            raise AbortQWorker()

    def connetToProgressBar(self, pbar, connectiontype=Qt.QueuedConnection):
        self.progressUpdate.connect(pbar.setValue, connectiontype)
        self.progressSetRange.connect(pbar.setRange, connectiontype)
        self.finished.connect(pbar.hide, connectiontype)
        self.started.connect(pbar.show, connectiontype)

    def __call__(self):
        self.started.emit()
        self.progressSetRange.emit(0, len(self.files))

        writer = HdfWriter(self.outfile)
        writer.setupImages(self.metadata.n_images,
                           len(self.channels),
                           self.metadata.size, self.metadata.dtype)

        try:
            for i, file_ in enumerate(self.files):
                self.progressUpdate.emit(i+1)
                self.interruption_point()
                self.thread().msleep(self.PYDELAY)
                mp = LsmProcessor(file_)
                # first channel for primary segementation
                mp.segmentation(self.seg_params, self.channels)
                mp.calculateFeatures(self.feature_groups)
                objects = mp.objects
                # saveData ignores empty objects
                writer.saveData(objects)
                writer.setImage(mp.image[:, :, self.channels.keys()], i)
                self.contourImage.emit(tuple(mp.iterQImages()),
                                       objects.contours)

            writer.flush()
            self.finished.emit()

        except AbortQWorker:
            pass

        except HdfError as e:
            self.error.emit(e)
            traceback.print_exc()
            raise

        except Exception as e:
            # writer.flush()
            self.error.emit(e)
            traceback.print_exc()
            raise

        finally:
            writer.close()
