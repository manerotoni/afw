"""
importer.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtImporter', 'AbortQWorker')

from os.path import isdir, dirname
import traceback

from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from cat.hdfio.hdfwriter import HdfWriter
from cat.hdfio.readercore import HdfError
from cat.segmentation.multicolor import LsmProcessor


class AbortQWorker(Exception):
    pass


class AtImporter(QtCore.QObject):

    PYDELAY = 50 # ms

    progressUpdate = QtCore.pyqtSignal(int)
    progressSetRange = QtCore.pyqtSignal(int, int)
    finished = QtCore.pyqtSignal()
    started = QtCore.pyqtSignal()
    imageReady = QtCore.pyqtSignal(tuple)
    contourImage = QtCore.pyqtSignal(tuple, dict)
    error = QtCore.pyqtSignal("PyQt_PyObject")

    def __init__(self, files, metadata, outfile, channels, colors,
                 seg_params, feature_groups):
        super(AtImporter, self).__init__()
        self._abort = False

        if not isdir(dirname(outfile)):
            raise IOError(self, "Error", "path does not exist!")

        self.files = files
        self.channels = channels
        self.colors = colors
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

    def __call__(self):
        self.started.emit()
        self.progressSetRange.emit(0, len(self.files))

        writer = HdfWriter(self.outfile)
        colors = [self.colors[ch] for ch in self.channels.values()]
        writer.setupFile(self.metadata.n_images, self.channels, colors)
        writer.saveSettings(self.seg_params, self.feature_groups,
                            self.channels.values(), self.colors)

        try:
            gsize = self.seg_params.values()[0].gallery_size
            for i, (file_, treatment) in enumerate(self.files.iteritems()):
                self.progressUpdate.emit(i+1)
                self.interruption_point()
                self.thread().msleep(self.PYDELAY)
                mp = LsmProcessor(file_, self.seg_params, self.channels, gsize,
                                  treatment)

                # first channel for primary segementation
                mp.segmentation()
                mp.calculateFeatures(self.feature_groups)
                objects = mp.objects
                # saveData ignores empty objects
                image = mp.image[:, :, :, self.channels.keys()]
                writer.saveData(objects, image)

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
            self.error.emit(e)
            traceback.print_exc()
            raise

        finally:
            writer.close()
