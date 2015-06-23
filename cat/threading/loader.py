"""
loader.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtLoader', )


from PyQt5 import QtCore
from cat.hdfio.guesser import guessHdfType
from cat.config import AtConfig

class AtLoader(QtCore.QObject):

    PYDELAY = 2000 # micro seconds

    itemLoaded = QtCore.pyqtSignal("PyQt_PyObject")
    progressUpdate = QtCore.pyqtSignal(int)
    fileOpened = QtCore.pyqtSignal("PyQt_PyObject")
    finished = QtCore.pyqtSignal()
    started = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(AtLoader, self).__init__(*args, **kw)
        self._h5f = None
        self._coordinate = None
        self._size = None
        self._nitems = None
        self._aborted = False
        self._feature_names = None
        self._fgroups = None

    def __call__(self):
        self._aborted = False
        self.loadItems()

    def cspace(self):
        return self._h5f.cspace()

    @property
    def filename(self):
        return self._h5f.filename

    @property
    def file(self):
        return self._h5f

    @property
    def featureNames(self):
        """Return the feature names of the last dataset loaded"""
        if self._feature_names is None:
            raise RuntimeError("No dataset loaded yet")
        return self._feature_names

    @property
    def featureGroups(self):
        """Return the feature names of the last dataset loaded"""
        if self._fgroups is None:
            raise RuntimeError("No dataset loaded yet")
        return self._fgroups

    def openFile(self, file_):
        self.close()
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
            self._feature_names = None
            self._fgroups = None
            self._h5f = None

    def abort(self):
        self._aborted = True

    def loadItems(self):

        if self._h5f is None:
            return

        # feature names of the last dataset loaded
        self._feature_names = self._h5f.featureNames(self._coordinate['region'])
        try:
            self._fgroups = self._h5f.featureGroups(self._coordinate['region'])
        except KeyError:
            pass
        self.started.emit()

        if AtConfig().interactive_item_limit < self._h5f.numberItems(self._coordinate):
            self._loadItemsSingle()
        else:
            self._loadItemsBulk()

        self.finished.emit()

    def _loadItemsSingle(self):
        """Load Item from hdf file and display it immediately."""
        for i, item in enumerate(
                self._h5f.iterItems(self._nitems, self._coordinate,
                                    self._size, delayed=True)):
            self.thread().usleep(self.PYDELAY)
            if self._aborted:
                break
            self.progressUpdate.emit(i+1)
            self.itemLoaded.emit(item)


    def _loadItemsBulk(self):
        """Load items from hdf and display all items after loading is finished."""
        items = list()
        for i, item in enumerate(
                self._h5f.iterItems(self._nitems, self._coordinate, self._size)):
            if self._aborted:
                break
            self.progressUpdate.emit(i+1)
            items.append(item)
        self.itemLoaded.emit(items)
