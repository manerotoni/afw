"""
loader.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AfLoader', )


from PyQt4 import QtCore
from af.hdfio.guesser import guessHdfType


class AfLoader(QtCore.QObject):

    PYDELAY = 50 # ms

    itemLoaded = QtCore.pyqtSignal("PyQt_PyObject")
    progressUpdate = QtCore.pyqtSignal(int)
    featureNames = QtCore.pyqtSignal(tuple)
    fileOpened = QtCore.pyqtSignal("PyQt_PyObject")
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

    def cspace(self):
        return self._h5f.cspace()

    @property
    def filename(self):
        return self._h5f.filename

    def openFile(self, file_):

        if self._h5f is not None:
            self._h5f.close()

        self._h5f = guessHdfType(file_)
        self.fileOpened.emit(self._h5f.fileinfo)

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

        if self._h5f is None:
            return

        nf = self._h5f.numberItems(self._coordinate)
        indices = range(0, nf)
        # np.random.shuffle(indices)
        for i, idx in enumerate(sorted(indices[:self._nitems])):
            if self._aborted:
                break
            item = self._h5f.loadItem(idx, self._coordinate, self._size)
            self.progressUpdate.emit(i+1)
            self.itemLoaded.emit(item)
            self.thread().msleep(self.PYDELAY)
