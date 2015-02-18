"""
loader.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtThread', )


import warnings
import traceback

from PyQt5 import QtGui
from PyQt5 import QtCore


class AtThread(QtCore.QThread):

    error = QtCore.pyqtSignal("PyQt_PyObject")

    def __init__(self, *args, **kw):
        super(AtThread, self).__init__(*args, **kw)
        self.worker = None

    def start(self, worker):
        self.worker = worker
        self.worker.moveToThread(self)
        super(AtThread, self).start()

    def run(self):

        try:
            self.worker()
        except Exception as e:
            traceback.print_exc()
            warnings.warn(str(e))
            self.error.emit(e)
        finally:
            self.worker.moveToThread(QtGui.QApplication.instance().thread())
            self.worker = None
