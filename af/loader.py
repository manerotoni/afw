"""
loader.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AfLoader', 'AfLoaderThread')


import warnings
import numpy as np

from PyQt4 import QtGui
from PyQt4 import QtCore
from af.hdfio import HdfReader


class AfLoaderThread(QtCore.QThread):

    error = QtCore.pyqtSignal("PyQt_PyObject")

    def __init__(self, *args, **kw):
        super(AfLoaderThread, self).__init__(*args, **kw)
        self._worker = None

    def start(self, worker):
        self._worker = worker
        self._worker.moveToThread(self)
        super(AfLoaderThread, self).start()

    def run(self):

        try:
            self._worker()
        except Exception as e:
            warnings.warn(str(e))
            self.error.emit(e)
        finally:
            self._worker.moveToThread(QtGui.QApplication.instance().thread())



class AfLoader(QtCore.QObject):

    PYDELAY = 10 # ms


    itemLoaded = QtCore.pyqtSignal("PyQt_PyObject")
    progressUpdate = QtCore.pyqtSignal(int)
    featureNames = QtCore.pyqtSignal(tuple)
    fileOpened = QtCore.pyqtSignal(dict)
    finished = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(AfLoader, self).__init__(*args, **kw)
        self._h5f = None
        self._coordinate = None
        self._size = None
        self._nitems = None
        self._aborted = False

    def __call__(self):
        self._aborted = False
        self.loadItems()

    def timerEvent(self, event):
        self.thread().msleep(100)

    @property
    def filename(self):
        return self._h5f.filename

    def openFile(self, file_):

        if self._h5f is not None:
            self._h5f.close()

        self._h5f = HdfReader(file_, "r", cached=True)

        # XXX assuming all values have the same subranges
        coord =  dict()
        plates = self._h5f.plateNames()
        coord['plate'] = plates[0]
        wells = self._h5f.wellNames(coord)
        coord['well'] = wells[0]
        sites = self._h5f.siteNames(coord)
        coord['site'] = sites[0]
        regions =  self._h5f.regionNames()

        self.fileOpened.emit({'plate': plates,
                              'well': wells,
                              'site': sites,
                              'region': regions})

    def setCoordinate(self, coordinate):
        self._coordinate = coordinate

    def setNumberItems(self, nitems):
        self._nitems = nitems

    def setGallerySize(self, size):
        self._size = size

    def close(self):
        if self._h5f is not None:
            self._h5f.close()

    def abort(self):
        self._aborted = True

    def loadItems(self):

        nf = self._h5f.numberItems(self._coordinate)
        indices = np.random.randint(0, nf, self._nitems)
        for i, idx in enumerate(indices):
            print i
            if self._aborted:
                break
            item = self._h5f.loadItem(idx, self._coordinate, self._size)
            self.progressUpdate.emit(i+1)
            self.itemLoaded.emit(item)
            # QtCore.QCoreApplication.processEvents()
            self.thread().msleep(self.PYDELAY)
