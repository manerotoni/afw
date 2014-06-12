"""
loader.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AfThread', )


import warnings
import traceback

from PyQt4 import QtGui
from PyQt4 import QtCore


class AfThread(QtCore.QThread):

    error = QtCore.pyqtSignal("PyQt_PyObject")

    def __init__(self, *args, **kw):
        super(AfThread, self).__init__(*args, **kw)
        self._worker = None

    def start(self, worker):
        self._worker = worker
        self._worker.moveToThread(self)
        super(AfThread, self).start()

    def run(self):

        try:
            self._worker()
        except Exception as e:
            traceback.print_exc()
            warnings.warn(str(e))
            self.error.emit(e)
        finally:
            self._worker.moveToThread(QtGui.QApplication.instance().thread())
