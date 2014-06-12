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
        self.worker = None

    def start(self, worker):
        self.worker = worker
        self.worker.moveToThread(self)
        super(AfThread, self).start()

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
